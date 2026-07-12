#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
debugs/stat_ocr_pct_bench.py -- three-way PCT-LINE-ONLY head-to-head
comparison across all three stat_ocr engines (production, padded, fft).

WHY A SEPARATE TOOL FROM debugs/stat_ocr_bench.py: that script times
engine.read(cell) as a whole, which is correct for a pct+val comparison
between production and padded -- but gfl2.stat_ocr_fft.py never
implements val (see its module docstring), so a whole-read() timing
number for it isn't measuring the same thing as the other two.  This
tool isolates each engine's PCT-LINE classification specifically (via
each engine's own _read_line(pct_strip, pct_templates, is_pct=True)
call, using each engine's own pct-strip extraction convention), so all
three numbers measure exactly the same unit of work.

Cell crops + Tesseract ground truth are collected ONCE (shared by all
three engines, same as stat_ocr_bench.py), so the actual head-to-head
runs in seconds even across the full corpus.

Usage:
    python debugs/stat_ocr_pct_bench.py [--images <glob>]
"""
from __future__ import annotations
import argparse
import glob as _glob
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _collect_cells, _load_tess_gt_cache, StatOcr, PCT_STRIP_Y
from gfl2.stat_ocr_padded import StatOcrPadded
from gfl2.stat_ocr_fft import StatOcrFft, _pct_strip_bottom


def _apply_overrides(samples: list[dict]) -> int:
    gt_file = _ROOT / "tests" / "inputs" / "daily" / "stat_gt_overrides.json"
    if not gt_file.exists():
        return 0
    overrides = json.loads(gt_file.read_text(encoding="utf-8"))
    n = 0
    for item in samples:
        ov = overrides.get(item["source"])
        if ov and "pct" in ov:
            item["pct"] = ov["pct"]
            n += 1
    return n


def _bench_pct(name: str, samples: list[dict], strip_fn, classify_fn) -> dict:
    """strip_fn(cell) -> pct_strip ; classify_fn(pct_strip) -> pct_str|None."""
    total = correct = miss = wrong = 0
    times = []
    for item in samples:
        if not item["pct"]:
            continue
        total += 1
        strip = strip_fn(item["cell"])
        t0 = time.perf_counter()
        got = classify_fn(strip)
        times.append(time.perf_counter() - t0)
        if got is None:
            miss += 1
        elif got != item["pct"]:
            wrong += 1
        else:
            correct += 1
    mean_us = statistics.mean(times) * 1e6 if times else 0.0
    stdev_us = statistics.pstdev(times) * 1e6 if len(times) > 1 else 0.0
    return {
        "name": name, "total": total, "correct": correct,
        "misclassified": wrong, "unknown": miss,
        "mean_us": mean_us, "stdev_us": stdev_us,
        "cv": (stdev_us / mean_us) if mean_us else 0.0,
    }


def _print_result(r: dict) -> None:
    acc = 100 * r["correct"] / r["total"] if r["total"] else 0.0
    print(f"\n{r['name']}")
    print(f"  pct  {r['correct']}/{r['total']}  ({acc:.2f}%)  "
          f"misclassified={r['misclassified']}  unknown={r['unknown']}")
    print(f"  classify time: mean={r['mean_us']:.1f}us  stdev={r['stdev_us']:.1f}us  "
          f"cv={r['cv']:.2f}  (n={r['total']} cells)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Three-way pct-only stat_ocr engine comparison")
    parser.add_argument("--images", default="single/*.png",
                        help="Glob of images to use  [default: single/*.png]")
    args = parser.parse_args()

    run_start = datetime.now().isoformat(timespec="seconds")
    print(f"Generated: {run_start}  (run start)")

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                         if "debug" not in Path(p).stem)
    print(f"Images: {len(image_paths)}")

    print("Collecting cells + Tesseract ground truth (one pass, shared by all three engines)...")
    t0 = time.perf_counter()
    gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    print(f"  {len(samples)} cells collected  ({time.perf_counter() - t0:.1f}s)"
          f"  [{'using' if gt_cache else 'NO'} Tesseract GT cache]")

    n_applied = _apply_overrides(samples)
    if n_applied:
        print(f"  Applied {n_applied} pct GT override(s) from stat_gt_overrides.json")

    prod = StatOcr.load()
    padded = StatOcrPadded.load()
    fft = StatOcrFft.load()

    r_prod = _bench_pct(
        "PRODUCTION (direct-stretch, gfl2/stat_ocr.py)", samples,
        strip_fn=lambda cell: cell[: int(cell.shape[0] * PCT_STRIP_Y[1]), :],
        classify_fn=lambda strip: prod._read_line(strip, prod._pct, is_pct=True),
    )
    r_padded = _bench_pct(
        "PADDED (aspect-preserving, gfl2/stat_ocr_padded.py)", samples,
        strip_fn=lambda cell: cell[: int(cell.shape[0] * PCT_STRIP_Y[1]), :],
        classify_fn=lambda strip: padded._read_line(strip, padded._pct, is_pct=True),
    )
    r_fft = _bench_pct(
        "FFT+GABOR two-agent (exploratory, gfl2/stat_ocr_fft.py)", samples,
        strip_fn=lambda cell: cell[: _pct_strip_bottom(cell.shape[0]), :],
        classify_fn=lambda strip: fft._read_line(strip, fft._pct, is_pct=True),
    )

    print(f"\n{'=' * 70}")
    print(f"THREE-WAY PCT-ONLY COMPARISON  ({len(samples)} cells, {len(image_paths)} images)")
    print(f"{'=' * 70}")
    for r in (r_prod, r_padded, r_fft):
        _print_result(r)


if __name__ == "__main__":
    main()
