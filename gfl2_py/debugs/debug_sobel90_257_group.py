# -*- coding: utf-8 -*-
"""
debugs/debug_sobel90_257_group.py -- goalpost redefinition of the
docs/known_issues.txt §26 / action_items.txt #13 FFT-iterated-Sobel probe.

§26's 90deg-MAX-response ranking (single-atlas-glyph, one sample per digit)
put 3 of the intended {2,4,5,7} group ('5','7','2') in the top 3 while '4'
fell to 9th of 11 -- the opposite extreme. This script drops '4' and asks
directly: can a 90deg (horizontal-edge / Sobel-Y) kernel segregate
{'2','5','7'} specifically from the rest of the pct-line digit set, at TWO
kernel sizes (3x3, 5x5) and iterated convolution depths (n=1,2,3) -- six
combos -- and if so, which is the CHEAPEST one that clears an "ample
signal-to-noise ratio" bar.

ADDRESSES action_items.txt #13's OPEN CONCERN: every prior §26/§15
Sobel/Gabor measurement in this exploration used ONE glyph per digit (the
assets/fonts/glyph_daily_pct.png reference atlas) -- action item #13
explicitly flags that as an in-sample, single-source proxy that needs
checking "against a proper held-out set of REAL glyphs from single/*.png"
before being trusted. This script pulls MANY real, labelled glyphs per
digit from the full single/*.png corpus, via the exact same
_collect_cells + _extract_pct_digit_glyphs extraction gfl2/stat_ocr_fft.py's
own verify_glyphs()/build_templates() use -- still in-sample (train==eval,
same convention as this project's other F-ratio/d' measurements: e.g.
known_issues.txt §15's WEDGE FEATURE / PAREN+RING entries), but now backed
by thousands of samples per digit instead of one, and by a continuous d'/
gate metric instead of a single-sample top-N ranking.

KERNELS:
  3x3 -- classic Sobel-Y: [[-1,-2,-1],[0,0,0],[1,2,1]].
  5x5 -- OpenCV's own generalized Sobel-Y (verified via
         cv2.getDerivKernels(dx=0, dy=1, ksize=5)): outer product of a
         5-tap binomial smoothing vector [1,4,6,4,1] and a 5-tap central-
         difference derivative vector [-1,-2,0,2,1] -- the SAME kernel
         docs/known_issues.txt §26's original 90deg exploration used
         (imported directly from debugs/debug_sobel90_pct_glyphs.py, not
         re-derived, so this is provably the same kernel).

ITERATION: for a fixed linear kernel, applying it n times is equivalent to
ONE convolution with a merged kernel of effective footprint
n*(ksize-1)+1 (docs/action_items.txt #15's own math: a 5x5 kernel iterated
3x collapses to 13x13). That merged-footprint number is used here as the
COST metric for ranking combos -- it is what a production implementation
would actually pay (a single cv2.filter2D pass at that kernel size), not
the incidental cost of this script's own repeated-FFT-power implementation.

METRICS: for each (kernel_size, n, aggregation in {mean, max}) combo,
group A (target) = {'2','5','7'}, group B (rest) = the other 7 digits:
  d'        = (mean_A - mean_B) / pooled_std        (continuous separation)
  best gate = [lo, hi] maximizing recall - false_trigger (Youden's J),
              same coarse grid-search convention as
              debugs/debug_gabor_45_zscore_verify.py's _best_gate(), with
              the sweep step scaled to each combo's own value range (raw
              magnitude grows roughly an order of magnitude per iteration,
              so a fixed step size would be miscalibrated across combos --
              the same "don't assume one threshold transfers to a
              differently-scaled distribution" lesson as known_issues.txt
              §15's TWO-AGENT CLASSIFIER margin-threshold finding).

"Ample S/N" bars (borrowed from this project's own established precedents,
not invented here):
  STRONG bar -- recall>=99%, false_trigger<=1%, matching the shipped
                (disabled-by-default) vstroke gate's real {1,4,7} result
                (known_issues.txt §24).
  USEFUL bar -- d'>=1.0, matching decision 62's gabor_45-MAX {4,7}
                second-vote, which measurably helped despite not being
                standalone-sufficient on its own.

Usage:
    python debugs/debug_sobel90_257_group.py
    python debugs/debug_sobel90_257_group.py --images "single/*.png"
    python debugs/debug_sobel90_257_group.py --debug   # also render a
                                                         # per-digit heatmap
                                                         # sanity table
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
from debugs.debug_sobel45_pct_glyphs import _freq_response
from debugs.debug_sobel90_pct_glyphs import SOBEL_90 as SOBEL_90_5X5
from debugs.persist_run_result import save_run_result

N_STAGES = 3
TARGET_DIGITS = ("2", "5", "7")
ALL_DIGITS = "0123456789"
REST_DIGITS = tuple(d for d in ALL_DIGITS if d not in TARGET_DIGITS)

# Classic 3x3 Sobel-Y (horizontal-edge detector) -- the smaller-footprint
# counterpart to the 5x5 kernel imported above.
SOBEL_90_3X3 = np.array([
    [-1, -2, -1],
    [0,   0,  0],
    [1,   2,  1],
], dtype=np.float64)

KERNELS = {3: SOBEL_90_3X3, 5: SOBEL_90_5X5}

STRONG_RECALL_MIN, STRONG_FALSE_TRIGGER_MAX = 0.99, 0.01
USEFUL_DPRIME_MIN = 1.0


def merged_footprint(ksize: int, n: int) -> int:
    """Effective single-pass kernel size for `ksize` applied `n` times
    (docs/action_items.txt #15's own math) -- used as the cost metric."""
    return n * (ksize - 1) + 1


def _fft_stages(padded: np.ndarray, kernel: np.ndarray, margin: int,
                 n_stages: int = N_STAGES) -> list[np.ndarray]:
    """Magnitude of ifft2(glyph_fft * kernel_fft**n) for n=1..n_stages,
    cropped back to the margin-free region -- generic over kernel size,
    shared by both the synthetic validation (PART 0) and the real-glyph
    measurement (PART 2) so the exact same numeric path is what gets
    validated."""
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


def _pad_with_margin(glyph: np.ndarray, margin: int, bg_val: int = 0) -> np.ndarray:
    h, w = glyph.shape
    canvas = np.full((h + 2 * margin, w + 2 * margin), bg_val, dtype=np.uint8)
    canvas[margin:margin + h, margin:margin + w] = glyph
    return canvas


# ─────────────────────────────────────────────────────────────────────────
# PART 0 -- synthetic orientation-selectivity check for BOTH kernel sizes,
# before trusting either on real glyphs (known_issues.txt §15's "vrun"
# discipline). Generic over which axis actually wins -- only requires the
# two kernel sizes to AGREE with each other, since this script's own
# {0,45,90,135} angle labels are just a coordinate convention, not a claim
# about which literal label "should" win.
# ─────────────────────────────────────────────────────────────────────────

def _synthetic_stroke(angle_deg: int, size: int = 24, thickness: int = 2) -> np.ndarray:
    """A single thin straight stroke through the center of a `size`x`size`
    canvas at `angle_deg` (0=horizontal, 90=vertical, counter-clockwise
    from the horizontal), background=0, stroke=255 -- same polarity as the
    real binarized 12x20 glyphs (ink=255 on background=0)."""
    canvas = np.zeros((size, size), dtype=np.uint8)
    cx = cy = size // 2
    r = size // 2 - 2
    theta = np.deg2rad(angle_deg)
    dx, dy = np.cos(theta), -np.sin(theta)   # image y grows downward
    p1 = (int(cx - dx * r), int(cy - dy * r))
    p2 = (int(cx + dx * r), int(cy + dy * r))
    cv2.line(canvas, p1, p2, 255, thickness, cv2.LINE_AA)
    return canvas


def run_synthetic_check() -> None:
    print(f"\n{'=' * 72}")
    print("PART 0 -- synthetic orientation-selectivity check (n=1 pass only)")
    print(f"{'=' * 72}")
    print("Thin single strokes at 0/45/90/135deg (angle = counter-clockwise from")
    print("the horizontal, standard math convention). A genuine directional")
    print("kernel should show a CLEAR peak at one axis and a CLEAR trough at the")
    print("perpendicular axis (90deg apart) -- not a flat response -- for BOTH")
    print("kernel sizes, and BOTH sizes must agree on which axis, before either")
    print("is trusted on real glyphs.\n")
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
# PART 1 -- real, multi-sample corpus glyph collection
# ─────────────────────────────────────────────────────────────────────────

def collect_glyphs(image_paths: list[Path]) -> dict:
    """{digit: [norm_bin_12x20, ...]} pooled across every pct-line glyph in
    the corpus -- same extraction gfl2.stat_ocr_fft.verify_glyphs() uses,
    so this is a real, many-sample-per-digit population, not the one-glyph-
    per-digit atlas every prior §26/§15 Sobel/Gabor probe in this
    exploration relied on."""
    gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)

    gt_file = _ROOT / "stat_gt_overrides.json"
    if gt_file.exists():
        overrides = json.loads(gt_file.read_text(encoding="utf-8"))
        for item in samples:
            ov = overrides.get(item["source"])
            if ov and "pct" in ov:
                item["pct"] = ov["pct"]

    buckets: dict[str, list[np.ndarray]] = {d: [] for d in ALL_DIGITS}
    for item in samples:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, label in glyphs:
            buckets.setdefault(label, []).append(norm)
    return buckets


# ─────────────────────────────────────────────────────────────────────────
# PART 2 -- iterated-Sobel response over the real corpus
# ─────────────────────────────────────────────────────────────────────────

def compute_responses(buckets: dict) -> dict:
    """responses[ksize][n]['mean'|'max'][digit] -> np.ndarray of per-glyph
    values.  One FFT-power sweep per glyph per kernel size covers all
    N_STAGES iterations at once (Kpow accumulates), so this is NOT 6x the
    FFT work per glyph -- only 2x (one per kernel size)."""
    responses = {ksize: {n: {"mean": {}, "max": {}} for n in range(1, N_STAGES + 1)}
                 for ksize in KERNELS}
    for ksize, kernel in KERNELS.items():
        margin = merged_footprint(ksize, N_STAGES) // 2 + 2
        for digit, glyphs in buckets.items():
            means = [[] for _ in range(N_STAGES)]
            maxes = [[] for _ in range(N_STAGES)]
            for norm in glyphs:
                padded = _pad_with_margin(norm, margin)
                stages = _fft_stages(padded, kernel, margin, N_STAGES)
                for i, mag in enumerate(stages):
                    means[i].append(float(mag.mean()))
                    maxes[i].append(float(mag.max()))
            for i in range(N_STAGES):
                n = i + 1
                responses[ksize][n]["mean"][digit] = np.array(means[i]) if means[i] else np.array([0.0])
                responses[ksize][n]["max"][digit] = np.array(maxes[i]) if maxes[i] else np.array([0.0])
    return responses


# ─────────────────────────────────────────────────────────────────────────
# PART 3 -- metrics: d' and best-gate recall/false-trigger for {2,5,7}
# ─────────────────────────────────────────────────────────────────────────

def d_prime(pos: np.ndarray, neg: np.ndarray) -> float:
    pooled_std = np.sqrt((pos.std() ** 2 + neg.std() ** 2) / 2)
    return float((pos.mean() - neg.mean()) / pooled_std) if pooled_std > 0 else float("nan")


def best_gate(pos: np.ndarray, neg: np.ndarray, n_steps: int = 40):
    """Sweep [lo, hi] to maximize Youden's J (recall - false_trigger).
    Step size is scaled to THIS combo's own pos-value range (raw magnitude
    grows roughly an order of magnitude per iteration/kernel-size increase,
    so a fixed step miscalibrates across combos -- see module docstring)."""
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


def summarize(responses: dict) -> list[dict]:
    rows = []
    for ksize in KERNELS:
        for n in range(1, N_STAGES + 1):
            for agg in ("mean", "max"):
                vals = responses[ksize][n][agg]
                pos = np.concatenate([vals[d] for d in TARGET_DIGITS])
                neg = np.concatenate([vals[d] for d in REST_DIGITS])
                dp = d_prime(pos, neg)
                j, lo, hi, recall, ft = best_gate(pos, neg)
                rows.append({
                    "ksize": ksize, "n": n, "agg": agg,
                    "footprint": merged_footprint(ksize, n),
                    "d_prime": round(dp, 3),
                    "gate_lo": round(lo, 2), "gate_hi": round(hi, 2),
                    "recall": round(recall, 4), "false_trigger": round(ft, 4),
                    "youden_j": round(j, 4),
                    "n_pos": int(len(pos)), "n_neg": int(len(neg)),
                })
    return rows


def print_per_digit(responses: dict) -> None:
    print(f"\n{'=' * 72}")
    print("PART 2 -- per-digit response (cheapest combo per kernel size, n=1)")
    print(f"{'=' * 72}")
    for ksize in KERNELS:
        for agg in ("mean", "max"):
            vals = responses[ksize][1][agg]
            print(f"\n--- kernel={ksize}x{ksize} n=1 agg={agg} ---")
            ranked = sorted(ALL_DIGITS, key=lambda d: vals[d].mean())
            for d in ranked:
                v = vals[d]
                tag = " <- TARGET" if d in TARGET_DIGITS else ""
                print(f"  {d}: n={len(v):5d}  mean={v.mean():10.2f}  std={v.std():10.2f}{tag}")


def print_summary(rows: list[dict]) -> None:
    rows_sorted = sorted(rows, key=lambda r: (r["footprint"], r["ksize"], r["n"], r["agg"]))
    dprime_hdr = "d'"
    print(f"\n{'=' * 100}")
    print("PART 3 -- {'2','5','7'} vs rest, ranked by cost (merged-kernel footprint)")
    print(f"{'=' * 100}")
    print(f"{'kernel':>7} {'n':>2} {'footprint':>9} {'agg':>5} {dprime_hdr:>7} "
          f"{'gate':>20} {'recall':>8} {'false_trig':>11} {'J':>7}  bar")
    for r in rows_sorted:
        gate_str = f"[{r['gate_lo']:.1f},{r['gate_hi']:.1f}]"
        strong = r["recall"] >= STRONG_RECALL_MIN and r["false_trigger"] <= STRONG_FALSE_TRIGGER_MAX
        useful = abs(r["d_prime"]) >= USEFUL_DPRIME_MIN
        bar = "STRONG" if strong else ("useful" if useful else "")
        print(f"{r['ksize']:>6}x{r['ksize']} {r['n']:>2} {r['footprint']:>9} {r['agg']:>5} "
              f"{r['d_prime']:>7.3f} {gate_str:>20} {100*r['recall']:>7.1f}% "
              f"{100*r['false_trigger']:>10.2f}% {r['youden_j']:>7.3f}  {bar}")

    strong_hits = [r for r in rows_sorted
                   if r["recall"] >= STRONG_RECALL_MIN and r["false_trigger"] <= STRONG_FALSE_TRIGGER_MAX]
    useful_hits = [r for r in rows_sorted if abs(r["d_prime"]) >= USEFUL_DPRIME_MIN]

    print(f"\n{'=' * 100}")
    print("CONCLUSION")
    print(f"{'=' * 100}")
    print(f"STRONG bar (recall>={100*STRONG_RECALL_MIN:.0f}%, false_trigger<={100*STRONG_FALSE_TRIGGER_MAX:.0f}%, "
          f"matching the shipped vstroke gate's real {{1,4,7}} result):")
    if strong_hits:
        cheapest = min(strong_hits, key=lambda r: r["footprint"])
        print(f"  {len(strong_hits)} combo(s) clear it. CHEAPEST: {cheapest['ksize']}x{cheapest['ksize']} "
              f"kernel, n={cheapest['n']} ({cheapest['agg']}), effective footprint "
              f"{cheapest['footprint']}x{cheapest['footprint']}, "
              f"gate=[{cheapest['gate_lo']},{cheapest['gate_hi']}], "
              f"recall={100*cheapest['recall']:.1f}%, false_trigger={100*cheapest['false_trigger']:.2f}%.")
    else:
        print("  NONE of the 12 combos clear this bar.")

    print(f"\nUSEFUL bar (|d'|>={USEFUL_DPRIME_MIN}, matching decision 62's gabor_45-MAX "
          f"{{4,7}} second-vote):")
    if useful_hits:
        cheapest_u = min(useful_hits, key=lambda r: r["footprint"])
        print(f"  {len(useful_hits)} combo(s) clear it. CHEAPEST: {cheapest_u['ksize']}x{cheapest_u['ksize']} "
              f"kernel, n={cheapest_u['n']} ({cheapest_u['agg']}), effective footprint "
              f"{cheapest_u['footprint']}x{cheapest_u['footprint']}, d'={cheapest_u['d_prime']}.")
    else:
        print("  NONE of the 12 combos clear this bar either.")

    if not strong_hits and not useful_hits:
        print("\n  Neither bar is cleared by any (kernel_size, n, aggregation) combo tried --")
        print("  a 90deg Sobel does not appear to carry ample signal-to-noise for")
        print("  segregating {2,5,7} from the rest, at these depths/sizes, on the real,")
        print("  many-sample corpus (contrast with §26's single-atlas-glyph ranking).")


# ─────────────────────────────────────────────────────────────────────────
# Optional visual sanity table (one representative real glyph per digit) --
# "unit debug before/alongside integration" convention.
# ─────────────────────────────────────────────────────────────────────────

def render_debug_table(buckets: dict, out_path: Path) -> None:
    UPSCALE = 8
    combos = [(3, 1), (3, 3), (5, 1), (5, 3)]
    cell_w, cell_h = 110, 150
    label_w = 60
    header_h = 30
    n_cols = 1 + len(combos)
    n_rows = len(ALL_DIGITS)
    W = label_w + n_cols * cell_w
    H = header_h + n_rows * cell_h
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)

    columns = ["glyph"] + [f"{k}x{k} n={n}" for k, n in combos]
    for j, name in enumerate(columns):
        x0 = label_w + j * cell_w
        cv2.putText(canvas, name, (x0 + 4, header_h - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.4, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (x0, 0), (x0, H), (210, 210, 210), 1)
    cv2.line(canvas, (0, header_h), (W, header_h), (150, 150, 150), 1)

    # Precompute a global max per combo (across the 10 representative
    # glyphs) so the heatmap color scale is shared, not per-cell-normalized
    # -- known_issues.txt §15's DEBUG TABLE entry lesson.
    reps = {d: buckets[d][0] for d in ALL_DIGITS if buckets[d]}
    stage_max = {}
    per_digit_stages = {}
    for (ksize, n) in combos:
        kernel = KERNELS[ksize]
        margin = merged_footprint(ksize, N_STAGES) // 2 + 2
        vals = []
        for d, norm in reps.items():
            padded = _pad_with_margin(norm, margin)
            stages = _fft_stages(padded, kernel, margin, N_STAGES)
            per_digit_stages[(d, ksize, n)] = stages[n - 1]
            vals.append(float(stages[n - 1].max()))
        stage_max[(ksize, n)] = max(vals) if vals else 1.0

    for i, d in enumerate(ALL_DIGITS):
        y0 = header_h + i * cell_h
        cv2.line(canvas, (0, y0), (W, y0), (210, 210, 210), 1)
        tag = " *" if d in TARGET_DIGITS else ""
        cv2.putText(canvas, f"'{d}'{tag}", (8, y0 + cell_h // 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (0, 0, 0), 1, cv2.LINE_AA)
        if d not in reps:
            continue
        norm = reps[d]
        glyph_bgr = cv2.cvtColor(
            cv2.resize(norm, (norm.shape[1] * UPSCALE, norm.shape[0] * UPSCALE),
                       interpolation=cv2.INTER_NEAREST),
            cv2.COLOR_GRAY2BGR)
        gh, gw = glyph_bgr.shape[:2]
        x0 = label_w
        canvas[y0 + 4: y0 + 4 + min(gh, cell_h - 8), x0 + 4: x0 + 4 + min(gw, cell_w - 8)] = \
            glyph_bgr[:min(gh, cell_h - 8), :min(gw, cell_w - 8)]

        for j, (ksize, n) in enumerate(combos):
            mag = per_digit_stages[(d, ksize, n)]
            scale = stage_max[(ksize, n)] or 1.0
            mag_u8 = np.clip(mag / scale * 255, 0, 255).astype(np.uint8)
            heat = cv2.applyColorMap(mag_u8, cv2.COLORMAP_JET)
            heat_up = cv2.resize(heat, (heat.shape[1] * UPSCALE, heat.shape[0] * UPSCALE),
                                  interpolation=cv2.INTER_NEAREST)
            base_up = cv2.resize(cv2.cvtColor(norm, cv2.COLOR_GRAY2BGR),
                                  (heat_up.shape[1], heat_up.shape[0]),
                                  interpolation=cv2.INTER_NEAREST)
            overlay = cv2.addWeighted(heat_up, 0.55, base_up, 0.45, 0)
            x0 = label_w + (j + 1) * cell_w
            oh, ow = overlay.shape[:2]
            fh, fw = min(oh, cell_h - 20), min(ow, cell_w - 8)
            canvas[y0 + 4: y0 + 4 + fh, x0 + 4: x0 + 4 + fw] = overlay[:fh, :fw]
            cv2.putText(canvas, f"mean={mag.mean():.2f}", (x0 + 4, y0 + cell_h - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.32, (30, 30, 30), 1, cv2.LINE_AA)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas)
    print(f"\nWrote debug table -> {out_path}  (* marks the {{2,5,7}} target group)")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    ap.add_argument("--debug", action="store_true",
                     help="also render a per-digit heatmap sanity table")
    ap.add_argument("--output", default=str(_ROOT / "tests" / "outputs" / "daily" /
                                             "sobel90_257_glyph_table.png"))
    args = ap.parse_args(argv)

    run_synthetic_check()

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                          if "debug" not in Path(p).stem)
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    print(f"\nCollecting real pct-line glyphs from {len(image_paths)} image(s) ...")
    buckets = collect_glyphs(image_paths)
    print(f"{'digit':>6} {'n':>6}")
    for d in ALL_DIGITS:
        print(f"{d:>6} {len(buckets[d]):>6}")

    print(f"\nComputing iterated-Sobel responses "
          f"({sum(len(v) for v in buckets.values())} glyphs x {len(KERNELS)} kernel sizes) ...")
    responses = compute_responses(buckets)
    print_per_digit(responses)
    rows = summarize(responses)
    print_summary(rows)

    save_run_result(
        {"target": list(TARGET_DIGITS), "rest": list(REST_DIGITS), "rows": rows},
        subdir="sobel90_257_runs",
    )

    if args.debug:
        render_debug_table(buckets, Path(args.output))


if __name__ == "__main__":
    main()
