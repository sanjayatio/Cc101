# -*- coding: utf-8 -*-
"""
debugs/debug_sobel0_vstroke_replacement.py -- direct follow-up to
debugs/debug_sobel0_147_group.py, reframed per direct feedback (2026-07-10):
that script asked whether a 0deg/vertical Sobel kernel could ELIMINATE '7'
from {1,4,7}, or SPLIT '1' vs '4' -- two questions that already assumed the
{1,4,7} grouping (and the gabor_45 gate that produces it) as given. This
script does NOT assume that grouping: yesterday's branching-decision-tree
work (known_issues.txt §25) was never re-examined against what a feature
ACTUALLY separates when shown the full 10-digit alphabet -- only against
the branch structure already chosen. The separation table below IS that
re-examination: sorting all ten digits by a feature's mean response is
literally what a branch/gate at that feature would look like, so a natural
gap between two clusters in the sorted list is a candidate branch in its
own right, not just evidence for or against the {1,4,7} branch that
already exists.

TWO GOALS, BOTH DIRECT INSTRUCTIONS:

1. Target vertical (0deg) Sobel as a DIRECT REPLACEMENT for
   gfl2/stat_ocr_fft.py's shipped `_vstroke_feature` -- the 2D-SLIDING,
   77-position punished matched filter that is the dominant cost of the
   hierarchical classifier's {1,4,7} branches (known_issues.txt §25's
   per-branch timing: 72% of hierarchical_branch time on ~35% of glyphs;
   action_items.txt #17 names vstroke as the suspected reason). Benchmark
   against vstroke's own REAL feature values (computed here via the actual
   shipped `_vstroke_feature`, not quoted from an old module comment).

2. Produce a SEPARATION TABLE -- one row per digit ('0'-'9'), sorted
   ascending by mean response, both the raw value and a 0-1 min-max-
   normalized value -- for vertical Sobel AND for every other feature
   pipeline already in this module EXCEPT gabor_45 (already exhaustively
   characterized elsewhere: known_issues.txt §24's d'=0.213 conclusive NO
   as a discriminator, and §24/§25's already-implemented gate/vote roles).
   ACROSS ALL TEN DIGITS, not pre-filtered to {1,4,7} -- the table itself
   is the candidate branch; pre-filtering to {1,4,7} would just re-ask the
   question the existing tree already answered instead of looking for a
   different one.

METHODOLOGY (same discipline as every other script in this exploration):
  - Real, many-sample corpus glyphs via debugs.debug_sobel90_257_group.
    collect_glyphs (NOT a single-atlas-glyph proxy), all ten digit buckets.
  - The 0deg/vertical Sobel kernels and their synthetic orientation-
    selectivity check are imported UNCHANGED from debug_sobel0_147_group.py
    (already validated there -- not re-derived here).
  - Same STRONG/USEFUL bars as every prior sweep in this project:
      STRONG: recall>=99%, false_trigger<=1% (the shipped vstroke gate's
              own real {1,4,7} result, known_issues.txt §24)
      USEFUL: |d'|>=1.0 (decision 62's gabor_45-MAX {4,7} second-vote)
    applied to the '1'-vs-every-other-digit split (vstroke's actual job),
    PLUS a one-way-ANOVA F-ratio across all ten classes as an overall
    separability score, so a feature that separates some OTHER pair/group
    well (not '1') doesn't get silently missed just because this session's
    motivating question is about vstroke specifically.
  - All feature values are computed from the SAME normalized 12x20
    binarized glyph crop every real classify() call would receive
    (collect_glyphs already returns exactly that representation).

Usage:
    python debugs/debug_sobel0_vstroke_replacement.py
    python debugs/debug_sobel0_vstroke_replacement.py --images "single/*.png"
"""
from __future__ import annotations
import argparse
import glob as _glob
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from debugs.debug_sobel0_147_group import (
    KERNELS as SOBEL0_KERNELS,
    N_STAGES,
    ALL_DIGITS,
    merged_footprint,
    _fft_stages,
    d_prime,
    best_gate,
    forced_choice_accuracy,
    run_synthetic_check,
    STRONG_RECALL_MIN,
    STRONG_FALSE_TRIGGER_MAX,
    USEFUL_DPRIME_MIN,
)
from debugs.debug_sobel90_257_group import collect_glyphs, _pad_with_margin
from debugs.persist_run_result import save_run_result
from gfl2.stat_ocr_fft import (
    _vstroke_feature,
    _paren_features,
    _loop_features,
    _ring_energies,
    _hbar_features,
    _hbar_features_sobel,
    VSTROKE_KERNEL_H,
    VSTROKE_KERNEL_W,
    HBAR_KERNEL_H,
    HBAR_KERNEL_W,
)

N_RING_BINS = 8
TARGET_DIGIT = "1"   # vstroke's own job: isolate '1' from everything else

# vstroke/hbar-sliding pay a real per-glyph search of (H-kh+1)*(W-kw+1)
# positions (NORM_H_PCT=20, NORM_W_PCT=12); every other feature here is ONE
# global pass (an FFT, a merged-kernel convolution, or a single normalized
# cross-correlation) -- cheap regardless of kernel size, same "cost" framing
# action_items.txt #15 already established for the Sobel-90 hbar swap.
_VSTROKE_POSITIONS = (20 - VSTROKE_KERNEL_H + 1) * (12 - VSTROKE_KERNEL_W + 1)
_HBAR_POSITIONS = (20 - HBAR_KERNEL_H + 1) * (12 - HBAR_KERNEL_W + 1)


def _bar(dp: float, recall: float, false_trigger: float) -> str:
    strong = recall >= STRONG_RECALL_MIN and false_trigger <= STRONG_FALSE_TRIGGER_MAX
    useful = abs(dp) >= USEFUL_DPRIME_MIN
    return "STRONG" if strong else ("useful" if useful else "")


def f_ratio(values_by_digit: dict) -> float:
    """One-way-ANOVA F-ratio (between-class variance / within-class
    variance) across ALL ten digit classes -- an overall separability
    score, independent of which single digit this session's own question
    happens to be about. Same convention as known_issues.txt §15's WEDGE/
    PAREN+RING per-dimension F-ratio measurements."""
    groups = [v for v in values_by_digit.values() if len(v)]
    all_vals = np.concatenate(groups)
    grand_mean = all_vals.mean()
    k = len(groups)
    n_total = len(all_vals)
    between = sum(len(v) * (v.mean() - grand_mean) ** 2 for v in groups) / max(k - 1, 1)
    within_ss = sum(((v - v.mean()) ** 2).sum() for v in groups)
    within = within_ss / max(n_total - k, 1)
    return float(between / within) if within > 0 else float("nan")


# ─────────────────────────────────────────────────────────────────────────
# PART 1 -- one unified per-glyph pass computing EVERY feature dimension
# this session is allowed to look at (all but gabor_45), across ALL TEN
# digits, so every table and every consensus check below is aligned to the
# exact same glyph -- not recomputed independently per feature.
# ─────────────────────────────────────────────────────────────────────────

def compute_all_features(buckets: dict, digits=ALL_DIGITS) -> list[dict]:
    records: list[dict] = []
    margins = {ksize: merged_footprint(ksize, N_STAGES) // 2 + 2 for ksize in SOBEL0_KERNELS}
    for d in digits:
        for norm in buckets[d]:
            rec: dict = {"digit": d}

            # -- vstroke (REAL shipped feature -- the baseline to beat) --
            rec["vstroke"] = float(_vstroke_feature(norm))

            # -- paren_(/paren_) --
            paren = _paren_features(norm)
            rec["paren_open"] = float(paren[0])
            rec["paren_close"] = float(paren[1])

            # -- loop_top/loop_bot --
            loop = _loop_features(norm)
            rec["loop_top"] = float(loop[0])
            rec["loop_bot"] = float(loop[1])

            # -- ring (8 radial FFT-energy bins) --
            ring = _ring_energies(norm)
            for i in range(N_RING_BINS):
                rec[f"ring_{i}"] = float(ring[i])

            # -- hbar, SLIDING mode (the shipped default) --
            hbar = _hbar_features(norm)
            rec["hbar_top"] = float(hbar[0])
            rec["hbar_bottom"] = float(hbar[1])

            # -- hbar, SOBEL mode (the collapsed-13x13-kernel global pass) --
            hbar_s = _hbar_features_sobel(norm)
            rec["hbar_sobel_mean"] = float(hbar_s[0])
            rec["hbar_sobel_max"] = float(hbar_s[1])

            # -- vertical (0deg) Sobel, iterated n=1..3, both kernel sizes --
            for ksize, kernel in SOBEL0_KERNELS.items():
                margin = margins[ksize]
                padded = _pad_with_margin(norm, margin)
                stages = _fft_stages(padded, kernel, margin, N_STAGES)
                for i, mag in enumerate(stages):
                    n = i + 1
                    rec[f"sobel0_{ksize}x{ksize}_n{n}_mean"] = float(mag.mean())
                    rec[f"sobel0_{ksize}x{ksize}_n{n}_max"] = float(mag.max())

            records.append(rec)
    return records


def _values_by_digit(records: list[dict], feature: str, digits=ALL_DIGITS) -> dict:
    return {d: np.array([r[feature] for r in records if r["digit"] == d]) for d in digits}


# ─────────────────────────────────────────────────────────────────────────
# PART 2 -- separation table: one row per digit ('0'-'9'), sorted ascending
# by mean -- THIS is the branch: a gap between two clusters in this sorted
# list is a candidate gate, independent of the {1,4,7} grouping already
# shipped. Raw value AND a 0-1 min-max-normalized value (normalized across
# all ten digit means).
# ─────────────────────────────────────────────────────────────────────────

def print_separation_table(name: str, values_by_digit: dict, digits=ALL_DIGITS) -> None:
    rows = []
    for d in digits:
        v = values_by_digit[d]
        if len(v) == 0:
            continue
        rows.append({"digit": d, "n": len(v), "mean": float(v.mean()), "std": float(v.std())})
    means = [r["mean"] for r in rows]
    lo, hi = min(means), max(means)
    span = (hi - lo) or 1e-9
    rows.sort(key=lambda r: r["mean"])
    print(f"\n  separation table: {name}")
    print(f"    {'digit':>6} {'n':>6} {'raw_mean':>14} {'std':>12} {'normalized':>11}")
    for r in rows:
        norm = (r["mean"] - lo) / span
        tag = " <- TARGET" if r["digit"] == TARGET_DIGIT else ""
        print(f"    {r['digit']:>6} {r['n']:>6} {r['mean']:>14.4f} {r['std']:>12.4f} {norm:>11.3f}{tag}")


def evaluate_feature(name: str, values_by_digit: dict, cost_tag: str,
                      target: str = TARGET_DIGIT) -> dict:
    """Score `name` on vstroke's REAL job: isolate TARGET_DIGIT ('1') from
    every OTHER digit in the full ten-digit alphabet (not just {4,7})."""
    pos = values_by_digit[target]
    neg = np.concatenate([v for d, v in values_by_digit.items() if d != target and len(v)])
    dp = d_prime(pos, neg)
    j, lo, hi, recall, ft = best_gate(pos, neg)
    acc, baseline = forced_choice_accuracy(pos, neg)
    return {
        "name": name, "cost": cost_tag, "d_prime": round(dp, 3),
        "gate_lo": round(lo, 3), "gate_hi": round(hi, 3),
        "recall": round(recall, 4), "false_trigger": round(ft, 4),
        "accuracy": round(acc, 4), "baseline": round(baseline, 4),
        "f_ratio": round(f_ratio(values_by_digit), 3),
        "bar": _bar(dp, recall, ft),
    }


def print_master_table(rows: list[dict]) -> None:
    rows_sorted = sorted(rows, key=lambda r: -abs(r["d_prime"]))
    print(f"\n{'=' * 118}")
    print(f"MASTER RANKING -- isolate '{TARGET_DIGIT}' from the OTHER NINE digits, sorted by |d'| descending")
    print(f"{'=' * 118}")
    print(f"{'feature':>24} {'cost':>10} {'d\'':>8} {'gate':>18} "
          f"{'recall':>8} {'false_trig':>11} {'accuracy':>9} {'F(10-cls)':>10}  bar")
    for r in rows_sorted:
        gate_str = f"[{r['gate_lo']:.2f},{r['gate_hi']:.2f}]"
        print(f"{r['name']:>24} {r['cost']:>10} {r['d_prime']:>8.3f} {gate_str:>18} "
              f"{100*r['recall']:>7.1f}% {100*r['false_trigger']:>10.2f}% "
              f"{100*r['accuracy']:>8.1f}% {r['f_ratio']:>10.2f}  {r['bar']}")


# ─────────────────────────────────────────────────────────────────────────
# PART 3 -- consensus check: can two weak (non-STRONG) signals combined
# reach vstroke's real accuracy, the same "agree/disagree" methodology
# decision 62 used for the {4,7} leaf's gabor-max+vstroke vote -- now
# scored against the FULL ten-digit population, not just {4,7}.
# ─────────────────────────────────────────────────────────────────────────

def _predict_target(value: float, mean_pos: float, mean_neg: float) -> bool:
    return abs(value - mean_pos) < abs(value - mean_neg)


def consensus_check(name_a: str, records: list[dict], name_b: str,
                     target: str = TARGET_DIGIT) -> dict:
    a_vals = _values_by_digit(records, name_a)
    b_vals = _values_by_digit(records, name_b)
    mean_pos_a = a_vals[target].mean()
    mean_neg_a = np.concatenate([v for d, v in a_vals.items() if d != target and len(v)]).mean()
    mean_pos_b = b_vals[target].mean()
    mean_neg_b = np.concatenate([v for d, v in b_vals.items() if d != target and len(v)]).mean()

    n_agree = n_agree_correct = n_disagree = n_disagree_correct_either = 0
    n_total = len(records)
    for r in records:
        truth_is_target = (r["digit"] == target)
        pred_a = _predict_target(r[name_a], mean_pos_a, mean_neg_a)
        pred_b = _predict_target(r[name_b], mean_pos_b, mean_neg_b)
        if pred_a == pred_b:
            n_agree += 1
            if pred_a == truth_is_target:
                n_agree_correct += 1
        else:
            n_disagree += 1
            if pred_a == truth_is_target or pred_b == truth_is_target:
                n_disagree_correct_either += 1

    return {
        "a": name_a, "b": name_b,
        "coverage": round(n_agree / n_total, 4),
        "accuracy_on_agree": round(n_agree_correct / n_agree, 4) if n_agree else float("nan"),
        "n_disagree": n_disagree,
        "disagree_recoverable_frac": round(n_disagree_correct_either / n_disagree, 4) if n_disagree else float("nan"),
    }


def print_consensus(results: list[dict]) -> None:
    print(f"\n{'=' * 100}")
    print(f"CONSENSUS CHECK -- do two independently-weak/useful signals agree often, and")
    print(f"correctly, on isolating '{TARGET_DIGIT}' from the other nine digits? (mirrors decision")
    print("62's {4,7} gabor-max + vstroke precedent)")
    print(f"{'=' * 100}")
    print(f"{'A':>20} {'B':>20} {'coverage':>10} {'acc@agree':>11} {'n_disagree':>11} {'recoverable':>12}")
    for r in results:
        print(f"{r['a']:>20} {r['b']:>20} {100*r['coverage']:>9.1f}% "
              f"{100*r['accuracy_on_agree']:>10.1f}% {r['n_disagree']:>11} "
              f"{100*r['disagree_recoverable_frac']:>11.1f}%")


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
    for d in ALL_DIGITS:
        print(f"  '{d}': {len(buckets[d])} glyphs")

    n_glyphs = sum(len(buckets[d]) for d in ALL_DIGITS)
    print(f"\nComputing every feature dimension (except gabor_45) for all "
          f"{n_glyphs} glyphs across all ten digits -- this includes the REAL "
          f"vstroke feature (2D-sliding, {_VSTROKE_POSITIONS} positions/glyph) "
          f"and hbar-sliding ({_HBAR_POSITIONS} positions/glyph x2), so this "
          f"may take a little while ...")
    records = compute_all_features(buckets)

    eval_rows = []

    print(f"\n{'=' * 72}")
    print("BASELINE TO BEAT -- REAL vstroke (2D-sliding punished matched filter)")
    print(f"{'=' * 72}")
    vstroke_vals = _values_by_digit(records, "vstroke")
    print_separation_table("vstroke (REAL, shipped)", vstroke_vals)
    eval_rows.append(evaluate_feature("vstroke", vstroke_vals, f"slide-{_VSTROKE_POSITIONS}"))

    print(f"\n{'=' * 72}")
    print("CANDIDATE REPLACEMENT -- vertical (0deg) Sobel, iterated, both aggregations")
    print(f"{'=' * 72}")
    for ksize in SOBEL0_KERNELS:
        for n in range(1, N_STAGES + 1):
            for agg in ("mean", "max"):
                fname = f"sobel0_{ksize}x{ksize}_n{n}_{agg}"
                vals = _values_by_digit(records, fname)
                footprint = merged_footprint(ksize, n)
                print_separation_table(f"{fname} (footprint {footprint}x{footprint}, global pass)", vals)
                eval_rows.append(evaluate_feature(fname, vals, f"global-{footprint}"))

    print(f"\n{'=' * 72}")
    print("OTHER EXISTING PIPELINES (except gabor_45) -- already-cheap global features")
    print(f"{'=' * 72}")
    other_features = ["paren_open", "paren_close", "loop_top", "loop_bot"] + \
                      [f"ring_{i}" for i in range(N_RING_BINS)] + \
                      ["hbar_top", "hbar_bottom", "hbar_sobel_mean", "hbar_sobel_max"]
    cost_tags = {
        "hbar_top": f"slide-{_HBAR_POSITIONS}", "hbar_bottom": f"slide-{_HBAR_POSITIONS}",
    }
    for fname in other_features:
        vals = _values_by_digit(records, fname)
        cost_tag = cost_tags.get(fname, "global-1")
        print_separation_table(fname, vals)
        eval_rows.append(evaluate_feature(fname, vals, cost_tag))

    print_master_table(eval_rows)

    strong = [r for r in eval_rows if r["bar"] == "STRONG"]
    useful = [r for r in eval_rows if r["bar"] in ("STRONG", "useful")]
    vstroke_row = next(r for r in eval_rows if r["name"] == "vstroke")

    print(f"\n{'=' * 100}")
    print(f"CONCLUSION -- can vertical Sobel (or any other cheap existing feature) "
          f"DIRECTLY REPLACE vstroke?")
    print(f"{'=' * 100}")
    print(f"  vstroke (REAL, shipped): d'={vstroke_row['d_prime']}, "
          f"recall={100*vstroke_row['recall']:.1f}%, "
          f"false_trigger={100*vstroke_row['false_trigger']:.2f}%, "
          f"accuracy={100*vstroke_row['accuracy']:.1f}%, bar={vstroke_row['bar'] or '(below useful)'}")
    non_vstroke_strong = [r for r in strong if r["name"] != "vstroke"]
    if non_vstroke_strong:
        print(f"  {len(non_vstroke_strong)} non-vstroke feature(s) ALSO clear the STRONG bar "
              f"-- a real, direct, cheaper replacement candidate exists:")
        for r in non_vstroke_strong:
            print(f"    {r['name']}: d'={r['d_prime']}, recall={100*r['recall']:.1f}%, "
                  f"false_trigger={100*r['false_trigger']:.2f}%, cost={r['cost']}")
    else:
        print("  NO non-vstroke feature clears the STRONG bar alone -- vertical Sobel "
              "cannot cleanly replace vstroke as a standalone gate on this corpus.")

    non_vstroke_useful = [r for r in useful if r["name"] != "vstroke" and r["bar"] != "STRONG"]
    if non_vstroke_useful:
        print(f"\n  {len(non_vstroke_useful)} non-vstroke feature(s) clear the USEFUL bar "
              f"(|d'|>=1.0) without being STRONG alone -- candidates for a consensus vote:")
        for r in sorted(non_vstroke_useful, key=lambda r: -abs(r["d_prime"])):
            print(f"    {r['name']}: d'={r['d_prime']}, accuracy={100*r['accuracy']:.1f}%, cost={r['cost']}")

    candidates = sorted([r for r in eval_rows if r["name"] != "vstroke"],
                         key=lambda r: -abs(r["d_prime"]))[:5]
    consensus_results = []
    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            consensus_results.append(
                consensus_check(candidates[i]["name"], records, candidates[j]["name"]))
    for c in candidates[:3]:
        consensus_results.append(consensus_check(c["name"], records, "vstroke"))
    print_consensus(consensus_results)

    if not non_vstroke_strong and not non_vstroke_useful:
        print(f"\n{'=' * 100}")
        print("Neither a standalone replacement nor a useful consensus partner was found "
              "among every existing feature pipeline (except gabor_45) on this corpus -- "
              "a genuinely NEW feature would be needed to replace vstroke's cost, not a "
              "recombination of what's already computed.")

    save_run_result(
        {
            "target_digit": TARGET_DIGIT,
            "n_glyphs": {d: len(buckets[d]) for d in ALL_DIGITS},
            "eval_rows": eval_rows,
            "consensus": consensus_results,
        },
        subdir="sobel0_vstroke_runs",
    )


if __name__ == "__main__":
    main()
