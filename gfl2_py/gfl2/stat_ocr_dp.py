# -*- coding: utf-8 -*-
"""
gfl2/stat_ocr_dp.py -- simplified, mostly-spatial-domain nearest-centroid OCR
engine for Daily Gunsmoke stat cells (pct-line only), built by COPYING the
specific mechanisms this session's exploration validated inside
gfl2/stat_ocr_fft.py -- NOT by modifying that engine. gfl2/stat_ocr_fft.py is
left completely untouched (no import from it, no edits to it); this module
duplicates only the pieces it actually needs, matching this project's
established full-duplication precedent for parallel engines (decision 47's
policy, gfl2/stat_ocr_padded.py) rather than a config flag on the existing
one -- the two trees are structurally different enough (this one has no
Agent A/B two-agent fallback, no pair-tiebreak, no vstroke-gate, no
hbar-sliding mode) that a shared module would need more branching machinery
than either tree on its own.

WHY "DP": the root mechanism is cv2.approxPolyDP-derived reflex-vertex
spread (gfl2/stat_ocr_fft.py's known_issues.txt §30), not FFT/Gabor -- and
almost everything downstream of it turned out to be replaceable with plain
spatial primitives too (contour geometry, cross-correlation template
matching, a fixed-position ink count), once "falling back to the spatial
domain is unavoidable" was accepted as the premise. The ONE remaining
frequency-domain-derived feature (_hbar_features_sobel's merged-kernel
Sobel-90 convolution) is kept for exactly one leaf ('2' vs '5') where no
clean spatial substitute has been found yet -- this engine is "not FFT-major"
rather than "FFT-free".

TREE:
  isoperimetric ratio (contour geometry, ISO_GATE_LO/HI)
  +-- circular ({0,6,8,9} likely): inner-blob hole count
  |     +-- holes>=2 -> '8' (categorical)
  |     +-- holes==1 -> {0,6,9} via paren+loop nearest-of-3 (corpus-trained
  |     |               centroids, reused from the existing stat_pct_fft.py
  |     |               template file -- no new training needed)
  |     +-- holes==0 -> '?' (defensive; never hit on the real corpus)
  +-- non-circular ({1,2,3,4,5,7} likely):
        +-- '4' gate FIRST (top-band ink count at the CROSSBAR's own row
        |   band, atlas-derived -- see TOP_BAND_4 section below): PERFECT
        |   on the real corpus (recall=1.0000, false_trigger=0.0000, real
        |   gap=1, held-out 1259/1259) -- replaces what used to be THREE
        |   separate rescue branches in stat_ocr_fft.py's spread_y tree
        |   with ONE upfront check. If it fires, done -- no reflex-vertex
        |   work, no Sobel convolution, nothing else computed at all.
        +-- else: spread_y (reflex-vertex vertical spread) splits {1,7}
            (spread_y==0 always) from {2,3,5} (spread_y>=8 always) -- a
            PERFECT, wide (8-unit), trivial gap now that '4' (the only
            digit that ever contaminated this boundary) is already gone.
            +-- {1,7}: top-band ink count (height=3, near the very top)
            |     -- PERFECT (real gap=3) -- '7' vs '1'.
            +-- {2,3,5}: paren_close (cross-correlation vs a ')' template,
                  already validated 100% recall/0% false-trigger) -> '3';
                  else _hbar_features_sobel nearest-of-2 (the ONE
                  frequency-domain feature kept) -> '2' or '5'.

STATUS: EXPLORATORY, pct-line only (matching gfl2/stat_ocr_fft.py's own
val-line gap -- _extract_val_glyphs/_reconstruct_val below are real no-op
functions, not omissions, so this class's is_pct dispatch shape matches
every other engine). NOT registered in main.py's --stat-ocr-engine
selector -- no production entry point reaches this module.

VALIDATED (2026-07-10): every individual gate/split in this tree measures
PERFECT (recall=1.0000/false_trigger=0.0000, or already-100%-accuracy
nearest-of-2/3) on the real single/*.png corpus (6792 non-circular +
3535 circular glyphs) except the final '2'/'5' sobel_mean split, which was
ALREADY 100.00% accurate in gfl2/stat_ocr_fft.py and is unchanged here.
End-to-end validation of THIS assembled engine is tracked separately (run
--verify-glyphs) -- do not assume the individual-piece numbers above
compose to the same result without checking; that composition IS checked
by this module's own verify_glyphs() run, not merely inferred.

Usage:
    python -m gfl2.stat_ocr_dp --verify --images "single/*.png"
    python -m gfl2.stat_ocr_dp --verify-glyphs --images "single/*.png"
"""
from __future__ import annotations
import json, sys, time, glob as _glob
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from gfl2.stat_ocr import (
    PCT_STRIP_Y, VAL_STRIP_Y, DOT_MAX_DIM, NORM_W_PCT, NORM_H_PCT,
    _binarize, _find_blobs, _filter_y_outliers, _find_percent_x_start,
    _collect_cells, _count_inner_blobs,
)

_HERE = Path(__file__).parent.parent
_FONTS_DIR = _HERE / "assets" / "fonts"
# Reuses gfl2/stat_ocr_fft.py's ALREADY-TRAINED template file, read-only --
# only its '0'/'6'/'9' paren/loop centroid slots are used (see
# _load_circular_centroids below). No new --build step exists or is needed
# for this engine.
_SOURCE_TMPL_F = _FONTS_DIR / "stat_pct_fft.py"

TRAIN_CHARS = list("0123456789")


# ── ROOT GATE: isoperimetric ratio (copied from gfl2/stat_ocr_fft.py) ───────
ISO_GATE_LO = 0.48
ISO_GATE_HI = 0.95


def _isoperimetric_ratio(norm: np.ndarray) -> float:
    """4*pi*area / perimeter^2 of the glyph's outer contour -- 1.0 for a
    perfect circle, well below 1.0 for an elongated/open-stroke shape."""
    padded = cv2.copyMakeBorder(norm, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=0)
    cnts, _ = cv2.findContours(padded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cnts:
        return 0.0
    outer = max(cnts, key=cv2.contourArea)
    area = cv2.contourArea(outer)
    perim = cv2.arcLength(outer, True)
    if area <= 0 or perim <= 0:
        return 0.0
    return float((4 * np.pi * area) / (perim ** 2))


# ── Paren / loop cross-correlation templates (copied from gfl2/stat_ocr_fft.py) ─
# Whole-glyph normalized cross-correlation against hand-drawn curve templates
# -- spatial template matching, no FFT/kernel involved.
_PAREN_TEMPLATE_CACHE: "dict[tuple[int, int], tuple[np.ndarray, np.ndarray]]" = {}
_LOOP_CY_TOP, _LOOP_CY_BOT = 0.35, 0.65
_LOOP_RY_FRAC, _LOOP_RX_FRAC = 0.20, 0.80
_LOOP_TEMPLATE_CACHE: "dict[tuple[int, int], tuple[np.ndarray, np.ndarray]]" = {}


def _paren_templates(h: int, w: int) -> "tuple[np.ndarray, np.ndarray]":
    key = (h, w)
    cached = _PAREN_TEMPLATE_CACHE.get(key)
    if cached is not None:
        return cached
    axes = (max(1, w - 2), h // 2 + 2)
    open_t = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(open_t, (w - 1, h // 2), axes, 0, 90, 270, 255, thickness=2)
    close_t = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(close_t, (0, h // 2), axes, 0, -90, 90, 255, thickness=2)
    _PAREN_TEMPLATE_CACHE[key] = (open_t, close_t)
    return open_t, close_t


def _loop_templates(h: int, w: int) -> "tuple[np.ndarray, np.ndarray]":
    key = (h, w)
    cached = _LOOP_TEMPLATE_CACHE.get(key)
    if cached is not None:
        return cached
    rx = max(2, int(round(_LOOP_RX_FRAC * w)))
    ry = max(2, int(round(_LOOP_RY_FRAC * h)))
    top_t = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(top_t, (w - 1, int(round(_LOOP_CY_TOP * h))), (rx, ry), 0, 90, 270, 255, thickness=2)
    bot_t = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(bot_t, (w - 1, int(round(_LOOP_CY_BOT * h))), (rx, ry), 0, 90, 270, 255, thickness=2)
    _LOOP_TEMPLATE_CACHE[key] = (top_t, bot_t)
    return top_t, bot_t


def _norm_xcorr(a: np.ndarray, b: np.ndarray) -> float:
    af = a.astype(np.float64).ravel() - a.mean()
    bf = b.astype(np.float64).ravel() - b.mean()
    denom = (np.linalg.norm(af) * np.linalg.norm(bf)) + 1e-9
    return float(np.dot(af, bf) / denom)


def _paren_features(gray_norm: np.ndarray) -> np.ndarray:
    """[corr_with_'(' , corr_with_')']."""
    h, w = gray_norm.shape
    open_t, close_t = _paren_templates(h, w)
    return np.array([_norm_xcorr(gray_norm, open_t), _norm_xcorr(gray_norm, close_t)])


def _loop_features(gray_norm: np.ndarray) -> np.ndarray:
    """[corr_with_loop_top, corr_with_loop_bot]."""
    h, w = gray_norm.shape
    top_t, bot_t = _loop_templates(h, w)
    return np.array([_norm_xcorr(gray_norm, top_t), _norm_xcorr(gray_norm, bot_t)])


PAREN_CLOSE_3_GATE = 0.277  # gfl2/stat_ocr_fft.py's leaf_235.paren_close_gate


# ── Reflex-vertex spread (copied from gfl2/stat_ocr_fft.py) ─────────────────
SPREAD_EPS = 0.03
# Once '4' is gated out FIRST (see TOP_BAND_4 below), {1,7} (spread_y==0
# always) and {2,3,5} (spread_y>=8 always) never overlap at all -- any
# threshold in (0, 8) works; 4.0 is the midpoint, not a fitted edge.
SPREAD_Y_THRESHOLD = 4.0


def _reflex_vertices(gray_norm: np.ndarray, eps_frac: float = SPREAD_EPS) -> "tuple[np.ndarray, float] | tuple[None, None]":
    padded = cv2.copyMakeBorder(gray_norm, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=0)
    cnts, hierarchy = cv2.findContours(padded, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    if not cnts or hierarchy is None:
        return None, None
    outers = [(i, c) for i, c in enumerate(cnts) if hierarchy[0][i][3] < 0]
    if not outers:
        return None, None
    _, outer = max(outers, key=lambda t: cv2.contourArea(t[1]))

    x, y, bw, bh = cv2.boundingRect(outer)
    ink_center_x = x + bw / 2.0

    perim = cv2.arcLength(outer, True)
    eps = max(eps_frac * perim, 0.5)
    approx = cv2.approxPolyDP(outer, eps, True)
    pts = approx.reshape(-1, 2).astype(np.float64)
    n = len(pts)
    if n < 3:
        return np.empty((0, 2)), ink_center_x

    signed_area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
                       for i in range(n))
    overall_sign = 1.0 if signed_area >= 0 else -1.0
    reflex_pts = []
    for i in range(n):
        prev, cur, nxt = pts[i - 1], pts[i], pts[(i + 1) % n]
        v1, v2 = cur - prev, nxt - cur
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        if cross != 0 and (cross > 0) != (overall_sign > 0):
            reflex_pts.append(cur)
    return np.array(reflex_pts).reshape(-1, 2), ink_center_x


def _spread_y(reflex_pts: "np.ndarray | None") -> float:
    if reflex_pts is None or len(reflex_pts) == 0:
        return 0.0
    return float(reflex_pts[:, 1].max() - reflex_pts[:, 1].min())


# ── Top-band ink count (copied from gfl2/stat_ocr_fft.py) ───────────────────
def _band_count(gray_norm: np.ndarray, y0: int, y1: int) -> int:
    """Count of non-zero (ink) pixels in rows [y0, y1) (exclusive), full
    width -- a kernel-free, convolution-free spatial primitive. Used at two
    different row bands below for two different digits."""
    return int(cv2.countNonZero(gray_norm[y0:y1, :]))


# '7' vs '1': top 3 rows -- gfl2/stat_ocr_fft.py's TOP_BAND_HEIGHT/
# TOP_BAND_7_GATE (gfl2/configs/daily_pct_spread_gate_calib.json), copied
# here as plain constants rather than a JSON-config load, per this engine's
# "simpler" mandate. Real corpus gap: '7' min=23, '1' max=20 (gap=3).
TOP_BAND_7_HEIGHT = 3
TOP_BAND_7_GATE = 21.5

# '4': the CROSSBAR's own row band, derived once from assets/fonts/
# glyph_daily_pct.png's real '4' sample -- see debugs/ exploration this
# session (row-wise ink-density profile, peak at the flat crossbar, half-
# max-ish threshold isolates rows [12,15] cleanly from the diagonal's
# approach; expanded +-1px per the original request -> [11,16]). Real
# corpus gap: '4' min=48, next-highest of every other non-circular digit
# (all six: '1','2','3','5','7') = 47 (from '3') -- a genuine, if thin
# (1-unit), non-overlapping gap; confirmed on the 16-image held-out set too
# (1259/1259 correct isolating 4-vs-not-4 at this threshold).
TOP_BAND_4_Y0 = 11
TOP_BAND_4_Y1 = 17  # exclusive -- rows 11..16 inclusive
TOP_BAND_4_GATE = 47.5


# ── Sobel-90 merged kernel (copied from gfl2/stat_ocr_fft.py) ───────────────
# The ONE remaining frequency-domain-derived feature in this engine, kept
# only for the '2'/'5' leaf -- no clean spatial substitute found yet (a
# top-band count gets close, 96.46% recall/0.93% false-trigger, but not as
# clean as this, which is already 100.00% in gfl2/stat_ocr_fft.py).
_SOBEL90_5X5 = np.array([
    [-1, -4,  -6, -4, -1],
    [-2, -8, -12, -8, -2],
    [ 0,  0,   0,  0,  0],
    [ 2,  8,  12,  8,  2],
    [ 1,  4,   6,  4,  1],
], dtype=np.float64)
_SOBEL90_ITERATIONS = 3
_SOBEL90_MERGED_KERNEL_CACHE: "np.ndarray | None" = None


def _conv2d_full(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ah, aw = a.shape
    bh, bw = b.shape
    out = np.zeros((ah + bh - 1, aw + bw - 1), dtype=np.float64)
    bf = b[::-1, ::-1]
    for i in range(ah):
        for j in range(aw):
            out[i:i + bh, j:j + bw] += a[i, j] * bf
    return out


def _sobel90_merged_kernel() -> np.ndarray:
    global _SOBEL90_MERGED_KERNEL_CACHE
    if _SOBEL90_MERGED_KERNEL_CACHE is not None:
        return _SOBEL90_MERGED_KERNEL_CACHE
    merged = _SOBEL90_5X5
    for _ in range(_SOBEL90_ITERATIONS - 1):
        merged = _conv2d_full(merged, _SOBEL90_5X5)
    _SOBEL90_MERGED_KERNEL_CACHE = merged
    return merged


def _hbar_features_sobel(gray_norm: np.ndarray) -> np.ndarray:
    """[mean, max] of the merged-kernel Sobel-90 response magnitude."""
    kernel = _sobel90_merged_kernel()
    m = kernel.shape[0] // 2
    h, w = gray_norm.shape
    canvas = np.zeros((h + 2 * m, w + 2 * m), dtype=np.float64)
    canvas[m:m + h, m:m + w] = gray_norm
    resp = np.abs(cv2.filter2D(canvas, -1, kernel, borderType=cv2.BORDER_CONSTANT))
    resp = resp[m:m + h, m:m + w]
    return np.array([float(resp.mean()), float(resp.max())])


SOBEL_MEAN_C2 = 20805927.45  # gfl2/stat_ocr_fft.py's leaf_235.sobel_mean_c2
SOBEL_MEAN_C5 = 28691358.42  # gfl2/stat_ocr_fft.py's leaf_235.sobel_mean_c5


# ── Glyph normalize/extract (copied from gfl2/stat_ocr_fft.py) ─────────────
def _pad_glyph_no_resize(crop: np.ndarray, norm_w: int, norm_h: int) -> np.ndarray:
    canvas = np.zeros((norm_h, norm_w), dtype=crop.dtype)
    ch, cw = crop.shape[:2]
    if ch == 0 or cw == 0:
        return canvas
    sy0 = max(0, (ch - norm_h) // 2)
    sx0 = max(0, (cw - norm_w) // 2)
    src = crop[sy0: sy0 + norm_h, sx0: sx0 + norm_w]
    sh, sw = src.shape[:2]
    dy0 = (norm_h - sh) // 2
    dx0 = (norm_w - sw) // 2
    canvas[dy0: dy0 + sh, dx0: dx0 + sw] = src
    return canvas


def _extract_pct_glyphs(pct_blobs: list, thresh: np.ndarray) -> "list[tuple[int, Optional[np.ndarray], str]]":
    """Inference-time (label-free) glyph extraction. Same shape as
    gfl2.stat_ocr_fft's function of the same name."""
    if not pct_blobs:
        return []
    blobs = sorted(pct_blobs, key=lambda b: b[0])
    pct_x = _find_percent_x_start(blobs)
    result = []
    for (x, y, w, h) in blobs:
        if pct_x is not None and x >= pct_x:
            result.append((x, None, 'skip'))
            continue
        if w <= DOT_MAX_DIM and h <= DOT_MAX_DIM:
            result.append((x, None, '.'))
        else:
            crop = thresh[y: y + h, x: x + w]
            norm = _pad_glyph_no_resize(crop, NORM_W_PCT, NORM_H_PCT)
            result.append((x, norm, 'digit'))
    return result


_PCT_STRIP_EXTRA_PX = 5


def _pct_strip_bottom(ch: int) -> int:
    return min(ch, int(ch * PCT_STRIP_Y[1]) + _PCT_STRIP_EXTRA_PX, int(ch * VAL_STRIP_Y[0]))


def _extract_pct_digit_glyphs(cell: np.ndarray, pct_label: str):
    """Training/verify-time (label-aligned) glyph extraction. Returns
    [(norm_bin_12x20, digit_char), ...] or None if the blob count doesn't
    match the label."""
    if not pct_label:
        return None
    expected = [c for c in pct_label if c.isdigit()]
    if not expected:
        return None

    ch = cell.shape[0]
    pct_strip = cell[: _pct_strip_bottom(ch), :]
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

    glyphs = []
    for (x, y, w, h), label in zip(digit_blobs, expected):
        crop = thresh[y: y + h, x: x + w]
        if crop.size == 0:
            return None
        norm = _pad_glyph_no_resize(crop, NORM_W_PCT, NORM_H_PCT)
        glyphs.append((norm, label))
    return glyphs


def _extract_val_glyphs(blobs: list, thresh) -> list:
    """NOT IMPLEMENTED -- val-line classification was never built in
    gfl2/stat_ocr_fft.py either. Kept as a real no-op function (matching
    that module's own convention) so this class's is_pct dispatch shape
    stays identical to every other engine."""
    return []


def _reconstruct_val(glyphs: list, templates: dict) -> Optional[str]:
    return None


# ── Classify tree ────────────────────────────────────────────────────────────
def classify(norm: np.ndarray, circular_centroids: dict) -> str:
    """Full classify tree -- see module docstring for the diagram.
    circular_centroids: {'0': [paren_open, paren_close, loop_top, loop_bot],
    '6': [...], '9': [...]} -- reused from gfl2/stat_ocr_fft.py's already-
    trained stat_pct_fft.py template (see _load_circular_centroids)."""
    iso = _isoperimetric_ratio(norm)
    if ISO_GATE_LO <= iso <= ISO_GATE_HI:
        holes = _count_inner_blobs(norm)
        if holes >= 2:
            return '8'
        if holes == 1:
            combined = np.concatenate([_paren_features(norm), _loop_features(norm)])
            best_d, best_dist = None, None
            for d, centroid in circular_centroids.items():
                dist = float(np.linalg.norm(combined - centroid))
                if best_dist is None or dist < best_dist:
                    best_d, best_dist = d, dist
            return best_d if best_d is not None else '?'
        return '?'  # holes==0 but iso_gate said circular -- defensive, unexpected

    # non-circular: '4' gate FIRST, before any reflex-vertex work at all.
    if _band_count(norm, TOP_BAND_4_Y0, TOP_BAND_4_Y1) >= TOP_BAND_4_GATE:
        return '4'

    reflex_pts, _ = _reflex_vertices(norm)
    sy = _spread_y(reflex_pts)
    if sy <= SPREAD_Y_THRESHOLD:
        # {1,7}
        top = _band_count(norm, 0, TOP_BAND_7_HEIGHT)
        return '7' if top >= TOP_BAND_7_GATE else '1'

    # {2,3,5}
    paren_close = _paren_features(norm)[1]
    if paren_close > PAREN_CLOSE_3_GATE:
        return '3'
    sobel_mean = float(_hbar_features_sobel(norm)[0])
    return '2' if abs(sobel_mean - SOBEL_MEAN_C2) < abs(sobel_mean - SOBEL_MEAN_C5) else '5'


# ── Circular-leaf centroids: reuse gfl2/stat_ocr_fft.py's already-trained file ─
_PAREN_OPEN_IDX, _PAREN_CLOSE_IDX = 1, 2
_LOOP_TOP_IDX, _LOOP_BOT_IDX = 11, 12


def _load_circular_centroids(tmpl_path: Path = _SOURCE_TMPL_F) -> dict:
    """{'0': np.array([paren_open, paren_close, loop_top, loop_bot]), '6': ...,
    '9': ...} sliced from gfl2/stat_ocr_fft.py's own trained gpr centroids --
    no new training/calibration needed for this engine's one remaining
    trained-data dependency."""
    if not tmpl_path.exists():
        raise FileNotFoundError(
            f"stat_ocr_dp needs gfl2/stat_ocr_fft.py's trained templates: {tmpl_path}\n"
            f"Run: python -m gfl2.stat_ocr_fft --build"
        )
    import importlib.util
    spec = importlib.util.spec_from_file_location(tmpl_path.stem, tmpl_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    gpr = mod.DATA["pct"]["gpr"]
    idx = [_PAREN_OPEN_IDX, _PAREN_CLOSE_IDX, _LOOP_TOP_IDX, _LOOP_BOT_IDX]
    return {d: np.asarray(gpr[d], dtype=np.float64)[idx] for d in ('0', '6', '9') if d in gpr}


# ── Public engine ─────────────────────────────────────────────────────────────
class StatOcrDp:
    """Simplified, mostly-spatial-domain nearest-centroid OCR engine --
    pct-line only, exploratory. See module docstring for the full tree."""

    def __init__(self, circular_centroids: dict) -> None:
        self._circular_centroids = circular_centroids

    @classmethod
    def load(cls, tmpl_path: Path = _SOURCE_TMPL_F) -> "StatOcrDp":
        return cls(_load_circular_centroids(tmpl_path))

    def read(self, cell: np.ndarray, timer=None) -> "tuple[Optional[str], Optional[str]]":
        ch = cell.shape[0]
        pct_strip = cell[: _pct_strip_bottom(ch), :]
        val_strip = cell[int(ch * VAL_STRIP_Y[0]): int(ch * VAL_STRIP_Y[1]), :]
        pct_str = self._read_line(pct_strip, is_pct=True)
        val_str = self._read_line(val_strip, is_pct=False)
        return pct_str, val_str

    def _read_line(self, strip: np.ndarray, is_pct: bool) -> Optional[str]:
        if strip.size == 0:
            return None
        if not is_pct:
            return _reconstruct_val(_extract_val_glyphs([], None), {})

        thresh = _binarize(strip)
        blobs = _find_blobs(thresh)
        if not blobs:
            return None
        blobs = _filter_y_outliers(blobs, threshold=12)
        if not blobs:
            return None
        glyphs = _extract_pct_glyphs(blobs, thresh)

        items = [(x, norm, hint) for x, norm, hint in glyphs if hint != 'skip']
        parts = []
        for i, (x, norm, hint) in enumerate(items):
            if hint == '.':
                parts.append('.')
            else:
                c = classify(norm, self._circular_centroids)
                if c == '?' and i == len(items) - 1:
                    continue  # rightmost unclassifiable blob -> % glyph, drop it
                parts.append(c)
        result = ''.join(parts).strip('.')
        return result if result and '?' not in result else None


# ── Benchmark / verification ────────────────────────────────────────────────
def verify(image_paths: "list[Path]", verbose: bool = True,
           gt_overrides: "dict | None" = None, gt_cache: "dict | None" = None) -> dict:
    """Cell-level: compare against Tesseract ground truth, same contract as
    gfl2.stat_ocr_fft.verify()."""
    import statistics
    from gfl2.stat_ocr import _load_tess_gt_cache
    run_start = datetime.now().isoformat(timespec="seconds")
    engine = StatOcrDp.load()
    if gt_cache is None:
        gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, gt_cache=gt_cache)

    _GT_FILE = Path("stat_gt_overrides.json")
    if gt_overrides is None:
        gt_overrides = json.loads(_GT_FILE.read_text()) if _GT_FILE.exists() else {}
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and "pct" in ov:
            item["pct"] = ov["pct"]

    pct_total = pct_match = pct_miss = 0
    mismatches = []
    classify_times = []
    for item in samples:
        t0 = time.perf_counter()
        blob_pct, _blob_val = engine.read(item["cell"])
        classify_times.append(time.perf_counter() - t0)
        if item["pct"]:
            pct_total += 1
            if blob_pct is None:
                pct_miss += 1
                mismatches.append((item["source"], item["pct"], blob_pct))
            elif blob_pct != item["pct"]:
                mismatches.append((item["source"], item["pct"], blob_pct))
            else:
                pct_match += 1

    mean_us = statistics.mean(classify_times) * 1e6 if classify_times else 0.0
    stdev_us = statistics.pstdev(classify_times) * 1e6 if len(classify_times) > 1 else 0.0
    cv_ = (stdev_us / mean_us) if mean_us else 0.0

    if verbose:
        def pct_str(n, d): return f"{100*n/d:.1f}%" if d else "n/a"
        print(f"\n{'-'*60}")
        print(f"Generated: {run_start}  (run start)")
        print(f"StatOcrDp verify  ({len(image_paths)} images, {len(samples)} cells)")
        print(f"  pct  {pct_match}/{pct_total} correct  ({pct_str(pct_match, pct_total)})  {pct_miss} no-read")
        print(f"  val  not implemented (pct-line only)")
        print(f"  timing  mean={mean_us:.1f}us/cell  stdev={stdev_us:.1f}us  cv={cv_:.2f}  (n={len(classify_times)} cells)")
        if mismatches:
            print(f"\nFirst 20 mismatches:")
            for source, exp, got in mismatches[:20]:
                print(f"  {source}  pct  expected={exp!r}  got={got!r}")
        print(f"{'-'*60}")

    return {"pct_total": pct_total, "pct_match": pct_match, "pct_miss": pct_miss,
            "mismatches": mismatches, "mean_us": mean_us, "stdev_us": stdev_us, "cv": cv_}


def verify_glyphs(image_paths: "list[Path]", verbose: bool = True,
                   gt_overrides: "dict | None" = None, gt_cache: "dict | None" = None) -> dict:
    """Glyph-level: classify every individual labelled digit glyph and
    tally classified/correct/misclassified/unknown PER DIGIT."""
    import statistics
    from gfl2.stat_ocr import _load_tess_gt_cache
    run_start = datetime.now().isoformat(timespec="seconds")
    engine = StatOcrDp.load()

    if gt_cache is None:
        gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)

    _GT_FILE = Path("stat_gt_overrides.json")
    if gt_overrides is None:
        gt_overrides = json.loads(_GT_FILE.read_text()) if _GT_FILE.exists() else {}
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and "pct" in ov:
            item["pct"] = ov["pct"]

    per_digit = {d: {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0}
                 for d in TRAIN_CHARS}
    classify_times = []
    for item in samples:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, true_label in glyphs:
            bucket = per_digit.setdefault(
                true_label, {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0})
            t0 = time.perf_counter()
            pred = classify(norm, engine._circular_centroids)
            classify_times.append(time.perf_counter() - t0)
            bucket["classified"] += 1
            if pred == '?':
                bucket["unknown"] += 1
            elif pred == true_label:
                bucket["correct"] += 1
            else:
                bucket["misclassified"] += 1

    totals = {k: sum(per_digit[d][k] for d in per_digit)
              for k in ("classified", "correct", "misclassified", "unknown")}
    mean_us = statistics.mean(classify_times) * 1e6 if classify_times else 0.0
    stdev_us = statistics.pstdev(classify_times) * 1e6 if len(classify_times) > 1 else 0.0
    cv_ = (stdev_us / mean_us) if mean_us else 0.0

    if verbose:
        print(f"\n{'-'*60}")
        print(f"Generated: {run_start}  (run start)")
        print(f"StatOcrDp verify_glyphs  ({len(image_paths)} images, {totals['classified']} glyphs)")
        print(f"{'digit':>6} {'classified':>10} {'correct':>8} {'misclassified':>13} {'unknown':>8}")
        for d in TRAIN_CHARS:
            b = per_digit[d]
            print(f"{d:>6} {b['classified']:>10} {b['correct']:>8} {b['misclassified']:>13} {b['unknown']:>8}")
        acc = totals['correct'] / totals['classified'] if totals['classified'] else 0.0
        print(f"{'TOTAL':>6} {totals['classified']:>10} {totals['correct']:>8} "
              f"{totals['misclassified']:>13} {totals['unknown']:>8}  ({100*acc:.1f}% correct)")
        print(f"  timing  mean={mean_us:.1f}us/glyph  stdev={stdev_us:.1f}us  cv={cv_:.2f}  (n={len(classify_times)} glyphs)")
        print(f"{'-'*60}")

    return {"per_digit": per_digit, "totals": totals, "mean_us": mean_us, "stdev_us": stdev_us, "cv": cv_}


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--verify-glyphs", dest="verify_glyphs", action="store_true")
    ap.add_argument("--gt-overrides", default=None)
    args = ap.parse_args(argv)

    if not args.verify and not args.verify_glyphs:
        ap.print_help()
        sys.exit(1)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images) if "debug" not in Path(p).stem)
    if not image_paths:
        print(f"No images matched: {args.images}", file=sys.stderr)
        sys.exit(1)
    print(f"Images: {len(image_paths)}")

    from gfl2.stat_ocr import _load_tess_gt_cache
    gt_cache = _load_tess_gt_cache() or {}
    if gt_cache:
        print(f"Using Tesseract GT cache: {len(gt_cache)} cells")

    gt_file = Path(args.gt_overrides) if args.gt_overrides else Path("stat_gt_overrides.json")
    gt_overrides = json.loads(gt_file.read_text(encoding="utf-8")) if gt_file.exists() else None

    if args.verify:
        verify(image_paths, verbose=True, gt_overrides=gt_overrides, gt_cache=gt_cache)
    if args.verify_glyphs:
        verify_glyphs(image_paths, verbose=True, gt_overrides=gt_overrides, gt_cache=gt_cache)


if __name__ == "__main__":
    main()
