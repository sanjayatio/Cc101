# -*- coding: utf-8 -*-
"""
debugs/debug_gabor_4_rotated_bruteforce.py -- brute-force (ksize, lambd,
sigma, gamma) against a SINGLE rotated '4' glyph only, ignoring every
other digit. gamma is restricted to <=0.5 (a genuine elongated line
detector, not the near-isotropic "winner" from the whole-corpus sweep
that turned out to just be a blob/energy detector -- see this module's
conversation history: gamma=1.0 numerically separated {2,4,5,7} from the
rest on aggregate, but never actually detected '4' specifically, which
ranked at or near the bottom of all 10 digits in every configuration
tried).

WHY SINGLE-DIGIT, NO COMPARISON GROUP: the whole-corpus separation score
(mean of group vs mean of rest) can look good while completely failing on
one target member -- exactly what happened to '4' throughout this
exploration. This script instead asks a narrower, more honest question:
of all (ksize, lambd, sigma, gamma<=0.5) candidates that don't hard-clip,
which ones produce the strongest matched-filter response to '4's own
crossbar, full stop -- no averaging across digits to hide behind.

ORIENTATION: the glyph is rotated +45deg first (a horizontal line becomes
a ~45deg line after rotation), so the kernel is built at theta=45deg to
match -- consistent with the earlier finding that pairing the WRONG
orientation with a rotated crop actively hurts (k90-on-rotated scored
worse than k90-on-original in the whole-corpus experiment).

SCORING: energy-normalized kernel (unit L2 norm, matching this module's
_build_90_kernel convention) so raw kernel size/energy doesn't confound
the ranking, then MAX (not mean) of |filter response| over the rotated
crop -- a whole-glyph mean was already shown not to rescue '4' (see
conversation history); max asks whether ANY position in the crop matches
the kernel strongly, closer in spirit to hbar/vstroke's own sliding-
window max design.

DOES NOT TOUCH gfl2/stat_ocr_v0_2_0.py -- prototyping only.

Usage:
    python debugs/debug_gabor_4_rotated_bruteforce.py
"""
from __future__ import annotations
import sys
import argparse
from pathlib import Path
import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr_v0_1_0 import _load_tess_gt_cache
from debugs.debug_gabor_features import (
    DEFAULT_IMAGE, CELL_W, CELL_H, LABEL_W, HEADER_H, CAPTION_H,
    collect_one_glyph_per_digit, _to_bgr, _fit_and_paste, _heatmap_overlay, _put_caption,
)
from debugs.debug_gabor_45_on_rotated import _rotate_45, ROTATE_CANVAS

TARGET_DIGIT = "4"
THETA_DEG = 45   # matches the post-rotation orientation of an originally-horizontal line

# gamma capped at 0.5 per explicit direction ("can't be greater than 0.5,
# ideally lower") -- biased toward low values to actually test elongation,
# not repeat the near-isotropic result already shown to be a false winner.
_GAMMA_GRID  = [0.05, 0.08, 0.1, 0.12, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
_SIGMA_GRID  = [0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
_LAMBD_GRID  = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0]
_KSIZE_GRID  = [7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
_CONTAINMENT_MARGIN = 2.5


def _build_kernel(ksize: int, lambd: float, sigma: float, gamma: float,
                   theta_deg: float = THETA_DEG, energy_normalize: bool = True) -> np.ndarray:
    theta = np.deg2rad(theta_deg)
    k = cv2.getGaborKernel((ksize, ksize), sigma, theta, lambd, gamma, 0.0, cv2.CV_32F)
    if energy_normalize:
        k = k / (np.linalg.norm(k) + 1e-9)
    return k


def _envelope_containment_45(ksize: int, sigma: float, gamma: float,
                              margin_mult: float = _CONTAINMENT_MARGIN) -> dict:
    """At theta=45deg both pixel axes see the SAME blended variance
    0.5*(sigma^2 + (sigma/gamma)^2) (the elongation is split across row
    and column instead of landing fully on one axis) -- see this module's
    conversation history for the derivation. margin>=1.0 means the
    envelope tapers to ~0 before the kernel edge on EITHER pixel axis."""
    sig_a, sig_b = sigma, sigma / gamma
    var_pixel = 0.5 * (sig_a ** 2 + sig_b ** 2)
    std_pixel = float(np.sqrt(var_pixel))
    half = ksize / 2.0
    margin = half / (margin_mult * std_pixel)
    return {"std_pixel": std_pixel, "margin": margin, "fits": margin >= 1.0}


def _max_response(img: np.ndarray, kernel: np.ndarray) -> float:
    return float(np.abs(cv2.filter2D(img.astype(np.float32), -1, kernel)).max())


def sweep(rotated_crop: np.ndarray) -> list[dict]:
    results = []
    skipped = 0
    for ksize in _KSIZE_GRID:
        for sigma in _SIGMA_GRID:
            for gamma in _GAMMA_GRID:
                containment = _envelope_containment_45(ksize, sigma, gamma)
                if not containment["fits"]:
                    skipped += len(_LAMBD_GRID)
                    continue
                for lambd in _LAMBD_GRID:
                    kernel = _build_kernel(ksize, lambd, sigma, gamma)
                    score = _max_response(rotated_crop, kernel)
                    results.append({"ksize": ksize, "lambd": lambd, "sigma": sigma,
                                     "gamma": gamma, "score": score, **containment})
    results.sort(key=lambda r: r["score"], reverse=True)
    print(f"  ({skipped} clipped combos skipped; {len(results)} evaluated)")
    return results


def build_debug_image(glyph_info: dict, rotated: np.ndarray, top: list[dict]) -> np.ndarray:
    kernels = [(_build_kernel(c["ksize"], c["lambd"], c["sigma"], c["gamma"]), c) for c in top]
    resp_maps = [(np.abs(cv2.filter2D(rotated.astype(np.float32), -1, k)), c) for k, c in kernels]
    global_max = max((m.max() for m, _ in resp_maps), default=1.0)

    columns = ["original_crop", "binarized_crop", "normalized_12x20", "rotated_45deg"] + [
        f"#{i+1} ks={c['ksize']} l={c['lambd']} s={c['sigma']} g={c['gamma']}"
        for i, c in enumerate(top)
    ]
    n_cols = len(columns)
    W = LABEL_W + n_cols * CELL_W
    H = HEADER_H + CELL_H
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)

    for j, name in enumerate(columns):
        x0 = LABEL_W + j * CELL_W
        cv2.putText(canvas, name[:22], (x0 + 4, HEADER_H - 28), cv2.FONT_HERSHEY_SIMPLEX,
                    0.32, (0, 0, 0), 1, cv2.LINE_AA)
        if len(name) > 22:
            cv2.putText(canvas, name[22:], (x0 + 4, HEADER_H - 14), cv2.FONT_HERSHEY_SIMPLEX,
                        0.32, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (x0, 0), (x0, H), (210, 210, 210), 1)
    cv2.line(canvas, (0, HEADER_H), (W, HEADER_H), (150, 150, 150), 1)
    cv2.putText(canvas, f"digit '4' only, rotated 45deg, gamma<=0.5, ranked by max(|response|) "
                         f"(shared scale: max<={global_max:.3f})",
                (LABEL_W + 4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (90, 90, 90), 1, cv2.LINE_AA)

    y0 = HEADER_H
    cell_imgs, captions = [], []
    cell_imgs.append(_to_bgr(glyph_info["raw"]));        captions.append("")
    cell_imgs.append(_to_bgr(glyph_info["binarized"]));  captions.append("")
    cell_imgs.append(_to_bgr(glyph_info["normalized"])); captions.append(f"{glyph_info['normalized'].shape[1]}x{glyph_info['normalized'].shape[0]}")
    cell_imgs.append(_to_bgr(rotated));                  captions.append(f"{rotated.shape[1]}x{rotated.shape[0]}")

    for m, c in resp_maps:
        cell_imgs.append(_heatmap_overlay(rotated, m, global_max))
        captions.append(f"score={c['score']:.3f}")

    for j, (img, cap) in enumerate(zip(cell_imgs, captions)):
        x0 = LABEL_W + j * CELL_W
        _fit_and_paste(canvas, img, x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)
        _put_caption(canvas, cap, x0, y0 + CELL_H, CELL_W)

    return canvas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", nargs="+", default=[DEFAULT_IMAGE])
    ap.add_argument("--output", default="tests/outputs/daily/gabor_4_rotated_bruteforce.png")
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--no-gt-cache", action="store_true")
    args = ap.parse_args(argv)

    image_paths = [Path(p) for p in args.images]
    missing = [p for p in image_paths if not p.exists()]
    if missing:
        sys.exit(f"Image(s) not found: {missing}")

    gt_cache = {} if args.no_gt_cache else (_load_tess_gt_cache() or {})
    glyphs = collect_one_glyph_per_digit(image_paths, gt_cache=gt_cache)
    if TARGET_DIGIT not in glyphs:
        sys.exit(f"Digit '{TARGET_DIGIT}' not found in {args.images}")
    glyph_info = glyphs[TARGET_DIGIT]
    print(f"Using digit '4' from {glyph_info['source']}")

    rotated = _rotate_45(glyph_info["normalized"])
    print(f"Rotated 45deg into a {ROTATE_CANVAS}x{ROTATE_CANVAS} canvas")

    total = len(_KSIZE_GRID) * len(_SIGMA_GRID) * len(_GAMMA_GRID) * len(_LAMBD_GRID)
    print(f"\nBrute-forcing {total} (ksize,lambd,sigma,gamma<=0.5) candidates at theta={THETA_DEG}deg, "
          f"scored by max(|response|) on THIS crop only ...")
    results = sweep(rotated)

    print(f"\nTop {args.top_n} parameter sets:")
    print(f"{'rank':>4} {'ksize':>6} {'lambd':>6} {'sigma':>6} {'gamma':>6}  {'std_pixel':>9} {'margin':>7} {'score':>8}")
    top = results[:args.top_n]
    for i, r in enumerate(top):
        print(f"{i+1:>4} {r['ksize']:>6} {r['lambd']:>6.1f} {r['sigma']:>6.2f} {r['gamma']:>6.2f}  "
              f"{r['std_pixel']:>9.3f} {r['margin']:>7.2f} {r['score']:>8.4f}")

    canvas = build_debug_image(glyph_info, rotated, top)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas)
    print(f"\nWrote {canvas.shape[1]}x{canvas.shape[0]} debug image -> {out_path}")


if __name__ == "__main__":
    main()
