# -*- coding: utf-8 -*-
"""
stat_ocr.py — Blob + projection/Hu moment OCR for Daily Gunsmoke stat cells.

Character set: 0-9, '.', 'K', 'M'
The trailing '%' on the pct line is always appended by convention; its sub-blobs
are detected structurally (two small square glyphs after the last large digit)
and stripped before classification — no template needed.

Cell layout (trimmed 90 px height, varying width at native resolution):
  pct line  (y ≈ 41–61)   large digits ~20 px tall  e.g. "35.38%"
  val line  (y ≈ 70–83)   small digits ~13 px tall  e.g. "665669"

Template storage:
  assets/fonts/stat_pct.json + stat_val.json
  {"pct": {char: {"proj": [...], "hu": [...], "n": N}},
   "val": {char: {…}}}

Build templates:
    python stat_ocr.py --build [--images <glob>] [--font <name>] [--save-crops]

Verify pipeline against Tesseract ground truth:
    python stat_ocr.py --verify [--images <glob>]
"""
from __future__ import annotations
import json, math, sys, time, glob as _glob
from datetime import datetime
from contextlib import nullcontext as _nullctx
from pathlib import Path
from typing import Optional
import cv2
import numpy as np

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE        = Path(__file__).parent.parent          # project root
_FONTS_DIR   = _HERE / "assets" / "fonts"
PCT_TMPL_F   = _FONTS_DIR / "stat_pct.py"
VAL_TMPL_F   = _FONTS_DIR / "stat_val.py"
STAT_SET_DIR = _HERE / "tests" / "inputs" / "daily"

# ── Binarization ──────────────────────────────────────────────────────────────
THRESH_BIN = 180   # THRESH_BINARY_INV; text is gray/orange on near-white bg

# ── Blob size filters (native resolution) ────────────────────────────────────
BLOB_MIN_W, BLOB_MAX_W = 2, 30
BLOB_MIN_H, BLOB_MAX_H = 2, 30
BLOB_MIN_X             =  0   # frame-relative crops start at text edge; no left-edge filter needed

# ── Line-split helpers ────────────────────────────────────────────────────────
LARGE_H_MIN  = 14   # pct-line digit blobs:  h ≈ 19–21 px
DOT_MAX_DIM  =  8   # '.' blob: w ≤ DOT_MAX_DIM AND h ≤ DOT_MAX_DIM
# % detection
PCT_MERGED_W = 18   # merged-% blob width threshold (all 3 parts fused → w ≥ 18)

# ── Normalised glyph dims for feature vectors ─────────────────────────────────
NORM_W_PCT, NORM_H_PCT = 12, 20   # pct-line (large) glyphs
NORM_W_VAL, NORM_H_VAL =  8, 13   # val-line (small) glyphs

# ── Classifier thresholds ─────────────────────────────────────────────────────
PROJ_CORR_MIN    = 0.70   # combined (v+h)/2 score; was 0.75 for v-only
PROJ_VERY_LOW    = 0.35   # if best proj < this, Hu fallback is unreliable → return '?'
                          # prevents K (proj≈0.27) from misfiring via Hu to a digit
HU_DIST_MAX      = 0.30
HU_HALF_DIST_MAX = 0.60   # combined top+bot half-Hu MAD threshold

# 2-vs-3 discriminator (docs/known_issues.txt §15): neither digit has an
# enclosed hole, so _count_inner_blobs can't tell them apart.  '2' always
# ends in a full-width flat bottom stroke; '3' always curls inward at the
# bottom.  Measured on confirmed samples: '2' bottom row = 0.875 (8px val
# canvas), '3' bottom row <= 0.625 — thresholds sit in the observed gap.
TWO_BOTTOM_FULL_MIN = 0.80   # bottom row this wide or wider -> rule out '3'
THREE_BOTTOM_CURL_MAX = 0.70 # bottom row this narrow or narrower -> rule out '2'

# ── Within-cell y-strip boundaries (fractions of combined cell height) ────────
# Derived from CELL_Y_FR=(0.20, 0.90), calibrated at fh=88.
# All pct-line blobs have cy_frac ≈ 0.21; val-line blobs have cy_frac ≈ 0.61.
# Within-cell y-strip boundaries (fractions of combined cell height).
# pct-line blob centres ≈ 0.21; val-line blob centres ≈ 0.61.
# pct strip is generous to fully capture the % descender (avoids %-as-7 errors).
# val strip extends to 1.00 so the bottom of the last val row is never clipped.
# Within-cell y-strip boundaries (fractions of combined cell height).
# pct-line blob centres ≈ 0.21; val-line blob centres ≈ 0.61.
# pct strip ends at 0.46 (slightly past tallest pct glyph bottom at ~0.37)
# to ensure % and tall digits are never vertically clipped.
# val strip starts at 0.44 (below pct glyphs, above val glyph tops at ~0.47).
PCT_STRIP_Y = (0.00, 0.46)   # pct-only strip: top 46% of combined cell
VAL_STRIP_Y = (0.50, 0.82)   # val-only strip: 50–82% of combined cell (≥0.50 clears pct bleed)

# ── Training character sets ───────────────────────────────────────────────────
TRAIN_CHARS = list("0123456789KM")   # '.' handled by size; '%' stripped


# ─────────────────────────────────────────────────────────────────────────────
# Feature helpers  (mirrored from gfl2/score_ocr.py)
# ─────────────────────────────────────────────────────────────────────────────

def _v_projection(norm: np.ndarray) -> list[float]:
    """1D vertical projection: avg pixel value per column, normalised 0-1."""
    proj = norm.mean(axis=0).tolist()
    mx   = max(proj) or 1.0
    return [v / mx for v in proj]


def _h_projection(norm: np.ndarray) -> list[float]:
    """1D horizontal projection: avg pixel value per row, normalised 0-1."""
    proj = norm.mean(axis=1).tolist()
    mx   = max(proj) or 1.0
    return [v / mx for v in proj]


def _hu_moments(norm: np.ndarray) -> list[float]:
    """7 Hu moments, log-scaled."""
    m  = cv2.moments(norm)
    hu = cv2.HuMoments(m).flatten()
    eps = 1e-10
    return [-math.copysign(1.0, v) * math.log10(abs(v) + eps) for v in hu]


def _half_hu_moments(norm: np.ndarray) -> tuple[list[float], list[float]]:
    """Compute Hu moments separately for the top and bottom halves of norm.

    Splitting before computing Hu moments breaks the rotation invariance
    that makes full-glyph Hu unreliable for pairs like '2'/'3' and '5'/'8':
    their top and bottom halves have structurally distinct moment signatures
    even though the full-glyph moments are close.

    Returns (top_hu, bot_hu) — each a list of 7 log-scaled floats.
    """
    mid = max(1, norm.shape[0] // 2)
    return _hu_moments(norm[:mid, :]), _hu_moments(norm[mid:, :])


def _proj_corr(a: list[float], b: list[float]) -> float:
    """Pearson correlation between two projection vectors."""
    a_, b_ = np.array(a), np.array(b)
    if a_.std() < 1e-6 or b_.std() < 1e-6:
        return 0.0
    return float(np.corrcoef(a_, b_)[0, 1])


def _hu_dist(a: list[float], b: list[float]) -> float:
    """Mean absolute distance between two Hu moment vectors."""
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def _count_inner_blobs(norm: np.ndarray, min_area: int = 4) -> int:
    """Count enclosed holes inside a normalised glyph image.

    Uses RETR_CCOMP contour hierarchy: any contour with a parent (hierarchy[i][3] >= 0)
    is a hole boundary.  Holes with area < min_area are ignored to filter out
    1-3px interpolation artifacts that appear when a 19px-tall '4' is stretched
    to NORM_H_PCT=20 — the tiny resize artifact would otherwise be counted as a
    second inner blob, confusing '4' with '8'.

    Expected counts for each digit/char:
        0 holes : 1, 2, 3, 5, 7, K, M, '.'
        1 hole  : 0, 4, 6, 9
        2 holes : 8

    At very small sizes (e.g. NORM_W_VAL=8) holes may close due to interpolation or
    thin strokes; the function then returns 0.  Callers should only use the result as
    a hard constraint when it is > 0 (a hole that IS there cannot be imagined away).
    """
    # Re-threshold after resize smear
    _, binary = cv2.threshold(norm, 127, 255, cv2.THRESH_BINARY)
    cnts, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        return 0
    count = 0
    for i, row in enumerate(hierarchy[0]):
        if row[3] >= 0 and cv2.contourArea(cnts[i]) >= min_area:
            count += 1
    return count


def _bottom_row_width_frac(norm: np.ndarray) -> float:
    """Width of the foreground span in the glyph's last row, as a fraction of
    NORM_W.  Distinguishes '2' (flat bottom stroke, spans nearly full width)
    from '3' (curls inward, spans well under half) — see TWO_BOTTOM_FULL_MIN /
    THREE_BOTTOM_CURL_MAX and docs/known_issues.txt §15.
    """
    w = norm.shape[1]
    cols = np.where(norm[-1, :] > 127)[0]
    if cols.size == 0:
        return 0.0
    return float(cols[-1] - cols[0] + 1) / w


def _features(norm: np.ndarray) -> tuple:
    top_hu, bot_hu = _half_hu_moments(norm)
    inner = _count_inner_blobs(norm)
    return _hu_moments(norm), _v_projection(norm), _h_projection(norm), top_hu, bot_hu, inner


# ─────────────────────────────────────────────────────────────────────────────
# Blob detection & line splitting
# ─────────────────────────────────────────────────────────────────────────────

def _binarize(cell: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY) if cell.ndim == 3 else cell
    _, t = cv2.threshold(gray, THRESH_BIN, 255, cv2.THRESH_BINARY_INV)
    return t


def _find_blobs(thresh: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Return [(x, y, w, h)] filtered by BLOB_MIN/MAX, sorted y then x.

    Blobs at x < BLOB_MIN_X are discarded: they are left-edge UI artifacts
    (column borders, adjacent-column bleed) that fall between the two text
    lines and corrupt the y-gap used by _split_lines.
    """
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if x < BLOB_MIN_X:
            continue
        if BLOB_MIN_W <= w <= BLOB_MAX_W and BLOB_MIN_H <= h <= BLOB_MAX_H:
            blobs.append((x, y, w, h))
    return sorted(blobs, key=lambda b: (b[1], b[0]))


def _filter_y_outliers(
    blobs: list[tuple], threshold: int = 12
) -> list[tuple]:
    """
    Remove blobs whose y-centroid differs from the group median by more than
    `threshold` pixels.  Handles noise blobs that leak across the line split
    (e.g. a stray pixel below the val digits that would be detected as '.').

    Groups of ≤ 2 are returned unchanged to avoid removing legitimate glyphs.
    """
    if len(blobs) <= 2:
        return blobs
    cys = sorted(b[1] + b[3] // 2 for b in blobs)
    median_cy = cys[len(cys) // 2]
    return [b for b in blobs if abs(b[1] + b[3] // 2 - median_cy) <= threshold]


def _split_lines(
    blobs: list[tuple[int, int, int, int]],
) -> tuple[list, list]:
    """
    Split blobs into (pct_blobs, val_blobs) by finding the largest
    y-centroid gap.  Falls back to height-based split if gap < 6 px.
    Within-group y-outliers (> 12 px from median) are removed after the split
    to eliminate stray noise blobs that would corrupt glyph extraction.
    """
    if not blobs:
        return [], []

    by_cy = sorted(blobs, key=lambda b: b[1] + b[3] // 2)
    cys   = [b[1] + b[3] // 2 for b in by_cy]

    if len(cys) == 1:
        b = blobs[0]
        return (blobs, []) if b[3] >= LARGE_H_MIN else ([], blobs)

    gaps      = [(cys[i + 1] - cys[i], i) for i in range(len(cys) - 1)]
    gap_size, split_idx = max(gaps)

    if gap_size < 6:
        # No clear gap — use height as proxy
        pct = [b for b in blobs if b[3] >= LARGE_H_MIN]
        val = [b for b in blobs if b[3] <  LARGE_H_MIN]
        return _filter_y_outliers(pct), _filter_y_outliers(val)

    pct_group = _filter_y_outliers(by_cy[: split_idx + 1])
    val_group = _filter_y_outliers(by_cy[split_idx + 1 :])
    return pct_group, val_group


# ─────────────────────────────────────────────────────────────────────────────
# Glyph extraction (strip %, identify '.')
# ─────────────────────────────────────────────────────────────────────────────

def _find_percent_x_start(blobs: list[tuple]) -> Optional[int]:
    """
    Detect the x-start of the '%' glyph cluster and return the x position
    from which all remaining blobs should be treated as % sub-blobs (skip).

    Two cases for how '%' renders at native resolution:

    Case A — Merged blob (all three parts fused into one wide glyph):
      Rightmost large blob has w ≥ PCT_MERGED_W.
      → pct_x_start = that blob's x.

    Case B — Split blobs (top circle + diagonal slash + bottom circle):
      Bottom circle is a small square blob with y > min_y + 6.
      To avoid confusing the decimal point '.' (also a y-outlier) with
      the bottom circle, we require the candidate to be in the RIGHT HALF
      of the pct blob x-range (position ≥ 0.5 of x_range).
      → pct_x_start = bottom_circle.x − 25 px.
    """
    if not blobs:
        return None

    sorted_x = sorted(blobs, key=lambda b: b[0])

    # Case A: merged % (all three sub-glyphs fused into one wide blob).
    # The merged '%' is roughly square (w/h ≈ 1.0), while pct digits are
    # taller than wide (w/h ≈ 0.7).  Accept if either the classic width
    # threshold fires (w ≥ PCT_MERGED_W=18) OR the glyph is nearly square
    # (w ≥ h * 0.90) — catches '%' blobs whose width falls just below 18
    # (observed w=17 at native resolution on some screenshots).
    # Back up 10 px to absorb any stray sub-blobs to the left of the fused glyph.
    rightmost = sorted_x[-1]
    if ((rightmost[2] >= PCT_MERGED_W or rightmost[2] >= rightmost[3] * 0.90)
            and rightmost[3] >= LARGE_H_MIN):
        return max(0, rightmost[0] - 10)

    # Case B: split % — bottom circle must be in the right half of x-range
    x_min   = sorted_x[0][0]
    x_max   = max(b[0] + b[2] for b in sorted_x)
    x_range = x_max - x_min or 1
    min_y   = min(b[1] for b in blobs)

    candidates = [
        b for b in blobs
        if b[1] > min_y + 6          # y-outlier: lower than main glyphs
        and b[2] <= 14 and b[3] <= 14  # small square
        and (b[0] - x_min) / x_range >= 0.5   # right half of x-range
    ]
    if not candidates:
        return None

    bottom = max(candidates, key=lambda b: b[0])   # rightmost
    return max(0, bottom[0] - 25)


def _extract_pct_glyphs(
    pct_blobs: list[tuple],
    thresh:    np.ndarray,
) -> list[tuple[int, Optional[np.ndarray], str]]:
    """
    Return [(x, norm_or_None, hint)] for the pct line.
    hint ∈ {'digit', '.', 'skip'}   ('skip' = % sub-blob, ignored)

    Algorithm:
      1. Detect '%' cluster via y-outlier (bottom circle of %).
         All blobs with x >= pct_x_start are marked 'skip'.
      2. Tiny blobs (w ≤ DOT_MAX_DIM AND h ≤ DOT_MAX_DIM) → hint='.'.
      3. Remaining blobs → hint='digit', normalised to NORM_W_PCT × NORM_H_PCT.
    """
    if not pct_blobs:
        return []

    blobs = sorted(pct_blobs, key=lambda b: b[0])  # sort by x

    pct_x = _find_percent_x_start(blobs)  # None if no % detected

    result = []
    for (x, y, w, h) in blobs:
        if pct_x is not None and x >= pct_x:
            result.append((x, None, 'skip'))
            continue
        if w <= DOT_MAX_DIM and h <= DOT_MAX_DIM:
            result.append((x, None, '.'))
        else:
            crop = thresh[y: y + h, x: x + w]
            norm = cv2.resize(crop, (NORM_W_PCT, NORM_H_PCT),
                              interpolation=cv2.INTER_AREA)
            result.append((x, norm, 'digit'))

    return result


def _extract_val_glyphs(
    val_blobs: list[tuple],
    thresh:    np.ndarray,
) -> list[tuple[int, Optional[np.ndarray], str]]:
    """
    Return [(x, norm_or_None, hint)] for the val line.
    Tiny blobs (both dims ≤ DOT_MAX_DIM) → hint='.'.
    """
    result = []
    for (x, y, w, h) in sorted(val_blobs, key=lambda b: b[0]):
        if w <= DOT_MAX_DIM and h <= DOT_MAX_DIM:
            result.append((x, None, '.'))
        else:
            crop = thresh[y: y + h, x: x + w]
            norm = cv2.resize(crop, (NORM_W_VAL, NORM_H_VAL),
                              interpolation=cv2.INTER_AREA)
            result.append((x, norm, 'digit'))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Classifier
# ─────────────────────────────────────────────────────────────────────────────

def _classify(norm: np.ndarray, templates: dict, v_primary: bool = False,
              acc: "list[float] | None" = None) -> str:
    """
    Combined projection correlation (primary) → Hu moment distance (fallback).

    Primary score: average of vertical-projection correlation and
    horizontal-projection correlation.  Using both axes gives better
    discrimination for digit pairs that differ mainly in row-density
    profile (e.g. '4' vs '2': '4' has near-zero energy in the top rows
    while '2' has a full curve there).

    v_primary=True (used for pct glyphs at NORM_W_PCT×NORM_H_PCT):
      If the v-projection winner scores >= PROJ_CORR_MIN on v alone, return
      it immediately without averaging with h.  This prevents h-projection
      template bias from overriding a decisive v match (e.g. '3'→'2').

    acc: optional [inner_blobs_s, projection_s, hu_s] accumulator — when
      provided, perf_counter deltas are added in-place so _read_line can
      emit them as synthetic child Spans without context-manager overhead
      per glyph call.

    Returns a single char, or '?' if confidence is below both thresholds.
    """
    if not templates:
        return '?'

    # ── Phase 1: inner-blob pre-filter ───────────────────────────────────────
    # Count enclosed holes in the query glyph and restrict scoring to templates
    # whose modal hole count matches.  Only applied when query count >= 2
    # because at small sizes (NORM_W_VAL=8) single-loop digits (0, 4, 6, 9)
    # may or may not show their hole depending on interpolation — the hole
    # count is unreliable as a categorical filter at count=1.  Two holes
    # unambiguously identify '8' at any reasonable size.
    #   2 holes → must be '8' (categorical)
    #   1 hole  → ambiguous at small size; don't restrict candidates
    #   0 holes → don't filter (hole may have closed)
    #
    # min_area: pct glyphs (NORM_H_PCT=20) use min_area=8 to filter the
    # larger 4-7px resize artifact that can appear when a ~19px '4' is
    # stretched to 20px via INTER_AREA (genuine '8' loops at 12×20 are
    # well above 8px).  Val glyphs (NORM_H_VAL=13) use min_area=4 because
    # their loops are smaller and would be filtered by a higher threshold.
    _min_area = 8 if norm.shape == (NORM_H_PCT, NORM_W_PCT) else 4
    _t0 = time.perf_counter() if acc is not None else 0.0
    query_inner = _count_inner_blobs(norm, min_area=_min_area)
    if query_inner >= 2:
        filtered = {c: t for c, t in templates.items()
                    if t.get("inner_blobs", -1) == query_inner}
        if filtered:   # only apply when at least one template matches
            templates = filtered
    # ── Phase 1b: 2-vs-3 discriminator ───────────────────────────────────────
    # Neither '2' nor '3' has an enclosed hole, so Phase 1 can't separate them —
    # and Tesseract-sourced training labels for this font's '2' are unreliable
    # enough (docs/known_issues.txt §15) that the '3' template itself is
    # partly built from '2'-shaped samples, making pure projection scoring
    # favor '3' even on a genuine '2'.  The bottom row is categorical instead:
    # '2' ends in a full-width flat stroke, '3' curls inward.
    if '2' in templates and '3' in templates:
        bottom_frac = _bottom_row_width_frac(norm)
        if bottom_frac >= TWO_BOTTOM_FULL_MIN:
            templates = {c: t for c, t in templates.items() if c != '3'}
        elif bottom_frac <= THREE_BOTTOM_CURL_MAX:
            templates = {c: t for c, t in templates.items() if c != '2'}

    if acc is not None:
        _now = time.perf_counter(); acc[0] += _now - _t0; _t0 = _now

    # ── Phase 2: projection scoring ───────────────────────────────────────────
    vproj = _v_projection(norm)
    hproj = _h_projection(norm)

    v_scores:        dict[str, float] = {}
    combined_scores: dict[str, float] = {}
    for c, t in templates.items():
        v_corr = _proj_corr(vproj, t["proj"])
        h_corr = _proj_corr(hproj, t["hproj"]) if "hproj" in t else 0.0
        v_scores[c]        = v_corr
        combined_scores[c] = (v_corr + h_corr) / 2

    best_c    = max(combined_scores, key=combined_scores.get)
    best_corr = combined_scores[best_c]

    # Single-candidate shortcut: when inner-blob pre-filter narrowed to one
    # template and the score is at least plausible, the structural evidence
    # (hole count) is categorical — return it without requiring PROJ_CORR_MIN.
    if len(combined_scores) == 1 and best_corr >= PROJ_VERY_LOW:
        if acc is not None: acc[1] += time.perf_counter() - _t0
        return best_c

    # V-primary shortcut (pct glyphs): if v-projection alone decisively picks
    # a winner with a clear gap, skip combined and return immediately.  The
    # h-projection template average can be biased by training variance, causing
    # combined to reverse a correct v-projection result (e.g. '3'→'2' after
    # inner_blobs rebuild — v-gap=0.258, so the gap guard lets it through, while
    # close pairs like '9' vs '2' at v-gap=0.021 fall back to combined).
    if v_primary:
        v_sorted    = sorted(v_scores.values(), reverse=True)
        v_gap       = v_sorted[0] - v_sorted[1] if len(v_sorted) > 1 else 1.0
        best_v_c    = max(v_scores, key=v_scores.get)
        best_v_corr = v_scores[best_v_c]
        if best_v_corr >= PROJ_CORR_MIN and v_gap >= 0.15:
            best_c    = best_v_c
            best_corr = combined_scores[best_v_c]
            # Fall through to reverse inner-blob check below with updated best_c

    if best_corr >= PROJ_CORR_MIN or (v_primary and v_scores.get(best_c, 0) >= PROJ_CORR_MIN):
        # ── Reverse inner-blob check ──────────────────────────────────────────
        # If the highest-scoring template requires 2+ holes (i.e. '8') but the
        # query glyph shows zero holes, the classification is structurally
        # inconsistent — '5' and '8' have the same projection profile but differ
        # by exactly this structural feature.
        #
        # Only applied when ALL templates carry inner_blobs data (requires
        # templates to have been rebuilt with the new pipeline).  Falls through
        # silently on old templates so behaviour is unchanged before rebuild.
        best_c_inner = templates[best_c].get("inner_blobs", -1)
        if (best_c_inner >= 2 and query_inner == 0
                and all("inner_blobs" in t for t in templates.values())):
            # Redirect: best zero-hole candidate by projection score
            zero_hole = {c: combined_scores[c] for c in combined_scores
                         if templates[c].get("inner_blobs", -1) == 0}
            if zero_hole:
                if acc is not None: acc[1] += time.perf_counter() - _t0
                return max(zero_hole, key=zero_hole.get)
            # No zero-hole template found — fall through to Hu tiebreaker
        else:
            if acc is not None: acc[1] += time.perf_counter() - _t0
            return best_c

    # If projection confidence is extremely low, Hu fallback is unreliable
    # (e.g. K glyph in ib_d: best proj ≈ 0.27, Hu misfires to '2').
    if best_corr < PROJ_VERY_LOW:
        if acc is not None: acc[1] += time.perf_counter() - _t0
        return '?'

    # Clear-winner shortcut: when the best combined score wins by a decisive
    # margin over the second-best and is at least plausible (≥ 0.55), return
    # it without requiring the full PROJ_CORR_MIN threshold.  This handles
    # val '0' crops that consistently score 0.58–0.67 (just below 0.70) but
    # are clear winners — the Hu tiebreaker is unreliable for these crops
    # because all Hu distances are >> HU_HALF_DIST_MAX.  The gap guard (≥ 0.10)
    # prevents near-ties from misfiring.
    _sorted_combined = sorted(combined_scores.values(), reverse=True)
    _gap = (_sorted_combined[0] - _sorted_combined[1]
            if len(_sorted_combined) > 1 else 1.0)
    if best_corr >= 0.55 and _gap >= 0.10:
        # Apply the same reverse inner-blob check as the main confidence path
        best_c_inner = templates[best_c].get("inner_blobs", -1)
        if (best_c_inner >= 2 and query_inner == 0
                and all("inner_blobs" in t for t in templates.values())):
            zero_hole = {c: combined_scores[c] for c in combined_scores
                         if templates[c].get("inner_blobs", -1) == 0}
            if zero_hole:
                if acc is not None: acc[1] += time.perf_counter() - _t0
                return max(zero_hole, key=zero_hole.get)
            # No zero-hole template — fall through to Hu tiebreaker
        else:
            if acc is not None: acc[1] += time.perf_counter() - _t0
            return best_c

    if acc is not None:
        _now = time.perf_counter(); acc[1] += _now - _t0; _t0 = _now

    # ── Phase 3: Hu moment tiebreaker ────────────────────────────────────────
    # Use split half-Hu when templates support it
    sample_t = next(iter(templates.values()))
    if "top_hu" in sample_t:
        top_hu, bot_hu = _half_hu_moments(norm)
        best_c_hu, best_dist = '?', float('inf')
        for c, t in templates.items():
            d = _hu_dist(top_hu, t["top_hu"]) + _hu_dist(bot_hu, t["bot_hu"])
            if d < best_dist:
                best_dist, best_c_hu = d, c
        result = best_c_hu if best_dist <= HU_HALF_DIST_MAX else '?'
    else:
        # Legacy templates without half-Hu
        hu = _hu_moments(norm)
        best_c_hu, best_dist = '?', float('inf')
        for c, t in templates.items():
            d = _hu_dist(hu, t["hu"])
            if d < best_dist:
                best_dist, best_c_hu = d, c
        result = best_c_hu if best_dist <= HU_DIST_MAX else '?'

    if acc is not None: acc[2] += time.perf_counter() - _t0
    return result


def _reconstruct(
    glyphs:    list[tuple[int, Optional[np.ndarray], str]],
    templates: dict,
) -> Optional[str]:
    """
    Turn a glyph list into a string.  Returns None if any '?' appears.
    Skips hint='skip' entries.
    """
    parts = []
    for _, norm, hint in glyphs:
        if hint == 'skip':
            continue
        if hint == '.':
            parts.append('.')
        else:
            parts.append(_classify(norm, templates))

    result = ''.join(parts)
    return result if result and '?' not in result else None


def _reconstruct_val(
    glyphs:    list[tuple[int, Optional[np.ndarray], str, Optional[np.ndarray]]],
    templates: dict,
    acc:       "list[float] | None" = None,
) -> Optional[str]:
    """
    Reconstruct the val string. Rightmost '?' → 'K' (K multiplier suffix).
    'M' suffix renders as 2 blobs at header font size; last two '?' → 'M'.
    K/M always appear rightmost; interior '?' still aborts the result.
    """
    items = [(x, norm, hint) for x, norm, hint in glyphs if hint != 'skip']
    if not items:
        return None
    # K/M suffix is only plausible when there are ≥ 4 items (3+ digits + K/M).
    # "440" → 3 items, "4246K" → 5 items.  Prevents lone '0' → 'K'.
    km_eligible = len(items) >= 4
    parts = []
    for i, (x, norm, hint) in enumerate(items):
        if hint == '.':
            parts.append('.')
        else:
            c = _classify(norm, templates, acc=acc)
            if km_eligible and c == '?' and i == len(items) - 1:
                # 'M' splits into 2 blobs at header font size: last two '?' → 'M'
                if parts and parts[-1] == '?':
                    parts[-1] = 'M'
                else:
                    parts.append('K')  # rightmost unclassifiable in long val → K suffix
            else:
                parts.append(c)
    result = ''.join(parts)
    # Return partial results with '?' markers rather than None — callers can
    # inspect uncertainty.  Only return None when the result is empty.
    return result if result else None


def _reconstruct_pct(
    glyphs:    list[tuple[int, Optional[np.ndarray], str, Optional[np.ndarray]]],
    templates: dict,
    acc:       "list[float] | None" = None,
) -> Optional[str]:
    """
    Reconstruct the pct value string from pct-strip glyphs.

    Like _reconstruct, but applies a rightmost-'?' fallback: if the last
    non-skip glyph cannot be classified, it is silently dropped rather than
    returning None.  This handles the case where the '%' glyph (always the
    rightmost element) renders as a single merged blob indistinguishable
    from a digit by bounding-box size alone — it would otherwise produce
    '?' and abort the result.
    """
    items = [(x, norm, hint) for x, norm, hint in glyphs if hint != 'skip']
    parts = []
    for i, (x, norm, hint) in enumerate(items):
        if hint == '.':
            parts.append('.')
        else:
            c = _classify(norm, templates, v_primary=True, acc=acc)
            if c == '?' and i == len(items) - 1:
                continue  # rightmost unclassifiable blob → % glyph, drop it
            parts.append(c)
    result = ''.join(parts)
    # Strip leading/trailing '.' noise blobs.  A valid pct value always starts
    # and ends with a digit (e.g. "35.38", "0") — a leading dot comes from a
    # stray noise blob at the left edge of the pct strip that is too small to
    # be filtered by blob-size or y-outlier checks.
    result = result.strip('.')
    return result if result and '?' not in result else None


# ─────────────────────────────────────────────────────────────────────────────
# Public engine
# ─────────────────────────────────────────────────────────────────────────────

def _tmpl_variant_paths(variant: str) -> tuple[Path, Path]:
    """Resolve a template-set name to its matched (pct, val) file pair,
    e.g. 'padded' -> stat_pct_padded.py/stat_val_padded.py, 'default' or
    None -> stat_pct.py/stat_val.py. One name for both files rules out a
    mismatched pct/val template pairing (see gfl2/stat_ocr_padded.py's
    identical copy of this helper)."""
    suffix = "" if variant in (None, "default") else f"_{variant}"
    return (_FONTS_DIR / f"stat_pct{suffix}.py", _FONTS_DIR / f"stat_val{suffix}.py")


class StatOcr:
    """Blob-based OCR engine for Daily Gunsmoke stat cells."""

    def __init__(self, templates: dict) -> None:
        self._pct = templates.get("pct", {})
        self._val = templates.get("val", {})

    # ── Construction ─────────────────────────────────────────────────────────

    @classmethod
    def load(cls, tmpl_variant: str | None = None) -> "StatOcr":
        """tmpl_variant: None -> this engine's own default templates
        (stat_pct.py/stat_val.py). Any other name (e.g. 'padded') loads that
        named template set instead, for cross-checking this classifier
        against a different template pair — see _tmpl_variant_paths().

        Uses dynamic module loading (importlib.util) rather than a static
        `from assets.fonts.stat_pct import DATA` regardless of variant, so
        there is one code path instead of two. This reads the identical
        file and produces an identical DATA dict for the default case; the
        only observable difference is the module no longer registers under
        sys.modules["assets.fonts.stat_pct"], which nothing else in the repo
        depends on. Matches the mechanism gfl2/stat_ocr_padded.py already used.
        """
        pct_path, val_path = (
            (PCT_TMPL_F, VAL_TMPL_F) if tmpl_variant is None
            else _tmpl_variant_paths(tmpl_variant)
        )
        for p in (pct_path, val_path):
            if not p.exists():
                raise FileNotFoundError(
                    f"Stat OCR templates not found: {p}\n"
                    "Run: python -m gfl2.stat_ocr --build"
                )
        import importlib.util

        def _load_tmpl_module(path: Path):
            spec = importlib.util.spec_from_file_location(path.stem, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.DATA

        pct_data = _load_tmpl_module(pct_path)
        val_data = _load_tmpl_module(val_path)
        return cls({"pct": pct_data, "val": val_data})

    # ── Inference ─────────────────────────────────────────────────────────────

    def read(
        self, cell: np.ndarray, timer=None
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Read a stat cell crop using frame-relative strip splitting.

        The combined cell spans both pct and val lines.  PCT_STRIP_Y /
        VAL_STRIP_Y slice each line independently before blob detection,
        replacing _split_lines and eliminating cross-line contamination.

        Returns (pct_str, val_str) where:
          pct_str  — digits of the percentage, e.g. "35.38"  (no trailing %)
          val_str  — raw value,                e.g. "665669"

        Returns (None, None) on parse failure; the caller should fall back
        to Tesseract.

        timer: optional TimerStack — when provided, sub-spans are recorded
          under the caller's active span:
            pct/binarize, pct/blobs, pct/extract, pct/classify
            val/binarize, val/blobs, val/extract, val/classify
        """
        ch = cell.shape[0]
        pct_strip = cell[: int(ch * PCT_STRIP_Y[1]), :]
        val_strip = cell[int(ch * VAL_STRIP_Y[0]) : int(ch * VAL_STRIP_Y[1]), :]

        pct_str = self._read_line(pct_strip, self._pct, is_pct=True,  timer=timer)
        val_str = self._read_line(val_strip, self._val, is_pct=False, timer=timer)
        return pct_str, val_str

    def _read_line(
        self, strip: np.ndarray, templates: dict, is_pct: bool, timer=None
    ) -> Optional[str]:
        if strip.size == 0:
            return None
        prefix = "pct" if is_pct else "val"
        _t = timer.timed if timer is not None else _nullctx

        with _t(f"{prefix}/binarize"):
            thresh = _binarize(strip)

        with _t(f"{prefix}/blobs"):
            blobs = _find_blobs(thresh)
            if not blobs:
                return None
            # Filter blobs whose y-centroid is far from the group median.
            # Needed because the pct and val strips overlap by ~2 rows, causing
            # partial bottom-edge fragments of pct glyphs to appear at y≈0 of
            # the val strip (and vice-versa for pct).
            # Val-strip threshold is tighter (8 px) than pct (12 px): val digits
            # sit on a single tight baseline (cy spread < 5 px), so cy=5 noise blobs
            # (gap=9 from median=14) are safely excluded without touching real glyphs.
            blobs = _filter_y_outliers(blobs, threshold=8 if not is_pct else 12)
            if not blobs:
                return None

        with _t(f"{prefix}/extract"):
            if is_pct:
                glyphs = _extract_pct_glyphs(blobs, thresh)
            else:
                glyphs = _extract_val_glyphs(blobs, thresh)

        acc = [0.0, 0.0, 0.0] if timer is not None else None
        with _t(f"{prefix}/classify") as classify_span:
            if is_pct:
                result = _reconstruct_pct(glyphs, templates, acc)
            else:
                result = _reconstruct_val(glyphs, templates, acc)

        # Inject per-phase sub-timings as synthetic child Spans so that
        # pipeline_summary can aggregate inner_blobs / projection / hu_fallback
        # across all cells without context-manager overhead per glyph call.
        if timer is not None:
            from gfl2.timing import Span as _Span
            for _name, _elapsed in zip(
                ("inner_blobs", "projection", "hu_fallback"), acc
            ):
                if _elapsed > 0:
                    classify_span.children.append(_Span(_name, _elapsed))

        return result


# ─────────────────────────────────────────────────────────────────────────────
# Template builder
# ─────────────────────────────────────────────────────────────────────────────

def _avg_features(samples: list[tuple]) -> dict:
    from collections import Counter
    n           = len(samples)
    avg_hu      = [sum(s[0][i] for s in samples) / n for i in range(7)]
    proj_len    = len(samples[0][1])
    avg_proj    = [sum(s[1][i] for s in samples) / n for i in range(proj_len)]
    hproj_len   = len(samples[0][2])
    avg_hproj   = [sum(s[2][i] for s in samples) / n for i in range(hproj_len)]
    avg_top_hu  = [sum(s[3][i] for s in samples) / n for i in range(7)]
    avg_bot_hu  = [sum(s[4][i] for s in samples) / n for i in range(7)]
    # Modal inner blob count — most common observed value across training samples.
    # Legacy samples (5-tuple) lack index [5]; default to -1 (unknown).
    inner_counts = [s[5] for s in samples if len(s) > 5]
    modal_inner  = Counter(inner_counts).most_common(1)[0][0] if inner_counts else -1
    return {"hu": avg_hu, "proj": avg_proj, "hproj": avg_hproj,
            "top_hu": avg_top_hu, "bot_hu": avg_bot_hu,
            "inner_blobs": modal_inner, "n": n}


def build_templates(
    training:     list[dict],
    verbose:      bool = True,
    gt_overrides: "dict | None" = None,
) -> dict:
    """
    Build and save template JSON from a list of training dicts:
        {"cell": np.ndarray, "pct": str, "val": str, "source": str (optional)}

    pct should be the digit string WITHOUT trailing '%', e.g. "35.38".
    val should be the raw value string, e.g. "665669" or "2M".

    gt_overrides corrects known-wrong Tesseract labels (docs/known_issues.txt
    §15) before training, keyed by each item's "source" field.  Applied here
    rather than by each caller so EVERY path that can (re)build stat_pct.py/
    stat_val.py — gfl2/stat_ocr.py's --build CLI and assets/builders/build.py,
    which calls this function directly and bypasses that CLI entirely — is
    protected uniformly.  A caller-side-only fix (as this project's --verify
    already had) can't prevent a *different* caller from silently rebuilding
    contaminated templates.  Items with no "source" key are left unmatched
    (never raises).  Explicit gt_overrides=None auto-loads
    stat_gt_overrides.json from the project root if present; pass {} to
    disable entirely.
    """
    if gt_overrides is None:
        _gt_file = Path("stat_gt_overrides.json")
        gt_overrides = json.loads(_gt_file.read_text(encoding="utf-8")) if _gt_file.exists() else {}
    if gt_overrides:
        n_applied = 0
        for item in training:
            ov = gt_overrides.get(item.get("source"))
            if ov:
                if "pct" in ov: item["pct"] = ov["pct"]
                if "val" in ov: item["val"] = ov["val"]
                n_applied += 1
        if verbose and n_applied:
            print(f"  Applied {n_applied} GT override(s) from stat_gt_overrides.json "
                  "(corrects known Tesseract mislabels before training)")

    pct_buckets: dict[str, list] = {c: [] for c in TRAIN_CHARS}
    val_buckets: dict[str, list] = {c: [] for c in TRAIN_CHARS}

    n_cells = 0
    for item in training:
        cell    = item["cell"]
        pct_str = item.get("pct") or ""
        val_str = item.get("val") or ""

        ch = cell.shape[0]

        # ── pct line (top strip) ──────────────────────────────────────────
        pct_strip = cell[: int(ch * PCT_STRIP_Y[1]), :]
        thresh_p  = _binarize(pct_strip)
        blobs_p   = _filter_y_outliers(_find_blobs(thresh_p))
        pct_glyphs = _extract_pct_glyphs(blobs_p, thresh_p)
        # Only 'digit' glyphs need training; '.' detected by size
        digit_glyphs_pct = [(x, norm) for x, norm, hint in pct_glyphs
                            if hint == 'digit' and norm is not None]
        # Expected char sequence: remove '.' from pct_str (dot detected by size)
        expected_pct = [c for c in pct_str if c in TRAIN_CHARS]

        if len(digit_glyphs_pct) == len(expected_pct):
            for (_, norm), char in zip(digit_glyphs_pct, expected_pct):
                pct_buckets[char].append(_features(norm))
            n_cells += 1
        # else: blob count mismatch, skip this cell for training

        # ── val line (middle strip) ───────────────────────────────────────
        val_strip = cell[int(ch * VAL_STRIP_Y[0]) : int(ch * VAL_STRIP_Y[1]), :]
        thresh_v  = _binarize(val_strip)
        blobs_v   = _filter_y_outliers(_find_blobs(thresh_v))
        val_glyphs = _extract_val_glyphs(blobs_v, thresh_v)
        digit_glyphs_val = [(x, norm) for x, norm, hint in val_glyphs
                            if hint == 'digit' and norm is not None]
        expected_val = [c for c in val_str if c in TRAIN_CHARS]

        if len(digit_glyphs_val) == len(expected_val):
            for (_, norm), char in zip(digit_glyphs_val, expected_val):
                val_buckets[char].append(_features(norm))

    # ── Average per character ─────────────────────────────────────────────
    pct_templates, val_templates = {}, {}

    for char, samples in pct_buckets.items():
        if not samples:
            continue
        pct_templates[char] = _avg_features(samples)

    for char, samples in val_buckets.items():
        if not samples:
            continue
        val_templates[char] = _avg_features(samples)

    templates = {"pct": pct_templates, "val": val_templates}

    # ── Save ─────────────────────────────────────────────────────────────
    def _write_font_py(path, data):
        src = "# auto-generated — do not edit\nDATA = " + json.dumps(data, indent=2) + "\n"
        path.write_text(src, encoding="utf-8")

    _FONTS_DIR.mkdir(parents=True, exist_ok=True)
    _write_font_py(PCT_TMPL_F, pct_templates)
    _write_font_py(VAL_TMPL_F, val_templates)

    if verbose:
        print(f"\nBuilt templates from {n_cells} cells")
        print(f"  pct -> {PCT_TMPL_F}  chars: { {c: pct_templates[c]['n'] for c in sorted(pct_templates)} }")
        print(f"  val -> {VAL_TMPL_F}  chars: { {c: val_templates[c]['n'] for c in sorted(val_templates)} }")

    return templates


# ─────────────────────────────────────────────────────────────────────────────
# Collect training / verification data from daily-gunsmoke images
# ─────────────────────────────────────────────────────────────────────────────

def _collect_cells(
    image_paths: list[Path],
    tess_only: bool = True,
) -> list[dict]:
    """
    Extract every stat cell from a list of images and return
    a list of {"cell": ndarray, "pct": str, "val": str, "source": str}.

    Cells are extracted using _frame_col_cell (frame-relative coordinates)
    so training crops exactly match inference crops at any resolution.

    tess_only=True  (default for --build): forces pure Tesseract labeling so
    that blob-pipeline results are never used as training ground truth.
    tess_only=False (used by --verify): uses the full pipeline (_extract_stat_cell).
    """
    import shutil, pytesseract
    if not shutil.which("tesseract"):
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    from gfl2.patterns.daily_gunsmoke import (
        _split_panels, _find_frames, _frame_col_cell,
        _ocr_raw, _parse_pct_val, _extract_stat_cell,
        COL1_FR, COL2_FR, COL3_FR, COL4_FR,
    )
    from gfl2.timing import TimerStack

    def _tess_label(cell):
        """Pure Tesseract label: no blob pipeline, no circular training."""
        txt = _ocr_raw(cell, "--psm 6")
        pct, val = _parse_pct_val(txt)
        if val is None or len(val) <= 2:
            txt2 = _ocr_raw(cell, "--psm 4")
            pct2, val2 = _parse_pct_val(txt2)
            if val2 and (val is None or len(val2) > len(val)):
                pct = pct2 or pct
                val = val2
        return pct, val

    COLS_FR = [
        ("col1", COL1_FR),
        ("col2", COL2_FR),
        ("col3", COL3_FR),
        ("col4", COL4_FR),
    ]

    results = []
    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        panels = _split_panels(img)
        for pi, panel in enumerate(panels):
            frames = _find_frames(panel)
            if not frames:
                continue
            ph, pw = panel.shape[:2]
            _timer = TimerStack()
            for ri, (fx, fy, fw, fh) in enumerate(frames):
                for cname, col_fr in COLS_FR:
                    cell = _frame_col_cell(panel, fx, fy, fw, fh, col_fr)
                    if cell.size == 0:
                        continue
                    # Compute strip rects in panel coords for debug overlay
                    from gfl2.patterns.daily_gunsmoke import CELL_Y_FR
                    fr   = fx + fw
                    bx0  = max(0, fr + int(fw * col_fr[0]))
                    bx1  = min(pw, fr + int(fw * col_fr[1]))
                    by0  = max(0, fy + int(fh * CELL_Y_FR[0]))
                    by1  = min(ph, fy + int(fh * CELL_Y_FR[1]))
                    ch_  = by1 - by0
                    pbx  = (bx0, by0,
                            bx1, by0 + int(ch_ * PCT_STRIP_Y[1]))
                    vbx  = (bx0, by0 + int(ch_ * VAL_STRIP_Y[0]),
                            bx1, by0 + int(ch_ * VAL_STRIP_Y[1]))
                    if tess_only:
                        pct, val = _tess_label(cell)
                    else:
                        pct, val, _ = _extract_stat_cell(cell, _timer)
                    if pct is not None or val is not None:
                        key = f"{img_path.stem}_p{pi+1}_r{ri}_{cname}"
                        results.append({
                            "cell":     cell,
                            "pct":      pct or "",
                            "val":      val or "",
                            "source":   key,
                            # debug metadata
                            "img_path":  img_path,
                            "panel_idx": pi,
                            "panel":     panel,
                            "pct_bbox":  pbx,
                            "val_bbox":  vbx,
                        })

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark / verification
# ─────────────────────────────────────────────────────────────────────────────


def _save_verify_debug(samples: list, mismatches: list, out_dir: "Path") -> None:
    """Draw crop rectangles on each panel and save annotated PNGs.

    Colour coding per cell:
      green  — pct + val both correct (or not expected)
      yellow — one of pct/val wrong
      red    — both wrong, or a no-read
    Label format (shown above the rectangle): "pct:exp→got  val:exp→got"
    Only differing fields are shown; matching fields are omitted.
    """
    from pathlib import Path as _Path
    import cv2 as _cv2
    import numpy as _np

    out_dir = _Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build mismatch lookup  source → {kind: (expected, got)}
    mm_map: dict = {}
    for src_key, kind, expected, got in mismatches:
        mm_map.setdefault(src_key, {})[kind] = (expected, got)

    # Group samples by (img_path, panel_idx)
    panels_seen: dict = {}   # (img_path, panel_idx) → (panel_img, [sample, ...])
    for item in samples:
        key = (item["img_path"], item["panel_idx"])
        if key not in panels_seen:
            panels_seen[key] = (item["panel"].copy(), [])
        panels_seen[key][1].append(item)

    FONT       = _cv2.FONT_HERSHEY_SIMPLEX
    FONT_SCALE = 0.38
    THICKNESS  = 1

    GREEN  = (  0, 200,   0)
    RED    = (  0,   0, 200)

    def _draw_strip(canvas, bbox, colour, label):
        x0, y0, x1, y1 = bbox
        _cv2.rectangle(canvas, (x0, y0), (x1, y1), colour, 1)
        if label:
            lx = x0
            ly = max(y0 - 2, 8)
            (tw, th), _ = _cv2.getTextSize(label, FONT, FONT_SCALE, THICKNESS)
            _cv2.rectangle(canvas, (lx - 1, ly - th - 2),
                           (lx + tw + 1, ly + 2), (20, 20, 20), -1)
            _cv2.putText(canvas, label, (lx, ly),
                         FONT, FONT_SCALE, colour, THICKNESS, _cv2.LINE_AA)

    for (img_path, pi), (canvas, items) in panels_seen.items():
        for item in items:
            s   = item["source"]
            mm  = mm_map.get(s, {})

            # ── pct strip ────────────────────────────────────────────────────
            pct_col  = RED if "pct" in mm else GREEN
            pct_lbl  = ""
            if "pct" in mm:
                exp, got = mm["pct"]
                pct_lbl  = f"pct:{exp}→{got if got is not None else '∅'}"
            _draw_strip(canvas, item["pct_bbox"], pct_col, pct_lbl)

            # ── val strip ────────────────────────────────────────────────────
            val_col  = RED if "val" in mm else GREEN
            val_lbl  = ""
            if "val" in mm:
                exp, got = mm["val"]
                val_lbl  = f"val:{exp}→{got if got is not None else '∅'}"
            _draw_strip(canvas, item["val_bbox"], val_col, val_lbl)

        stem    = _Path(img_path).stem
        out_png = out_dir / f"{stem}_p{pi+1}_verify.png"
        _cv2.imwrite(str(out_png), canvas)
        print(f"  debug -> {out_png}")


def verify(
    image_paths:  list[Path],
    verbose:      bool = True,
    debug_dir:    "Path | None" = None,
    gt_overrides: dict = None,
) -> dict:
    """
    Compare blob pipeline against Tesseract on every cell across all images.
    Returns accuracy dict.

    gt_overrides: optional dict of {source_key: {"pct": "...", "val": "..."}}
      that overrides Tesseract ground truth for specific cells.  Use this to
      correct known Tesseract labelling errors without rerunning Tesseract.
      Example: {"ib_d_20260111_p2_r0_col3": {"val": "8143"}}
      Loaded automatically from stat_gt_overrides.json if it exists.

    debug_dir: if given, save one annotated PNG per panel to that directory.
      Rectangles are colour-coded:
        green  = pct+val both correct
        yellow = one of pct/val wrong
        red    = both wrong or no-read
      Each rectangle is labelled "exp/got" for the mismatching field.
    """
    run_start = datetime.now().isoformat(timespec="seconds")
    engine  = StatOcr.load()
    samples = _collect_cells(image_paths)

    # Load GT overrides: explicit dict takes priority, then file, then empty
    _GT_FILE = Path("stat_gt_overrides.json")
    if gt_overrides is None:
        gt_overrides = json.loads(_GT_FILE.read_text()) if _GT_FILE.exists() else {}
    # Apply overrides to samples
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov:
            if "pct" in ov: item["pct"] = ov["pct"]
            if "val" in ov: item["val"] = ov["val"]

    pct_total = pct_match = pct_miss = 0
    val_total = val_match = val_miss = 0
    mismatches = []

    for item in samples:
        blob_pct, blob_val = engine.read(item["cell"])

        if item["pct"]:
            pct_total += 1
            if blob_pct is None:
                pct_miss += 1
                mismatches.append((item["source"], "pct", item["pct"], blob_pct))
            elif blob_pct != item["pct"]:
                mismatches.append((item["source"], "pct", item["pct"], blob_pct))
            else:
                pct_match += 1

        if item["val"]:
            val_total += 1
            if blob_val is None:
                val_miss += 1
                mismatches.append((item["source"], "val", item["val"], blob_val))
            elif blob_val != item["val"]:
                mismatches.append((item["source"], "val", item["val"], blob_val))
            else:
                val_match += 1

    if debug_dir is not None:
        _save_verify_debug(samples, mismatches, debug_dir)

    if verbose:
        def pct_str(n, d): return f"{100*n/d:.1f}%" if d else "n/a"
        print(f"\n{'-'*60}")
        print(f"Generated: {run_start}  (run start)")
        print(f"StatOcr verify  ({len(image_paths)} images, {len(samples)} cells)")
        print(f"  pct  {pct_match}/{pct_total} correct  "
              f"({pct_str(pct_match, pct_total)})  "
              f"{pct_miss} no-read")
        print(f"  val  {val_match}/{val_total} correct  "
              f"({pct_str(val_match, val_total)})  "
              f"{val_miss} no-read")
        if mismatches:
            print(f"\nFirst 20 mismatches:")
            for src, kind, expected, got in mismatches[:20]:
                print(f"  {src}  {kind}  expected={expected!r}  got={got!r}")
        print(f"{'-'*60}")

    return {
        "pct_correct": pct_match, "pct_total": pct_total,
        "val_correct": val_match, "val_total": val_total,
        "mismatches":  mismatches,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def _main() -> None:
    import argparse, shutil, time

    parser = argparse.ArgumentParser(
        description="StatOcr template builder / verifier"
    )
    parser.add_argument("--build",      action="store_true",
                        help="Build templates from images and save")
    parser.add_argument("--verify",     action="store_true",
                        help="Verify blob pipeline vs Tesseract ground truth")
    parser.add_argument("--images",     default="single/*.png",
                        help="Glob of images to use  [default: single/*.png]")
    parser.add_argument("--save-crops", action="store_true",
                        help="Save individual cell crops to tests/inputs/daily/")
    parser.add_argument("--debug",      action="store_true",
                        help="Save annotated panel PNGs with crop overlays to stat_verify_debug/")
    parser.add_argument("--gt-overrides", default=None,
                        help="JSON file of GT overrides {source: {pct,val}} "
                             "[default: stat_gt_overrides.json if present]")
    args = parser.parse_args()

    if not args.build and not args.verify:
        parser.print_help()
        sys.exit(1)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                         if "debug" not in Path(p).stem)
    if not image_paths:
        print(f"No images matched: {args.images}", file=sys.stderr)
        sys.exit(1)

    print(f"Images: {len(image_paths)}")

    if args.build:
        print("Collecting training data via Tesseract ...")
        t0 = time.perf_counter()
        training = _collect_cells(image_paths, tess_only=True)
        print(f"  {len(training)} cells collected  ({time.perf_counter()-t0:.1f}s)")

        # Applied here (silently) so --save-crops persists corrected labels;
        # build_templates() below re-applies the same dict (idempotent) and
        # is the one that prints the "Applied N" line — see its docstring for
        # why override application also lives there and not only here.
        gt_file = Path(args.gt_overrides) if args.gt_overrides else Path("stat_gt_overrides.json")
        gt_overrides = json.loads(gt_file.read_text(encoding="utf-8")) if gt_file.exists() else {}
        for item in training:
            ov = gt_overrides.get(item["source"])
            if ov:
                if "pct" in ov: item["pct"] = ov["pct"]
                if "val" in ov: item["val"] = ov["val"]

        if args.save_crops:
            STAT_SET_DIR.mkdir(parents=True, exist_ok=True)
            crops = []
            for item in training:
                fname = f"{item['source']}.png"
                cv2.imwrite(str(STAT_SET_DIR / fname), item["cell"])
                crops.append({"path": fname, "pct": item["pct"], "val": item["val"]})
            manifest = {
                "font": "assets/fonts/stat_pct.json",
                "crops": crops,
            }
            (STAT_SET_DIR / "stat.json").write_text(
                json.dumps(manifest, indent=2), encoding="utf-8")
            print(f"  Saved {len(crops)} crops to tests/inputs/daily/")

        print("Building templates ...")
        t1 = time.perf_counter()
        build_templates(training)
        print(f"  Done  ({time.perf_counter()-t1:.1f}s)  -> {PCT_TMPL_F}, {VAL_TMPL_F}")

    if args.verify:
        gt_file = Path(args.gt_overrides) if args.gt_overrides else Path("stat_gt_overrides.json")
        gt_overrides = json.loads(gt_file.read_text(encoding="utf-8")) if gt_file.exists() else None
        debug_dir = Path("stat_verify_debug") if args.debug else None
        verify(image_paths, verbose=True,
               debug_dir=debug_dir, gt_overrides=gt_overrides)


if __name__ == "__main__":
    _main()

