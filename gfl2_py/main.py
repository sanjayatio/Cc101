#!/usr/bin/env python3
"""
main.py - GFL2 report image parser

Usage:
    python main.py <image_path> [--pattern PATTERN] [--output OUTPUT]

Arguments:
    image_path    Path to the report screenshot (PNG/JPG/BMP)

Options:
    --pattern     Report pattern [default: weekly_gunsmoke]
    --output      Output CSV path [default: <image_name>.csv]
    --list-patterns  List available patterns and exit
"""
from __future__ import annotations
import argparse
import shutil
import sys
from pathlib import Path

import cv2
import pytesseract

if not shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from gfl2.patterns import PATTERNS
from gfl2.patterns.weekly_gunsmoke import GunsmokRecord


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse a GFL2 report screenshot into CSV.")
    parser.add_argument("image_path", nargs="?", help="Path to report screenshot")
    parser.add_argument("--pattern", default="weekly_gunsmoke", choices=list(PATTERNS.keys()))
    parser.add_argument("--output", default=None, help="Output CSV path (default: <image>.csv)")
    parser.add_argument("--list-patterns", action="store_true")
    args = parser.parse_args()

    if args.list_patterns:
        for name in PATTERNS:
            print(f"  {name}")
        sys.exit(0)

    if not args.image_path:
        parser.print_help()
        sys.exit(1)

    image_path = Path(args.image_path)
    if not image_path.exists():
        print(f"Error: file not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Error: could not read image: {image_path}", file=sys.stderr)
        sys.exit(1)

    records = PATTERNS[args.pattern](image)

    lines = [GunsmokRecord.csv_header()] + [r.to_csv_row() for r in records]
    csv_text = "\n".join(lines) + "\n"

    out_path = Path(args.output) if args.output else image_path.with_suffix(".csv")
    out_path.write_text(csv_text, encoding="utf-8")
    print(f"Wrote {len(records)} record(s) to {out_path}")


if __name__ == "__main__":
    main()
