# -*- coding: utf-8 -*-
"""
debugs/stat_ocr_padded.py — EXPLORATION duplicate of gfl2/stat_ocr.py for §15.

Investigates whether aspect-preserving (pad-don't-stretch) glyph normalization
removes the within-class feature variation documented in docs/known_issues.txt §15:
the production pipeline's cv2.resize(crop, (NORM_W, NORM_H)) stretches every glyph
to the SAME fixed box regardless of its original aspect ratio, so a 5px-wide '1'
gets stretched ~2.4x in pct glyphs while an 11px-wide '0' barely stretches at all.
That's tolerable for 1D projection correlation but pollutes 2D features (FFT/Gabor).

This file is a DELIBERATE full copy of gfl2/stat_ocr.py, not an import-and-wrap.
Per project decision: during this exploration, duplication is preferred over DRY
so that any threshold re-tuning needed to make the padded normalization work
happens here and can NEVER regress the production module or its 830-test baseline.
Only _extract_pct_glyphs / _extract_val_glyphs (the resize call) and the new
_normalize_glyph() helper differ from the original; everything else is copied
verbatim so behavior stays comparable.

Own template output files (assets/fonts/stat_pct_padded.py / stat_val_padded.py) —
never touches the production stat_pct.py / stat_val.py.

Build templates:
    python debugs/stat_ocr_padded.py --build [--images <glob>]

Verify pipeline against Tesseract ground truth:
    python debugs/stat_ocr_padded.py --verify [--images <glob>]
"""
from __future__ import annotations
import json, math, sys, time, glob as _glob
from contextlib import nullcontext as _nullctx
from pathlib import Path
from typing import Optional
import cv2
import numpy as np

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE        = Path(__file__).parent.parent          # project root
_FONTS_DIR   = _HERE / "assets" / "fonts"
PCT_TMPL_F   = _FONTS_DIR / "stat_pct_padded.py"
VAL_TMPL_F   = _FONTS_DIR / "stat_val_padded.py"
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

# 2-vs-3 discriminator (docs/known_issues.txt §15) — copied verbatim from
# gfl2/stat_ocr.py, see that module for the full rationale.
TWO_BOTTOM_FULL_MIN = 0.80   # bottom row this wide or wider -> rule out '3'
THREE_BOTTOM_CURL_MAX = 0.70 # bottom row this narrow or narrower -> rule out '2'

# ── Within-cell y-strip boundaries (fractions of combined cell height) ────────
PCT_STRIP_Y = (0.00, 0.46)   # pct-only strip: top 46% of combined cell
VAL_STRIP_Y = (0.50, 0.82)   # val-only strip: 50–82% of combined cell (≥0.50 clears pct bleed)

# ── Training character sets ───────────────────────────────────────────────────
TRAIN_CHARS = list("0123456789KM")   # '.' handled by size; '%' stripped


# ─────────────────────────────────────────────────────────────────────────────
# Feature helpers  (copied from gfl2/stat_ocr.py)
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
    """Compute Hu moments separately for the top and bottom halves of norm."""
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
    """Count enclosed holes inside a normalised glyph image (see gfl2/stat_ocr.py)."""
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
    NORM_W (see gfl2/stat_ocr.py for the full rationale)."""
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
# Blob detection & line splitting (copied unchanged from gfl2/stat_ocr.py)
# ─────────────────────────────────────────────────────────────────────────────

def _binarize(cell: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY) if cell.ndim == 3 else cell
    _, t = cv2.threshold(gray, THRESH_BIN, 255, cv2.THRESH_BINARY_INV)
    return t


def _find_blobs(thresh: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Return [(x, y, w, h)] filtered by BLOB_MIN/MAX, sorted y then x."""
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
    """Remove blobs whose y-centroid differs from the group median by more than `threshold` pixels."""
    if len(blobs) <= 2:
        return blobs
    cys = sorted(b[1] + b[3] // 2 for b in blobs)
    median_cy = cys[len(cys) // 2]
    return [b for b in blobs if abs(b[1] + b[3] // 2 - median_cy) <= threshold]


def _split_lines(
    blobs: list[tuple[int, int, int, int]],
) -> tuple[list, list]:
    """Split blobs into (pct_blobs, val_blobs) by finding the largest y-centroid gap."""
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
        pct = [b for b in blobs if b[3] >= LARGE_H_MIN]
        val = [b for b in blobs if b[3] <  LARGE_H_MIN]
        return _filter_y_outliers(pct), _filter_y_outliers(val)

    pct_group = _filter_y_outliers(by_cy[: split_idx + 1])
    val_group = _filter_y_outliers(by_cy[split_idx + 1 :])
    return pct_group, val_group


# ─────────────────────────────────────────────────────────────────────────────
# Glyph extraction (strip %, identify '.')  — NORMALIZATION CHANGED HERE
# ─────────────────────────────────────────────────────────────────────────────

def _find_percent_x_start(blobs: list[tuple]) -> Optional[int]:
    """Detect the x-start of the '%' glyph cluster (see gfl2/stat_ocr.py for full doc)."""
    if not blobs:
        return None

    sorted_x = sorted(blobs, key=lambda b: b[0])

    rightmost = sorted_x[-1]
    if ((rightmost[2] >= PCT_MERGED_W or rightmost[2] >= rightmost[3] * 0.90)
            and rightmost[3] >= LARGE_H_MIN):
        return max(0, rightmost[0] - 10)

    x_min   = sorted_x[0][0]
    x_max   = max(b[0] + b[2] for b in sorted_x)
    x_range = x_max - x_min or 1
    min_y   = min(b[1] for b in blobs)

    candidates = [
        b for b in blobs
        if b[1] > min_y + 6
        and b[2] <= 14 and b[3] <= 14
        and (b[0] - x_min) / x_range >= 0.5
    ]
    if not candidates:
        return None

    bottom = max(candidates, key=lambda b: b[0])
    return max(0, bottom[0] - 25)


def _normalize_glyph(crop: np.ndarray, norm_w: int, norm_h: int) -> np.ndarray:
    """
    Aspect-preserving normalize: scale crop so its height becomes norm_h
    (uniform scale factor, no horizontal stretch), then center it in a
    norm_w x norm_h canvas, padding with background (0) on both sides.

    This is the fix under exploration for known_issues.txt §15: the production
    _extract_*_glyphs() instead does cv2.resize(crop, (norm_w, norm_h)) directly,
    which applies a DIFFERENT horizontal stretch factor per glyph depending on its
    original width (e.g. '1' at ~5px stretches far more than '0' at ~11px).  Here,
    every glyph is scaled by the SAME height-locked factor; narrow glyphs simply
    occupy less of the canvas width instead of being stretched to fill it.

    Falls back to a direct resize (old behavior) if the height-locked scale would
    make the glyph wider than norm_w — not expected for single digits, but keeps
    this safe for unusually wide / merged blobs.
    """
    ch, cw = crop.shape[:2]
    if ch == 0 or cw == 0:
        return cv2.resize(crop, (norm_w, norm_h), interpolation=cv2.INTER_AREA)

    scale   = norm_h / ch
    new_w   = max(1, round(cw * scale))

    if new_w > norm_w:
        return cv2.resize(crop, (norm_w, norm_h), interpolation=cv2.INTER_AREA)

    resized = cv2.resize(crop, (new_w, norm_h), interpolation=cv2.INTER_AREA)

    canvas = np.zeros((norm_h, norm_w), dtype=crop.dtype)
    x0 = (norm_w - new_w) // 2
    canvas[:, x0: x0 + new_w] = resized
    return canvas


def _extract_pct_glyphs(
    pct_blobs: list[tuple],
    thresh:    np.ndarray,
) -> list[tuple[int, Optional[np.ndarray], str]]:
    """
    Return [(x, norm_or_None, hint)] for the pct line.
    hint ∈ {'digit', '.', 'skip'}   ('skip' = % sub-blob, ignored)
    Digits are normalised via _normalize_glyph (pad, don't stretch) — see §15.
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
            norm = _normalize_glyph(crop, NORM_W_PCT, NORM_H_PCT)
            result.append((x, norm, 'digit'))

    return result


def _extract_val_glyphs(
    val_blobs: list[tuple],
    thresh:    np.ndarray,
) -> list[tuple[int, Optional[np.ndarray], str]]:
    """
    Return [(x, norm_or_None, hint)] for the val line.
    Tiny blobs (both dims ≤ DOT_MAX_DIM) → hint='.'.
    Digits are normalised via _normalize_glyph (pad, don't stretch) — see §15.
    """
    result = []
    for (x, y, w, h) in sorted(val_blobs, key=lambda b: b[0]):
        if w <= DOT_MAX_DIM and h <= DOT_MAX_DIM:
            result.append((x, None, '.'))
        else:
            crop = thresh[y: y + h, x: x + w]
            norm = _normalize_glyph(crop, NORM_W_VAL, NORM_H_VAL)
            result.append((x, norm, 'digit'))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Classifier (copied unchanged from gfl2/stat_ocr.py — re-tune HERE if the
# padded normalization shifts projection shapes enough to need it)
# ─────────────────────────────────────────────────────────────────────────────

def _classify(norm: np.ndarray, templates: dict, v_primary: bool = False,
              acc: "list[float] | None" = None) -> str:
    """Combined projection correlation (primary) → Hu moment distance (fallback).
    See gfl2/stat_ocr.py:_classify for full documentation of each phase.
    """
    if not templates:
        return '?'

    _min_area = 8 if norm.shape == (NORM_H_PCT, NORM_W_PCT) else 4
    _t0 = time.perf_counter() if acc is not None else 0.0
    query_inner = _count_inner_blobs(norm, min_area=_min_area)
    if query_inner >= 2:
        filtered = {c: t for c, t in templates.items()
                    if t.get("inner_blobs", -1) == query_inner}
        if filtered:
            templates = filtered

    if '2' in templates and '3' in templates:
        bottom_frac = _bottom_row_width_frac(norm)
        if bottom_frac >= TWO_BOTTOM_FULL_MIN:
            templates = {c: t for c, t in templates.items() if c != '3'}
        elif bottom_frac <= THREE_BOTTOM_CURL_MAX:
            templates = {c: t for c, t in templates.items() if c != '2'}

    if acc is not None:
        _now = time.perf_counter(); acc[0] += _now - _t0; _t0 = _now

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

    if len(combined_scores) == 1 and best_corr >= PROJ_VERY_LOW:
        if acc is not None: acc[1] += time.perf_counter() - _t0
        return best_c

    if v_primary:
        v_sorted    = sorted(v_scores.values(), reverse=True)
        v_gap       = v_sorted[0] - v_sorted[1] if len(v_sorted) > 1 else 1.0
        best_v_c    = max(v_scores, key=v_scores.get)
        best_v_corr = v_scores[best_v_c]
        if best_v_corr >= PROJ_CORR_MIN and v_gap >= 0.15:
            best_c    = best_v_c
            best_corr = combined_scores[best_v_c]

    if best_corr >= PROJ_CORR_MIN or (v_primary and v_scores.get(best_c, 0) >= PROJ_CORR_MIN):
        best_c_inner = templates[best_c].get("inner_blobs", -1)
        if (best_c_inner >= 2 and query_inner == 0
                and all("inner_blobs" in t for t in templates.values())):
            zero_hole = {c: combined_scores[c] for c in combined_scores
                         if templates[c].get("inner_blobs", -1) == 0}
            if zero_hole:
                if acc is not None: acc[1] += time.perf_counter() - _t0
                return max(zero_hole, key=zero_hole.get)
        else:
            if acc is not None: acc[1] += time.perf_counter() - _t0
            return best_c

    if best_corr < PROJ_VERY_LOW:
        if acc is not None: acc[1] += time.perf_counter() - _t0
        return '?'

    _sorted_combined = sorted(combined_scores.values(), reverse=True)
    _gap = (_sorted_combined[0] - _sorted_combined[1]
            if len(_sorted_combined) > 1 else 1.0)
    if best_corr >= 0.55 and _gap >= 0.10:
        best_c_inner = templates[best_c].get("inner_blobs", -1)
        if (best_c_inner >= 2 and query_inner == 0
                and all("inner_blobs" in t for t in templates.values())):
            zero_hole = {c: combined_scores[c] for c in combined_scores
                         if templates[c].get("inner_blobs", -1) == 0}
            if zero_hole:
                if acc is not None: acc[1] += time.perf_counter() - _t0
                return max(zero_hole, key=zero_hole.get)
        else:
            if acc is not None: acc[1] += time.perf_counter() - _t0
            return best_c

    if acc is not None:
        _now = time.perf_counter(); acc[1] += _now - _t0; _t0 = _now

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
        hu = _hu_moments(norm)
        best_c_hu, best_dist = '?', float('inf')
        for c, t in templates.items():
            d = _hu_dist(hu, t["hu"])
            if d < best_dist:
                best_dist, best_c_hu = d, c
        result = best_c_hu if best_dist <= HU_DIST_MAX else '?'

    if acc is not None: acc[2] += time.perf_counter() - _t0
    return result


def _reconstruct_val(
    glyphs:    list[tuple[int, Optional[np.ndarray], str, Optional[np.ndarray]]],
    templates: dict,
    acc:       "list[float] | None" = None,
) -> Optional[str]:
    """Reconstruct the val string. Rightmost '?' → 'K'/'M' suffix. See gfl2/stat_ocr.py."""
    items = [(x, norm, hint) for x, norm, hint in glyphs if hint != 'skip']
    if not items:
        return None
    km_eligible = len(items) >= 4
    parts = []
    for i, (x, norm, hint) in enumerate(items):
        if hint == '.':
            parts.append('.')
        else:
            c = _classify(norm, templates, acc=acc)
            if km_eligible and c == '?' and i == len(items) - 1:
                if parts and parts[-1] == '?':
                    parts[-1] = 'M'
                else:
                    parts.append('K')
            else:
                parts.append(c)
    result = ''.join(parts)
    return result if result else None


def _reconstruct_pct(
    glyphs:    list[tuple[int, Optional[np.ndarray], str, Optional[np.ndarray]]],
    templates: dict,
    acc:       "list[float] | None" = None,
) -> Optional[str]:
    """Reconstruct the pct value string from pct-strip glyphs. See gfl2/stat_ocr.py."""
    items = [(x, norm, hint) for x, norm, hint in glyphs if hint != 'skip']
    parts = []
    for i, (x, norm, hint) in enumerate(items):
        if hint == '.':
            parts.append('.')
        else:
            c = _classify(norm, templates, v_primary=True, acc=acc)
            if c == '?' and i == len(items) - 1:
                continue
            parts.append(c)
    result = ''.join(parts)
    result = result.strip('.')
    return result if result and '?' not in result else None


# ─────────────────────────────────────────────────────────────────────────────
# Public engine
# ─────────────────────────────────────────────────────────────────────────────

class StatOcrPadded:
    """Blob-based OCR engine for Daily Gunsmoke stat cells — padded-normalize variant."""

    def __init__(self, templates: dict) -> None:
        self._pct = templates.get("pct", {})
        self._val = templates.get("val", {})

    @classmethod
    def load(cls) -> "StatOcrPadded":
        for p in (PCT_TMPL_F, VAL_TMPL_F):
            if not p.exists():
                raise FileNotFoundError(
                    f"Padded Stat OCR templates not found: {p}\n"
                    "Run: python debugs/stat_ocr_padded.py --build"
                )
        import importlib.util

        def _load_module(path: Path):
            spec = importlib.util.spec_from_file_location(path.stem, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.DATA

        pct_data = _load_module(PCT_TMPL_F)
        val_data = _load_module(VAL_TMPL_F)
        return cls({"pct": pct_data, "val": val_data})

    def read(
        self, cell: np.ndarray, timer=None
    ) -> tuple[Optional[str], Optional[str]]:
        """Read a stat cell crop. Returns (pct_str, val_str); (None, None) on failure."""
        ch = cell.shape[0]
        pct_strip = cell[: int(ch * PCT_STRIP_Y[1]), :]
        val_strip = cell[int(ch * VAL_STRIP_Y[0]) : int(ch * VAL_STRIP_Y[1]), :]

        pct_str = self._read_line(pct_strip, self._pct, is_pct=True)
        val_str = self._read_line(val_strip, self._val, is_pct=False)
        return pct_str, val_str

    def _read_line(
        self, strip: np.ndarray, templates: dict, is_pct: bool
    ) -> Optional[str]:
        if strip.size == 0:
            return None

        thresh = _binarize(strip)

        blobs = _find_blobs(thresh)
        if not blobs:
            return None
        blobs = _filter_y_outliers(blobs, threshold=8 if not is_pct else 12)
        if not blobs:
            return None

        if is_pct:
            glyphs = _extract_pct_glyphs(blobs, thresh)
        else:
            glyphs = _extract_val_glyphs(blobs, thresh)

        if is_pct:
            result = _reconstruct_pct(glyphs, templates)
        else:
            result = _reconstruct_val(glyphs, templates)

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
    """Build and save padded-normalize template JSON from training dicts.
    See gfl2/stat_ocr.py:build_templates for the full contract, including why
    GT-override application lives here (not just in each CLI's --build branch).
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

        pct_strip = cell[: int(ch * PCT_STRIP_Y[1]), :]
        thresh_p  = _binarize(pct_strip)
        blobs_p   = _filter_y_outliers(_find_blobs(thresh_p))
        pct_glyphs = _extract_pct_glyphs(blobs_p, thresh_p)
        digit_glyphs_pct = [(x, norm) for x, norm, hint in pct_glyphs
                            if hint == 'digit' and norm is not None]
        expected_pct = [c for c in pct_str if c in TRAIN_CHARS]

        if len(digit_glyphs_pct) == len(expected_pct):
            for (_, norm), char in zip(digit_glyphs_pct, expected_pct):
                pct_buckets[char].append(_features(norm))
            n_cells += 1

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

    def _write_font_py(path, data):
        src = "# auto-generated (padded-normalize exploration) — do not edit\nDATA = " + json.dumps(data, indent=2) + "\n"
        path.write_text(src, encoding="utf-8")

    _FONTS_DIR.mkdir(parents=True, exist_ok=True)
    _write_font_py(PCT_TMPL_F, pct_templates)
    _write_font_py(VAL_TMPL_F, val_templates)

    if verbose:
        print(f"\nBuilt PADDED templates from {n_cells} cells")
        print(f"  pct -> {PCT_TMPL_F}  chars: { {c: pct_templates[c]['n'] for c in sorted(pct_templates)} }")
        print(f"  val -> {VAL_TMPL_F}  chars: { {c: val_templates[c]['n'] for c in sorted(val_templates)} }")

    return templates


# ─────────────────────────────────────────────────────────────────────────────
# Collect training / verification data — reuses production cell extraction
# (frame-finding / panel-splitting layout logic is NOT part of this
# experiment, so importing it read-only from gfl2.patterns.daily_gunsmoke
# is safe and not subject to the duplication policy above).
# ─────────────────────────────────────────────────────────────────────────────

def _collect_cells(
    image_paths: list[Path],
    tess_only: bool = True,
) -> list[dict]:
    """Extract every stat cell from a list of images. See gfl2/stat_ocr.py:_collect_cells."""
    import shutil, pytesseract
    if not shutil.which("tesseract"):
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    from gfl2.patterns.daily_gunsmoke import (
        _split_panels, _find_frames, _frame_col_cell,
        _ocr_raw, _parse_pct_val, _extract_stat_cell,
        COL1_FR, COL2_FR, COL3_FR, COL4_FR,
    )

    def _tess_label(cell):
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
            for ri, (fx, fy, fw, fh) in enumerate(frames):
                for cname, col_fr in COLS_FR:
                    cell = _frame_col_cell(panel, fx, fy, fw, fh, col_fr)
                    if cell.size == 0:
                        continue
                    if tess_only:
                        pct, val = _tess_label(cell)
                    else:
                        from gfl2.timing import TimerStack
                        pct, val, _ = _extract_stat_cell(cell, TimerStack())
                    if pct is not None or val is not None:
                        key = f"{img_path.stem}_p{pi+1}_r{ri}_{cname}"
                        results.append({
                            "cell":     cell,
                            "pct":      pct or "",
                            "val":      val or "",
                            "source":   key,
                            "img_path": img_path,
                            "panel_idx": pi,
                        })

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark / verification
# ─────────────────────────────────────────────────────────────────────────────

def verify(
    image_paths:  list[Path],
    verbose:      bool = True,
    gt_overrides: dict = None,
) -> dict:
    """Compare padded-normalize pipeline against Tesseract on every cell. See gfl2/stat_ocr.py:verify."""
    engine  = StatOcrPadded.load()
    samples = _collect_cells(image_paths)

    _GT_FILE = Path("stat_gt_overrides.json")
    if gt_overrides is None:
        gt_overrides = json.loads(_GT_FILE.read_text()) if _GT_FILE.exists() else {}
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

    if verbose:
        def pct_str(n, d): return f"{100*n/d:.1f}%" if d else "n/a"
        print(f"\n{'-'*60}")
        print(f"StatOcrPadded verify  ({len(image_paths)} images, {len(samples)} cells)")
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
    import argparse

    parser = argparse.ArgumentParser(
        description="StatOcrPadded (§15 exploration) template builder / verifier"
    )
    parser.add_argument("--build",  action="store_true",
                        help="Build padded templates from images and save")
    parser.add_argument("--verify", action="store_true",
                        help="Verify padded pipeline vs Tesseract ground truth")
    parser.add_argument("--images", default="single/*.png",
                        help="Glob of images to use  [default: single/*.png]")
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

        # Applied here (silently) so a custom --gt-overrides path is honored;
        # build_templates() below re-applies the same dict (idempotent) and
        # prints the "Applied N" line — see its docstring / gfl2/stat_ocr.py's
        # build_templates() for why override application also lives there.
        gt_file = Path(args.gt_overrides) if args.gt_overrides else Path("stat_gt_overrides.json")
        gt_overrides = json.loads(gt_file.read_text(encoding="utf-8")) if gt_file.exists() else {}
        for item in training:
            ov = gt_overrides.get(item["source"])
            if ov:
                if "pct" in ov: item["pct"] = ov["pct"]
                if "val" in ov: item["val"] = ov["val"]

        print("Building padded templates ...")
        t1 = time.perf_counter()
        build_templates(training)
        print(f"  Done  ({time.perf_counter()-t1:.1f}s)  -> {PCT_TMPL_F}, {VAL_TMPL_F}")

    if args.verify:
        verify(image_paths, verbose=True)


if __name__ == "__main__":
    sys.path.insert(0, str(_HERE))
    _main()
