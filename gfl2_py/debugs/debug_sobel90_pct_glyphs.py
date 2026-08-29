# -*- coding: utf-8 -*-
"""
debugs/debug_sobel90_pct_glyphs.py -- follow-up to
debugs/debug_sobel45_pct_glyphs.py, switching the probe kernel from 45deg
to 90deg (classic Sobel-Y, horizontal-edge detector).

WHY: the 45deg kernel was confirmed via a synthetic thin-stroke test to be
genuinely orientation-selective (mean response 0deg=76.5, 45deg=247.4,
90deg=144.1, 135deg=12.8 -- not a kernel bug), but on REAL pct-line glyphs
it strongly detected '7's HORIZONTAL top bar while only lightly catching
'7's diagonal descender (which doesn't actually render at a clean 45deg in
this font), and by the 2nd iterated convolution the diagonal response had
vanished while the horizontal one survived. A morphological-open
pre-processing step was tried next (hoping to suppress small incidental
structure while keeping real strokes, since repeated LINEAR convolution
turned out NOT to behave like morphological opening -- it's frequency-
selective, not size-selective) but a 2x2 structuring element over-eroded
these thin strokes before the Sobel step ever ran, so it was dropped by
explicit direction -- this script goes directly from the padded glyph to
the iterated 90deg convolution, matching '7's reliably-detected horizontal
bar instead of chasing the off-angle diagonal.

PIPELINE:
  1. Re-isolate glyphs from assets/fonts/glyph_daily_pct.png (contour +
     glyph_lookup.py re-derivation, same as debug_sobel45_pct_glyphs.py).
  2. Pad into ONE consistent canvas, sized from the ACTUAL max
     width/height across the extracted glyphs -- computed fresh every
     run, never a remembered constant.
  3. FFT the padded (grayscale, unbinarized) glyph.
  4. "Convolve" against a 90deg Sobel kernel via frequency-domain
     multiplication, iterated n=1,2,3 by raising the kernel's frequency
     response to the n-th power before one inverse FFT per stage
     (mathematically equivalent to re-convolving the spatial result n
     times for this fixed linear filter).
  5. One heatmap per (glyph, n), color scale shared across every glyph
     WITHIN a stage (not across stages -- see debug_sobel45_pct_glyphs.py
     module docstring for why one global scale crushed early stages).

Standalone probe -- nothing here is wired into any classifier.

Usage:
    python debugs/debug_sobel90_pct_glyphs.py
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from debugs.debug_sobel45_pct_glyphs import (
    _DEFAULT_ATLAS, _DEFAULT_LOOKUP, _load_lookup, load_atlas_glyphs,
    pad_to, _freq_response, _to_bgr, _fit_and_paste, _heatmap_overlay,
    _put_caption, N_STAGES, CELL_W, CELL_H, LABEL_W, HEADER_H, CAPTION_H,
)

_DEFAULT_OUTPUT = _ROOT / "tests" / "outputs" / "daily" / "sobel90_5x5_pct_glyph_table.png"

# 90deg (classic Sobel-Y) horizontal-edge detector, 5x5 -- OpenCV's own
# generalized Sobel construction (verified via cv2.getDerivKernels(dx=0,
# dy=1, ksize=5)): outer product of a 5-tap binomial smoothing vector
# [1,4,6,4,1] (x-axis) and a 5-tap central-difference derivative vector
# [-1,-2,0,2,1] (y-axis) -- wider smoothing than the 3x3 version, so less
# sensitive to single-pixel noise but blurs nearby edges together more.
SOBEL_90 = np.array([
    [-1, -4,  -6, -4, -1],
    [-2, -8, -12, -8, -2],
    [ 0,  0,   0,  0,  0],
    [ 2,  8,  12,  8,  2],
    [ 1,  4,   6,  4,  1],
], dtype=np.float64)


def sobel90_fft_stages(padded_glyph: np.ndarray, margin: int, n_stages: int = N_STAGES) -> list[np.ndarray]:
    h, w = padded_glyph.shape
    G = np.fft.fft2(padded_glyph.astype(np.float64))
    K = _freq_response(SOBEL_90, (h, w))
    stages = []
    Kpow = np.ones_like(K)
    for _ in range(n_stages):
        Kpow = Kpow * K
        resp = np.fft.ifft2(G * Kpow)
        mag = np.abs(resp)[margin:h - margin, margin:w - margin]
        stages.append(mag)
    return stages


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--atlas", default=str(_DEFAULT_ATLAS))
    ap.add_argument("--lookup", default=str(_DEFAULT_LOOKUP))
    ap.add_argument("--output", default=str(_DEFAULT_OUTPUT))
    args = ap.parse_args(argv)

    atlas_path = Path(args.atlas)
    lookup_all = _load_lookup(Path(args.lookup))
    lookup = lookup_all[atlas_path.name]

    glyphs, bg_gray = load_atlas_glyphs(atlas_path, lookup)

    # Derived fresh from the actual extracted crops every run -- not a
    # remembered/hardcoded constant.
    target_w = max(g["w"] for g in glyphs)
    target_h = max(g["h"] for g in glyphs)
    print(f"{len(glyphs)} glyphs isolated from {atlas_path.name}; "
          f"consistent canvas = {target_w}x{target_h} (max native w/h, "
          f"measured this run), bg_gray={bg_gray}")

    # Circular-convolution wraparound spreads by (kernel_size-1) per pass;
    # margin must cover N_STAGES passes of the ACTUAL kernel size in use
    # (was hardcoded for the earlier 3x3 kernel -- must scale with the 5x5
    # kernel now, or wraparound would contaminate the glyph content).
    ksize = SOBEL_90.shape[0]
    margin = (ksize - 1) * N_STAGES + 2
    for g in glyphs:
        padded = pad_to(g["native"], target_w, target_h, bg_gray)
        g["padded"] = padded
        canvas_for_fft = np.full((target_h + 2 * margin, target_w + 2 * margin),
                                  bg_gray, dtype=np.uint8)
        canvas_for_fft[margin:margin + target_h, margin:margin + target_w] = padded
        g["stages"] = sobel90_fft_stages(canvas_for_fft, margin)

    stage_max = [max(float(g["stages"][n].max()) for g in glyphs) for n in range(N_STAGES)]

    print(f"\nPer-glyph MEAN response magnitude (per-stage scale max={[round(m) for m in stage_max]}):")
    print(f"{'char':>5}  " + "  ".join(f"n={n+1}" for n in range(N_STAGES)))
    ranked_mean = []
    for g in glyphs:
        means = [float(s.mean()) for s in g["stages"]]
        ranked_mean.append((g["char"], means))
        print(f"{g['char']!r:>5}  " + "  ".join(f"{m:6.3f}" for m in means))
    ranked_mean.sort(key=lambda t: t[1][-1], reverse=True)
    print(f"Ranked by n={N_STAGES} mean response (highest first): "
          + ", ".join(f"'{c}'({m[-1]:.3f})" for c, m in ranked_mean))

    print(f"\nPer-glyph MAX response magnitude (per-stage scale max={[round(m) for m in stage_max]}):")
    print(f"{'char':>5}  " + "  ".join(f"n={n+1}" for n in range(N_STAGES)))
    ranked_max = []
    for g in glyphs:
        maxes = [float(s.max()) for s in g["stages"]]
        ranked_max.append((g["char"], maxes))
        print(f"{g['char']!r:>5}  " + "  ".join(f"{m:8.2f}" for m in maxes))
    ranked_max.sort(key=lambda t: t[1][-1], reverse=True)
    print(f"Ranked by n={N_STAGES} max response (highest first): "
          + ", ".join(f"'{c}'({m[-1]:.2f})" for c, m in ranked_max))

    columns = ["native", f"padded {target_w}x{target_h}"] + [f"sobel90 x{n+1}" for n in range(N_STAGES)]
    n_cols = len(columns)
    n_rows = len(glyphs)
    W = LABEL_W + n_cols * CELL_W
    H = HEADER_H + n_rows * CELL_H
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)

    for j, name in enumerate(columns):
        x0 = LABEL_W + j * CELL_W
        cv2.putText(canvas, name, (x0 + 4, HEADER_H - 14), cv2.FONT_HERSHEY_SIMPLEX,
                    0.42, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (x0, 0), (x0, H), (210, 210, 210), 1)
    cv2.line(canvas, (0, HEADER_H), (W, HEADER_H), (150, 150, 150), 1)
    cv2.putText(canvas, f"(per-stage scale, shared across digits within each: "
                         f"{[round(m) for m in stage_max]}; canvas {target_w}x{target_h} "
                         f"measured this run)",
                (LABEL_W + 4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (90, 90, 90), 1, cv2.LINE_AA)

    for i, g in enumerate(glyphs):
        y0 = HEADER_H + i * CELL_H
        cv2.line(canvas, (0, y0), (W, y0), (210, 210, 210), 1)
        cv2.putText(canvas, f"'{g['char']}'", (10, y0 + CELL_H // 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 0), 1, cv2.LINE_AA)

        cell_imgs = [_to_bgr(g["native"]), _to_bgr(g["padded"])]
        captions = ["", f"{g['w']}x{g['h']}"]
        for n, resp in enumerate(g["stages"]):
            cell_imgs.append(_heatmap_overlay(g["padded"], resp, stage_max[n]))
            captions.append(f"mean={resp.mean():.3f}")

        for j, (img, cap) in enumerate(zip(cell_imgs, captions)):
            x0 = LABEL_W + j * CELL_W
            _fit_and_paste(canvas, img, x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)
            _put_caption(canvas, cap, x0, y0 + CELL_H, CELL_W)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas)
    print(f"\nWrote {canvas.shape[1]}x{canvas.shape[0]} debug table -> {out_path}")


if __name__ == "__main__":
    main()
