# -*- coding: utf-8 -*-
"""
gfl2/score_ocr_v0_3_0.py -- Daily Gunsmoke header-score reader, multi-Otsu
adaptive-threshold segmentation PLUS a real "v0_3_0-family" classify_score()
tree (docs/decisions.txt #85-#87) -- no longer a
segmentation-only stub.

BACKGROUND: gfl2/patterns/daily_gunsmoke.py's shared score pipeline
(score_ocr.THRESH_VAL=150 + an escalating +5/+10/+15/+20-delta ladder,
gfl2.extraction.score.isolate_score_blobs_legacy) can silently DROP an
adjacent identical-digit pair
(e.g. "44") -- the ladder stops at the FIRST delta whose blob count
increases at all, which can reflect an unrelated partial separation
elsewhere in the crop rather than the genuinely merged pair splitting.
Confirmed via a live parse() call: single/fb_d_20251019.png panel 2's real
score "4407" reads back as "07", with no '?' marker anywhere to flag the
loss. Corpus-wide, at least 10 of 20 score/Tesseract mismatches across
single/*.png share this exact signature.

A per-crop multi-level (3-class) Otsu threshold -- copied (not imported;
see WHY COPIED below) from gfl2.stat_ocr_v0_3_0._multi_otsu_2thresh, which has
the full algorithm derivation -- correctly isolates all digit blobs in
156/157 score crops in single/*.png (the one exception, gm_d_20250908.png,
is the corpus's own known different-capture-resolution outlier,
known_issues.txt §18 -- NOT solved by this alone; see §33's caveat that
this direction is not a complete cross-resolution fix).

CLASSIFICATION: score_digits.py's
templates were trained on glyphs extracted at score_ocr.THRESH_VAL=150 --
a matched, mutually-consistent pair with that fixed threshold, even though
150 itself is not derived from anything principled (known_issues.txt
§33's ATTEMPTED, THEN REVERTED entry: reusing score_digits.py against
THIS module's adaptive-threshold segmentation net-REGRESSED accuracy,
68 regressed vs. 7 fixed out of 88 changed reads). Rather than re-attempt
that mismatch, this module now carries its OWN classify_score() tree --
copied from gfl2/stat_ocr_v0_3_0.py's mostly-spatial-domain nearest-centroid
design (isoperimetric ratio root gate, hole-count + paren/loop centroids
for the circular leaf, proportional/absolute ink-count band gates and
reflex-vertex spread for the non-circular leaves) and recalibrated on
THIS module's own adaptive-threshold glyph representation via
gfl2/calibration/calibrate_score_v0_3_0.py, exactly mirroring gfl2/
calibration/calibrate_v0_3_0.py's own "write everything twice, don't let
reuse become inertia" precedent for the pct-line engine. NO internal
Tesseract fallback tier of any kind (no Hu-moment second pass, unlike
production's score_ocr.py) -- every leaf either decides or abstains to
'?' directly, matching gfl2/stat_ocr_v0_3_0.py's own classify() philosophy.
This engine has the SAME acknowledged scarcity of abstention paths as
that one (docs/action_items.txt #28) -- most leaves always answer.
daily_gunsmoke.py's EXISTING, unconditional, unrelated external Tesseract
score fallback is untouched by any of this and still fires whenever
read_score() returns a string containing '?' (or None) -- see
read_score()'s own docstring for the exact contract.

WHY COPIED, NOT IMPORTED: this module and gfl2/stat_ocr_v0_3_0.py are peer
"v0_3_0-family" exploratory modules (both MIXED scope, both reachable via
`main.py --stat-ocr-engine v0_3_0`) -- gfl2/patterns/daily_gunsmoke.py (MAIN)
must not depend on either of them (main.py alone picks concrete engine
classes; daily_gunsmoke.py stays engine-agnostic, see parse()'s own
docstring), and this module avoids a peer-to-peer import for the same
"write it twice rather than couple two independent exploratory engines"
reason gfl2/stat_ocr_v0_3_0.py itself was built by copying out of
gfl2/stat_ocr_v0_2_0.py (decisions.txt #75). Every generic spatial-feature
function below (isoperimetric ratio, paren/loop templates, reflex-vertex
spread, band-ink-count helpers) is therefore a COPY of gfl2/
stat_ocr_v0_3_0.py's own copy, not an import -- the SCORE font's own
calibrated gate constants (a separate corpus, a separate ink polarity,
different absolute pixel scale) live in a separate config file
(gfl2/configs/daily_score_v0_3_0_calib.json) and are never shared with the
pct-line engine's gfl2/configs/daily_pct_v0_3_0_calib.json.

CORPUS, NOT ATLAS, FOR CALIBRATION: assets/fonts/glyph_daily_score.png (one
real sample per digit, docs/action_items.txt #12, decisions.txt #84)
is a legitimate reference for eyeballing this font's glyph shapes, but
this module's calibration (gfl2/calibration/calibrate_score_v0_3_0.py) derives
every gate constant from the REAL multi-image corpus (single/*.png's own
medal-anchored score crops, matching debugs/build_glyph_reference.py's
own crop-finding logic) rather than that single-sample atlas --
known_issues.txt §27/decisions.txt #70 already established that an
interval-style gate derived from n=1 can look clean in isolation while
still misrouting real corpus glyphs whose within-class spread a single
sample cannot represent; every constant this tree needs (iso_gate,
top_band_4/5/7, spread_x_5_gate, bottom_band_23) is exactly that kind of
interval, not a plain centroid, so corpus mode is not optional here the
way it was an upgrade for gfl2/stat_ocr_v0_3_0.py's own pct calibration.

SELECTION: `main.py --stat-ocr-engine v0_3_0` constructs a ScoreOcrV0_3_0
alongside gfl2.stat_ocr_v0_3_0.StatOcrV0_3_0 and injects it into
gfl2.patterns.daily_gunsmoke.parse(..., score_ocr=...). Every other
--stat-ocr-engine selection (v0_1_0, v0_1_1, v0_2_0) leaves score_ocr=None,
which keeps daily_gunsmoke.py's original score pipeline completely
unchanged -- confirmed byte-identical (known_issues.txt §33).

Usage:
    python -m gfl2.score_ocr_v0_3_0 --verify --images "single/*.png"
    python -m gfl2.score_ocr_v0_3_0 --verify-glyphs --images "single/*.png"
    python -m gfl2.calibration.calibrate_score_v0_3_0 --images "single/*.png"  # recalibrate
"""
from __future__ import annotations
import glob as _glob
import json
import statistics
import sys
import time
from contextlib import nullcontext as _nullctx
from datetime import datetime
from pathlib import Path
from typing import Optional

from gfl2.timing import inject_branch_spans

import cv2
import numpy as np

from gfl2.score_ocr import DIGIT_MIN_W, DIGIT_MAX_W, DIGIT_MIN_H, DIGIT_MAX_H
from gfl2.stat_ocr_v0_1_0 import _count_inner_blobs

_HERE = Path(__file__).parent.parent
_CALIB_F = _HERE / "gfl2" / "configs" / "daily_score_v0_3_0_calib.json"

TRAIN_CHARS = list("0123456789")


# ── Multi-Otsu adaptive threshold (copied from gfl2.stat_ocr_v0_3_0, see WHY
# COPIED above) ──────────────────────────────────────────────────────────
def _multi_otsu_2thresh(gray: np.ndarray) -> "tuple[int, int]":
    """Fast 3-class Otsu thresholding (Liao, Chen & Chung, 2001) via
    cumulative histogram zeroth/first-order moments -- O(256^2) candidate
    (t1, t2) pairs instead of the naive O(256^3) recomputation. Returns
    (t1, t2): t1 is the boundary between the darkest class and the middle
    class; t2 is the boundary between the middle class and the brightest
    class. Copied verbatim from gfl2.stat_ocr_v0_3_0._multi_otsu_2thresh --
    see this module's own docstring (WHY COPIED) for why, and that
    function's docstring for the algorithm citation."""
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    total = float(hist.sum())
    if total <= 0:
        return 128, 128
    p = hist / total
    idx = np.arange(256, dtype=np.float64)
    cum_p0 = np.cumsum(p)
    cum_p1 = np.cumsum(idx * p)

    def _sigma(a: int, b: int) -> float:
        w = cum_p0[b] - (cum_p0[a - 1] if a > 0 else 0.0)
        if w <= 1e-12:
            return 0.0
        mu = cum_p1[b] - (cum_p1[a - 1] if a > 0 else 0.0)
        return (mu * mu) / w

    best_var, best_t1, best_t2 = -1.0, 0, 1
    for t1 in range(0, 254):
        s01 = _sigma(0, t1)
        for t2 in range(t1 + 1, 255):
            between_var = s01 + _sigma(t1 + 1, t2) + _sigma(t2 + 1, 255)
            if between_var > best_var:
                best_var, best_t1, best_t2 = between_var, t1, t2
    return best_t1, best_t2


def _score_otsu_threshold(gray: np.ndarray) -> int:
    """t2 -- the ink-halo/background boundary -- because Daily Gunsmoke's
    header-bar score text is BRIGHT-on-DARK, the opposite ink polarity
    from gfl2.stat_ocr_v0_3_0's dark-on-light pct strips (where t1, the
    darker ink/halo boundary, is the useful one). Recomputed fresh per
    crop, never cached: known_issues.txt §32/decisions.txt #83 already
    found a per-run-shared threshold cache can let one image's value leak
    into another's read -- recomputing per crop (O(256^2), a few ms) is
    cheap enough here (called once or twice per image) to just avoid that
    whole failure class outright."""
    _t1, t2 = _multi_otsu_2thresh(gray)
    return t2


def _binarize_score_adaptive(gray: np.ndarray) -> np.ndarray:
    """THRESH_BINARY (not INV -- score ink is bright-on-dark already, see
    _score_otsu_threshold) at this crop's own adaptive threshold."""
    t = _score_otsu_threshold(gray)
    _, thresh = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)
    return thresh


def _isolate_score_blobs_from_thresh(thresh: np.ndarray) -> "list[tuple[int, int, int, int]]":
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if DIGIT_MIN_W <= w <= DIGIT_MAX_W and DIGIT_MIN_H <= h <= DIGIT_MAX_H:
            blobs.append((x, y, w, h))
    blobs.sort(key=lambda b: b[0])
    return blobs


def isolate_score_blobs(gray: np.ndarray) -> "list[tuple[int, int, int, int]]":
    """Return digit-shaped (x, y, w, h) blobs for a score crop, sorted
    left-to-right, using this module's per-crop adaptive threshold instead
    of daily_gunsmoke.py's fixed-THRESH_VAL escalating-delta ladder.
    Corpus-validated (known_issues.txt §33): blob count matches Tesseract
    ground-truth digit-string length for 156/157 score crops in
    single/*.png, including every "adjacent-44-dropped" case the fixed
    ladder is known to miss. The one exception, gm_d_20250908.png, is the
    corpus's own already-tracked different-resolution outlier (§18)."""
    return _isolate_score_blobs_from_thresh(_binarize_score_adaptive(gray))


# ── Calibration (gfl2/calibration/calibrate_score_v0_3_0.py writes this file --
# corpus-derived, not atlas-derived, for every interval-style gate; see this
# module's own docstring's CORPUS, NOT ATLAS section). Falls back to the
# last-calibrated hardcoded values below if the config file is absent --
# same pattern as gfl2/stat_ocr_v0_3_0.py's daily_pct_v0_3_0_calib.json.
_CALIB_DEFAULT = {
    "iso_gate": {"lo": 0.3667, "hi": 0.8873},
    "top_band_4": {"p0": 0.54, "p1": 0.73, "gate": 15.5},
    "top_band_7": {"height": 1, "gate": 6.5},
    "spread_x_3_gate": 4.0,
    "bottom_band_25": {"height": 1, "gate": 9.0},
    "circular_centroids": {
        "0": [0.4148, 0.3691, 0.0014, -0.0172],
        "6": [0.203, 0.1116, 0.0321, 0.2449],
        "9": [0.1107, 0.1193, 0.2939, -0.0359],
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


# ── ROOT GATE: isoperimetric ratio (copied from gfl2.stat_ocr_v0_3_0) ──────────
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


# ── Paren / loop cross-correlation templates (copied from gfl2.stat_ocr_v0_3_0,
# itself copied from gfl2/stat_ocr_v0_2_0.py) -- whole-glyph normalized cross-
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


# ── Reflex-vertex spread (copied from gfl2.stat_ocr_v0_3_0) ─────────────────────
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
    """Horizontal counterpart to _spread_y -- same reflex/concave contour
    points (already computed for the {1,7}-vs-{2,3,5} split), just the
    x-axis extent instead of the y-axis one. See gfl2.stat_ocr_v0_3_0's own
    docstring for this feature -- identical mechanism, own SCORE_*
    calibrated gate below."""
    if reflex_pts is None or len(reflex_pts) == 0:
        return 0.0
    return float(reflex_pts[:, 0].max() - reflex_pts[:, 0].min())


# ── Top/bottom-band ink count (copied from gfl2.stat_ocr_v0_3_0) ────────────────
def _band_count(gray_norm: np.ndarray, y0: int, y1: int) -> int:
    """Count of non-zero (ink) pixels in rows [y0, y1) (exclusive), full
    width. `gray_norm` is the RAW tight crop (no padding at all) -- row 0
    is, by construction of cv2.boundingRect, always the glyph's own first
    ink row."""
    return int(cv2.countNonZero(gray_norm[y0:y1, :]))


TOP_BAND_7_HEIGHT = _CALIB["top_band_7"]["height"]
TOP_BAND_7_GATE = _CALIB["top_band_7"]["gate"]

TOP_BAND_4_P0 = _CALIB["top_band_4"]["p0"]
TOP_BAND_4_P1 = _CALIB["top_band_4"]["p1"]
TOP_BAND_4_GATE = _CALIB["top_band_4"]["gate"]


def _band_count_proportional(crop: np.ndarray, p0: float, p1: float) -> int:
    """Ink count over rows [round(p0*h), round(p1*h)) of the glyph's OWN
    height h -- see gfl2.stat_ocr_v0_3_0's TOP_BAND_4 for why a proportion,
    not an absolute row range, generalizes across genuinely different crop
    sizes (this module's score font renders at its own, different scale
    from the pct-line font, hence its own separately-calibrated p0/p1)."""
    h = crop.shape[0]
    y0, y1 = int(round(p0 * h)), int(round(p1 * h))
    return _band_count(crop, y0, max(y0 + 1, y1))


# '3' vs {2,5}: unlike the pct-line engine (where spread_x isolates '5'
# from {2,3}), THIS font's spread_x isolates '3' (low, near-straight
# contour) from {2,5} (both render with a genuine reflex corner spread
# horizontally) -- measured directly on the real corpus, not assumed by
# analogy: '3' spread_x in [0,3], {2,5} spread_x in [5,7], a real 2-unit
# gap. Digit shapes differ enough between the pct and score fonts that
# the SAME feature ends up discriminating a DIFFERENT pair -- see
# gfl2/calibration/calibrate_score_v0_3_0.py's own derivation notes.
SPREAD_X_3_GATE = _CALIB["spread_x_3_gate"]

# '2' vs '5' (spread_x said "not 3"): a BOTTOM-anchored ink count, same
# mechanism as the pct engine's '2'/'3' split -- '2' has a full flat
# bottom foot (high, constant count), '5' curls inward at the bottom
# (lower, more variable count). Real corpus gap: '2'=11 (constant),
# '5' in [5,7] -- a 4-unit gap, the cleanest split in this whole tree.
BOTTOM_BAND_25_HEIGHT = _CALIB["bottom_band_25"]["height"]
BOTTOM_BAND_25_GATE = _CALIB["bottom_band_25"]["gate"]


def _bottom_band_count(crop: np.ndarray, height: int) -> int:
    """Ink count over the LAST `height` rows of the glyph's own tight
    crop -- mirrors _band_count's top-anchored convention but anchored to
    the glyph's own bottom edge instead."""
    ch = crop.shape[0]
    return _band_count(crop, max(0, ch - height), ch)


# ── Classify tree (same shape as gfl2.stat_ocr_v0_3_0.classify(), SCORE's own
# calibrated gates) ──────────────────────────────────────────────────────────
def classify_score(crop: np.ndarray, circular_centroids: dict,
                   branch_acc: "dict[str, list[float]] | None" = None) -> str:
    """Full classify tree for a single score digit glyph -- see gfl2/
    stat_ocr_v0_3_0.py's module docstring for the identically-shaped tree
    diagram (isoperimetric ratio root -> circular hole-count/paren+loop
    leaf, or non-circular '4'-gate-first -> spread_y -> {1,7} top-band /
    {2,3,5} spread_x+top-band/bottom-band leaves). `crop` is the glyph's
    RAW tight crop from _binarize_score_adaptive's thresholded image -- no
    normalization of any kind, matching gfl2.stat_ocr_v0_3_0's own design.
    NO internal Tesseract fallback of any kind -- every leaf either
    decides or abstains to '?' directly (see module docstring).

    branch_acc: optional {branch_name: [elapsed_s, ...]} accumulator, same
      convention as gfl2.stat_ocr_v0_3_0.classify() -- lets a
      pipeline_summary/report tree show which leaf of THIS tree dominates
      real corpus time, not just this function's own aggregate mean
      (known_issues.txt §41, decisions.txt #104)."""
    _bt0 = time.perf_counter() if branch_acc is not None else 0.0

    def _rec(branch_name: str, result: str) -> str:
        if branch_acc is not None:
            branch_acc.setdefault(branch_name, []).append(time.perf_counter() - _bt0)
        return result

    iso = _isoperimetric_ratio(crop)
    if ISO_GATE_LO <= iso <= ISO_GATE_HI:
        holes = _count_inner_blobs(crop)
        if holes >= 2:
            return _rec("circular_8", '8')
        if holes == 1:
            combined = np.concatenate([_paren_features(crop), _loop_features(crop)])
            best_d, best_dist = None, None
            for d, centroid in circular_centroids.items():
                dist = float(np.linalg.norm(combined - centroid))
                if best_dist is None or dist < best_dist:
                    best_d, best_dist = d, dist
            return _rec("circular_069", best_d if best_d is not None else '?')
        return _rec("circular_holes0_unexpected", '?')  # defensive, unexpected

    # non-circular: '4' gate FIRST, before any reflex-vertex work at all.
    if _band_count_proportional(crop, TOP_BAND_4_P0, TOP_BAND_4_P1) >= TOP_BAND_4_GATE:
        return _rec("noncircular_4", '4')

    reflex_pts, _ = _reflex_vertices(crop)
    sy = _spread_y(reflex_pts)
    if sy <= SPREAD_Y_THRESHOLD:
        # {1,7}
        top = _band_count(crop, 0, TOP_BAND_7_HEIGHT)
        return _rec("concentrated_17", '7' if top >= TOP_BAND_7_GATE else '1')

    # {2,3,5}: spread_x isolates '3' FIRST (low, near-straight contour) --
    # NOTE this is the opposite pairing from gfl2.stat_ocr_v0_3_0's pct-line
    # tree, where spread_x isolates '5' from {2,3} instead; this SCORE
    # font's own '3' glyph renders with near-zero reflex-vertex spread
    # while both '2' and '5' spread wide, the reverse of the pct font's
    # shape (see SPREAD_X_3_GATE's own comment). Remaining {2,5} splits via
    # a bottom-anchored ink count -- '2' ends in a full-width flat foot
    # (high count), '5' curls inward (lower count).
    sx = _spread_x(reflex_pts)
    if sx < SPREAD_X_3_GATE:
        return _rec("spread_x_3", '3')
    bottom25 = _bottom_band_count(crop, BOTTOM_BAND_25_HEIGHT)
    return _rec("bottom_band_25", '2' if bottom25 >= BOTTOM_BAND_25_GATE else '5')


def _load_circular_centroids() -> dict:
    """{'0': np.array([paren_open, paren_close, loop_top, loop_bot]), '6':
    ..., '9': ...} -- loaded from _CALIB (gfl2/configs/
    daily_score_v0_3_0_calib.json, written by gfl2/calibration/
    calibrate_score_v0_3_0.py), this module's OWN corpus calibration."""
    return {d: np.asarray(v, dtype=np.float64) for d, v in _CALIB["circular_centroids"].items()}


# ── Label-aligned glyph extraction (training/calibration/verify) ───────────
def _extract_score_digit_glyphs(gray: np.ndarray, label: str) -> "list[tuple[np.ndarray, str]] | None":
    """Returns [(raw_tight_crop, digit_char), ...] or None if the adaptive-
    threshold blob count doesn't match `label`'s digit count -- same
    skip-don't-guess convention as gfl2.stat_ocr_v0_3_0._extract_pct_digit_glyphs."""
    expected = [c for c in label if c.isdigit()]
    if not expected:
        return None
    thresh = _binarize_score_adaptive(gray)
    blobs = _isolate_score_blobs_from_thresh(thresh)
    if len(blobs) != len(expected):
        return None
    glyphs = []
    for (x, y, w, h), ch in zip(blobs, expected):
        crop = thresh[y:y + h, x:x + w]
        if crop.size == 0:
            return None
        glyphs.append((crop, ch))
    return glyphs


def _collect_score_crops(image_paths: "list[Path]") -> "list[dict]":
    """One entry per panel with a Tesseract-readable score:
    {"source", "gray", "label"}. Mirrors debugs/build_glyph_reference.py's
    collect_daily_score_glyphs crop-finding logic (the exact medal-anchored
    header-bar score crop gfl2.patterns.daily_gunsmoke._extract_header's
    score section reads) -- NOT imported from there (gfl2/ modules don't
    import from debugs/, see gfl2/stat_ocr_v0_2_0.py's own precedent for this
    rule) -- but keeps the WHOLE crop (not per-digit blobs) so verify() can
    score whole-string accuracy the same way gfl2.stat_ocr_v0_3_0.verify() does
    for pct cells; per-digit bucketing is done separately by
    _extract_score_digit_glyphs()."""
    from assets.builders.build import _tess_read
    from gfl2.patterns.daily_gunsmoke import (
        _split_panels, _find_frames, _find_medal_right,
        HEADER_BAR_Y0, HEADER_BAR_Y1, SCORE_X0, SCORE_CROP_W_FR,
    )

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
            medal_right = _find_medal_right(panel)
            fw = frames[0][2]
            sc_y0 = int(ph * HEADER_BAR_Y0) + 3
            sc_y1 = int(ph * HEADER_BAR_Y1) - 3
            sc_x0 = ((medal_right + 2) if medal_right is not None else int(pw * SCORE_X0)) + 3
            sc_w = int(fw * SCORE_CROP_W_FR)
            crop = panel[sc_y0:sc_y1, sc_x0:min(sc_x0 + sc_w, pw)]
            if crop.size == 0:
                continue
            gt = _tess_read(crop)
            label = ''.join(c for c in gt if c.isdigit())
            if not label:
                continue
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop
            samples.append({
                "source": f"{img_path.stem}_p{pi + 1}_score",
                "gray": gray,
                "label": label,
            })
    return samples


# ── Public engine ─────────────────────────────────────────────────────────────
class ScoreOcrV0_3_0:
    """Daily Gunsmoke header-score reader, injected via
    gfl2.patterns.daily_gunsmoke.parse(..., score_ocr=...) when
    `main.py --stat-ocr-engine v0_3_0` is selected. isolate_score_blobs()'s
    adaptive-threshold segmentation plus classify_score()'s v0_3_0-family
    classify tree -- see module docstring for the full design."""

    def __init__(self, circular_centroids: dict) -> None:
        self._circular_centroids = circular_centroids

    @classmethod
    def load(cls) -> "ScoreOcrV0_3_0":
        return cls(_load_circular_centroids())

    def read_score(self, gray: np.ndarray, return_partial: bool = False,
                    timer=None) -> "str | None":
        """Same contract as gfl2.patterns.daily_gunsmoke._read_bright_number:
        returns a digit string (e.g. "4407"), or None if no blobs were
        found. If any glyph is unclassifiable, classify_score() marks it
        '?' -- with return_partial=True the '?'-containing string is
        returned as-is (so the caller can log/inspect the partial answer,
        exactly like _extract_header does for every other score path);
        with return_partial=False (the default) a '?'-containing result
        is collapsed to None instead. Either way, no internal Tesseract
        fallback runs here -- daily_gunsmoke.py's own existing,
        unconditional external Tesseract score fallback is what actually
        recovers a None/partial result, unchanged by this module.

        timer: optional TimerStack -- when provided, records score/binarize,
        score/blobs, score/classify sub-spans under the caller's active
        span, same convention as gfl2.stat_ocr_v0_3_0.StatOcrV0_3_0.read()
        (known_issues.txt §39). Added because this module's multi-Otsu
        binarization (_binarize_score_adaptive -> _multi_otsu_2thresh), UNLIKE
        gfl2.stat_ocr_v0_3_0's own _binarize_pct_adaptive, has NO cross-call
        threshold cache -- every single read_score() call re-derives the
        threshold from scratch -- so this span exists to measure, not
        assume, how much of this engine's real cost that is. score/classify
        additionally gains a "branch" child breaking down which
        classify_score() leaf each glyph took (circular_8, circular_069,
        noncircular_4, concentrated_17, spread_x_3, bottom_band_25,
        circular_holes0_unexpected) -- same mechanism as gfl2.stat_ocr_v0_3_0's
        own branch breakdown, added here so the report can show whether a
        given leaf's cost is worth its accuracy for THIS field specifically
        (known_issues.txt §41, decisions.txt #104)."""
        _t = timer.timed if timer is not None else _nullctx
        with _t("score/binarize"):
            thresh = _binarize_score_adaptive(gray)
        with _t("score/blobs"):
            blobs = _isolate_score_blobs_from_thresh(thresh)
        if not blobs:
            return None
        branch_acc: "dict[str, list[float]] | None" = {} if timer is not None else None
        with _t("score/classify") as classify_span:
            parts = [classify_score(thresh[y:y + h, x:x + w], self._circular_centroids,
                                     branch_acc=branch_acc)
                      for (x, y, w, h) in blobs]
        if timer is not None:
            inject_branch_spans(classify_span, branch_acc)
        result = ''.join(parts)
        if not result:
            return None
        if '?' in result and not return_partial:
            return None
        return result


# ── Benchmark / verification ────────────────────────────────────────────────
def verify(image_paths: "list[Path]", verbose: bool = True) -> dict:
    """Whole-score-level: compare against Tesseract ground truth, same
    contract as gfl2.stat_ocr_v0_3_0.verify()."""
    run_start = datetime.now().isoformat(timespec="seconds")
    engine = ScoreOcrV0_3_0.load()
    samples = _collect_score_crops(image_paths)

    total = match = miss = 0
    mismatches = []
    classify_times = []
    for item in samples:
        t0 = time.perf_counter()
        got = engine.read_score(item["gray"], return_partial=True)
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
        print(f"ScoreOcrV0_3_0 verify  ({len(image_paths)} images, {total} scores)")
        print(f"  score  {match}/{total} correct  ({pct_str(match, total)})  {miss} no-read/uncertain")
        print(f"  timing  mean={mean_us:.1f}us/score  stdev={stdev_us:.1f}us  cv={cv_:.2f}  (n={len(classify_times)})")
        if mismatches:
            print(f"\nFirst 20 mismatches:")
            for source, exp, got in mismatches[:20]:
                print(f"  {source}  expected={exp!r}  got={got!r}")
        print(f"{'-'*60}")

    return {"total": total, "match": match, "miss": miss,
            "mismatches": mismatches, "mean_us": mean_us, "stdev_us": stdev_us, "cv": cv_}


def verify_glyphs(image_paths: "list[Path]", verbose: bool = True) -> dict:
    """Glyph-level: classify every individual labelled score digit and
    tally classified/correct/misclassified/unknown PER DIGIT -- same
    contract as gfl2.stat_ocr_v0_3_0.verify_glyphs()."""
    run_start = datetime.now().isoformat(timespec="seconds")
    engine = ScoreOcrV0_3_0.load()
    samples = _collect_score_crops(image_paths)

    per_digit = {d: {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0}
                 for d in TRAIN_CHARS}
    classify_times = []
    for item in samples:
        glyphs = _extract_score_digit_glyphs(item["gray"], item["label"])
        if glyphs is None:
            continue
        for crop, true_label in glyphs:
            bucket = per_digit.setdefault(
                true_label, {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0})
            t0 = time.perf_counter()
            pred = classify_score(crop, engine._circular_centroids)
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
        print(f"ScoreOcrV0_3_0 verify_glyphs  ({len(image_paths)} images, {totals['classified']} glyphs)")
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
