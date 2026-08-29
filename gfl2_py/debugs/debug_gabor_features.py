# -*- coding: utf-8 -*-
"""
debugs/debug_gabor_features.py -- tabular per-digit debug image for
gfl2.stat_ocr_v0_2_0's spatial features (Gabor, paren), complementing the
real-pipeline accuracy validation calibrate_gabor.py already does.

WHY THIS EXISTS: docs/known_issues.txt §15's Gabor calibration work made
real-pipeline (integrated) accuracy the deciding factor after two proxy
metrics both looked good in isolation and regressed the real classifier
(docs/takeaways.txt #48) -- "penny-wise, pound-foolish" in the other
direction.  But an integrated accuracy number has its own blind spot: a
bug in one stage (binarization, cropping, template alignment) could be
silently canceled out by a bug in another, and the end-to-end number would
still look fine -- a "double negative."  Integrated tests can't see that;
only looking directly at what each stage actually produces can.  This
script is the deliberately narrow, visual, UNIT-level complement: one
image, all 10 digits, every intermediate representation and spatial
feature laid out side by side for direct human inspection.

Deliberately small in scope (1-2 source images, one glyph per digit) --
this is for eyeballing whether each stage looks sane, not for corpus-wide
statistics (that's what calibrate_gabor.py's real-pipeline sweeps are for).

COLUMNS:
  original_crop     raw grayscale digit crop straight from the source
                     image, before binarization (native resolution,
                     upscaled for visibility).
  binarized_crop     the SAME crop after gfl2.stat_ocr_v0_1_0._binarize() -- lets
                     a human directly compare against original_crop to
                     catch binarization bugs (bad threshold, off-by-one
                     crop bounds) that a downstream feature could
                     otherwise mask.
  normalized_12x20   the actual classifier input (_normalize_glyph output,
                     aspect-preserving padded) -- every column after this
                     one is computed FROM this image, not the raw crop.
  gabor_{angle}deg   semi-transparent heatmap of that orientation's Gabor
                     filter response magnitude, overlaid on
                     normalized_12x20, using the CURRENTLY SHIPPED kernels
                     (gfl2.stat_ocr_v0_2_0._GABOR_KERNELS, i.e. whatever
                     assets/fonts/gabor_calib.json currently holds).
  paren_( / paren_)  the '(' / ')' curve template overlaid on
                     normalized_12x20, opacity SCALED BY the correlation
                     score (weak/negative correlation -> nearly invisible;
                     the strongest correlation anywhere in the table ->
                     fully vivid) -- the numeric score is also captioned.
  hist, ring         bar charts of the actual per-bin feature values (64
                     bins / 8 bins) -- NOT a spatial overlay, since both
                     are computed from the 2D FFT magnitude spectrum
                     (frequency domain), which has no natural per-pixel
                     mapping back onto the spatial glyph image.  A bar
                     chart is the honest representation of what these
                     features actually are: a 1D distribution, not a
                     spatial map.

NORMALIZATION IS GLOBAL, NOT PER-CELL: every heatmap/overlay/bar chart in
this table shares ONE scale across all 10 digits (and, for Gabor, across
all orientations too).  An earlier version of this script normalized each
cell independently (per-cell min-max) -- which visually stretched every
glyph's response to fill the same color range regardless of its actual
magnitude, making every digit look like it "detects" every feature
strongly.  That defeated the entire point of a cross-digit debug table:
the classifier cares about RELATIVE magnitude between digits/orientations,
and per-cell normalization erases exactly that signal.  With shared
scaling, a weak response is now visibly dim and a strong one is visibly
vivid, comparable at a glance across the whole table.

Usage:
    python debugs/debug_gabor_features.py
    python debugs/debug_gabor_features.py --images single/fb_d_060518.png
    python debugs/debug_gabor_features.py --images single/a.png single/b.png --output out.png
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
from gfl2.stat_ocr_v0_2_0 import (
    _GABOR_KERNELS, _GABOR_STEP, _paren_templates, _norm_xcorr,
    _fft_magnitudes, _make_hist, _ring_energies, N_BINS, N_RINGS,
)

# Default: the smallest single image (by total digit-glyph count) in
# single/*.png whose pct-line digits alone cover all of '0'-'9' -- found by
# a one-off scan (see docs/known_issues.txt §15's DEBUG TABLE entry).
DEFAULT_IMAGE = "single/fb_d_060518.png"

DIGITS   = "0123456789"
UPSCALE  = 8      # 12x20 glyph -> 96x160 for visibility
ALPHA    = 0.55   # heatmap/template overlay opacity

CELL_W, CELL_H = 130, 190
LABEL_W  = 90
HEADER_H = 46
CAPTION_H = 22    # reserved strip at the bottom of each cell for text


# ── Glyph extraction (mirrors gfl2.stat_ocr_v0_2_0._extract_pct_digit_glyphs, ──
#    but keeps the raw + binarized intermediate crops that function discards)

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
    """First occurrence of each digit across image_paths, in cell-iteration
    order -- deterministic given a fixed image list.  Returns
    {digit: {"label","raw","binarized","normalized","source"}}."""
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
    """Nearest-neighbor upscale img_bgr to fit within (w, h) preserving
    aspect ratio, then paste centered -- nearest-neighbor keeps individual
    source pixels visibly square/blocky, which matters more here than
    smoothness since these crops are tiny (down to a few pixels wide)."""
    ih, iw = img_bgr.shape[:2]
    scale = min(w / iw, h / ih)
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    resized = cv2.resize(img_bgr, (nw, nh), interpolation=cv2.INTER_NEAREST)
    ox, oy = x0 + (w - nw) // 2, y0 + (h - nh) // 2
    canvas[oy: oy + nh, ox: ox + nw] = resized


def _heatmap_overlay(norm_glyph: np.ndarray, response: np.ndarray, global_max: float) -> np.ndarray:
    """abs(response) scaled against a GLOBAL max (shared across every digit
    and orientation in the table, not this cell alone), JET-colormapped,
    alpha-blended over the (grayscale) normalized glyph.  A weak response
    now renders visibly dim; only a response near the table-wide strongest
    renders fully saturated -- see module docstring's NORMALIZATION note."""
    mag = np.abs(response).astype(np.float64)
    scale = global_max if global_max > 1e-9 else 1.0
    mag_u8 = np.clip(mag / scale * 255, 0, 255).astype(np.uint8)
    heat = cv2.applyColorMap(mag_u8, cv2.COLORMAP_JET)
    base = _to_bgr(norm_glyph)
    return cv2.addWeighted(heat, ALPHA, base, 1 - ALPHA, 0)


def _template_overlay(
    norm_glyph: np.ndarray, template: np.ndarray, color: tuple,
    corr: float, corr_min: float, corr_max: float,
) -> np.ndarray:
    """template (0/255 mask) drawn in `color`, opacity SCALED by how strong
    `corr` is relative to [corr_min, corr_max] (the range observed across
    the WHOLE table, both '(' and ')', all digits) -- a weak/negative
    correlation renders the template nearly invisible; the single
    strongest correlation anywhere in the table renders it at full ALPHA.
    This encodes the actual signal visually instead of a flat highlight
    that looks identical regardless of score -- see module docstring's
    NORMALIZATION note."""
    base = _to_bgr(norm_glyph).astype(np.float64)
    mask = (template > 0)
    rng = max(corr_max - corr_min, 1e-9)
    strength = float(np.clip((corr - corr_min) / rng, 0.0, 1.0))
    alpha = ALPHA * strength
    blended = base.copy()
    blended[mask] = base[mask] * (1 - alpha) + np.array(color, dtype=np.float64) * alpha
    return blended.astype(np.uint8)


def _bar_chart(values: np.ndarray, w: int, h: int, global_max: float, color=(180, 90, 0)) -> np.ndarray:
    """Vertical bar chart of `values` against a GLOBAL max (shared across
    all digits for this feature) so bar heights are comparable cell to
    cell -- the honest representation for a 1D feature (hist, ring) that
    has no spatial pixel mapping to overlay instead."""
    img = np.full((h, w, 3), 250, dtype=np.uint8)
    n = len(values)
    bar_w = max(1, w // n)
    scale = global_max if global_max > 1e-9 else 1.0
    for i, v in enumerate(values):
        bh = int(np.clip(v / scale, 0, 1) * (h - 8))
        x0 = i * bar_w
        cv2.rectangle(img, (x0 + 1, h - 3 - bh), (x0 + max(1, bar_w - 1), h - 3), color, -1)
    cv2.line(img, (0, h - 3), (w, h - 3), (170, 170, 170), 1)
    return img


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

def _compute_raw_features(glyphs_by_digit: dict) -> dict:
    """Pass 1: compute every raw feature value for every present digit,
    with NO normalization applied yet -- normalization scales are derived
    from this dict afterward so they can be shared across the whole table
    (see module docstring's NORMALIZATION note)."""
    raw = {}
    for d, g in glyphs_by_digit.items():
        norm = g["normalized"]
        f32 = norm.astype(np.float32)
        h, w = norm.shape

        gabor_resp = [np.abs(cv2.filter2D(f32, -1, k)) for k in _GABOR_KERNELS]

        open_t, close_t = _paren_templates(h, w)
        corr_open  = _norm_xcorr(norm, open_t)
        corr_close = _norm_xcorr(norm, close_t)

        hist = _make_hist(_fft_magnitudes(norm), N_BINS)
        ring = _ring_energies(norm, N_RINGS)

        raw[d] = {
            "gabor_resp": gabor_resp, "open_t": open_t, "close_t": close_t,
            "corr_open": corr_open, "corr_close": corr_close,
            "hist": hist, "ring": ring,
        }
    return raw


def build_table(glyphs_by_digit: dict) -> np.ndarray:
    raw = _compute_raw_features(glyphs_by_digit)

    # Global scales -- shared across every digit (and, for Gabor, every
    # orientation) so cell-to-cell color/height differences reflect real
    # magnitude differences instead of independent per-cell stretching.
    gabor_global_max = max(
        (float(r.max()) for v in raw.values() for r in v["gabor_resp"]), default=1.0
    )
    all_corr = [v["corr_open"] for v in raw.values()] + [v["corr_close"] for v in raw.values()]
    corr_min, corr_max = (min(all_corr), max(all_corr)) if all_corr else (0.0, 1.0)
    hist_global_max = max((float(v["hist"].max()) for v in raw.values()), default=1.0)
    ring_global_max = max((float(v["ring"].max()) for v in raw.values()), default=1.0)

    angle_labels = [f"gabor_{int(round(i * 180 / _GABOR_STEP))}deg" for i in range(len(_GABOR_KERNELS))]
    columns = (
        ["original_crop", "binarized_crop", "normalized_12x20"]
        + angle_labels
        + ["paren_(", "paren_)", "hist (64 bins)", "ring (8 bins)"]
    )
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
    cv2.putText(canvas, f"(shared scale: gabor<={gabor_global_max:.3f} "
                         f"corr in [{corr_min:.2f},{corr_max:.2f}])",
                (LABEL_W + 4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (90, 90, 90), 1, cv2.LINE_AA)

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
        r = raw[d]
        w = norm.shape[1]

        cell_imgs, captions = [], []
        cell_imgs.append(_to_bgr(g["raw"]));         captions.append("")
        cell_imgs.append(_to_bgr(g["binarized"]));   captions.append("")
        cell_imgs.append(_to_bgr(norm));             captions.append(f"{norm.shape[1]}x{norm.shape[0]}")

        for resp in r["gabor_resp"]:
            cell_imgs.append(_heatmap_overlay(norm, resp, gabor_global_max))
            captions.append(f"mean={resp.mean():.3f}")

        cell_imgs.append(_template_overlay(norm, r["open_t"], (0, 200, 0),
                                            r["corr_open"], corr_min, corr_max))
        captions.append(f"corr={r['corr_open']:.2f}")
        cell_imgs.append(_template_overlay(norm, r["close_t"], (0, 0, 220),
                                            r["corr_close"], corr_min, corr_max))
        captions.append(f"corr={r['corr_close']:.2f}")

        cell_imgs.append(_bar_chart(r["hist"], CELL_W - 8, CELL_H - CAPTION_H - 8, hist_global_max))
        captions.append(f"max={r['hist'].max():.3f}")
        cell_imgs.append(_bar_chart(r["ring"], CELL_W - 8, CELL_H - CAPTION_H - 8, ring_global_max,
                                     color=(0, 130, 180)))
        captions.append(f"max={r['ring'].max():.3f}")

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
    ap.add_argument("--output", default="tests/outputs/daily/gabor_feature_table.png",
                     help="Where to write the debug image  [default: "
                          "tests/outputs/daily/ -- already gitignored, same "
                          "as other stat_ocr --debug diagnostic output]")
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

    table = build_table(glyphs_by_digit)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), table)
    print(f"Wrote {table.shape[1]}x{table.shape[0]} debug table -> {out_path}")
    print(f"Gabor kernels visualized: {len(_GABOR_KERNELS)} "
          f"(currently loaded from assets/fonts/gabor_calib.json if present)")


if __name__ == "__main__":
    main()
