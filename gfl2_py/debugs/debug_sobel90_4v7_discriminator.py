# -*- coding: utf-8 -*-
"""
debugs/debug_sobel90_4v7_discriminator.py -- finishes action_items.txt
#13's ORIGINAL ask (never completed by the {2,5,7} group-segregation
follow-up in docs/known_issues.txt §26's 2026-07-08 entry, which asked a
different question): can a 90deg Sobel kernel cleanly tell '4' FROM '7'
(a pairwise discriminator, not a "is this glyph in {group}" gate)?

WHY THIS IS A DIFFERENT QUESTION FROM THE {2,5,7} GATE: gating asks "is
this glyph in the target set or not" (accept/reject); discriminating asks
"given it's one of these two, WHICH one" (forced choice between exactly
two classes). A feature can be an excellent gate and a useless
discriminator, or vice versa -- known_issues.txt §24 already demonstrated
exactly this split for gabor_45 itself: useless at deciding WHICH of
'4'/'7' a glyph is (d'=0.213 on MEAN response, worse than the majority-
class baseline) but close to perfect at gating {1,4,7} vs the rest (same
raw values, different question, same script:
debugs/debug_gabor_45_zscore_verify.py). This script asks the
DISCRIMINATOR question of Sobel-90, mirroring that script's PART 1.

CURRENT PRODUCTION-ADJACENT BASELINE TO BEAT: gabor_45's MAX response
(decision 62) is the existing free second vote for '4' vs '7', standalone
d'=1.668, standalone forced-choice accuracy 80.8% (not "clean" alone --
it's used ALONGSIDE vstroke, agreeing 65.8% of the time at 100% accuracy
when they do). This script reports Sobel-90's numbers side by side with
that benchmark so "is this better than what's already used" is a direct
comparison, not a vibe.

METHOD: reuses debugs/debug_sobel90_257_group.py's real, many-sample
corpus extraction (collect_glyphs, compute_responses) UNCHANGED -- same
12 (kernel_size in {3,5}, n in {1,2,3}, aggregation in {mean,max}) combos,
same synthetic orientation-selectivity pre-check. For each combo:
  d'                  = (mean4 - mean7) / pooled_std
  forced-choice acc   = nearest-centroid classification (|v-mean4| vs
                         |v-mean7|) over the REAL pooled '4'+'7' glyphs,
                         compared against the majority-class baseline.

Usage:
    python debugs/debug_sobel90_4v7_discriminator.py
    python debugs/debug_sobel90_4v7_discriminator.py --images "single/*.png"
"""
from __future__ import annotations
import argparse
import glob as _glob
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from debugs.debug_sobel90_257_group import (
    KERNELS, N_STAGES, collect_glyphs, compute_responses,
    merged_footprint, run_synthetic_check,
)
from debugs.persist_run_result import save_run_result

# Established benchmark this script's numbers should be compared against
# (docs/decisions.txt #62 / known_issues.txt §24/§25) -- the feature
# currently used as a free second vote for '4' vs '7' in production's
# (opt-in) hierarchical classifier.
GABOR45_MAX_BENCHMARK = {"d_prime": 1.668, "accuracy": 0.808}


def d_prime(v4: np.ndarray, v7: np.ndarray) -> float:
    pooled_std = np.sqrt((v4.std() ** 2 + v7.std() ** 2) / 2)
    return float((v4.mean() - v7.mean()) / pooled_std) if pooled_std > 0 else float("nan")


def forced_choice_accuracy(v4: np.ndarray, v7: np.ndarray) -> tuple[float, float]:
    """Nearest-centroid '4' vs '7' classification -- returns (accuracy,
    majority_class_baseline). Matches debugs/debug_gabor_45_zscore_verify.py's
    PART 1 methodology exactly, so the two are directly comparable."""
    mean4, mean7 = v4.mean(), v7.mean()
    correct4 = int(np.sum(np.abs(v4 - mean4) < np.abs(v4 - mean7)))
    correct7 = int(np.sum(np.abs(v7 - mean7) < np.abs(v7 - mean4)))
    total = len(v4) + len(v7)
    accuracy = (correct4 + correct7) / total
    baseline = max(len(v4), len(v7)) / total
    return accuracy, baseline


def summarize(responses: dict) -> list[dict]:
    rows = []
    for ksize in KERNELS:
        for n in range(1, N_STAGES + 1):
            for agg in ("mean", "max"):
                v4 = responses[ksize][n][agg]["4"]
                v7 = responses[ksize][n][agg]["7"]
                dp = d_prime(v4, v7)
                acc, baseline = forced_choice_accuracy(v4, v7)
                rows.append({
                    "ksize": ksize, "n": n, "agg": agg,
                    "footprint": merged_footprint(ksize, n),
                    "mean4": round(float(v4.mean()), 2), "std4": round(float(v4.std()), 2),
                    "mean7": round(float(v7.mean()), 2), "std7": round(float(v7.std()), 2),
                    "d_prime": round(dp, 3),
                    "accuracy": round(acc, 4),
                    "majority_baseline": round(baseline, 4),
                    "beats_gabor45_max": bool(abs(dp) > GABOR45_MAX_BENCHMARK["d_prime"]
                                               and acc > GABOR45_MAX_BENCHMARK["accuracy"]),
                    "n4": int(len(v4)), "n7": int(len(v7)),
                })
    return rows


def print_summary(rows: list[dict]) -> None:
    rows_sorted = sorted(rows, key=lambda r: (r["footprint"], r["ksize"], r["n"], r["agg"]))
    dprime_hdr = "d'"
    print(f"\n{'=' * 100}")
    print("'4' vs '7' PAIRWISE DISCRIMINATION -- ranked by cost (merged-kernel footprint)")
    print(f"{'=' * 100}")
    print(f"  benchmark to beat (gabor_45-MAX, decision 62): "
          f"d'={GABOR45_MAX_BENCHMARK['d_prime']}, accuracy={100*GABOR45_MAX_BENCHMARK['accuracy']:.1f}%\n")
    print(f"{'kernel':>7} {'n':>2} {'footprint':>9} {'agg':>5} {'mean4':>10} {'mean7':>10} "
          f"{dprime_hdr:>7} {'accuracy':>9} {'baseline':>9}  beats_benchmark")
    for r in rows_sorted:
        print(f"{r['ksize']:>6}x{r['ksize']} {r['n']:>2} {r['footprint']:>9} {r['agg']:>5} "
              f"{r['mean4']:>10.2f} {r['mean7']:>10.2f} {r['d_prime']:>7.3f} "
              f"{100*r['accuracy']:>8.1f}% {100*r['majority_baseline']:>8.1f}%  "
              f"{'YES' if r['beats_gabor45_max'] else 'no'}")

    winners = [r for r in rows_sorted if r["beats_gabor45_max"]]
    best_by_acc = max(rows_sorted, key=lambda r: r["accuracy"])

    print(f"\n{'=' * 100}")
    print("CONCLUSION")
    print(f"{'=' * 100}")
    if winners:
        cheapest = min(winners, key=lambda r: r["footprint"])
        print(f"  {len(winners)}/12 combo(s) beat BOTH gabor_45-MAX's d' and accuracy.")
        print(f"  CHEAPEST: {cheapest['ksize']}x{cheapest['ksize']} kernel, n={cheapest['n']} "
              f"({cheapest['agg']}), footprint {cheapest['footprint']}x{cheapest['footprint']}, "
              f"d'={cheapest['d_prime']}, accuracy={100*cheapest['accuracy']:.1f}%.")
    else:
        print("  NONE of the 12 combos beat gabor_45-MAX on both d' and accuracy.")
    print(f"\n  Best accuracy overall: {best_by_acc['ksize']}x{best_by_acc['ksize']} kernel, "
          f"n={best_by_acc['n']} ({best_by_acc['agg']}), "
          f"accuracy={100*best_by_acc['accuracy']:.1f}% "
          f"(majority baseline {100*best_by_acc['majority_baseline']:.1f}%), "
          f"d'={best_by_acc['d_prime']}.")
    print(f"\n  Verdict: Sobel-90 {'IS' if winners else 'is NOT'} a cleaner standalone '4'/'7' "
          f"discriminator than the existing gabor_45-MAX vote, on this in-sample corpus.")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    args = ap.parse_args(argv)

    run_synthetic_check()

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                          if "debug" not in Path(p).stem)
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    print(f"\nCollecting real pct-line glyphs from {len(image_paths)} image(s) ...")
    buckets = collect_glyphs(image_paths)
    print(f"  '4': {len(buckets['4'])} glyphs   '7': {len(buckets['7'])} glyphs")

    print(f"\nComputing iterated-Sobel responses for '4'/'7' "
          f"({len(buckets['4']) + len(buckets['7'])} glyphs x {len(KERNELS)} kernel sizes) ...")
    responses = compute_responses({"4": buckets["4"], "7": buckets["7"]})
    rows = summarize(responses)
    print_summary(rows)

    save_run_result({"pair": ["4", "7"], "rows": rows}, subdir="sobel90_4v7_runs")


if __name__ == "__main__":
    main()
