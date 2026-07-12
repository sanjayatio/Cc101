# -*- coding: utf-8 -*-
"""
debugs/debug_hbar_feature.py -- prototype + tabular debug image for a
2D-sliding, single-sided matched-filter HORIZONTAL-bar feature. Same
mechanism as debugs/debug_vstroke_feature.py (currently on hold), transposed:
the split axis is now height (ink band vs background band, both spanning
the full kernel width) instead of width.

TARGET DIGITS: '2', '4', '5', '7' -- each has a real horizontal stroke
('2' foot, '4' crossbar, '5' and '7' top bar) the other six digits lack.
This feature should score these four high and the rest low.

DIRECTIONAL CHOICE -- TWO SEPARATE FEATURES, NOT ONE MERGED ONE: the
vertical prototype's left-vs-right ambiguity carries over here as
top-vs-bottom -- ink expected in the window's TOP rows (background below)
vs BOTTOM rows (background above). A single orientation was tried first
and rejected empirically ('7' scored 0.097, dead last, because ink-BOTTOM
structurally cannot reach '7's top bar -- see git history / conversation
log for that run). '2' (bottom bar) and '5'/'7' (top bar) are a genuine
mirror pair along this axis, the same way '4' exposed the vertical
kernel's reachability limit -- no single orientation can serve both.

The fix is NOT to combine both orientations into one max-of-two score --
that was tried on the vertical prototype and explicitly rejected by
direction: a real feature can't pick per-glyph which orientation "wins" at
inference time, so a max isn't a computation, it's hindsight. The fix
already exists elsewhere in this codebase: gfl2.stat_ocr_v0_2_0's paren_(/
paren_) and loop_top/loop_bot are each two INDEPENDENT feature dimensions,
never pre-merged -- the classifier (nearest-centroid over the full vector)
does the combining, not the feature extractor. This script reports
hbar_top and hbar_bottom as two separate columns/dimensions, exactly that
pattern, and checks whether between the two (not "the better of the two
picked per glyph", but "does each target show up somewhere") the four
targets are distinguishable from the six non-targets.

Reachability math (same formula family as the vertical prototype): with
H=20, kernel_h=6, ink_h=2, ink-TOP's ink rows can reach rows 0-15; ink-
BOTTOM's ink rows can reach rows 4-19.

Usage:
    python debugs/debug_hbar_feature.py
    python debugs/debug_hbar_feature.py --images single/fb_d_060518.png
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

DEFAULT_IMAGE = "single/fb_d_060518.png"

DIGITS  = "0123456789"
TARGETS = ("2", "4", "5", "7")
ALPHA   = 0.55

CELL_W, CELL_H = 150, 190
LABEL_W  = 90
HEADER_H = 46
CAPTION_H = 22

# ── Kernel geometry (split axis = height; span axis = width) ────────────────
HBAR_KERNEL_H = 6      # split axis window size -- mirrors vstroke's KERNEL_W
HBAR_KERNEL_W = 10     # span axis window size -- mirrors vstroke's KERNEL_H
HBAR_INK_FRAC = 0.4    # fraction of kernel_h that is "ink"
HBAR_SIDES    = ("top", "bottom")   # TWO separate features, not merged -- see module docstring


def _hbar_kernel(kernel_h: int, kernel_w: int, side: str, punish: bool = False) -> np.ndarray:
    """weight: +1 = ink expected, 0 = background expected. If punish, one
    extra cell -- the background-side row immediately ADJACENT to the ink
    band, RIGHTMOST column only -- gets -1 instead of 0: a stronger,
    signed penalty rather than a neutral "expect background" reading.
    Motivation (per direction, from inspecting '5's overlay): a genuine
    isolated bar has clean background right above/below it; a curve
    merely PASSING THROUGH a locally-flat segment (the false-positive mode
    measured on '3'/'5'/'6'/'8'/'9') usually has its connecting stroke
    bleed into exactly that adjacent row at one edge -- so punishing ink
    there specifically (not just failing to reward it) should suppress
    curve false-positives without touching a genuine bar, which has
    nothing to punish there in the first place.

    RIGHT, not left: placed left-most first, then reconsidered by
    direction -- '2' and '4' (both targets) also have real ink near that
    adjacent-row-left-column position (e.g. '4's diagonal, '2's upper
    curve closing in from the left), so a left-side punish cell risked
    punishing the very targets this feature exists to detect. The right
    side avoids that overlap for these two digits' actual strokes."""
    ink_h = max(1, int(round(HBAR_INK_FRAC * kernel_h)))
    weight = np.zeros((kernel_h, kernel_w), dtype=np.float64)
    if side == "top":
        weight[:ink_h, :] = 1.0
        punish_row = ink_h              # first background row, just below the ink band
    elif side == "bottom":
        weight[kernel_h - ink_h:, :] = 1.0
        punish_row = kernel_h - ink_h - 1   # last background row, just above the ink band
    else:
        raise ValueError(f"side must be 'top' or 'bottom', got {side!r}")
    if punish and 0 <= punish_row < kernel_h:
        weight[punish_row, kernel_w - 1] = -1.0
    return weight


def _norm_xcorr(a: np.ndarray, b: np.ndarray) -> float:
    af = a.astype(np.float64).ravel() - a.mean()
    bf = b.astype(np.float64).ravel() - b.mean()
    denom = (np.linalg.norm(af) * np.linalg.norm(bf)) + 1e-9
    return float(np.dot(af, bf) / denom)


def _hbar_feature_sliding2d(
    gray_norm: np.ndarray, weight: np.ndarray,
) -> tuple[float, tuple[int, int], np.ndarray]:
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


# ── Glyph extraction (duplicated, same as debug_vstroke_feature.py) ─────────

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


# ── Rendering helpers (same pattern as debug_vstroke_feature.py) ────────────

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
    """green=ink expected (+1), near-white=background expected (0),
    red=punished cell (-1, stronger-than-background penalty)."""
    img = np.full((*weight.shape, 3), 245, dtype=np.uint8)
    img[weight > 0] = (60, 190, 60)
    img[weight < 0] = (40, 40, 220)
    return img


def _hbar_overlay(norm_glyph, weight, best_xy, corr, corr_min, corr_max) -> np.ndarray:
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


def _response_heatmap(grid, w, h, global_min, global_max, best_xy_idx) -> np.ndarray:
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


def _blank_cell(w, h, text="N/A") -> np.ndarray:
    img = np.full((h, w, 3), 235, dtype=np.uint8)
    cv2.putText(img, text, (max(2, w // 2 - 22), h // 2), cv2.FONT_HERSHEY_SIMPLEX,
                0.4, (140, 140, 140), 1, cv2.LINE_AA)
    return img


def _put_caption(canvas, text, x0, y0, w) -> None:
    if not text:
        return
    cv2.putText(canvas, text, (x0 + 4, y0 - 4), cv2.FONT_HERSHEY_SIMPLEX,
                0.38, (30, 30, 30), 1, cv2.LINE_AA)


# ── Main table builder ────────────────────────────────────────────────────────

def build_table(glyphs_by_digit: dict, punish: bool = True) -> tuple[np.ndarray, dict]:
    weights = {side: _hbar_kernel(HBAR_KERNEL_H, HBAR_KERNEL_W, side, punish=punish) for side in HBAR_SIDES}
    legends = {side: _kernel_legend_image(weights[side]) for side in HBAR_SIDES}

    result_by_digit = {}
    for d, g in glyphs_by_digit.items():
        per_side = {}
        for side in HBAR_SIDES:
            best, xy, grid = _hbar_feature_sliding2d(g["normalized"], weights[side])
            per_side[side] = {"best": best, "xy": xy, "grid": grid}
        result_by_digit[d] = per_side

    all_best = [r[s]["best"] for r in result_by_digit.values() for s in HBAR_SIDES]
    corr_min, corr_max = (min(all_best), max(all_best)) if all_best else (0.0, 1.0)
    all_grid_vals = [v for r in result_by_digit.values() for s in HBAR_SIDES for v in r[s]["grid"].ravel()]
    resp_min, resp_max = (min(all_grid_vals), max(all_grid_vals)) if all_grid_vals else (0.0, 1.0)

    columns = ["original_crop", "normalized_12x20", "kernels (T/B)"]
    for side in HBAR_SIDES:
        columns += [f"overlay ({side})", f"heatmap ({side})"]
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
    cv2.putText(canvas, f"(score scale [{corr_min:.3f},{corr_max:.3f}]; "
                         f"kernel {HBAR_KERNEL_H}x{HBAR_KERNEL_W}, ink_frac={HBAR_INK_FRAC}; "
                         f"top+bottom are TWO SEPARATE features, not merged; targets={TARGETS})",
                (LABEL_W + 4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (90, 90, 90), 1, cv2.LINE_AA)

    legend_pair = np.concatenate(
        [legends["top"], np.full((legends["top"].shape[0], 4, 3), 255, dtype=np.uint8), legends["bottom"]],
        axis=1,
    )

    for i, d in enumerate(DIGITS):
        y0 = HEADER_H + i * CELL_H
        cv2.line(canvas, (0, y0), (W, y0), (210, 210, 210), 1)
        g = glyphs_by_digit.get(d)
        tag = " *TARGET*" if d in TARGETS else ""
        cv2.putText(canvas, f"digit '{d}'{tag}", (6, y0 + 24), cv2.FONT_HERSHEY_SIMPLEX,
                    0.48, (0, 0, 0) if not tag else (0, 100, 0), 1, cv2.LINE_AA)
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
        cell_imgs = [_to_bgr(g["raw"]), _to_bgr(norm), legend_pair]
        captions = ["", f"{norm.shape[1]}x{norm.shape[0]}", "T=top-ink B=bottom-ink"]
        for side in HBAR_SIDES:
            rs = r[side]
            cell_imgs.append(_hbar_overlay(norm, weights[side], rs["xy"], rs["best"], corr_min, corr_max))
            captions.append(f"{side}={rs['best']:.3f} @{rs['xy']}")
            cell_imgs.append(_response_heatmap(rs["grid"], CELL_W - 8, CELL_H - CAPTION_H - 8,
                                                resp_min, resp_max, rs["xy"]))
            captions.append("surface")

        for j, (img, cap) in enumerate(zip(cell_imgs, captions)):
            x0 = LABEL_W + j * CELL_W
            _fit_and_paste(canvas, img, x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)
            _put_caption(canvas, cap, x0, y0 + CELL_H, CELL_W)

    return canvas, result_by_digit


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", nargs="+", default=[DEFAULT_IMAGE])
    ap.add_argument("--output", default="tests/outputs/daily/hbar_feature_table.png")
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
        print(f"WARNING: {args.images} do not cover digit(s) {missing_digits}")

    table, result_by_digit = build_table(glyphs_by_digit, punish=True)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), table)
    print(f"Wrote {table.shape[1]}x{table.shape[0]} debug table -> {out_path}  (punish=True, rendered version)")

    _, plain_by_digit = build_table(glyphs_by_digit, punish=False)

    print(f"\nhbar scores per digit, PLAIN vs PUNISH (kernel {HBAR_KERNEL_H}x{HBAR_KERNEL_W}):")
    print(f"{'digit':>6} {'top(plain)':>11} {'top(punish)':>12} {'bot(plain)':>11} {'bot(punish)':>12}")
    for d in DIGITS:
        if d not in result_by_digit:
            print(f"  '{d}': (missing)")
            continue
        r, p = result_by_digit[d], plain_by_digit[d]
        tag = " *TARGET*" if d in TARGETS else ""
        print(f"{d:>6} {p['top']['best']:11.3f} {r['top']['best']:12.3f} "
              f"{p['bottom']['best']:11.3f} {r['bottom']['best']:12.3f}{tag}")

    # Per-dimension check -- each dim evaluated on its own, NOT merged into a
    # per-glyph max (that combination was rejected by direction; see docstring).
    for side in HBAR_SIDES:
        target_scores = [result_by_digit[d][side]["best"] for d in TARGETS if d in result_by_digit]
        other_scores = [result_by_digit[d][side]["best"] for d in DIGITS if d not in TARGETS and d in result_by_digit]
        if not (target_scores and other_scores):
            continue
        worst_target, best_other = min(target_scores), max(other_scores)
        print(f"\n[{side}] worst target: {worst_target:+.3f}   best non-target: {best_other:+.3f}")
        if worst_target > best_other:
            print(f"[{side}] -> clean separation on this dimension alone")
        else:
            failing = [d for d in TARGETS if d in result_by_digit
                       and result_by_digit[d][side]["best"] <= best_other]
            print(f"[{side}] -> NOT clean alone: target(s) {failing} do not beat the best non-target")

    # Does each target show up on AT LEAST ONE of the two dims, well clear of
    # every non-target's score on THAT SAME dim (the classifier sees both
    # dims together, so a target only needs to stand out on one of them)?
    print("\nper-target: does it clear all six non-targets on at least one dimension?")
    for d in TARGETS:
        if d not in result_by_digit:
            continue
        clears = []
        for side in HBAR_SIDES:
            others = [result_by_digit[o][side]["best"] for o in DIGITS if o not in TARGETS and o in result_by_digit]
            if others and result_by_digit[d][side]["best"] > max(others):
                clears.append(side)
        verdict = f"yes, via {clears}" if clears else "no -- fails on both dims"
        print(f"  '{d}': {verdict}")


if __name__ == "__main__":
    main()
