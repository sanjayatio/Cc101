#!/usr/bin/env python3
"""
rebuild_assets.py
-----------------
Clears assets/buff and assets/dolls, then re-crops them from a reference
image using the current (correct) layout.

Crops are saved as:  row<N>_buff.png  and  row<N>_doll<1-5>.png
Open each file, identify the character/buff, then rename it to that name.

Usage:
    python rebuild_assets.py gm_250801.png
"""
import argparse
import shutil
import sys
from pathlib import Path

import cv2
import pytesseract
import os

if not shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from gfl2.layout import parse_rows

ASSETS_DIR = Path(__file__).parent / "assets"


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild asset crops from a reference image.")
    parser.add_argument("image", help="Reference screenshot to crop from")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup of existing assets")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: {image_path} not found", file=sys.stderr)
        sys.exit(1)

    # ── backup existing assets ────────────────────────────────────────────────
    if not args.no_backup:
        backup_dir = ASSETS_DIR / "_backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        for category in ("buff", "dolls"):
            for f in (ASSETS_DIR / category).glob("*.png"):
                dst = backup_dir / f"{category}_{f.name}"
                shutil.copy2(f, dst)
        print(f"Backed up existing assets to {backup_dir}")

    # ── clear existing assets ─────────────────────────────────────────────────
    for category in ("buff", "dolls"):
        d = ASSETS_DIR / category
        d.mkdir(parents=True, exist_ok=True)
        for f in d.glob("*.png"):
            f.unlink()
    print("Cleared assets/buff and assets/dolls")

    # ── crop fresh from image ─────────────────────────────────────────────────
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Error: could not read {image_path}", file=sys.stderr)
        sys.exit(1)

    rows = parse_rows(image)
    print(f"Found {len(rows)} rows\n")

    for i, row in enumerate(rows):
        date = row.date or "?"

        buff_cell = row.crop("buff")
        if buff_cell is not None and buff_cell.size > 0:
            out = ASSETS_DIR / "buff" / f"row{i:02d}_buff.png"
            cv2.imwrite(str(out), buff_cell)

        for d in range(1, 6):
            doll_cell = row.crop(f"doll{d}")
            if doll_cell is not None and doll_cell.size > 0:
                out = ASSETS_DIR / "dolls" / f"row{i:02d}_doll{d}.png"
                cv2.imwrite(str(out), doll_cell)

        print(f"  row {i:02d}  date={date}  → cropped buff + 5 dolls")

    print(f"\nDone. Open assets/buff/ and assets/dolls/, identify each crop,")
    print("and rename each file to the character/buff name (e.g. 'Lethal Firepower.png').")
    print("Rows with the same buff/doll will share one file once you rename duplicates.")


if __name__ == "__main__":
    main()
