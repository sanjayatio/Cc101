#!/usr/bin/env python3
"""
debug_layout.py - Shows image dimensions and saves annotated row crops for inspection.
Usage: python debug_layout.py <image>
"""
import sys, shutil
from pathlib import Path
import cv2
import numpy as np
import pytesseract

if not shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from gfl2.layout import parse_rows, _COL

def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_layout.py <image>")
        sys.exit(1)

    img = cv2.imread(sys.argv[1])
    h, w = img.shape[:2]
    print(f"Image size: {w} x {h} px")
    print(f"Expected width for calibrated ratios: 1485 px")
    print(f"Scale factor: {w/1485:.3f}\n")

    out_dir = Path("debug_crops")
    out_dir.mkdir(exist_ok=True)

    rows = parse_rows(img)
    print(f"Rows detected: {len(rows)}\n")

    # Draw column boundaries on first row and save
    row0 = rows[0].img.copy()
    rh, rw = row0.shape[:2]
    colors = [(0,255,0),(255,0,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255),(128,128,0),(0,128,255)]
    for ci, (col, (x0r, x1r)) in enumerate(_COL.items()):
        x0, x1 = int(x0r * rw), int(x1r * rw)
        color = colors[ci % len(colors)]
        cv2.rectangle(row0, (x0, 0), (x1, rh-1), color, 2)
        cv2.putText(row0, col, (x0+2, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    cv2.imwrite(str(out_dir / "row0_annotated.png"), row0)
    print(f"Saved debug_crops/row0_annotated.png  ← open this to check column alignment")

    # Save individual column crops from row 0
    row = rows[0]
    for col in _COL:
        cell = row.crop(col)
        if cell is not None:
            cv2.imwrite(str(out_dir / f"row0_{col}.png"), cell)
    print(f"Saved individual crops to debug_crops/row0_*.png\n")

    # Print exact pixel positions for this image width
    print("Column positions for this image:")
    for col, (x0r, x1r) in _COL.items():
        x0, x1 = int(x0r * w), int(x1r * w)
        print(f"  {col:8s}: x={x0}-{x1}  (width={x1-x0}px)")

if __name__ == "__main__":
    main()
