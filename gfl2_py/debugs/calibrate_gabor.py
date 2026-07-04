# -*- coding: utf-8 -*-
"""
debugs/calibrate_gabor.py -- calibrate gfl2.stat_ocr_fft's Gabor kernel
parameters (lambda/sigma/gamma) against a training corpus by scoring each
candidate through the REAL two-agent classify pipeline (see IMPORTANT
CORRECTION #2 below for why two earlier proxy-metric attempts were
insufficient), reporting two STRUCTURAL diagnostics alongside overall
accuracy.

WHY THIS EXISTS (not a throwaway script): docs/known_issues.txt §15's FFT
exploration patched around two symptoms downstream of the Gabor feature
itself -- the PAIR TIEBREAK override for '4'/'7' (which only exists because
the line features can't decisively separate them, forcing reliance on the
unstable paren_( feature) and the abandoned universal lines-first cascade
(which broke on '3'/'0' because their line signal is noisy/unstable, not
because lines are meaningless for them).  Both are downstream fixes for an
upstream problem: the Gabor kernel's (lambda, sigma, gamma) were never
tuned for THIS font, just carried over from an earlier general-purpose
sweep (debugs/debug_pct_classify.py --tune) that only optimized overall
LOO accuracy.

This script optimizes for the two specific properties instead:
  1. '4' vs '7' should be decisively separable -- both digits fit '-' and
     '/' by construction, so this is asking for the best available
     lambda/sigma/gamma, not a guarantee of perfect separation, but it
     directly targets "stop needing the PAIR TIEBREAK's arc-based
     fallback."
  2. The arc-dominant digit group {0,3,6,8,9} should have a STABLE (low
     within-class variance) line-feature reading -- i.e. their Gabor
     values shouldn't "flip" between runs/samples due to noise, which is
     what made the universal lines-first cascade unreliable for them (a
     noisy signal that occasionally excludes the correct candidate is
     worse than an honestly weak, but STABLE, one).

IMPORTANT CORRECTION #1 (kept in this docstring so it isn't repeated): the
first version of this script scored these properties using ONLY the 3
Gabor dims in isolation.  That calibration was strictly better than the
historical default on all three isolated metrics (99.7% vs 88.2% 4/7
separability, 0.0012 vs 0.0171 arc instability, 86.8% vs 75.4% Gabor-only
accuracy) -- and made the REAL two-agent classifier WORSE end to end
(cell-level pct accuracy 90.1%->86.5% without the pair tiebreak, 93.2%->
90.5% with it).  Agent A never uses Gabor in isolation -- it's always
concatenated with paren+ring into one 13-dim nearest-centroid distance
(gfl2/stat_ocr_fft.py's TWO-AGENT CLASSIFIER) -- so a Gabor configuration
tuned in isolation can trade away how well it interacts with paren+ring in
the combined space even while genuinely improving on its own.

IMPORTANT CORRECTION #2: fixing #1 by scoring an analytic leave-one-out
nearest-centroid accuracy on the FULL 13-dim gabor+paren+ring vector
STILL wasn't enough.  The winning candidate that emerged (lambd=3.0,
sigma=2.0, gamma=1.0 -- barely different from the historical default's
lambd=4.0) looked good on that proxy (96.1% 4/7 separability, 95.0%
overall LOO accuracy, both above the default) but STILL regressed the
real end-to-end classifier when actually built and verified (pct
88.2%/89.6% without/with pair tiebreak, vs. the default's 90.1%/93.2%).
Root cause: a plain nearest-centroid LOO metric on Agent A's feature
space, however complete, still isn't what the shipped pipeline actually
does at inference time -- it ignores Agent B (the independently
z-normalized histogram classifier) entirely, the confidence-margin gating
between the two agents (CONF_A_DEFAULT/CONF_B_DEFAULT), and the '?'
no-read behavior when neither agent is confident.  A digit that Agent A
alone would misclassify might be correctly rescued by Agent B in the real
pipeline, or vice versa -- no proxy that only look at Agent A's raw
feature space can capture that.  This is a THIRD instance of the "looks
better in isolation, worse in combination" family (docs/takeaways.txt
#46, #47) -- and the generalized lesson this time is stronger: there is
no feature-space proxy shortcut for a multi-agent decision system, so
FIX APPLIED below scores candidates via the actual `_classify()` decision
function (both agents, real confidence gating, real pair-tiebreak flag),
run in-process per candidate via `set_gabor_params()` -- i.e. the same
thing --build followed by --verify would show, just without the disk
round-trip, so a 54-point sweep stays practical.  Evaluation is IN-SAMPLE
(trains and scores against the same corpus), matching this project's own
convention for stat_ocr's --build/--verify (see reference.txt §5.5) --
this script is not attempting a held-out generalization estimate, only a
faithful reproduction of what --build + --verify would report for each
candidate.  See docs/known_issues.txt §15 and docs/takeaways.txt for the
general lesson.

Because this recalibrates a font-dependent classifier component, it needs
to be RE-RUN (not just kept as a one-off result) whenever this pipeline is
pointed at a new game/font's digit rendering -- hence a proper CLI tool
with saved, versioned output, not inline exploration code.

Output: assets/fonts/gabor_calib.json -- {"lambd", "sigma", "gamma",
"generated", "source_images"}.  gfl2/stat_ocr_fft.py loads this file if
present (falling back to the historical hardcoded defaults if absent), so
running this script against a new font's images and re-running
`python -m gfl2.stat_ocr_fft --build` is the complete recalibration path.

Usage:
    python debugs/calibrate_gabor.py --images "single/*.png"
    python debugs/calibrate_gabor.py --images "single/*.png" --output assets/fonts/gabor_calib.json
"""
from __future__ import annotations
import json, sys, glob as _glob
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _collect_cells, _load_tess_gt_cache
from gfl2.stat_ocr_fft import (
    _extract_pct_digit_glyphs, N_BINS, N_ORIENT, _GABOR_STEP,
    compute_features, _classify, set_gabor_params,
    _paren_features, _ring_energies, _nearest_centroid,
    CONF_A_DEFAULT, CONF_B_DEFAULT,
)

_FONTS_DIR = _ROOT / "assets" / "fonts"
OUT_F      = _FONTS_DIR / "gabor_calib.json"

# Same grid as debugs/debug_pct_classify.py's gabor_sweep(), which found the
# CURRENT hardcoded defaults (lambd=4.0, sigma=2.0, gamma=1.0) via plain LOO
# accuracy.  This script re-scores the identical grid against the two
# targeted properties instead.
_LAMBD_GRID = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0]
_SIGMA_GRID = [1.0, 1.5, 2.0]
_GAMMA_GRID = [0.25, 0.5, 1.0]
_KSIZE      = 7

ARC_GROUP = ("0", "3", "6", "8", "9")   # digits whose real signal is curves/loops, not lines
LINE_PAIR = ("4", "7")                  # the confirmed line-feature collision (known_issues.txt §15)


# ── Glyph collection (mirrors gfl2.stat_ocr_fft.build_templates's extraction) ─

def collect_training_glyphs(
    image_paths: list[Path], gt_cache: "dict | None" = None,
) -> dict[str, list[np.ndarray]]:
    """Return {digit: [normalized 12x20 glyph, ...]} using the exact same
    label-aligned extraction production template-building uses, so
    calibration sees the identical crops compute_features() will later see.

    gt_cache: explicit None auto-loads tests/inputs/daily/tess_gt_cache.py
      (debugs/build_tess_gt_cache.py) -- skips ~20 minutes of live
      Tesseract against a static, already-labelled image set.  Pass {} to
      force live Tesseract (e.g. when calibrating against a NEW font's
      images that aren't in the cache yet -- a cache miss per cell already
      falls back to live Tesseract automatically, so this is only needed
      to force-refresh a stale cache).
    """
    if gt_cache is None:
        gt_cache = _load_tess_gt_cache() or {}
    cells = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    buckets: dict[str, list[np.ndarray]] = defaultdict(list)
    for item in cells:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, label in glyphs:
            buckets[label].append(norm)
    return buckets


# ── Real-pipeline scoring for a candidate parameter set ───────────────────────

def _real_pipeline_metrics(buckets: dict[str, list[np.ndarray]]) -> dict:
    """
    Build Agent A (gpr) + Agent B (hist) centroids from `buckets` -- same
    math as gfl2.stat_ocr_fft.build_templates(), duplicated here because
    that function re-extracts glyphs from raw cells and this script already
    has glyphs extracted once up front, reused across all 54 candidates --
    using the CURRENTLY ACTIVE Gabor kernels (the caller sets these via
    set_gabor_params() before calling this), then classifies every training
    glyph through the REAL `_classify()` two-agent decision path (real
    confidence gating, pair-tiebreak left at its production default of
    off).  This is what makes the result faithful to --build + --verify --
    see the module docstring's IMPORTANT CORRECTION #2 for why the two
    earlier proxy-metric attempts (Gabor-only LOO, then full-vector LOO)
    both failed to predict this.
    """
    feats = {d: np.array([compute_features(g) for g in glyphs]) for d, glyphs in buckets.items()}

    gpr_templates = {d: f[:, N_BINS:].mean(axis=0) for d, f in feats.items()}
    all_hist = np.concatenate([f[:, :N_BINS] for f in feats.values()], axis=0)
    hist_mu = all_hist.mean(axis=0)
    hist_sigma = all_hist.std(axis=0) + 1e-9
    hist_templates = {d: ((f[:, :N_BINS] - hist_mu) / hist_sigma).mean(axis=0) for d, f in feats.items()}
    templates = {"gpr": gpr_templates, "hist": hist_templates,
                 "hist_mu": hist_mu, "hist_sigma": hist_sigma}

    total = correct = 0
    line_pair_total = line_pair_flip = 0    # '4'<->'7' confused into EACH OTHER specifically
    arc_total = arc_correct = 0
    for d, glyphs in buckets.items():
        for g in glyphs:
            pred = _classify(g, templates)
            total += 1
            correct += int(pred == d)
            if d in LINE_PAIR:
                line_pair_total += 1
                other = LINE_PAIR[0] if d == LINE_PAIR[1] else LINE_PAIR[1]
                line_pair_flip += int(pred == other)
            if d in ARC_GROUP:
                arc_total += 1
                arc_correct += int(pred == d)

    return {
        "overall_accuracy":   correct / total if total else 0.0,
        "line_pair_flip_rate": line_pair_flip / line_pair_total if line_pair_total else 0.0,
        "arc_group_accuracy": arc_correct / arc_total if arc_total else 0.0,
    }


# ── Calibration search ────────────────────────────────────────────────────────

def calibrate(
    buckets: dict[str, list[np.ndarray]], min_accuracy_frac: float = 0.90,
) -> tuple[dict, list[dict], list[dict]]:
    """
    Sweep (lambd, sigma, gamma); score each via _real_pipeline_metrics --
    the actual two-agent `_classify()` decision path, not a feature-space
    proxy (see IMPORTANT CORRECTION #2).  Ranks candidates by overall
    accuracy directly (with the 4/7 flip rate as a tiebreaker), unlike the
    first version of this function which ranked by z-scored proxy metrics
    and needed an artificial accuracy floor to avoid a degenerate solution
    (known_issues.txt §15) -- now that overall_accuracy IS the real metric,
    ranking by it directly cannot produce that failure mode.
    min_accuracy_frac is kept only to size the reported "eligible" table,
    not to gate the winner.

    Returns (winner_dict, eligible_sorted, all_results_sorted).
    """
    results = []
    for lambd in _LAMBD_GRID:
        for sigma in _SIGMA_GRID:
            for gamma in _GAMMA_GRID:
                set_gabor_params(lambd, sigma, gamma)
                m = _real_pipeline_metrics(buckets)
                results.append({"lambd": lambd, "sigma": sigma, "gamma": gamma, **m})

    results.sort(key=lambda r: (r["overall_accuracy"], -r["line_pair_flip_rate"]), reverse=True)
    max_acc = results[0]["overall_accuracy"]
    acc_floor = max_acc * min_accuracy_frac
    eligible = [r for r in results if r["overall_accuracy"] >= acc_floor]

    winner = results[0]
    winner["_acc_floor"] = acc_floor
    winner["_max_acc"] = max_acc
    return winner, eligible, results


# ── Multi-scale Gabor bank prototype (validation only, not wired to production) ─
#
# A single (lambd, sigma, gamma) is a compromise scale across digits with
# very different stroke widths at the normalized 12x20 glyph size ('1' is a
# thin single stroke; '8'/'0' have thick looping strokes) -- calibrate()
# above can only ever find the best COMPROMISE, not fix this.  The standard
# answer in texture/character recognition is a Gabor filter BANK: compute
# the same orientations at more than one scale and concatenate, so the
# per-digit centroid can lean on whichever scale actually discriminates
# that digit, without needing to know the digit ahead of time (every glyph
# gets every scale).
#
# This is validation-only: gfl2/stat_ocr_fft.py's shipped classify path has
# index math hardcoded to a single 3-dim Gabor block (_PAREN_OPEN/
# _PAREN_CLOSE indices, PAIR_TIEBREAK_RULES's range(13)) that would need a
# careful, separate change to generalize safely -- not worth making until a
# multi-scale bank is shown to actually help.  So this uses its own local
# two-agent nearest-centroid+margin-gate simulation (same CONF_A_DEFAULT/
# CONF_B_DEFAULT thresholds and _nearest_centroid distance function as
# production's real _classify(), just not calling it directly) instead of
# compute_features()/_classify(), which both assume exactly one scale.
#
# Search strategy: fix the validated single-scale winner from calibrate()
# as the base scale, and sweep a SECOND scale against the same grid used
# above (54 candidates) -- greedy one-scale-at-a-time addition, not a full
# combinatorial search over scale sets, for the same tractability reason
# calibrate() only ever varied one triple.  This is how filter banks are
# normally built in practice (add a scale, keep it if it helps, repeat).

def _scale_kernels(lambd: float, sigma: float, gamma: float) -> list[np.ndarray]:
    return [
        cv2.getGaborKernel((_KSIZE, _KSIZE), sigma, i * np.pi / _GABOR_STEP, lambd, gamma, 0.0, cv2.CV_32F)
        for i in range(N_ORIENT)
    ]


def _multiscale_gabor_features(gray_norm: np.ndarray, kernel_sets: list[list[np.ndarray]]) -> np.ndarray:
    """Per-scale orientation fractions (each scale's N_ORIENT dims sum to 1
    independently, same normalization as the single-scale feature), all
    scales concatenated -- N_ORIENT * len(kernel_sets) dims total."""
    f32 = gray_norm.astype(np.float32)
    parts = []
    for kernels in kernel_sets:
        resps = [float(np.abs(cv2.filter2D(f32, -1, k)).mean()) for k in kernels]
        tot = sum(resps) + 1e-9
        parts.extend(r / tot for r in resps)
    return np.array(parts)


def _multiscale_pipeline_metrics(
    buckets: dict[str, list[np.ndarray]], kernel_sets: list[list[np.ndarray]],
) -> dict:
    """
    Same real two-agent evaluation as _real_pipeline_metrics, but Agent A's
    feature vector is [multiscale_gabor, paren(2), ring(8)] -- a different
    length than production's fixed 13-dim vector -- so this replicates
    _classify()'s decision logic locally (same _nearest_centroid function,
    same CONF_A_DEFAULT/CONF_B_DEFAULT thresholds) instead of calling it.
    """
    feats = {}
    for d, glyphs in buckets.items():
        rows = []
        for g in glyphs:
            hist  = compute_features(g)[:N_BINS]   # gabor-independent slice
            gabor = _multiscale_gabor_features(g, kernel_sets)
            rows.append(np.concatenate([hist, gabor, _paren_features(g), _ring_energies(g)]))
        feats[d] = np.array(rows)

    gpr_templates = {d: f[:, N_BINS:].mean(axis=0) for d, f in feats.items()}
    all_hist = np.concatenate([f[:, :N_BINS] for f in feats.values()], axis=0)
    hist_mu = all_hist.mean(axis=0)
    hist_sigma = all_hist.std(axis=0) + 1e-9
    hist_templates = {d: ((f[:, :N_BINS] - hist_mu) / hist_sigma).mean(axis=0) for d, f in feats.items()}

    total = correct = 0
    line_pair_total = line_pair_flip = 0
    arc_total = arc_correct = 0
    for d, f in feats.items():
        for row in f:
            pred_a, margin_a = _nearest_centroid(row[N_BINS:], gpr_templates)
            if margin_a >= CONF_A_DEFAULT:
                pred = pred_a
            else:
                feat_hist = (row[:N_BINS] - hist_mu) / hist_sigma
                pred_b, margin_b = _nearest_centroid(feat_hist, hist_templates)
                pred = pred_b if margin_b >= CONF_B_DEFAULT else '?'
            total += 1
            correct += int(pred == d)
            if d in LINE_PAIR:
                line_pair_total += 1
                other = LINE_PAIR[0] if d == LINE_PAIR[1] else LINE_PAIR[1]
                line_pair_flip += int(pred == other)
            if d in ARC_GROUP:
                arc_total += 1
                arc_correct += int(pred == d)

    return {
        "overall_accuracy":    correct / total if total else 0.0,
        "line_pair_flip_rate": line_pair_flip / line_pair_total if line_pair_total else 0.0,
        "arc_group_accuracy":  arc_correct / arc_total if arc_total else 0.0,
    }


def sweep_second_scale(
    buckets: dict[str, list[np.ndarray]], base_scale: tuple[float, float, float],
) -> list[dict]:
    """
    Fix `base_scale` (pass the winner from calibrate()) and sweep a second
    scale over the same grid calibrate() used, scoring each 2-scale bank
    via _multiscale_pipeline_metrics.  Returns all results sorted best
    first (overall accuracy, 4/7 flip rate as tiebreak) -- compare
    results[0] against the single-scale baseline to see whether a bank
    genuinely helps before considering the production refactor.
    """
    base_kernels = _scale_kernels(*base_scale)
    results = []
    for lambd in _LAMBD_GRID:
        for sigma in _SIGMA_GRID:
            for gamma in _GAMMA_GRID:
                second_kernels = _scale_kernels(lambd, sigma, gamma)
                m = _multiscale_pipeline_metrics(buckets, [base_kernels, second_kernels])
                results.append({"lambd": lambd, "sigma": sigma, "gamma": gamma, **m})
    results.sort(key=lambda r: (r["overall_accuracy"], -r["line_pair_flip_rate"]), reverse=True)
    return results


# ── Entry point ───────────────────────────────────────────────────────────────

def main(argv=None):
    import argparse
    run_start = datetime.now().isoformat(timespec="seconds")
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png",
                     help="Glob of images to calibrate against  [default: single/*.png]")
    ap.add_argument("--output", default=str(OUT_F),
                     help=f"Where to write the calibrated params  [default: {OUT_F}]")
    ap.add_argument("--no-gt-cache", action="store_true",
                     help="Force live Tesseract for every cell instead of "
                          "tests/inputs/daily/tess_gt_cache.py (debugs/"
                          "build_tess_gt_cache.py) -- use when calibrating "
                          "against images not covered by that cache")
    ap.add_argument("--min-accuracy-frac", type=float, default=0.90,
                     help="Reporting only: size of the 'eligible' table printed "
                          "alongside the winner, as a fraction of grid-best "
                          "accuracy  [default: 0.90].  Does not affect which "
                          "candidate is selected -- see calibrate()'s docstring")
    ap.add_argument("--multiscale", action="store_true",
                     help="After the single-scale calibration, also sweep a "
                          "SECOND Gabor scale paired with the winner (see "
                          "sweep_second_scale()'s docstring) and report "
                          "whether a 2-scale bank beats the single-scale "
                          "result -- validation only, NOT written to "
                          "gabor_calib.json (gfl2/stat_ocr_fft.py doesn't "
                          "support multi-scale loading yet)")
    args = ap.parse_args(argv)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                         if "debug" not in Path(p).stem)
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    gt_cache = {} if args.no_gt_cache else (_load_tess_gt_cache() or {})
    if gt_cache:
        print(f"Using Tesseract GT cache: {len(gt_cache)} cells "
              f"(tests/inputs/daily/tess_gt_cache.py)")

    print(f"Generated: {run_start}  (run start)")
    print(f"Collecting training glyphs from {len(image_paths)} image(s) ...")
    buckets = collect_training_glyphs(image_paths, gt_cache=gt_cache)
    if not all(d in buckets for d in "0123456789"):
        missing = [d for d in "0123456789" if d not in buckets]
        sys.exit(f"Missing training samples for digit(s): {missing}")
    print(f"  {sum(len(v) for v in buckets.values())} glyphs across "
          f"{len(buckets)} digits: { {d: len(v) for d, v in sorted(buckets.items())} }")

    print(f"\nSweeping {len(_LAMBD_GRID)*len(_SIGMA_GRID)*len(_GAMMA_GRID)} "
          f"(lambda, sigma, gamma) combinations ...")
    winner, eligible, all_results = calibrate(buckets, args.min_accuracy_frac)

    print(f"\n{len(eligible)}/{len(all_results)} candidates within "
          f"{args.min_accuracy_frac*100:.0f}% of grid-best accuracy "
          f"({winner['_max_acc']*100:.1f}%) -- ranked by real overall accuracy "
          f"(4/7 flip rate as tiebreak), top 10:")
    print(f"\n{'lambd':>6} {'sigma':>6} {'gamma':>6}  {'overall_acc':>12} "
          f"{'4v7_flip':>9} {'arc_acc':>8}")
    for r in all_results[:10]:
        print(f"{r['lambd']:>6.1f} {r['sigma']:>6.2f} {r['gamma']:>6.2f}  "
              f"{r['overall_accuracy']:>12.3f} "
              f"{r['line_pair_flip_rate']:>9.3f} {r['arc_group_accuracy']:>8.3f}")

    print(f"\nSelected: lambd={winner['lambd']} sigma={winner['sigma']} gamma={winner['gamma']}")
    print(f"  overall accuracy (real pipeline): {winner['overall_accuracy']*100:.1f}%")
    print(f"  4/7 flip rate                   : {winner['line_pair_flip_rate']*100:.1f}%")
    print(f"  arc-group ({''.join(ARC_GROUP)}) accuracy   : {winner['arc_group_accuracy']*100:.1f}%")

    if args.multiscale:
        base_scale = (winner["lambd"], winner["sigma"], winner["gamma"])
        print(f"\n--multiscale: sweeping a second Gabor scale against base "
              f"{base_scale} ({len(_LAMBD_GRID)*len(_SIGMA_GRID)*len(_GAMMA_GRID)} candidates) ...")
        ms_results = sweep_second_scale(buckets, base_scale)
        ms_best = ms_results[0]
        print(f"\n{'lambd':>6} {'sigma':>6} {'gamma':>6}  {'overall_acc':>12} "
              f"{'4v7_flip':>9} {'arc_acc':>8}   (2nd scale, base fixed)")
        for r in ms_results[:10]:
            print(f"{r['lambd']:>6.1f} {r['sigma']:>6.2f} {r['gamma']:>6.2f}  "
                  f"{r['overall_accuracy']:>12.3f} "
                  f"{r['line_pair_flip_rate']:>9.3f} {r['arc_group_accuracy']:>8.3f}")
        delta = ms_best["overall_accuracy"] - winner["overall_accuracy"]
        print(f"\nBest 2-scale bank: base={base_scale} + second="
              f"({ms_best['lambd']}, {ms_best['sigma']}, {ms_best['gamma']})")
        print(f"  overall accuracy: {ms_best['overall_accuracy']*100:.1f}%  "
              f"({'+' if delta >= 0 else ''}{delta*100:.1f} pts vs single-scale)")
        print(f"  4/7 flip rate   : {ms_best['line_pair_flip_rate']*100:.1f}%  "
              f"(single-scale: {winner['line_pair_flip_rate']*100:.1f}%)")
        print(f"  arc-group acc   : {ms_best['arc_group_accuracy']*100:.1f}%  "
              f"(single-scale: {winner['arc_group_accuracy']*100:.1f}%)")
        print("\nValidation only -- not written to gabor_calib.json.  "
              "gfl2/stat_ocr_fft.py's shipped classify path assumes a single "
              "Gabor scale (index math hardcoded to a 3-dim block); wiring a "
              "2-scale bank into production is a separate change, only "
              "worth making if the numbers above show a real gain.")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "lambd": winner["lambd"], "sigma": winner["sigma"], "gamma": winner["gamma"],
        "generated": run_start,
        "source_images": [p.name for p in image_paths],
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nWrote calibration: {out_path}")
    print("Run `python -m gfl2.stat_ocr_fft --build` to rebuild templates with it.")


if __name__ == "__main__":
    main()
