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
                         weekly: <image>.csv next to the image, UNLESS the
                                 image is under tests/inputs/ (test fixture)
                                 -> tests/outputs/weekly_gunsmoke/<image>.csv
                         daily:  <image>.js  (folder mode: <folder>/daily_gunsmoke.js)
    --score-pipeline   Score detection pipeline        [default: blob]
                         blob      - 1D projection/Hu (~4ms/row, no Tesseract)
                         tesseract - Tesseract OCR (~200ms/row)
    --buff-pipeline    Buff recognition pipeline       [default: projection]
                         projection - 1D projection match (~0.5ms/buff)
                         ocr        - OCR-only
    --stat-ocr-engine  Daily Gunsmoke stat-cell OCR engine [default: production]
                         production - gfl2.stat_ocr.StatOcr (direct-stretch)
                         padded     - gfl2.stat_ocr_padded.StatOcrPadded
                                      (aspect-preserving pad, decision 47)
                         dp         - gfl2.stat_ocr_dp.StatOcrDp (pct-line
                                      only, exploratory -- val is ALWAYS a
                                      no-op stub, so val is left as `null`
                                      unless --stat-tess-fallback is passed;
                                      see decisions.txt)
    --stat-templates   Template variant name for BOTH pct+val [default: engine's own]
                         e.g. 'padded' -> stat_pct_padded.py/stat_val_padded.py
    --stat-tess-fallback / --no-stat-tess-fallback
                       Run Tesseract psm6/psm4 when a stat-cell engine
                       leaves pct/val as None          [default: off]
                         Off by default: an engine with an unimplemented
                         val-line (dp) would otherwise force a ~300ms
                         Tesseract call on EVERY cell, not just a genuine
                         blob-classifier miss.
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

SCORE_PIPELINES  = ("blob", "tesseract")
BUFF_PIPELINES   = ("projection", "ocr")
STAT_OCR_ENGINES = ("production", "padded", "dp")

_ROOT                     = Path(__file__).resolve().parent
_TESTS_INPUTS_DIR         = _ROOT / "tests" / "inputs"
_TESTS_OUTPUTS_WEEKLY_DIR = _ROOT / "tests" / "outputs" / "weekly_gunsmoke"


def _default_weekly_output(image_path: Path) -> Path:
    """Default CSV path for a weekly-gunsmoke image when --output is not given.

    Images under tests/inputs/ are committed test fixtures; writing
    <image>.csv next to them pollutes the fixtures directory with generated
    output (docs/action_items.txt #4). Redirect those to
    tests/outputs/weekly_gunsmoke/ instead, mirroring the existing
    tests/outputs/daily/ convention. Any other image (single/, or a user's
    own screenshot folder) keeps the original <image>.csv-next-to-the-image
    default.
    """
    try:
        image_path.resolve().relative_to(_TESTS_INPUTS_DIR)
    except ValueError:
        return image_path.with_suffix(".csv")
    _TESTS_OUTPUTS_WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    return _TESTS_OUTPUTS_WEEKLY_DIR / (image_path.stem + ".csv")


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


def _get_stat_ocr_engine(engine: str, tmpl_variant: str | None):
    """Return a pre-loaded Daily Gunsmoke stat-cell OCR engine to inject via
    parse(..., stat_ocr=...), or None to keep today's default (the lazy
    production StatOcr singleton in gfl2.patterns.daily_gunsmoke). This is
    the only place in the codebase that picks a concrete engine class —
    gfl2/patterns/daily_gunsmoke.py stays engine-agnostic (see its stat_ocr
    parameter docs) and just consumes whatever is injected here.
    """
    if engine == "production" and tmpl_variant is None:
        return None  # unchanged default path
    try:
        if engine == "padded":
            from gfl2.stat_ocr_padded import StatOcrPadded as _Engine
        elif engine == "dp":
            from gfl2.stat_ocr_dp import StatOcrDp as _Engine
        else:
            from gfl2.stat_ocr import StatOcr as _Engine
        return _Engine.load(tmpl_variant)
    except (FileNotFoundError, ImportError) as e:
        print(f"Warning: {e}\nFalling back to default stat-cell OCR engine.",
              file=sys.stderr)
        return None


def _process_weekly(image_path: Path, args) -> None:
    image    = cv2.imread(str(image_path))
    score_fn = _get_score_fn(args.score_pipeline)
    parse_fn = PATTERNS["weekly_gunsmoke"]
    records  = parse_fn(image, score_fn=score_fn, source_name=image_path.stem)
    lines    = [GunsmokRecord.csv_header()] + [r.to_csv_row() for r in records]
    out      = Path(args.output) if args.output else _default_weekly_output(image_path)
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
        out     = _default_weekly_output(img_path)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  {img_path.name}  →  {out.name}  ({len(records)} rows)")


def _process_daily_single(image_path: Path, args) -> None:
    image = cv2.imread(str(image_path))
    stat_engine = _get_stat_ocr_engine(args.stat_ocr_engine, args.stat_templates)
    timer = TimerStack()
    with timer.timed(image_path.stem):
        entries = PATTERNS["daily_gunsmoke"](image, filename=image_path.stem, timer=timer,
                                              stat_ocr=stat_engine,
                                              tess_fallback=args.stat_tess_fallback)
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
    stat_engine = _get_stat_ocr_engine(args.stat_ocr_engine, args.stat_templates)
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
            entries = PATTERNS["daily_gunsmoke"](image, filename=img_path.stem, timer=timer,
                                                  stat_ocr=stat_engine,
                                                  tess_fallback=args.stat_tess_fallback)
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
    parser.add_argument("--stat-ocr-engine", default="production",
                        choices=STAT_OCR_ENGINES, dest="stat_ocr_engine",
                        help="Daily Gunsmoke stat-cell OCR engine [default: production]")
    parser.add_argument("--stat-templates", default=None, dest="stat_templates", metavar="VARIANT",
                        help="Template variant name to load for BOTH pct and val "
                             "(e.g. 'padded' -> stat_pct_padded.py/stat_val_padded.py). "
                             "Default: the selected engine's own built-in templates.")
    parser.add_argument("--stat-tess-fallback", action=argparse.BooleanOptionalAction,
                        default=False, dest="stat_tess_fallback",
                        help="Run the Tesseract psm6/psm4 fallback when a stat-cell "
                             "engine leaves pct/val as None [default: off]. Off by "
                             "default because engines with an unimplemented val-line "
                             "(e.g. --stat-ocr-engine dp) leave val as None on EVERY "
                             "cell, which would otherwise force a ~300ms Tesseract "
                             "call per cell unconditionally rather than only on a "
                             "genuine blob-classifier miss.")
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
          f"Buff: {args.buff_pipeline}  Stat: {args.stat_ocr_engine}", file=sys.stderr)

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
