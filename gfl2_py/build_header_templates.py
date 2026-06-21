#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_header_templates.py — build OCR templates for header stats-row digits.

The stats-row numbers (Damage Dealt / Damage Taken / Combat Turns) are rendered
at a different size from stat-cell val glyphs, so they need their own template set.

Uses Tesseract as ground truth to label blobs extracted from the header crops,
then averages features per digit class — same pipeline as stat_ocr --build.

Usage:
    python build_header_templates.py --images "single/ib_d_*.png"

Output:
    assets/stat_fonts/default/header_templates.json

The templates are then loaded by daily_gunsmoke._read_stat_crop via
_get_header_stat_templates().
"""
from __future__ import annotations
import argparse
import glob as _glob
import json
import re
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
import pytesseract

sys.dont_write_bytecode = True

if not shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ── Reuse stat_ocr machinery ──────────────────────────────────────────────────
from gfl2.stat_ocr import (
    _filter_y_outliers,
    _extract_val_glyphs, _features, _avg_features,
    BLOB_MIN_W, BLOB_MAX_W, BLOB_MAX_H,
    NORM_W_VAL, NORM_H_VAL, TRAIN_CHARS,
)

# ── Header-specific binarization ──────────────────────────────────────────────
# Must match the constants used in daily_gunsmoke._read_stat_crop.
# Lower threshold separates touching digits (e.g. '4'+'8' merge at THRESH_BIN=180).
# Min-height 12 filters comma thousand-separator blobs (h≈5-7) and UI-chrome noise.
HDR_THRESH     = 155
HDR_BLOB_MIN_H =  12


def _binarize_hdr(crop: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop
    _, t = cv2.threshold(gray, HDR_THRESH, 255, cv2.THRESH_BINARY_INV)
    return t


def _find_header_blobs(thresh: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Like stat_ocr._find_blobs but with h≥HDR_BLOB_MIN_H to filter commas/noise."""
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if BLOB_MIN_W <= w <= BLOB_MAX_W and HDR_BLOB_MIN_H <= h <= BLOB_MAX_H:
            blobs.append((x, y, w, h))
    return sorted(blobs, key=lambda b: (b[1], b[0]))

# ── Reuse header geometry from daily_gunsmoke ─────────────────────────────────
from gfl2.patterns.daily_gunsmoke import (
    _split_panels, _find_frames,
    STATS_ROW_Y0, STATS_ROW_Y1,
    STATS_DEALT_FR, STATS_TAKEN_FR, STATS_TURNS_FR,
)

OUT_PATH = Path(__file__).parent / "assets" / "stat_fonts" / "default" / "header_templates.json"

TESS_CFG = "--psm 7 -c tessedit_char_whitelist=0123456789KM"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _stats_crop(panel: np.ndarray, fr_range: tuple[float, float]) -> np.ndarray:
    ph, pw = panel.shape[:2]
    frames = _find_frames(panel)
    if not frames:
        return np.zeros((0, 0, 3), dtype=np.uint8)
    fx, _fy, fw, _fh = frames[0]
    fr = fx + fw
    sy0, sy1 = int(ph * STATS_ROW_Y0), int(ph * STATS_ROW_Y1)
    x0 = max(0, fr + int(fw * fr_range[0]))
    x1 = min(pw, fr + int(fw * fr_range[1]))
    return panel[sy0:sy1, x0:x1]


def _tess_read(crop: np.ndarray) -> str:
    """Return Tesseract digit string from a header crop, e.g. '12583' or '6453K'."""
    if crop.size == 0:
        return ""
    up   = cv2.resize(crop, (0, 0), fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY) if up.ndim == 3 else up
    txt  = pytesseract.image_to_string(gray, config=TESS_CFG).strip()
    return re.sub(r"[^0-9KM]", "", txt)


def _collect_samples(
    crop:      np.ndarray,
    gt_string: str,
) -> list[tuple[str, tuple]]:
    """
    Extract blob features from *crop* and align to *gt_string*.

    Returns a list of (char, feature_tuple) pairs for digits that could be
    unambiguously aligned.  Skips the crop if blob count != expected char count.
    """
    thresh = _binarize_hdr(crop)
    blobs  = _filter_y_outliers(_find_header_blobs(thresh))
    if not blobs:
        return []

    glyphs = _extract_val_glyphs(blobs, thresh)
    # keep only 'digit' hint entries (skip '.' and 'skip')
    digit_glyphs = [(x, norm) for x, norm, hint in glyphs
                    if hint == "digit" and norm is not None]

    # Expected chars = all TRAIN_CHARS characters in the gt string
    expected = [c for c in gt_string if c in TRAIN_CHARS]

    if len(digit_glyphs) != len(expected):
        return []   # count mismatch — skip to avoid mis-labelling

    return [(char, _features(norm)) for (_, norm), char in zip(digit_glyphs, expected)]


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--images", required=True,
                        help='Glob pattern for source images, e.g. "single/ib_d_*.png"')
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print per-crop details")
    args = parser.parse_args()

    image_paths = sorted(_glob.glob(args.images))
    if not image_paths:
        print(f"No images found matching: {args.images}", file=sys.stderr)
        sys.exit(1)

    print(f"Building header templates from {len(image_paths)} image(s)…")

    buckets: dict[str, list] = {c: [] for c in TRAIN_CHARS}
    n_panels = n_crops = 0

    for path in image_paths:
        img = cv2.imread(path)
        if img is None:
            print(f"  SKIP {path} (unreadable)")
            continue

        panels = _split_panels(img)
        for pi, panel in enumerate(panels):
            n_panels += 1
            for crop_range, label in [
                (STATS_DEALT_FR, "dealt"),
                (STATS_TAKEN_FR, "taken"),
                (STATS_TURNS_FR, "turns"),
            ]:
                crop = _stats_crop(panel, crop_range)
                if crop.size == 0:
                    continue
                gt = _tess_read(crop)
                if not gt:
                    if args.verbose:
                        print(f"  {Path(path).name} p{pi+1} {label}: no Tesseract result")
                    continue

                samples = _collect_samples(crop, gt)
                for char, feat in samples:
                    buckets[char].append(feat)
                n_crops += 1

                if args.verbose:
                    print(f"  {Path(path).name} p{pi+1} {label}: gt={gt!r}"
                          f"  blobs→{len(samples)} aligned")

    print(f"\nProcessed {n_panels} panel(s), {n_crops} crops with Tesseract labels.")

    # ── Build templates ───────────────────────────────────────────────────────
    templates: dict[str, dict] = {}
    for char in sorted(buckets):
        samples = buckets[char]
        if not samples:
            continue
        templates[char] = _avg_features(samples)

    if not templates:
        print("ERROR: no samples collected — check image paths.", file=sys.stderr)
        sys.exit(1)

    print("\nSamples per digit:")
    for c in sorted(templates):
        print(f"  {c!r}: {templates[c]['n']} sample(s)")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(templates, indent=2), encoding="utf-8")
    print(f"\nSaved {len(templates)} digit templates → {OUT_PATH}")
    print("Run main.py to verify — stats_row/tess should drop to near zero.")


if __name__ == "__main__":
    main()
