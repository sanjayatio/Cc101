# -*- coding: utf-8 -*-
"""
daily_gunsmoke.py - Daily Gunsmoke (Challenge Points) report parser.

Output format: JavaScript constant accumulated into daily_gunsmoke.js.

    const DAILY_GUNSMOKE = [
      ["gm_d_20250929",1,4635,"2263K",39170,7,[
        ["Qiongjiu",   38.97,882107,24.22,186,14.58, 5716, 0,    0],
        ...
      ]],
      ...
    ];

Usage (folder mode, recommended):
    python main.py gm/ --pattern daily_gunsmoke

Usage (single file):
    python main.py gm/gm_d_20250929.png --pattern daily_gunsmoke
"""
from __future__ import annotations
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Optional
import cv2
import numpy as np
import pytesseract

from gfl2.asset_mapper import ASSETS_DIR
from gfl2.timing import TimerStack
from gfl2.dg_output import (
    DollRow, ReportEntry, save_js,          # re-export for callers
    _save_doll_portrait, _crop_portrait,
    FRAME_BG_DELTA,
    _get_doll_name_ocr, _known_doll_names, _fuzzy_correct,
    _NEW_CROPS, flush_name_templates,       # re-export for main.py
)

# ── Layout (proportions of panel width / image height) ───────────────────────
HEADER_BAR_Y0  = 0.010
HEADER_BAR_Y1  = 0.082
STATS_ROW_Y0    = 0.082   # panel-fraction fallback when no frames detected
STATS_ROW_Y1    = 0.170   # panel-fraction fallback when no frames detected
STATS_ROW_Y0_FR = 1.25    # frame-relative: sy0 = fy - int(fh * STATS_ROW_Y0_FR)
STATS_ROW_Y1_FR = 0.70    # frame-relative: sy1 = fy - int(fh * STATS_ROW_Y1_FR)

COL1_X0, COL1_X1   = 0.192, 0.384   # Damage dealt  (kept for external callers)
COL2_X0, COL2_X1   = 0.376, 0.575   # Stability broken
COL3_X0, COL3_X1   = 0.575, 0.767   # Damage taken
COL4_X0, COL4_X1   = 0.767, 1.000   # Healed
SCORE_X0, SCORE_X1   = 0.920, 1.000   # fallback crop if medal anchor not found
SCORE_CROP_W_FR      = 90.0 / 89.0   # score crop width ≈ one doll frame width
MEDAL_SEARCH_X0      = 0.75           # scan this fraction rightward for the medal
MEDAL_MIN_AREA       = 80             # min blob area (px²) to consider as medal

# Frame-relative column x-offsets (multiples of fw, from frame right edge FR=fx+fw).
# Calibrated from gm_d_20250929 at fw=89; expressed in fw units so they scale
# with any detected frame size — resolution-independent.
COL1_FR = (2.034, 3.200)   # Damage dealt (widened to fit 5-digit pct %)
COL2_FR = (4.978, 6.250)   # Stability      (widened: 6-digit pct % must not clip)
COL3_FR = (7.270, 8.520)   # Damage taken   (widened: 6-digit pct % must not clip)
COL4_FR = (9.540, 10.888)  # Healed

# Stats-row number x-positions — panel-width fractions anchored just after
# each static label phrase ("Damage dealt", "Damage taken", "Combat turns").
# These are fixed text landmarks independent of frame size.
# Calibrated from gm_d_20251110.png (1142px panel, fw=89).
STATS_DEALT_X = (0.223, 0.330)  # number follows "♦ Damage dealt "
STATS_TAKEN_X = (0.540, 0.645)  # number follows "♦ Damage taken "; x1 stays before the "/" separator
STATS_TURNS_X = (0.860, 0.940)  # number follows "♦ Combat turns "

# Frame-relative vertical strip extent (multiples of fh, from frame top fy).
# Covers pct-line top (≈0.227·fh) through val-line bottom (≈0.761·fh) with buffer.
CELL_Y_FR = (0.20, 0.90)

CELL_BOTTOM_TRIM = 0.15   # kept for reference; no longer applied in _extract_stat_cell

# ── Frame / portrait detection ────────────────────────────────────────────────
FRAME_MIN_DIM       = 40    # minimum portrait width/height in pixels
FRAME_MIN_SQ        = 0.70  # minimum squareness (shorter/longer side ratio)
FRAME_OUTLIER_RATIO = 0.60  # discard frames smaller than this fraction of largest area
_FRAME_GROUP_X_GAP  = 50   # x-gap (px) separating portrait columns of different reports
NAME_W_FRAC         = 0.14  # name-column width as fraction of panel width


# ── Stat-cell blob OCR engine (lazy-loaded) ───────────────────────────────────

_STAT_OCR = None   # StatOcr instance, or False if templates not available


def _get_stat_ocr():
    global _STAT_OCR
    if _STAT_OCR is None:
        try:
            from gfl2.stat_ocr import StatOcr
            _STAT_OCR = StatOcr.load()
        except Exception:
            _STAT_OCR = False
    return _STAT_OCR if _STAT_OCR is not False else None


# (name OCR utilities imported from gfl2.dg_output)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _crop(img, x0f, x1f, y0f=0.0, y1f=1.0):
    h, w = img.shape[:2]
    return img[int(h*y0f):int(h*y1f), int(w*x0f):int(w*x1f)]


def _ocr_raw(region, cfg="--psm 6"):
    if region.size == 0:
        return ""
    up   = cv2.resize(region, (0, 0), fx=8, fy=8, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY) if up.ndim == 3 else up
    return pytesseract.image_to_string(gray, config=cfg).strip()


def _ocr_bright(region, threshold=170, cfg="--psm 7"):
    if region.size == 0:
        return ""
    up   = cv2.resize(region, (0, 0), fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY) if up.ndim == 3 else up
    _, t = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return pytesseract.image_to_string(255 - t, config=cfg).strip()


def _parse_pct_val(txt: str):
    m   = re.search(r"([\d.]+)\s*%", txt)
    pct = m.group(1) if m else None
    if pct is None:
        # % may be clipped by cell boundary — fall back to first decimal number
        m2  = re.search(r"(\d+\.\d+)", txt)
        pct = m2.group(1) if m2 else None
    nums = re.findall(r"\d+", txt)
    if not nums:
        return pct, None
    pct_digits = pct.replace(".", "") if pct else ""
    joined     = "".join(nums)
    after      = joined[len(pct_digits):]
    val_m      = re.search(r"\d+", after)
    val        = val_m.group(0) if val_m else (nums[-1] if (after and nums) else None)
    # Preserve K/M suffix (ib_d shows large values as e.g. "4246K" = 4,246,000)
    if val:
        km = re.search(re.escape(val) + r"([KkMm])", txt.replace(",", ""))
        if km:
            val = val + km.group(1).upper()
    return pct, val


# Trailing badge patterns: "w5", "s3", "v1", "Lv" etc. appended by OCR noise.
_BADGE_RE = re.compile(r"^[A-Za-z]{1,2}\d*$")


def _extract_name(cell: np.ndarray) -> Optional[str]:
    txt   = _ocr_raw(cell, "--psm 7")
    clean = re.sub(r"[^A-Za-z0-9_\-\. ]", "", txt).strip()
    words = clean.split()
    while words and len(words[0]) <= 2 and not words[0][0].isupper():
        words.pop(0)
    while words and len(words[-1]) <= 3 and _BADGE_RE.match(words[-1]):
        words.pop()
    return " ".join(words) or None


# (_levenshtein, _known_doll_names, _fuzzy_correct imported from gfl2.dg_output)


# ── Header blob OCR ───────────────────────────────────────────────────────────

_HEADER_TMPL      = None   # score digit_templates (score_detect); False when unavailable
_HEADER_STAT_TMPL = None   # stats-row digit templates (header_templates.json); False when unavailable


def _get_header_templates():
    global _HEADER_TMPL
    if _HEADER_TMPL is None:
        try:
            from assets.fonts.score_digits import DATA
            _HEADER_TMPL = DATA
        except Exception:
            _HEADER_TMPL = False
    return _HEADER_TMPL if _HEADER_TMPL is not False else None


def _get_header_stat_templates():
    """Load header_templates.json built by build_header_templates.py."""
    global _HEADER_STAT_TMPL
    if _HEADER_STAT_TMPL is None:
        try:
            from assets.fonts.stat_header import DATA
            _HEADER_STAT_TMPL = DATA
        except Exception:
            _HEADER_STAT_TMPL = False
    return _HEADER_STAT_TMPL if _HEADER_STAT_TMPL is not False else None


def _find_medal_right(panel: np.ndarray) -> int | None:
    """
    Find the right edge of the medal/coin icon in the header bar.

    Crops the right MEDAL_SEARCH_X0 fraction of the header bar — narrow enough
    that the leftmost qualifying blob is reliably the medal (score digits always
    sit to its right).  The medal may binarize into multiple sub-blobs; adjacent
    blobs within MEDAL_BLOB_GAP px are merged into the same object.

    Returns the panel-space x just past the medal's right edge, or None if no
    qualifying blob is found (falls back to SCORE_X0 fraction).
    """
    from gfl2.score_ocr import THRESH_VAL
    ph, pw      = panel.shape[:2]
    y0          = int(ph * HEADER_BAR_Y0)
    y1          = int(ph * HEADER_BAR_Y1)
    x_start     = int(pw * MEDAL_SEARCH_X0)
    min_score_w = 50          # must leave this many px for score digits
    medal_gap   = 10          # max gap (px) between medal sub-blobs

    sub  = panel[y0:y1, x_start:pw]
    gray = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY) if sub.ndim == 3 else sub
    _, thresh = cv2.threshold(gray, THRESH_VAL, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    blobs = []   # (panel_left, panel_right)
    for c in cnts:
        bx, by, bw, bh = cv2.boundingRect(c)
        if bw * bh < MEDAL_MIN_AREA:
            continue
        pl = x_start + bx
        pr = x_start + bx + bw
        if pr + min_score_w > pw:
            continue   # too close to right edge — no room left for score digits
        blobs.append((pl, pr))

    if not blobs:
        return None

    # Take the leftmost blob as the medal anchor.
    blobs.sort(key=lambda b: b[0])
    medal_right = blobs[0][1]

    # Extend rightward through adjacent sub-blobs of the same medal object.
    changed = True
    while changed:
        changed = False
        for pl, pr in blobs:
            if medal_right < pl <= medal_right + medal_gap:
                if pr + min_score_w <= pw:
                    medal_right = pr
                    changed = True

    return medal_right


def _header_isolate_blobs(gray: np.ndarray, inv: bool = False) -> list:
    """Find digit blobs in a crop.  inv=True for dark-on-light text.

    Returns [(x, norm, w, h, n_inner)] where n_inner is the count of interior
    contours (holes) within the blob — used to disambiguate digits like 5 vs 6.
    """
    from gfl2.score_ocr import (THRESH_VAL, NORM_W, NORM_H,
                                DIGIT_MIN_W, DIGIT_MAX_W, DIGIT_MIN_H, DIGIT_MAX_H)
    mode = cv2.THRESH_BINARY_INV if inv else cv2.THRESH_BINARY

    # Width above which a blob is likely two merged digits.
    _MERGE_W = int(NORM_W * 1.3)   # ≈ 26 px

    def _raw_blobs(thresh):
        cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out = []
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            out.append((x, y, w, h))
        out.sort(key=lambda b: b[0])
        return out

    def _normalize(thresh, x, y, w, h):
        sub = thresh[y:y+h, x:x+w]
        return cv2.resize(sub, (NORM_W, NORM_H), interpolation=cv2.INTER_AREA)

    def _count_holes(thresh, x, y, w, h):
        sub = thresh[y:y+h, x:x+w]
        _, hier = cv2.findContours(sub, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if hier is None:
            return 0
        return int(sum(1 for hh in hier[0] if hh[3] >= 0))

    _, thresh_lo = cv2.threshold(gray, THRESH_VAL, 255, mode)
    blobs_lo = _raw_blobs(thresh_lo)

    # Find the lowest threshold increment that separates any merged digit pair.
    # Using the smallest effective delta keeps stroke shapes closest to the
    # templates (which were built at THRESH_VAL).
    thresh_hi = None
    blobs_hi  = []
    for _delta in (5, 10, 15, 20):
        _, _t = cv2.threshold(gray, THRESH_VAL + _delta, 255, mode)
        _rb   = _raw_blobs(_t)
        if len(_rb) > len(blobs_lo):
            thresh_hi = _t
            blobs_hi  = _rb
            break
    if thresh_hi is None:
        _, thresh_hi = cv2.threshold(gray, THRESH_VAL + 10, 255, mode)
        blobs_hi     = _raw_blobs(thresh_hi)

    result = []
    for bx, by, bw, bh in blobs_lo:
        if not (DIGIT_MIN_H <= bh <= DIGIT_MAX_H):
            continue
        if DIGIT_MIN_W <= bw <= _MERGE_W:
            # Normal blob — normalize from the primary threshold image so the
            # pixel shape matches templates built at the same threshold.
            n_inner = _count_holes(thresh_lo, bx, by, bw, bh)
            result.append((bx, _normalize(thresh_lo, bx, by, bw, bh), bw, bh, n_inner))
        elif bw > _MERGE_W:
            # Merged blob — use higher-threshold detections that fall within this
            # blob's x-range to find the split sub-blobs.  Each sub-blob is
            # normalized from thresh_hi so its boundaries are clean; the higher
            # threshold is the minimum delta that achieved the separation, so
            # stroke shapes stay as close as possible to the 150-threshold templates.
            sub_hi = [(hx, hy, hw, hh) for hx, hy, hw, hh in blobs_hi
                      if DIGIT_MIN_W <= hw <= _MERGE_W
                      and DIGIT_MIN_H <= hh <= DIGIT_MAX_H
                      and hx >= bx and hx + hw <= bx + bw + 2]
            for hx, hy, hw, hh in sub_hi:
                nx  = max(0, hx);  nx1 = min(thresh_hi.shape[1], hx + hw)
                ny  = max(0, hy);  ny1 = min(thresh_hi.shape[0], hy + hh)
                n_inner = _count_holes(thresh_hi, nx, ny, nx1 - nx, ny1 - ny)
                result.append((hx, _normalize(thresh_hi, nx, ny, nx1 - nx, ny1 - ny),
                               hw, hh, n_inner))
            # If no valid sub-blobs at higher threshold, the merged blob is dropped.
    result.sort(key=lambda b: b[0])
    return result


def _read_bright_number(gray: np.ndarray, templates: dict, allow_km: bool = False,
                        inv: bool = False, proj_min: float = None,
                        return_partial: bool = False):
    """
    Read a number from a single-channel crop using digit templates.
    allow_km: if True, an unrecognised trailing blob is treated as a K/M suffix.
    inv: True for dark-on-light text (stats row).
    proj_min: override projection correlation threshold (default: PROJ_CORR_MIN from score_detect).
    return_partial: if True, return the raw string with '?' markers instead of None on failure.
    Returns a string like "4246K" or "3820", or None if uncertain (unless return_partial=True).
    """
    from gfl2.score_ocr import (_features, _proj_correlation, _hu_distance,
                                PROJ_CORR_MIN, HU_THRESHOLD)
    # Digits that normally have interior holes (closed loops).
    _HOLE_DIGITS    = {'0', '6', '8', '9'}
    _NO_HOLE_DIGITS = {'1', '2', '3', '5', '7'}

    _proj_min = proj_min if proj_min is not None else PROJ_CORR_MIN
    blobs = _header_isolate_blobs(gray, inv=inv)
    if not blobs:
        return None
    result = []
    trailing_km = None
    for x, norm, w, h, n_inner in blobs:
        hu, proj = _features(norm)
        proj_scores = {d: _proj_correlation(proj, t["proj"]) for d, t in templates.items()}
        best_d  = max(proj_scores, key=proj_scores.get)
        best_pc = proj_scores[best_d]
        if best_pc >= _proj_min:
            # If the blob has interior holes but the top proj match is a no-hole
            # digit (e.g. '5' matching a '6'), prefer the best-scoring hole-digit.
            if n_inner >= 1 and best_d in _NO_HOLE_DIGITS:
                hole_scores = {d: proj_scores[d] for d in _HOLE_DIGITS if d in proj_scores}
                if hole_scores:
                    hole_best = max(hole_scores, key=hole_scores.get)
                    if hole_scores[hole_best] >= _proj_min * 0.90:
                        best_d = hole_best
            result.append(best_d)
            continue
        best_digit, best_dist = "?", float("inf")
        for digit, tmpl in templates.items():
            d = _hu_distance(hu, tmpl["hu"])
            if d < best_dist:
                best_dist, best_digit = d, digit
        if best_dist <= HU_THRESHOLD:
            result.append(best_digit)
        elif allow_km and result:
            # Unrecognised blob after at least one digit — treat as K or M suffix.
            # K is narrower than M relative to its height.
            trailing_km = "K" if (w / h) < 0.75 else "M"
            break
        else:
            result.append("?")
    if not result:
        return None
    s = "".join(result)
    if "?" in s:
        return s if return_partial else None
    return s + trailing_km if trailing_km else s


# ── Panel detection ───────────────────────────────────────────────────────────

def _find_all_frames(image: np.ndarray) -> list:
    """Find all portrait frames in the full image in one contour pass.

    Scans the entire image rather than a pre-split panel, making panel
    discovery and frame detection a single step.  Portrait frames drive
    panel splitting (not header brightness).  Size-outlier filter eliminates
    dividers/headers that pass the squareness test.

    Returns (x, y, w, h) in absolute image coordinates.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bg   = int(np.bincount(gray.flatten()).argmax())
    mask = (np.abs(gray.astype(int) - bg) > FRAME_BG_DELTA).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cands = []
    for c in cnts:
        x, y, cw, ch = cv2.boundingRect(c)
        if cw >= FRAME_MIN_DIM and ch >= FRAME_MIN_DIM:
            if min(cw, ch) / max(cw, ch) >= FRAME_MIN_SQ:
                cands.append((x, y, cw, ch))
    if not cands:
        return []
    max_area = max(cw * ch for _, _, cw, ch in cands)
    return [(x, y, cw, ch) for x, y, cw, ch in cands
            if cw * ch >= max_area * FRAME_OUTLIER_RATIO]


def _group_frames_into_panels(frames: list) -> list[list]:
    """Cluster portrait frames into per-panel groups by x-proximity.

    Frames in one report share nearly the same x (same portrait column,
    stacked vertically).  Frames in different reports are separated by
    hundreds of pixels.  Groups are sorted by x then each group by y
    (top-to-bottom row order).

    NOTE: currently handles left-right panel layouts only.  Top-bottom
    stacking (vertically arranged panels) is not yet supported.
    """
    if not frames:
        return []
    by_x = sorted(frames, key=lambda f: f[0])
    groups: list[list] = [[by_x[0]]]
    for f in by_x[1:]:
        if f[0] - groups[-1][-1][0] < _FRAME_GROUP_X_GAP:
            groups[-1].append(f)
        else:
            groups.append([f])
    return [sorted(g, key=lambda b: b[1]) for g in groups]


def _panel_bounds_from_groups(groups: list[list], image_w: int) -> list[tuple[int, int]]:
    """Compute panel x-slices from frame groups.

    Split points are the midpoints between adjacent groups' anchor x-positions,
    preserving panel-width-fraction constants (STATS_*_X etc.) correctly.
    """
    anchor_xs = [min(f[0] for f in g) for g in groups]
    bounds = []
    for i, ax in enumerate(anchor_xs):
        x0 = 0 if i == 0 else (anchor_xs[i - 1] + ax) // 2
        x1 = image_w if i == len(anchor_xs) - 1 else (ax + anchor_xs[i + 1]) // 2
        bounds.append((x0, x1))
    return bounds


def _split_panels(image: np.ndarray) -> list[np.ndarray]:
    """Header-brightness heuristic split — fallback when frame detection fails.

    Finds the brightest column in the middle third of the top 10% bar; treats
    it as the panel divider if it falls between 40-60% of image width.
    Used by stat_ocr --verify, build.py, and doll_name_ocr --build for
    template-building passes where frame-based splitting is not needed.
    """
    h, w  = image.shape[:2]
    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bar   = gray[:int(h * 0.10), :]
    third = w // 3
    mid   = third + int(np.argmax(bar.mean(axis=0)[third: 2 * third]))
    if mid < w * 0.40 or mid > w * 0.60:
        return [image]
    return [image[:, :mid], image[:, mid:]]


# ── Header & row extraction ───────────────────────────────────────────────────

def _extract_header(panel: np.ndarray, timer: TimerStack,
                    filename: str = "unknown", panel_idx: int = 0,
                    frames: list | None = None) -> dict:
    with timer.timed("extract_header"):
        tmpl   = _get_header_templates()
        ph, pw = panel.shape[:2]

        if frames is None:
            frames = _find_frames(panel)

        # ── score ──────────────────────────────────────────────────────────────
        medal_right = _find_medal_right(panel)
        fw      = frames[0][2] if frames else 89
        sc_y0   = int(ph * HEADER_BAR_Y0) + 3
        sc_y1   = int(ph * HEADER_BAR_Y1) - 3
        sc_x0   = ((medal_right + 2) if medal_right is not None else int(pw * SCORE_X0)) + 3
        sc_w    = int(fw * SCORE_CROP_W_FR)
        sc      = panel[sc_y0:sc_y1, sc_x0:min(sc_x0 + sc_w, pw)]
        score = None
        if tmpl is not None and sc.size > 0:
            with timer.timed("score/blob"):
                gray_sc   = cv2.cvtColor(sc, cv2.COLOR_BGR2GRAY) if sc.ndim == 3 else sc
                blob_score = _read_bright_number(gray_sc, tmpl, return_partial=True)
                score      = blob_score if (blob_score and '?' not in blob_score) else None
        else:
            blob_score = None
        if score is None:
            with timer.timed("score/tess"):
                for thresh_val in (150, 160, 170, 180, 190):
                    stxt = _ocr_bright(sc, thresh_val,
                                       "--psm 7 -c tessedit_char_whitelist=0123456789")
                    sm = re.search(r"\d{3,}", stxt)
                    if sm:
                        score = sm.group(0)
                        break
                if _SAVE_TESS_CROPS and sc.size > 0:
                    _FALLBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(str(_FALLBACK_LOG.parent /
                                    f"{filename}_p{panel_idx+1}_score.png"), sc)
                _TESS_FALLBACKS.append({
                    "file": filename, "panel": panel_idx + 1,
                    "field": "score", "blob": blob_score, "got": score,
                })

        # ── stats row ──────────────────────────────────────────────────────────
        # frames already computed above (reused from score section)
        if frames:
            _, fy0, _, fh0 = frames[0]
            sy0 = fy0 - int(fh0 * STATS_ROW_Y0_FR)
            sy1 = fy0 - int(fh0 * STATS_ROW_Y1_FR)
        else:
            sy0 = int(ph * STATS_ROW_Y0)
            sy1 = int(ph * STATS_ROW_Y1)

        def _stats_crop(x_range):
            x0 = max(0, int(pw * x_range[0]))
            x1 = min(pw, int(pw * x_range[1]))
            return panel[sy0:sy1, x0:x1]

        dealt = taken = turns = None
        hdr_stat_tmpl = _get_header_stat_templates()
        if hdr_stat_tmpl is not None:
            with timer.timed("stats_row/blob"):
                from gfl2.stat_ocr import (BLOB_MIN_W, BLOB_MAX_W, BLOB_MAX_H,
                                            _filter_y_outliers,
                                            _extract_val_glyphs, _reconstruct_val)
                # Lower threshold separates touching digits (e.g. '4'+'8' merge at 180).
                # Min-height 12 filters comma blobs (h≈5-7) and UI-chrome noise (h<10).
                _HDR_THRESH     = 155
                _HDR_BLOB_MIN_H =  12
                def _drop_label_bleed(blobs, gap_thresh=15):
                    # Drop blobs to the left of the first inter-blob gap > gap_thresh px.
                    # Handles label chars (e.g. trailing 't' of "Damage dealt") bleeding
                    # into the crop when the value is short; digit gaps are 2–10 px.
                    s = sorted(blobs, key=lambda b: b[0])
                    for i in range(len(s) - 1):
                        gap = s[i + 1][0] - (s[i][0] + s[i][2])
                        if gap > gap_thresh:
                            return s[i + 1:]
                    return s
                def _read_stat_crop(fr_range):
                    sub = _stats_crop(fr_range)
                    if sub.size == 0:
                        return None
                    gray = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY) if sub.ndim == 3 else sub
                    _, thresh = cv2.threshold(gray, _HDR_THRESH, 255, cv2.THRESH_BINARY_INV)
                    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)
                    raw_blobs = []
                    for _c in cnts:
                        _x, _y, _w, _h = cv2.boundingRect(_c)
                        if (BLOB_MIN_W <= _w <= BLOB_MAX_W
                                and _HDR_BLOB_MIN_H <= _h <= BLOB_MAX_H):
                            raw_blobs.append((_x, _y, _w, _h))
                    blobs = _drop_label_bleed(_filter_y_outliers(
                        sorted(raw_blobs, key=lambda b: (b[1], b[0]))))
                    if not blobs:
                        return None
                    glyphs = _extract_val_glyphs(blobs, thresh)
                    return _reconstruct_val(glyphs, hdr_stat_tmpl)
                dealt = _read_stat_crop(STATS_DEALT_X)
                taken = _read_stat_crop(STATS_TAKEN_X)
                turns = _read_stat_crop(STATS_TURNS_X)
                # strip any '?' — treat partial reads as failures
                if dealt and '?' in dealt: dealt = None
                if taken and '?' in taken: taken = None
                if turns and '?' in turns: turns = None

        # Tesseract fallback for any field blob could not read
        if dealt is None or taken is None or turns is None:
            _missing = [f for f, v in
                        [("dealt", dealt), ("taken", taken), ("turns", turns)]
                        if v is None]
            blob_dealt, blob_taken, blob_turns = dealt, taken, turns
            with timer.timed("stats_row/tess"):
                txt = _ocr_raw(panel[sy0:sy1, :], "--psm 6")
                def _find(pat):
                    m = re.search(pat, txt, re.IGNORECASE)
                    return m.group(1).replace(",", "") if m else None
                if dealt is None:
                    dealt = _find(r"[Dd]amage\s*[Dd]ealt\s+([\d,.KMkm]+)")
                if taken is None:
                    taken = _find(r"[Dd]amage\s*[Tt]aken\s+([\d,.]+)")
                if turns is None:
                    turns = _find(r"[Cc]ombat\s*[Tt]urns?\s*(\d+)")
                if _SAVE_TESS_CROPS:
                    _FALLBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
                    _pi = panel_idx + 1
                    for _fname, _xr in [("dealt", STATS_DEALT_X),
                                        ("taken", STATS_TAKEN_X),
                                        ("turns", STATS_TURNS_X)]:
                        if _fname in _missing:
                            _c = _stats_crop(_xr)
                            if _c.size > 0:
                                cv2.imwrite(str(_FALLBACK_LOG.parent /
                                               f"{filename}_p{_pi}_{_fname}.png"), _c)
                _TESS_FALLBACKS.append({
                    "file": filename, "panel": panel_idx + 1,
                    "field": "stats_row", "missing": _missing,
                    "blob": {"dealt": blob_dealt, "taken": blob_taken, "turns": blob_turns},
                    "got":  {"dealt": dealt,      "taken": taken,      "turns": turns},
                })

    return {
        "score":           score,
        "dmg_dealt_total": dealt,
        "dmg_taken_total": taken,
        "combat_turns":    turns,
    }


def _find_frames(panel: np.ndarray) -> list:
    """Per-panel frame finder — used only in the legacy fallback path."""
    frames = _find_all_frames(panel)
    return sorted(frames, key=lambda b: b[1])[:5]

def _frame_col_cell(
    panel: np.ndarray,
    fx: int, fy: int, fw: int, fh: int,
    col_fr: tuple,
) -> np.ndarray:
    """Extract a stat-cell strip using frame-relative coordinates.

    x: FR = fx+fw, then offset by col_fr multiples of fw.
    y: CELL_Y_FR multiples of fh from frame top, giving a fixed-height
       strip that spans both the pct and val text lines.

    All offsets scale with the detected frame size so crops are
    resolution-independent and identical between training and inference.
    """
    ph, pw = panel.shape[:2]
    fr  = fx + fw
    x0  = max(0, fr + int(fw * col_fr[0]))
    x1  = min(pw, fr + int(fw * col_fr[1]))
    y0  = max(0, fy + int(fh * CELL_Y_FR[0]))
    y1  = min(ph, fy + int(fh * CELL_Y_FR[1]))
    return panel[y0:y1, x0:x1]


def _extract_stat_cell(cell: np.ndarray, timer: TimerStack):
    """Return (pct, val, meta) where meta is a dict with fallback info, or {} if blob succeeded."""
    engine = _get_stat_ocr()
    blob_pct = blob_val = None
    if engine is not None:
        with timer.timed("stat_cell/blob"):
            blob_pct, blob_val = engine.read(cell, timer=timer)
        if blob_pct is not None and blob_val is not None:
            return blob_pct, blob_val, {}

    # At least one strip returned None — run Tesseract on the whole cell.
    with timer.timed("stat_cell/psm6"):
        txt = _ocr_raw(cell, "--psm 6")
    tess_pct, tess_val = _parse_pct_val(txt)
    used_psm4 = False
    if tess_val is None or len(tess_val) <= 2:
        with timer.timed("stat_cell/psm4"):
            txt2 = _ocr_raw(cell, "--psm 4")
        _, tess_val2 = _parse_pct_val(txt2)
        if tess_val2 and (tess_val is None or len(tess_val2) > len(tess_val)):
            tess_val = tess_val2
            used_psm4 = True

    strips = []
    if blob_pct is None: strips.append("pct")
    if blob_val is None: strips.append("val")

    pct = blob_pct if blob_pct is not None else tess_pct
    val = blob_val if blob_val is not None else tess_val
    meta = {
        "strips": strips, "psm4": used_psm4,
        "blob_pct": blob_pct, "blob_val": blob_val,
    }
    return pct, val, meta


_TESS_FALLBACKS: list[dict] = []   # accumulated across parse() calls; reset each run
_SAVE_TESS_CROPS: bool = False


def _extract_doll_rows(panel: np.ndarray, timer: TimerStack,
                       filename: str = "unknown", panel_idx: int = 0,
                       frames: list | None = None):
    with timer.timed("extract_doll_rows"):
        h, w = panel.shape[:2]

        if frames is None:
            with timer.timed("find_frames"):
                frames = _find_frames(panel)

        if not frames:
            return []

        ax, ay, aw, ah = frames[0]
        name_x0 = ax + aw + 2
        name_x1 = name_x0 + round(w * NAME_W_FRAC)

        _COL_NAMES = ("dmg_dealt", "stability", "dmg_taken", "healed")
        _COL_FRS   = (COL1_FR, COL2_FR, COL3_FR, COL4_FR)

        rows = []
        for i, (fx, fy, fw, fh) in enumerate(frames):
            with timer.timed("crop_portrait"):
                portrait = _crop_portrait(panel, fx, fy, fw, fh)

            name_cell = panel[fy:fy + fh, name_x0:name_x1]

            with timer.timed("name/proj"):
                _ocr = _get_doll_name_ocr()
                name = _ocr.classify(name_cell) if _ocr is not None else None
            if name is not None:
                with timer.timed("fuzzy_correct"):
                    name = _fuzzy_correct(name)

            if name is None:
                with timer.timed("name"):
                    name = _extract_name(name_cell)
                if name:
                    with timer.timed("fuzzy_correct"):
                        name = _fuzzy_correct(name)
                    if name in _known_doll_names():
                        _NEW_CROPS.append((name_cell.copy(), name))

            if name and portrait.size > 0:
                with timer.timed("save_portrait"):
                    _save_doll_portrait(name, portrait)

            vals = []
            for col_name, col_fr in zip(_COL_NAMES, _COL_FRS):
                cell = _frame_col_cell(panel, fx, fy, fw, fh, col_fr)
                p, v, meta = _extract_stat_cell(cell, timer)
                vals.extend([p, v])
                if meta.get("strips"):
                    if _SAVE_TESS_CROPS and cell.size > 0:
                        _FALLBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
                        cv2.imwrite(str(_FALLBACK_LOG.parent /
                                        f"{filename}_p{panel_idx+1}_r{i}_{col_name}.png"), cell)
                    _TESS_FALLBACKS.append({
                        "file": filename, "panel": panel_idx + 1,
                        "row": i, "col": col_name,
                        "strips": meta["strips"],
                        "psm4": meta["psm4"],
                        "blob_pct": meta.get("blob_pct"),
                        "blob_val": meta.get("blob_val"),
                        "pct": p, "val": v,
                    })

            dp, dv, sp, sv, tp, tv, hp, hv = vals
            rows.append(DollRow(name, dp, dv, sp, sv, tp, tv, hp, hv))

    return rows


_FALLBACK_LOG = Path(__file__).parent.parent.parent / "tests" / "outputs" / "daily" / "stat_tess_fallbacks.json"


def parse(image, filename="unknown", timer=None, **_):
    if timer is None:
        timer = TimerStack()

    # Panel BOUNDS: brightness-based header split (preserves width-fraction constants).
    # Frame detection: one full-image pass; groups assigned to panels by count match.
    split = _split_panels(image)
    all_frames = _find_all_frames(image)
    groups     = _group_frames_into_panels(all_frames)

    if groups and len(groups) == len(split):
        # Compute x0 of each panel from the brightness split widths.
        x0s = [0]
        for p in split[:-1]:
            x0s.append(x0s[-1] + p.shape[1])
        panel_list = []
        for panel, group, x0 in zip(split, groups, x0s):
            panel_frames = [(fx - x0, fy, fw, fh) for fx, fy, fw, fh in group]
            panel_list.append((panel, panel_frames))
    else:
        # Fallback: panel count mismatch or no frames detected — skip pre-computed frames.
        panel_list = [(_p, None) for _p in split]

    entries = []
    for idx, (panel, panel_frames) in enumerate(panel_list):
        hdr   = _extract_header(panel, timer, filename=filename, panel_idx=idx,
                                 frames=panel_frames)
        dolls = _extract_doll_rows(panel, timer, filename=filename, panel_idx=idx,
                                    frames=panel_frames)
        entries.append(ReportEntry(
            filename        = filename,
            report_idx      = idx + 1,
            score           = hdr.get("score"),
            dmg_dealt_total = hdr.get("dmg_dealt_total"),
            dmg_taken_total = hdr.get("dmg_taken_total"),
            combat_turns    = hdr.get("combat_turns"),
            dolls           = dolls,
        ))
    return entries


def set_save_tess_crops(enabled: bool) -> None:
    global _SAVE_TESS_CROPS
    _SAVE_TESS_CROPS = enabled


def flush_tess_fallbacks() -> int:
    """Overwrite tests/outputs/daily/stat_tess_fallbacks.json with this run's fallbacks."""
    import json
    n = len(_TESS_FALLBACKS)
    _FALLBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
    _FALLBACK_LOG.write_text(json.dumps(_TESS_FALLBACKS, indent=2), encoding="utf-8")
    _TESS_FALLBACKS.clear()
    return n
