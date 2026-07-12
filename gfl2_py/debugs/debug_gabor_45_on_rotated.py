# -*- coding: utf-8 -*-
"""
debugs/debug_gabor_45_on_rotated.py -- rotate each glyph by 45deg, then
apply the SHIPPED gabor_45 kernel (gfl2.stat_ocr_v0_2_0._GABOR_KERNELS[0],
whatever assets/fonts/gabor_calib.json currently holds -- lambd=5.0,
sigma=2.0, gamma=0.5 as of this writing) directly, unmodified.

RATIONALE: a horizontal line in the ORIGINAL glyph becomes a ~45deg line
in a 45deg-rotated glyph. So instead of retuning a separate 90deg kernel
from scratch (debug_gabor_90_tune.py's approach, which ran into a real
sigma/gamma-vs-glyph-resolution ceiling for genuine elongation), reuse the
kernel that's ALREADY validated end-to-end in the real two-agent pipeline
-- rotate the input instead of building a new filter. Whatever made 45deg
survive every ablation should transfer to horizontal-line digits once
their lines are rotated into the same 45deg orientation the kernel
already targets.

DOES NOT TOUCH gfl2/stat_ocr_v0_2_0.py -- prototyping only. Uses the shipped
kernel completely unmodified (imported directly, not rebuilt).

Usage:
    python debugs/debug_gabor_45_on_rotated.py
    python debugs/debug_gabor_45_on_rotated.py --images single/fb_d_060518.png
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
from gfl2.stat_ocr_v0_2_0 import _GABOR_KERNELS, _GABOR_PARAMS

from debugs.debug_gabor_features import (
    DEFAULT_IMAGE, DIGITS, CELL_W, CELL_H, LABEL_W, HEADER_H, CAPTION_H,
    collect_one_glyph_per_digit, _to_bgr, _fit_and_paste, _heatmap_overlay,
    _put_caption, _blank_cell,
)

HBAR_GROUP = ("2", "4", "5", "7")
REST_GROUP = tuple(d for d in DIGITS if d not in HBAR_GROUP)

# Canvas large enough that a 45deg rotation of a 12x20 glyph never clips a
# corner: the rotated bounding box of a WxH rect is
# W*|cos|+H*|sin| x W*|sin|+H*|cos| -- at 45deg that's (W+H)/sqrt(2) on
# each side, so ceil((12+20)/sqrt(2)) = 23 is the true minimum; padded
# further for a clean margin.
ROTATE_CANVAS = 30


def _rotate_45(glyph: np.ndarray, canvas: int = ROTATE_CANVAS) -> np.ndarray:
    """Center `glyph` (background=0) in a canvas x canvas square, rotate
    45deg about the canvas center, background-filled border."""
    h, w = glyph.shape[:2]
    base = np.zeros((canvas, canvas), dtype=glyph.dtype)
    y0, x0 = (canvas - h) // 2, (canvas - w) // 2
    base[y0:y0 + h, x0:x0 + w] = glyph
    center = (canvas / 2.0, canvas / 2.0)
    M = cv2.getRotationMatrix2D(center, 45, 1.0)
    return cv2.warpAffine(base, M, (canvas, canvas), flags=cv2.INTER_LINEAR,
                           borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def _mean_response(rotated: np.ndarray, kernel: np.ndarray) -> float:
    f32 = rotated.astype(np.float32)
    return float(np.abs(cv2.filter2D(f32, -1, kernel)).mean())


def _separation_score(means: dict) -> float:
    group_vals = np.array([means[d] for d in HBAR_GROUP if d in means])
    rest_vals = np.array([means[d] for d in REST_GROUP if d in means])
    if len(group_vals) == 0 or len(rest_vals) == 0:
        return -1e9
    pooled_std = np.sqrt((group_vals.var() + rest_vals.var()) / 2) + 1e-9
    return float((group_vals.mean() - rest_vals.mean()) / pooled_std)


def build_table(glyphs_by_digit: dict, kernel: np.ndarray, kernel_label: str = "gabor_45 (shipped)") -> np.ndarray:
    rotated_by_digit = {d: _rotate_45(g["normalized"]) for d, g in glyphs_by_digit.items()}
    resp = {d: (np.abs(cv2.filter2D(r.astype(np.float32), -1, kernel)), _mean_response(r, kernel))
            for d, r in rotated_by_digit.items()}
    means = {d: v[1] for d, v in resp.items()}
    maxes = {d: float(m.max()) for d, (m, _) in resp.items()}
    global_max = max((m.max() for m, _ in resp.values()), default=1.0)

    columns = ["original_crop", "binarized_crop", "normalized_12x20",
               "rotated_45deg", f"{kernel_label} on rotated"]
    n_cols = len(columns)
    n_rows = len(DIGITS)
    W = LABEL_W + n_cols * CELL_W
    H = HEADER_H + n_rows * CELL_H
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)

    for j, name in enumerate(columns):
        x0 = LABEL_W + j * CELL_W
        cv2.putText(canvas, name[:26], (x0 + 4, HEADER_H - 28), cv2.FONT_HERSHEY_SIMPLEX,
                    0.36, (0, 0, 0), 1, cv2.LINE_AA)
        if len(name) > 26:
            cv2.putText(canvas, name[26:], (x0 + 4, HEADER_H - 14), cv2.FONT_HERSHEY_SIMPLEX,
                        0.36, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (x0, 0), (x0, H), (210, 210, 210), 1)
    cv2.line(canvas, (0, HEADER_H), (W, HEADER_H), (150, 150, 150), 1)
    score = _separation_score(means)
    cv2.putText(canvas, f"target group: {','.join(HBAR_GROUP)}  separation_score={score:+.3f}  "
                         f"(shared scale: max<={global_max:.3f})",
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
        rotated = rotated_by_digit[d]
        m, mean_v = resp[d]

        cell_imgs, captions = [], []
        cell_imgs.append(_to_bgr(g["raw"]));        captions.append("")
        cell_imgs.append(_to_bgr(g["binarized"]));  captions.append("")
        cell_imgs.append(_to_bgr(norm));            captions.append(f"{norm.shape[1]}x{norm.shape[0]}")
        cell_imgs.append(_to_bgr(rotated));         captions.append(f"{rotated.shape[1]}x{rotated.shape[0]}")
        cell_imgs.append(_heatmap_overlay(rotated, m, global_max))
        captions.append(f"max={maxes[d]:.1f} mean={mean_v:.1f}")

        for j, (img, cap) in enumerate(zip(cell_imgs, captions)):
            x0 = LABEL_W + j * CELL_W
            _fit_and_paste(canvas, img, x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)
            _put_caption(canvas, cap, x0, y0 + CELL_H, CELL_W)

    return canvas, means, maxes, score


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", nargs="+", default=[DEFAULT_IMAGE])
    ap.add_argument("--output", default="tests/outputs/daily/gabor_45_rotated_table.png")
    ap.add_argument("--ksize", type=int, default=None, help="Override kernel size [default: shipped ksize=7]")
    ap.add_argument("--lambd", type=float, default=None, help="Override lambda [default: shipped]")
    ap.add_argument("--sigma", type=float, default=None, help="Override sigma [default: shipped]")
    ap.add_argument("--gamma", type=float, default=None, help="Override gamma [default: shipped]")
    ap.add_argument("--theta", type=float, default=45.0, help="Kernel orientation in degrees [default: 45]")
    ap.add_argument("--no-gt-cache", action="store_true")
    args = ap.parse_args(argv)

    image_paths = [Path(p) for p in args.images]
    missing = [p for p in image_paths if not p.exists()]
    if missing:
        sys.exit(f"Image(s) not found: {missing}")

    gt_cache = {} if args.no_gt_cache else (_load_tess_gt_cache() or {})
    glyphs_by_digit = collect_one_glyph_per_digit(image_paths, gt_cache=gt_cache)
    missing_digits = [d for d in DIGITS if d not in glyphs_by_digit]
    if missing_digits:
        print(f"WARNING: missing digit(s) {missing_digits}")
    print(f"Sample glyphs: { {d: g['source'] for d, g in sorted(glyphs_by_digit.items())} }")

    overriding = any(v is not None for v in (args.ksize, args.lambd, args.sigma, args.gamma))
    if overriding:
        ksize = args.ksize if args.ksize is not None else 7
        lambd = args.lambd if args.lambd is not None else _GABOR_PARAMS["lambd"]
        sigma = args.sigma if args.sigma is not None else _GABOR_PARAMS["sigma"]
        gamma = args.gamma if args.gamma is not None else _GABOR_PARAMS["gamma"]
        theta = np.deg2rad(args.theta)
        kernel = cv2.getGaborKernel((ksize, ksize), sigma, theta, lambd, gamma, 0.0, cv2.CV_32F)
        kernel = kernel / (np.linalg.norm(kernel) + 1e-9)
        label = f"ks={ksize} l={lambd} s={sigma} g={gamma} th={args.theta:.0f}"
        print(f"Using OVERRIDE kernel: {label} (energy-normalized)")
    else:
        kernel = _GABOR_KERNELS[0]
        label = f"gabor_45 shipped l={_GABOR_PARAMS['lambd']} s={_GABOR_PARAMS['sigma']} g={_GABOR_PARAMS['gamma']}"
        print(f"Using SHIPPED gabor_45 kernel: lambd={_GABOR_PARAMS['lambd']} "
              f"sigma={_GABOR_PARAMS['sigma']} gamma={_GABOR_PARAMS['gamma']} (unmodified)")

    table, means, maxes, score = build_table(glyphs_by_digit, kernel, kernel_label=label)

    print("\nPer-digit response (kernel applied to the 45deg-rotated glyph):")
    print(f"{'digit':>6} {'max_resp':>10} {'mean_resp':>10}")
    for d in DIGITS:
        if d in means:
            marker = "*" if d in HBAR_GROUP else " "
            print(f"{d}{marker:>5} {maxes[d]:>10.3f} {means[d]:>10.3f}")
    print(f"\nMEAN separation score (2/4/5/7 vs rest): {score:+.3f}")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), table)
    print(f"\nWrote {table.shape[1]}x{table.shape[0]} debug table -> {out_path}")


if __name__ == "__main__":
    main()
