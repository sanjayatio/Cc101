#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
populate_doll_assets.py
-----------------------
Extracts doll portrait crops from Daily Gunsmoke images and saves them to
assets/dolls/ using OCR-derived names — no manual renaming required.

Cropping strategy:
  1. Take the left 15% of each row (wider than the portrait).
  2. Binarize against the background colour to find non-background regions.
  3. Pick the largest compact (roughly square) contour → tight bounding box.
  4. Crop to that box, normalise to 128×128 for the asset library.

Usage:
    python populate_doll_assets.py <folder>           # all gm_d_*.png
    python populate_doll_assets.py gm_d_20250929.png  # single image

Behaviour:
  - Saves _<DollName>.png to assets/dolls/ (replaces existing if found).
  - Skips dolls whose OCR name fails the validity check.
  - Reports every action taken.
"""
from __future__ import annotations
import sys, re
sys.dont_write_bytecode = True

from pathlib import Path
import cv2
import numpy as np
import pytesseract
import shutil

if not shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from gfl2.patterns.daily_gunsmoke import (
    _split_panels, _crop, _extract_name,
    NAME_X0, NAME_X1,
    DOLL_ROWS_Y0, N_DOLL_ROWS,
)

ASSETS_DOLLS  = Path(__file__).parent / "assets" / "dolls"
PORTRAIT_NORM = 128          # output size in pixels
SEARCH_X1     = 0.15         # search area: left 15% of panel width
BG_DELTA      = 30           # brightness delta from background to count as content
MIN_DIM       = 30           # minimum portrait dimension to be considered valid

_VALID_RE = re.compile(r"^[A-Z][A-Za-z0-9 \-_\.]{2,}$")


def _is_valid(name: str) -> bool:
    return bool(name and _VALID_RE.match(name) and len(name) >= 3)


def _find_portrait_bbox(row_img: np.ndarray) -> tuple[int, int, int, int] | None:
    """
    Return (x, y, w, h) of the doll portrait within the left SEARCH_X1
    of the row, or None if not found.

    Strategy: binarize against the background colour, find contours, pick
    the largest compact (roughly square) one.
    """
    h, w   = row_img.shape[:2]
    region = row_img[:, :int(w * SEARCH_X1)]
    gray   = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

    # Background is the most-common brightness value
    bg   = int(np.argmax(np.bincount(gray.flatten())))
    mask = (np.abs(gray.astype(int) - bg) > BG_DELTA).astype(np.uint8) * 255

    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best, best_score = None, 0
    for c in cnts:
        x, y, cw, ch = cv2.boundingRect(c)
        if cw < MIN_DIM or ch < MIN_DIM:
            continue
        squareness = min(cw, ch) / max(cw, ch)
        score      = cw * ch * squareness
        if score > best_score:
            best_score = score
            best = (x, y, cw, ch)
    return best


def _extract_portraits(image: np.ndarray) -> list[tuple[str, np.ndarray]]:
    """Return [(doll_name, portrait_crop), ...] from all panels and rows."""
    panels  = _split_panels(image)
    results = []
    for panel in panels:
        h, w   = panel.shape[:2]
        y0     = int(h * DOLL_ROWS_Y0)
        row_h  = (h - y0) // N_DOLL_ROWS
        for i in range(N_DOLL_ROWS):
            row  = panel[y0 + i*row_h : y0 + (i+1)*row_h, :]

            # Doll name via OCR
            name = _extract_name(_crop(row, NAME_X0, NAME_X1))
            if not name or not _is_valid(name):
                continue

            # Portrait via tight bounding box
            bbox = _find_portrait_bbox(row)
            if bbox is None:
                continue
            x, y, bw, bh = bbox
            portrait     = row[y:y+bh, x:x+bw]
            if portrait.size == 0:
                continue

            # Normalise to square
            portrait_norm = cv2.resize(portrait, (PORTRAIT_NORM, PORTRAIT_NORM),
                                       interpolation=cv2.INTER_AREA)
            results.append((name, portrait_norm))
    return results


def process(image_path: Path) -> dict[str, str]:
    """Process one image; return {name: action}."""
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"  SKIP {image_path.name}: unreadable")
        return {}
    pairs   = _extract_portraits(image)
    actions = {}
    ASSETS_DOLLS.mkdir(parents=True, exist_ok=True)
    for name, portrait in pairs:
        dest = ASSETS_DOLLS / f"_{name}.png"
        cv2.imwrite(str(dest), portrait)
        actions[name] = f"saved → {dest.name}"
    return actions


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = Path(sys.argv[1])
    images = sorted(target.glob("gm_d_*.png")) if target.is_dir() else [target]

    if not images:
        print(f"No gm_d_*.png found in {target}")
        sys.exit(1)

    total = 0
    for img_path in images:
        print(f"\n{img_path.name}:")
        actions = process(img_path)
        for name, action in sorted(actions.items()):
            print(f"  + {name:<22} {action}")
            total += 1

    print(f"\nDone. {total} portrait(s) saved to {ASSETS_DOLLS}")


if __name__ == "__main__":
    main()
