# -*- coding: utf-8 -*-
"""
debugs/debug_stat_ocr_v0_3_0_skeleton_235.py

INVESTIGATION (known_issues.txt §37, following on from the fb_d_20251019.png
p1_r2_col4 val-line miss): the {2,3,5} leaf in every v0_3_0-family engine's
classify tree (gfl2/stat_ocr_v0_3_0.py's pct AND val trees,
gfl2/score_ocr_v0_3_0.py, gfl2/header_ocr_v0_3_0.py) resolves '2' vs '3' vs
'5' via plain spatial ink-COUNT gates -- magnitude thresholds sitting on a
calibrated number. The val-line miss traced directly to one of these: a
single antialiased pixel pair near the shared adaptive binarization
threshold flipped _bottom_row_deficit from 3 (correct) to 1 (misroutes to
'2') for one real '5' glyph. Direct feedback: don't keep tuning magnitude
gates, which have repeatedly proven brittle in this codebase's own history
(known_issues.txt §31's own "'2'/'5' margin never widened" note, §36's
threshold-cache bug, and now this one) -- try a TOPOLOGICAL/structural
feature instead.

HYPOTHESIS (direct feedback, confirmed by hand on two real glyphs in-
conversation before this script was written -- a '5' from
fb_d_20251019.png p1_r2_col4's val line, and a '2' from the SAME cell's
own pct line "20.37", at two different physical scales):
  - '5': the TOP stroke's free end (skeleton endpoint) sits on the RIGHT;
    it connects into the rest of the glyph on the LEFT.
  - '5': the BOTTOM stroke's free end sits on the LEFT; it connects on
    the RIGHT.
  - '2' is the mirror image of both.
This is a connectivity/topology property (which end of a stroke is a
degree-1 skeleton endpoint vs. where it joins the rest of the glyph),
NOT a magnitude threshold.

WHY NOT cv2.approxPolyDP (already tried, known_issues.txt §29/§31): that
operates on the glyph's OUTER CONTOUR boundary (a polygon simplification
of the ink blob's silhouette), not a medial-axis skeleton -- it was never
capable of answering "which end of the top stroke is free" in the first
place. This script uses a REAL topological skeleton (thinning) instead.

METHOD: a from-scratch, dependency-free skeleton -- this project has no
scikit-image dependency (established policy, e.g. known_issues.txt
§18(b)'s hand-rolled multi-level Otsu) and cv2.ximgproc.thinning is NOT
available in this environment (confirmed: `import cv2.ximgproc` raises
ModuleNotFoundError -- plain opencv-python, not the contrib build).
Implements Zhang-Suen thinning (Zhang & Suen, 1984), vectorized over the
whole image per sub-iteration, plus a spur-pruning pass (short branches
from antialiasing/binarization jitter are a KNOWN risk -- known_issues.txt
§23's own RELATED IDEA note already predicted this exact failure mode for
a broken/noisy blob).

SCOPE: this run is against tests/inputs/daily/*.png -- the curated,
committed 18-image "meaningful" set (tests/inputs/daily/meaningful_images.py),
NOT the full single/*.png corpus -- deliberately, so results are
reproducible from a committed fixture and finish quickly. Covers ALL FOUR
v0_3_0-family glyph populations that have a real '2'/'3'/'5' digit:
  - score  (gfl2.score_ocr_v0_3_0._collect_score_crops / _extract_score_digit_glyphs)
  - header (gfl2.header_ocr_v0_3_0._collect_header_crops / _extract_header_digit_glyphs)
  - pct    (gfl2.stat_ocr_v0_3_0._extract_pct_digit_glyphs, via _collect_cells)
  - val    (gfl2.stat_ocr_v0_3_0._extract_val_digit_glyphs, via _collect_cells)
Each uses that engine's own real adaptive binarization -- the same raw-crop,
no-normalization representation each engine's classify()/classify_score()/
classify_header() actually receives.

STRESS TEST: also runs the skeleton+degree pipeline directly against
fb_d_20260315.png's known-corrupted p1_r3 cells (ghosted/double-exposure
capture, known_issues.txt §23) by bypassing stat_excluded_cells.json
(excluded_cells={}, same precedent as debugs/debug_outlier_cell_compare.py)
-- this is the required negative-control check flagged when
tests/inputs/daily/meaningful_images.py's fb_d_20260315.png entry was
elevated for exactly this purpose: does thinning a broken/ghosted blob
manufacture spurious endpoints/branches, as §23 predicted?

This script does NOT touch any gfl2/*.py production module -- pure
feasibility measurement before any wiring-in decision, per this project's
own "unit debug before integration" convention.

Usage:
    python debugs/debug_stat_ocr_v0_3_0_skeleton_235.py
"""
from __future__ import annotations
import argparse, glob as _glob, json, sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from gfl2.stat_ocr_v0_1_0 import _collect_cells, _load_tess_gt_cache
from gfl2.stat_ocr_v0_2_0 import _parse_panel_row
from gfl2.stat_ocr_v0_3_0 import _extract_pct_digit_glyphs, _extract_val_digit_glyphs
from gfl2.score_ocr_v0_3_0 import _collect_score_crops, _extract_score_digit_glyphs
from gfl2.header_ocr_v0_3_0 import _collect_header_crops, _extract_header_digit_glyphs

_DAILY_DIR = Path(__file__).parent.parent / "tests" / "inputs" / "daily"

TOP_FRAC = 0.35
BOT_FRAC = 0.35
MIN_SPUR_LEN = 2


# ── Zhang-Suen thinning (vectorized, no per-pixel Python loop) ─────────────

def _shift8(padded: np.ndarray):
    H, W = padded.shape[0] - 2, padded.shape[1] - 2
    p2 = padded[0:H,     1:W + 1]
    p3 = padded[0:H,     2:W + 2]
    p4 = padded[1:H + 1, 2:W + 2]
    p5 = padded[2:H + 2, 2:W + 2]
    p6 = padded[2:H + 2, 1:W + 1]
    p7 = padded[2:H + 2, 0:W]
    p8 = padded[1:H + 1, 0:W]
    p9 = padded[0:H,     0:W]
    return p2, p3, p4, p5, p6, p7, p8, p9


def _zs_removal_mask(img01: np.ndarray, step: int) -> np.ndarray:
    padded = np.pad(img01, 1, mode="constant")
    p2, p3, p4, p5, p6, p7, p8, p9 = _shift8(padded)
    B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
    seq = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
    A = np.zeros(img01.shape, dtype=np.int32)
    for i in range(8):
        A += ((seq[i] == 0) & (seq[i + 1] == 1)).astype(np.int32)
    common = (img01 == 1) & (B >= 2) & (B <= 6) & (A == 1)
    if step == 1:
        extra = (p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)
    else:
        extra = (p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0)
    return common & extra


def zhang_suen_thin(img01: np.ndarray) -> np.ndarray:
    """img01: 2D 0/1 array (1=ink). Returns thinned 0/1 skeleton."""
    img = img01.astype(np.uint8).copy()
    if img.size == 0 or img.sum() == 0:
        return img
    changed = True
    guard = 0
    while changed and guard < 200:  # guard: pathological input should never need this many rounds
        guard += 1
        changed = False
        rm1 = _zs_removal_mask(img, 1)
        if rm1.any():
            img[rm1] = 0
            changed = True
        rm2 = _zs_removal_mask(img, 2)
        if rm2.any():
            img[rm2] = 0
            changed = True
    return img


def skeleton_degree(skel01: np.ndarray) -> np.ndarray:
    """Per-pixel count of 8-connected skeleton neighbors (0 where not skeleton)."""
    if skel01.size == 0:
        return skel01.astype(np.int32)
    padded = np.pad(skel01.astype(np.int32), 1, mode="constant")
    windows = np.lib.stride_tricks.sliding_window_view(padded, (3, 3))
    neighbor_sum = windows.sum(axis=(2, 3)) - skel01.astype(np.int32)
    return neighbor_sum * skel01.astype(np.int32)


def _neighbors8(y, x, H, W):
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W:
                yield ny, nx


def prune_spurs(skel01: np.ndarray, min_len: int = MIN_SPUR_LEN, max_rounds: int = 5) -> np.ndarray:
    """Remove short branches (<=min_len pixels from an endpoint to the
    junction/endpoint it connects to) -- antialiasing/binarization jitter
    reliably produces these (known_issues.txt §23's own predicted failure
    mode for thinning a noisy blob)."""
    skel = skel01.copy()
    H, W = skel.shape
    for _ in range(max_rounds):
        deg = skeleton_degree(skel)
        endpoints = list(zip(*np.where(deg == 1)))
        if not endpoints:
            break
        removed_any = False
        for ep in endpoints:
            if skel[ep] == 0:
                continue
            path = [ep]
            visited = {ep}
            prev, cur = None, ep
            while True:
                nbrs = [n for n in _neighbors8(cur[0], cur[1], H, W)
                        if skel[n] and n != prev and n not in visited]
                if not nbrs:
                    break
                nxt = nbrs[0]
                path.append(nxt)
                visited.add(nxt)
                if deg[nxt] != 2:
                    break  # reached a junction (>=3) or another endpoint (1)
                prev, cur = cur, nxt
            terminal_is_junction = deg[path[-1]] >= 3
            branch_len = len(path) - (1 if terminal_is_junction else 0)
            if branch_len <= min_len:
                to_zero = path[:-1] if terminal_is_junction else path
                for p in to_zero:
                    skel[p] = 0
                removed_any = True
        if not removed_any:
            break
    return skel


# ── Endpoint-side feature ───────────────────────────────────────────────────

def _band_endpoint_side(deg: np.ndarray, y0: int, y1: int, w: int) -> str:
    """'left' / 'right' / 'none' (no endpoint in band) / 'multi' (>1 endpoint,
    ambiguous -- likely noise or a genuinely different digit shape)."""
    band = deg[y0:y1, :]
    ys, xs = np.where(band == 1)
    if len(xs) == 0:
        return "none"
    if len(xs) > 1:
        return "multi"
    x = xs[0]
    return "left" if x < w / 2 else "right"


def classify_endpoint_sides(crop01: np.ndarray, top_frac: float = TOP_FRAC,
                             bot_frac: float = BOT_FRAC, min_spur_len: int = MIN_SPUR_LEN) -> dict:
    h, w = crop01.shape
    skel_raw = zhang_suen_thin(crop01)
    skel = prune_spurs(skel_raw, min_len=min_spur_len)
    deg = skeleton_degree(skel)
    top_h = max(1, round(h * top_frac))
    bot_h = max(1, round(h * bot_frac))
    top_side = _band_endpoint_side(deg, 0, top_h, w)
    bot_side = _band_endpoint_side(deg, h - bot_h, h, w)

    if top_side == "right" and bot_side == "left":
        pred = "5"
    elif top_side == "left" and bot_side == "right":
        pred = "2"
    elif top_side == "left" and bot_side == "left":
        pred = "3"  # observed pattern, see pct-line results below -- not part of the original hypothesis
    else:
        pred = "?"
    return {
        "pred": pred, "top_side": top_side, "bot_side": bot_side,
        "skel_raw": skel_raw, "skel": skel, "deg": deg,
        "n_spurs_removed": int((skel_raw.astype(int) - skel.astype(int)).sum()),
    }


def _sanity_check():
    """Cross-check the vectorized thinning against the hand-verified '5'
    glyph from the conversation that motivated this script, before trusting
    it on anything else."""
    crop = np.array([
        [0,1,1,1,1,1,0],
        [1,1,0,0,0,0,0],
        [1,1,0,0,0,0,0],
        [1,1,0,0,0,0,0],
        [1,1,1,1,0,0,0],
        [1,1,1,1,1,1,0],
        [1,0,0,0,1,1,0],
        [0,0,0,0,0,1,1],
        [0,0,0,0,0,1,1],
        [0,0,0,0,0,1,1],
        [1,1,0,0,1,1,0],
        [1,1,1,1,1,1,0],
    ], dtype=np.uint8)
    r = classify_endpoint_sides(crop)
    assert r["top_side"] == "right", f"sanity check failed: top_side={r['top_side']!r}"
    assert r["bot_side"] == "left", f"sanity check failed: bot_side={r['bot_side']!r}"
    assert r["pred"] == "5", f"sanity check failed: pred={r['pred']!r}"
    print("Sanity check OK: known '5' glyph -> top=right, bot=left, pred='5'")


# ── Per-family glyph collection (each engine's own real extractor) ─────────

def _daily_images():
    return sorted(_DAILY_DIR.glob("*.png"))


def _collect_pct_val(image_paths, font: str) -> dict:
    """font: 'pct' or 'val'."""
    gt_cache = _load_tess_gt_cache() or {}
    gt_file = Path("tests/inputs/daily/stat_gt_overrides.json")
    gt_overrides = json.loads(gt_file.read_text(encoding="utf-8")) if gt_file.exists() else {}

    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and font in ov:
            item[font] = ov[font]

    out = {"2": [], "3": [], "5": []}
    for item in samples:
        label_str = item.get(font) or ""
        if font == "pct":
            glyphs = _extract_pct_digit_glyphs(item["cell"], label_str, thresh_cache={})
        else:
            glyphs = _extract_val_digit_glyphs(item["cell"], label_str, thresh_cache={})
        if not glyphs:
            continue
        panel, row = _parse_panel_row(item["source"])
        for idx, (crop, label) in enumerate(glyphs):
            if label in out:
                out[label].append((item["source"], f"{panel}_{row}", idx, (crop > 0).astype(np.uint8)))
    return out


def _collect_score(image_paths) -> dict:
    samples = _collect_score_crops(image_paths)
    out = {"2": [], "3": [], "5": []}
    for item in samples:
        glyphs = _extract_score_digit_glyphs(item["gray"], item["label"])
        if not glyphs:
            continue
        for idx, (crop, label) in enumerate(glyphs):
            if label in out:
                out[label].append((item["source"], "-", idx, (crop > 0).astype(np.uint8)))
    return out


def _collect_header(image_paths) -> dict:
    samples = _collect_header_crops(image_paths)
    out = {"2": [], "3": [], "5": []}
    for item in samples:
        glyphs = _extract_header_digit_glyphs(item["gray"], item["label"])
        if not glyphs:
            continue
        for idx, (crop, label) in enumerate(glyphs):
            if label in out:
                out[label].append((item["source"], "-", idx, (crop > 0).astype(np.uint8)))
    return out


def _evaluate(glyphs_by_digit: dict) -> dict:
    confusion = {}
    side_dist = {}
    for true_digit, items in glyphs_by_digit.items():
        confusion[true_digit] = {}
        side_dist[true_digit] = {}
        for (src, part, idx, crop01) in items:
            r = classify_endpoint_sides(crop01)
            confusion[true_digit][r["pred"]] = confusion[true_digit].get(r["pred"], 0) + 1
            key = f"({r['top_side']},{r['bot_side']})"
            side_dist[true_digit][key] = side_dist[true_digit].get(key, 0) + 1
    return {"confusion": confusion, "side_dist": side_dist,
            "n_samples": {d: len(v) for d, v in glyphs_by_digit.items()}}


def _print_family(name: str, result: dict):
    print(f"\n{'='*70}\n{name}\n{'='*70}")
    conf = result["confusion"]
    for d in ("2", "3", "5"):
        n = result["n_samples"].get(d, 0)
        correct = conf.get(d, {}).get(d, 0)
        print(f"  '{d}': {correct}/{n} correct  -- confusion: {conf.get(d, {})}")
    for d in ("2", "3", "5"):
        print(f"  '{d}' (top,bot) sides: {result['side_dist'].get(d, {})}")


# ── Stress test: fb_d_20260315.png's known-ghosted cell ─────────────────────

def stress_test_ghosted_cell():
    print(f"\n{'='*70}\nSTRESS TEST: fb_d_20260315.png p1_r3 (known ghosted capture, §23)\n{'='*70}")
    path = _DAILY_DIR / "fb_d_20260315.png"
    if not path.exists():
        print("  fb_d_20260315.png not found in tests/inputs/daily/ -- skipping.")
        return None

    samples = _collect_cells([path], tess_only=True, gt_cache=_load_tess_gt_cache() or {},
                              excluded_cells={})  # bypass exclusion -- inspecting the excluded cells is the point
    # _collect_cells' own "source" key is "<stem>_p<panel>_r<row>_col<col>" (no
    # separate "part" field) -- match on that combined key directly.
    hits = [s for s in samples if s["source"].startswith("fb_d_20260315_p1_r3_col")]
    if not hits:
        print("  No matching fb_d_20260315_p1_r3_col1..4 cells found.")
        return None

    results = []
    for item in hits:
        part = item["source"]
        for font, extractor in (("pct", _extract_pct_digit_glyphs), ("val", _extract_val_digit_glyphs)):
            label_str = item.get(font) or ""
            glyphs = extractor(item["cell"], label_str, thresh_cache={}) if label_str else None
            if not glyphs:
                print(f"  {part} [{font}]: no glyphs extracted (label={label_str!r}) -- "
                      f"consistent with known corruption (blob count won't match a ghosted/blank line).")
                continue
            for idx, (crop, label) in enumerate(glyphs):
                crop01 = (crop > 0).astype(np.uint8)
                r = classify_endpoint_sides(crop01)
                print(f"  {part} [{font}] digit#{idx+1} label={label!r}: "
                      f"pred={r['pred']!r} top={r['top_side']} bot={r['bot_side']} "
                      f"spurs_removed={r['n_spurs_removed']} skel_px={int(r['skel'].sum())}")
                results.append({
                    "part": part, "font": font, "digit_index": idx + 1, "label": label,
                    "pred": r["pred"], "top_side": r["top_side"], "bot_side": r["bot_side"],
                    "n_spurs_removed": r["n_spurs_removed"], "skel_px": int(r["skel"].sum()),
                })
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    args = ap.parse_args(argv)

    _sanity_check()

    image_paths = _daily_images()
    if not image_paths:
        print("No images in tests/inputs/daily/*.png", file=sys.stderr)
        sys.exit(1)
    print(f"Images (curated 'meaningful' set): {len(image_paths)}")

    results = {}
    results["score"] = _evaluate(_collect_score(image_paths))
    _print_family("SCORE", results["score"])

    results["header"] = _evaluate(_collect_header(image_paths))
    _print_family("HEADER", results["header"])

    results["pct"] = _evaluate(_collect_pct_val(image_paths, "pct"))
    _print_family("PCT", results["pct"])

    results["val"] = _evaluate(_collect_pct_val(image_paths, "val"))
    _print_family("VAL", results["val"])

    print(f"\n{'='*70}\nSUMMARY (correct/total per glyph per set)\n{'='*70}")
    header = f"{'set':8s} " + "  ".join(f"{d:>9s}" for d in ("2", "3", "5"))
    print(header)
    for name in ("score", "header", "pct", "val"):
        r = results[name]
        cells = []
        for d in ("2", "3", "5"):
            n = r["n_samples"].get(d, 0)
            c = r["confusion"].get(d, {}).get(d, 0)
            cells.append(f"{c:>4d}/{n:<4d}")
        print(f"{name:8s} " + "  ".join(cells))

    stress_test_ghosted_cell()


if __name__ == "__main__":
    main()
