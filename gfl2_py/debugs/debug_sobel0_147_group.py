# -*- coding: utf-8 -*-
"""
debugs/debug_sobel0_147_group.py -- follow-up to debugs/debug_sobel90_257_group.py
and debug_sobel90_4v7_discriminator.py, switching the probe kernel from
90deg (Sobel-Y, horizontal-edge detector, targets bars) to 0deg (Sobel-X,
VERTICAL-edge detector, targets vertical strokes), asking whether it can
segregate {'1','4','7'} -- the line-dominant group vstroke/gabor_45 already
gate as a group -- specifically:
  (a) can it cleanly ELIMINATE '7' from the group (7 has no real vertical
      stroke: a top bar + diagonal descender only)?
  (b) can it cleanly SPLIT '1' from '4' (both have a vertical stroke, but
      '4' also carries a diagonal and horizontal crossbar that '1' lacks)?

Same methodology as the 90deg exploration throughout: real, many-sample
corpus glyphs (not the single-atlas-glyph proxy earlier explorations in
this project used), a synthetic orientation-selectivity check BEFORE
trusting either kernel size on real data, MAX aggregation only (per
direct instruction -- the 90deg exploration's own "get the max, not the
mean" precedent, decisions.txt #62 / #67), and the SAME cost metric
(merged-kernel effective footprint) for ranking
combos by cost.

KERNELS:
  3x3 -- classic Sobel-X: [[-1,0,1],[-2,0,2],[-1,0,1]].
  5x5 -- the TRANSPOSE of debugs/debug_sobel90_pct_glyphs.py's own 5x5
         Sobel-Y kernel (itself OpenCV's generalized Sobel construction) --
         swapping which axis carries the binomial-smoothing factor
         ([1,4,6,4,1]) and which carries the central-difference derivative
         ([-1,-2,0,2,1]) turns a horizontal-edge detector into a vertical-
         edge detector. Not re-derived from scratch -- transposing a
         validated kernel is exact, not an approximation.

Usage:
    python debugs/debug_sobel0_147_group.py
    python debugs/debug_sobel0_147_group.py --images "single/*.png"
    python debugs/debug_sobel0_147_group.py --debug   # per-digit heatmap sanity table
"""
from __future__ import annotations
import argparse
import glob as _glob
import sys
from pathlib import Path

import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from debugs.debug_sobel45_pct_glyphs import _freq_response
from debugs.debug_sobel90_pct_glyphs import SOBEL_90 as SOBEL_90_5X5
from debugs.debug_sobel90_257_group import collect_glyphs, _pad_with_margin
from debugs.persist_run_result import save_run_result

N_STAGES = 3
ALL_DIGITS = "0123456789"

# Classic 3x3 Sobel-X (vertical-edge detector).
SOBEL_0_3X3 = np.array([
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1],
], dtype=np.float64)

# Exact transpose of the validated 5x5 Sobel-Y kernel -- swaps which axis
# carries the binomial smoothing vs the central-difference derivative.
SOBEL_0_5X5 = SOBEL_90_5X5.T.copy()

KERNELS = {3: SOBEL_0_3X3, 5: SOBEL_0_5X5}

STRONG_RECALL_MIN, STRONG_FALSE_TRIGGER_MAX = 0.99, 0.01
USEFUL_DPRIME_MIN = 1.0

# Benchmark this session's own '4'/'7' Sobel-90 discriminator hit, for a
# same-units comparison on the (differently-scoped) '1'/'4' question here.
GABOR45_MAX_BENCHMARK_ACC = 0.808


def merged_footprint(ksize: int, n: int) -> int:
    return n * (ksize - 1) + 1


def _fft_stages(padded: np.ndarray, kernel: np.ndarray, margin: int,
                 n_stages: int = N_STAGES) -> list[np.ndarray]:
    h, w = padded.shape
    G = np.fft.fft2(padded.astype(np.float64))
    K = _freq_response(kernel, (h, w))
    stages = []
    Kpow = np.ones_like(K)
    for _ in range(n_stages):
        Kpow = Kpow * K
        resp = np.fft.ifft2(G * Kpow)
        mag = np.abs(resp)[margin:h - margin, margin:w - margin]
        stages.append(mag)
    return stages


# ─────────────────────────────────────────────────────────────────────────
# PART 0 -- synthetic orientation-selectivity check (generic over which
# literal angle label wins -- only requires the two kernel sizes to AGREE,
# same discipline as debug_sobel90_257_group.py's own check).
# ─────────────────────────────────────────────────────────────────────────

def _synthetic_stroke(angle_deg: int, size: int = 24, thickness: int = 2) -> np.ndarray:
    canvas = np.zeros((size, size), dtype=np.uint8)
    cx = cy = size // 2
    r = size // 2 - 2
    theta = np.deg2rad(angle_deg)
    dx, dy = np.cos(theta), -np.sin(theta)
    p1 = (int(cx - dx * r), int(cy - dy * r))
    p2 = (int(cx + dx * r), int(cy + dy * r))
    cv2.line(canvas, p1, p2, 255, thickness, cv2.LINE_AA)
    return canvas


def run_synthetic_check() -> None:
    print(f"\n{'=' * 72}")
    print("PART 0 -- synthetic orientation-selectivity check (n=1 pass only)")
    print(f"{'=' * 72}")
    angles = (0, 45, 90, 135)
    print(f"{'kernel':>8} {'0deg':>10} {'45deg':>10} {'90deg':>10} {'135deg':>10}   peak/trough")
    peak_troughs = {}
    for ksize, kernel in KERNELS.items():
        margin = merged_footprint(ksize, 1) // 2 + 2
        means = []
        for angle in angles:
            stroke = _synthetic_stroke(angle)
            padded = _pad_with_margin(stroke, margin)
            stages = _fft_stages(padded, kernel, margin, n_stages=1)
            means.append(float(stages[0].mean()))
        peak_i, trough_i = int(np.argmax(means)), int(np.argmin(means))
        peak_troughs[ksize] = (angles[peak_i], angles[trough_i])
        print(f"{ksize:>7}x{ksize} " + "  ".join(f"{m:9.2f}" for m in means)
              + f"   peak={angles[peak_i]}deg trough={angles[trough_i]}deg")

    sizes = list(KERNELS)
    agree = peak_troughs[sizes[0]] == peak_troughs[sizes[1]]
    print(f"\nBoth kernel sizes {'AGREE' if agree else 'DISAGREE'} on peak/trough axis "
          f"({peak_troughs[sizes[0]]} vs {peak_troughs[sizes[1]]}).")
    if not agree:
        sys.exit("Synthetic check FAILED: kernel sizes disagree on orientation axis; "
                  "do not trust the real-glyph numbers below without investigating first.")


# ─────────────────────────────────────────────────────────────────────────
# PART 2 -- iterated-Sobel MAX response over the real corpus (max only,
# per direct instruction -- this session's own precedent already found
# max beats mean for the horizontal-Sobel {4,7} question).
# ─────────────────────────────────────────────────────────────────────────

def compute_max_responses(buckets: dict) -> dict:
    """responses[ksize][n][digit] -> np.ndarray of per-glyph MAX values."""
    responses = {ksize: {n: {} for n in range(1, N_STAGES + 1)} for ksize in KERNELS}
    for ksize, kernel in KERNELS.items():
        margin = merged_footprint(ksize, N_STAGES) // 2 + 2
        for digit, glyphs in buckets.items():
            maxes = [[] for _ in range(N_STAGES)]
            for norm in glyphs:
                padded = _pad_with_margin(norm, margin)
                stages = _fft_stages(padded, kernel, margin, N_STAGES)
                for i, mag in enumerate(stages):
                    maxes[i].append(float(mag.max()))
            for i in range(N_STAGES):
                n = i + 1
                responses[ksize][n][digit] = np.array(maxes[i]) if maxes[i] else np.array([0.0])
    return responses


def d_prime(pos: np.ndarray, neg: np.ndarray) -> float:
    pooled_std = np.sqrt((pos.std() ** 2 + neg.std() ** 2) / 2)
    return float((pos.mean() - neg.mean()) / pooled_std) if pooled_std > 0 else float("nan")


def best_gate(pos: np.ndarray, neg: np.ndarray, n_steps: int = 40):
    span = max(float(pos.max() - pos.min()), 1e-9)
    step = span / n_steps
    best = None
    for lo in np.arange(pos.min() - 3 * step, pos.mean(), step):
        for hi in np.arange(pos.mean(), pos.max() + 3 * step, step):
            recall = float(np.mean((pos >= lo) & (pos <= hi)))
            false_trigger = float(np.mean((neg >= lo) & (neg <= hi)))
            j = recall - false_trigger
            if best is None or j > best[0]:
                best = (j, float(lo), float(hi), recall, false_trigger)
    return best


def forced_choice_accuracy(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    mean_a, mean_b = a.mean(), b.mean()
    correct_a = int(np.sum(np.abs(a - mean_a) < np.abs(a - mean_b)))
    correct_b = int(np.sum(np.abs(b - mean_b) < np.abs(b - mean_a)))
    total = len(a) + len(b)
    return (correct_a + correct_b) / total, max(len(a), len(b)) / total


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
    for d in "147":
        print(f"  '{d}': {len(buckets[d])} glyphs")

    n_glyphs_147 = sum(len(buckets[d]) for d in "147")
    print(f"\nComputing iterated-Sobel MAX responses "
          f"({n_glyphs_147} {{1,4,7}} glyphs x {len(KERNELS)} kernel sizes) ...")
    responses = compute_max_responses({d: buckets[d] for d in "147"})

    print(f"\n{'=' * 100}")
    print("PER-DIGIT MAX RESPONSE (mean +/- std across corpus)")
    print(f"{'=' * 100}")
    for ksize in KERNELS:
        for n in range(1, N_STAGES + 1):
            vals = responses[ksize][n]
            print(f"  {ksize}x{ksize} n={n}: " +
                  "  ".join(f"'{d}' mean={vals[d].mean():12.2f} std={vals[d].std():10.2f}"
                            for d in "147"))

    # ── (a) eliminate '7' from {1,4,7} ──────────────────────────────────
    print(f"\n{'=' * 100}")
    print("(a) ELIMINATE '7' -- gate: pos='7', neg={'1','4'} pooled")
    print(f"{'=' * 100}")
    dprime_hdr = "d'"
    print(f"{'kernel':>7} {'n':>2} {'footprint':>9} {dprime_hdr:>8} {'gate':>20} "
          f"{'recall':>8} {'false_trig':>11} {'J':>7}  bar")
    rows_a = []
    for ksize in KERNELS:
        for n in range(1, N_STAGES + 1):
            vals = responses[ksize][n]
            pos, neg = vals['7'], np.concatenate([vals['1'], vals['4']])
            dp = d_prime(pos, neg)
            j, lo, hi, recall, ft = best_gate(pos, neg)
            strong = recall >= STRONG_RECALL_MIN and ft <= STRONG_FALSE_TRIGGER_MAX
            useful = abs(dp) >= USEFUL_DPRIME_MIN
            bar = "STRONG" if strong else ("useful" if useful else "")
            rows_a.append({"ksize": ksize, "n": n, "footprint": merged_footprint(ksize, n),
                            "d_prime": dp, "recall": recall, "false_trigger": ft, "bar": bar})
            print(f"{ksize:>6}x{ksize} {n:>2} {merged_footprint(ksize, n):>9} {dp:>8.3f} "
                  f"[{lo:.1f},{hi:.1f}]".rjust(20) +
                  f" {100*recall:>7.1f}% {100*ft:>10.2f}%       -  {bar}")

    strong_a = [r for r in rows_a if r["bar"] == "STRONG"]
    useful_a = [r for r in rows_a if r["bar"] in ("STRONG", "useful")]
    if strong_a:
        cheapest = min(strong_a, key=lambda r: r["footprint"])
        print(f"\n  CHEAPEST STRONG: {cheapest['ksize']}x{cheapest['ksize']} n={cheapest['n']} "
              f"(footprint {cheapest['footprint']}), recall={100*cheapest['recall']:.1f}%, "
              f"false_trigger={100*cheapest['false_trigger']:.2f}%")
    elif useful_a:
        cheapest = min(useful_a, key=lambda r: r["footprint"])
        print(f"\n  No STRONG combo. Cheapest USEFUL: {cheapest['ksize']}x{cheapest['ksize']} "
              f"n={cheapest['n']} (footprint {cheapest['footprint']}), d'={cheapest['d_prime']:.3f}")
    else:
        print("\n  NONE of the 6 combos clear even the USEFUL bar for eliminating '7'.")

    # ── (b) split '1' vs '4' ─────────────────────────────────────────────
    print(f"\n{'=' * 100}")
    print("(b) SPLIT '1' vs '4' -- forced-choice pairwise discrimination")
    print(f"{'=' * 100}")
    print(f"  benchmark: this session's Sobel-90 '4'/'7' discriminator hit "
          f"{100*GABOR45_MAX_BENCHMARK_ACC:.1f}% (gabor_45-MAX) / 100.0% (best Sobel-90 combo)")
    print(f"{'kernel':>7} {'n':>2} {'footprint':>9} {'mean1':>12} {'mean4':>12} "
          f"{dprime_hdr:>8} {'accuracy':>9} {'baseline':>9}")
    rows_b = []
    for ksize in KERNELS:
        for n in range(1, N_STAGES + 1):
            vals = responses[ksize][n]
            v1, v4 = vals['1'], vals['4']
            dp = d_prime(v1, v4)
            acc, baseline = forced_choice_accuracy(v1, v4)
            rows_b.append({"ksize": ksize, "n": n, "footprint": merged_footprint(ksize, n),
                            "d_prime": dp, "accuracy": acc})
            print(f"{ksize:>6}x{ksize} {n:>2} {merged_footprint(ksize, n):>9} "
                  f"{v1.mean():>12.2f} {v4.mean():>12.2f} {dp:>8.3f} "
                  f"{100*acc:>8.1f}% {100*baseline:>8.1f}%")

    best_b = max(rows_b, key=lambda r: r["accuracy"])
    print(f"\n  Best '1'/'4' split: {best_b['ksize']}x{best_b['ksize']} n={best_b['n']} "
          f"(footprint {best_b['footprint']}), accuracy={100*best_b['accuracy']:.1f}%, "
          f"d'={best_b['d_prime']:.3f}")

    save_run_result({"group": ["1", "4", "7"], "eliminate_7": rows_a, "split_1_4": rows_b},
                     subdir="sobel0_147_runs")


if __name__ == "__main__":
    main()
