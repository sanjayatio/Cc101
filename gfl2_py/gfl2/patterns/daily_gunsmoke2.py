#!/usr/bin/env python3
"""
daily_gunsmoke2.py — Ground-up rewrite of the Daily Gunsmoke parser.

Panel discovery (replaces midpoint-split heuristic)
----------------------------------------------------
Instead of pre-splitting the image, parse() scans left-to-right:

  1. Search the left FRAME_SEARCH_W (120 px) of the remaining image for
     portrait frames.  These define the anchor for the current report.
  2. OCR the report (all rows, all columns).
  3. Compute the right edge of the last data column (FR + 969 px).
  4. If the remaining image width to the right is >= MIN_REPORT_W (900 px),
     advance x_cursor to report_end and repeat from step 1.
  5. Otherwise stop.

This correctly handles 1-panel images (remaining < 900 px after first report)
and 2-panel images (remaining ≈ 1141 px → second pass finds panel-2 frames).

Timing
------
Every parse call carries a TimerStack.  The completed tree is stored in
result["timing"].root and printed to stdout (or suppressed with quiet=True).

Hierarchy:
  parse [filename]
    report_1
      find_frames
      define_crops
      ocr_rows
        row_0
          name  col1_pct  col1_val  col2_pct  col2_val  col3_pct  col3_val  col4_pct  col4_val
        row_1 … row_4
    report_2 (if present)
      …

Batch CLI
---------
  # single image + wireframe
  python -m gfl2.patterns.daily_gunsmoke2 image.png --debug

  # folder batch — prints per-image trees + final summary
  python -m gfl2.patterns.daily_gunsmoke2 folder/ [--debug]

  # build projection templates from ground-truth CSV
  python -m gfl2.patterns.daily_gunsmoke2 image.png --build --gt gt.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

# Make `gfl2` importable when the script is run directly
# (i.e. `python gfl2/patterns/daily_gunsmoke2.py`).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from gfl2.timing import TimerStack, Span, batch_summary
from gfl2.dg_output import (
    DollRow, ReportEntry, save_js,
    _save_doll_portrait, _crop_portrait,
    _get_doll_name_ocr, _fuzzy_correct, _known_doll_names,
    _NEW_CROPS, flush_name_templates,
)

# ── geometry constants (calibrated on gm_d_20250929.png, 1141 px panel) ──────

FRAME_SEARCH_W = 200   # px to scan from the left edge of each report region
# 200 px (not 120) because the second report's frames start ~91 px into the
# search window (x_cursor lands at FR+969, ~62 px before the panel boundary).
MIN_REPORT_W   = 900   # minimum remaining px for a valid second report

MARGIN         = 5     # px above / below frame for strip crop
PITCH          = 99    # px between consecutive frame tops
MAX_ROWS       = 5
CHAR_NORM_H    = 24    # normalised character height for templates
PROJ_W         = 24    # fixed v_proj / top_v / bot_v length — keeps cosine
                       # comparisons honest when char widths differ across fonts
AMBIG_THRESH   = 0.025
MIN_CHAR_W     = 2
SEG_GAP        = 1     # intra-character gap tolerance
PCT_MAX_SEG_W  = 18   # pct digit widths are ≤ this; wider = merged digit+%
PCT_GLYPH_W    = 22   # approximate width of the % glyph in pixels
PCT_THRESHOLD  = 1    # pct x-proj gap threshold: cols with ≤1 pixel are gaps
VAL_MIN_SLOT_W = 8.5  # minimum px per digit in val forced-seg sweep
OCC_THRESH     = 1    # xp cols with <= this many pixels treated as empty

# Column x-offsets relative to FR = anchor_x + anchor_w
COL_OFFSETS: dict[str, tuple[int, int]] = {
    "name": ( 11, 134),
    "col1": (181, 271),   # damage dealt
    "col2": (445, 536),   # stability
    "col3": (647, 738),   # damage taken
    "col4": (849, 969),   # healed
}

# Vertical offsets relative to frame top fy
NAME_Y = (35, 56)
PCT_Y  = (20, 43)
VAL_Y  = (49, 67)   # 18 px — trimmed to exclude progress-bar rows at bottom

FONT_NAME = "name"
FONT_PCT  = "pct"
FONT_VAL  = "val"

_FONTS_DIR = Path(__file__).parent.parent.parent / "assets" / "fonts"

# Right-most data offset from FR (used to compute report boundary)
_REPORT_RIGHT_PAD = COL_OFFSETS["col4"][1]  # 969


# ─── frame detection ──────────────────────────────────────────────────────────

def _find_frames_in_crop(crop: np.ndarray) -> list[tuple[int, int, int, int]]:
    """
    Find portrait frames in a narrow crop (≈120 px wide).
    Returns (x, y, w, h) sorted by y, coordinates relative to the crop.
    """
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    bg   = int(np.bincount(gray.flatten()).argmax())
    mask = (np.abs(gray.astype(int) - bg) > 30).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cands = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if w >= 40 and h >= 40 and min(w, h) / max(w, h) >= 0.70:
            cands.append((x, y, w, h))
    if not cands:
        return []
    # Use the largest-area frame as the size prototype; discard outliers.
    # This eliminates false positives from panel headers / dividers that pass
    # the squareness check but are significantly smaller than real portrait frames.
    max_area = max(w * h for _, _, w, h in cands)
    cands = [(x, y, w, h) for x, y, w, h in cands if w * h >= max_area * 0.60]
    return sorted(cands, key=lambda b: b[1])[:MAX_ROWS]


# ─── crop definitions ─────────────────────────────────────────────────────────

def _define_crops(
    anchor: tuple[int, int, int, int],
    n_rows: int,
) -> list[dict]:
    """
    Derive all crop rects from anchor (absolute image coordinates).
    Each crop dict: label, row, col, kind, font, rect=(x0,y0,x1,y1).
    """
    ax, ay, aw, ah = anchor
    fr = ax + aw

    _STAT_COLS = [("col1", "col1"), ("col2", "col2"),
                  ("col3", "col3"), ("col4", "col4")]

    crops: list[dict] = []
    for i in range(n_rows):
        fy = ay + i * PITCH
        x0, x1 = fr + COL_OFFSETS["name"][0], fr + COL_OFFSETS["name"][1]
        crops.append(dict(label=f"r{i}_name", row=i, col="name",
                          kind="name", font=FONT_NAME,
                          rect=(x0, fy + NAME_Y[0], x1, fy + NAME_Y[1])))
        for col_key, col_label in _STAT_COLS:
            ox0, ox1 = COL_OFFSETS[col_key]
            cx0, cx1 = fr + ox0, fr + ox1
            crops.append(dict(label=f"r{i}_{col_label}_pct", row=i, col=col_label,
                              kind="pct", font=FONT_PCT,
                              rect=(cx0, fy + PCT_Y[0], cx1, fy + PCT_Y[1])))
            crops.append(dict(label=f"r{i}_{col_label}_val", row=i, col=col_label,
                              kind="val", font=FONT_VAL,
                              rect=(cx0, fy + VAL_Y[0], cx1, fy + VAL_Y[1])))
    return crops


# ─── debug wireframe ──────────────────────────────────────────────────────────

_KIND_COLOR = {
    "name": (0,   200,   0),
    "pct":  (0,   200, 255),
    "val":  (30,  130, 255),
}
_FRAME_COLOR = (255, 80, 0)

def _debug_wireframe(
    panel_slice: np.ndarray,
    frames_local: list[tuple],
    crops_local:  list[dict],
    out_path: str | Path,
) -> None:
    """
    Save annotated copy of a panel slice.
    frames_local and crops_local use coordinates relative to panel_slice.
    """
    dbg = panel_slice.copy()
    for (x, y, w, h) in frames_local:
        cv2.rectangle(dbg, (x, y), (x + w, y + h), _FRAME_COLOR, 2)
        cv2.putText(dbg, "frame", (x, y - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, _FRAME_COLOR, 1, cv2.LINE_AA)
    for crop in crops_local:
        x0, y0, x1, y1 = crop["rect"]
        color = _KIND_COLOR.get(crop["kind"], (180, 180, 180))
        cv2.rectangle(dbg, (x0, y0), (x1, y1), color, 1)
        tag = "_".join(crop["label"].split("_")[1:])[:14]
        cv2.putText(dbg, tag, (x0 + 2, y1 - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.26, color, 1, cv2.LINE_AA)
    cv2.imwrite(str(out_path), dbg)


# ─── binarization + projection ────────────────────────────────────────────────

def _binarize(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    _, b  = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if int((b == 0).sum()) > int((b == 255).sum()):
        b = cv2.bitwise_not(b)
    return b

def _x_proj(b: np.ndarray) -> np.ndarray:
    return (b == 0).sum(axis=0).astype(float)

def _y_proj(b: np.ndarray) -> np.ndarray:
    return (b == 0).sum(axis=1).astype(float)

def _norm_proj(arr: np.ndarray) -> list[float]:
    s = float(arr.sum())
    return (arr / s).tolist() if s > 0 else arr.tolist()


# ─── character segmentation ───────────────────────────────────────────────────

def _segment(bin_img: np.ndarray, gap: int = SEG_GAP,
             threshold: int = 0) -> list[tuple[int, int]]:
    """Gap-based segmentation.

    A column with x-projection ≤ threshold counts as a gap.
    Consecutive gap-columns spanning ≤ gap are treated as intra-character
    noise and ignored (the character is not split).
    """
    xp = _x_proj(bin_img)
    segs: list[list[int]] = []
    in_char = False
    gap_count = 0
    start = 0
    for i, v in enumerate(xp):
        is_gap = (v <= threshold)
        if not in_char:
            if not is_gap:
                in_char, start, gap_count = True, i, 0
        else:
            if is_gap:
                gap_count += 1
                if gap_count > gap:
                    segs.append([start, i - gap_count])
                    in_char = False
            else:
                gap_count = 0
    if in_char:
        segs.append([start, len(xp)])
    return [(s[0], s[1]) for s in segs if s[1] - s[0] >= MIN_CHAR_W]


def _segment_val(bin_img: np.ndarray) -> list[tuple[int, int]]:
    """Segmentation for val strips where digits are touching (no zero gaps).

    Uses an adaptive threshold: columns with x-projection ≤ global_min + 1
    are treated as inter-character gaps.  Merging tolerance is SEG_GAP (1).
    """
    xp = _x_proj(bin_img)
    pos = xp[xp > 0]
    if len(pos) == 0:
        return []
    thresh = int(pos.min())   # adaptive: global min of non-zero values
    return _segment(bin_img, gap=SEG_GAP, threshold=thresh)


def _pct_segs(bin_img: np.ndarray) -> list[tuple[int, int]]:
    """Segmentation for pct strips.

    Uses PCT_THRESHOLD=1 so that stray 1-pixel bridges between the last digit
    and the '%' glyph are treated as gaps.  Any segment wider than
    PCT_MAX_SEG_W either contains the '%' glyph alone (discard) or is a
    digit+% merge (trim by PCT_GLYPH_W from the right to recover the digit).
    """
    segs = _segment(bin_img, gap=SEG_GAP, threshold=PCT_THRESHOLD)
    out = []
    for x0, x1 in segs:
        w = x1 - x0
        if w <= PCT_MAX_SEG_W:
            out.append((x0, x1))
        else:
            # Wider than a digit — trim off the % glyph from the right
            trimmed = x1 - PCT_GLYPH_W
            if trimmed - x0 >= MIN_CHAR_W:
                out.append((x0, trimmed))
            # else: the whole segment is just the % glyph — discard
    return out


def _forced_segs(bin_strip: np.ndarray, n_chars: int) -> list[tuple[int, int]]:
    """
    Fallback segmentation when gap-based _segment() returns the wrong count.
    Divides the OCCUPIED width (first→last non-zero xp column) into n_chars
    equal slots, snapping each boundary to the local xp minimum within ±30%
    of the expected position.  Working over the occupied region prevents blank
    trailing slots when digits don't fill the full strip.
    Suitable for near-monospace digit strips (val / pct).
    """
    xp = _x_proj(bin_strip)
    w = len(xp)
    if n_chars <= 0 or w == 0:
        return []

    # Determine the occupied span using OCC_THRESH to ignore faint noise columns.
    # Fall back to xp>0 only if the strip is entirely faint.
    nz = np.where(xp > OCC_THRESH)[0]
    if len(nz) == 0:
        nz = np.where(xp > 0)[0]
    if len(nz) == 0:
        return []
    occ_start = int(nz[0])
    occ_end   = int(nz[-1]) + 1
    occ_w     = occ_end - occ_start

    if n_chars == 1:
        return [(occ_start, occ_end)] if occ_w >= MIN_CHAR_W else []

    slot = occ_w / n_chars
    splits = [occ_start]
    for i in range(1, n_chars):
        lo = max(splits[-1] + 1, occ_start + int((i - 0.3) * slot))
        hi = min(occ_end,        occ_start + int((i + 0.3) * slot) + 1)
        if lo >= hi:
            mid = max(splits[-1] + 1, occ_start + int(i * slot))
        else:
            mid = lo + int(xp[lo:hi].argmin())
            mid = max(mid, splits[-1] + 1)
        splits.append(min(mid, occ_end - 1))
    splits.append(occ_end)
    return [
        (splits[i], splits[i + 1])
        for i in range(n_chars)
        if splits[i + 1] - splits[i] >= MIN_CHAR_W
    ]


# ─── character features ───────────────────────────────────────────────────────

def _char_features(char_bin: np.ndarray) -> dict:
    # Tight-crop horizontally (x only) to remove background padding from
    # forced-seg slots. Preserves vertical extent so aspect ratio is stable.
    xp_tc = _x_proj(char_bin)
    nz_x = np.where(xp_tc > OCC_THRESH)[0]
    if len(nz_x):
        char_bin = char_bin[:, nz_x[0]:nz_x[-1]+1]
    h, w = char_bin.shape
    if h == 0 or w == 0:
        empty = [0.0] * PROJ_W
        return dict(v_proj=empty, h_proj=[0.0]*CHAR_NORM_H,
                    top_v=empty, bot_v=empty, width=0)
    nw  = max(1, int(w * CHAR_NORM_H / h))
    img = cv2.resize(char_bin, (nw, CHAR_NORM_H), interpolation=cv2.INTER_AREA)
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    mid = CHAR_NORM_H // 2

    def _fixed(arr: np.ndarray) -> list[float]:
        """Interpolate a 1-D projection to exactly PROJ_W elements."""
        raw = _norm_proj(arr)
        if len(raw) == PROJ_W:
            return raw
        xs  = np.linspace(0, 1, PROJ_W)
        xp  = np.linspace(0, 1, len(raw))
        return list(np.interp(xs, xp, raw))

    return dict(
        v_proj = _fixed(_x_proj(img)),
        h_proj = _norm_proj(_y_proj(img)),   # always CHAR_NORM_H long
        top_v  = _fixed(_x_proj(img[:mid])),
        bot_v  = _fixed(_x_proj(img[mid:])),
        width  = nw,
    )


# ─── template store ───────────────────────────────────────────────────────────

_cache: dict[str, dict] = {}

def _load_templates(font: str) -> dict:
    if font not in _cache:
        p = _FONTS_DIR / f"dg2_{font}.json"
        raw = json.loads(p.read_text()) if p.exists() else {}
        # Normalise all stored projection vectors to the current PROJ_W so that
        # templates built before PROJ_W was introduced remain compatible.
        xs = np.linspace(0, 1, PROJ_W)
        for d in raw.values():
            for key in ("v_proj", "top_v", "bot_v"):
                v = d.get(key)
                if v is not None and len(v) != PROJ_W:
                    xp = np.linspace(0, 1, len(v))
                    d[key] = list(np.interp(xs, xp, v))
        _cache[font] = raw
    return _cache[font]

def save_templates(font: str, assets_dir: Path = _FONTS_DIR) -> None:
    p = assets_dir / f"dg2_{font}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(_cache.get(font, {}), indent=2))
    print(f"  saved {p}  ({len(_cache.get(font, {}))} chars)")

def add_template(font: str, char: str, char_bin: np.ndarray) -> None:
    templates = _load_templates(font)
    feats = _char_features(char_bin)
    if char in templates:
        n = int(templates[char].get("count", 1))
        def _avg(old: list, new: list, n: int, target_len: int) -> list:
            """Running average; output is always target_len elements."""
            xs = np.linspace(0, 1, target_len)
            a  = np.interp(xs, np.linspace(0, 1, len(old)), np.array(old, float))
            b  = np.interp(xs, np.linspace(0, 1, len(new)), np.array(new, float))
            return ((a * n + b) / (n + 1)).tolist()
        for key in ("v_proj", "top_v", "bot_v"):
            templates[char][key] = _avg(templates[char][key], feats[key], n, PROJ_W)
        # h_proj is always CHAR_NORM_H long
        templates[char]["h_proj"] = _avg(
            templates[char]["h_proj"], feats["h_proj"], n, CHAR_NORM_H)
        templates[char]["count"] = n + 1
    else:
        templates[char] = dict(feats, count=1)
    _cache[font] = templates


# ─── character matching ───────────────────────────────────────────────────────

def _cosine(a: list[float], b: list[float]) -> float:
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    if len(a) != len(b):
        n = max(len(a), len(b))
        a = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(a)), a)
        b = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(b)), b)
    d = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / d) if d > 1e-9 else 0.0

def _match_char(feats: dict, templates: dict) -> tuple[str, float]:
    if not templates:
        return "?", 0.0
    scores: dict[str, float] = {
        ch: 0.6 * _cosine(feats["v_proj"], t["v_proj"])
          + 0.4 * _cosine(feats["h_proj"], t["h_proj"])
        for ch, t in templates.items()
    }
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_ch, best_sc = ranked[0]
    if len(ranked) >= 2:
        sec_ch, sec_sc = ranked[1]
        if best_sc - sec_sc < AMBIG_THRESH:
            half: dict[str, float] = {}
            for ch in (best_ch, sec_ch):
                t = templates[ch]
                half[ch] = (
                    _cosine(feats["top_v"], t.get("top_v", feats["top_v"]))
                    + _cosine(feats["bot_v"], t.get("bot_v", feats["bot_v"]))
                )
            best_ch = max(half, key=half.__getitem__)
            best_sc = half[best_ch] / 2.0
    return best_ch, best_sc


# ─── strip OCR ────────────────────────────────────────────────────────────────

def _ocr_strip(strip_bgr: np.ndarray, font: str, max_chars: int = 8) -> str:
    """OCR a single strip image.

    pct font
    --------
    Uses standard gap segmentation (SEG_GAP=1).  The strip includes a trailing
    '%' glyph that merges with the last digit when SEG_GAP≥2; with SEG_GAP=1
    they separate.  Any segment wider than PCT_MAX_SEG_W is the '%' and is
    discarded.

    val font
    --------
    Digits touch with no zero-valued column gaps.  _segment_val() uses an
    adaptive threshold (global_min of x-projection) to find inter-char
    boundaries.  Falls back to forced-seg sweep if adaptive gives only one
    segment on a wide strip.
    """
    templates = _load_templates(font)
    if not templates:
        return ""
    bin_strip = _binarize(strip_bgr)

    if font == FONT_PCT:
        segs = _pct_segs(bin_strip)
    elif font == FONT_VAL:
        # Always sweep forced-seg counts over the occupied region.
        # Partial segmentation from _segment_val() is unreliable for touching
        # digits; the sweep with occupied-width _forced_segs is more robust.
        # Constrain max N so each slot is at least VAL_MIN_SLOT_W px wide —
        # this prevents over-segmenting one digit into multiple sub-digit crops.
        xp_v = _x_proj(bin_strip)
        nz_v = np.where(xp_v > OCC_THRESH)[0]  # ignore faint noise columns
        occ_w = int(nz_v[-1]) - int(nz_v[0]) + 1 if len(nz_v) else 0
        best_text  = ""
        best_score = -1.0

        # Candidate 1: natural (gap-based) segmentation — wins when clean gaps exist.
        # Guard: reject if any segment is too narrow (split artifact) or too wide
        # (merged chars).  4-14 px is the valid single-digit range for this font.
        nat_segs = _segment_val(bin_strip)
        if len(nat_segs) >= 1:
            nat_widths = [x1 - x0 for x0, x1 in nat_segs]
            if min(nat_widths) >= 4 and max(nat_widths) <= 14:
                pairs = [_match_char(_char_features(bin_strip[:, x0:x1]), templates)
                         for x0, x1 in nat_segs]
                avg = sum(s for _, s in pairs) / len(nat_segs)
                if avg > best_score:
                    best_score = avg
                    best_text  = "".join(c for c, _ in pairs)

        # Candidate 2: forced-seg sweep over occupied region
        for n in range(1, max_chars + 1):
            if n > 1 and occ_w > 0 and occ_w / n < VAL_MIN_SLOT_W:
                continue
            trial = _forced_segs(bin_strip, n)
            if len(trial) != n:
                continue
            pairs = [_match_char(_char_features(bin_strip[:, x0:x1]), templates)
                     for x0, x1 in trial]
            avg = sum(s for _, s in pairs) / n
            if avg > best_score:
                best_score = avg
                best_text  = "".join(c for c, _ in pairs)
        return best_text
    else:
        segs = _segment(bin_strip)

    return "".join(
        _match_char(_char_features(bin_strip[:, x0:x1]), templates)[0]
        for x0, x1 in segs
    )


# ─── row + panel OCR ─────────────────────────────────────────────────────────

def _ocr_report(
    image:   np.ndarray,
    frames:  list[tuple],
    crops:   list[dict],
    timer:   TimerStack,
) -> list[dict]:
    """OCR all rows in one report, timing each row and each strip."""
    ih, iw = image.shape[:2]
    rows: list[dict] = []

    with timer.timed("ocr_rows"):
        for row_i in range(len(frames)):
            with timer.timed(f"row_{row_i}"):
                row: dict[str, str] = {}
                for crop in crops:
                    if crop["row"] != row_i:
                        continue
                    x0, y0, x1, y1 = crop["rect"]
                    x0, y0 = max(0, x0), max(0, y0)
                    x1, y1 = min(iw, x1), min(ih, y1)
                    if x1 <= x0 or y1 <= y0:
                        row[crop["label"]] = ""
                        continue
                    if crop["kind"] == "name":
                        # Use doll_name_ocr projection classifier (same as dg1).
                        # The classifier needs the same crop it was trained on:
                        #   full frame height, x from fr+2 to fr+162
                        # (dg1: panel[fy:fy+fh, ax+aw+2 : ax+aw+2+round(panel_w*0.14)])
                        # COL_OFFSETS["name"] is narrower and gives wrong projections.
                        with timer.timed("name"):
                            ax0, ay0, aw0, ah0 = frames[0]   # anchor
                            fr_x   = ax0 + aw0
                            nx0    = max(0, fr_x + 2)
                            nx1    = min(iw, fr_x + 162)   # 160px ≈ round(1141*NAME_W_FRAC)
                            _, fy_fr, _, fh_fr = frames[row_i]
                            name_strip = image[fy_fr:fy_fr + fh_fr, nx0:nx1]
                            _name_ocr  = _get_doll_name_ocr()
                            name_str   = _name_ocr.classify(name_strip) if _name_ocr else ""
                            if name_str:
                                name_str = _fuzzy_correct(name_str)
                        row[crop["label"]] = name_str
                    else:
                        # timer label: "col1_pct", "col1_val", …
                        timer_label = crop["col"] + "_" + crop["kind"]
                        with timer.timed(timer_label):
                            row[crop["label"]] = _ocr_strip(
                                image[y0:y1, x0:x1], crop["font"]
                            )
                # Portrait save
                fx, fy, fw, fh = frames[row_i]
                name = row.get(f"r{row_i}_name", "")
                if name:
                    with timer.timed("save_portrait"):
                        portrait = _crop_portrait(image, fx, fy, fw, fh)
                        if portrait.size > 0:
                            _save_doll_portrait(name, portrait)
                rows.append(row)

    return rows


# ─── public entry point ───────────────────────────────────────────────────────

def parse(
    image:     np.ndarray,
    debug_dir: Optional[Path] = None,
    timer:     Optional[TimerStack] = None,
    quiet:     bool = False,
) -> list[dict]:
    """
    Parse a Daily Gunsmoke image containing one or two side-by-side reports.

    Algorithm
    ---------
    Scans left to right.  For each candidate position x_cursor:
      1. Search image[:, x_cursor : x_cursor + FRAME_SEARCH_W] for frames.
      2. If found, define crops from the anchor, OCR the report.
      3. Advance x_cursor to FR + _REPORT_RIGHT_PAD.
      4. If remaining width < MIN_REPORT_W, stop.

    Returns a list of report dicts:
      report_idx, frames, anchor, crops, rows, timing_root (Span)
    """
    if timer is None:
        timer = TimerStack()

    ih, iw = image.shape[:2]
    x_cursor   = 0
    report_idx = 1
    results: list[dict] = []

    while x_cursor < iw:
        with timer.timed(f"report_{report_idx}"):

            # ── 1. find frames ────────────────────────────────────────────
            with timer.timed("find_frames"):
                search_end   = min(x_cursor + FRAME_SEARCH_W, iw)
                crop_slice   = image[:, x_cursor:search_end]
                frames_local = _find_frames_in_crop(crop_slice)

            if not frames_local:
                break   # no frames → no more reports

            # Lift to absolute image coordinates
            frames = [(x + x_cursor, y, w, h) for x, y, w, h in frames_local]
            anchor = frames[0]
            ax, ay, aw, ah = anchor
            fr = ax + aw

            # ── 2. define crops ───────────────────────────────────────────
            with timer.timed("define_crops"):
                crops = _define_crops(anchor, len(frames))

            # ── 3. optional debug wireframe ───────────────────────────────
            if debug_dir is not None:
                report_end_x  = min(fr + _REPORT_RIGHT_PAD + 80, iw)
                panel_slice   = image[:, x_cursor:report_end_x]
                frames_local2 = [(x - x_cursor, y, w, h) for x, y, w, h in frames]
                crops_local   = [
                    {**c, "rect": (
                        c["rect"][0] - x_cursor, c["rect"][1],
                        c["rect"][2] - x_cursor, c["rect"][3],
                    )}
                    for c in crops
                ]
                out_p = Path(debug_dir) / f"dg2_report{report_idx}_wire.png"
                _debug_wireframe(panel_slice, frames_local2, crops_local, out_p)

            # ── 4. OCR ───────────────────────────────────────────────────
            rows = _ocr_report(image, frames, crops, timer)

            results.append(dict(
                report_idx  = report_idx,
                frames      = frames,
                anchor      = anchor,
                crops       = crops,
                rows        = rows,
            ))

            # ── 5. advance cursor ─────────────────────────────────────────
            report_end = fr + _REPORT_RIGHT_PAD
            remaining  = iw - report_end
            if remaining < MIN_REPORT_W:
                break
            x_cursor   = report_end
            report_idx += 1

    return results


# ─── build mode ───────────────────────────────────────────────────────────────

def _build_templates(
    image_path: str | Path,
    gt_path:    str | Path,
    debug:      bool = False,
) -> None:
    """Learn per-character projection templates from a ground-truth CSV."""
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    gt_rows: dict[tuple[int, int], dict] = {}
    with open(gt_path, newline="") as f:
        panel_counters: dict[int, int] = {}
        for rec in csv.DictReader(f):
            ridx  = int(rec["report_idx"])
            row_i = panel_counters.get(ridx, 0)
            panel_counters[ridx] = row_i + 1
            gt_rows[(ridx, row_i)] = rec

    timer   = TimerStack()
    results = parse(image, debug_dir=Path(image_path).parent if debug else None,
                    timer=timer)
    learned: dict[str, int] = {FONT_NAME: 0, FONT_PCT: 0, FONT_VAL: 0}
    ih, iw  = image.shape[:2]

    for result in results:
        p_idx  = result["report_idx"]
        frames = result["frames"]
        crops  = result["crops"]

        for row_i in range(len(frames)):
            gt = gt_rows.get((p_idx, row_i))
            if gt is None:
                continue
            gt_map = {
                "name":     gt.get("dollName", ""),
                "col1_pct": gt.get("dmg_dealt_pct", ""),
                "col1_val": gt.get("dmg_dealt_val", ""),
                "col2_pct": gt.get("stab_pct", ""),
                "col2_val": gt.get("stab_val", ""),
                "col3_pct": gt.get("dmg_taken_pct", ""),
                "col3_val": gt.get("dmg_taken_val", ""),
                "col4_pct": gt.get("healed_pct", ""),
                "col4_val": gt.get("healed_val", ""),
            }
            for crop in crops:
                if crop["row"] != row_i:
                    continue
                col, kind = crop["col"], crop["kind"]
                # Name recognition is handled by doll_name_ocr; skip here.
                if kind == "name":
                    continue
                key      = f"{col}_{kind}"
                expected = gt_map.get(key, "").strip().replace(",", "")
                if not expected:
                    continue
                x0, y0, x1, y1 = crop["rect"]
                x0, y0 = max(0, x0), max(0, y0)
                x1, y1 = min(iw, x1), min(ih, y1)
                if x1 <= x0 or y1 <= y0:
                    continue
                strip     = image[y0:y1, x0:x1]
                bin_strip = _binarize(strip)
                # Use the same font-specific segmentation as _ocr_strip.
                if kind == "pct":
                    segs = _pct_segs(bin_strip)
                elif kind == "val":
                    segs = _segment_val(bin_strip)
                else:
                    segs = _segment(bin_strip)
                # Fallback: forced equal-width split when count is still wrong.
                if len(segs) != len(expected):
                    segs = _forced_segs(bin_strip, len(expected))
                if len(segs) != len(expected):
                    if debug:
                        print(f"  SKIP {crop['label']:24} "
                              f"segs={len(segs)} expected={len(expected)!r}")
                    continue
                for (sx0, sx1), ch in zip(segs, expected):
                    cb = bin_strip[:, sx0:sx1]
                    if cb.shape[0] >= 3 and cb.shape[1] >= 2:
                        add_template(crop["font"], ch, cb)
                        learned[crop["font"]] += 1

    for font in (FONT_NAME, FONT_PCT, FONT_VAL):
        save_templates(font)
    print(f"Build complete.  Chars learned: {learned}")


# ─── JS conversion ──────────────────────────────────────────────────────────────

def _to_report_entry(filename: str, result: dict) -> ReportEntry:
    """Convert a dg2 parse() result dict to a ReportEntry for JS output."""
    dolls = []
    for i, row_dict in enumerate(result["rows"]):
        dolls.append(DollRow(
            name          = row_dict.get(f"r{i}_name") or None,
            dmg_dealt_pct = row_dict.get(f"r{i}_col1_pct") or None,
            dmg_dealt_val = row_dict.get(f"r{i}_col1_val") or None,
            stab_pct      = row_dict.get(f"r{i}_col2_pct") or None,
            stab_val      = row_dict.get(f"r{i}_col2_val") or None,
            dmg_taken_pct = row_dict.get(f"r{i}_col3_pct") or None,
            dmg_taken_val = row_dict.get(f"r{i}_col3_val") or None,
            healed_pct    = row_dict.get(f"r{i}_col4_pct") or None,
            healed_val    = row_dict.get(f"r{i}_col4_val") or None,
        ))
    return ReportEntry(
        filename        = filename,
        report_idx      = result["report_idx"],
        score           = None,   # TODO: add header OCR to dg2
        dmg_dealt_total = None,
        dmg_taken_total = None,
        combat_turns    = None,
        dolls           = dolls,
    )


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _process_one(
    image_path: Path,
    debug_dir:  Optional[Path],
    quiet:      bool,
    out_js:     Optional[Path] = None,
) -> Optional[Span]:
    """Parse one image; print timing tree; optionally write JS; return root Span."""
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"  ERROR: cannot read {image_path}", file=sys.stderr)
        return None

    timer = TimerStack()
    with timer.timed(image_path.name):
        results = parse(img, debug_dir=debug_dir, timer=timer)

    if not quiet:
        print(timer.root.tree())
        for r in results:
            print(f"\n  report {r['report_idx']}  ({len(r['frames'])} rows)")
            for row in r["rows"]:
                vals = {k.split("_", 1)[1]: v for k, v in row.items()}
                print("    " + "  |  ".join(
                    f"{k}: {v!r}" for k, v in vals.items()
                ))
        print()

    # JS accumulation
    if out_js is not None:
        entries = [_to_report_entry(image_path.stem, r) for r in results]
        added   = save_js(entries, out_js)
        if not quiet:
            status = f"+{added}" if added else "skip"
            print(f"  JS: {status} -> {out_js}")

    return timer.root


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Daily Gunsmoke parser v2 — projection-based OCR"
    )
    ap.add_argument("target",
                    help="Image file, directory of images, or glob pattern")
    ap.add_argument("--debug",  action="store_true",
                    help="Save annotated wireframe PNGs alongside each image")
    ap.add_argument("--quiet",  action="store_true",
                    help="Suppress per-image output; show only batch summary")
    ap.add_argument("--build",  action="store_true",
                    help="Build projection templates from --gt ground-truth CSV")
    ap.add_argument("--gt",     metavar="CSV",
                    help="Ground-truth CSV for --build mode")
    ap.add_argument("--output", default=None, metavar="JS",
                    help="JS output path (default: <image>.js or <folder>/daily_gunsmoke.js)")
    args = ap.parse_args()

    target = Path(args.target)
    if target.is_dir():
        images = sorted(target.glob("*.png"))
    elif "*" in str(target) or "?" in str(target):
        images = sorted(Path(".").glob(str(target)))
    else:
        images = [target]

    if not images:
        print(f"No images found: {args.target}")
        return

    # Determine JS output path
    if args.output:
        folder_js: Optional[Path] = Path(args.output)
    elif target.is_dir():
        folder_js = target / "daily_gunsmoke.js"
    else:
        folder_js = None   # each image gets its own .js

    all_names: list[str] = []
    all_roots: list = []

    for img_path in images:
        debug_dir = img_path.parent if args.debug else None
        if args.build:
            gt_path = Path(args.gt) if args.gt else img_path.with_suffix(".csv")
            timer = TimerStack()
            with timer.timed("total"):
                _build_templates(img_path, gt_path, debug=args.debug)
            all_names.append(img_path.name)
            all_roots.append(timer.root)
        else:
            out_js = folder_js if folder_js is not None else img_path.with_suffix(".js")
            root   = _process_one(img_path, debug_dir, args.quiet, out_js=out_js)
            if root is not None:
                all_names.append(img_path.name)
                all_roots.append(root)

    if len(all_roots) > 1:
        print(batch_summary(all_names, all_roots))


if __name__ == "__main__":
    main()
