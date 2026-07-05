# -*- coding: utf-8 -*-
"""
debugs/debug_gabor_90_tune.py -- tune a 90deg (horizontal-line) Gabor
kernel standalone, targeting separation of {2,4,5,7} from the rest.

Does NOT compare against or touch the shipped 45deg kernel/feature -- that
comparison was a distraction from the actual question, which is simply:
can a properly tuned 90deg Gabor kernel produce a strong, clean signal for
horizontal-line digits, on its own terms? If 45deg produces a usable
signal for its target pair, a correctly-oriented, correctly-scaled 90deg
kernel should be able to as well -- this script searches for that
parameterization directly.

GAMMA AND LINE DETECTION: for theta=90deg exactly, OpenCV's Gabor formula
reduces to value = exp(-0.5*(y^2 + gamma^2*x^2)/sigma^2) * cos(2*pi*y/lambda)
(x=column, y=row, origin at kernel center) -- i.e. the envelope's std is
`sigma` along the row axis (the oscillation direction) and `sigma/gamma`
along the column axis (the elongation/"along-the-line" axis). LOW gamma
therefore elongates the kernel along the line's own direction, exactly the
classic line-detector configuration -- gamma near 1 gives a roughly
isotropic (blob-like) receptive field, not a line detector.

CLIPPING GUARD: a low gamma inflates sigma/gamma, which can easily exceed
the kernel's own half-width -- if the Gaussian envelope doesn't decay to
~0 before the kernel edge, the kernel is hard-clipped (a truncated
sinusoid, not a tapered Gabor), which can look fine on a coarse row/col
variance check while silently not being the filter the parameters claim
to describe. `_envelope_containment` computes the actual required margin
analytically (row/col std vs kernel half-width) and gates candidates on
it BEFORE scoring on digit separation, instead of an empirical shape
heuristic that doesn't distinguish "tapered" from "clipped."

DOES NOT TOUCH gfl2/stat_ocr_fft.py -- prototyping only, same convention
as debug_vstroke_feature.py / debug_hbar_feature.py.

Usage:
    python debugs/debug_gabor_90_tune.py
    python debugs/debug_gabor_90_tune.py --images single/fb_d_060518.png
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
from gfl2.stat_ocr_fft import _GABOR_STEP

from debugs.debug_gabor_features import (
    DEFAULT_IMAGE, DIGITS, CELL_W, CELL_H, LABEL_W, HEADER_H, CAPTION_H,
    collect_one_glyph_per_digit, _to_bgr, _fit_and_paste, _heatmap_overlay,
    _put_caption, _blank_cell,
)

HBAR_GROUP = ("2", "4", "5", "7")
REST_GROUP = tuple(d for d in DIGITS if d not in HBAR_GROUP)

# Sigma kept small and gamma allowed to run low -- a low gamma inflates
# sigma/gamma (the column/elongation-axis std), so containment forces the
# search toward small sigma once gamma is small (see _envelope_containment).
# ksize extended past 15 -- with the glyph padded to a 20x20 square (see
# _pad_to_square), a kernel up to ~19 no longer exceeds the canvas itself.
_LAMBD_GRID = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0]
_SIGMA_GRID = [0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
_GAMMA_GRID = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0]
_KSIZE_GRID = [5, 7, 9, 11, 13, 15, 17, 19]
_ANGLE_90 = 2 * np.pi / _GABOR_STEP   # 90deg, same indexing convention as production
_CONTAINMENT_MARGIN = 2.5   # required multiples of std within the kernel half-width

_PAD_TARGET = 20   # square canvas -- matches NORM_H_PCT so width no longer
                    # bottlenecks the elongation (column) axis at 12px


def _pad_to_square(glyph: np.ndarray, target: int = _PAD_TARGET) -> np.ndarray:
    """Center `glyph` (background=0, per _normalize_glyph's convention) in
    a target x target canvas, padding width with background columns.
    Only pads (never shrinks) -- a no-op if glyph is already >= target
    wide. This removes the 12px-width bottleneck that forced low-gamma
    (elongated) candidates into a clipping-avoiding sigma so small it fell
    below the corpus's real stroke width (see the RESOLUTION CONSTRAINT
    finding in this module's exploration history)."""
    h, w = glyph.shape[:2]
    if w >= target:
        return glyph
    canvas = np.zeros((h, target), dtype=glyph.dtype)
    x0 = (target - w) // 2
    canvas[:, x0:x0 + w] = glyph
    return canvas


def _build_90_kernel(ksize: int, lambd: float, sigma: float, gamma: float,
                      energy_normalize: bool = True) -> np.ndarray:
    """energy_normalize divides by the kernel's own L2 norm. Without this,
    a bigger (sigma, ksize) kernel has strictly more nonzero support and
    therefore mechanically higher total energy -- larger raw mean response
    regardless of how well-aligned it is with genuine horizontal-line
    content. That confound is exactly what let an isotropic (gamma=1),
    large-sigma candidate win the first pass: it wasn't a better line
    detector, it was just a bigger, more energetic filter. Normalizing
    kernel energy puts every (ksize, sigma, gamma) candidate on equal
    footing so the comparison is about alignment/shape, not raw size."""
    k = cv2.getGaborKernel((ksize, ksize), sigma, _ANGLE_90, lambd, gamma, 0.0, cv2.CV_32F)
    if energy_normalize:
        k = k / (np.linalg.norm(k) + 1e-9)
    return k


def _envelope_containment(ksize: int, sigma: float, gamma: float) -> dict:
    """Analytic containment check for theta=90deg: sig_row=sigma (the
    oscillation/thickness axis), sig_col=sigma/gamma (the elongation/
    along-the-line axis). `margin` is how many multiples of MARGIN*std fit
    inside the kernel half-width on the tightest axis -- >=1.0 means the
    envelope is adequately tapered before the kernel edge; <1.0 means it's
    hard-clipped (see module docstring's CLIPPING GUARD note)."""
    half = ksize / 2.0
    sig_row = sigma
    sig_col = sigma / gamma
    margin_row = half / (_CONTAINMENT_MARGIN * sig_row)
    margin_col = half / (_CONTAINMENT_MARGIN * sig_col)
    return {"sig_row": sig_row, "sig_col": sig_col,
            "margin": min(margin_row, margin_col), "fits": min(margin_row, margin_col) >= 1.0}


def _mean_response(norm_glyph: np.ndarray, kernel: np.ndarray) -> float:
    f32 = norm_glyph.astype(np.float32)
    return float(np.abs(cv2.filter2D(f32, -1, kernel)).mean())


def _separation_score(means: dict) -> float:
    group_vals = np.array([means[d] for d in HBAR_GROUP if d in means])
    rest_vals = np.array([means[d] for d in REST_GROUP if d in means])
    if len(group_vals) == 0 or len(rest_vals) == 0:
        return -1e9
    pooled_std = np.sqrt((group_vals.var() + rest_vals.var()) / 2) + 1e-9
    return float((group_vals.mean() - rest_vals.mean()) / pooled_std)


def sweep(glyphs_by_digit: dict, require_fit: bool = True) -> list[dict]:
    """Sweep the full (ksize, lambd, sigma, gamma) grid, gated by the
    analytic envelope-containment check (see _envelope_containment) --
    candidates whose implied Gaussian envelope would be hard-clipped by
    the kernel window are skipped before even building the kernel (cheap:
    containment only depends on ksize/sigma/gamma, not lambd, so this also
    avoids redundant work across the lambd grid for a combo already known
    to clip). lambd does not affect containment (it only sets the
    oscillation wavelength within the envelope), so it's still swept
    independently for its effect on separation score."""
    results = []
    skipped_clipped = 0
    for ksize in _KSIZE_GRID:
        for sigma in _SIGMA_GRID:
            for gamma in _GAMMA_GRID:
                containment = _envelope_containment(ksize, sigma, gamma)
                if require_fit and not containment["fits"]:
                    skipped_clipped += len(_LAMBD_GRID)
                    continue
                for lambd in _LAMBD_GRID:
                    kernel = _build_90_kernel(ksize, lambd, sigma, gamma)
                    means = {d: _mean_response(g["normalized"], kernel)
                              for d, g in glyphs_by_digit.items()}
                    score = _separation_score(means)
                    results.append({"ksize": ksize, "lambd": lambd, "sigma": sigma,
                                     "gamma": gamma, "score": score, "means": means,
                                     **containment})
    results.sort(key=lambda r: r["score"], reverse=True)
    print(f"  ({skipped_clipped} clipped combos skipped before kernel evaluation)")
    return results


def build_table(glyphs_by_digit: dict, candidates: list[dict]) -> np.ndarray:
    """One row per digit, one column per candidate (plus original/binarized/
    normalized lead-in columns)."""
    kernels = [(_build_90_kernel(c["ksize"], c["lambd"], c["sigma"], c["gamma"]), c)
               for c in candidates]
    resp = {}
    for d, g in glyphs_by_digit.items():
        norm = g["normalized"].astype(np.float32)
        resp[d] = [(np.abs(cv2.filter2D(norm, -1, k)), _mean_response(g["normalized"], k))
                   for k, _ in kernels]

    global_max = max(
        (m.max() for maps in resp.values() for m, _ in maps), default=1.0,
    )

    columns = ["original_crop", "binarized_crop", "normalized_12x20"] + [
        f"90deg ks={c['ksize']} l={c['lambd']} s={c['sigma']} g={c['gamma']}"
        for c in candidates
    ]
    n_cols = len(columns)
    n_rows = len(DIGITS)
    W = LABEL_W + n_cols * CELL_W
    H = HEADER_H + n_rows * CELL_H
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)

    for j, name in enumerate(columns):
        x0 = LABEL_W + j * CELL_W
        cv2.putText(canvas, name[:22], (x0 + 4, HEADER_H - 28), cv2.FONT_HERSHEY_SIMPLEX,
                    0.34, (0, 0, 0), 1, cv2.LINE_AA)
        if len(name) > 22:
            cv2.putText(canvas, name[22:], (x0 + 4, HEADER_H - 14), cv2.FONT_HERSHEY_SIMPLEX,
                        0.34, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (x0, 0), (x0, H), (210, 210, 210), 1)
    cv2.line(canvas, (0, HEADER_H), (W, HEADER_H), (150, 150, 150), 1)
    cv2.putText(canvas, f"target group: {','.join(HBAR_GROUP)}  (shared scale: max<={global_max:.3f})",
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

        for m, mean_v in resp[d]:
            cell_imgs.append(_heatmap_overlay(norm, m, global_max))
            captions.append(f"mean={mean_v:.3f}")

        for j, (img, cap) in enumerate(zip(cell_imgs, captions)):
            x0 = LABEL_W + j * CELL_W
            _fit_and_paste(canvas, img, x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)
            _put_caption(canvas, cap, x0, y0 + CELL_H, CELL_W)

    return canvas


def build_kernel_preview(candidates: list[dict]) -> np.ndarray:
    """Render each candidate's actual (upscaled) kernel matrix -- the
    containment check made visible (margin>=1.0 means adequately tapered
    before the kernel edge) instead of only a scalar score."""
    cell = 160
    imgs = []
    for c in candidates:
        k = _build_90_kernel(c["ksize"], c["lambd"], c["sigma"], c["gamma"])
        kn = (k - k.min()) / (k.max() - k.min() + 1e-9)
        kn = (kn * 255).astype(np.uint8)
        kn = cv2.resize(kn, (cell, cell), interpolation=cv2.INTER_NEAREST)
        kn = _to_bgr(kn)
        label = f"ks={c['ksize']} l={c['lambd']} s={c['sigma']} g={c['gamma']}"
        cv2.putText(kn, label, (3, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(kn, f"sig_row={c['sig_row']:.2f} sig_col={c['sig_col']:.2f}", (3, cell - 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(kn, f"margin={c['margin']:.2f} score={c['score']:+.3f}", (3, cell - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, (0, 0, 255), 1, cv2.LINE_AA)
        imgs.append(kn)
    return np.hstack(imgs)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", nargs="+", default=[DEFAULT_IMAGE])
    ap.add_argument("--output", default="tests/outputs/daily/gabor_90_tune_table.png")
    ap.add_argument("--kernel-preview", default="tests/outputs/daily/gabor_90_tune_kernels.png")
    ap.add_argument("--top-n", type=int, default=4, help="How many top candidates to render [default: 4]")
    ap.add_argument("--allow-clipping", action="store_true",
                     help="Disable the envelope-containment gate (debugging only -- "
                          "lets hard-clipped candidates compete on separation score)")
    ap.add_argument("--no-pad", action="store_true",
                     help="Skip the 12->20 width padding (debugging only -- reproduces "
                          "the original 12x20-bottlenecked resolution-constraint result)")
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

    if not args.no_pad:
        for g in glyphs_by_digit.values():
            before_w = g["normalized"].shape[1]
            g["normalized"] = _pad_to_square(g["normalized"])
        print(f"Padded normalized glyphs {before_w}x20 -> "
              f"{glyphs_by_digit[next(iter(glyphs_by_digit))]['normalized'].shape[1]}x20 (background=0)")

    total = len(_KSIZE_GRID) * len(_LAMBD_GRID) * len(_SIGMA_GRID) * len(_GAMMA_GRID)
    print(f"\nSweeping up to {total} (ksize, lambd, sigma, gamma) 90deg candidates "
          f"(containment_margin>=1.0 required unless --allow-clipping) ...")
    results = sweep(glyphs_by_digit, require_fit=not args.allow_clipping)
    print(f"{len(results)}/{total} candidates evaluated (envelope fits the kernel window).")

    print(f"\nTop {args.top_n} by separation score:")
    print(f"{'ksize':>6} {'lambd':>6} {'sigma':>6} {'gamma':>6}  {'sig_row':>8} {'sig_col':>8} "
          f"{'margin':>7} {'score':>8}")
    for r in results[:args.top_n]:
        print(f"{r['ksize']:>6} {r['lambd']:>6.1f} {r['sigma']:>6.2f} {r['gamma']:>6.2f}  "
              f"{r['sig_row']:>8.2f} {r['sig_col']:>8.2f} {r['margin']:>7.2f} {r['score']:>8.3f}")

    winner = results[0]
    print(f"\nWinner: ksize={winner['ksize']} lambd={winner['lambd']} sigma={winner['sigma']} "
          f"gamma={winner['gamma']}  (score={winner['score']:+.3f}, containment margin={winner['margin']:.2f})")
    print("Raw mean response per digit:")
    for d in DIGITS:
        if d in winner["means"]:
            marker = " *" if d in HBAR_GROUP else ""
            print(f"  '{d}'{marker}: {winner['means'][d]:8.3f}")

    top = results[:args.top_n]
    kernel_preview = build_kernel_preview(top)
    Path(args.kernel_preview).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(args.kernel_preview, kernel_preview)
    print(f"\nWrote kernel-shape preview -> {args.kernel_preview}")

    table = build_table(glyphs_by_digit, top)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), table)
    print(f"Wrote {table.shape[1]}x{table.shape[0]} debug table -> {out_path}")


if __name__ == "__main__":
    main()
