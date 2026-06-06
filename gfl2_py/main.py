#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py - GFL2 report image parser

Usage:
    # Single image (Weekly or Daily):
    python main.py <image.png> [options]

    # Folder (Daily Gunsmoke batch mode — accumulates into daily_gunsmoke.js):
    python main.py <folder/> --pattern daily_gunsmoke

Options:
    --pattern          Report pattern                  [default: weekly_gunsmoke]
                         weekly_gunsmoke  - Weekly challenge summary  → CSV
                         daily_gunsmoke   - Daily Challenge Points    → JS
    --output           Output path                     [default: auto]
                         weekly: <image>.csv
                         daily single: <image>.js
                         daily folder: <folder>/daily_gunsmoke.js
    --score-pipeline   Score detection pipeline        [default: blob]
                         blob      - 1D projection/Hu (~4ms/row, no Tesseract)
                         tesseract - Tesseract OCR (~200ms/row)
    --buff-pipeline    Buff recognition pipeline       [default: projection]
                         projection - 1D projection match (~0.5ms/buff)
                         ocr        - OCR-only
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
from gfl2.patterns.daily_gunsmoke import ReportEntry, save_js

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
    import gfl2.buff_ocr as bo
    bo.PROJ_THRESHOLD = 0.030 if pipeline == "projection" else -1.0


def _process_weekly(image_path: Path, args) -> None:
    image    = cv2.imread(str(image_path))
    score_fn = _get_score_fn(args.score_pipeline)
    parse_fn = PATTERNS["weekly_gunsmoke"]
    try:
        records = parse_fn(image, score_fn=score_fn)
    except TypeError:
        records = parse_fn(image)
    lines    = [GunsmokRecord.csv_header()] + [r.to_csv_row() for r in records]
    out      = Path(args.output) if args.output else image_path.with_suffix(".csv")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} record(s) to {out}")


def _process_daily_single(image_path: Path, args) -> None:
    image    = cv2.imread(str(image_path))
    entries  = PATTERNS["daily_gunsmoke"](image, filename=image_path.stem)
    out      = Path(args.output) if args.output else image_path.with_suffix(".js")
    save_js(entries, out)
    total    = sum(len(e.dolls) for e in entries)
    print(f"Wrote {len(entries)} report(s) / {total} doll rows to {out}")


def _process_daily_folder(folder: Path, args) -> None:
    images  = sorted(folder.glob("gm_d_*.png"))
    if not images:
        print(f"No gm_d_*.png files found in {folder}", file=sys.stderr)
        sys.exit(1)
    out     = Path(args.output) if args.output else folder / "daily_gunsmoke.js"
    total_e = 0
    for img_path in images:
        image   = cv2.imread(str(img_path))
        if image is None:
            print(f"  SKIP {img_path.name} (unreadable)", file=sys.stderr)
            continue
        entries = PATTERNS["daily_gunsmoke"](image, filename=img_path.stem)
        added = save_js(entries, out) or 0
        total_e += added
        status = f"+{added}" if added else "skip"
        print(f"  {img_path.name}: {len(entries)} parsed  [{status}]")
    print(f"Added {total_e} new report(s) → {out}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse GFL2 report screenshots.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("image_path", nargs="?",
                        help="Image file or folder (folder only for daily_gunsmoke)")
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

    _configure_buff_pipeline(args.buff_pipeline)
    target = Path(args.image_path)

    print(f"Pattern: {args.pattern}  Score: {args.score_pipeline}  "
          f"Buff: {args.buff_pipeline}", file=sys.stderr)

    if args.pattern == "daily_gunsmoke":
        if target.is_dir():
            _process_daily_folder(target, args)
        else:
            if not target.exists():
                print(f"Error: not found: {target}", file=sys.stderr); sys.exit(1)
            _process_daily_single(target, args)
    else:
        if not target.exists():
            print(f"Error: not found: {target}", file=sys.stderr); sys.exit(1)
        _process_weekly(target, args)


if __name__ == "__main__":
    main()
