# -*- coding: utf-8 -*-
"""
debugs/debug_gabor_2457_retune.py -- UNIT-level visual debug table comparing
the SHIPPED 45deg Gabor kernel against a candidate 90deg kernel, retuned to
target separating the horizontal-line digit group {2,4,5,7} from the rest.

DOES NOT TOUCH gfl2/stat_ocr_fft.py. The 45deg column uses the currently
shipped kernel (_GABOR_KERNELS, whatever assets/fonts/gabor_calib.json
holds) unmodified; the 90deg column is a candidate kernel built locally in
this script only, for visual/quick-scoring inspection -- same "prototype in
debugs/ before touching production" convention as debug_vstroke_feature.py
and debug_hbar_feature.py.

WHY THIS EXISTS: gabor_90 was removed from production (known_issues.txt
§22) via a marginal-utility ablation that found it "byte-identical" once
hbar_top/hbar_bottom already existed in the feature vector. Before
concluding that's evidence Gabor-at-90deg has nothing left to offer for
lines in 2/4/5/7, it's worth actually looking at the raw per-digit response
-- both to sanity check gabor_45 (the one dim that DID survive every
ablation) against the same eyeball test, and to see whether a properly
targeted 90deg candidate would even show the expected 2/4/5/7-vs-rest
pattern in principle, on a real sample, before any corpus-wide claim.

SCOPE: deliberately narrow -- one sample glyph per digit from ONE source
image (same convention as debugs/debug_gabor_features.py: this is for
eyeballing whether the response looks sane on real data, not a corpus-wide
accuracy claim). Any candidate that looks promising here still needs
calibrate_gabor.py-style real-pipeline validation before it could justify
touching gfl2/stat_ocr_fft.py.

Usage:
    python debugs/debug_gabor_2457_retune.py
    python debugs/debug_gabor_2457_retune.py --images single/fb_d_060518.png
"""
from __future__ import annotations
import sys
import argparse
from pathlib import Path
import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _load_tess_gt_cache
from gfl2.stat_ocr_fft import _GABOR_KERNELS, _GABOR_STEP, _GABOR_PARAMS

from debugs.debug_gabor_features import (
    DEFAULT_IMAGE, DIGITS, CELL_W, CELL_H, LABEL_W, HEADER_H, CAPTION_H, ALPHA,
    collect_one_glyph_per_digit, _to_bgr, _fit_and_paste, _heatmap_overlay,
    _put_caption, _blank_cell,
)

HBAR_GROUP = ("2", "4", "5", "7")   # horizontal-line digits (2 foot, 4 crossbar, 5/7 top bar)
REST_GROUP = tuple(d for d in DIGITS if d not in HBAR_GROUP)

# Same grid calibrate_gabor.py sweeps, for a candidate 90deg kernel.
_LAMBD_GRID = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0]
_SIGMA_GRID = [1.0, 1.5, 2.0]
_GAMMA_GRID = [0.25, 0.5, 1.0]
_KSIZE = 7
_ANGLE_90 = 2 * np.pi / _GABOR_STEP   # i=2 -> 90deg, matching the historical _GABOR_ANGLE_IDXS convention


def _build_90_kernel(lambd: float, sigma: float, gamma: float) -> np.ndarray:
    return cv2.getGaborKernel((_KSIZE, _KSIZE), sigma, _ANGLE_90, lambd, gamma, 0.0, cv2.CV_32F)


def _mean_response(norm_glyph: np.ndarray, kernel: np.ndarray) -> float:
    f32 = norm_glyph.astype(np.float32)
    return float(np.abs(cv2.filter2D(f32, -1, kernel)).mean())


def _separation_score(means: dict) -> float:
    """Standardized gap between HBAR_GROUP and REST_GROUP means -- a quick,
    single-sample separation index (Cohen's-d style), NOT a substitute for
    calibrate_gabor.py's real-pipeline scoring. Just enough to rank
    candidates for this debug table."""
    group_vals = np.array([means[d] for d in HBAR_GROUP if d in means])
    rest_vals = np.array([means[d] for d in REST_GROUP if d in means])
    if len(group_vals) == 0 or len(rest_vals) == 0:
        return -1e9
    pooled_std = np.sqrt((group_vals.var() + rest_vals.var()) / 2) + 1e-9
    return float((group_vals.mean() - rest_vals.mean()) / pooled_std)


def find_best_90_candidate(glyphs_by_digit: dict) -> tuple[dict, list[dict]]:
    """Sweep the 90deg candidate grid against the single-image sample
    glyphs, scoring each by _separation_score. Returns (winner, all_results
    sorted best-first)."""
    results = []
    for lambd in _LAMBD_GRID:
        for sigma in _SIGMA_GRID:
            for gamma in _GAMMA_GRID:
                kernel = _build_90_kernel(lambd, sigma, gamma)
                means = {d: _mean_response(g["normalized"], kernel)
                          for d, g in glyphs_by_digit.items()}
                score = _separation_score(means)
                results.append({"lambd": lambd, "sigma": sigma, "gamma": gamma,
                                 "score": score, "means": means})
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[0], results


def build_table(glyphs_by_digit: dict, kernel_45: np.ndarray, kernel_90: np.ndarray,
                params_45: dict, params_90: dict) -> np.ndarray:
    resp_45 = {d: (np.abs(cv2.filter2D(g["normalized"].astype(np.float32), -1, kernel_45)),
                    _mean_response(g["normalized"], kernel_45))
               for d, g in glyphs_by_digit.items()}
    resp_90 = {d: (np.abs(cv2.filter2D(g["normalized"].astype(np.float32), -1, kernel_90)),
                    _mean_response(g["normalized"], kernel_90))
               for d, g in glyphs_by_digit.items()}

    global_max = max(
        [m.max() for m, _ in resp_45.values()] + [m.max() for m, _ in resp_90.values()],
        default=1.0,
    )

    columns = ["original_crop", "binarized_crop", "normalized_12x20",
               f"gabor_45deg (shipped, l={params_45['lambd']},s={params_45['sigma']},g={params_45['gamma']})",
               f"gabor_90deg (candidate, l={params_90['lambd']},s={params_90['sigma']},g={params_90['gamma']})"]
    n_cols = len(columns)
    n_rows = len(DIGITS)

    W = LABEL_W + n_cols * CELL_W
    H = HEADER_H + n_rows * CELL_H
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)

    for j, name in enumerate(columns):
        x0 = LABEL_W + j * CELL_W
        cv2.putText(canvas, name[:24], (x0 + 4, HEADER_H - 28), cv2.FONT_HERSHEY_SIMPLEX,
                    0.38, (0, 0, 0), 1, cv2.LINE_AA)
        if len(name) > 24:
            cv2.putText(canvas, name[24:], (x0 + 4, HEADER_H - 14), cv2.FONT_HERSHEY_SIMPLEX,
                        0.38, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (x0, 0), (x0, H), (210, 210, 210), 1)
    cv2.line(canvas, (0, HEADER_H), (W, HEADER_H), (150, 150, 150), 1)
    cv2.putText(canvas, f"target group (horizontal lines): {','.join(HBAR_GROUP)}  "
                         f"(shared heatmap scale: max<={global_max:.3f})",
                (LABEL_W + 4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (90, 90, 90), 1, cv2.LINE_AA)

    for i, d in enumerate(DIGITS):
        y0 = HEADER_H + i * CELL_H
        cv2.line(canvas, (0, y0), (W, y0), (210, 210, 210), 1)
        g = glyphs_by_digit.get(d)
        in_group = d in HBAR_GROUP
        label_color = (0, 120, 0) if in_group else (0, 0, 0)

        cv2.putText(canvas, f"digit '{d}'" + ("  *" if in_group else ""),
                    (6, y0 + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.5, label_color, 1, cv2.LINE_AA)
        if g is not None:
            cv2.putText(canvas, g["source"][:16], (6, y0 + 42), cv2.FONT_HERSHEY_SIMPLEX,
                        0.32, (120, 120, 120), 1, cv2.LINE_AA)

        if g is None:
            for j in range(n_cols):
                x0 = LABEL_W + j * CELL_W
                _fit_and_paste(canvas, _blank_cell(CELL_W - 8, CELL_H - CAPTION_H - 8, "missing"),
                               x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)
            continue

        norm = g["normalized"]
        cell_imgs, captions = [], []
        cell_imgs.append(_to_bgr(g["raw"]));        captions.append("")
        cell_imgs.append(_to_bgr(g["binarized"]));  captions.append("")
        cell_imgs.append(_to_bgr(norm));            captions.append(f"{norm.shape[1]}x{norm.shape[0]}")

        m45, mean45 = resp_45[d]
        cell_imgs.append(_heatmap_overlay(norm, m45, global_max))
        captions.append(f"mean={mean45:.3f}")

        m90, mean90 = resp_90[d]
        cell_imgs.append(_heatmap_overlay(norm, m90, global_max))
        captions.append(f"mean={mean90:.3f}")

        for j, (img, cap) in enumerate(zip(cell_imgs, captions)):
            x0 = LABEL_W + j * CELL_W
            _fit_and_paste(canvas, img, x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)
            _put_caption(canvas, cap, x0, y0 + CELL_H, CELL_W)

    return canvas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", nargs="+", default=[DEFAULT_IMAGE],
                     help=f"1-2 source images whose pct-line digits together "
                          f"cover '0'-'9'  [default: {DEFAULT_IMAGE}]")
    ap.add_argument("--output", default="tests/outputs/daily/gabor_2457_retune_table.png",
                     help="Where to write the debug image")
    ap.add_argument("--no-gt-cache", action="store_true",
                     help="Force live Tesseract instead of tests/inputs/daily/tess_gt_cache.py")
    args = ap.parse_args(argv)

    image_paths = [Path(p) for p in args.images]
    missing = [p for p in image_paths if not p.exists()]
    if missing:
        sys.exit(f"Image(s) not found: {missing}")

    gt_cache = {} if args.no_gt_cache else (_load_tess_gt_cache() or {})
    glyphs_by_digit = collect_one_glyph_per_digit(image_paths, gt_cache=gt_cache)

    missing_digits = [d for d in DIGITS if d not in glyphs_by_digit]
    if missing_digits:
        print(f"WARNING: {args.images} do not cover digit(s) {missing_digits} -- "
              f"those rows will be marked 'missing'.")

    print(f"Sample glyphs collected: { {d: g['source'] for d, g in sorted(glyphs_by_digit.items())} }")

    # Baseline: current shipped 45deg raw mean response per digit, on this
    # exact sample, so it's directly comparable to the 90deg sweep below.
    kernel_45 = _GABOR_KERNELS[0]
    means_45 = {d: _mean_response(g["normalized"], kernel_45) for d, g in glyphs_by_digit.items()}
    score_45 = _separation_score(means_45)
    print(f"\nShipped gabor_45deg (lambd={_GABOR_PARAMS['lambd']}, sigma={_GABOR_PARAMS['sigma']}, "
          f"gamma={_GABOR_PARAMS['gamma']}) raw mean response per digit:")
    for d in DIGITS:
        if d in means_45:
            marker = " *" if d in HBAR_GROUP else ""
            print(f"  '{d}'{marker}: {means_45[d]:8.3f}")
    print(f"  2/4/5/7-vs-rest separation score: {score_45:+.3f}")

    print(f"\nSweeping {len(_LAMBD_GRID)*len(_SIGMA_GRID)*len(_GAMMA_GRID)} "
          f"90deg candidates for best 2/4/5/7-vs-rest separation ...")
    winner, all_results = find_best_90_candidate(glyphs_by_digit)
    print(f"\nTop 10 candidates by separation score:")
    print(f"{'lambd':>6} {'sigma':>6} {'gamma':>6}  {'score':>8}")
    for r in all_results[:10]:
        print(f"{r['lambd']:>6.1f} {r['sigma']:>6.2f} {r['gamma']:>6.2f}  {r['score']:>8.3f}")

    print(f"\nBest 90deg candidate: lambd={winner['lambd']} sigma={winner['sigma']} gamma={winner['gamma']}"
          f"  (separation score {winner['score']:+.3f} vs shipped 45deg's {score_45:+.3f})")
    print("Raw mean response per digit (best 90deg candidate):")
    for d in DIGITS:
        if d in winner["means"]:
            marker = " *" if d in HBAR_GROUP else ""
            print(f"  '{d}'{marker}: {winner['means'][d]:8.3f}")

    kernel_90 = _build_90_kernel(winner["lambd"], winner["sigma"], winner["gamma"])
    params_90 = {"lambd": winner["lambd"], "sigma": winner["sigma"], "gamma": winner["gamma"]}
    table = build_table(glyphs_by_digit, kernel_45, kernel_90, _GABOR_PARAMS, params_90)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), table)
    print(f"\nWrote {table.shape[1]}x{table.shape[0]} debug table -> {out_path}")
    print("NOTE: single-image sample only (unit-level eyeball check) -- any promising "
          "candidate still needs calibrate_gabor.py-style real-pipeline validation "
          "before touching gfl2/stat_ocr_fft.py.")


if __name__ == "__main__":
    main()
