#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
debugs/stat_ocr_bench.py -- head-to-head accuracy + timing comparison between
the production stat_ocr pipeline (gfl2/stat_ocr.py, direct-stretch normalize)
and the padded-normalize pipeline (gfl2/stat_ocr_padded.py), for
docs/known_issues.txt §15.

The two pipelines already train against separate template files
(assets/fonts/stat_pct.py + stat_val.py vs stat_pct_padded.py +
stat_val_padded.py), so they can run side by side with no interference.
Cell crops + Tesseract ground truth are collected ONCE (the slow step) and
reused for both engines, so the actual head-to-head (blob classification
only) runs in seconds even across the full corpus.

Usage:
    python debugs/stat_ocr_bench.py [--images <glob>]
"""
from __future__ import annotations
import argparse
import glob as _glob
import json
import sys
import time
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _collect_cells, StatOcr
from gfl2.stat_ocr_padded import StatOcrPadded


def _apply_overrides(samples: list[dict]) -> int:
    gt_file = _ROOT / "tests" / "inputs" / "daily" / "stat_gt_overrides.json"
    if not gt_file.exists():
        return 0
    overrides = json.loads(gt_file.read_text(encoding="utf-8"))
    n = 0
    for item in samples:
        ov = overrides.get(item["source"])
        if ov:
            if "pct" in ov:
                item["pct"] = ov["pct"]
            if "val" in ov:
                item["val"] = ov["val"]
            n += 1
    return n


def _bench(engine, samples: list[dict], name: str) -> dict:
    pct_total = pct_match = val_total = val_match = 0
    t_total = 0.0
    for item in samples:
        t0 = time.perf_counter()
        pct, val = engine.read(item["cell"])
        t_total += time.perf_counter() - t0
        if item["pct"]:
            pct_total += 1
            if pct == item["pct"]:
                pct_match += 1
        if item["val"]:
            val_total += 1
            if val == item["val"]:
                val_match += 1
    return {
        "name": name, "n_cells": len(samples),
        "pct_match": pct_match, "pct_total": pct_total,
        "val_match": val_match, "val_total": val_total,
        "total_s": t_total,
        "avg_ms": 1000 * t_total / len(samples) if samples else 0.0,
    }


def _print_result(r: dict) -> None:
    def pct_str(n, d):
        return f"{100 * n / d:.2f}%" if d else "n/a"
    print(f"\n{r['name']}")
    print(f"  pct  {r['pct_match']}/{r['pct_total']}  ({pct_str(r['pct_match'], r['pct_total'])})")
    print(f"  val  {r['val_match']}/{r['val_total']}  ({pct_str(r['val_match'], r['val_total'])})")
    print(f"  classify time: {r['total_s']:.3f}s total, {r['avg_ms']:.4f}ms/cell avg  "
          f"({r['n_cells']} cells)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Head-to-head stat_ocr pipeline benchmark")
    parser.add_argument("--images", default="single/*.png",
                        help="Glob of images to use  [default: single/*.png]")
    args = parser.parse_args()

    run_start = datetime.now().isoformat(timespec="seconds")
    print(f"Generated: {run_start}  (run start)")

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                         if "debug" not in Path(p).stem)
    print(f"Images: {len(image_paths)}")

    print("Collecting cells + Tesseract ground truth (one pass, shared by both engines)...")
    t0 = time.perf_counter()
    samples = _collect_cells(image_paths, tess_only=True)
    print(f"  {len(samples)} cells collected  ({time.perf_counter() - t0:.1f}s)")

    n_applied = _apply_overrides(samples)
    if n_applied:
        print(f"  Applied {n_applied} GT override(s) from stat_gt_overrides.json")

    prod = StatOcr.load()
    padded = StatOcrPadded.load()

    r_prod = _bench(prod, samples, "PRODUCTION (direct-stretch, gfl2/stat_ocr.py)")
    r_padded = _bench(padded, samples, "PADDED (aspect-preserving, gfl2/stat_ocr_padded.py)")

    print(f"\n{'=' * 70}")
    print(f"HEAD-TO-HEAD  ({len(samples)} cells, {len(image_paths)} images)")
    print(f"{'=' * 70}")
    _print_result(r_prod)
    _print_result(r_padded)


if __name__ == "__main__":
    main()
