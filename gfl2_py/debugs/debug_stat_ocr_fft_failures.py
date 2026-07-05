# -*- coding: utf-8 -*-
"""
debugs/debug_stat_ocr_fft_failures.py -- per-FAILING-GLYPH debug table for
gfl2.stat_ocr_fft's two-agent classifier.

WHY THIS EXISTS: debugs/debug_gabor_features.py's table has one row per
DIGIT CLASS (a single canonical glyph for '0'-'9'), which is the right
shape for "does each feature look sane on a normal glyph."  It's the wrong
shape for "what does the classifier actually see on the glyphs it gets
wrong" -- gfl2.stat_ocr_fft.verify_glyphs() (docs/known_issues.txt §17-§20)
only tallies aggregate misclassified/unknown COUNTS per digit, with no
record of which specific glyph instance failed or what its intermediate
representations looked like.  This script closes that gap: it re-runs the
exact same real-pipeline classification verify_glyphs() does (same
StatOcrFft.load(), same _classify(), pair_tiebreak=off to match its
default run), keeps every glyph where the prediction was wrong or '?', and
renders one row per failure with the same "every feature side by side,
globally-scaled" convention as debug_gabor_features.py -- extended with
the features added since that script was written (loop_top/loop_bot,
vstroke, hbar_top/hbar_bottom).

Two separate output images (misclassified vs unknown) rather than one,
each with its OWN globally-shared scale -- mixing the two failure modes
into one shared scale would dilute the misclassified table's color range
against the much rarer unknown cases, or vice versa.

Usage:
    python debugs/debug_stat_ocr_fft_failures.py
    python debugs/debug_stat_ocr_fft_failures.py --images "single/*.png"
    python debugs/debug_stat_ocr_fft_failures.py --enable-pair-tiebreak
"""
from __future__ import annotations
import sys
import glob
import argparse
from pathlib import Path
import json
import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import (
    DOT_MAX_DIM, NORM_W_PCT, NORM_H_PCT,
    _binarize, _find_blobs, _filter_y_outliers, _find_percent_x_start,
    _collect_cells, _load_tess_gt_cache,
)
from gfl2.stat_ocr_padded import _normalize_glyph
from gfl2.stat_ocr_fft import (
    StatOcrFft, _classify, PAIR_TIEBREAK_DEFAULT,
    _GABOR_KERNELS, _GABOR_STEP, _GABOR_ANGLE_IDXS,
    _paren_templates, _loop_templates, _norm_xcorr,
    _fft_magnitudes, _make_hist, _ring_energies, N_BINS, N_RINGS,
    _vstroke_kernel, _hbar_kernel, _pct_strip_bottom,
)

DEFAULT_IMAGES = "single/*.png"
UPSCALE  = 8
ALPHA    = 0.55

CELL_W, CELL_H = 120, 170
LABEL_W  = 150
HEADER_H = 46
CAPTION_H = 20

_GT_FILE = _ROOT / "stat_gt_overrides.json"


# ── Glyph extraction (mirrors gfl2.stat_ocr_fft._extract_pct_digit_glyphs, ──
#    keeping the raw + binarized intermediate crops that function discards,
#    same duplication convention as debugs/debug_gabor_features.py)

def _extract_glyphs_verbose(cell: np.ndarray, pct_label: str):
    if not pct_label:
        return None
    expected = [c for c in pct_label if c.isdigit()]
    if not expected:
        return None

    ch = cell.shape[0]
    pct_strip = cell[: _pct_strip_bottom(ch), :]
    gray = cv2.cvtColor(pct_strip, cv2.COLOR_BGR2GRAY) if pct_strip.ndim == 3 else pct_strip
    thresh = _binarize(pct_strip)
    blobs = _filter_y_outliers(_find_blobs(thresh), threshold=12)
    if not blobs:
        return None

    sorted_x = sorted(blobs, key=lambda b: b[0])
    pct_x = _find_percent_x_start(sorted_x)
    digit_blobs = [
        (x, y, w, h) for (x, y, w, h) in sorted_x
        if (pct_x is None or x < pct_x)
        and not (w <= DOT_MAX_DIM and h <= DOT_MAX_DIM)
    ]
    if len(digit_blobs) != len(expected):
        return None

    out = []
    for (x, y, w, h), label in zip(digit_blobs, expected):
        bin_crop = thresh[y: y + h, x: x + w]
        if bin_crop.size == 0:
            return None
        raw_crop = gray[y: y + h, x: x + w]
        norm = _normalize_glyph(bin_crop, NORM_W_PCT, NORM_H_PCT)
        out.append({"label": label, "raw": raw_crop, "binarized": bin_crop, "normalized": norm})
    return out


def collect_failures(image_paths: list[Path], enable_pair_tiebreak: bool = False):
    """Re-run the real StatOcrFft classifier over every labelled pct-line
    glyph in image_paths (same corpus/labelling verify_glyphs() uses) and
    split failures into (misclassified, unknown) lists of per-glyph dicts
    carrying the raw/binarized/normalized crops plus source/position."""
    engine = StatOcrFft.load(enable_pair_tiebreak=enable_pair_tiebreak)
    templates = engine._pct

    gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)

    gt_overrides = json.loads(_GT_FILE.read_text()) if _GT_FILE.exists() else {}
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and "pct" in ov:
            item["pct"] = ov["pct"]

    misclassified, unknown = [], []
    for item in samples:
        glyphs = _extract_glyphs_verbose(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        full_pct = item.get("pct") or ""
        digit_char_positions = [i for i, c in enumerate(full_pct) if c.isdigit()]
        for idx, g in enumerate(glyphs):
            pred = _classify(g["normalized"], templates, enable_pair_tiebreak=enable_pair_tiebreak)
            if pred == g["label"]:
                continue
            char_index = digit_char_positions[idx] if idx < len(digit_char_positions) else None
            record = {
                **g,
                "source": item["source"], "pos": f"#{idx + 1}/{len(glyphs)}", "pred": pred,
                "full_pct": full_pct, "digit_index": idx + 1, "n_digits": len(glyphs),
                "char_index": char_index,
            }
            (unknown if pred == '?' else misclassified).append(record)
    return misclassified, unknown


def _write_manifest(records: list[dict], path: Path) -> None:
    """Companion JSON for a debug table -- one entry per row, in the SAME
    order as the PNG rows, carrying exact copy-pasteable identifiers
    (source key matching stat_gt_overrides.json's keys, full ground-truth
    pct string, and both the digit-only index used by
    _extract_pct_digit_glyphs and the literal character index into
    full_pct) so a correction can be reported/applied without retyping
    anything by hand from the image."""
    manifest = [
        {
            "row": i + 1,
            "source": rec["source"],
            "full_pct": rec["full_pct"],
            "digit_index": rec["digit_index"],
            "n_digits": rec["n_digits"],
            "char_index": rec["char_index"],
            "true": rec["label"],
            "pred": rec["pred"],
        }
        for i, rec in enumerate(records)
    ]
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


# ── Rendering helpers (shared style with debugs/debug_gabor_features.py / ──
#    debugs/debug_vstroke_feature.py -- duplicated rather than imported, per
#    this repo's own "debug scripts don't couple to each other" convention)

def _to_bgr(img: np.ndarray) -> np.ndarray:
    return img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def _fit_and_paste(canvas: np.ndarray, img_bgr: np.ndarray, x0: int, y0: int, w: int, h: int) -> None:
    ih, iw = img_bgr.shape[:2]
    scale = min(w / iw, h / ih)
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    resized = cv2.resize(img_bgr, (nw, nh), interpolation=cv2.INTER_NEAREST)
    ox, oy = x0 + (w - nw) // 2, y0 + (h - nh) // 2
    canvas[oy: oy + nh, ox: ox + nw] = resized


def _heatmap_overlay(norm_glyph: np.ndarray, response: np.ndarray, global_max: float) -> np.ndarray:
    mag = np.abs(response).astype(np.float64)
    scale = global_max if global_max > 1e-9 else 1.0
    mag_u8 = np.clip(mag / scale * 255, 0, 255).astype(np.uint8)
    heat = cv2.applyColorMap(mag_u8, cv2.COLORMAP_JET)
    base = _to_bgr(norm_glyph)
    return cv2.addWeighted(heat, ALPHA, base, 1 - ALPHA, 0)


def _template_overlay(norm_glyph, template, color, corr, corr_min, corr_max) -> np.ndarray:
    base = _to_bgr(norm_glyph).astype(np.float64)
    mask = (template > 0)
    rng = max(corr_max - corr_min, 1e-9)
    strength = float(np.clip((corr - corr_min) / rng, 0.0, 1.0))
    alpha = ALPHA * strength
    blended = base.copy()
    blended[mask] = base[mask] * (1 - alpha) + np.array(color, dtype=np.float64) * alpha
    return blended.astype(np.uint8)


def _kernel_overlay(norm_glyph, weight, best_xy, score, score_min, score_max) -> np.ndarray:
    """Sliding-window kernel (vstroke/hbar) drawn at its best-fit (x, y):
    ink cells tinted green, punish cell tinted red, opacity SCALED by score
    relative to the table-wide [score_min, score_max] -- same convention as
    _template_overlay, adapted from debugs/debug_vstroke_feature.py's
    _vstroke_overlay (generalized here to also serve hbar)."""
    kh, kw = weight.shape
    bx, by = best_xy
    base = _to_bgr(norm_glyph).astype(np.float64)
    out = base.copy()
    rng = max(score_max - score_min, 1e-9)
    strength = float(np.clip((score - score_min) / rng, 0.0, 1.0))
    alpha = ALPHA * strength
    green = np.array((0, 200, 0), dtype=np.float64)
    red = np.array((40, 40, 220), dtype=np.float64)
    window = out[by: by + kh, bx: bx + kw]
    sub_base = base[by: by + kh, bx: bx + kw]
    ink = weight > 0
    window[ink] = sub_base[ink] * (1 - alpha) + green * alpha
    punished = weight < 0
    if punished.any():
        window[punished] = sub_base[punished] * (1 - ALPHA) + red * ALPHA
    out[by: by + kh, bx: bx + kw] = window
    cv2.rectangle(out, (bx, by), (bx + kw - 1, by + kh - 1), (0, 0, 220), 1)
    return out.astype(np.uint8)


def _bar_chart(values, w, h, global_max, color=(180, 90, 0)) -> np.ndarray:
    img = np.full((h, w, 3), 250, dtype=np.uint8)
    n = len(values)
    bar_w = max(1, w // n)
    scale = global_max if global_max > 1e-9 else 1.0
    for i, v in enumerate(values):
        bh = int(np.clip(v / scale, 0, 1) * (h - 8))
        x0 = i * bar_w
        cv2.rectangle(img, (x0 + 1, h - 3 - bh), (x0 + max(1, bar_w - 1), h - 3), color, -1)
    cv2.line(img, (0, h - 3), (w, h - 3), (170, 170, 170), 1)
    return img


def _put_caption(canvas, text, x0, y0, w) -> None:
    if not text:
        return
    cv2.putText(canvas, text, (x0 + 4, y0 - 4), cv2.FONT_HERSHEY_SIMPLEX,
                0.38, (30, 30, 30), 1, cv2.LINE_AA)


def _slide_best_2d_pos(gray_norm: np.ndarray, weight: np.ndarray) -> tuple[float, tuple[int, int]]:
    """Same normalized-cross-correlation sliding search as
    gfl2.stat_ocr_fft._slide_best_2d (must match EXACTLY so the score shown
    here is the real feature value), but also returns the winning (x, y) so
    it can be drawn -- the production function only needs the max score."""
    h, w = gray_norm.shape
    kh, kw = weight.shape
    wf = weight.astype(np.float64).ravel()
    wf = wf - wf.mean()
    w_norm = np.linalg.norm(wf) + 1e-9
    best, best_xy = -1e9, (0, 0)
    for y0 in range(max(1, h - kh + 1)):
        for x0 in range(max(1, w - kw + 1)):
            sub = gray_norm[y0: y0 + kh, x0: x0 + kw].astype(np.float64).ravel()
            sub = sub - sub.mean()
            score = float(np.dot(sub, wf)) / (np.linalg.norm(sub) * w_norm + 1e-9)
            if score > best:
                best, best_xy = score, (x0, y0)
    return best, best_xy


# ── Table builder ────────────────────────────────────────────────────────────

_GABOR_ANGLE_LABELS = [f"gabor_{idx * 180 // _GABOR_STEP}deg" for idx in _GABOR_ANGLE_IDXS]

COLUMNS = (
    ["original_crop", "binarized_crop", "normalized_12x20"]
    + _GABOR_ANGLE_LABELS
    + ["paren_(", "paren_)", "loop_top", "loop_bot", "vstroke", "hbar_top", "hbar_bot",
       "hist (64 bins)", "ring (8 bins)"]
)


def _compute_raw(records: list[dict]) -> list[dict]:
    raw = []
    for rec in records:
        norm = rec["normalized"]
        f32 = norm.astype(np.float32)
        h, w = norm.shape

        gabor_resp = [np.abs(cv2.filter2D(f32, -1, k)) for k in _GABOR_KERNELS]

        open_t, close_t = _paren_templates(h, w)
        corr_open = _norm_xcorr(norm, open_t)
        corr_close = _norm_xcorr(norm, close_t)

        loop_top_t, loop_bot_t = _loop_templates(h, w)
        corr_loop_top = _norm_xcorr(norm, loop_top_t)
        corr_loop_bot = _norm_xcorr(norm, loop_bot_t)

        vs_score, vs_xy = _slide_best_2d_pos(norm, _vstroke_kernel())
        hb_top_score, hb_top_xy = _slide_best_2d_pos(norm, _hbar_kernel("top"))
        hb_bot_score, hb_bot_xy = _slide_best_2d_pos(norm, _hbar_kernel("bottom"))

        hist = _make_hist(_fft_magnitudes(norm), N_BINS)
        ring = _ring_energies(norm, N_RINGS)

        raw.append({
            "gabor_resp": gabor_resp, "open_t": open_t, "close_t": close_t,
            "corr_open": corr_open, "corr_close": corr_close,
            "loop_top_t": loop_top_t, "loop_bot_t": loop_bot_t,
            "corr_loop_top": corr_loop_top, "corr_loop_bot": corr_loop_bot,
            "vs_score": vs_score, "vs_xy": vs_xy,
            "hb_top_score": hb_top_score, "hb_top_xy": hb_top_xy,
            "hb_bot_score": hb_bot_score, "hb_bot_xy": hb_bot_xy,
            "hist": hist, "ring": ring,
        })
    return raw


def build_table(records: list[dict], title: str) -> "np.ndarray | None":
    if not records:
        return None
    raw = _compute_raw(records)

    gabor_global_max = max(
        (float(r.max()) for rr in raw for r in rr["gabor_resp"]), default=1.0
    )
    paren_corrs = [rr["corr_open"] for rr in raw] + [rr["corr_close"] for rr in raw]
    paren_min, paren_max = (min(paren_corrs), max(paren_corrs)) if paren_corrs else (0.0, 1.0)
    loop_corrs = [rr["corr_loop_top"] for rr in raw] + [rr["corr_loop_bot"] for rr in raw]
    loop_min, loop_max = (min(loop_corrs), max(loop_corrs)) if loop_corrs else (0.0, 1.0)
    vs_scores = [rr["vs_score"] for rr in raw]
    vs_min, vs_max = (min(vs_scores), max(vs_scores)) if vs_scores else (0.0, 1.0)
    hb_scores = [rr["hb_top_score"] for rr in raw] + [rr["hb_bot_score"] for rr in raw]
    hb_min, hb_max = (min(hb_scores), max(hb_scores)) if hb_scores else (0.0, 1.0)
    hist_global_max = max((float(rr["hist"].max()) for rr in raw), default=1.0)
    ring_global_max = max((float(rr["ring"].max()) for rr in raw), default=1.0)

    n_cols, n_rows = len(COLUMNS), len(records)
    W = LABEL_W + n_cols * CELL_W
    H = HEADER_H + n_rows * CELL_H
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)

    cv2.putText(canvas, title, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
    for j, name in enumerate(COLUMNS):
        x0 = LABEL_W + j * CELL_W
        cv2.putText(canvas, name, (x0 + 4, HEADER_H - 16), cv2.FONT_HERSHEY_SIMPLEX,
                    0.38, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (x0, 0), (x0, H), (210, 210, 210), 1)
    cv2.line(canvas, (0, HEADER_H), (W, HEADER_H), (150, 150, 150), 1)

    for i, (rec, rr) in enumerate(zip(records, raw)):
        y0 = HEADER_H + i * CELL_H
        cv2.line(canvas, (0, y0), (W, y0), (210, 210, 210), 1)

        pred_disp = "?" if rec["pred"] == '?' else f"'{rec['pred']}'"
        cv2.putText(canvas, f"row {i + 1}", (6, y0 + 12), cv2.FONT_HERSHEY_SIMPLEX,
                    0.32, (80, 80, 80), 1, cv2.LINE_AA)
        cv2.putText(canvas, f"true '{rec['label']}'", (6, y0 + 28), cv2.FONT_HERSHEY_SIMPLEX,
                    0.42, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas, f"pred {pred_disp}", (6, y0 + 38), cv2.FONT_HERSHEY_SIMPLEX,
                    0.42, (150, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas, rec["source"][:18], (6, y0 + 54), cv2.FONT_HERSHEY_SIMPLEX,
                    0.30, (120, 120, 120), 1, cv2.LINE_AA)
        cv2.putText(canvas, rec["pos"], (6, y0 + 68), cv2.FONT_HERSHEY_SIMPLEX,
                    0.30, (120, 120, 120), 1, cv2.LINE_AA)

        norm = rec["normalized"]
        cell_imgs, captions = [], []
        cell_imgs.append(_to_bgr(rec["raw"]));       captions.append("")
        cell_imgs.append(_to_bgr(rec["binarized"])); captions.append("")
        cell_imgs.append(_to_bgr(norm));             captions.append(f"{norm.shape[1]}x{norm.shape[0]}")

        for resp in rr["gabor_resp"]:
            cell_imgs.append(_heatmap_overlay(norm, resp, gabor_global_max))
            captions.append(f"mean={resp.mean():.3f}")

        cell_imgs.append(_template_overlay(norm, rr["open_t"], (0, 200, 0),
                                            rr["corr_open"], paren_min, paren_max))
        captions.append(f"corr={rr['corr_open']:.2f}")
        cell_imgs.append(_template_overlay(norm, rr["close_t"], (0, 0, 220),
                                            rr["corr_close"], paren_min, paren_max))
        captions.append(f"corr={rr['corr_close']:.2f}")

        cell_imgs.append(_template_overlay(norm, rr["loop_top_t"], (0, 200, 0),
                                            rr["corr_loop_top"], loop_min, loop_max))
        captions.append(f"corr={rr['corr_loop_top']:.2f}")
        cell_imgs.append(_template_overlay(norm, rr["loop_bot_t"], (0, 0, 220),
                                            rr["corr_loop_bot"], loop_min, loop_max))
        captions.append(f"corr={rr['corr_loop_bot']:.2f}")

        cell_imgs.append(_kernel_overlay(norm, _vstroke_kernel(), rr["vs_xy"],
                                          rr["vs_score"], vs_min, vs_max))
        captions.append(f"score={rr['vs_score']:.2f}")
        cell_imgs.append(_kernel_overlay(norm, _hbar_kernel("top"), rr["hb_top_xy"],
                                          rr["hb_top_score"], hb_min, hb_max))
        captions.append(f"score={rr['hb_top_score']:.2f}")
        cell_imgs.append(_kernel_overlay(norm, _hbar_kernel("bottom"), rr["hb_bot_xy"],
                                          rr["hb_bot_score"], hb_min, hb_max))
        captions.append(f"score={rr['hb_bot_score']:.2f}")

        cell_imgs.append(_bar_chart(rr["hist"], CELL_W - 8, CELL_H - CAPTION_H - 8, hist_global_max))
        captions.append(f"max={rr['hist'].max():.3f}")
        cell_imgs.append(_bar_chart(rr["ring"], CELL_W - 8, CELL_H - CAPTION_H - 8, ring_global_max,
                                     color=(0, 130, 180)))
        captions.append(f"max={rr['ring'].max():.3f}")

        for j, (img, cap) in enumerate(zip(cell_imgs, captions)):
            x0 = LABEL_W + j * CELL_W
            _fit_and_paste(canvas, img, x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)
            _put_caption(canvas, cap, x0, y0 + CELL_H, CELL_W)

    return canvas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default=DEFAULT_IMAGES,
                     help=f"glob of source images  [default: {DEFAULT_IMAGES}]")
    ap.add_argument("--enable-pair-tiebreak", action="store_true", default=PAIR_TIEBREAK_DEFAULT,
                     help="match StatOcrFft's --enable-pair-tiebreak (off by default)")
    ap.add_argument("--out-dir", default="tests/outputs/daily",
                     help="output directory  [default: tests/outputs/daily -- gitignored]")
    args = ap.parse_args(argv)

    image_paths = [Path(p) for p in sorted(glob.glob(args.images))]
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    misclassified, unknown = collect_failures(image_paths, enable_pair_tiebreak=args.enable_pair_tiebreak)
    print(f"Images: {len(image_paths)}  pair_tiebreak={'ON' if args.enable_pair_tiebreak else 'off'}")
    print(f"Misclassified glyphs: {len(misclassified)}   Unknown ('?') glyphs: {len(unknown)}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    mis_table = build_table(misclassified, f"MISCLASSIFIED ({len(misclassified)} glyphs)")
    if mis_table is not None:
        mis_path = out_dir / "stat_ocr_fft_misclassified.png"
        cv2.imwrite(str(mis_path), mis_table)
        print(f"Wrote {mis_table.shape[1]}x{mis_table.shape[0]} -> {mis_path}")
        mis_json = out_dir / "stat_ocr_fft_misclassified.json"
        _write_manifest(misclassified, mis_json)
        print(f"Wrote manifest -> {mis_json}")
    else:
        print("No misclassified glyphs -- nothing written.")

    unk_table = build_table(unknown, f"UNKNOWN / '?' ({len(unknown)} glyphs)")
    if unk_table is not None:
        unk_path = out_dir / "stat_ocr_fft_unknown.png"
        cv2.imwrite(str(unk_path), unk_table)
        print(f"Wrote {unk_table.shape[1]}x{unk_table.shape[0]} -> {unk_path}")
        unk_json = out_dir / "stat_ocr_fft_unknown.json"
        _write_manifest(unknown, unk_json)
        print(f"Wrote manifest -> {unk_json}")
    else:
        print("No unknown glyphs -- nothing written.")


if __name__ == "__main__":
    main()
