# -*- coding: utf-8 -*-
"""
debugs/debug_vstroke_feature.py -- prototype + tabular debug image for a
2D-SLIDING, single-sided matched-filter vertical-stroke feature, proposed as
a reinforcement of gfl2.stat_ocr_v0_2_0's existing vrun feature (see
docs/known_issues.txt §15's GABOR_0 REMOVED, VRUN + LOOP_TOP/LOOP_BOT ADDED
entry) and a possible root cause fix for §17's open '1'/'7' confusion.

STATUS: ON HOLD, PROTOTYPE, NOT WIRED INTO gfl2/stat_ocr_v0_2_0.py.  Per this
repo's established methodology (docs/known_issues.txt §15's GABOR
CALIBRATION entry: "no feature-space proxy shortcut for a multi-agent
decision system"), a convincing-looking standalone number here is NOT
sufficient to promote this into compute_features() -- that needs the same
real --build/--verify pipeline validation every other feature in that file
went through. This script is the UNIT-level visual check that should
happen first (docs/known_issues.txt §15's DEBUG TABLE entry; feedback
memory "unit debug before integration").

DESIGN HISTORY (kept here so the reasoning isn't lost):

  1. FIXED, CENTERED, BOTH-FLANKS kernel (background required on both sides
     of a centered ink column, spanning the full glyph height). Rejected:
     '1' only narrowly beat '7' (+0.083 gap), and a fixed ink-column WIDTH
     silently assumes a stroke thickness.

  2. SLIDING (x only), SINGLE-SIDED, full-height, with a bottom "don't
     care" band on the background side. '1'/'7' gap widened a lot
     (+0.334), but exposed two problems: (a) a single-sided, full-height
     kernel's ink region can only reach a limited band of columns, and
     '4's vertical stroke landed outside that band; (b) flipping
     orientation to reach it made '4' WORSE, because '4's crossbar sits at
     MID-HEIGHT, not near the bottom where the "don't care" band lived --
     the crossbar cuts through the "must be background" zone at
     mid-height regardless of which side the ink column is on.

  3. 2D SLIDING (x AND y), no "don't care" band: a short kernel that also
     slides vertically can dodge structure like '4's crossbar by
     positioning itself below it, instead of needing a pre-placed mask to
     ignore it. This is the version below.

  ORIENTATION (single, not dual): a single-sided kernel's reachable ink
  band depends on which side (left/right) carries the ink -- a real,
  non-obvious tradeoff, not a preference. Comparing both orientations and
  taking a per-glyph max was tried during investigation and explicitly
  REJECTED by direction: a real feature can't pick per-glyph which
  orientation "wins" at inference time, so that comparison doesn't
  represent anything the shipped classifier could actually do. This script
  commits to ONE orientation (VSTROKE_SIDE below) and reports only that.

Kernel (kernel_h x kernel_w, both << glyph size): single-sided, ink on one
side (all rows of the window), background on the other -- no mask.

Search space: with kernel_h=10, kernel_w=6 against a 20x12 glyph, that's
11 y-offsets x 7 x-offsets = 77 positions -- trivial for a plain spatial
double loop (no FFT needed).

KNOWN LIMITATION, still not addressed: single-sided still cannot
distinguish an isolated stroke's edge from a wider blob's edge (e.g. '0's
loop) -- see known_issues.txt §15's vrun history for why that mattered
there. 2D sliding also reopened a second false-positive mode: a short
window free to move in both axes can find a locally-straight-looking patch
inside a curved digit's stroke (measured on '3'/'7'/'9').

NOT DONE HERE: the analogous horizontal-bar feature now lives in
debugs/debug_hbar_feature.py (targets '2','4','5','7').

Usage:
    python debugs/debug_vstroke_feature.py
    python debugs/debug_vstroke_feature.py --images single/fb_d_060518.png
    python debugs/debug_vstroke_feature.py --images single/a.png single/b.png --output out.png
"""
from __future__ import annotations
import sys
import argparse
from pathlib import Path
import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr_v0_1_0 import (
    PCT_STRIP_Y, DOT_MAX_DIM, NORM_W_PCT, NORM_H_PCT,
    _binarize, _find_blobs, _filter_y_outliers, _find_percent_x_start,
    _collect_cells, _load_tess_gt_cache,
)
from gfl2.stat_ocr_v0_1_1 import _normalize_glyph

DEFAULT_IMAGE = "single/fb_d_060518.png"   # same corpus-covers-all-10-digits pick as debug_gabor_features.py

DIGITS  = "0123456789"
ALPHA   = 0.55

CELL_W, CELL_H = 150, 190
LABEL_W  = 90
HEADER_H = 46
CAPTION_H = 22

# ── Kernel geometry (single committed direction -- see module docstring) ────
VSTROKE_KERNEL_W = 6     # window width, in glyph-pixel units. Starting point
                          # borrowed from vrun's MAX_STROKE_W (corpus-measured
                          # stroke width, known_issues.txt §15) -- unvalidated
                          # for this kernel, open to tuning.
VSTROKE_KERNEL_H = 10    # window height -- half NORM_H_PCT, a first guess
                          # (no corpus measurement behind this yet): short
                          # enough to dodge a mid-height crossbar by sliding
                          # past it in y, per the DESIGN HISTORY note above.
VSTROKE_INK_FRAC = 0.4   # fraction of kernel_w that is "ink" (the rest is background)
VSTROKE_SIDE     = "right"   # single committed direction -- see module docstring


VSTROKE_PUNISH = True   # see _vstroke_kernel docstring -- targets '7's diagonal drift


def _vstroke_kernel(kernel_h: int, kernel_w: int, side: str = VSTROKE_SIDE,
                     punish: bool = VSTROKE_PUNISH) -> np.ndarray:
    """Ink/background weight template, shape (kernel_h, kernel_w): +1 =
    ink expected, 0 = background expected. If punish, one extra cell --
    the background column immediately ADJACENT to the ink band, BOTTOM row
    only -- gets -1 instead of 0 (same "punish" mechanism as
    debugs/debug_hbar_feature.py's hbar kernel, transposed).

    WHY THIS TARGETS '7': '7's diagonal descender drifts left as y
    increases (it is diagonal, not vertical); a short vertical window
    positioned somewhere along it can still score well as "isolated
    vertical stroke" because the drift is small over kernel_h=10 rows.
    But by the BOTTOM row of such a window, the diagonal has drifted
    furthest left -- into the background column right next to the ink
    band -- which a genuine vertical stroke ('1', or '4's vertical, both
    the same columns for the full window height by construction) never
    does. Punishing ink there specifically should suppress '7' without
    touching '1'/'4'.

    Bottom row, not top: drift accumulates going DOWN '7's descender, so
    it is largest at the window's bottom edge, not its top."""
    ink_w = max(1, int(round(VSTROKE_INK_FRAC * kernel_w)))
    weight = np.zeros((kernel_h, kernel_w), dtype=np.float64)
    if side == "left":
        weight[:, :ink_w] = 1.0
        punish_col = ink_w                  # first background column, just right of the ink band
    elif side == "right":
        weight[:, kernel_w - ink_w:] = 1.0
        punish_col = kernel_w - ink_w - 1   # last background column, just left of the ink band
    else:
        raise ValueError(f"side must be 'left' or 'right', got {side!r}")
    if punish and 0 <= punish_col < kernel_w:
        weight[kernel_h - 1, punish_col] = -1.0
    return weight


def _norm_xcorr(a: np.ndarray, b: np.ndarray) -> float:
    """Whole-window normalized cross-correlation (cosine similarity of
    mean-subtracted, flattened patches) -- unmasked, since this kernel no
    longer uses a "don't care" region (see DESIGN HISTORY)."""
    af = a.astype(np.float64).ravel() - a.mean()
    bf = b.astype(np.float64).ravel() - b.mean()
    denom = (np.linalg.norm(af) * np.linalg.norm(bf)) + 1e-9
    return float(np.dot(af, bf) / denom)


def _vstroke_feature_sliding2d(
    gray_norm: np.ndarray, weight: np.ndarray,
) -> tuple[float, tuple[int, int], np.ndarray]:
    """Slide `weight` across every (x, y) offset in gray_norm; return
    (best_score, (best_x, best_y), scores_grid) where scores_grid has
    shape (n_y_offsets, n_x_offsets)."""
    h, w = gray_norm.shape
    kh, kw = weight.shape
    n_y = max(1, h - kh + 1)
    n_x = max(1, w - kw + 1)
    grid = np.zeros((n_y, n_x), dtype=np.float64)
    for y0 in range(n_y):
        for x0 in range(n_x):
            sub = gray_norm[y0: y0 + kh, x0: x0 + kw]
            grid[y0, x0] = _norm_xcorr(sub, weight)
    by, bx = np.unravel_index(int(np.argmax(grid)), grid.shape)
    return float(grid[by, bx]), (int(bx), int(by)), grid


# ── Glyph extraction (duplicated from debugs/debug_gabor_features.py rather ──
#    than cross-imported -- see that script's own module docstring for why
#    debug scripts in this repo duplicate rather than couple to each other)

def _extract_glyphs_verbose(cell: np.ndarray, pct_label: str):
    if not pct_label:
        return None
    expected = [c for c in pct_label if c.isdigit()]
    if not expected:
        return None

    ch = cell.shape[0]
    pct_strip = cell[: int(ch * PCT_STRIP_Y[1]), :]
    gray = cv2.cvtColor(pct_strip, cv2.COLOR_BGR2GRAY) if pct_strip.ndim == 3 else pct_strip
    thresh = _binarize(pct_strip)
    blobs = _filter_y_outliers(_find_blobs(thresh), threshold=12)
    if not blobs:
        return None

    sorted_x = sorted(blobs, key=lambda b: b[0])
    pct_x = _find_percent_x_start(sorted_x)
    digit_blobs = [
        (x, y, w, h) for (x, y, w, h) in sorted_x
        if (pct_x is None or x < pct_x)
        and not (w <= DOT_MAX_DIM and h <= DOT_MAX_DIM)
    ]
    if len(digit_blobs) != len(expected):
        return None

    out = []
    for (x, y, w, h), label in zip(digit_blobs, expected):
        bin_crop = thresh[y: y + h, x: x + w]
        if bin_crop.size == 0:
            return None
        raw_crop = gray[y: y + h, x: x + w]
        norm = _normalize_glyph(bin_crop, NORM_W_PCT, NORM_H_PCT)
        out.append({"label": label, "raw": raw_crop, "binarized": bin_crop, "normalized": norm})
    return out


def collect_one_glyph_per_digit(image_paths: list[Path], gt_cache=None) -> dict:
    if gt_cache is None:
        gt_cache = _load_tess_gt_cache() or {}
    cells = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    found: dict = {}
    for item in cells:
        if len(found) == 10:
            break
        glyphs = _extract_glyphs_verbose(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for g in glyphs:
            if g["label"] not in found:
                found[g["label"]] = {**g, "source": item["source"]}
    return found


# ── Rendering helpers ─────────────────────────────────────────────────────────

def _to_bgr(img: np.ndarray) -> np.ndarray:
    return img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def _fit_and_paste(canvas: np.ndarray, img_bgr: np.ndarray, x0: int, y0: int, w: int, h: int) -> None:
    ih, iw = img_bgr.shape[:2]
    scale = min(w / iw, h / ih)
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    resized = cv2.resize(img_bgr, (nw, nh), interpolation=cv2.INTER_NEAREST)
    ox, oy = x0 + (w - nw) // 2, y0 + (h - nh) // 2
    canvas[oy: oy + nh, ox: ox + nw] = resized


def _kernel_legend_image(weight: np.ndarray) -> np.ndarray:
    """The raw kernel itself (kernel_h x kernel_w): green=ink expected,
    near-white=background expected."""
    img = np.full((*weight.shape, 3), 245, dtype=np.uint8)
    img[weight > 0] = (60, 190, 60)
    img[weight < 0] = (40, 40, 220)
    return img


def _vstroke_overlay(
    norm_glyph: np.ndarray, weight: np.ndarray, best_xy: tuple[int, int],
    corr: float, corr_min: float, corr_max: float,
) -> np.ndarray:
    """normalized glyph with the kernel drawn at its BEST-FIT (x, y): ink
    region tinted green, opacity SCALED by corr relative to the table-wide
    [corr_min, corr_max]. Pixels outside the winning window are untouched."""
    kh, kw = weight.shape
    bx, by = best_xy
    base = _to_bgr(norm_glyph).astype(np.float64)
    out = base.copy()

    rng = max(corr_max - corr_min, 1e-9)
    strength = float(np.clip((corr - corr_min) / rng, 0.0, 1.0))
    alpha = ALPHA * strength
    green = np.array((0, 200, 0), dtype=np.float64)
    red = np.array((40, 40, 220), dtype=np.float64)

    window = out[by: by + kh, bx: bx + kw]
    sub_base = base[by: by + kh, bx: bx + kw]
    ink = weight > 0
    window[ink] = sub_base[ink] * (1 - alpha) + green * alpha
    punished = weight < 0
    if punished.any():
        window[punished] = sub_base[punished] * (1 - ALPHA) + red * ALPHA
    out[by: by + kh, bx: bx + kw] = window
    cv2.rectangle(out, (bx, by), (bx + kw - 1, by + kh - 1), (0, 0, 220), 1)

    return out.astype(np.uint8)


def _response_heatmap(grid: np.ndarray, w: int, h: int, global_min: float, global_max: float,
                       best_xy_idx: tuple[int, int]) -> np.ndarray:
    """Color-mapped 2D response surface (one cell per (x,y) offset), shared
    scale across the whole table, with the winning offset marked."""
    rng = max(global_max - global_min, 1e-9)
    norm_u8 = np.clip((grid - global_min) / rng * 255, 0, 255).astype(np.uint8)
    heat = cv2.applyColorMap(norm_u8, cv2.COLORMAP_JET)
    scale = max(1, min(w // heat.shape[1], h // heat.shape[0]))
    big = cv2.resize(heat, (heat.shape[1] * scale, heat.shape[0] * scale), interpolation=cv2.INTER_NEAREST)
    canvas = np.full((h, w, 3), 250, dtype=np.uint8)
    oy, ox = (h - big.shape[0]) // 2, (w - big.shape[1]) // 2
    canvas[oy: oy + big.shape[0], ox: ox + big.shape[1]] = big
    bx_idx, by_idx = best_xy_idx
    cx, cy = ox + bx_idx * scale + scale // 2, oy + by_idx * scale + scale // 2
    cv2.drawMarker(canvas, (cx, cy), (255, 255, 255), cv2.MARKER_TILTED_CROSS, max(6, scale), 1, cv2.LINE_AA)
    return canvas


def _blank_cell(w: int, h: int, text: str = "N/A") -> np.ndarray:
    img = np.full((h, w, 3), 235, dtype=np.uint8)
    cv2.putText(img, text, (max(2, w // 2 - 22), h // 2), cv2.FONT_HERSHEY_SIMPLEX,
                0.4, (140, 140, 140), 1, cv2.LINE_AA)
    return img


def _put_caption(canvas: np.ndarray, text: str, x0: int, y0: int, w: int) -> None:
    if not text:
        return
    cv2.putText(canvas, text, (x0 + 4, y0 - 4), cv2.FONT_HERSHEY_SIMPLEX,
                0.38, (30, 30, 30), 1, cv2.LINE_AA)


# ── Main table builder ─────────────────────────────────────────────────────────

def build_table(glyphs_by_digit: dict, punish: bool = True) -> tuple[np.ndarray, dict]:
    weight = _vstroke_kernel(VSTROKE_KERNEL_H, VSTROKE_KERNEL_W, punish=punish)
    legend = _kernel_legend_image(weight)

    result_by_digit = {}
    for d, g in glyphs_by_digit.items():
        best, xy, grid = _vstroke_feature_sliding2d(g["normalized"], weight)
        result_by_digit[d] = {"best": best, "xy": xy, "grid": grid}

    all_best = [r["best"] for r in result_by_digit.values()]
    corr_min, corr_max = (min(all_best), max(all_best)) if all_best else (0.0, 1.0)
    all_grid_vals = [v for r in result_by_digit.values() for v in r["grid"].ravel()]
    resp_min, resp_max = (min(all_grid_vals), max(all_grid_vals)) if all_grid_vals else (0.0, 1.0)

    columns = ["original_crop", "normalized_12x20", "vstroke_kernel",
               f"best overlay (side={VSTROKE_SIDE})", "response heatmap"]
    n_cols = len(columns)
    n_rows = len(DIGITS)

    W = LABEL_W + n_cols * CELL_W
    H = HEADER_H + n_rows * CELL_H
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)

    for j, name in enumerate(columns):
        x0 = LABEL_W + j * CELL_W
        cv2.putText(canvas, name, (x0 + 4, HEADER_H - 16), cv2.FONT_HERSHEY_SIMPLEX,
                    0.42, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (x0, 0), (x0, H), (210, 210, 210), 1)
    cv2.line(canvas, (0, HEADER_H), (W, HEADER_H), (150, 150, 150), 1)
    cv2.putText(canvas, f"(best-score scale [{corr_min:.3f},{corr_max:.3f}]; "
                         f"heatmap scale [{resp_min:.3f},{resp_max:.3f}]; "
                         f"kernel {VSTROKE_KERNEL_H}x{VSTROKE_KERNEL_W}, ink_frac={VSTROKE_INK_FRAC}, "
                         f"side={VSTROKE_SIDE})",
                (LABEL_W + 4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (90, 90, 90), 1, cv2.LINE_AA)

    for i, d in enumerate(DIGITS):
        y0 = HEADER_H + i * CELL_H
        cv2.line(canvas, (0, y0), (W, y0), (210, 210, 210), 1)
        g = glyphs_by_digit.get(d)

        cv2.putText(canvas, f"digit '{d}'", (6, y0 + 24), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 0), 1, cv2.LINE_AA)
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
        r = result_by_digit[d]

        cell_imgs = [
            _to_bgr(g["raw"]),
            _to_bgr(norm),
            legend,
            _vstroke_overlay(norm, weight, r["xy"], r["best"], corr_min, corr_max),
            _response_heatmap(r["grid"], CELL_W - 8, CELL_H - CAPTION_H - 8, resp_min, resp_max, r["xy"]),
        ]
        captions = ["", f"{norm.shape[1]}x{norm.shape[0]}", f"ink={VSTROKE_SIDE}",
                    f"best={r['best']:.3f} @{r['xy']}", "surface"]

        for j, (img, cap) in enumerate(zip(cell_imgs, captions)):
            x0 = LABEL_W + j * CELL_W
            _fit_and_paste(canvas, img, x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)
            _put_caption(canvas, cap, x0, y0 + CELL_H, CELL_W)

    return canvas, result_by_digit


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", nargs="+", default=[DEFAULT_IMAGE],
                     help=f"1-2 source images whose pct-line digits together "
                          f"cover '0'-'9'  [default: {DEFAULT_IMAGE}]")
    ap.add_argument("--output", default="tests/outputs/daily/vstroke_feature_table.png",
                     help="Where to write the debug image  [default: "
                          "tests/outputs/daily/ -- already gitignored]")
    ap.add_argument("--no-gt-cache", action="store_true",
                     help="Force live Tesseract instead of "
                          "tests/inputs/daily/tess_gt_cache.py")
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
              f"those rows will be marked 'missing'. Add another --images entry to cover them.")

    table, result_by_digit = build_table(glyphs_by_digit, punish=True)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), table)
    print(f"Wrote {table.shape[1]}x{table.shape[0]} debug table -> {out_path}  (punish=True, rendered version)")

    _, plain_by_digit = build_table(glyphs_by_digit, punish=False)

    print(f"\nvstroke 2D-sliding best score per digit, PLAIN vs PUNISH "
          f"(kernel {VSTROKE_KERNEL_H}x{VSTROKE_KERNEL_W}, side={VSTROKE_SIDE}):")
    print(f"{'digit':>6} {'plain':>8} {'punish':>8}")
    for d in DIGITS:
        if d not in result_by_digit:
            print(f"  '{d}': (missing)")
            continue
        r, p = result_by_digit[d], plain_by_digit[d]
        print(f"{d:>6} {p['best']:8.3f} {r['best']:8.3f}")

    if "1" in result_by_digit and "7" in result_by_digit:
        gap = result_by_digit["1"]["best"] - result_by_digit["7"]["best"]
        plain_gap = plain_by_digit["1"]["best"] - plain_by_digit["7"]["best"]
        print(f"\n'1' vs '7' gap: {gap:+.3f}  (plain was {plain_gap:+.3f})")
    if "0" in result_by_digit and "8" in result_by_digit:
        gap = result_by_digit["0"]["best"] - result_by_digit["8"]["best"]
        print(f"'0' vs '8' gap: {gap:+.3f}")
    if "4" in result_by_digit:
        others = ["2", "3", "6", "7", "8", "9"]
        best4 = result_by_digit["4"]["best"]
        beats = [o for o in others if o in result_by_digit and best4 > result_by_digit[o]["best"]]
        loses = [o for o in others if o in result_by_digit and best4 <= result_by_digit[o]["best"]]
        print(f"\n'4' ({best4:.3f}) beats {beats or 'none'}, loses to {loses or 'none'} "
              f"(qualification bar: should beat all of {others})")


if __name__ == "__main__":
    main()
