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
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _collect_cells, _load_tess_gt_cache
from gfl2.stat_ocr_fft import (
    _extract_pct_digit_glyphs, N_BINS,
    compute_features, _classify, set_gabor_params,
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
