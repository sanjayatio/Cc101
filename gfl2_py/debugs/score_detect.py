#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
score_detect.py  --  Score-OCR benchmark: Tesseract vs. blob/Hu-moment pipeline.

The blob/Hu pipeline itself lives in gfl2/score_ocr.py and is used in
production via make_score_fn().  This script exists only for benchmarking
and for rebuilding digit templates.

Usage:
    python score_detect.py              # run both pipelines on the score set
    python score_detect.py --build      # (re)build digit template library only

Outputs:
    tests/inputs/score/report_tesseract.txt      # Tesseract benchmark log
    tests/inputs/score/report_blob.txt           # Blob pipeline benchmark log
    tests/inputs/score/report_summary.txt        # Side-by-side comparison
    tests/inputs/score/digit_templates.json      # Serialised digit feature library
"""
from __future__ import annotations
import sys, json, time, argparse
sys.dont_write_bytecode = True

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # project root
import cv2
import numpy as np
import pytesseract
import shutil

# ── Tesseract path (Windows) ──────────────────────────────────────────────────
if not shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from gfl2.score_ocr import (
    SCORE_SET_DIR, TEMPLATES_F,
    build_templates, detect_blob,
)

MANIFEST = SCORE_SET_DIR / "manifest.json"


# ── Pipeline A: Tesseract (benchmark only) ────────────────────────────────────

def detect_tesseract(crop: np.ndarray) -> str | None:
    up   = cv2.resize(crop, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    text = pytesseract.image_to_string(up, config="--psm 6").strip()
    import re
    nums = re.findall(r"\d+", text)
    if nums:
        return nums[-1]
    data = pytesseract.image_to_data(
        up,
        config="--psm 6 -c tessedit_char_whitelist=0123456789",
        output_type=pytesseract.Output.DICT,
    )
    candidates = [
        (data["left"][i], data["text"][i])
        for i in range(len(data["text"]))
        if re.fullmatch(r"\d{3,6}", data["text"][i])
        and int(data["conf"][i]) > 20
        and data["left"][i] > 0
    ]
    return max(candidates, key=lambda t: t[0])[1] if candidates else None


# ── Benchmarking ──────────────────────────────────────────────────────────────

def _benchmark(score_set: list[dict], detect_fn, label: str) -> list[dict]:
    results = []
    for entry in score_set:
        crop = cv2.imread(entry["path"])
        if crop is None:
            results.append({**entry, "detected": None, "correct": False, "elapsed": 0.0})
            continue
        t0       = time.perf_counter()
        detected = detect_fn(crop)
        elapsed  = time.perf_counter() - t0
        correct  = (detected == entry["expected"])
        results.append({**entry, "detected": detected, "correct": correct, "elapsed": elapsed})
    return results


def _write_report(results: list[dict], path: Path, label: str) -> None:
    correct = sum(1 for r in results if r["correct"])
    total   = len(results)
    lines   = [
        f"Pipeline: {label}",
        f"Accuracy: {correct}/{total}  ({100*correct/total:.1f}%)",
        f"Avg time: {sum(r['elapsed'] for r in results)/total*1000:.1f} ms/crop",
        "",
        f"{'Key':<22} {'Expected':<10} {'Detected':<10} {'OK':<4} {'ms':>6}",
        "-" * 58,
    ]
    for r in results:
        ok = "✓" if r["correct"] else "✗"
        ms = f"{r['elapsed']*1000:.1f}"
        lines.append(f"{r['key']:<22} {r['expected']:<10} {str(r['detected']):<10} {ok:<4} {ms:>6}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  → {path.name}: {correct}/{total} correct")


def _write_summary(r_tess: list[dict], r_blob: list[dict]) -> None:
    path      = SCORE_SET_DIR / "report_summary.txt"
    correct_t = sum(1 for r in r_tess if r["correct"])
    correct_b = sum(1 for r in r_blob if r["correct"])
    total     = len(r_tess)
    lines = [
        "Score Detection Pipeline Comparison",
        "=" * 58,
        f"{'Metric':<30} {'Tesseract':>12} {'Blob/Hu':>12}",
        "-" * 58,
        f"{'Accuracy':<30} {correct_t}/{total:>10} {correct_b}/{total:>10}",
        f"{'Accuracy %':<30} {100*correct_t/total:>11.1f}% {100*correct_b/total:>11.1f}%",
        f"{'Avg ms/crop':<30} {sum(r['elapsed'] for r in r_tess)/total*1000:>11.1f}  {sum(r['elapsed'] for r in r_blob)/total*1000:>11.1f}",
        "",
        f"{'Key':<22} {'Exp':<7} {'Tess':<8} {'Blob':<8} {'T?':<3} {'B?'}",
        "-" * 58,
    ]
    for rt, rb in zip(r_tess, r_blob):
        ot = "✓" if rt["correct"] else "✗"
        ob = "✓" if rb["correct"] else "✗"
        lines.append(f"{rt['key']:<22} {rt['expected']:<7} {str(rt['detected']):<8} {str(rb['detected']):<8} {ot:<3} {ob}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  → {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Score detection benchmark")
    parser.add_argument("--build", action="store_true", help="Rebuild templates only")
    args = parser.parse_args()

    score_set = json.loads(MANIFEST.read_text())
    manifest_dir = MANIFEST.parent
    for entry in score_set:
        entry["path"] = str(manifest_dir / entry["path"])
    print(f"Score set: {len(score_set)} crops\n")

    if args.build or not TEMPLATES_F.exists():
        print("Building digit templates...")
        templates = build_templates(score_set)
        TEMPLATES_F.write_text(json.dumps(templates, indent=2))
        print()
    else:
        templates = json.loads(TEMPLATES_F.read_text())
        print(f"Loaded templates for digits: {sorted(templates.keys())}\n")

    if args.build:
        return

    print("Running Pipeline A: Tesseract...")
    r_tess = _benchmark(score_set, detect_tesseract, "Tesseract")
    _write_report(r_tess, SCORE_SET_DIR / "report_tesseract.txt", "Tesseract")

    print("\nRunning Pipeline B: Blob / Hu moment...")
    r_blob = _benchmark(score_set, lambda c: detect_blob(c, templates), "Blob/Hu")
    _write_report(r_blob, SCORE_SET_DIR / "report_blob.txt", "Blob/Hu moment")

    print("\nWriting summary...")
    _write_summary(r_tess, r_blob)
    print("\nDone. Results in tests/inputs/score/")


if __name__ == "__main__":
    main()
