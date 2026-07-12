# -*- coding: utf-8 -*-
"""
gfl2/calibration/calibrate_spread_gate.py -- re-derives gfl2/stat_ocr_fft.py's
SPREAD_Y_LO/HI, SPREAD_EXCESS_GATE, and TOP_BAND_7_GATE constants, the four
thresholds the noncircular_mode="spread_y" alternative needs (see the
REFLEX-VERTEX SPREAD and TOP-BAND SPATIAL GATE sections in
gfl2/stat_ocr_fft.py for the full investigation).

CORPUS-ONLY, no atlas mode -- unlike gfl2/calibration/calibrate_hierarchical.py's
leaf_235/leaf_47 (reference CENTROIDS, where a single atlas sample per digit
is a legitimate value), these three constants are INTERVAL/GATE thresholds.
calibrate_hierarchical.py's own module docstring already measured, not just
assumed, that a single-sample atlas cannot stand in for a threshold's real
within-class spread (vstroke_gate regressed full-corpus accuracy 86.6%->82.15%
despite looking clean at n=1) -- the same caution applies here, so this script
only ever takes --images, matching debugs/calibrate_gabor.py's own
--objective gate47/gate147 precedent for interval-style constants.

PIPELINE:
  1. Collect every labelled pct-line glyph across --images via the SAME
     label-aligned extraction build_templates() trains from
     (gfl2.stat_ocr_fft._extract_pct_digit_glyphs, fed by
     gfl2.stat_ocr._collect_cells) -- no reimplementation of extraction.
  2. Compute the exact raw feature values noncircular_mode="spread_y" itself
     uses, via the real functions imported from gfl2.stat_ocr_fft
     (_reflex_vertices, _spread_y, _hbar_features_sobel) -- no
     reimplementation of feature math.
  3. Sweep candidate thresholds (midpoints of sorted unique values) and pick
     the one maximizing Youden's J (recall - false_trigger) -- the same
     methodology debugs/calibrate_gabor.py's --objective gate47/gate147 and
     debugs/debug_isoperimetric_hierarchy_check.py already established for
     this project's OTHER interval-style constants (ISO_GATE_LO/HI,
     VSTROKE_GATE_LO/HI's original corpus-driven recalibration). This is
     deliberately NOT calibrate_hierarchical.py's simpler _gap_bounds
     (nearest-neighbor midpoint) -- spread_y.lo's own boundary has a REAL
     overlap (both {1,7} and '4' read spread_y==0 for a real fraction of
     glyphs), so a clean-gap midpoint approach doesn't apply; the sweep finds
     the best achievable trade-off despite that overlap instead of assuming
     one doesn't exist.
  4. Write the four derived values to
     gfl2/configs/daily_pct_spread_gate_calib.json.

TOP_BAND_7_GATE (2026-07-10, same-day follow-up): once _reflex_vertices()
already committed this pipeline to spatial-domain (contour-based) work for
the root split, isolating '7' within the concentrated {1,4,7} bucket via
sobel_max (a frequency-domain-derived merged-kernel convolution) was
re-examined -- a plain spatial box count (top `height` rows, full width,
cv2.countNonZero, no kernel at all) isolates '7' from {1,4} with a
PERFECT, clean margin (real min/max gap, not a sweep's razor edge -- see
docs/takeaways.txt #65 for why that distinction matters here). height is
swept the same way threshold candidates are (a small fixed set, not part
of the Youden's J search) since it changes the FEATURE itself, not just
where to cut it; the smallest height that still clears the margin is kept
by default to minimize pixels touched.

VALIDATION (2026-07-10, same-day): derived on a 71-image TRAIN split of
single/*.png (excluding the project's own 16-image held-out set, see
tests/inputs/daily/stat_data.py), then the full noncircular_mode="spread_y"
pipeline (which also reuses several ALREADY-shipped, separately-calibrated
constants -- production's {1,4,7} sobel line-split's '1' vs '4' step,
PAREN_CLOSE_3_GATE, SOBEL_MEAN_C2/C5) reached 100.00% (1259/1259) on the 16
held-out images never used to derive these four thresholds. Also 100.00%
(6792/6792) on the full corpus, at a measured ~6-7% classify-time
improvement over the pre-top-band-gate version (the '7'-isolation branch's
own cost alone dropped ~66%, since the merged-kernel Sobel convolution is
now skipped entirely whenever the top-band gate fires). See
docs/decisions.txt for the full investigation trail.

Usage:
    python -m gfl2.calibration.calibrate_spread_gate --images "single/*.png"
    python -m gfl2.calibration.calibrate_spread_gate --images "single/*.png" --eps 0.03
    python -m gfl2.calibration.calibrate_spread_gate --images "single/*.png" --top-band-heights 3,4,5,6
"""
from __future__ import annotations
import argparse
import glob as _glob
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _collect_cells, _load_tess_gt_cache
from gfl2.stat_ocr_fft import (
    _extract_pct_digit_glyphs, _reflex_vertices, _spread_y, _hbar_features_sobel,
    _top_band_count, SOBEL_MEAN_C2, SOBEL_MEAN_C5, SPREAD_Y_LO, SPREAD_Y_HI,
    SPREAD_EXCESS_GATE, SPREAD_EPS, TOP_BAND_HEIGHT, TOP_BAND_7_GATE,
)

_DEFAULT_CONFIG_DIR = _ROOT / "gfl2" / "configs"
_DEFAULT_OUTPUT = _DEFAULT_CONFIG_DIR / "daily_pct_spread_gate_calib.json"

_NONCIRCULAR_DIGITS = ("1", "2", "3", "4", "5", "7")


def collect_corpus_glyphs(image_paths: list, gt_cache: "dict | None" = None) -> "dict[str, list]":
    """{digit: [normalized glyph, ...]} across every labelled pct-line glyph
    in `image_paths`, same shape as calibrate_hierarchical.py's own
    collect_corpus_glyphs() -- kept as a separate copy (not imported) since
    the two calibration scripts target independent, unrelated constant
    groups and importing across them would create a coupling neither needs."""
    if gt_cache is None:
        gt_cache = _load_tess_gt_cache() or {}
    cells = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)

    gt_file = Path("tests/inputs/daily/stat_gt_overrides.json")
    if gt_file.exists():
        gt_overrides = json.loads(gt_file.read_text(encoding="utf-8"))
        for item in cells:
            ov = gt_overrides.get(item["source"])
            if ov and "pct" in ov:
                item["pct"] = ov["pct"]

    buckets: "dict[str, list]" = defaultdict(list)
    for item in cells:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, label in glyphs:
            if label in _NONCIRCULAR_DIGITS:
                buckets[label].append(norm)
    return buckets


def compute_raw_features(buckets: "dict[str, list]", eps_frac: float) -> "dict[str, dict[str, list]]":
    """Per-digit lists of spread_y and sobel-mean-distance-to-nearest(C2,C5)
    -- the two raw quantities every derive_* function below sweeps over.
    Lists, not means -- these are threshold derivations, which need the real
    per-glyph distribution, not a collapsed per-digit summary."""
    out = {}
    for d, glyphs in buckets.items():
        spread_y_vals = []
        dist_vals = []
        for g in glyphs:
            reflex_pts, _ = _reflex_vertices(g, eps_frac)
            spread_y_vals.append(_spread_y(reflex_pts))
            sobel_mean = float(_hbar_features_sobel(g)[0])
            dist_vals.append(min(abs(sobel_mean - SOBEL_MEAN_C2), abs(sobel_mean - SOBEL_MEAN_C5)))
        out[d] = {"spread_y": spread_y_vals, "dist_to_nearest": dist_vals}
    return out


def compute_top_band_counts(buckets: "dict[str, list]", heights: "list[int]") -> "dict[int, dict[str, list]]":
    """{height: {digit: [top_band_count, ...]}} for every candidate height --
    height changes the FEATURE itself (not just a threshold cut), so each
    one needs its own full per-glyph recomputation, unlike a plain
    threshold sweep over a fixed feature."""
    out = {}
    for h in heights:
        out[h] = {d: [_top_band_count(g, h) for g in glyphs] for d, glyphs in buckets.items()}
    return out


def _best_threshold(pos_vals: list, neg_vals: list, prefer_low_for_pos: bool) -> "tuple[float, float, float, float]":
    """Sweep candidate thresholds (midpoints of sorted unique values) and
    return (threshold, J, recall, false_trigger) maximizing Youden's J
    (recall - false_trigger) -- same convention as debugs/calibrate_gabor.py's
    --objective gate47/gate147 and debugs/debug_isoperimetric_hierarchy_check.py."""
    candidates = sorted(set(pos_vals) | set(neg_vals))
    best = (candidates[0] if candidates else 0.0, -2.0, 0.0, 0.0)
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
    return best


def derive_spread_y_lo(feats: "dict[str, dict[str, list]]") -> "tuple[dict, float, float]":
    """Boundary between concentrated ({1,7}) and in-between ('4'). A REAL
    overlap exists here (both read spread_y==0 for a real fraction of
    glyphs) -- the sweep finds the best achievable trade-off, not a clean
    gap; production's own {1,4,7} sobel line-split rescues whatever '4'
    still leaks through at inference time (see the REFLEX-VERTEX SPREAD
    section for why that rescue works regardless of how the glyph got
    routed here)."""
    pos = feats["1"]["spread_y"] + feats["7"]["spread_y"]
    neg = feats["4"]["spread_y"]
    t, j, recall, ft = _best_threshold(pos, neg, prefer_low_for_pos=True)
    return {"lo": round(t, 2)}, recall, ft


def derive_spread_y_hi(feats: "dict[str, dict[str, list]]") -> "tuple[dict, float, float]":
    """Boundary between {concentrated, in-between} ({1,4,7} pooled) and
    spread-out ({2,3,5})."""
    pos = feats["1"]["spread_y"] + feats["4"]["spread_y"] + feats["7"]["spread_y"]
    neg = feats["2"]["spread_y"] + feats["3"]["spread_y"] + feats["5"]["spread_y"]
    t, j, recall, ft = _best_threshold(pos, neg, prefer_low_for_pos=True)
    return {"hi": round(t, 2)}, recall, ft


def derive_spread_excess_gate(feats: "dict[str, dict[str, list]]") -> "tuple[dict, float, float]":
    """Boundary isolating '4' as an outlier (large distance to its nearest
    of SOBEL_MEAN_C2/C5) from real {2,3,5} (small distance) -- the rescue
    mechanism for '4' glyphs that leak into the spread-out bucket."""
    pos = feats["4"]["dist_to_nearest"]
    neg = feats["2"]["dist_to_nearest"] + feats["3"]["dist_to_nearest"] + feats["5"]["dist_to_nearest"]
    t, j, recall, ft = _best_threshold(pos, neg, prefer_low_for_pos=False)
    return {"gate": round(t, 2)}, recall, ft


def derive_top_band_7_gate(top_band_by_height: "dict[int, dict[str, list]]") -> "tuple[dict, float, float]":
    """Isolate '7' from {1,4} via top-band ink count -- picks the SMALLEST
    swept height that still reaches a perfect (or best available) recall/
    false_trigger trade-off, since a smaller crop is cheaper and there is
    no accuracy reason to prefer a larger one once the margin is clean.
    Reports the real min/max gap (not just the sweep's J score) so a
    razor-thin margin is visible before it's trusted -- see
    docs/takeaways.txt #65."""
    best = None  # (height, threshold, recall, false_trigger, gap)
    for h, per_digit in sorted(top_band_by_height.items()):  # smallest height first
        pos = per_digit["7"]
        neg = per_digit["1"] + per_digit["4"]
        t, j, recall, ft = _best_threshold(pos, neg, prefer_low_for_pos=False)
        gap = min(pos) - max(neg) if pos and neg else 0.0
        candidate = (h, t, recall, ft, gap)
        # replace only on a STRICTLY better J -- ties keep the smallest
        # height already in `best`, since heights are visited in order.
        if best is None or (recall - ft) > (best[2] - best[3]):
            best = candidate
    h, t, recall, ft, gap = best
    return {"height": h, "gate": round(t, 1)}, recall, ft


def print_summary(feats: "dict[str, dict[str, list]]", derived: dict,
                   metrics: "dict[str, tuple[float, float]]") -> None:
    import numpy as np
    print(f"{'digit':>5}  {'n':>6}  {'spread_y mean/median':>22}  {'dist_to_nearest mean/median':>28}")
    for d in _NONCIRCULAR_DIGITS:
        sy = np.array(feats[d]["spread_y"])
        dn = np.array(feats[d]["dist_to_nearest"])
        print(f"{d:>5}  {len(sy):>6}  {sy.mean():>10.2f} / {np.median(sy):<8.1f}  "
              f"{dn.mean():>14.0f} / {np.median(dn):<12.0f}")
    print()
    print("Derived vs current effective value (config if loaded, else hardcoded default):")
    r, ft = metrics["spread_y_lo"]
    print(f"  spread_y.lo       {derived['spread_y']['lo']:>14.2f}   (was {SPREAD_Y_LO})   "
          f"recall={r:.4f} false_trigger={ft:.4f}")
    r, ft = metrics["spread_y_hi"]
    print(f"  spread_y.hi       {derived['spread_y']['hi']:>14.2f}   (was {SPREAD_Y_HI})   "
          f"recall={r:.4f} false_trigger={ft:.4f}")
    r, ft = metrics["spread_excess_gate"]
    print(f"  spread_excess.gate {derived['spread_excess']['gate']:>13.0f}   (was {SPREAD_EXCESS_GATE:.0f})   "
          f"recall={r:.4f} false_trigger={ft:.4f}")
    r, ft = metrics["top_band_7_gate"]
    print(f"  top_band_7.height {derived['top_band_7']['height']:>15}   (was {TOP_BAND_HEIGHT})")
    print(f"  top_band_7.gate   {derived['top_band_7']['gate']:>15.1f}   (was {TOP_BAND_7_GATE})   "
          f"recall={r:.4f} false_trigger={ft:.4f}")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png",
                     help="Corpus glob (e.g. \"single/*.png\") -- required source of "
                          "real per-glyph distributions; there is no atlas mode for "
                          "these interval-style constants, see module docstring.")
    ap.add_argument("--eps", type=float, default=SPREAD_EPS,
                     help=f"approxPolyDP epsilon fraction (default {SPREAD_EPS}, "
                          f"matching known_issues.txt §29's established operating point)")
    ap.add_argument("--top-band-heights", default="3,4,5,6",
                     help="Comma-separated candidate heights (rows) to sweep for "
                          "top_band_7 -- picks the smallest with the best recall/"
                          "false_trigger trade-off (default: 3,4,5,6).")
    ap.add_argument("--output", default=None,
                     help=f"default: {_DEFAULT_OUTPUT}")
    args = ap.parse_args(argv)

    run_start = datetime.now().isoformat(timespec="seconds")
    print(f"Generated: {run_start}  (run start)")

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                          if "debug" not in Path(p).stem)
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    print(f"Collecting glyphs from {len(image_paths)} image(s) ...")
    buckets = collect_corpus_glyphs(image_paths)
    missing = [d for d in _NONCIRCULAR_DIGITS if d not in buckets]
    if missing:
        sys.exit(f"Corpus is missing digit(s) {missing} -- cannot calibrate.")
    print(f"  {sum(len(v) for v in buckets.values())} glyphs across "
          f"{len(buckets)} digits: { {d: len(buckets[d]) for d in _NONCIRCULAR_DIGITS} }")

    feats = compute_raw_features(buckets, args.eps)

    heights = [int(h) for h in args.top_band_heights.split(",")]
    top_band_by_height = compute_top_band_counts(buckets, heights)

    spread_y_lo, recall_lo, ft_lo = derive_spread_y_lo(feats)
    spread_y_hi, recall_hi, ft_hi = derive_spread_y_hi(feats)
    spread_excess, recall_ex, ft_ex = derive_spread_excess_gate(feats)
    top_band_7, recall_tb, ft_tb = derive_top_band_7_gate(top_band_by_height)

    derived = {
        "spread_y": {**spread_y_lo, **spread_y_hi},
        "spread_excess": spread_excess,
        "top_band_7": top_band_7,
    }
    metrics = {
        "spread_y_lo": (recall_lo, ft_lo),
        "spread_y_hi": (recall_hi, ft_hi),
        "spread_excess_gate": (recall_ex, ft_ex),
        "top_band_7_gate": (recall_tb, ft_tb),
    }
    print_summary(feats, derived, metrics)

    output_path = Path(args.output) if args.output else _DEFAULT_OUTPUT
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(derived)
    payload["generated"] = run_start
    payload["source_images"] = [p.name for p in image_paths]
    payload["eps_frac"] = args.eps
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {output_path}")


if __name__ == "__main__":
    main()
