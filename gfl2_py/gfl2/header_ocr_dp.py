# -*- coding: utf-8 -*-
"""
gfl2/header_ocr_dp.py -- Daily Gunsmoke HEADER STATS-ROW reader (Damage
dealt / Damage taken / Combat turns) for `--stat-ocr-engine dp`, built by
copying the dp-family's spatial-primitive classify tree design (gfl2/
stat_ocr_dp.py, gfl2/score_ocr_dp.py) onto a real glyph atlas for THIS
font, assets/fonts/glyph_daily_header.png (0-9, K, M -- no '.' ever found
in a header crop, see debugs/build_glyph_reference.py's own module
docstring).

BACKGROUND: production's stats-row reading (gfl2/patterns/
daily_gunsmoke.py's `_extract_header`, inline `_read_stat_crop` closure)
already uses a simpler, FIXED-threshold binarization (HDR_THRESH=155,
no escalating-delta merge ladder -- unlike the header SCORE field's
THRESH_VAL+delta ladder that known_issues.txt #33 found silently drops
adjacent merged digits) plus gfl2.stat_ocr's own val-line projection-
correlation classifier (_extract_val_glyphs/_reconstruct_val, trained on
assets/fonts/stat_header.py). No segmentation bug is on record for this
field the way #33 documented for score -- this module's job is ONLY the
classify tree, reusing the SAME segmentation (binarize/find-blobs/drop-
label-bleed) production already uses, copied here rather than imported
(peer-module "write it twice" precedent, gfl2/stat_ocr_dp.py's own WHY
COPIED note).

CHARACTER SET: 0-9, K, M. K and M are new leaves this dp-family has never
needed before (gfl2/stat_ocr_dp.py's pct line and gfl2/score_ocr_dp.py's
score field are both digit-only, 0-9). Two new spatial primitives were
added specifically for them:

  - M: isolated FIRST, before the isoperimetric-ratio root gate even runs
    -- M's own glyph width alone (a single scalar, no sweep needed) is a
    clean, corpus-validated one-shot gate; nothing else in this font's
    character set renders anywhere near as wide. See M_WIDTH_GATE below.

  - K: isolated within the non-circular branch via a LEFT-anchored ink
    count -- the SAME mechanism this dp-family already uses for '4'/'7'/
    '5' (an ink count over a swept-width BAND), just transposed from a
    TOP row-band to a LEFT column-band: K's own leftmost stroke is a
    solid, near-full-height vertical bar (unlike '1'/'4', whose left
    edge is comparatively bare), so counting ink in the glyph's own
    leftmost columns (full height) isolates it the same way TOP_BAND_7/
    TOP_BAND_5 isolate their own target digits by counting a swept-height
    row band instead. See K_LEFT_GATE below.

TREE: see classify_header()'s own docstring for the exact diagram --
mirrors gfl2/stat_ocr_dp.py's tree shape (isoperimetric ratio root ->
circular hole-count/paren+loop leaf, or non-circular gate-first leaves)
with M gated out before the root and K gated out first inside the
non-circular branch, ahead of '4'.

CALIBRATION: every gate/centroid below is derived from Daily Gunsmoke's
own real header-stats-row crops (single/*.png's dealt/taken/turns crops,
Tesseract-GT-labelled with the same "0123456789KM" whitelist assets/
builders/build.py's own header-template training already uses) via
gfl2/calibration/calibrate_header_dp.py -- CORPUS, not the
glyph_daily_header.png atlas, for every interval-style gate (known_issues.txt
#27/decisions.txt #70's established atlas-vs-corpus distinction: an
atlas's n=1 sample can look clean in isolation while still misrouting
real corpus glyphs whose within-class spread that one sample can't
represent). Every gate constant loads from gfl2/configs/
daily_header_dp_calib.json at import time, falling back to this file's
own last-calibrated hardcoded default if that file is absent -- same
pattern as every other dp-family engine's calibration wiring.

NO NORMALIZATION: matching gfl2/stat_ocr_dp.py's own design (its
NORMALIZATION section), every glyph is used at its raw, native tight-crop
size -- no padding, no cropping, no resize. NO internal Tesseract
fallback of any kind -- every leaf either decides or abstains to '?'
directly (docs/action_items.txt #28's confidence-abstention concern
applies here identically; most leaves always answer).

SELECTION: `main.py --stat-ocr-engine dp` constructs a HeaderOcrDp
alongside gfl2.stat_ocr_dp.StatOcrDp and gfl2.score_ocr_dp.ScoreOcrDp,
injecting it into gfl2.patterns.daily_gunsmoke.parse(..., header_ocr=...).
Every other --stat-ocr-engine selection leaves header_ocr=None, which
keeps daily_gunsmoke.py's original stats-row pipeline completely
unchanged.

Usage:
    python -m gfl2.header_ocr_dp --verify --images "single/*.png"
    python -m gfl2.header_ocr_dp --verify-glyphs --images "single/*.png"
    python -m gfl2.calibration.calibrate_header_dp --images "single/*.png"  # recalibrate
"""
from __future__ import annotations
import glob as _glob
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from gfl2.stat_ocr import (
    BLOB_MIN_W, BLOB_MAX_W, BLOB_MAX_H, TRAIN_CHARS,
    _filter_y_outliers, _count_inner_blobs,
)

_HERE = Path(__file__).parent.parent
_CALIB_F = _HERE / "gfl2" / "configs" / "daily_header_dp_calib.json"

# ── Segmentation (copied from gfl2/patterns/daily_gunsmoke.py's
# _extract_header inline _read_stat_crop closure / assets/builders/
# build.py's own duplicate -- see module docstring's BACKGROUND) ──────────
HDR_THRESH = 155
HDR_BLOB_MIN_H = 12
_LABEL_BLEED_GAP = 15


def _binarize_hdr(gray: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY) if gray.ndim == 3 else gray
    _, thresh = cv2.threshold(gray, HDR_THRESH, 255, cv2.THRESH_BINARY_INV)
    return thresh


def _find_header_blobs(thresh: np.ndarray) -> "list[tuple[int, int, int, int]]":
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if BLOB_MIN_W <= w <= BLOB_MAX_W and HDR_BLOB_MIN_H <= h <= BLOB_MAX_H:
            blobs.append((x, y, w, h))
    return sorted(blobs, key=lambda b: b[0])


def _drop_label_bleed(blobs: "list[tuple[int, int, int, int]]",
                       gap_thresh: int = _LABEL_BLEED_GAP) -> "list[tuple[int, int, int, int]]":
    """Drop blobs left of the first inter-blob gap > gap_thresh px -- handles
    a trailing label character (e.g. "...dealt") bleeding into the crop
    when the value itself is short. Digit-to-digit gaps run 2-10px."""
    s = sorted(blobs, key=lambda b: b[0])
    for i in range(len(s) - 1):
        gap = s[i + 1][0] - (s[i][0] + s[i][2])
        if gap > gap_thresh:
            return s[i + 1:]
    return s


# ── Merge-split: adjacent identical digits (e.g. "44") can bridge into ONE
# blob at the fixed HDR_THRESH=155 -- discovered via this module's OWN
# whole-field verify() (glyph-level accuracy was already 100.0%; several
# whole-field mismatches turned out to be a genuine "44"->'M' misread, not a
# classify_header() defect). A merged pair's width (~20-23px on this corpus)
# comfortably exceeds even 'M's own widest real sample (15px), so the NEW
# M_WIDTH_GATE this module adds (see module docstring) unintentionally
# swallows a merge the same way it isolates a real M -- the same failure
# category as known_issues.txt #33's score-field "44" merge-drop, just a
# different downstream symptom (misclassified, not silently dropped).
#
# FIX DIRECTION: the opposite of the SCORE field's escalating-threshold
# ladder. Score text is BRIGHT-on-DARK (THRESH_BINARY there), so RAISING
# the threshold shrinks each stroke and can break a weak bridge. This
# crop's text is DARK-on-LIGHT (THRESH_BINARY_INV here), so the same idea
# requires LOWERING the threshold instead (a stricter "how dark counts as
# ink" bar) -- validated directly against a real merged "44" crop: it
# stays fused through HDR_THRESH-5, then cleanly splits into two 11px
# blobs at HDR_THRESH-10.
MERGE_WIDTH_GATE = 17  # real M max=15, real merge widths observed ~20-23
_SPLIT_DELTAS = (10, 15, 20, 25, 30)
_SPLIT_MIN_W, _SPLIT_MIN_H = BLOB_MIN_W, HDR_BLOB_MIN_H


def _try_split_merged(gray: np.ndarray, x: int, y: int, w: int, h: int):
    """Attempt to split one abnormally-wide blob into its real sub-glyphs by
    re-binarizing the FULL gray image at a stricter (lower) threshold and
    re-scanning just this blob's own (x, y, w, h) region. Returns
    [(x, y, w, h, source_thresh_image), ...] on success (>=2 sub-blobs
    found), or None if no delta separates it -- caller keeps the original
    single wide blob in that case."""
    for delta in _SPLIT_DELTAS:
        _, split_thresh = cv2.threshold(gray, HDR_THRESH - delta, 255, cv2.THRESH_BINARY_INV)
        sub = split_thresh[y:y + h, x:x + w]
        cnts, _ = cv2.findContours(sub, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        sub_boxes = []
        for c in cnts:
            sx, sy, sw, sh = cv2.boundingRect(c)
            if sw >= _SPLIT_MIN_W and sh >= _SPLIT_MIN_H:
                sub_boxes.append((x + sx, y + sy, sw, sh))
        if len(sub_boxes) >= 2:
            sub_boxes.sort(key=lambda b: b[0])
            return [(bx, by, bw, bh, split_thresh) for (bx, by, bw, bh) in sub_boxes]
    return None


def isolate_header_blobs(gray: np.ndarray) -> "list[np.ndarray]":
    """Return digit/K/M-shaped glyph crops (raw ink, 255=ink) for a header
    stats crop, left-to-right, using production's own fixed-threshold
    segmentation (HDR_THRESH=155) plus a merge-split pass for abnormally
    wide blobs (see _try_split_merged above)."""
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY) if gray.ndim == 3 else gray
    thresh = _binarize_hdr(gray)
    raw_blobs = _find_header_blobs(thresh)

    expanded = []  # [(x, y, w, h, source_thresh_image), ...]
    for (x, y, w, h) in raw_blobs:
        if w < MERGE_WIDTH_GATE:
            expanded.append((x, y, w, h, thresh))
            continue
        split = _try_split_merged(gray, x, y, w, h)
        expanded.extend(split if split is not None else [(x, y, w, h, thresh)])

    boxes = _drop_label_bleed(_filter_y_outliers([(x, y, w, h) for (x, y, w, h, _t) in expanded]))
    kept = {(x, y, w, h) for (x, y, w, h) in boxes}
    return [t[y:y + h, x:x + w] for (x, y, w, h, t) in expanded if (x, y, w, h) in kept]


# ── Calibration (gfl2/calibration/calibrate_header_dp.py writes this file;
# falls back to this hardcoded default if absent -- same pattern as every
# other dp-family engine) ───────────────────────────────────────────────────
_CALIB_DEFAULT = {
    "m_width_gate": 30.0,
    "iso_gate": {"lo": 0.40, "hi": 0.92},
    "k_left_gate": {"width": 2, "gate": 10.0},
    "top_band_4": {"p0": 0.53, "p1": 0.76, "gate": 20.0},
    "top_band_7": {"height": 2, "gate": 15.0},
    "spread_x_3_gate": 4.0,
    "bottom_band_25": {"height": 1, "gate": 8.0},
    "circular_centroids": {
        "0": [0.40, 0.40, 0.0, 0.0],
        "6": [0.15, 0.10, 0.05, 0.20],
        "9": [0.10, 0.15, 0.20, -0.05],
    },
}


def _load_calib() -> dict:
    merged = {k: (dict(v) if isinstance(v, dict) else v) for k, v in _CALIB_DEFAULT.items()}
    if _CALIB_F.exists():
        calib = json.loads(_CALIB_F.read_text(encoding="utf-8"))
        for k, v in calib.items():
            if isinstance(v, dict) and isinstance(merged.get(k), dict):
                merged[k].update(v)
            else:
                merged[k] = v
    return merged


_CALIB = _load_calib()


# ── M GATE: width alone (copied convention, new mechanism) ──────────────
# M is the widest glyph in this font's whole character set by a wide margin
# (three strokes side by side vs. a digit's single/double stroke) -- a
# corpus-validated one-shot gate on raw glyph width, no sweep needed (see
# gfl2/calibration/calibrate_header_dp.py's calibrate_m_width_gate).
M_WIDTH_GATE = _CALIB["m_width_gate"]


def _glyph_width(crop: np.ndarray) -> int:
    return int(crop.shape[1])


# ── ROOT GATE: isoperimetric ratio (copied from gfl2.stat_ocr_dp) ──────────
ISO_GATE_LO = _CALIB["iso_gate"]["lo"]
ISO_GATE_HI = _CALIB["iso_gate"]["hi"]


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


# ── Paren / loop cross-correlation templates (copied from gfl2.stat_ocr_dp,
# itself copied from gfl2/stat_ocr_fft.py) -- whole-glyph normalized cross-
# correlation against hand-drawn curve templates, no FFT/kernel involved.
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


# ── Reflex-vertex spread (copied from gfl2.stat_ocr_dp) ─────────────────────
SPREAD_EPS = 0.03
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


def _spread_x(reflex_pts: "np.ndarray | None") -> float:
    if reflex_pts is None or len(reflex_pts) == 0:
        return 0.0
    return float(reflex_pts[:, 0].max() - reflex_pts[:, 0].min())


# ── Top/left-band ink count (top-band copied from gfl2.stat_ocr_dp; left-band
# is this module's OWN new primitive for K -- see module docstring) ────────
def _band_count(gray_norm: np.ndarray, y0: int, y1: int) -> int:
    """Count of non-zero (ink) pixels in rows [y0, y1) (exclusive), full
    width."""
    return int(cv2.countNonZero(gray_norm[y0:y1, :]))


def _band_count_left(gray_norm: np.ndarray, x0: int, x1: int) -> int:
    """Count of non-zero (ink) pixels in columns [x0, x1) (exclusive), full
    height -- the horizontal-band counterpart to _band_count, transposed
    from rows to columns. Column 0 is, by construction of cv2.boundingRect,
    always the glyph's own leftmost ink column. Used ONLY for the K gate:
    K's leftmost stroke is a solid near-full-height vertical bar, unlike any
    other char in this font's set (see K_LEFT_GATE below)."""
    return int(cv2.countNonZero(gray_norm[:, x0:x1]))


K_LEFT_WIDTH = _CALIB["k_left_gate"]["width"]
K_LEFT_GATE = _CALIB["k_left_gate"]["gate"]

TOP_BAND_7_HEIGHT = _CALIB["top_band_7"]["height"]
TOP_BAND_7_GATE = _CALIB["top_band_7"]["gate"]

TOP_BAND_4_P0 = _CALIB["top_band_4"]["p0"]
TOP_BAND_4_P1 = _CALIB["top_band_4"]["p1"]
TOP_BAND_4_GATE = _CALIB["top_band_4"]["gate"]


def _band_count_proportional(crop: np.ndarray, p0: float, p1: float) -> int:
    """Ink count over rows [round(p0*h), round(p1*h)) of the glyph's OWN
    height h -- see gfl2.stat_ocr_dp's TOP_BAND_4 for why a proportion, not
    an absolute row range, generalizes across genuinely different crop
    sizes."""
    h = crop.shape[0]
    y0, y1 = int(round(p0 * h)), int(round(p1 * h))
    return _band_count(crop, y0, max(y0 + 1, y1))


SPREAD_X_3_GATE = _CALIB["spread_x_3_gate"]

BOTTOM_BAND_25_HEIGHT = _CALIB["bottom_band_25"]["height"]
BOTTOM_BAND_25_GATE = _CALIB["bottom_band_25"]["gate"]


def _bottom_band_count(crop: np.ndarray, height: int) -> int:
    """Ink count over the LAST `height` rows of the glyph's own tight
    crop."""
    ch = crop.shape[0]
    return _band_count(crop, max(0, ch - height), ch)


# ── Glyph extraction -- NO normalization ─────────────────────────────────
def _extract_header_digit_glyphs(gray: np.ndarray, label: str) -> "list[tuple[np.ndarray, str]] | None":
    """Training/verify-time (label-aligned) glyph extraction. Returns
    [(raw_tight_crop, char), ...] or None if the blob count doesn't match
    `label`'s expected TRAIN_CHARS count -- same skip-don't-guess convention
    as every other dp-family engine. Uses isolate_header_blobs() -- the same
    segmentation (including the merge-split pass) that inference uses -- so
    training/verify glyphs never drift from what read_stat() actually sees."""
    expected = [c for c in label if c in TRAIN_CHARS]
    if not expected:
        return None
    crops = isolate_header_blobs(gray)
    if len(crops) != len(expected):
        return None
    glyphs = []
    for crop, ch in zip(crops, expected):
        if crop.size == 0:
            return None
        glyphs.append((crop, ch))
    return glyphs


# ── Classify tree ────────────────────────────────────────────────────────────
def classify_header(crop: np.ndarray, circular_centroids: dict) -> str:
    """Full classify tree for a single header-stats glyph. `crop` is the
    glyph's RAW tight crop from isolate_header_blobs's thresholded image --
    no normalization of any kind.

    TREE:
      M gate (raw glyph width -- see module docstring) -- checked FIRST,
      before anything else is computed at all.
      +-- width >= M_WIDTH_GATE -> 'M' (categorical)
      else: isoperimetric ratio (root)
        +-- circular ({0,6,8,9} likely): inner-blob hole count
        |     +-- holes>=2 -> '8'
        |     +-- holes==1 -> {0,6,9} via paren+loop nearest-of-3
        |     +-- holes==0 -> '?' (defensive, unexpected)
        +-- non-circular ({1,2,3,4,5,7,K} likely):
              +-- K gate (left-band ink count -- see module docstring)
              |     FIRST, before '4' or any reflex-vertex work.
              +-- '4' gate (top-band proportional ink count, same
              |     mechanism as gfl2.stat_ocr_dp's own TOP_BAND_4).
              +-- else: spread_y splits {1,7} from {2,3,5}
                    +-- {1,7}: top-band ink count -- '7' vs '1'
                    +-- {2,3,5}: spread_x isolates '3' FIRST (near-zero,
                          the SAME grouping gfl2.score_ocr_dp.py found for
                          the score font, not the pct-line engine's own
                          '5' vs {2,3} pairing -- measured directly for
                          this font, see gfl2/calibration/
                          calibrate_header_dp.py). Remaining {2,5} splits
                          via a bottom-anchored ink count.
    """
    if _glyph_width(crop) >= M_WIDTH_GATE:
        return 'M'

    iso = _isoperimetric_ratio(crop)
    if ISO_GATE_LO <= iso <= ISO_GATE_HI:
        holes = _count_inner_blobs(crop)
        if holes >= 2:
            return '8'
        if holes == 1:
            combined = np.concatenate([_paren_features(crop), _loop_features(crop)])
            best_d, best_dist = None, None
            for d, centroid in circular_centroids.items():
                dist = float(np.linalg.norm(combined - centroid))
                if best_dist is None or dist < best_dist:
                    best_d, best_dist = d, dist
            return best_d if best_d is not None else '?'
        return '?'  # holes==0 but iso_gate said circular -- defensive, unexpected

    # non-circular: K gate FIRST, before '4' or any reflex-vertex work at all.
    if _band_count_left(crop, 0, K_LEFT_WIDTH) >= K_LEFT_GATE:
        return 'K'

    if _band_count_proportional(crop, TOP_BAND_4_P0, TOP_BAND_4_P1) >= TOP_BAND_4_GATE:
        return '4'

    reflex_pts, _ = _reflex_vertices(crop)
    sy = _spread_y(reflex_pts)
    if sy <= SPREAD_Y_THRESHOLD:
        # {1,7}
        top = _band_count(crop, 0, TOP_BAND_7_HEIGHT)
        return '7' if top >= TOP_BAND_7_GATE else '1'

    # {2,3,5}: spread_x isolates '3' FIRST (near-zero on this font -- see
    # module docstring), then a bottom-band count splits the remaining {2,5}.
    sx = _spread_x(reflex_pts)
    if sx < SPREAD_X_3_GATE:
        return '3'
    bottom25 = _bottom_band_count(crop, BOTTOM_BAND_25_HEIGHT)
    return '2' if bottom25 >= BOTTOM_BAND_25_GATE else '5'


def _load_circular_centroids() -> dict:
    return {d: np.asarray(v, dtype=np.float64) for d, v in _CALIB["circular_centroids"].items()}


# ── Corpus crop collection (calibration/verify only) ────────────────────────
def _collect_header_crops(image_paths: "list[Path]") -> "list[dict]":
    """One entry per (panel, field) with a Tesseract-readable label:
    {"source", "gray", "label"}. Mirrors gfl2.patterns.daily_gunsmoke's
    _extract_header stats-row crop logic (STATS_DEALT_X/TAKEN_X/TURNS_X,
    frame-relative y-range) -- NOT imported from there (gfl2/ modules don't
    import from each other's engine-selection call sites; this stays
    self-contained except for layout constants and Tesseract GT, mirroring
    gfl2.score_ocr_dp's own _collect_score_crops precedent)."""
    from assets.builders.build import _tess_read
    from gfl2.patterns.daily_gunsmoke import (
        _split_panels, _find_frames,
        STATS_ROW_Y0_FR, STATS_ROW_Y1_FR,
        STATS_DEALT_X, STATS_TAKEN_X, STATS_TURNS_X,
    )

    _fields = [(STATS_DEALT_X, "dealt"), (STATS_TAKEN_X, "taken"), (STATS_TURNS_X, "turns")]
    samples = []
    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        for pi, panel in enumerate(_split_panels(img)):
            frames = _find_frames(panel)
            if not frames:
                continue
            ph, pw = panel.shape[:2]
            _, fy, _, fh = frames[0]
            sy0 = fy - int(fh * STATS_ROW_Y0_FR)
            sy1 = fy - int(fh * STATS_ROW_Y1_FR)
            for x_range, label in _fields:
                x0 = max(0, int(pw * x_range[0]))
                x1 = min(pw, int(pw * x_range[1]))
                crop = panel[sy0:sy1, x0:x1]
                if crop.size == 0:
                    continue
                gt = _tess_read(crop)
                expected = [c for c in gt if c in TRAIN_CHARS]
                if not expected:
                    continue
                gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop
                samples.append({
                    "source": f"{img_path.stem}_p{pi + 1}_{label}",
                    "gray": gray,
                    "label": gt,
                })
    return samples


# ── Public engine ─────────────────────────────────────────────────────────────
class HeaderOcrDp:
    """Daily Gunsmoke header-stats-row reader (dealt/taken/turns), injected
    via gfl2.patterns.daily_gunsmoke.parse(..., header_ocr=...) when
    `main.py --stat-ocr-engine dp` is selected. isolate_header_blobs()'s
    fixed-threshold segmentation (unchanged from production -- no known
    segmentation bug on this field) plus classify_header()'s dp-family
    classify tree -- see module docstring for the full design."""

    def __init__(self, circular_centroids: dict) -> None:
        self._circular_centroids = circular_centroids

    @classmethod
    def load(cls) -> "HeaderOcrDp":
        return cls(_load_circular_centroids())

    def read_stat(self, gray: np.ndarray, return_partial: bool = False) -> "str | None":
        """Same contract as gfl2.patterns.daily_gunsmoke._read_stat_crop:
        returns a string (e.g. "4635", "2263K"), or None if no blobs were
        found. If any glyph is unclassifiable, classify_header() marks it
        '?' -- with return_partial=True the '?'-containing string is
        returned as-is; with return_partial=False (the default) a
        '?'-containing result collapses to None. No internal Tesseract
        fallback runs here -- daily_gunsmoke.py's own existing,
        unconditional external Tesseract stats-row fallback is what
        actually recovers a None/partial result, unchanged by this
        module."""
        if gray.size == 0:
            return None
        glyphs = isolate_header_blobs(gray)
        if not glyphs:
            return None
        parts = [classify_header(g, self._circular_centroids) for g in glyphs]
        result = ''.join(parts)
        if not result:
            return None
        if '?' in result and not return_partial:
            return None
        return result


# ── Benchmark / verification ────────────────────────────────────────────────
def verify(image_paths: "list[Path]", verbose: bool = True) -> dict:
    """Whole-field-level: compare against Tesseract ground truth, same
    contract as gfl2.score_ocr_dp.verify()."""
    run_start = datetime.now().isoformat(timespec="seconds")
    engine = HeaderOcrDp.load()
    samples = _collect_header_crops(image_paths)

    total = match = miss = 0
    mismatches = []
    classify_times = []
    for item in samples:
        t0 = time.perf_counter()
        got = engine.read_stat(item["gray"], return_partial=True)
        classify_times.append(time.perf_counter() - t0)
        total += 1
        if got is None or '?' in got:
            miss += 1
            mismatches.append((item["source"], item["label"], got))
        elif got != item["label"]:
            mismatches.append((item["source"], item["label"], got))
        else:
            match += 1

    mean_us = statistics.mean(classify_times) * 1e6 if classify_times else 0.0
    stdev_us = statistics.pstdev(classify_times) * 1e6 if len(classify_times) > 1 else 0.0
    cv_ = (stdev_us / mean_us) if mean_us else 0.0

    if verbose:
        def pct_str(n, d): return f"{100*n/d:.1f}%" if d else "n/a"
        print(f"\n{'-'*60}")
        print(f"Generated: {run_start}  (run start)")
        print(f"HeaderOcrDp verify  ({len(image_paths)} images, {total} fields)")
        print(f"  field  {match}/{total} correct  ({pct_str(match, total)})  {miss} no-read/uncertain")
        print(f"  timing  mean={mean_us:.1f}us/field  stdev={stdev_us:.1f}us  cv={cv_:.2f}  (n={len(classify_times)})")
        if mismatches:
            print(f"\nFirst 20 mismatches:")
            for source, exp, got in mismatches[:20]:
                print(f"  {source}  expected={exp!r}  got={got!r}")
        print(f"{'-'*60}")

    return {"total": total, "match": match, "miss": miss,
             "mismatches": mismatches, "mean_us": mean_us, "stdev_us": stdev_us, "cv": cv_}


def verify_glyphs(image_paths: "list[Path]", verbose: bool = True) -> dict:
    """Glyph-level: classify every individual labelled header-stat digit/K/M
    and tally classified/correct/misclassified/unknown PER CHAR."""
    run_start = datetime.now().isoformat(timespec="seconds")
    engine = HeaderOcrDp.load()
    samples = _collect_header_crops(image_paths)

    per_char = {d: {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0}
                for d in TRAIN_CHARS}
    classify_times = []
    for item in samples:
        glyphs = _extract_header_digit_glyphs(item["gray"], item["label"])
        if glyphs is None:
            continue
        for crop, true_label in glyphs:
            bucket = per_char.setdefault(
                true_label, {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0})
            t0 = time.perf_counter()
            pred = classify_header(crop, engine._circular_centroids)
            classify_times.append(time.perf_counter() - t0)
            bucket["classified"] += 1
            if pred == '?':
                bucket["unknown"] += 1
            elif pred == true_label:
                bucket["correct"] += 1
            else:
                bucket["misclassified"] += 1

    totals = {k: sum(per_char[d][k] for d in per_char)
              for k in ("classified", "correct", "misclassified", "unknown")}
    mean_us = statistics.mean(classify_times) * 1e6 if classify_times else 0.0
    stdev_us = statistics.pstdev(classify_times) * 1e6 if len(classify_times) > 1 else 0.0
    cv_ = (stdev_us / mean_us) if mean_us else 0.0

    if verbose:
        print(f"\n{'-'*60}")
        print(f"Generated: {run_start}  (run start)")
        print(f"HeaderOcrDp verify_glyphs  ({len(image_paths)} images, {totals['classified']} glyphs)")
        print(f"{'char':>6} {'classified':>10} {'correct':>8} {'misclassified':>13} {'unknown':>8}")
        for d in TRAIN_CHARS:
            b = per_char[d]
            print(f"{d:>6} {b['classified']:>10} {b['correct']:>8} {b['misclassified']:>13} {b['unknown']:>8}")
        acc = totals['correct'] / totals['classified'] if totals['classified'] else 0.0
        print(f"{'TOTAL':>6} {totals['classified']:>10} {totals['correct']:>8} "
              f"{totals['misclassified']:>13} {totals['unknown']:>8}  ({100*acc:.1f}% correct)")
        print(f"  timing  mean={mean_us:.1f}us/glyph  stdev={stdev_us:.1f}us  cv={cv_:.2f}  (n={len(classify_times)} glyphs)")
        print(f"{'-'*60}")

    return {"per_char": per_char, "totals": totals, "mean_us": mean_us, "stdev_us": stdev_us, "cv": cv_}


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--verify-glyphs", dest="verify_glyphs", action="store_true")
    args = ap.parse_args(argv)

    if not args.verify and not args.verify_glyphs:
        ap.print_help()
        sys.exit(1)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images) if "debug" not in Path(p).stem)
    if not image_paths:
        print(f"No images matched: {args.images}", file=sys.stderr)
        sys.exit(1)
    print(f"Images: {len(image_paths)}")

    if args.verify:
        verify(image_paths, verbose=True)
    if args.verify_glyphs:
        verify_glyphs(image_paths, verbose=True)


if __name__ == "__main__":
    main()
