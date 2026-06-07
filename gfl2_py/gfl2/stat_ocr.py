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
  assets/stat_fonts/<font>/templates.json
  {"pct": {char: {"proj": [...], "hu": [...], "n": N}},
   "val": {char: {…}}}

Build templates:
    python stat_ocr.py --build [--images <glob>] [--font <name>] [--save-crops]

Verify pipeline against Tesseract ground truth:
    python stat_ocr.py --verify [--images <glob>]
"""
from __future__ import annotations
import json, math, sys, glob as _glob
from pathlib import Path
from typing import Optional
import cv2
import numpy as np

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE        = Path(__file__).parent.parent          # project root
FONTS_DIR    = _HERE / "assets" / "stat_fonts"
STAT_SET_DIR = _HERE / "stat_set"
DEFAULT_FONT = "default"

# ── Binarization ──────────────────────────────────────────────────────────────
THRESH_BIN = 180   # THRESH_BINARY_INV; text is gray/orange on near-white bg

# ── Blob size filters (native resolution) ────────────────────────────────────
BLOB_MIN_W, BLOB_MAX_W = 2, 30
BLOB_MIN_H, BLOB_MAX_H = 2, 30
BLOB_MIN_X             = 30   # skip blobs very close to left edge (UI artifacts)

# ── Line-split helpers ────────────────────────────────────────────────────────
LARGE_H_MIN  = 14   # pct-line digit blobs:  h ≈ 19–21 px
DOT_MAX_DIM  =  8   # '.' blob: w ≤ DOT_MAX_DIM AND h ≤ DOT_MAX_DIM
# % detection
PCT_MERGED_W = 18   # merged-% blob width threshold (all 3 parts fused → w ≥ 18)

# ── Normalised glyph dims for feature vectors ─────────────────────────────────
NORM_W_PCT, NORM_H_PCT = 12, 20   # pct-line (large) glyphs
NORM_W_VAL, NORM_H_VAL =  8, 13   # val-line (small) glyphs

# ── Classifier thresholds ─────────────────────────────────────────────────────
PROJ_CORR_MIN = 0.70   # combined (v+h)/2 score; was 0.75 for v-only
HU_DIST_MAX   = 0.30

# ── Training character sets ───────────────────────────────────────────────────
TRAIN_CHARS = list("0123456789KM")   # '.' handled by size; '%' stripped


# ─────────────────────────────────────────────────────────────────────────────
# Feature helpers  (mirrored from score_detect.py)
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


def _proj_corr(a: list[float], b: list[float]) -> float:
    """Pearson correlation between two projection vectors."""
    a_, b_ = np.array(a), np.array(b)
    if a_.std() < 1e-6 or b_.std() < 1e-6:
        return 0.0
    return float(np.corrcoef(a_, b_)[0, 1])


def _hu_dist(a: list[float], b: list[float]) -> float:
    """Mean absolute distance between two Hu moment vectors."""
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def _features(norm: np.ndarray) -> tuple[list[float], list[float], list[float]]:
    return _hu_moments(norm), _v_projection(norm), _h_projection(norm)


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

    # Case A: merged %
    # Back up 10 px to also absorb any stray sub-blobs (e.g. top circle of %)
    # that rendered just to the left of the fused glyph.
    rightmost = sorted_x[-1]
    if rightmost[2] >= PCT_MERGED_W and rightmost[3] >= LARGE_H_MIN:
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

def _classify(norm: np.ndarray, templates: dict) -> str:
    """
    Combined projection correlation (primary) → Hu moment distance (fallback).

    Primary score: average of vertical-projection correlation and
    horizontal-projection correlation.  Using both axes gives better
    discrimination for digit pairs that differ mainly in row-density
    profile (e.g. '4' vs '2': '4' has near-zero energy in the top rows
    while '2' has a full curve there).

    Returns a single char, or '?' if confidence is below both thresholds.
    """
    if not templates:
        return '?'

    vproj = _v_projection(norm)
    hproj = _h_projection(norm)

    combined_scores: dict[str, float] = {}
    for c, t in templates.items():
        v_corr = _proj_corr(vproj, t["proj"])
        h_corr = _proj_corr(hproj, t["hproj"]) if "hproj" in t else 0.0
        combined_scores[c] = (v_corr + h_corr) / 2

    best_c    = max(combined_scores, key=combined_scores.get)
    best_corr = combined_scores[best_c]

    if best_corr >= PROJ_CORR_MIN:
        return best_c

    # Hu moment tiebreaker
    hu = _hu_moments(norm)
    best_c_hu, best_dist = '?', float('inf')
    for c, t in templates.items():
        d = _hu_dist(hu, t["hu"])
        if d < best_dist:
            best_dist, best_c_hu = d, c

    return best_c_hu if best_dist <= HU_DIST_MAX else '?'


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


# ─────────────────────────────────────────────────────────────────────────────
# Public engine
# ─────────────────────────────────────────────────────────────────────────────

class StatOcr:
    """Blob-based OCR engine for Daily Gunsmoke stat cells."""

    def __init__(self, templates: dict) -> None:
        self._pct = templates.get("pct", {})
        self._val = templates.get("val", {})

    # ── Construction ─────────────────────────────────────────────────────────

    @classmethod
    def load(cls, font: str = DEFAULT_FONT) -> "StatOcr":
        path = FONTS_DIR / font / "templates.json"
        if not path.exists():
            raise FileNotFoundError(
                f"Stat OCR templates not found: {path}\n"
                "Run: python stat_ocr.py --build"
            )
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(data)

    # ── Inference ─────────────────────────────────────────────────────────────

    def read(
        self, cell: np.ndarray
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Read a stat cell crop (already trimmed of the progress bar).

        Returns (pct_str, val_str) where:
          pct_str  — digits of the percentage, e.g. "35.38"  (no trailing %)
          val_str  — raw value,                e.g. "665669"

        Returns (None, None) on parse failure; the caller should fall back
        to Tesseract.
        """
        thresh = _binarize(cell)
        blobs  = _find_blobs(thresh)
        if not blobs:
            return None, None

        pct_blobs, val_blobs = _split_lines(blobs)

        pct_glyphs = _extract_pct_glyphs(pct_blobs, thresh)
        val_glyphs = _extract_val_glyphs(val_blobs, thresh)

        pct_str = _reconstruct(pct_glyphs, self._pct)
        val_str = _reconstruct(val_glyphs, self._val)

        return pct_str, val_str


# ─────────────────────────────────────────────────────────────────────────────
# Template builder
# ─────────────────────────────────────────────────────────────────────────────

def _avg_features(samples: list[tuple]) -> dict:
    n           = len(samples)
    avg_hu      = [sum(s[0][i] for s in samples) / n for i in range(7)]
    proj_len    = len(samples[0][1])
    avg_proj    = [sum(s[1][i] for s in samples) / n for i in range(proj_len)]
    hproj_len   = len(samples[0][2])
    avg_hproj   = [sum(s[2][i] for s in samples) / n for i in range(hproj_len)]
    return {"hu": avg_hu, "proj": avg_proj, "hproj": avg_hproj, "n": n}


def build_templates(
    training: list[dict],
    font:     str = DEFAULT_FONT,
    verbose:  bool = True,
) -> dict:
    """
    Build and save template JSON from a list of training dicts:
        {"cell": np.ndarray, "pct": str, "val": str}

    pct should be the digit string WITHOUT trailing '%', e.g. "35.38".
    val should be the raw value string, e.g. "665669" or "2M".

    Returns the templates dict.
    """
    pct_buckets: dict[str, list] = {c: [] for c in TRAIN_CHARS}
    val_buckets: dict[str, list] = {c: [] for c in TRAIN_CHARS}

    n_cells = 0
    for item in training:
        cell    = item["cell"]
        pct_str = item.get("pct") or ""
        val_str = item.get("val") or ""

        thresh = _binarize(cell)
        blobs  = _find_blobs(thresh)
        if not blobs:
            continue

        pct_blobs, val_blobs = _split_lines(blobs)

        # ── pct line ──────────────────────────────────────────────────────
        pct_glyphs = _extract_pct_glyphs(pct_blobs, thresh)
        # Only 'digit' glyphs need training; '.' detected by size
        digit_glyphs_pct = [(x, norm) for x, norm, hint in pct_glyphs
                            if hint == 'digit' and norm is not None]
        # Expected char sequence: remove '.' from pct_str (dot detected by size)
        expected_pct = [c for c in pct_str if c in TRAIN_CHARS]

        if len(digit_glyphs_pct) == len(expected_pct):
            for (_, norm), char in zip(digit_glyphs_pct, expected_pct):
                hu, proj, hproj = _features(norm)
                pct_buckets[char].append((hu, proj, hproj))
            n_cells += 1
        # else: blob count mismatch, skip this cell for training

        # ── val line ──────────────────────────────────────────────────────
        val_glyphs = _extract_val_glyphs(val_blobs, thresh)
        digit_glyphs_val = [(x, norm) for x, norm, hint in val_glyphs
                            if hint == 'digit' and norm is not None]
        expected_val = [c for c in val_str if c in TRAIN_CHARS]

        if len(digit_glyphs_val) == len(expected_val):
            for (_, norm), char in zip(digit_glyphs_val, expected_val):
                hu, proj, hproj = _features(norm)
                val_buckets[char].append((hu, proj, hproj))

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
    out_dir = FONTS_DIR / font
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "templates.json"
    out_path.write_text(json.dumps(templates, indent=2), encoding="utf-8")

    if verbose:
        print(f"\nBuilt templates from {n_cells} cells → {out_path}")
        print(f"  pct chars: { {c: pct_templates[c]['n'] for c in sorted(pct_templates)} }")
        print(f"  val chars: { {c: val_templates[c]['n'] for c in sorted(val_templates)} }")

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

    tess_only=True  (default for --build): forces pure Tesseract labeling so
    that blob-pipeline results are never used as training ground truth.
    tess_only=False (used by --verify): uses the full pipeline (_extract_stat_cell).

    Used for both --build (ground truth) and --verify (reference).
    """
    import shutil, pytesseract
    if not shutil.which("tesseract"):
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    from gfl2.patterns.daily_gunsmoke import (
        _split_panels, _crop, _ocr_raw, _parse_pct_val, _extract_stat_cell,
        DOLL_ROWS_Y0, N_DOLL_ROWS,
        COL1_X0, COL1_X1, COL2_X0, COL2_X1,
        COL3_X0, COL3_X1, COL4_X0, COL4_X1,
        CELL_BOTTOM_TRIM,
    )

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

    COLS = [
        ("col1", COL1_X0, COL1_X1),
        ("col2", COL2_X0, COL2_X1),
        ("col3", COL3_X0, COL3_X1),
        ("col4", COL4_X0, COL4_X1),
    ]

    label_fn = _tess_label if tess_only else _extract_stat_cell

    results = []
    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        panels = _split_panels(img)
        for pi, panel in enumerate(panels):
            h, w = panel.shape[:2]
            y0    = int(h * DOLL_ROWS_Y0)
            row_h = (h - y0) // N_DOLL_ROWS
            for ri in range(N_DOLL_ROWS):
                row  = panel[y0 + ri * row_h: y0 + (ri + 1) * row_h, :]
                rh   = row.shape[0]
                trim = int(rh * (1 - CELL_BOTTOM_TRIM))
                for cname, cx0, cx1 in COLS:
                    cell = _crop(row, cx0, cx1)[:trim, :]
                    pct, val = label_fn(cell)
                    if pct is not None or val is not None:
                        key = f"{img_path.stem}_p{pi+1}_r{ri}_{cname}"
                        results.append({
                            "cell":   cell,
                            "pct":    pct or "",
                            "val":    val or "",
                            "source": key,
                        })

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark / verification
# ─────────────────────────────────────────────────────────────────────────────

def verify(
    image_paths: list[Path],
    font:        str = DEFAULT_FONT,
    verbose:     bool = True,
) -> dict:
    """
    Compare blob pipeline against Tesseract on every cell across all images.
    Returns accuracy dict.
    """
    engine  = StatOcr.load(font)
    samples = _collect_cells(image_paths)

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
        print(f"\n{'─'*60}")
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
        print(f"{'─'*60}")

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
    parser.add_argument("--font",       default=DEFAULT_FONT,
                        help=f"Font name  [default: {DEFAULT_FONT}]")
    parser.add_argument("--save-crops", action="store_true",
                        help="Save individual cell crops to stat_set/")
    args = parser.parse_args()

    if not args.build and not args.verify:
        parser.print_help()
        sys.exit(1)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                         if "debug" not in Path(p).stem)
    if not image_paths:
        print(f"No images matched: {args.images}", file=sys.stderr)
        sys.exit(1)

    print(f"Images: {len(image_paths)}  Font: {args.font}")

    if args.build:
        print("Collecting training data via Tesseract …")
        t0 = time.perf_counter()
        training = _collect_cells(image_paths, tess_only=True)
        print(f"  {len(training)} cells collected  ({time.perf_counter()-t0:.1f}s)")

        if args.save_crops:
            STAT_SET_DIR.mkdir(exist_ok=True)
            manifest = []
            for item in training:
                fname = f"{item['source']}.png"
                cv2.imwrite(str(STAT_SET_DIR / fname), item["cell"])
                manifest.append({"path": f"stat_set/{fname}",
                                  "pct": item["pct"], "val": item["val"],
                                  "font": args.font})
            (STAT_SET_DIR / "manifest.json").write_text(
                json.dumps(manifest, indent=2), encoding="utf-8"
            )
            print(f"  Saved {len(manifest)} crops to stat_set/")

        build_templates(training, font=args.font, verbose=True)

    if args.verify:
        verify(image_paths, font=args.font, verbose=True)


if __name__ == "__main__":
    _main()
