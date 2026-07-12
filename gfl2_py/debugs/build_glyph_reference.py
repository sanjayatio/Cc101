#!/usr/bin/env python3
"""
debugs/build_glyph_reference.py — accumulate one real glyph crop per
character into a single reference PNG per font/context, plus a lookup
module mapping (file, left-to-right index) -> character.

None of assets/fonts/{score_digits,stat_header,stat_pct,stat_val}.py store
the actual glyph pixels — only derived feature vectors (proj/hu/hproj/
inner_blobs).  Eyeballing what a font's digits actually look like has
therefore always meant re-running a --build pass with --debug, or hunting
through single/*.png by hand.  This script streamlines that: for each of
the four character sets below, it re-runs the SAME extraction pipeline
each font's own --build path already uses, across the same corpus, and
for every character picks the ONE real sample whose feature vector lands
closest to that font's own already-trained centroid (proj, i.e. the same
nearest-centroid convention this project uses everywhere else) — never a
synthetic average, never resized. Crops are saved at NATIVE resolution in
their original color, so pixel fidelity is preserved for future feature
work (measuring stroke widths, prototyping a new spatial feature, etc.).

Each output PNG is a plain glyph atlas, nothing else (no borders, no text
labels): glyphs laid out left-to-right on that font's own real background
color (sampled from the same source strips, not a synthetic black/gray
canvas), each vertically placed at its TRUE proportional position within
its source line (so e.g. a decimal point sits low near the baseline, not
centered) rather than individually re-centered. Ample horizontal gaps
between glyphs mean a plain threshold + cv2.findContours pass on the atlas
image cleanly re-isolates each glyph; sorting the resulting contours by x
reproduces the same left-to-right order recorded in glyph_lookup.py — no
per-glyph coordinates are stored anywhere, by design.

Output:
    assets/fonts/glyph_daily_score.png    0-9              (daily GS header score,
                                                              medal-anchored crop)
    assets/fonts/glyph_daily_header.png   0-9,K,M[,.]      (daily GS header stats)
    assets/fonts/glyph_daily_pct.png      0-9,.            (daily GS pct line)
    assets/fonts/glyph_daily_val.png      0-9,K            (daily GS val line)
    assets/fonts/glyph_lookup.py          DATA[filename][index] -> char

val has no '.' or 'M' entry: neither ever appears in stat_val.py's own
trained DATA (checked: keys are only '0'-'9','K') or in this project's
val-line ground truth anywhere in the corpus — the 'M' suffix on a val
value is currently only ever inferred behaviorally (docs/known_issues.txt
§9's "two trailing '??' -> M" safety net), never backed by a real
classified glyph.  header's '.' entry is included only if this run
actually finds a real dot-sized blob in a header crop; if none is found
across the corpus, it is silently omitted (header's Tesseract ground
truth is generated with a "0123456789KM" whitelist, so a dot never
becomes part of the expected string either way — same absence-of-evidence
as val).

Usage:
    python debugs/build_glyph_reference.py [--images "single/*.png"]
"""
from __future__ import annotations
import argparse
import glob as _glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # project root

import cv2
import numpy as np

from gfl2.score_ocr import (
    THRESH_VAL as SCORE_THRESH_VAL,
    DIGIT_MIN_W, DIGIT_MAX_W, DIGIT_MIN_H, DIGIT_MAX_H,
    NORM_W as SCORE_NORM_W, NORM_H as SCORE_NORM_H,
)
from gfl2.stat_ocr import (
    _binarize, _find_blobs, _filter_y_outliers, _find_percent_x_start,
    _load_tess_gt_cache, _load_excluded_cells, _collect_cells,
    PCT_STRIP_Y, VAL_STRIP_Y, DOT_MAX_DIM, TRAIN_CHARS,
    NORM_W_PCT, NORM_H_PCT, NORM_W_VAL, NORM_H_VAL,
)
from assets.builders.build import (
    _binarize_hdr, _find_header_blobs, _drop_label_bleed,
    _header_crop, _tess_read, _STAT_RANGES,
)
from gfl2.patterns.daily_gunsmoke import (
    _split_panels, _find_frames, _find_medal_right,
    HEADER_BAR_Y0, HEADER_BAR_Y1, SCORE_X0, SCORE_CROP_W_FR,
)

_HERE       = Path(__file__).resolve().parent.parent
_FONTS_DIR  = _HERE / "assets" / "fonts"
_LOOKUP_F   = _FONTS_DIR / "glyph_lookup.py"

_DIGITS = list("0123456789")


# ── Background / ink color estimation ──────────────────────────────────────────

def _bg_mode_color(color_strip: np.ndarray) -> "np.ndarray | None":
    """Background = the MODE (most-common pixel value) of the crop — the same
    convention layout.py's _detect_columns already uses (reference.txt §4:
    'the background colour is identified as the most-common pixel value'),
    not a mean/median over some other mask. A UI crop is mostly background,
    so its single most-frequent gray level reliably IS the background,
    without depending on separately getting an ink/background threshold's
    polarity right for every font."""
    gray = cv2.cvtColor(color_strip, cv2.COLOR_BGR2GRAY) if color_strip.ndim == 3 else color_strip
    if gray.size == 0:
        return None
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    mode_val = int(np.argmax(hist))
    mask = gray == mode_val
    if not np.any(mask):
        return None
    return np.median(color_strip[mask].reshape(-1, 3), axis=0)


def _aggregate_color(samples: list[np.ndarray]) -> "tuple[int, int, int] | None":
    if not samples:
        return None
    return tuple(int(v) for v in np.median(np.array(samples), axis=0))


def _candidate_ink_color(cand: dict) -> np.ndarray:
    mask = cand["bin"] > 0
    if not np.any(mask):
        return np.zeros(3)
    return np.median(cand["raw"][mask].reshape(-1, 3), axis=0)


def _ink_ref_from_buckets(buckets: dict[str, list[dict]]) -> "tuple[int, int, int] | None":
    """Corpus-wide reference ink color, pooled from the ALREADY-ISOLATED digit
    blobs themselves (never a whole-strip/whole-crop sample) — used to keep a
    color-outlier candidate (e.g. a differently-rendered source image mixed
    into the corpus) from being picked over an equally-good-shaped,
    correctly-colored one (see _pick_by_centroid). Sampling from the whole
    crop instead of the isolated blob was tried first and rejected: a score
    crop's medal icon graphic is also "ink" by threshold (and by mode, since
    it's a solid-colored blob of its own), and being larger than the digit
    strokes it dominated the aggregate, skewing it toward the icon's
    tan/gold tone rather than the digits' true color."""
    colors = [_candidate_ink_color(c) for cands in buckets.values() for c in cands]
    return _aggregate_color(colors)


# ── Selection: nearest-real-sample-to-trained-centroid ────────────────────────

def _v_proj_native(bin_crop: np.ndarray, norm_size: tuple[int, int]) -> np.ndarray:
    """Resize (for scoring only, never for the saved crop) and compute the
    same v-projection feature every font's own templates were trained on."""
    resized = cv2.resize(bin_crop, norm_size, interpolation=cv2.INTER_AREA)
    proj = resized.mean(axis=0).astype(float)
    mx = proj.max() or 1.0
    return proj / mx


def _pick_by_centroid(cands: list[dict], centroid_proj: list[float],
                       norm_size: tuple[int, int],
                       ink_ref: "tuple[int, int, int] | None" = None,
                       color_weight: float = 0.5) -> tuple[dict, float]:
    """Nearest-real-sample-to-trained-centroid, shape first. When ink_ref is
    given, color is folded in as a SECOND-ORDER tiebreak (not primary) so a
    color-outlier source (e.g. a differently-rendered screenshot mixed into
    the corpus) doesn't get picked purely because its shape happens to be a
    hair closer to centroid than every correctly-colored candidate's — this
    is what previously surfaced an orange '1' in glyph_daily_score.png even
    though same-shaped black '1's exist in the corpus."""
    target = np.array(centroid_proj)
    scored = []
    for cand in cands:
        proj = _v_proj_native(cand["bin"], norm_size)
        dist = float(np.linalg.norm(proj - target))
        scored.append((dist, cand))
    scored.sort(key=lambda t: t[0])

    if ink_ref is None or len(scored) == 1:
        return scored[0][1], scored[0][0]

    ink_target = np.array(ink_ref, dtype=float)

    def combined(dist_cand):
        dist, cand = dist_cand
        color_dist = float(np.linalg.norm(_candidate_ink_color(cand) - ink_target)) / 255.0
        return dist + color_weight * color_dist

    best_dist, best_cand = min(scored, key=combined)
    return best_cand, best_dist


def _self_corpus_centroid(cands: list[dict], norm_size: tuple[int, int]) -> np.ndarray:
    """Mean v-projection feature across a digit's OWN real candidate pool,
    used in place of a production-trained template centroid when that
    template was built from a DIFFERENT font/context than the corpus being
    sampled here (see collect_daily_score_glyphs -- assets/fonts/
    score_digits.py is trained only from Weekly Gunsmoke crops, so it is not
    a meaningful "typical shape" reference for Daily Gunsmoke's own score
    font, docs/action_items.txt #12). Still nearest-centroid selection,
    just self-referential instead of borrowing an unrelated font's shape."""
    projs = [_v_proj_native(c["bin"], norm_size) for c in cands]
    return np.mean(projs, axis=0)


def _pick_by_median_size(cands: list[dict]) -> dict:
    sizes = np.array([[c["raw"].shape[1], c["raw"].shape[0]] for c in cands], dtype=float)
    med = np.median(sizes, axis=0)
    dists = np.linalg.norm(sizes - med, axis=1)
    return cands[int(np.argmin(dists))]


# ── Group 1: daily Gunsmoke header score digits (0-9) ──────────────────────────
#
# NOTE (docs/action_items.txt #12): this group used to be sourced from
# tests/inputs/weekly_scores/manifest.json -- the WEEKLY Gunsmoke score-cell
# corpus -- even though glyph_daily_score.png's own name, and the header-bar
# score field it's meant to document, are Daily Gunsmoke's. Now sourced
# directly from Daily Gunsmoke's own medal-anchored header-bar score crop
# (the exact crop gfl2.patterns.daily_gunsmoke._extract_header's score
# section reads), mirroring collect_header_glyphs's own real-Daily-image
# convention below.

def collect_daily_score_glyphs(image_paths: list[Path]) -> tuple[
        dict[str, list[dict]], list[np.ndarray]]:
    buckets: dict[str, list[dict]] = {d: [] for d in _DIGITS}
    bg_samples: list[np.ndarray] = []
    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        for pi, panel in enumerate(_split_panels(img)):
            frames = _find_frames(panel)
            if not frames:
                continue
            ph, pw = panel.shape[:2]
            medal_right = _find_medal_right(panel)
            fw    = frames[0][2]
            sc_y0 = int(ph * HEADER_BAR_Y0) + 3
            sc_y1 = int(ph * HEADER_BAR_Y1) - 3
            sc_x0 = ((medal_right + 2) if medal_right is not None else int(pw * SCORE_X0)) + 3
            sc_w  = int(fw * SCORE_CROP_W_FR)
            crop  = panel[sc_y0:sc_y1, sc_x0:min(sc_x0 + sc_w, pw)]
            if crop.size == 0:
                continue
            gt = _tess_read(crop)
            expected = [c for c in gt if c in _DIGITS]
            if not expected:
                continue
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, SCORE_THRESH_VAL, 255, cv2.THRESH_BINARY)
            cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            blobs = []
            for c in cnts:
                x, y, w, h = cv2.boundingRect(c)
                if DIGIT_MIN_W <= w <= DIGIT_MAX_W and DIGIT_MIN_H <= h <= DIGIT_MAX_H:
                    blobs.append((x, y, w, h))
            blobs.sort(key=lambda b: b[0])
            if len(blobs) != len(expected):
                continue  # e.g. adjacent digits merged at SCORE_THRESH_VAL -- skip, don't guess
            strip_h = crop.shape[0]
            bg = _bg_mode_color(crop)
            if bg is not None:
                bg_samples.append(bg)
            src = f"{img_path.stem}_p{pi + 1}_score"
            for (x, y, w, h), ch in zip(blobs, expected):
                buckets[ch].append({
                    "raw": crop[y:y + h, x:x + w],
                    "bin": thresh[y:y + h, x:x + w],
                    "source": src,
                    "y": y, "strip_h": strip_h,
                })
    return buckets, bg_samples


# ── Group 2: daily Gunsmoke header stats (0-9, K, M, [.]) ──────────────────────

def collect_header_glyphs(image_paths: list[Path]) -> tuple[
        dict[str, list[dict]], list[dict], list[np.ndarray]]:
    buckets: dict[str, list[dict]] = {c: [] for c in TRAIN_CHARS}
    dot_cands: list[dict] = []
    bg_samples: list[np.ndarray] = []
    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        for pi, panel in enumerate(_split_panels(img)):
            frames = _find_frames(panel)
            if not frames:
                continue
            for fr_range, label in _STAT_RANGES:
                crop = _header_crop(panel, frames, fr_range)
                if crop.size == 0:
                    continue
                gt = _tess_read(crop)
                if not gt:
                    continue
                thresh = _binarize_hdr(crop)
                blobs = _drop_label_bleed(_filter_y_outliers(_find_header_blobs(thresh)))
                if not blobs:
                    continue
                strip_h = crop.shape[0]
                bg = _bg_mode_color(crop)
                if bg is not None:
                    bg_samples.append(bg)
                digit_cands, blob_dots = [], []
                for (x, y, w, h) in sorted(blobs, key=lambda b: b[0]):
                    raw = crop[y:y + h, x:x + w]
                    bin_native = thresh[y:y + h, x:x + w]
                    src = f"{img_path.stem}_p{pi + 1}_{label}"
                    cand = {"raw": raw, "bin": bin_native, "source": src,
                            "y": y, "strip_h": strip_h}
                    if w <= DOT_MAX_DIM and h <= DOT_MAX_DIM:
                        blob_dots.append(cand)
                    else:
                        digit_cands.append(cand)
                dot_cands.extend(blob_dots)
                expected = [c for c in gt if c in TRAIN_CHARS]
                if len(digit_cands) == len(expected):
                    for cand, ch in zip(digit_cands, expected):
                        buckets[ch].append(cand)
    return buckets, dot_cands, bg_samples


# ── Groups 3 & 4: daily Gunsmoke stat-cell pct / val lines ─────────────────────

def _native_line_glyphs(strip_color: np.ndarray, is_pct: bool) -> tuple[
        list[dict], list[dict], "np.ndarray | None"]:
    """Mirror _extract_pct_glyphs / _extract_val_glyphs but WITHOUT resizing —
    returns (digit_candidates, dot_candidates, bg_sample), each candidate
    carrying its native raw+bin crop and true (y, strip_h) position."""
    thresh = _binarize(strip_color)
    bg = _bg_mode_color(strip_color)
    blobs = _filter_y_outliers(_find_blobs(thresh))
    if not blobs:
        return [], [], bg
    blobs = sorted(blobs, key=lambda b: b[0])
    pct_x = _find_percent_x_start(blobs) if is_pct else None
    strip_h = strip_color.shape[0]

    digit_cands, dot_cands = [], []
    for (x, y, w, h) in blobs:
        if pct_x is not None and x >= pct_x:
            continue  # '%' sub-blob
        raw = strip_color[y:y + h, x:x + w]
        bin_native = thresh[y:y + h, x:x + w]
        cand = {"raw": raw, "bin": bin_native, "y": y, "strip_h": strip_h}
        if w <= DOT_MAX_DIM and h <= DOT_MAX_DIM:
            dot_cands.append(cand)
        else:
            digit_cands.append(cand)
    return digit_cands, dot_cands, bg


def collect_pct_val_glyphs(cells: list[dict]) -> tuple[
        dict[str, list[dict]], list[dict], dict[str, list[dict]],
        list[np.ndarray], list[np.ndarray]]:
    pct_buckets: dict[str, list[dict]] = {d: [] for d in _DIGITS}
    val_buckets: dict[str, list[dict]] = {d: [] for d in _DIGITS + ["K"]}
    pct_dot_cands: list[dict] = []
    pct_bg_samples: list[np.ndarray] = []
    val_bg_samples: list[np.ndarray] = []

    for item in cells:
        cell = item["cell"]
        ch = cell.shape[0]
        source = item["source"]

        pct_strip = cell[: int(ch * PCT_STRIP_Y[1]), :]
        digit_cands, dot_cands, bg_p = _native_line_glyphs(pct_strip, is_pct=True)
        if bg_p is not None:
            pct_bg_samples.append(bg_p)
        for c in digit_cands + dot_cands:
            c["source"] = source
        pct_dot_cands.extend(dot_cands)
        expected_pct = [c for c in (item.get("pct") or "") if c in TRAIN_CHARS]
        if len(digit_cands) == len(expected_pct):
            for cand, char in zip(digit_cands, expected_pct):
                if char in pct_buckets:
                    pct_buckets[char].append(cand)

        val_strip = cell[int(ch * VAL_STRIP_Y[0]): int(ch * VAL_STRIP_Y[1]), :]
        digit_cands_v, _dot_v, bg_v = _native_line_glyphs(val_strip, is_pct=False)
        if bg_v is not None:
            val_bg_samples.append(bg_v)
        for c in digit_cands_v:
            c["source"] = source
        expected_val = [c for c in (item.get("val") or "") if c in TRAIN_CHARS]
        if len(digit_cands_v) == len(expected_val):
            for cand, char in zip(digit_cands_v, expected_val):
                if char in val_buckets:
                    val_buckets[char].append(cand)

    return pct_buckets, pct_dot_cands, val_buckets, pct_bg_samples, val_bg_samples


def _apply_gt_overrides(cells: list[dict]) -> None:
    gt_file = _HERE / "tests" / "inputs" / "daily" / "stat_gt_overrides.json"
    if not gt_file.exists():
        return
    overrides = json.loads(gt_file.read_text(encoding="utf-8"))
    for item in cells:
        ov = overrides.get(item.get("source"))
        if ov:
            if "pct" in ov:
                item["pct"] = ov["pct"]
            if "val" in ov:
                item["val"] = ov["val"]


# ── Atlas assembly ────────────────────────────────────────────────────────────

def make_atlas(rows: list[tuple[str, dict]], bg_color: tuple[int, int, int],
                out_path: Path, pad_x: int = 20, margin_y: int = 6) -> None:
    """Plain glyph atlas: no borders, no text, nothing but the glyphs on their
    own real background. Glyphs run left-to-right with ample horizontal gaps
    (so a simple threshold + findContours pass on the saved PNG cleanly
    re-isolates each one) and sit at their TRUE proportional vertical
    position within their source line, not individually re-centered."""
    max_w = max(c["raw"].shape[1] for _, c in rows)
    row_h = max(c["strip_h"] for _, c in rows)
    slot_w = max_w + pad_x
    canvas_w = slot_w * len(rows) + pad_x
    canvas_h = row_h + 2 * margin_y

    canvas = np.full((canvas_h, canvas_w, 3), bg_color, dtype=np.uint8)

    for i, (_ch, cand) in enumerate(rows):
        raw = cand["raw"]
        h, w = raw.shape[:2]
        x0 = pad_x + i * slot_w + (max_w - w) // 2
        y_frac = cand["y"] / cand["strip_h"]
        y0 = margin_y + int(round(y_frac * row_h))
        y0 = max(0, min(y0, canvas_h - h))
        canvas[y0:y0 + h, x0:x0 + w] = raw

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas)


def _write_lookup(lookup: dict[str, dict[int, str]]) -> None:
    body = {fname: {str(i): ch for i, ch in rows.items()} for fname, rows in lookup.items()}
    src = ("# auto-generated by debugs/build_glyph_reference.py — do not edit\n"
           '"""Left-to-right index -> glyph-character lookup for the\n'
           "glyph_daily_*.png reference atlases in this directory. No per-glyph\n"
           "coordinates are stored -- re-isolate glyphs from the PNG yourself via\n"
           "a plain threshold + cv2.findContours pass, sort by x, then look up\n"
           "each contour's position here. Regenerate via:\n"
           "    python debugs/build_glyph_reference.py\n"
           '"""\n'
           "DATA = " + json.dumps(body, indent=2) + "\n")
    _LOOKUP_F.write_text(src, encoding="utf-8")


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--images", default="single/*.png",
                        help="Glob of daily-GS images to use [default: single/*.png]")
    args = parser.parse_args()

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                         if "debug" not in Path(p).stem)
    if not image_paths:
        print(f"No images matched: {args.images}", file=sys.stderr)
        sys.exit(1)

    lookup: dict[str, dict[int, str]] = {}

    # ── 1. score ─────────────────────────────────────────────────────────────
    print("Collecting daily-score glyph candidates ...")
    score_buckets, score_bg = collect_daily_score_glyphs(image_paths)
    score_ink_ref = _ink_ref_from_buckets(score_buckets)
    rows = []
    for d in _DIGITS:
        cands = score_buckets.get(d) or []
        if not cands:
            print(f"  WARNING: no score candidates for '{d}', skipping")
            continue
        # Nearest-to-OWN-corpus-centroid, not assets/fonts/score_digits.py's
        # template -- that template is trained purely from Weekly Gunsmoke
        # crops (docs/action_items.txt #12) and is not a meaningful "typical
        # shape" reference for this, Daily Gunsmoke's own, score font.
        centroid = _self_corpus_centroid(cands, (SCORE_NORM_W, SCORE_NORM_H))
        best, dist = _pick_by_centroid(cands, centroid,
                                       (SCORE_NORM_W, SCORE_NORM_H), score_ink_ref)
        print(f"  '{d}': {len(cands)} candidates, chose {best['source']} (dist={dist:.4f})")
        rows.append((d, best))
    make_atlas(rows, _aggregate_color(score_bg) or (0, 0, 0), _FONTS_DIR / "glyph_daily_score.png")
    lookup["glyph_daily_score.png"] = {i: ch for i, (ch, _) in enumerate(rows)}
    print(f"  -> {_FONTS_DIR / 'glyph_daily_score.png'}  ({len(rows)} glyphs)\n")

    # ── 2. header ────────────────────────────────────────────────────────────
    print("Collecting daily-header glyph candidates (this re-runs Tesseract "
          "per header crop, similar cost to assets/builders/build.py) ...")
    import assets.fonts.stat_header as header_tmpl
    header_buckets, header_dots, header_bg = collect_header_glyphs(image_paths)
    header_ink_ref = _ink_ref_from_buckets(header_buckets)
    rows = []
    for d in _DIGITS:
        cands = header_buckets.get(d) or []
        if not cands:
            print(f"  WARNING: no header candidates for '{d}', skipping")
            continue
        best, dist = _pick_by_centroid(cands, header_tmpl.DATA[d]["proj"],
                                       (NORM_W_VAL, NORM_H_VAL), header_ink_ref)
        print(f"  '{d}': {len(cands)} candidates, chose {best['source']} (dist={dist:.4f})")
        rows.append((d, best))
    if header_dots:
        best_dot = _pick_by_median_size(header_dots)
        print(f"  '.': {len(header_dots)} candidates, chose {best_dot['source']} (median-size pick)")
        rows.append((".", best_dot))
    else:
        print("  '.': no dot-sized blob ever found in a header crop -- omitted")
    for c in ("K", "M"):
        cands = header_buckets.get(c) or []
        if not cands:
            print(f"  WARNING: no header candidates for '{c}', skipping")
            continue
        best, dist = _pick_by_centroid(cands, header_tmpl.DATA[c]["proj"],
                                       (NORM_W_VAL, NORM_H_VAL), header_ink_ref)
        print(f"  '{c}': {len(cands)} candidates, chose {best['source']} (dist={dist:.4f})")
        rows.append((c, best))
    make_atlas(rows, _aggregate_color(header_bg) or (0, 0, 0), _FONTS_DIR / "glyph_daily_header.png")
    lookup["glyph_daily_header.png"] = {i: ch for i, (ch, _) in enumerate(rows)}
    print(f"  -> {_FONTS_DIR / 'glyph_daily_header.png'}  ({len(rows)} glyphs)\n")

    # ── 3 & 4. pct / val ─────────────────────────────────────────────────────
    print("Collecting daily stat-cell (pct/val) glyph candidates ...")
    gt_cache = _load_tess_gt_cache() or {}
    excluded_cells = _load_excluded_cells()
    cells = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache,
                           excluded_cells=excluded_cells)
    _apply_gt_overrides(cells)
    print(f"  {len(cells)} cells collected")
    pct_buckets, pct_dots, val_buckets, pct_bg, val_bg = collect_pct_val_glyphs(cells)
    pct_ink_ref = _ink_ref_from_buckets(pct_buckets)
    val_ink_ref = _ink_ref_from_buckets(val_buckets)

    import assets.fonts.stat_pct as pct_tmpl
    rows = []
    for d in _DIGITS:
        cands = pct_buckets.get(d) or []
        if not cands:
            print(f"  WARNING: no pct candidates for '{d}', skipping")
            continue
        best, dist = _pick_by_centroid(cands, pct_tmpl.DATA[d]["proj"],
                                       (NORM_W_PCT, NORM_H_PCT), pct_ink_ref)
        print(f"  pct '{d}': {len(cands)} candidates, chose {best['source']} (dist={dist:.4f})")
        rows.append((d, best))
    if pct_dots:
        best_dot = _pick_by_median_size(pct_dots)
        print(f"  pct '.': {len(pct_dots)} candidates, chose {best_dot['source']} (median-size pick)")
        rows.append((".", best_dot))
    else:
        print("  pct '.': no dot-sized blob found -- omitted")
    make_atlas(rows, _aggregate_color(pct_bg) or (0, 0, 0), _FONTS_DIR / "glyph_daily_pct.png")
    lookup["glyph_daily_pct.png"] = {i: ch for i, (ch, _) in enumerate(rows)}
    print(f"  -> {_FONTS_DIR / 'glyph_daily_pct.png'}  ({len(rows)} glyphs)\n")

    import assets.fonts.stat_val as val_tmpl
    rows = []
    for c in _DIGITS + ["K"]:
        cands = val_buckets.get(c) or []
        if not cands:
            print(f"  WARNING: no val candidates for '{c}', skipping")
            continue
        best, dist = _pick_by_centroid(cands, val_tmpl.DATA[c]["proj"],
                                       (NORM_W_VAL, NORM_H_VAL), val_ink_ref)
        print(f"  val '{c}': {len(cands)} candidates, chose {best['source']} (dist={dist:.4f})")
        rows.append((c, best))
    make_atlas(rows, _aggregate_color(val_bg) or (0, 0, 0), _FONTS_DIR / "glyph_daily_val.png")
    lookup["glyph_daily_val.png"] = {i: ch for i, (ch, _) in enumerate(rows)}
    print(f"  -> {_FONTS_DIR / 'glyph_daily_val.png'}  ({len(rows)} glyphs)")
    print("  ('.' and 'M' intentionally absent -- see module docstring)\n")

    _write_lookup(lookup)
    print(f"Lookup written -> {_LOOKUP_F}")


if __name__ == "__main__":
    main()
