# -*- coding: utf-8 -*-
"""
debugs/debug_sobel45_pct_glyphs.py -- exploratory FFT + iterated 45deg-Sobel
debug table for assets/fonts/glyph_daily_pct.png, asking whether a plain
Sobel-diagonal operator (not Gabor -- see docs/known_issues.txt §24/§25 for
the extensive, largely-negative Gabor-as-line-detector history on this
exact '4'/'7' problem) can segregate '4'/'7' from the rest of the pct-line
digit set, and whether iterating the convolution sharpens that signal.

PIPELINE (matches the request this script was built for):
  1. Re-isolate every glyph from assets/fonts/glyph_daily_pct.png via a
     plain threshold + cv2.findContours pass, sorted left-to-right, then
     labelled via assets/fonts/glyph_lookup.py's index->char map -- this
     is exactly the "no coordinates stored, re-derive them yourself"
     contract that atlas was built to support (see
     debugs/build_glyph_reference.py's module docstring).
  2. Pad (never resize/stretch) every glyph into ONE consistent canvas
     size, derived from the ACTUAL max width/height across the extracted
     glyphs -- not a remembered/guessed constant. Padding uses the atlas's
     own background gray level (the same mode-based estimate
     build_glyph_reference.py uses) so the pad fill doesn't itself become
     a false edge the Sobel kernel would react to.
  3. Compute each padded glyph's 2D FFT.
  4. "Convolve" against a 45deg Sobel kernel via frequency-domain
     multiplication (not cv2.filter2D) -- i.e. actually using the FFT from
     step 3, per the request. Repeated application n times is just raising
     the kernel's frequency response to the n-th power before one inverse
     FFT (mathematically identical to re-convolving the spatial result
     n times for a fixed linear filter), computed for n=1,2,3.
  5. Render one heatmap per (glyph, n) cell, JET-colormapped and alpha-
     blended over the padded glyph, sharing ONE magnitude scale across the
     WHOLE table (every glyph, every n) -- per-cell independent scaling
     was tried and rejected earlier in this project's own Gabor debug
     table (docs/known_issues.txt §15's DEBUG TABLE entry) for exactly
     the reason it would hide here: it erases the cross-glyph magnitude
     difference the table exists to show.

CIRCULAR-CONVOLUTION CARE: frequency-domain multiplication is CIRCULAR
convolution, which can wrap a kernel's response around the image border --
docs/known_issues.txt §15 already flagged this as a real corruption risk
for small glyphs ("circular wraparound corrupts exactly the boundary
information ... depends on"). Mitigated here by adding a small background-
colored margin (enough for 3 passes of a 3x3 kernel) around the padded
glyph before the FFT, then cropping the margin back off for display --
the wraparound lands in the throwaway margin, not the glyph content.

This is a standalone unit-level visual/quantitative probe, not a
classifier change -- nothing here is wired into gfl2/stat_ocr_fft.py.

Usage:
    python debugs/debug_sobel45_pct_glyphs.py
    python debugs/debug_sobel45_pct_glyphs.py --atlas assets/fonts/glyph_daily_pct.png
"""
from __future__ import annotations
import argparse
import importlib.util
import sys
from pathlib import Path

import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

_DEFAULT_ATLAS  = _ROOT / "assets" / "fonts" / "glyph_daily_pct.png"
_DEFAULT_LOOKUP = _ROOT / "assets" / "fonts" / "glyph_lookup.py"
_DEFAULT_OUTPUT = _ROOT / "tests" / "outputs" / "daily" / "sobel45_pct_glyph_table.png"

N_STAGES = 3       # 1x, 2x, 3x convolution
UPSCALE  = 10       # display upscale for the tiny native/padded glyph crops
ALPHA    = 0.55     # heatmap overlay opacity
CELL_W, CELL_H = 130, 170
LABEL_W  = 90
HEADER_H = 40
CAPTION_H = 20

# 45deg (NE-SW gradient) Sobel-style diagonal kernel.
SOBEL_45 = np.array([
    [0,  1,  2],
    [-1, 0,  1],
    [-2, -1, 0],
], dtype=np.float64)


def _load_lookup(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location("glyph_lookup", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.DATA


def _bg_mode_gray(gray: np.ndarray) -> int:
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    return int(np.argmax(hist))


def load_atlas_glyphs(atlas_path: Path, lookup: dict) -> tuple[list[dict], int]:
    """Re-isolate every glyph from the atlas via threshold + findContours,
    sorted left-to-right, labelled via `lookup` (index -> char) -- exactly
    the re-derivation contract the atlas was built to support. Returns
    (glyphs, bg_gray) where each glyph carries its NATIVE (unresized)
    crop and true (w, h)."""
    atlas = cv2.imread(str(atlas_path))
    if atlas is None:
        sys.exit(f"Could not read atlas: {atlas_path}")
    gray = cv2.cvtColor(atlas, cv2.COLOR_BGR2GRAY)
    bg_gray = _bg_mode_gray(gray)

    diff = cv2.absdiff(gray, np.full_like(gray, bg_gray))
    _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = sorted((cv2.boundingRect(c) for c in cnts), key=lambda b: b[0])

    if len(boxes) != len(lookup):
        sys.exit(f"Found {len(boxes)} contours in {atlas_path.name} but "
                  f"glyph_lookup.py lists {len(lookup)} entries for it -- "
                  f"atlas and lookup are out of sync, regenerate both via "
                  f"debugs/build_glyph_reference.py before re-running this.")

    glyphs = []
    for i, (x, y, w, h) in enumerate(boxes):
        char = lookup[str(i)]
        glyphs.append({
            "char": char,
            "native": gray[y:y + h, x:x + w].copy(),
            "w": w, "h": h,
        })
    return glyphs, bg_gray


def pad_to(crop: np.ndarray, target_w: int, target_h: int, bg_val: int) -> np.ndarray:
    """Center `crop` in a (target_h, target_w) canvas filled with bg_val --
    NEVER resizes/stretches the glyph itself, only adds background."""
    h, w = crop.shape
    canvas = np.full((target_h, target_w), bg_val, dtype=np.uint8)
    y0, x0 = (target_h - h) // 2, (target_w - w) // 2
    canvas[y0:y0 + h, x0:x0 + w] = crop
    return canvas


def _freq_response(kernel: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """FFT of `kernel`, zero-padded to `shape` and centered via np.roll so
    the resulting frequency-domain multiplication corresponds to a
    kernel-centered ("same"-style) convolution rather than a top-left-
    anchored one."""
    kh, kw = kernel.shape
    padded = np.zeros(shape, dtype=np.float64)
    padded[:kh, :kw] = kernel
    padded = np.roll(padded, (-(kh // 2), -(kw // 2)), axis=(0, 1))
    return np.fft.fft2(padded)


def sobel45_fft_stages(padded_glyph: np.ndarray, margin: int, n_stages: int = N_STAGES) -> list[np.ndarray]:
    """Pad `padded_glyph` with `margin` extra pixels of its own background
    (already baked in by the caller) so 3x3-kernel circular wraparound
    (frequency-domain multiplication is CIRCULAR convolution) lands in the
    margin, not the glyph content -- then for n=1..n_stages, return the
    magnitude of ifft2(glyph_fft * kernel_fft**n), i.e. the result of
    convolving with the SAME 45deg Sobel kernel n times, cropped back to
    the margin-free region for display."""
    h, w = padded_glyph.shape
    G = np.fft.fft2(padded_glyph.astype(np.float64))
    K = _freq_response(SOBEL_45, (h, w))

    stages = []
    Kpow = np.ones_like(K)
    for _ in range(n_stages):
        Kpow = Kpow * K
        resp = np.fft.ifft2(G * Kpow)
        mag = np.abs(resp)[margin:h - margin, margin:w - margin]
        stages.append(mag)
    return stages


def _to_bgr(img: np.ndarray) -> np.ndarray:
    return img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def _fit_and_paste(canvas, img_bgr, x0, y0, w, h) -> None:
    ih, iw = img_bgr.shape[:2]
    scale = min(w / iw, h / ih)
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    resized = cv2.resize(img_bgr, (nw, nh), interpolation=cv2.INTER_NEAREST)
    ox, oy = x0 + (w - nw) // 2, y0 + (h - nh) // 2
    canvas[oy:oy + nh, ox:ox + nw] = resized


def _heatmap_overlay(base_gray: np.ndarray, response: np.ndarray, global_max: float) -> np.ndarray:
    scale = global_max if global_max > 1e-9 else 1.0
    mag_u8 = np.clip(response / scale * 255, 0, 255).astype(np.uint8)
    heat = cv2.applyColorMap(mag_u8, cv2.COLORMAP_JET)
    base = _to_bgr(base_gray)
    return cv2.addWeighted(heat, ALPHA, base, 1 - ALPHA, 0)


def _put_caption(canvas, text, x0, y0, w) -> None:
    cv2.putText(canvas, text, (x0 + 4, y0 - 4), cv2.FONT_HERSHEY_SIMPLEX,
                0.36, (30, 30, 30), 1, cv2.LINE_AA)


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

    # "consistent dimension ... from the actual dimension" -- derived from
    # the real extracted crops, not a remembered constant.
    target_w = max(g["w"] for g in glyphs)
    target_h = max(g["h"] for g in glyphs)
    print(f"{len(glyphs)} glyphs isolated from {atlas_path.name}; "
          f"consistent canvas = {target_w}x{target_h} (max native w/h), "
          f"bg_gray={bg_gray}")

    margin = 2 * N_STAGES + 2  # 3x3 kernel: (k-1)//2=1 px bleed/pass, generous margin
    for g in glyphs:
        padded = pad_to(g["native"], target_w, target_h, bg_gray)
        g["padded"] = padded
        canvas_for_fft = np.full((target_h + 2 * margin, target_w + 2 * margin),
                                  bg_gray, dtype=np.uint8)
        canvas_for_fft[margin:margin + target_h, margin:margin + target_w] = padded
        g["stages"] = sobel45_fft_stages(canvas_for_fft, margin)

    # ── Scale shared across every glyph WITHIN a stage, not across stages ──
    # Each convolution pass multiplies the frequency response again, so raw
    # magnitude naturally grows an order of magnitude per stage -- sharing
    # ONE scale across all 3 stages (tried first) crushed x1/x2 to near-
    # invisible dark blue under x3's much larger range. Per-stage scale is
    # still shared across every DIGIT within that stage (same discipline
    # as docs/known_issues.txt §15's DEBUG TABLE entry), which is what
    # actually matters for "does '4'/'7' stand out at this iteration depth".
    stage_max = [max(float(g["stages"][n].max()) for g in glyphs) for n in range(N_STAGES)]

    # ── Quantify: does '4'/'7' actually separate from the rest? ────────────
    print(f"\nPer-glyph mean response magnitude (per-stage scale max={['%.2f' % m for m in stage_max]}):")
    print(f"{'char':>5}  " + "  ".join(f"n={n+1}" for n in range(N_STAGES)))
    ranked = []
    for g in glyphs:
        means = [float(s.mean()) for s in g["stages"]]
        ranked.append((g["char"], means))
        print(f"{g['char']!r:>5}  " + "  ".join(f"{m:6.3f}" for m in means))
    ranked.sort(key=lambda t: t[1][-1], reverse=True)
    print(f"\nRanked by n={N_STAGES} mean response (highest first): "
          + ", ".join(f"'{c}'({m[-1]:.3f})" for c, m in ranked))

    # ── Table image ──────────────────────────────────────────────────────
    columns = ["native", f"padded {target_w}x{target_h}"] + [f"sobel45 x{n+1}" for n in range(N_STAGES)]
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
                         f"from actual glyph extents)",
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
