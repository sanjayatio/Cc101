#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py - GFL2 report image parser

Usage:
    # Single image (Weekly or Daily):
    python main.py <image.png> [options]

    # Folder batch mode:
    python main.py <folder/> --pattern daily_gunsmoke
    python main.py <folder/>                            # weekly_gunsmoke (one CSV per image)

Options:
    --pattern          Report pattern                  [default: weekly_gunsmoke]
                         weekly_gunsmoke  - Weekly challenge summary  → CSV
                         daily_gunsmoke   - Daily Challenge Points    → JS
    --output           Output path (single image only)  [default: auto]
                         weekly: <image>.csv
                         daily:  <image>.js  (folder mode: <folder>/daily_gunsmoke.js)
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
from gfl2.patterns.daily_gunsmoke import (flush_name_templates as _flush_names,
                                            flush_tess_fallbacks as _flush_tess,
                                            set_save_tess_crops as _set_save_tess_crops)
from gfl2.dg_output import ReportEntry, save_js, flush_portrait_log
from gfl2.timing import TimerStack, batch_summary, pipeline_summary

SCORE_PIPELINES = ("blob", "tesseract")
BUFF_PIPELINES  = ("projection", "ocr")


def _get_score_fn(pipeline: str):
    if pipeline == "tesseract":
        return None
    from gfl2.score_ocr import make_score_fn
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
    records  = parse_fn(image, score_fn=score_fn, source_name=image_path.stem)
    lines    = [GunsmokRecord.csv_header()] + [r.to_csv_row() for r in records]
    out      = Path(args.output) if args.output else image_path.with_suffix(".csv")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} record(s) to {out}")


def _process_weekly_folder(folder: Path, args) -> None:
    images = sorted(folder.glob("*.png"))
    if not images:
        print(f"No *.png files found in {folder}", file=sys.stderr)
        sys.exit(1)
    score_fn = _get_score_fn(args.score_pipeline)
    parse_fn = PATTERNS["weekly_gunsmoke"]
    for img_path in images:
        image = cv2.imread(str(img_path))
        if image is None:
            print(f"  SKIP {img_path.name} (unreadable)", file=sys.stderr)
            continue
        records = parse_fn(image, score_fn=score_fn, source_name=img_path.stem)
        lines   = [GunsmokRecord.csv_header()] + [r.to_csv_row() for r in records]
        out     = img_path.with_suffix(".csv")
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  {img_path.name}  →  {out.name}  ({len(records)} rows)")


def _process_daily_single(image_path: Path, args) -> None:
    image = cv2.imread(str(image_path))
    timer = TimerStack()
    with timer.timed(image_path.stem):
        entries = PATTERNS["daily_gunsmoke"](image, filename=image_path.stem, timer=timer)
    out        = Path(args.output) if args.output else image_path.with_suffix(".js")
    added      = save_js(entries, out)
    port_log   = flush_portrait_log()
    _flush_names()
    n_tess     = _flush_tess()
    total_rows = sum(len(e.dolls) for e in entries)
    n_unique   = len({name for name, _ in port_log})
    row_str    = (f"{total_rows} rows → {n_unique} unique"
                  if n_unique < total_rows else f"{total_rows} rows")
    status_str = f"+{added}" if added else "skip (already in JS)"
    tess_str   = f"  tess_fallbacks={n_tess}" if n_tess else ""
    print(f"\n{image_path.name}:  ({row_str}, {timer.root.ms:.0f}ms)  [{status_str}]{tess_str}")
    for name, action in port_log:
        marker = "+" if action != "skip" else " "
        print(f"  {marker} {name:<24} {action}")
    print()
    print(timer.root.tree())


def _process_daily_folder(folder: Path, args) -> None:
    images = sorted(folder.glob("*.png"))
    if not images:
        print(f"No *.png files found in {folder}", file=sys.stderr)
        sys.exit(1)
    out       = Path(args.output) if args.output else folder / "daily_gunsmoke.js"
    total_e   = 0
    all_names = []
    all_roots = []
    for img_path in images:
        image = cv2.imread(str(img_path))
        if image is None:
            print(f"  SKIP {img_path.name} (unreadable)", file=sys.stderr)
            continue
        timer = TimerStack()
        with timer.timed(img_path.name):
            entries = PATTERNS["daily_gunsmoke"](image, filename=img_path.stem, timer=timer)
        added      = save_js(entries, out) or 0
        port_log   = flush_portrait_log()
        total_e   += added
        all_names.append(img_path.name)
        all_roots.append(timer.root)
        total_rows = sum(len(e.dolls) for e in entries)
        n_unique   = len({name for name, _ in port_log})
        row_str    = (f"{total_rows} rows → {n_unique} unique"
                      if n_unique < total_rows else f"{total_rows} rows")
        status     = f"+{added}" if added else "skip"
        print(f"\n{img_path.name}:  ({row_str}, {timer.root.ms:.0f}ms)  [{status}]")
        for name, action in port_log:
            marker = "+" if action != "skip" else " "
            print(f"  {marker} {name:<24} {action}")
    _flush_names()
    n_tess = _flush_tess()
    if n_tess:
        print(f"Tess fallbacks logged: {n_tess} → tests/outputs/daily/stat_tess_fallbacks.json")
    print(f"\nAdded {total_e} new report(s) → {out}")
    if len(all_roots) == 1:
        print(all_roots[0].tree())
    elif all_roots:
        print(batch_summary(all_names, all_roots))
        print(pipeline_summary(all_names, all_roots))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse GFL2 report screenshots.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("image_path", nargs="?",
                        help="Image file or folder")
    parser.add_argument("--pattern", default="weekly_gunsmoke",
                        choices=list(PATTERNS.keys()))
    parser.add_argument("--output", default=None)
    parser.add_argument("--score-pipeline", default="blob",
                        choices=SCORE_PIPELINES, dest="score_pipeline")
    parser.add_argument("--buff-pipeline",  default="projection",
                        choices=BUFF_PIPELINES,  dest="buff_pipeline")
    parser.add_argument("--save-tess-crops", action=argparse.BooleanOptionalAction,
                        default=True, dest="save_tess_crops",
                        help="Save crop PNGs to tests/outputs/daily/ on Tesseract fallback")
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
    _set_save_tess_crops(args.save_tess_crops)
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
        if target.is_dir():
            _process_weekly_folder(target, args)
        else:
            if not target.exists():
                print(f"Error: not found: {target}", file=sys.stderr); sys.exit(1)
            _process_weekly(target, args)

    try:
        import winsound; winsound.Beep(1000, 300)
    except Exception:
        print('\a', end='', flush=True)


if __name__ == "__main__":
    main()
