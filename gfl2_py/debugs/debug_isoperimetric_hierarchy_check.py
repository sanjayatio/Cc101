# -*- coding: utf-8 -*-
"""
debugs/debug_isoperimetric_hierarchy_check.py -- corpus-wide validation of
an alternate hierarchical-classifier root gate, proposed as a replacement
for gabor_45's {1,4,7}-vs-rest gate (docs/known_issues.txt §24/§25):

    isoperimetric ratio (4*pi*area / perimeter^2 of the outer contour)
    ├── low (non-circular): {1,2,3,4,5,7} -> approx-poly-dp reflex count
    │   ├── low reflex:  {1,4,7} -> existing branches (vstroke/sobel line-split)
    │   └── high reflex: {2,3,5} -> existing branches (paren_close + sobel)
    └── high (circular):  {0,6,8,9} -> inner-blob hole count (already production)
        ├── 1 hole: {0,6,9} -> existing branch (paren + loop)
        └── 2 holes: {8}

debugs/debug_approx_poly_dp.py already found this promising on ONE atlas
sample per digit (assets/fonts/glyph_daily_pct.png) -- solidity/circularity
cleanly split {0,6,8,9} from the rest with NO overlap, and reflex-vertex-
count at eps=0.03 cleanly split {1,4,7} from {2,3,5} with a gap of exactly
1. But docs/known_issues.txt §27's own history is explicit that this kind
of finding does NOT reliably generalize from n=1: leaf/CENTROID-style
constants derived from one atlas sample validated fine, but an
INTERVAL/GATE-style threshold (vstroke_gate) derived the same way looked
clean in isolation and still regressed glyph accuracy to 82.15% once
checked against the real corpus's actual within-class spread. A gate is
exactly what's being proposed here, so it gets exactly that same
corpus-wide check before being trusted, using the same Youden's J sweep
methodology as debugs/debug_gabor_45_zscore_verify.py and
debugs/debug_sobel90_4v7_discriminator.py.

Features are computed on the REAL classify-time representation --
_extract_pct_digit_glyphs's already-binarized, already-padded-no-resize
12x20 canvas (gfl2.stat_ocr_fft._pad_glyph_no_resize) -- not the atlas's
raw native crop, since that's what a real gate would actually see at
inference.

Standalone probe -- nothing here is wired into any classifier.

Usage:
    python debugs/debug_isoperimetric_hierarchy_check.py
    python debugs/debug_isoperimetric_hierarchy_check.py --images "single/*.png"
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
from gfl2.stat_ocr_fft import _extract_pct_digit_glyphs
from debugs.debug_approx_poly_dp import _find_outer_and_holes, _classify_vertices, _padded_mask

EPS_FRACS = [0.01, 0.02, 0.03, 0.05, 0.08]
MIN_HOLE_AREA = 2.0

CIRCLE_GROUP = {"0", "6", "8", "9"}
LINE_GROUP   = {"1", "4", "7"}
ARC_GROUP    = {"2", "3", "5"}


def _contour_shape_features(norm_bin: np.ndarray) -> "dict | None":
    # Real glyphs from _pad_glyph_no_resize can have ink touching the 12x20
    # canvas edge (center-CROPPED when native width > NORM_W_PCT, per
    # known_issues.txt §27's own corpus measurement -- 77% of real glyphs
    # are wider than 12px). A small background border keeps cv2.findContours
    # from tracing an artificial corner exactly along the crop boundary,
    # same reasoning debugs/debug_approx_poly_dp.py's atlas-crop path used.
    padded = _padded_mask(norm_bin)
    outer, holes = _find_outer_and_holes(padded)
    if outer is None:
        return None
    area = cv2.contourArea(outer)
    perim = cv2.arcLength(outer, True)
    if area <= 0 or perim <= 0:
        return None
    hull = cv2.convexHull(outer)
    hull_area = cv2.contourArea(hull)
    solidity = (area / hull_area) if hull_area > 0 else 0.0
    isoperimetric_ratio = (4 * np.pi * area) / (perim ** 2)  # 1.0 = perfect circle

    reflex = {}
    for frac in EPS_FRACS:
        eps = max(frac * perim, 0.5)
        approx = cv2.approxPolyDP(outer, eps, True)
        _, n_reflex = _classify_vertices(approx)
        reflex[frac] = n_reflex

    return {
        "solidity": solidity,
        "isoperimetric_ratio": isoperimetric_ratio,
        "hole_count": len(holes),
        "reflex": reflex,
    }


def collect_glyph_features(image_paths: list[Path]) -> dict[str, list[dict]]:
    gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    gt_file = Path("tests/inputs/daily/stat_gt_overrides.json")
    if gt_file.exists():
        gt_overrides = json.loads(gt_file.read_text(encoding="utf-8"))
        for item in samples:
            ov = gt_overrides.get(item["source"])
            if ov and "pct" in ov:
                item["pct"] = ov["pct"]

    buckets: dict[str, list[dict]] = {d: [] for d in "0123456789"}
    skipped = 0
    for item in samples:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, label in glyphs:
            feats = _contour_shape_features(norm)
            if feats is None:
                skipped += 1
                continue
            buckets.setdefault(label, []).append(feats)
    print(f"({skipped} glyphs skipped -- no outer contour found, e.g. blank/degenerate crop)")
    return buckets


def _best_gate(pos: np.ndarray, neg: np.ndarray, step: float):
    """Sweep [lo, hi] to maximize Youden's J (recall - false_trigger_rate) --
    same coarse exhaustive-grid convention as debugs/debug_gabor_45_zscore_verify.py."""
    best = None
    lo_range = np.arange(pos.min() - 5 * step, pos.mean(), step)
    hi_range = np.arange(pos.mean(), pos.max() + 5 * step, step)
    for lo in lo_range:
        for hi in hi_range:
            recall = float(np.mean((pos >= lo) & (pos <= hi)))
            false_trigger = float(np.mean((neg >= lo) & (neg <= hi)))
            j = recall - false_trigger
            if best is None or j > best[0]:
                best = (j, lo, hi, recall, false_trigger)
    return best


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    args = ap.parse_args(argv)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                         if "debug" not in Path(p).stem)
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    print(f"Collecting real glyphs from {len(image_paths)} image(s) ...")
    buckets = collect_glyph_features(image_paths)
    n_total = sum(len(v) for v in buckets.values())
    print(f"{n_total} glyphs collected across {len(image_paths)} images\n")

    # ── Per-digit distribution of solidity / isoperimetric ratio ────────────
    print(f"{'digit':>6} {'n':>6} {'solidity(mean/std)':>20} "
          f"{'isoperim(mean/std)':>20} {'holes(mode)':>12}")
    for d in "0123456789":
        v = buckets[d]
        if not v:
            print(f"{d:>6} {0:>6}  (no samples)")
            continue
        sol = np.array([f["solidity"] for f in v])
        iso = np.array([f["isoperimetric_ratio"] for f in v])
        holes = np.array([f["hole_count"] for f in v])
        mode_hole = int(np.bincount(holes).argmax())
        print(f"{d:>6} {len(v):>6} {sol.mean():>10.3f}/{sol.std():<8.3f} "
              f"{iso.mean():>10.3f}/{iso.std():<8.3f} {mode_hole:>12}")

    # ── ROOT GATE: isoperimetric ratio, {0,6,8,9} (circular) vs rest ────────
    circ = np.array([f["isoperimetric_ratio"] for d in CIRCLE_GROUP for f in buckets[d]])
    non_circ = np.array([f["isoperimetric_ratio"] for d in (LINE_GROUP | ARC_GROUP) for f in buckets[d]])
    j, lo, hi, recall, false_trigger = _best_gate(circ, non_circ, step=0.01)
    print(f"\nROOT GATE -- isoperimetric_ratio interval for {{0,6,8,9}} (n={len(circ)}) "
          f"vs {{1,2,3,4,5,7}} (n={len(non_circ)}):")
    print(f"  best interval [{lo:.3f}, {hi:.3f}]  recall={recall:.4f}  "
          f"false_trigger={false_trigger:.4f}  J={j:.4f}")

    # '4' specifically -- the digit hole_count alone cannot correctly route
    # (it shares hole_count==1 with {0,6,9}), the key claimed advantage of
    # this gate over a naive hole-count-first tree ordering.
    four_iso = np.array([f["isoperimetric_ratio"] for f in buckets["4"]])
    four_in_gate = float(np.mean((four_iso >= lo) & (four_iso <= hi)))
    print(f"  '4' isoperimetric_ratio: mean={four_iso.mean():.3f} std={four_iso.std():.3f}  "
          f"-- inside the {{0,6,8,9}} gate interval: {four_in_gate:.4f} "
          f"(want near 0.0 -- '4' must be REJECTED here, not accepted)")

    # ── SECOND-STAGE GATE: within {1,2,3,4,5,7} only, {1,4,7} vs {2,3,5} ────
    print(f"\nSECOND-STAGE GATE -- reflex-vertex-count, {{1,4,7}} vs {{2,3,5}} "
          f"(within the non-circular group only), swept across epsilon:")
    for frac in EPS_FRACS:
        line_r = np.array([f["reflex"][frac] for d in LINE_GROUP for f in buckets[d]])
        arc_r  = np.array([f["reflex"][frac] for d in ARC_GROUP for f in buckets[d]])
        j, lo, hi, recall, false_trigger = _best_gate(-arc_r, -line_r, step=1.0)
        # (negated so "arc" plays the role of `pos`/target-in-gate; report
        # thresholds back in original, non-negated reflex-count units)
        print(f"  e={frac:.2f}  {{1,4,7}} reflex mean={line_r.mean():.2f} "
              f"std={line_r.std():.2f}  {{2,3,5}} reflex mean={arc_r.mean():.2f} "
              f"std={arc_r.std():.2f}  best_split=[{-hi:.1f}, {-lo:.1f}] "
              f"recall={recall:.4f} false_trigger={false_trigger:.4f}")


if __name__ == "__main__":
    main()
