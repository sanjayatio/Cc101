#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py - GFL2 report image parser

Usage:
    python main.py <image_path> [options]

Options:
    --pattern          Report pattern                  [default: weekly_gunsmoke]
    --output           Output CSV path                 [default: <image>.csv]
    --score-pipeline   Score detection pipeline        [default: blob]
                         blob      - 1D projection/Hu (~4ms/row, no Tesseract)
                         tesseract - Tesseract OCR (~200ms/row)
    --buff-pipeline    Buff recognition pipeline       [default: projection]
                         projection - 1D projection match (~0.5ms/buff, primary)
                                      falls back to OCR for unknown buffs
                         ocr        - OCR-only (slower, always uses Tesseract)
    --list-patterns    List available patterns and exit

Note: run `python compile_gfl2.py` once after any source changes.
"""
from __future__ import annotations
import sys
import shutil
from pathlib import Path

sys.dont_write_bytecode = True

import argparse
import cv2
import pytesseract

if not shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from gfl2.patterns import PATTERNS
from gfl2.patterns.weekly_gunsmoke import GunsmokRecord

SCORE_PIPELINES = ("blob", "tesseract")
BUFF_PIPELINES  = ("projection", "ocr")


def _get_score_fn(pipeline: str):
    if pipeline == "tesseract":
        return None
    from score_detect import make_score_fn
    try:
        return make_score_fn()
    except FileNotFoundError as e:
        print(f"Warning: {e}\nFalling back to Tesseract score pipeline.", file=sys.stderr)
        return None


def _configure_buff_pipeline(pipeline: str) -> None:
    """Patch buff_ocr to use the requested strategy."""
    import gfl2.buff_ocr as bo
    if pipeline == "ocr":
        # Skip projection — go straight to OCR for every buff
        bo.PROJ_THRESHOLD = -1.0
    else:
        # Restore default (projection-first)
        bo.PROJ_THRESHOLD = 0.030


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse a GFL2 report screenshot into CSV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("image_path", nargs="?")
    parser.add_argument("--pattern", default="weekly_gunsmoke",
                        choices=list(PATTERNS.keys()))
    parser.add_argument("--output", default=None)
    parser.add_argument("--score-pipeline", default="blob",
                        choices=SCORE_PIPELINES, dest="score_pipeline")
    parser.add_argument("--buff-pipeline",  default="projection",
                        choices=BUFF_PIPELINES,  dest="buff_pipeline")
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

    _configure_buff_pipeline(args.buff_pipeline)
    score_fn = _get_score_fn(args.score_pipeline)

    print(f"Score pipeline: {args.score_pipeline}  "
          f"Buff pipeline: {args.buff_pipeline}", file=sys.stderr)

    parse_fn = PATTERNS[args.pattern]
    try:
        records = parse_fn(image, score_fn=score_fn)
    except TypeError:
        records = parse_fn(image)

    lines    = [GunsmokRecord.csv_header()] + [r.to_csv_row() for r in records]
    out_path = Path(args.output) if args.output else image_path.with_suffix(".csv")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} record(s) to {out_path}")


if __name__ == "__main__":
    main()
