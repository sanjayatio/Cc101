# -*- coding: utf-8 -*-
"""
debugs/debug_left_right_gate_147_235.py -- corpus validation of a NEW
candidate mechanism for the hierarchical classifier's non-circular branch
({1,2,3,4,5,7}, i.e. everything the isoperimetric root gate already
excludes {0,6,8,9} from -- docs/known_issues.txt §29), proposed as an
alternative to the shipped gabor_45 {1,4,7}-vs-{2,3,5} gate:

  STAGE 1 -- LEFT-ONLY CONCAVITY GATE: does the glyph's outer contour have
  at least one reflex (concave) vertex, with EVERY reflex vertex sitting
  LEFT of the glyph's own ink bounding-box center? Proposed split:
  {1,3,7} (left-only) vs {2,4,5} (not left-only -- a reflex vertex on the
  right, or on both sides). This is a SIDE test, not a COUNT test --
  unlike known_issues.txt §29's reflex-count gate (which put '4' in the
  wrong bucket relative to {1,7} because '4' can read the same count as
  the arc group), '4' is expected to fall out of {1,3,7} naturally here
  because its reflex vertex is not confined to the left.

  STAGE 2a -- WITHIN {1,3,7}: isolate '3' via the SPREAD of its LEFT-side
  reflex vertices ('3' is two stacked open-left curves -> 2 reflex points
  spread across the glyph's height; '1'/'7' -> 1 reflex point, no
  spread), then reuse the EXISTING production sobel-90 {1,4,7} line-split
  (LINE_SOBEL_MAX_C7/POOLED14 + the stroke-thickness confirmation gate,
  gfl2.stat_ocr_fft) UNMODIFIED for the remaining '1' vs '7' decision --
  restricted to just {1,7} here since '4' no longer reaches this branch.

  STAGE 2b -- WITHIN {2,4,5}: reuse the EXISTING sobel-90 MEAN centroids
  (SOBEL_MEAN_C2/C5, already shipped for the {2,3,5} leaf's {2,5} split)
  for a nearest-of-2 pick, but check whether '4' reliably lands as an
  OUTLIER (an "excess" band -- distance to its nearest of {C2,C5}
  noticeably larger than real '2'/'5' glyphs show) rather than needing a
  dedicated '4' centroid.

Real-corpus validation throughout (single/*.png via the same
gfl2.stat_ocr._collect_cells + gfl2.stat_ocr_fft._extract_pct_digit_glyphs
pipeline every other corpus-validation script in this project uses -- NOT
an n=1 atlas sample, per the lesson in docs/known_issues.txt §27/§29 and
docs/takeaways.txt #65 about thresholds that look clean on one sample but
don't generalize).

Standalone probe -- nothing here is wired into any classifier.

Usage:
    python debugs/debug_left_right_gate_147_235.py
    python debugs/debug_left_right_gate_147_235.py --images "single/*.png" --eps 0.03
"""
from __future__ import annotations
import argparse
import glob as _glob
import json
import sys
from pathlib import Path

import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _collect_cells, _load_tess_gt_cache
from gfl2.stat_ocr_fft import (
    _extract_pct_digit_glyphs, _hbar_features_sobel, _bar_thickness,
    SOBEL_MEAN_C2, SOBEL_MEAN_C5, LINE_SOBEL_MAX_C7, LINE_SOBEL_MAX_POOLED14,
    LINE_THICKNESS_GATE_MIN_C7, LINE7_THICKNESS_ROW_BAND,
)
from debugs.debug_approx_poly_dp import _find_outer_and_holes, _padded_mask

GROUP_137 = {"1", "3", "7"}
GROUP_245 = {"2", "4", "5"}
ALL_DIGITS = GROUP_137 | GROUP_245

EPS_SWEEP = [0.02, 0.03, 0.05]


# ── Reflex vertices with side (left/right of ink center) ────────────────────

def _reflex_vertices_with_side(bin_glyph: np.ndarray, eps_frac: float):
    """Returns (reflex_pts (N,2) float array in padded-image coords, or
    None if no outer contour, ink_center_x) for one already-binarized,
    no-resize-padded glyph crop -- same _padded_mask/_find_outer_and_holes
    primitives debugs/debug_approx_poly_dp*.py already use."""
    padded = _padded_mask(bin_glyph)
    outer, holes = _find_outer_and_holes(padded)
    if outer is None:
        return None, None
    x, y, w, h = cv2.boundingRect(outer)
    ink_center_x = x + w / 2.0

    perim = cv2.arcLength(outer, True)
    eps = max(eps_frac * perim, 0.5)
    approx = cv2.approxPolyDP(outer, eps, True)
    pts = approx.reshape(-1, 2).astype(np.float64)
    n = len(pts)
    if n < 3:
        return np.empty((0, 2)), ink_center_x

    signed_area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
                       for i in range(n))
    overall_sign = 1.0 if signed_area >= 0 else -1.0
    reflex_pts = []
    for i in range(n):
        prev, cur, nxt = pts[i - 1], pts[i], pts[(i + 1) % n]
        v1, v2 = cur - prev, nxt - cur
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        if cross != 0 and (cross > 0) != (overall_sign > 0):
            reflex_pts.append(cur)
    return np.array(reflex_pts).reshape(-1, 2), ink_center_x


def _left_only(reflex_pts: "np.ndarray | None", ink_center_x: "float | None") -> "bool | None":
    if reflex_pts is None or ink_center_x is None or len(reflex_pts) == 0:
        return None
    n_left = int((reflex_pts[:, 0] < ink_center_x).sum())
    n_right = int((reflex_pts[:, 0] > ink_center_x).sum())
    return n_left > 0 and n_right == 0


def _spread_y(reflex_pts: "np.ndarray | None") -> float:
    if reflex_pts is None or len(reflex_pts) == 0:
        return 0.0
    return float(reflex_pts[:, 1].max() - reflex_pts[:, 1].min())


def _spread_x(reflex_pts: "np.ndarray | None") -> float:
    if reflex_pts is None or len(reflex_pts) == 0:
        return 0.0
    return float(reflex_pts[:, 0].max() - reflex_pts[:, 0].min())


# ── Corpus walk ───────────────────────────────────────────────────────────────

def collect_glyphs(image_paths: list[Path]) -> list[dict]:
    gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    gt_file = Path("tests/inputs/daily/stat_gt_overrides.json")
    if gt_file.exists():
        gt_overrides = json.loads(gt_file.read_text(encoding="utf-8"))
        for item in samples:
            ov = gt_overrides.get(item["source"])
            if ov and "pct" in ov:
                item["pct"] = ov["pct"]
    samples = sorted(samples, key=lambda it: it["source"])

    rows = []
    for item in samples:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, label in glyphs:
            if label not in ALL_DIGITS:
                continue
            rows.append({"source": item["source"], "label": label, "norm": norm})
    return rows


def _recall_false_trigger(flags: dict, positive_group: set) -> tuple[float, float]:
    """flags: {digit: [bool,...]} -- recall over positive_group's Trues,
    false_trigger over the complement group's Trues."""
    pos = [v for d in positive_group for v in flags.get(d, [])]
    neg = [v for d in (ALL_DIGITS - positive_group) for v in flags.get(d, [])]
    recall = (sum(pos) / len(pos)) if pos else float("nan")
    false_trigger = (sum(neg) / len(neg)) if neg else float("nan")
    return recall, false_trigger


def _best_threshold(pos_vals: list, neg_vals: list, prefer_low_for_pos: bool):
    """Sweep candidate thresholds (midpoints of sorted unique values) and
    return the one maximizing recall-false_trigger (Youden's J), matching
    this project's established sweep convention (calibrate_gabor.py
    --objective gate47/gate147, debugs/debug_isoperimetric_hierarchy_check.py)."""
    candidates = sorted(set(pos_vals) | set(neg_vals))
    best = (None, -2.0, None, None)
    for i in range(len(candidates) - 1):
        t = (candidates[i] + candidates[i + 1]) / 2.0
        if prefer_low_for_pos:
            recall = sum(1 for v in pos_vals if v <= t) / len(pos_vals) if pos_vals else 0.0
            false_trigger = sum(1 for v in neg_vals if v <= t) / len(neg_vals) if neg_vals else 0.0
        else:
            recall = sum(1 for v in pos_vals if v >= t) / len(pos_vals) if pos_vals else 0.0
            false_trigger = sum(1 for v in neg_vals if v >= t) / len(neg_vals) if neg_vals else 0.0
        j = recall - false_trigger
        if j > best[1]:
            best = (t, j, recall, false_trigger)
    return best  # (threshold, J, recall, false_trigger)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    ap.add_argument("--eps", type=float, default=None,
                     help="single epsilon fraction to use; default sweeps %s" % EPS_SWEEP)
    args = ap.parse_args(argv)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                         if "debug" not in Path(p).stem)
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    print(f"Collecting {{1,2,3,4,5,7}} glyphs from {len(image_paths)} image(s) ...")
    rows = collect_glyphs(image_paths)
    per_digit = {}
    for r in rows:
        per_digit.setdefault(r["label"], []).append(r)
    print("Per-digit counts: " + ", ".join(f"{d}={len(per_digit.get(d, []))}" for d in sorted(ALL_DIGITS)))

    eps_list = [args.eps] if args.eps is not None else EPS_SWEEP

    # ── STAGE 1: left-only concavity gate ────────────────────────────────────
    print("\n=== STAGE 1: LEFT-ONLY CONCAVITY GATE -- {1,3,7} (left-only) vs "
          "{2,4,5} (not left-only) ===")
    for eps in eps_list:
        flags = {}
        for d, items in per_digit.items():
            for it in items:
                reflex_pts, cx = _reflex_vertices_with_side(it["norm"], eps)
                it.setdefault("reflex", {})[eps] = reflex_pts
                it.setdefault("ink_cx", {})[eps] = cx
                flags.setdefault(d, []).append(_left_only(reflex_pts, cx))
        # drop None (no-contour) entries from recall/false_trigger denominators
        flags_clean = {d: [v for v in vs if v is not None] for d, vs in flags.items()}
        none_counts = {d: sum(1 for v in vs if v is None) for d, vs in flags.items()}
        recall, false_trigger = _recall_false_trigger(flags_clean, GROUP_137)
        print(f"  eps={eps:.2f}  recall(1,3,7 left-only)={recall:.4f}  "
              f"false_trigger(2,4,5 left-only)={false_trigger:.4f}  "
              f"no-contour={sum(none_counts.values())}")
        for d in sorted(ALL_DIGITS):
            vs = flags_clean.get(d, [])
            frac = (sum(vs) / len(vs)) if vs else float("nan")
            print(f"      '{d}': left_only_frac={frac:.4f}  n={len(vs)}")

    chosen_eps = eps_list[len(eps_list) // 2] if args.eps is None else args.eps
    print(f"\n(Using eps={chosen_eps:.2f} for stages 2a/2b below.)")

    # ── STAGE 2a: within {1,3,7} -- isolate '3' via reflex spread/count ──────
    print("\n=== STAGE 2a: WITHIN {1,3,7} -- isolate '3' via reflex-vertex spread/count ===")
    n_reflex_by_digit = {d: [] for d in GROUP_137}
    spread_by_digit = {d: [] for d in GROUP_137}
    for d in GROUP_137:
        for it in per_digit.get(d, []):
            reflex_pts = it.get("reflex", {}).get(chosen_eps)
            if reflex_pts is None:
                continue
            n_reflex_by_digit[d].append(len(reflex_pts))
            spread_by_digit[d].append(_spread_y(reflex_pts))
    for d in sorted(GROUP_137):
        nr = np.array(n_reflex_by_digit[d]) if n_reflex_by_digit[d] else np.array([0.0])
        sp = np.array(spread_by_digit[d]) if spread_by_digit[d] else np.array([0.0])
        print(f"  '{d}': n_reflex mean={nr.mean():.2f} median={np.median(nr):.1f}  "
              f"spread_y mean={sp.mean():.2f} median={np.median(sp):.1f}  n={len(nr)}")

    pos_spread = spread_by_digit["3"]
    neg_spread = spread_by_digit["1"] + spread_by_digit["7"]
    t, j, recall, ft = _best_threshold(pos_spread, neg_spread, prefer_low_for_pos=False)
    print(f"  best spread_y threshold isolating '3': >= {t:.2f}  "
          f"recall={recall:.4f}  false_trigger={ft:.4f}  (J={j:.4f})")

    pos_nr = n_reflex_by_digit["3"]
    neg_nr = n_reflex_by_digit["1"] + n_reflex_by_digit["7"]
    t2, j2, recall2, ft2 = _best_threshold(pos_nr, neg_nr, prefer_low_for_pos=False)
    print(f"  best n_reflex threshold isolating '3':    >= {t2:.2f}  "
          f"recall={recall2:.4f}  false_trigger={ft2:.4f}  (J={j2:.4f})")

    # ── STAGE 2a continued: reuse the EXISTING production 1-vs-7 sobel pipeline ──
    print("\n=== STAGE 2a continued: reuse EXISTING sobel line-split for '1' vs '7' "
          "(restricted to just {1,7}, no '4' in this pool) ===")
    correct = total = 0
    for d in ("1", "7"):
        for it in per_digit.get(d, []):
            norm = it["norm"]
            sobel_mean, sobel_max = _hbar_features_sobel(norm)
            pred = None
            if abs(sobel_max - LINE_SOBEL_MAX_C7) < abs(sobel_max - LINE_SOBEL_MAX_POOLED14):
                thickness = _bar_thickness(norm, LINE7_THICKNESS_ROW_BAND)
                if thickness >= LINE_THICKNESS_GATE_MIN_C7:
                    pred = "7"
            if pred is None:
                pred = "1"   # only {1,7} in this pool -- no '4' fallback needed
            total += 1
            correct += (pred == d)
    print(f"  1-vs-7 accuracy (existing sobel+thickness gate, {{4}} excluded): "
          f"{correct}/{total} ({100*correct/total:.2f}%)" if total else "  no data")

    # ── STAGE 2b: within {2,4,5} -- '2'/'5' via existing sobel-mean centroids,
    # '4' as an outlier/excess ──────────────────────────────────────────────────
    print("\n=== STAGE 2b: WITHIN {2,4,5} -- '2'/'5' via SOBEL_MEAN_C2/C5, "
          "'4' as excess ===")
    print(f"  shipped centroids: SOBEL_MEAN_C2={SOBEL_MEAN_C2:.0f}  "
          f"SOBEL_MEAN_C5={SOBEL_MEAN_C5:.0f}")
    sobel_mean_by_digit = {d: [] for d in GROUP_245}
    dist_to_nearest_by_digit = {d: [] for d in GROUP_245}
    for d in GROUP_245:
        for it in per_digit.get(d, []):
            sobel_mean = float(_hbar_features_sobel(it["norm"])[0])
            sobel_mean_by_digit[d].append(sobel_mean)
            dist = min(abs(sobel_mean - SOBEL_MEAN_C2), abs(sobel_mean - SOBEL_MEAN_C5))
            dist_to_nearest_by_digit[d].append(dist)
    for d in sorted(GROUP_245):
        sm = np.array(sobel_mean_by_digit[d]) if sobel_mean_by_digit[d] else np.array([0.0])
        dn = np.array(dist_to_nearest_by_digit[d]) if dist_to_nearest_by_digit[d] else np.array([0.0])
        print(f"  '{d}': sobel_mean mean={sm.mean():.0f} median={np.median(sm):.0f}  "
              f"dist_to_nearest_centroid mean={dn.mean():.0f} median={np.median(dn):.0f}  n={len(sm)}")

    correct = total = 0
    for d in ("2", "5"):
        for v in sobel_mean_by_digit[d]:
            pred = "2" if abs(v - SOBEL_MEAN_C2) < abs(v - SOBEL_MEAN_C5) else "5"
            total += 1
            correct += (pred == d)
    print(f"  2-vs-5 nearest-of-2 accuracy (excluding '4'): {correct}/{total} "
          f"({100*correct/total:.2f}%)" if total else "  no data")

    pos_excess = dist_to_nearest_by_digit["4"]
    neg_excess = dist_to_nearest_by_digit["2"] + dist_to_nearest_by_digit["5"]
    t3, j3, recall3, ft3 = _best_threshold(pos_excess, neg_excess, prefer_low_for_pos=False)
    print(f"  best excess threshold isolating '4' (dist_to_nearest >= {t3:.0f}): "
          f"recall={recall3:.4f}  false_trigger={ft3:.4f}  (J={j3:.4f})")


if __name__ == "__main__":
    main()
