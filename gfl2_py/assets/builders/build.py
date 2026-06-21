#!/usr/bin/env python3
"""
assets/builders/build.py — rebuild Daily Gunsmoke assets in one pass.

Reads each image once and extracts all three Daily GS asset types:
  - Doll portraits           →  assets/dolls/_Name.png
  - Header-stat templates    →  assets/stat_fonts/default/header_templates.json
  - Stat-cell templates      →  assets/stat_fonts/default/templates.json

All outputs share the same cv2.imread / _split_panels / _find_frames calls,
so each image is decoded and its panels are segmented exactly once.

Usage:
    python assets/builders/build.py <folder>             # all *.png in folder
    python assets/builders/build.py image.png            # single image
    python assets/builders/build.py "single/*.png"      # glob pattern
    python assets/builders/build.py <folder> -v          # verbose per-panel log
"""
from __future__ import annotations
import argparse, glob as _glob, json, re, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # project root

import cv2
import numpy as np
import pytesseract

if not shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ── gfl2 imports ──────────────────────────────────────────────────────────────
from gfl2.patterns.daily_gunsmoke import (
    _split_panels, _find_frames,
    STATS_ROW_Y0_FR, STATS_ROW_Y1_FR,
    STATS_DEALT_X, STATS_TAKEN_X, STATS_TURNS_X,
    _frame_col_cell, _ocr_raw, _parse_pct_val,
    COL1_FR, COL2_FR, COL3_FR, COL4_FR,
)
from gfl2.dg_output import _crop_portrait, _save_doll_portrait, _fuzzy_correct
from gfl2.stat_ocr import (
    _filter_y_outliers, _extract_val_glyphs, _features, _avg_features,
    BLOB_MIN_W, BLOB_MAX_W, BLOB_MAX_H, TRAIN_CHARS,
    build_templates,
)

# ── Paths ─────────────────────────────────────────────────────────────────────
_ASSETS_DIR  = Path(__file__).parent.parent           # assets/
HEADER_TMPL  = _ASSETS_DIR / "stat_fonts" / "default" / "header_templates.json"

# ── Header binarization — must match daily_gunsmoke._read_stat_crop ───────────
HDR_THRESH     = 155
HDR_BLOB_MIN_H = 12
_TESS_CFG      = "--psm 7 -c tessedit_char_whitelist=0123456789KM"

# ── Name OCR ──────────────────────────────────────────────────────────────────
_NAME_W_FRAC = 0.14
_BADGE_RE    = re.compile(r"^[A-Za-z]{1,2}\d*$")
_VALID_RE    = re.compile(r"^[A-Z][A-Za-z0-9 \-_\.]{2,}$")


def _ocr_name(panel: np.ndarray,
              name_x0: int, name_x1: int,
              row_y0: int,  row_y1: int) -> str | None:
    cell  = panel[row_y0:row_y1, name_x0:name_x1]
    up    = cv2.resize(cell, (0, 0), fx=8, fy=8, interpolation=cv2.INTER_CUBIC)
    gray  = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY)
    txt   = pytesseract.image_to_string(gray, config="--psm 7").strip()
    clean = re.sub(r"[^A-Za-z0-9_\-\. ]", "", txt).strip()
    words = clean.split()
    while words and len(words[0]) <= 2 and not words[0][0].isupper():
        words.pop(0)
    while words and len(words[-1]) <= 3 and _BADGE_RE.match(words[-1]):
        words.pop()
    name = " ".join(words) or None
    return name if name and _VALID_RE.match(name) else None


# ── Header template helpers ───────────────────────────────────────────────────

def _binarize_hdr(crop: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop
    _, t = cv2.threshold(gray, HDR_THRESH, 255, cv2.THRESH_BINARY_INV)
    return t


def _find_header_blobs(thresh: np.ndarray) -> list[tuple[int, int, int, int]]:
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if BLOB_MIN_W <= w <= BLOB_MAX_W and HDR_BLOB_MIN_H <= h <= BLOB_MAX_H:
            blobs.append((x, y, w, h))
    return sorted(blobs, key=lambda b: (b[1], b[0]))


def _header_crop(panel: np.ndarray,
                 frames: list[tuple[int, int, int, int]],
                 x_range: tuple[float, float]) -> np.ndarray:
    """Extract a stats-row crop using panel-width fractions for X, frame-relative for Y."""
    _, pw = panel.shape[:2]
    _, fy, _, fh = frames[0]
    sy0 = fy - int(fh * STATS_ROW_Y0_FR)
    sy1 = fy - int(fh * STATS_ROW_Y1_FR)
    x0  = max(0, int(pw * x_range[0]))
    x1  = min(pw, int(pw * x_range[1]))
    return panel[sy0:sy1, x0:x1]


def _tess_read(crop: np.ndarray) -> str:
    if crop.size == 0:
        return ""
    up   = cv2.resize(crop, (0, 0), fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY) if up.ndim == 3 else up
    return re.sub(r"[^0-9KM]", "",
                  pytesseract.image_to_string(gray, config=_TESS_CFG).strip())


def _collect_samples(crop: np.ndarray, gt: str) -> list[tuple[str, tuple]]:
    thresh  = _binarize_hdr(crop)
    blobs   = _filter_y_outliers(_find_header_blobs(thresh))
    if not blobs:
        return []
    glyphs  = _extract_val_glyphs(blobs, thresh)
    dglyphs = [(x, norm) for x, norm, hint in glyphs
               if hint == "digit" and norm is not None]
    expected = [c for c in gt if c in TRAIN_CHARS]
    if len(dglyphs) != len(expected):
        return []
    return [(char, _features(norm)) for (_, norm), char in zip(dglyphs, expected)]


# ── Per-panel processing ──────────────────────────────────────────────────────

_STAT_RANGES = [
    (STATS_DEALT_X, "dealt"),
    (STATS_TAKEN_X, "taken"),
    (STATS_TURNS_X, "turns"),
]

_STAT_COLS = [
    ("col1", COL1_FR),
    ("col2", COL2_FR),
    ("col3", COL3_FR),
    ("col4", COL4_FR),
]


def _tess_label_cell(cell: np.ndarray) -> tuple:
    """Tesseract GT label for a stat cell: (pct_str, val_str)."""
    txt = _ocr_raw(cell, "--psm 6")
    pct, val = _parse_pct_val(txt)
    if val is None or len(val) <= 2:
        txt2 = _ocr_raw(cell, "--psm 4")
        pct2, val2 = _parse_pct_val(txt2)
        if val2 and (val is None or len(val2) > len(val)):
            pct = pct2 or pct
            val = val2
    return pct, val


def _process_panel(panel: np.ndarray,
                   buckets: dict[str, list],
                   stat_training: list,
                   verbose: bool = False) -> list[tuple[str, str]]:
    """
    Single pass over one panel:
      - _find_frames called once; result shared by portrait and header paths.
      - Returns [(doll_name, save_action), ...].
    """
    frames = _find_frames(panel)
    if not frames:
        return []

    ph, pw = panel.shape[:2]
    ax, _ay, aw, _ah = frames[0]
    name_x0 = ax + aw + 2
    name_x1 = name_x0 + round(pw * _NAME_W_FRAC)

    results = []

    # ── Portrait path ─────────────────────────────────────────────────────────
    for i, (fx, fy, fw, fh) in enumerate(frames):
        if i + 1 < len(frames):
            row_y1 = frames[i + 1][1]
        else:
            gap    = frames[i][1] - frames[i - 1][1] if i > 0 else fh + 2
            row_y1 = min(ph, fy + gap)

        portrait = _crop_portrait(panel, fx, fy, fw, fh)
        name     = _ocr_name(panel, name_x0, name_x1, fy, row_y1)
        if not name:
            continue
        name   = _fuzzy_correct(name)
        action = _save_doll_portrait(name, portrait)
        results.append((name, action))

    # ── Header-template path (shares frames — no second _find_frames) ─────────
    for fr_range, label in _STAT_RANGES:
        crop = _header_crop(panel, frames, fr_range)
        gt   = _tess_read(crop)
        if not gt:
            if verbose:
                print(f"      {label}: no Tesseract result")
            continue
        samples = _collect_samples(crop, gt)
        for char, feat in samples:
            buckets[char].append(feat)
        if verbose:
            print(f"      {label}: gt={gt!r}  aligned={len(samples)}")

    # ── Stat-cell path (shares frames — no second _find_frames) ──────────────
    for ri, (fx, fy, fw, fh) in enumerate(frames):
        for cname, col_fr in _STAT_COLS:
            cell = _frame_col_cell(panel, fx, fy, fw, fh, col_fr)
            if cell.size == 0:
                continue
            pct, val = _tess_label_cell(cell)
            if pct is not None or val is not None:
                stat_training.append({"cell": cell, "pct": pct or "", "val": val or ""})
                if verbose:
                    print(f"      stat [{ri}][{cname}]: pct={pct!r} val={val!r}")

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", help="Folder, glob pattern, or single .png file")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print per-panel details")
    args = parser.parse_args()

    target = Path(args.target)
    if target.is_dir():
        images = sorted(p for p in target.glob("*.png") if "debug" not in p.stem)
    elif "*" in args.target:
        images = sorted(Path(p) for p in _glob.glob(args.target))
    else:
        images = [target]

    if not images:
        print(f"No images found: {args.target}", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(images)} image(s)…\n")

    buckets:       dict[str, list] = {c: [] for c in TRAIN_CHARS}
    stat_training: list            = []
    doll_totals:   dict[str, str]  = {}
    n_panels = 0

    for img_path in images:
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"  SKIP {img_path.name} (unreadable)")
            continue

        panels = _split_panels(img)
        if args.verbose:
            print(f"  {img_path.name}  ({len(panels)} panel(s))")

        for pi, panel in enumerate(panels):
            n_panels += 1
            if args.verbose:
                print(f"    panel {pi + 1}")
            rows = _process_panel(panel, buckets, stat_training, verbose=args.verbose)
            for name, action in rows:
                if name not in doll_totals or "skip" in doll_totals.get(name, ""):
                    doll_totals[name] = action

    # ── Write header templates ─────────────────────────────────────────────────
    templates   = {c: _avg_features(s) for c, s in sorted(buckets.items()) if s}
    n_samples   = sum(len(v) for v in buckets.values())

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"{'─' * 56}")
    print(f"Panels : {n_panels}  ({len(images)} image(s))")

    if doll_totals:
        print(f"\nDoll portraits ({len(doll_totals)}):")
        for name, action in sorted(doll_totals.items()):
            marker = "+" if "skip" not in action else " "
            print(f"  {marker} {name:<26} {action}")
    else:
        print("\nNo doll portraits found.")

    if templates:
        HEADER_TMPL.parent.mkdir(parents=True, exist_ok=True)
        HEADER_TMPL.write_text(json.dumps(templates, indent=2), encoding="utf-8")
        print(f"\nHeader templates : {n_samples} crops → "
              f"{len(templates)} digits → {HEADER_TMPL}")
    else:
        print("\nNo header template samples (Tesseract found no labelled crops).")

    if stat_training:
        build_templates(stat_training, font="default", verbose=True)
    else:
        print("\nNo stat-cell samples (Tesseract found no labelled cells).")

    print(f"{'─' * 56}")
    try:
        import winsound; winsound.Beep(1000, 300)
    except Exception:
        print('\a', end='', flush=True)


if __name__ == "__main__":
    main()
