# -*- coding: utf-8 -*-
"""
debugs/debug_ring_hierarchy_check.py -- feasibility check for a branching/
hierarchical feature extractor: can `ring` (the cheap ~0.5ms/glyph radial
FFT-energy feature) alone, or ring+hist (both cheap), gate whether the
expensive vstroke/hbar sliding-window features (~81% of feature_extraction
time per known_issues.txt §19's timing breakdown) even need to run?

Two separate questions, since a real branching extractor needs BOTH to be
true to be a net win:
  1. GROUP recall: does ring/ring+hist reliably tell "this glyph is one of
     {0,6,8,9} (loop-dominant)" apart from the other six (line/mixed)?
     If recall is poor, the branch point itself is unreliable -- calling
     the expensive path unnecessary would misclassify glyphs that needed it.
  2. WITHIN-group accuracy: for glyphs correctly routed to the loop group,
     does ring/ring+hist alone (no vstroke/hbar) actually disambiguate
     0 vs 6 vs 8 vs 9, or does it just confirm group membership while
     still needing something else to pick the exact digit?

Uses the REAL compute_features() (production function, unmodified) on the
REAL training corpus (single/*.png via the Tesseract GT cache) -- not a
synthetic single-image sample -- then evaluates a nearest-centroid
classifier restricted to just the ring (and optionally hist) sub-vector.
IN-SAMPLE evaluation (same corpus builds centroids and is scored), matching
this project's own stated convention for stat_ocr_fft's --build/--verify
(see reference.txt sec 5.5) -- a feasibility check, not a generalization
claim.

DOES NOT TOUCH gfl2/stat_ocr_v0_2_0.py.

Usage:
    python debugs/debug_ring_hierarchy_check.py
    python debugs/debug_ring_hierarchy_check.py --images "single/*.png"
"""
from __future__ import annotations
import sys
import argparse
import glob as _glob
from collections import defaultdict
from pathlib import Path
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr_v0_1_0 import _load_tess_gt_cache
from gfl2.stat_ocr_v0_2_0 import (
    compute_features, N_BINS, _extract_pct_digit_glyphs,
)
from gfl2.stat_ocr_v0_1_0 import _collect_cells

LOOP_GROUP = ("0", "6", "8", "9")
LINE_GROUP = ("1", "2", "3", "4", "5", "7")
DIGITS = "0123456789"

# Index layout inside the 16-dim "gpr" slice (feat[N_BINS:]), per
# gfl2/stat_ocr_v0_2_0.py's own module-level comment:
#   0=gabor_45, 1=paren_(, 2=paren_), 3..10=ring(8), 11=loop_top,
#   12=loop_bot, 13=vstroke, 14=hbar_top, 15=hbar_bot
RING_SLICE = slice(3, 11)
PAREN_SLICE = slice(1, 3)


def collect_training_glyphs(image_paths, gt_cache=None):
    if gt_cache is None:
        gt_cache = _load_tess_gt_cache() or {}
    cells = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    buckets = defaultdict(list)
    for item in cells:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, label in glyphs:
            buckets[label].append(norm)
    return buckets


def _nearest(feat, centroids):
    dists = sorted((float(np.linalg.norm(feat - c)), d) for d, c in centroids.items())
    return dists[0][1]


def evaluate(buckets: dict, feature_name: str, extractor) -> dict:
    """extractor(full_feat_vector) -> reduced feature vector. Builds
    centroids from `extractor`'s output and classifies every training
    glyph by nearest centroid restricted to that reduced space."""
    feats = {d: np.array([extractor(compute_features(g)) for g in glyphs])
             for d, glyphs in buckets.items()}
    centroids = {d: f.mean(axis=0) for d, f in feats.items()}

    total = correct = 0
    group_total = group_correct = 0     # loop-group membership recall
    within_total = within_correct = 0   # exact digit accuracy, GIVEN correctly routed to loop group
    line_total = line_false_trigger = 0  # SAFETY: true line-group glyphs misrouted INTO loop-group
    confusion = defaultdict(lambda: defaultdict(int))

    for d, f in feats.items():
        for row in f:
            pred = _nearest(row, centroids)
            total += 1
            correct += int(pred == d)
            confusion[d][pred] += 1
            if d in LOOP_GROUP:
                group_total += 1
                pred_in_group = pred in LOOP_GROUP
                group_correct += int(pred_in_group)
                if pred_in_group:
                    within_total += 1
                    within_correct += int(pred == d)
            elif d in LINE_GROUP:
                line_total += 1
                line_false_trigger += int(pred in LOOP_GROUP)

    return {
        "feature": feature_name,
        "overall_accuracy": correct / total if total else 0.0,
        "loop_group_recall": group_correct / group_total if group_total else 0.0,
        "within_group_accuracy_given_routed": within_correct / within_total if within_total else 0.0,
        "line_group_false_trigger_rate": line_false_trigger / line_total if line_total else 0.0,
        "confusion": confusion,
    }


def print_report(result: dict):
    print(f"\n=== {result['feature']} ===")
    print(f"  overall 10-digit accuracy      : {result['overall_accuracy']*100:.1f}%")
    print(f"  loop-group {{0,6,8,9}} recall    : {result['loop_group_recall']*100:.1f}%  "
          f"(of glyphs truly in {{0,6,8,9}}, how many land in {{0,6,8,9}})")
    print(f"  within-group accuracy (given routed correctly): "
          f"{result['within_group_accuracy_given_routed']*100:.1f}%  "
          f"(among those, how many get the EXACT digit right)")
    print(f"  SAFETY -- line-group false-trigger rate: "
          f"{result['line_group_false_trigger_rate']*100:.1f}%  "
          f"(of true {{1,2,3,4,5,7}} glyphs, how many get misrouted INTO the loop-group branch)")
    if "stage2_invoked_fraction" in result:
        print(f"  stage-2 (ring+paren) invoked on: {result['stage2_invoked_fraction']*100:.1f}% of all glyphs")
    print(f"  per-digit confusion (loop-group rows + '4', the main confusor):")
    for d in LOOP_GROUP + ("4",):
        row = result["confusion"].get(d, {})
        total_d = sum(row.values())
        breakdown = ", ".join(f"{k}:{v}" for k, v in sorted(row.items(), key=lambda kv: -kv[1]))
        print(f"    '{d}' (n={total_d}): {breakdown}")


CONFUSABLE_SET = ("0", "4", "6", "8", "9")   # ring's actual confusion neighborhood for 6/9 includes '4'


def evaluate_cascade(buckets: dict) -> dict:
    """Two-stage cascade, not a flat feature concatenation -- this is the
    actual design being tested: (1) ring-only nearest centroid across all
    10 digits. (2) ONLY IF stage-1 lands in CONFUSABLE_SET ({0,4,6,8,9} --
    ring's real confusion neighborhood for 6/9, not just LOOP_GROUP, since
    a lot of true 6/9 get routed to '4' by ring alone) is paren introduced,
    re-deciding via ring+paren restricted to CONFUSABLE_SET candidates
    only. Digits ring routes to the clean line set {1,2,3,5,7} NEVER see
    paren at all -- this is the "paren shouldn't be a feature to consider
    with the presence of horizontal/vertical lines" constraint: paren only
    ever plugs in downstream of ring's own arc-ish branch, never mixed
    with a decision that's already confidently line-dominant."""
    gpr_by_digit = {d: [compute_features(g)[N_BINS:] for g in glyphs] for d, glyphs in buckets.items()}
    ring_by_digit = {d: [gpr[RING_SLICE] for gpr in gprs] for d, gprs in gpr_by_digit.items()}
    ring_paren_by_digit = {d: [np.concatenate([gpr[RING_SLICE], gpr[PAREN_SLICE]]) for gpr in gprs]
                           for d, gprs in gpr_by_digit.items()}

    centroids_ring = {d: np.mean(f, axis=0) for d, f in ring_by_digit.items()}
    centroids_ring_paren_confusable = {d: np.mean(f, axis=0) for d, f in ring_paren_by_digit.items()
                                        if d in CONFUSABLE_SET}

    total = correct = 0
    group_total = group_correct = 0
    within_total = within_correct = 0
    line_total = line_false_trigger = 0
    confusion = defaultdict(lambda: defaultdict(int))
    stage2_invoked = 0

    for d in buckets:
        for ring_feat, rp_feat in zip(ring_by_digit[d], ring_paren_by_digit[d]):
            pred1 = _nearest(ring_feat, centroids_ring)
            if pred1 in CONFUSABLE_SET:
                stage2_invoked += 1
                pred = _nearest(rp_feat, centroids_ring_paren_confusable)
            else:
                pred = pred1

            total += 1
            correct += int(pred == d)
            confusion[d][pred] += 1
            if d in LOOP_GROUP:
                group_total += 1
                pred_in_group = pred in LOOP_GROUP
                group_correct += int(pred_in_group)
                if pred_in_group:
                    within_total += 1
                    within_correct += int(pred == d)
            elif d in LINE_GROUP:
                line_total += 1
                line_false_trigger += int(pred in LOOP_GROUP)

    return {
        "feature": "CASCADE: ring -> (if in {0,4,6,8,9}) ring+paren",
        "overall_accuracy": correct / total if total else 0.0,
        "loop_group_recall": group_correct / group_total if group_total else 0.0,
        "within_group_accuracy_given_routed": within_correct / within_total if within_total else 0.0,
        "line_group_false_trigger_rate": line_false_trigger / line_total if line_total else 0.0,
        "confusion": confusion,
        "stage2_invoked_fraction": stage2_invoked / total if total else 0.0,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    ap.add_argument("--no-gt-cache", action="store_true")
    args = ap.parse_args(argv)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images) if "debug" not in Path(p).stem)
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    gt_cache = {} if args.no_gt_cache else (_load_tess_gt_cache() or {})
    if gt_cache:
        print(f"Using Tesseract GT cache: {len(gt_cache)} cells")

    print(f"Collecting training glyphs from {len(image_paths)} image(s) ...")
    buckets = collect_training_glyphs(image_paths, gt_cache=gt_cache)
    if not all(d in buckets for d in DIGITS):
        missing = [d for d in DIGITS if d not in buckets]
        sys.exit(f"Missing training samples for digit(s): {missing}")
    print(f"  {sum(len(v) for v in buckets.values())} glyphs across {len(buckets)} digits: "
          f"{ {d: len(v) for d, v in sorted(buckets.items())} }")

    results = []
    results.append(evaluate(buckets, "ring only (8d)", lambda f: f[N_BINS:][RING_SLICE]))
    results.append(evaluate(buckets, "paren only (2d)", lambda f: f[N_BINS:][PAREN_SLICE]))
    results.append(evaluate(buckets, "ring+paren, flat, ALL 10 digits (10d)",
                             lambda f: np.concatenate([f[N_BINS:][RING_SLICE], f[N_BINS:][PAREN_SLICE]])))
    results.append(evaluate_cascade(buckets))
    # full gpr (16d, no hist) as an upper-bound reference -- what ring is
    # being compared against if the branch decides NOT to skip vstroke/hbar
    results.append(evaluate(buckets, "full gpr (16d, incl. vstroke+hbar) [reference]",
                             lambda f: f[N_BINS:]))

    for r in results:
        print_report(r)


if __name__ == "__main__":
    main()
