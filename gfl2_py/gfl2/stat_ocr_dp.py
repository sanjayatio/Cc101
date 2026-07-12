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
everything downstream of it turned out to be replaceable with plain spatial
primitives too (contour geometry, ink counts, template correlation for the
circular leaf only), once "falling back to the spatial domain is
unavoidable" was accepted as the premise. The last two holdouts --
_hbar_features_sobel's merged-kernel Sobel-90 convolution and then a
paren_close cross-correlation template, both tried for the {2,3,5} leaf --
were each replaced in turn (see the SPREAD_X_5/BOTTOM_BAND_23 section
below) once a corpus-validated spatial substitute closed the gap; this
engine is now genuinely FFT-free and, outside the circular leaf's
paren+loop centroid lookup, template-free too.

TREE:
  isoperimetric ratio (contour geometry, ISO_GATE_LO/HI)
  +-- circular ({0,6,8,9} likely): inner-blob hole count
  |     +-- holes>=2 -> '8' (categorical)
  |     +-- holes==1 -> {0,6,9} via paren+loop nearest-of-3 (this engine's
  |     |               OWN corpus-derived centroids -- see NORMALIZATION
  |     |               below; no longer reused from another module)
  |     +-- holes==0 -> '?' (defensive; never hit on the real corpus)
  +-- non-circular ({1,2,3,4,5,7} likely):
        +-- '4' gate FIRST (top-band ink count over a PROPORTION of the
        |   glyph's own height -- p0/p1, TOP_BAND_4 section below):
        |   PERFECT on the real corpus (recall=1.0000, false_trigger=
        |   0.0000, real gap=14, held-out confirmed) -- replaces what used
        |   to be THREE separate rescue branches in stat_ocr_fft.py's
        |   spread_y tree with ONE upfront check. If it fires, done -- no
        |   reflex-vertex work, nothing else computed at all.
        +-- else: spread_y (reflex-vertex vertical spread) splits {1,7}
            (spread_y==0 always) from {2,3,5} (spread_y>=8 always) -- a
            PERFECT, wide (8-unit), trivial gap now that '4' (the only
            digit that ever contaminated this boundary) is already gone.
            +-- {1,7}: top-band ink count (height=2, near the very top)
            |     -- PERFECT (real gap=12) -- '7' vs '1'.
            +-- {2,3,5}: spread_x (the SAME reflex_pts already computed
                  for spread_y, just its x-axis extent -- free reuse, no
                  new contour work) -- '5' min=5.0, {2,3} max=4.0, a real
                  1-unit gap. Confirmed by a second top-band ink count
                  ('5' has a strong top bar, {2,3} don't; disagreement ->
                  '?' rather than trusting spread_x alone). Otherwise a
                  BOTTOM-anchored ink count ('2' ends in a full-width flat
                  foot, '3' curls inward) splits '2' from '3' -- '3'
                  max=9, '2' min=11, a real 2-unit gap. No paren/loop
                  template correlation anywhere in this leaf (that
                  mechanism is now used ONLY by the circular {0,6,9} leaf
                  above, where it remains load-bearing).

STATUS: pct-line AND val-line. The val-line gap (matching gfl2/
stat_ocr_fft.py's own no-op) is CLOSED -- see the VAL-LINE TREE section
below. Selectable via `main.py --stat-ocr-engine dp` (decisions.txt #78).

VAL-LINE TREE (added 2026-07-12): a SEPARATE tree from the pct-line one
above, not a parametrized reuse of it -- measured directly, not assumed by
analogy, and the measurements disagree with the pct tree's own design in
two structural ways:

  1. ROOT GATE IS HOLE COUNT, NOT ISOPERIMETRIC RATIO. The val font renders
     at a genuinely tiny native size (7-9 x 11-13px, vs the pct font's
     12-20px) -- at that scale, isoperimetric ratio (contour area/
     perimeter^2) does NOT cleanly separate {0,6,8,9} from the rest: the
     best Youden's-J threshold over the real corpus reaches only
     recall=0.9984/false_trigger=0.0033, not the clean zero-overlap gap
     the pct/header engines get. Hole count (_count_inner_blobs, already
     used one level down in every dp-family engine) is dramatically
     cleaner at this size: every digit's hole count matches its expected
     value (0 for {1,2,3,4,5,7}, 1 for {0,6,9}, 2 for {8}) in >=98.9% of
     real samples, with the residual almost entirely traceable to
     visually-confirmed Tesseract GT mislabels (e.g. a glyph shaped
     exactly like '8' -- two stacked loops, holes=2 -- labelled '5' or '3'
     by the GT; a glyph shaped exactly like '4' -- a diagonal into a full
     crossbar, holes=0 -- labelled '6'). Reflex-vertex spread_y (the
     {1,7}-vs-{2,3,5} split one level down) ALSO only separates cleanly
     once these same hole-count-contaminated samples are excluded --
     confirming the contamination is a GT-labelling issue, not a feature
     failure, the same category of finding as known_issues.txt #17/#32.

  2. '1' vs '7' IS A RAW WIDTH GATE, NOT A TOP-BAND INK COUNT. Every
     top-band-count height tried (matching TOP_BAND_7 above) gave a
     NEGATIVE gap ('1' had MORE top-row ink than '7', backwards from the
     pct font's own behavior) -- this font renders '1' with a small
     top-left serif flag that competes with '7's own top bar at this tiny
     resolution. Glyph WIDTH is what actually separates the pair cleanly:
     real corpus '1' renders at width 4-5px, '7' at width 7-8px (a small
     number of width-7/8 '1' samples and width-4/6 '7' samples are, on
     inspection, the exact same GT mislabels found above) -- a real,
     un-overlapping gap once those are excluded. WIDTH_17_GATE=6 sits
     in that gap. This is the SAME "isolate by raw glyph width alone"
     mechanism gfl2/header_ocr_dp.py already uses for M -- confirmed
     independently for a different digit pair on a different font here.

  The {2,3,5} leaf ALSO needed its own from-scratch derivation (spread_x,
  which cleanly separates this trio in the pct font, has NO separating
  power at all on this font -- every group's spread_x range overlaps
  heavily): '2' isolates via a BOTTOM-ROW-DEFICIT gate (glyph width minus
  its own last row's ink SPAN -- '2' ends in a flat, full-width stroke so
  the deficit is 0-1; {3,5} curl inward, deficit>=2), then '5' vs '3' via
  a TOP-LEFT-QUADRANT ink count ('5's flat top stroke starts further left
  than '3's right-open curves). Neither of these two features has been
  needed by any other dp-family engine before.

  Calibrated via gfl2/calibration/calibrate_val_dp.py (CORPUS-derived, same
  methodology as calibrate_dp.py) into gfl2/configs/daily_val_dp_calib.json
  -- own K-gate, top-band-4 gate, width-17 gate, deficit-2 gate,
  left-top-5 gate, and OWN circular {0,6,9} centroids (this font's paren/
  loop correlation values differ from the pct font's, per this project's
  "write everything twice" precedent). End-to-end corpus accuracy: 99.4%
  glyph-level (see that calibration script's own validation run for exact
  numbers) -- the residual is dominated by the same visually-confirmed
  GT-mislabel population described above, not classifier confusion.
  Like the pct tree, no confidence-based abstention exists on most leaves
  (action_items.txt #28's concern applies here identically) -- Tesseract
  fallback via `--stat-tess-fallback` remains available for cells this
  tree gets wrong.

VALIDATED (2026-07-11): every gate/split in this tree, INCLUDING the final
'2'/'5' split and the '0'/'6'/'9' centroids, now measures PERFECT
(recall=1.0000/false_trigger=0.0000, zero-overlap real corpus gap, or
already-100%-accuracy nearest-of-2/3) on the real single/*.png corpus
(6792 non-circular + 3535 circular glyphs). End-to-end validation of THIS
assembled engine is tracked separately (run --verify-glyphs) -- do not
assume the individual-piece numbers above compose to the same result
without checking; that composition IS checked by this module's own
verify_glyphs() run, not merely inferred.

NORMALIZATION (2026-07-11): THERE IS NONE. Earlier versions of this engine
reused NORM_W_PCT/NORM_H_PCT (a fixed 12x20 canvas, sized for
gfl2.stat_ocr's projection-correlation classifier, which genuinely needs
one) and gfl2/stat_ocr_fft.py's already-trained '0'/'6'/'9' centroids
(trained on that same fixed canvas). Neither reuse was load-bearing for
THIS engine -- every feature here (contour geometry, ink counts, template
correlation) sizes itself to whatever glyph it's given -- and reusing them
anyway meant this engine's accuracy was silently capped by a normalization
choice made for a DIFFERENT classifier's needs: 77.4% of real pct-line
glyphs in this corpus are wider than 12px (max 15px, action_items.txt
#19/known_issues.txt §27), so the shared canvas was center-cropping most
glyphs before any feature ever saw them. Every glyph is now used at its
own native, un-padded, un-cropped, un-resized tight-crop size -- the
extraction functions below return `thresh[y:y+h, x:x+w]` directly, nothing
else. Removing the shared canvas didn't just simplify the code, it
WIDENED every margin: '7' vs '1' top-band gap 3 (old, width=12) -> 12
(native); '4' vs everything else 1-unit (absolute canvas row range) -> 14
(measured as a PROPORTION of the glyph's own height instead). The
'0'/'6'/'9' centroids are now this engine's OWN, derived on this same
native representation by gfl2/calibration/calibrate_dp.py (corpus mean of
the holes==1 population) -- see that script's own module docstring for
the full "write everything twice, don't let reuse become inertia"
rationale. All calibrated constants load from
gfl2/configs/daily_pct_dp_calib.json at import time, falling back to a
hardcoded default (this file's own last-calibrated values) if that file
is absent -- same pattern as gfl2/stat_ocr_fft.py's gabor_calib.json /
daily_pct_hierarchical_calib.json.

Usage:
    python -m gfl2.stat_ocr_dp --verify --images "single/*.png"
    python -m gfl2.stat_ocr_dp --verify-glyphs --images "single/*.png"
    python -m gfl2.calibration.calibrate_dp --images "single/*.png"  # recalibrate
"""
from __future__ import annotations
import json, sys, time, glob as _glob
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from gfl2.stat_ocr import (
    PCT_STRIP_Y, VAL_STRIP_Y, DOT_MAX_DIM,
    _find_blobs, _filter_y_outliers, _find_percent_x_start,
    _collect_cells, _count_inner_blobs,
)

_HERE = Path(__file__).parent.parent
_CALIB_F = _HERE / "gfl2" / "configs" / "daily_pct_dp_calib.json"
_VAL_CALIB_F = _HERE / "gfl2" / "configs" / "daily_val_dp_calib.json"

TRAIN_CHARS = list("0123456789")
VAL_TRAIN_CHARS = list("0123456789K")   # val font never renders 'M' (see module docstring)


# ── Calibration (gfl2/calibration/calibrate_dp.py writes this file; see that
# script's module docstring for the "write everything twice, don't let reuse
# become inertia" rationale -- every constant below is THIS engine's own,
# derived on its own native/un-normalized glyph representation, not reused
# from another module). Falls back to the last-calibrated hardcoded values
# below if the config file is absent -- same pattern as gfl2/stat_ocr_fft.py's
# gabor_calib.json / daily_pct_hierarchical_calib.json.
_CALIB_DEFAULT = {
    "iso_gate": {"lo": 0.4106, "hi": 0.9211},
    "top_band_4": {"p0": 0.53, "p1": 0.76, "gate": 31.0},
    "top_band_7": {"height": 2, "gate": 17.0},
    "spread_x_5_gate": 4.5,
    "top_band_5": {"height": 1, "gate": 7.5},
    "bottom_band_23": {"height": 1, "gate": 10.0},
    "circular_centroids": {
        "0": [0.4744, 0.4671, -0.0321, 0.0103],
        "6": [0.1571, 0.1151, 0.0627, 0.2267],
        "9": [0.1072, 0.2037, 0.2330, -0.0310],
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


# ── VAL-LINE calibration (gfl2/calibration/calibrate_val_dp.py writes this
# SEPARATE file -- own font, own gates, own circular centroids; see module
# docstring's VAL-LINE TREE section for why this isn't a reuse of the
# pct-line constants above) ─────────────────────────────────────────────────
_VAL_CALIB_DEFAULT = {
    "k_left_gate": {"width": 2, "gate": 19.5},
    "top_band_4": {"p0": 0.58, "p1": 0.81, "gate": 10.5},
    "width_17_gate": 6.0,
    "deficit_2_gate": 1.0,
    "left_top_5_gate": 10.0,
    "circular_centroids": {
        "0": [0.1967, 0.2826, -0.1258, -0.0171],
        "6": [0.2671, 0.0328, 0.0084, 0.2112],
        "9": [0.0695, 0.1363, 0.1865, -0.1150],
    },
}


def _load_val_calib() -> dict:
    merged = {k: (dict(v) if isinstance(v, dict) else v) for k, v in _VAL_CALIB_DEFAULT.items()}
    if _VAL_CALIB_F.exists():
        calib = json.loads(_VAL_CALIB_F.read_text(encoding="utf-8"))
        for k, v in calib.items():
            if isinstance(v, dict) and isinstance(merged.get(k), dict):
                merged[k].update(v)
            else:
                merged[k] = v
    return merged


_VAL_CALIB = _load_val_calib()

VAL_K_LEFT_WIDTH = _VAL_CALIB["k_left_gate"]["width"]
VAL_K_LEFT_GATE = _VAL_CALIB["k_left_gate"]["gate"]
VAL_TOP_BAND_4_P0 = _VAL_CALIB["top_band_4"]["p0"]
VAL_TOP_BAND_4_P1 = _VAL_CALIB["top_band_4"]["p1"]
VAL_TOP_BAND_4_GATE = _VAL_CALIB["top_band_4"]["gate"]
VAL_WIDTH_17_GATE = _VAL_CALIB["width_17_gate"]
VAL_DEFICIT_2_GATE = _VAL_CALIB["deficit_2_gate"]
VAL_LEFT_TOP_5_GATE = _VAL_CALIB["left_top_5_gate"]
# Not calibrated from the config file, same convention as every other
# dp-family engine's own SPREAD_Y_THRESHOLD: any value inside the real,
# clean, hole==0-population gap (real corpus: {1,7} max=2.0, {2,3,5}
# min=7.0) works identically -- this is a midpoint, not a fitted edge.
VAL_SPREAD_Y_THRESHOLD = 4.5


# ── ROOT GATE: isoperimetric ratio ──────────────────────────────────────────
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


def _spread_x(reflex_pts: "np.ndarray | None") -> float:
    """Horizontal counterpart to _spread_y -- same reflex/concave contour
    points (already computed for the {1,7}-vs-{2,3,5} split, free to reuse
    here), just the x-axis extent instead of the y-axis one. Does NOT
    isolate '3' the way spread_y isolates {1,7} (only ~11% of real '3'
    glyphs read exactly 0; the rest overlap '2's own [3,4] range) -- but
    IS a clean gate for '5' vs {2,3}: '5' min=5.0, {2,3} max=4.0, a real
    1-unit corpus-wide gap. See SPREAD_X_5_GATE below."""
    if reflex_pts is None or len(reflex_pts) == 0:
        return 0.0
    return float(reflex_pts[:, 0].max() - reflex_pts[:, 0].min())


# ── Top-band ink count (copied from gfl2/stat_ocr_fft.py) ───────────────────
def _band_count(gray_norm: np.ndarray, y0: int, y1: int) -> int:
    """Count of non-zero (ink) pixels in rows [y0, y1) (exclusive), full
    width -- a kernel-free, convolution-free spatial primitive. Used at
    three different row bands below for three different digits. `gray_norm`
    is the RAW tight crop (no padding at all) -- row 0 is, by construction
    of cv2.boundingRect, always the glyph's own first ink row, and the
    array's own width is always the glyph's own native width."""
    return int(cv2.countNonZero(gray_norm[y0:y1, :]))


# '7' vs '1': top `height` rows of the RAW tight crop (row 0 IS the glyph's
# own first ink row -- there is no canvas edge to anchor away from anymore).
# Calibrated (gfl2/calibration/calibrate_dp.py, which also sweeps height
# itself -- the winning height=2, not the previous height=3) on the real
# corpus: '1' max=12, '7' min=24 -- a real 12-unit gap (vs. gap=3 under the
# original width-forced-to-12 canvas, gap=4 under the intermediate
# native-width-only version) -- removing normalization entirely made this
# margin WIDER, not just equally good.
TOP_BAND_7_HEIGHT = _CALIB["top_band_7"]["height"]
TOP_BAND_7_GATE = _CALIB["top_band_7"]["gate"]

# '4': the CROSSBAR's row band, measured as a PROPORTION of the glyph's OWN
# height (p0, p1) rather than an absolute canvas row range -- the earlier
# absolute-row version (TOP_BAND_4_Y0/Y1=11/17) only worked because every
# glyph was first forced into the SAME 20-row canvas; with no canvas at all,
# "row 11" has no meaning across glyphs of genuinely different native
# heights (18-21px in this corpus). Calibrated via a (p0,p1) grid sweep
# (gfl2/calibration/calibrate_dp.py): p0=0.55, p1=0.76 -- '4' min=43,
# every other non-circular digit's max=29 -- a real 14-unit gap (vs. the
# previous 1-unit razor edge under ANY padded representation). Proportional
# measurement, not padding, is what actually fixed this gate's fragility.
TOP_BAND_4_P0 = _CALIB["top_band_4"]["p0"]
TOP_BAND_4_P1 = _CALIB["top_band_4"]["p1"]
TOP_BAND_4_GATE = _CALIB["top_band_4"]["gate"]


def _band_count_proportional(crop: np.ndarray, p0: float, p1: float) -> int:
    """Ink count over rows [round(p0*h), round(p1*h)) of the glyph's OWN
    height h -- see TOP_BAND_4 above for why a proportion, not an absolute
    row range, is what generalizes across genuinely different crop sizes."""
    h = crop.shape[0]
    y0, y1 = int(round(p0 * h)), int(round(p1 * h))
    return _band_count(crop, y0, max(y0 + 1, y1))


# ── '5' vs {2,3} via spread_x, confirmed by a top-band ink count; '2' vs
# '3' via a BOTTOM-band ink count (replaces the paren_close cross-
# correlation template -- see known_issues.txt/decisions.txt for the
# corpus investigation) ──────────────────────────────────────────────────
# '5' vs {2,3}: spread_x (see _spread_x above) -- '5' min=5.0, {2,3}
# max=4.0, a real 1-unit gap, reusing the SAME reflex_pts already computed
# for the {1,7}-vs-{2,3,5} split (free -- no new contour work).
SPREAD_X_5_GATE = _CALIB["spread_x_5_gate"]

# CONFIRMATION for the spread_x '5' candidate, not a second independent
# vote to average against it: '5' has a strong top bar (like '7'), {2,3}
# don't -- same top-band-count mechanism as TOP_BAND_7/TOP_BAND_4.
# Calibrated (smallest clearing height, same preference as
# calibrate_top_band_7): height=1, {2,3} max=7, '5' min=8 (n=2499 + 867,
# zero overlap). If spread_x says '5' but the top band disagrees,
# classify() returns '?' rather than trusting spread_x alone
# (action_items.txt #28's confidence-abstention concern) -- never observed
# on the real corpus (recall=1.0000 at this gate too), but the check costs
# nothing spread_x wasn't already going to need computed anyway.
TOP_BAND_5_HEIGHT = _CALIB["top_band_5"]["height"]
TOP_BAND_5_GATE = _CALIB["top_band_5"]["gate"]

# '2' vs '3' (spread_x < SPREAD_X_5_GATE, i.e. NOT '5'): a BOTTOM-anchored
# ink count -- '2' always ends in a full-width flat bottom stroke (high
# ink count in its own last row(s)); '3' curls inward at the bottom (lower
# count). Same mechanism gfl2.stat_ocr's own _bottom_row_width_frac
# discriminator targets (known_issues.txt §15) for a DIFFERENT digit pair,
# expressed here as a plain ink COUNT rather than a width fraction, over
# the glyph's own last row(s) (crop.shape[0]-height : crop.shape[0]) --
# there is no canvas edge to anchor away from, same as every other
# band-count feature in this module. Calibrated: '3' max=9, '2' min=11
# (n=1129 + 1370, zero overlap, a real 2-unit gap).
BOTTOM_BAND_23_HEIGHT = _CALIB["bottom_band_23"]["height"]
BOTTOM_BAND_23_GATE = _CALIB["bottom_band_23"]["gate"]


def _bottom_band_count(crop: np.ndarray, height: int) -> int:
    """Ink count over the LAST `height` rows of the glyph's own tight
    crop -- mirrors _band_count's top-anchored convention but anchored to
    the glyph's own bottom edge instead (row crop.shape[0]-1 is, by
    construction of cv2.boundingRect, always the glyph's own last ink
    row)."""
    ch = crop.shape[0]
    return _band_count(crop, max(0, ch - height), ch)


# ── Resolution- and ink-color-group-adaptive binarization threshold ────────
# known_issues.txt #18 (2026-07-11 UPDATE): THRESH_BIN
# in gfl2/stat_ocr.py is one hardcoded global constant (180), calibrated
# against the corpus's typical (~2280x690-700) capture resolution. At
# gm_d_20250908.png's genuinely smaller (~2047x652, ~10%) resolution, 180
# bridges adjacent black-ink digit glyphs in col3 into one merged blob
# (known_issues.txt #18). A single global constant can't serve both scales.
#
# THIS IS NOT A "PICK A BETTER THRESHOLD VALUE" PROBLEM -- three different
# derivation methods were tried (plain 2-class Otsu, 3-class multi-Otsu's
# darker boundary, 3-class multi-Otsu's brighter boundary) and the FIRST
# TWO both regressed several already-classify()-calibrated gates
# (TOP_BAND_7_GATE, TOP_BAND_25_GATE) that measure an ABSOLUTE ink-pixel
# count over a FIXED few rows of the tight crop. Since normalization was
# removed entirely (this module's own NORMALIZATION section above), a
# glyph's crop origin IS wherever binarization draws its ink boundary --
# changing the threshold shifts what "row 0" physically is on the glyph,
# invalidating any gate measured in absolute rows/pixels, independent of
# whether the new threshold is itself "more correct" for foreground/
# background separation. (TOP_BAND_4 already sidesteps this by measuring
# a PROPORTION of the glyph's own height, not an absolute row range -- see
# that gate's own comment.) A first pass at making TOP_BAND_7/TOP_BAND_25
# proportional too did not reproduce their absolute-row versions' clean
# margins on a first attempt and was not pursued further this session --
# the corpus-validated fallback is multi-Otsu's DARKER boundary (t1, the
# ink/halo split, not t2's halo/background split -- t2 is far too
# inclusive, 92.6% corpus accuracy) applied ONLY to a lookup keyed by
# (pct-strip height, ink-color group), which is what ships below.
#
# ONE GROUP IS NOT ENOUGH: pct-line column 1 (Damage Dealt) renders in a
# visually distinct ORANGE ink (mean BGR ~[102,137,216], confirmed
# corpus-wide) vs. every other column's black/gray ink (~[110,104,91]) --
# a real, structural trait of this UI section (see known_issues.txt #18's
# 2026-07-11 UPDATE), NOT specific to gm_d_20250908.png. A single
# threshold derived from whichever cell happens to be sampled first would
# silently mix these two ink populations. col2/col3/col4 were all
# confirmed to share the SAME ink color (checked directly, not assumed) --
# two groups ("col1", "rest") is sufficient, a per-column table is not
# needed.
#
# CORPUS RESULT (2026-07-11, single/*.png, 3161 pct-labelled cells, GT
# overrides applied): 99.5% (3145/3161, THRESH_BIN=180 everywhere) ->
# 99.59% (3148/3161, this lookup) -- gm_d_20250908.png's col3 fully
# resolved (8->0 mismatches), net +3 cells despite 5 NEW col4 '5'->'3'
# misreads introduced elsewhere (col4 confirmed to share the "rest" ink
# color -- NOT a group-detection miss; root cause not yet investigated,
# filed as a fresh, separately-tracked item -- see known_issues.txt #18).
_INK_GROUP_RED_EXCESS_GATE = 60.0
_INK_GROUP_MIN_INK_PIXELS = 20


def _detect_ink_group(strip_bgr: np.ndarray) -> str:
    """'col1' (Damage Dealt's orange ink) vs 'rest' (every other pct
    column's black/gray ink) -- detected from the strip's OWN mean ink
    color, not column position, so it works regardless of which column is
    actually being read. Falls back to 'rest' if too little ink is found
    to measure a reliable color (matches this corpus's own ink-pixel-count
    convention elsewhere, e.g. _filter_y_outliers's threshold)."""
    gray = cv2.cvtColor(strip_bgr, cv2.COLOR_BGR2GRAY) if strip_bgr.ndim == 3 else strip_bgr
    ink_mask = gray < 200
    if int(ink_mask.sum()) < _INK_GROUP_MIN_INK_PIXELS:
        return "rest"
    b, g, r = strip_bgr[ink_mask].mean(axis=0)
    return "col1" if (r - b) > _INK_GROUP_RED_EXCESS_GATE else "rest"


def _multi_otsu_2thresh(gray: np.ndarray) -> "tuple[int, int]":
    """Fast 3-class Otsu thresholding (Liao, Chen & Chung, 2001) via
    cumulative histogram zeroth/first-order moments -- O(256^2) candidate
    (t1, t2) pairs instead of the naive O(256^3) recomputation. Returns
    (t1, t2): t1 is the boundary between the darkest class (solid ink) and
    the middle class (anti-aliasing halo); t2 is the boundary between the
    middle class and the brightest class (background). Standard binary
    (2-class) cv2.THRESH_OTSU collapses halo+ink into one class against
    background, landing at a halo-inclusive valley that is measurably too
    low for this corpus's already-calibrated gates -- see the section
    comment above. This project has no scikit-image dependency
    (skimage.filters.threshold_multiotsu implements the same algorithm);
    hand-implemented here rather than adding one for a single function."""
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


def _adaptive_pct_threshold(strip_bgr: np.ndarray, cache: dict) -> int:
    """Binarization threshold for a pct strip, keyed by (strip height,
    ink-color group) in `cache` -- populated lazily: the first cell of a
    given (height, group) pair encountered in a run derives that group's
    value via multi-Otsu; every later cell of the same (height, group)
    reuses it. `cache` is caller-owned so it can be shared across an
    entire corpus scan (StatOcrDp keeps one per engine instance;
    verify()/verify_glyphs()/calibrate_dp.py share one across their whole
    run) -- values are NOT persisted between runs, matching every other
    calibrated constant's build-time-only re-derivation in this module."""
    strip_h = strip_bgr.shape[0]
    group = _detect_ink_group(strip_bgr)
    key = (strip_h, group)
    cached = cache.get(key)
    if cached is not None:
        return cached
    gray = cv2.cvtColor(strip_bgr, cv2.COLOR_BGR2GRAY) if strip_bgr.ndim == 3 else strip_bgr
    t1, _t2 = _multi_otsu_2thresh(gray)
    cache[key] = t1
    return t1


def _binarize_pct_adaptive(strip_bgr: np.ndarray, cache: dict) -> np.ndarray:
    """Same THRESH_BINARY_INV convention as gfl2.stat_ocr._binarize, but at
    a per-(resolution, ink-group) adaptive threshold instead of the shared
    module's fixed THRESH_BIN=180 -- pct-strip-only, this engine's own,
    duplicated rather than added as a flag to the shared function (decision
    47's full-duplication policy; THRESH_BIN=180 stays untouched for every
    MAIN-scope engine)."""
    t = _adaptive_pct_threshold(strip_bgr, cache)
    gray = cv2.cvtColor(strip_bgr, cv2.COLOR_BGR2GRAY) if strip_bgr.ndim == 3 else strip_bgr
    _, thresh = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY_INV)
    return thresh


# ── Glyph extraction -- NO normalization ─────────────────────────────────
# Every glyph is used at its own native, tight-bounding-box size: no
# padding, no cropping, no resize, no forced canvas of any kind. See the
# module docstring's NORMALIZATION section for why (nothing downstream
# needs a fixed size) and what removing it bought (every gate's real
# corpus margin widened, some dramatically).
def _extract_pct_glyphs(pct_blobs: list, thresh: np.ndarray) -> "list[tuple[int, Optional[np.ndarray], str]]":
    """Inference-time (label-free) glyph extraction. Same shape as
    gfl2.stat_ocr_fft's function of the same name. Returns each glyph's
    RAW tight crop, unmodified."""
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
            result.append((x, crop, 'digit'))
    return result


_PCT_STRIP_EXTRA_PX = 5


def _pct_strip_bottom(ch: int) -> int:
    return min(ch, int(ch * PCT_STRIP_Y[1]) + _PCT_STRIP_EXTRA_PX, int(ch * VAL_STRIP_Y[0]))


def _extract_pct_digit_glyphs(cell: np.ndarray, pct_label: str, thresh_cache: "dict | None" = None):
    """Training/verify-time (label-aligned) glyph extraction. Returns
    [(raw_tight_crop, digit_char), ...] or None if the blob count doesn't
    match the label.

    thresh_cache: shared (strip_h, ink_group) -> threshold cache (see
    _adaptive_pct_threshold above). Defaults to a fresh, call-scoped dict
    if omitted (safe but non-shared -- callers scanning a whole corpus,
    e.g. verify_glyphs()/calibrate_dp.py, should pass one shared dict
    across the loop so a resolution/group's threshold is derived once,
    not re-derived per cell)."""
    if not pct_label:
        return None
    expected = [c for c in pct_label if c.isdigit()]
    if not expected:
        return None
    if thresh_cache is None:
        thresh_cache = {}

    ch = cell.shape[0]
    pct_strip = cell[: _pct_strip_bottom(ch), :]
    thresh = _binarize_pct_adaptive(pct_strip, thresh_cache)
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
        glyphs.append((crop, label))
    return glyphs


# ── VAL-LINE spatial primitives (this font's own -- see module docstring's
# VAL-LINE TREE section for why these differ from the pct-line leaves) ──────
def _band_count_left(crop: np.ndarray, x0: int, x1: int) -> int:
    """Ink count in columns [x0, x1) of the glyph's own tight crop, full
    height -- the horizontal-band counterpart to _band_count, transposed
    from rows to columns (same mechanism as gfl2/header_ocr_dp.py's own
    K-gate primitive). Column 0 is, by construction of cv2.boundingRect,
    always the glyph's own leftmost ink column."""
    return int(cv2.countNonZero(crop[:, x0:x1]))


def _bottom_row_deficit(crop: np.ndarray) -> int:
    """Glyph width minus the ink SPAN (last_col - first_col + 1) of its own
    LAST row -- '2' ends in a full-width flat stroke (deficit 0-1 on the
    real corpus); {3,5} curl inward well before the last row (deficit>=2).
    A scale-invariant sibling of gfl2.stat_ocr._bottom_row_width_frac
    (which divides by a FIXED NORM_W; this engine has no fixed canvas, so
    the deficit is expressed directly in the glyph's own native pixels)."""
    w = crop.shape[1]
    cols = np.where(crop[-1, :] > 127)[0]
    if cols.size == 0:
        return w
    span = int(cols[-1] - cols[0] + 1)
    return w - span


def _left_top_count(crop: np.ndarray) -> int:
    """Ink count in the glyph's own top-left quadrant (top half of its
    height, left half of its width) -- '5's flat top stroke starts at the
    glyph's own left edge; '3's two right-open curves don't reach nearly as
    far left at the top. Real corpus gap: '3' max=9, '5' min=10 (Youden's J
    at the real corpus's few remaining GT-mislabelled outliers:
    recall=0.9965/false_trigger=0.0009)."""
    h, w = crop.shape
    top = crop[: int(round(h * 0.5)), : max(1, w // 2)]
    return int(cv2.countNonZero(top))


def classify_val(crop: np.ndarray, val_circular_centroids: dict) -> str:
    """Full classify tree for a single val-line glyph. `crop` is the
    glyph's RAW tight crop -- no normalization of any kind (same
    NORMALIZATION policy as the pct-line classify() above). See the module
    docstring's VAL-LINE TREE section for the measurements behind each gate
    and why this tree's shape differs from classify()'s.

    TREE:
      hole count (root -- NOT isoperimetric ratio, see module docstring)
        +-- holes>=2 -> '8' (categorical)
        +-- holes==1 -> {0,6,9} via paren+loop nearest-of-3 (this font's
        |     OWN corpus-derived centroids, gfl2/calibration/
        |     calibrate_val_dp.py -- not reused from the pct-line leaf)
        +-- holes==0 ({1,2,3,4,5,7,K} likely):
              +-- K gate (left-band ink count) FIRST, before '4' or any
              |     reflex-vertex work -- same mechanism as
              |     gfl2/header_ocr_dp.py's own K gate.
              +-- '4' gate (top-band proportional ink count, same
              |     mechanism as TOP_BAND_4 above, own gate value).
              +-- else: spread_y splits {1,7} from {2,3,5}
                    +-- {1,7}: glyph WIDTH ALONE splits '7' (wide) from
                    |     '1' (narrow) -- NOT a top-band count, see module
                    |     docstring for why that mechanism is backwards on
                    |     this font.
                    +-- {2,3,5}: a bottom-row-deficit gate isolates '2'
                          FIRST (full-width flat bottom stroke), then a
                          top-left-quadrant ink count splits '5' from '3'.
    """
    holes = _count_inner_blobs(crop)
    if holes >= 2:
        return '8'
    if holes == 1:
        combined = np.concatenate([_paren_features(crop), _loop_features(crop)])
        best_d, best_dist = None, None
        for d, centroid in val_circular_centroids.items():
            dist = float(np.linalg.norm(combined - centroid))
            if best_dist is None or dist < best_dist:
                best_d, best_dist = d, dist
        return best_d if best_d is not None else '?'

    # holes == 0: K gate FIRST, before '4' or any reflex-vertex work at all.
    if _band_count_left(crop, 0, VAL_K_LEFT_WIDTH) >= VAL_K_LEFT_GATE:
        return 'K'

    if _band_count_proportional(crop, VAL_TOP_BAND_4_P0, VAL_TOP_BAND_4_P1) >= VAL_TOP_BAND_4_GATE:
        return '4'

    reflex_pts, _ = _reflex_vertices(crop)
    sy = _spread_y(reflex_pts)
    if sy <= VAL_SPREAD_Y_THRESHOLD:
        # {1,7}: raw glyph width, not a top-band count (see module docstring)
        return '7' if crop.shape[1] >= VAL_WIDTH_17_GATE else '1'

    # {2,3,5}: bottom-row-deficit isolates '2' FIRST, then a top-left-
    # quadrant ink count splits the remaining '5' from '3'.
    if _bottom_row_deficit(crop) <= VAL_DEFICIT_2_GATE:
        return '2'
    return '5' if _left_top_count(crop) >= VAL_LEFT_TOP_5_GATE else '3'


def _load_val_circular_centroids() -> dict:
    """{'0': np.array([paren_open, paren_close, loop_top, loop_bot]), '6':
    ..., '9': ...} -- THIS font's own corpus-derived centroids (gfl2/
    calibration/calibrate_val_dp.py -> gfl2/configs/daily_val_dp_calib.json),
    never reused from the pct-line leaf's own centroids (different font,
    different native scale -- see module docstring)."""
    return {d: np.asarray(v, dtype=np.float64) for d, v in _VAL_CALIB["circular_centroids"].items()}


# ── VAL-LINE glyph extraction -- NO normalization (same policy as pct) ──────
def _extract_val_glyphs(val_blobs: list, thresh: "np.ndarray | None") -> "list[tuple[int, Optional[np.ndarray], str]]":
    """Inference-time (label-free) glyph extraction. Same shape as
    gfl2.stat_ocr._extract_val_glyphs, but returns each glyph's RAW tight
    crop unmodified (no resize to NORM_W_VAL x NORM_H_VAL)."""
    if not val_blobs:
        return []
    result = []
    for (x, y, w, h) in sorted(val_blobs, key=lambda b: b[0]):
        if w <= DOT_MAX_DIM and h <= DOT_MAX_DIM:
            result.append((x, None, '.'))
        else:
            crop = thresh[y: y + h, x: x + w]
            result.append((x, crop, 'digit'))
    return result


def _reconstruct_val(glyphs: list, val_circular_centroids: dict) -> Optional[str]:
    items = [(x, crop, hint) for x, crop, hint in glyphs if hint != 'skip']
    if not items:
        return None
    parts = []
    for x, crop, hint in items:
        if hint == '.':
            parts.append('.')
        else:
            parts.append(classify_val(crop, val_circular_centroids))
    result = ''.join(parts)
    return result if result and '?' not in result else None


def _extract_val_digit_glyphs(cell: np.ndarray, val_label: str,
                               thresh_cache: "dict | None" = None) -> "list[tuple[np.ndarray, str]] | None":
    """Training/verify-time (label-aligned) glyph extraction. Returns
    [(raw_tight_crop, char), ...] or None if the blob count doesn't match
    `val_label`'s expected VAL_TRAIN_CHARS count -- same skip-don't-guess
    convention as _extract_pct_digit_glyphs above.

    thresh_cache: shared (strip_h, ink_group) -> threshold cache, same
    contract as _extract_pct_digit_glyphs's own parameter -- pass one
    shared dict across a whole-corpus scan so a resolution/group's
    threshold is derived once, not per cell."""
    if not val_label:
        return None
    expected = [c for c in val_label if c in VAL_TRAIN_CHARS]
    if not expected:
        return None
    if thresh_cache is None:
        thresh_cache = {}

    ch = cell.shape[0]
    val_strip = cell[int(ch * VAL_STRIP_Y[0]): int(ch * VAL_STRIP_Y[1]), :]
    if val_strip.size == 0:
        return None
    thresh = _binarize_pct_adaptive(val_strip, thresh_cache)
    blobs = _find_blobs(thresh)
    if not blobs:
        return None
    blobs = _filter_y_outliers(blobs, threshold=8)
    if not blobs:
        return None

    sorted_x = sorted(blobs, key=lambda b: b[0])
    digit_blobs = [(x, y, w, h) for (x, y, w, h) in sorted_x
                   if not (w <= DOT_MAX_DIM and h <= DOT_MAX_DIM)]
    if len(digit_blobs) != len(expected):
        return None

    glyphs = []
    for (x, y, w, h), label in zip(digit_blobs, expected):
        crop = thresh[y: y + h, x: x + w]
        if crop.size == 0:
            return None
        glyphs.append((crop, label))
    return glyphs


# ── Classify tree ────────────────────────────────────────────────────────────
def classify(crop: np.ndarray, circular_centroids: dict) -> str:
    """Full classify tree -- see module docstring for the diagram. `crop`
    is the glyph's RAW tight crop -- no normalization of any kind.
    circular_centroids: {'0': np.array([paren_open, paren_close, loop_top,
    loop_bot]), '6': [...], '9': [...]} -- THIS engine's own corpus-derived
    centroids (see _load_circular_centroids / gfl2/calibration/
    calibrate_dp.py), computed on this exact same raw-crop representation."""
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

    # non-circular: '4' gate FIRST, before any reflex-vertex work at all.
    if _band_count_proportional(crop, TOP_BAND_4_P0, TOP_BAND_4_P1) >= TOP_BAND_4_GATE:
        return '4'

    reflex_pts, _ = _reflex_vertices(crop)
    sy = _spread_y(reflex_pts)
    if sy <= SPREAD_Y_THRESHOLD:
        # {1,7}
        top = _band_count(crop, 0, TOP_BAND_7_HEIGHT)
        return '7' if top >= TOP_BAND_7_GATE else '1'

    # {2,3,5}: spread_x (already computed above) gates '5' vs {2,3} first;
    # a top-band count CONFIRMS it (abstain rather than trust spread_x
    # alone -- see TOP_BAND_5 above). Otherwise a bottom-band count splits
    # '2' from '3'. No paren/loop template correlation anywhere in this
    # leaf -- see module docstring's TREE section.
    sx = _spread_x(reflex_pts)
    if sx >= SPREAD_X_5_GATE:
        top5 = _band_count(crop, 0, TOP_BAND_5_HEIGHT)
        return '5' if top5 >= TOP_BAND_5_GATE else '?'
    bottom23 = _bottom_band_count(crop, BOTTOM_BAND_23_HEIGHT)
    return '2' if bottom23 >= BOTTOM_BAND_23_GATE else '3'


# ── Circular-leaf centroids: THIS engine's OWN corpus calibration ───────────
def _load_circular_centroids() -> dict:
    """{'0': np.array([paren_open, paren_close, loop_top, loop_bot]), '6': ...,
    '9': ...} -- loaded from _CALIB (gfl2/configs/daily_pct_dp_calib.json,
    written by gfl2/calibration/calibrate_dp.py), NOT reused from another
    module's trained templates. See that script's module docstring for why
    reuse here would have re-capped this engine's accuracy at a
    normalization choice made for a different classifier."""
    return {d: np.asarray(v, dtype=np.float64) for d, v in _CALIB["circular_centroids"].items()}


# ── Public engine ─────────────────────────────────────────────────────────────
class StatOcrDp:
    """Simplified, mostly-spatial-domain nearest-centroid OCR engine --
    pct-line AND val-line (see module docstring's VAL-LINE TREE section for
    why the two are separate trees, not a shared one). See module docstring
    for the full tree diagrams."""

    def __init__(self, circular_centroids: dict, val_circular_centroids: "dict | None" = None) -> None:
        self._circular_centroids = circular_centroids
        self._val_circular_centroids = val_circular_centroids or {}
        self._thresh_cache: dict = {}

    @classmethod
    def load(cls, tmpl_variant: str | None = None) -> "StatOcrDp":
        """tmpl_variant: accepted for interface parity with StatOcr.load()/
        StatOcrPadded.load() (main.py's _get_stat_ocr_engine() always calls
        .load(tmpl_variant) uniformly) but IGNORED -- this engine has no
        swappable template files, only its two calibration files
        (gfl2/configs/daily_pct_dp_calib.json, daily_val_dp_calib.json,
        both loaded at import time)."""
        if tmpl_variant is not None:
            import sys
            print(f"Warning: StatOcrDp has no template variants; ignoring "
                  f"--stat-templates {tmpl_variant!r}.", file=sys.stderr)
        return cls(_load_circular_centroids(), _load_val_circular_centroids())

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
            thresh = _binarize_pct_adaptive(strip, self._thresh_cache)
            blobs = _find_blobs(thresh)
            if not blobs:
                return None
            blobs = _filter_y_outliers(blobs, threshold=8)
            if not blobs:
                return None
            glyphs = _extract_val_glyphs(blobs, thresh)
            return _reconstruct_val(glyphs, self._val_circular_centroids)

        thresh = _binarize_pct_adaptive(strip, self._thresh_cache)
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

    _GT_FILE = Path("tests/inputs/daily/stat_gt_overrides.json")
    if gt_overrides is None:
        gt_overrides = json.loads(_GT_FILE.read_text()) if _GT_FILE.exists() else {}
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and "pct" in ov:
            item["pct"] = ov["pct"]
        if ov and "val" in ov:
            item["val"] = ov["val"]

    pct_total = pct_match = pct_miss = 0
    val_total = val_match = val_miss = 0
    mismatches = []
    val_mismatches = []
    classify_times = []
    for item in samples:
        t0 = time.perf_counter()
        blob_pct, blob_val = engine.read(item["cell"])
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
        if item.get("val"):
            val_total += 1
            if blob_val is None:
                val_miss += 1
                val_mismatches.append((item["source"], item["val"], blob_val))
            elif blob_val != item["val"]:
                val_mismatches.append((item["source"], item["val"], blob_val))
            else:
                val_match += 1

    mean_us = statistics.mean(classify_times) * 1e6 if classify_times else 0.0
    stdev_us = statistics.pstdev(classify_times) * 1e6 if len(classify_times) > 1 else 0.0
    cv_ = (stdev_us / mean_us) if mean_us else 0.0

    if verbose:
        def pct_str(n, d): return f"{100*n/d:.1f}%" if d else "n/a"
        print(f"\n{'-'*60}")
        print(f"Generated: {run_start}  (run start)")
        print(f"StatOcrDp verify  ({len(image_paths)} images, {len(samples)} cells)")
        print(f"  pct  {pct_match}/{pct_total} correct  ({pct_str(pct_match, pct_total)})  {pct_miss} no-read")
        print(f"  val  {val_match}/{val_total} correct  ({pct_str(val_match, val_total)})  {val_miss} no-read")
        print(f"  timing  mean={mean_us:.1f}us/cell  stdev={stdev_us:.1f}us  cv={cv_:.2f}  (n={len(classify_times)} cells)")
        if mismatches:
            print(f"\nFirst 20 pct mismatches:")
            for source, exp, got in mismatches[:20]:
                print(f"  {source}  pct  expected={exp!r}  got={got!r}")
        if val_mismatches:
            print(f"\nFirst 20 val mismatches:")
            for source, exp, got in val_mismatches[:20]:
                print(f"  {source}  val  expected={exp!r}  got={got!r}")
        print(f"{'-'*60}")

    return {"pct_total": pct_total, "pct_match": pct_match, "pct_miss": pct_miss,
            "val_total": val_total, "val_match": val_match, "val_miss": val_miss,
            "mismatches": mismatches, "val_mismatches": val_mismatches,
            "mean_us": mean_us, "stdev_us": stdev_us, "cv": cv_}


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

    _GT_FILE = Path("tests/inputs/daily/stat_gt_overrides.json")
    if gt_overrides is None:
        gt_overrides = json.loads(_GT_FILE.read_text()) if _GT_FILE.exists() else {}
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and "pct" in ov:
            item["pct"] = ov["pct"]
        if ov and "val" in ov:
            item["val"] = ov["val"]

    per_digit = {d: {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0}
                 for d in TRAIN_CHARS}
    per_val_char = {d: {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0}
                     for d in VAL_TRAIN_CHARS}
    classify_times = []
    val_classify_times = []
    thresh_cache: dict = {}
    for item in samples:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "", thresh_cache)
        if glyphs is not None:
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

        val_glyphs = _extract_val_digit_glyphs(item["cell"], item.get("val") or "", thresh_cache)
        if val_glyphs is not None:
            for norm, true_label in val_glyphs:
                bucket = per_val_char.setdefault(
                    true_label, {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0})
                t0 = time.perf_counter()
                pred = classify_val(norm, engine._val_circular_centroids)
                val_classify_times.append(time.perf_counter() - t0)
                bucket["classified"] += 1
                if pred == '?':
                    bucket["unknown"] += 1
                elif pred == true_label:
                    bucket["correct"] += 1
                else:
                    bucket["misclassified"] += 1

    totals = {k: sum(per_digit[d][k] for d in per_digit)
              for k in ("classified", "correct", "misclassified", "unknown")}
    val_totals = {k: sum(per_val_char[d][k] for d in per_val_char)
                  for k in ("classified", "correct", "misclassified", "unknown")}
    mean_us = statistics.mean(classify_times) * 1e6 if classify_times else 0.0
    stdev_us = statistics.pstdev(classify_times) * 1e6 if len(classify_times) > 1 else 0.0
    cv_ = (stdev_us / mean_us) if mean_us else 0.0
    val_mean_us = statistics.mean(val_classify_times) * 1e6 if val_classify_times else 0.0
    val_stdev_us = statistics.pstdev(val_classify_times) * 1e6 if len(val_classify_times) > 1 else 0.0
    val_cv_ = (val_stdev_us / val_mean_us) if val_mean_us else 0.0

    if verbose:
        print(f"\n{'-'*60}")
        print(f"Generated: {run_start}  (run start)")
        print(f"StatOcrDp verify_glyphs  ({len(image_paths)} images, {totals['classified']} pct glyphs, "
              f"{val_totals['classified']} val glyphs)")
        print("pct:")
        print(f"{'digit':>6} {'classified':>10} {'correct':>8} {'misclassified':>13} {'unknown':>8}")
        for d in TRAIN_CHARS:
            b = per_digit[d]
            print(f"{d:>6} {b['classified']:>10} {b['correct']:>8} {b['misclassified']:>13} {b['unknown']:>8}")
        acc = totals['correct'] / totals['classified'] if totals['classified'] else 0.0
        print(f"{'TOTAL':>6} {totals['classified']:>10} {totals['correct']:>8} "
              f"{totals['misclassified']:>13} {totals['unknown']:>8}  ({100*acc:.1f}% correct)")
        print(f"  timing  mean={mean_us:.1f}us/glyph  stdev={stdev_us:.1f}us  cv={cv_:.2f}  (n={len(classify_times)} glyphs)")
        print("val:")
        print(f"{'char':>6} {'classified':>10} {'correct':>8} {'misclassified':>13} {'unknown':>8}")
        for d in VAL_TRAIN_CHARS:
            b = per_val_char[d]
            print(f"{d:>6} {b['classified']:>10} {b['correct']:>8} {b['misclassified']:>13} {b['unknown']:>8}")
        val_acc = val_totals['correct'] / val_totals['classified'] if val_totals['classified'] else 0.0
        print(f"{'TOTAL':>6} {val_totals['classified']:>10} {val_totals['correct']:>8} "
              f"{val_totals['misclassified']:>13} {val_totals['unknown']:>8}  ({100*val_acc:.1f}% correct)")
        print(f"  timing  mean={val_mean_us:.1f}us/glyph  stdev={val_stdev_us:.1f}us  cv={val_cv_:.2f}  (n={len(val_classify_times)} glyphs)")
        print(f"{'-'*60}")

    return {"per_digit": per_digit, "totals": totals, "mean_us": mean_us, "stdev_us": stdev_us, "cv": cv_,
            "per_val_char": per_val_char, "val_totals": val_totals,
            "val_mean_us": val_mean_us, "val_stdev_us": val_stdev_us, "val_cv": val_cv_}


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

    gt_file = Path(args.gt_overrides) if args.gt_overrides else Path("tests/inputs/daily/stat_gt_overrides.json")
    gt_overrides = json.loads(gt_file.read_text(encoding="utf-8")) if gt_file.exists() else None

    if args.verify:
        verify(image_paths, verbose=True, gt_overrides=gt_overrides, gt_cache=gt_cache)
    if args.verify_glyphs:
        verify_glyphs(image_paths, verbose=True, gt_overrides=gt_overrides, gt_cache=gt_cache)


if __name__ == "__main__":
    main()
