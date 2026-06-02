#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
score_detect.py  --  Score-OCR benchmark: Tesseract vs. blob/Hu-moment pipeline.

Usage:
    python score_detect.py              # run both pipelines on the score set
    python score_detect.py --build      # (re)build digit template library only

Outputs:
    score_set/report_tesseract.txt      # Tesseract benchmark log
    score_set/report_blob.txt           # Blob pipeline benchmark log
    score_set/report_summary.txt        # Side-by-side comparison
    score_set/digit_templates.json      # Serialised digit feature library
"""
from __future__ import annotations
import sys, json, time, argparse
sys.dont_write_bytecode = True

from pathlib import Path
import cv2
import numpy as np
import pytesseract
import shutil

# ── Tesseract path (Windows) ──────────────────────────────────────────────────
if not shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

SCORE_SET_DIR = Path(__file__).parent / "score_set"
MANIFEST      = SCORE_SET_DIR / "manifest.json"
TEMPLATES_F   = SCORE_SET_DIR / "digit_templates.json"

# ── Blob detection parameters ─────────────────────────────────────────────────
THRESH_VAL    = 150    # THRESH_BINARY_INV threshold
MIN_X_DIGIT   = 30    # skip blobs left of this (coin icon)
DIGIT_MIN_W   = 5
DIGIT_MAX_W   = 60
DIGIT_MIN_H   = 15
DIGIT_MAX_H   = 100
NORM_W        = 20    # normalised digit width for feature computation
NORM_H        = 30    # normalised digit height
HU_THRESHOLD  = 0.25  # max Hu-chi-square distance to accept a match
PROJ_CORR_MIN  = 0.75  # min projection correlation to accept


# ─────────────────────────────────────────────────────────────────────────────
# Blob / feature helpers
# ─────────────────────────────────────────────────────────────────────────────

def _isolate_digits(crop: np.ndarray) -> list[tuple[int, np.ndarray]]:
    """
    Return list of (x_position, normalised_digit_crop) sorted left-to-right.
    Uses inverse binary threshold to find dark digits on light background.
    """
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop
    _, thresh = cv2.threshold(gray, THRESH_VAL, 255, cv2.THRESH_BINARY_INV)
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if x < MIN_X_DIGIT:
            continue
        if not (DIGIT_MIN_W <= w <= DIGIT_MAX_W and DIGIT_MIN_H <= h <= DIGIT_MAX_H):
            continue
        digit_crop = thresh[y:y+h, x:x+w]
        norm       = cv2.resize(digit_crop, (NORM_W, NORM_H), interpolation=cv2.INTER_AREA)
        blobs.append((x, norm))
    blobs.sort(key=lambda b: b[0])
    return blobs


def _hu_moments(norm: np.ndarray) -> list[float]:
    """Compute 7 Hu moments (log-scaled) from a normalised digit crop."""
    m   = cv2.moments(norm)
    hu  = cv2.HuMoments(m).flatten()
    # Log-scale (standard Hu moment normalisation)
    eps = 1e-10
    return [-np.sign(v) * np.log10(abs(v) + eps) for v in hu]


def _v_projection(norm: np.ndarray) -> list[float]:
    """1D vertical projection: average pixel value per column, normalised 0-1."""
    proj = norm.mean(axis=0).tolist()
    mx   = max(proj) or 1.0
    return [v / mx for v in proj]


def _features(norm: np.ndarray) -> tuple[list[float], list[float]]:
    return _hu_moments(norm), _v_projection(norm)


def _hu_distance(a: list[float], b: list[float]) -> float:
    """Chi-square-like distance between two Hu moment vectors."""
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def _proj_correlation(a: list[float], b: list[float]) -> float:
    """Pearson correlation between two 1D projections."""
    a_, b_ = np.array(a), np.array(b)
    if a_.std() < 1e-6 or b_.std() < 1e-6:
        return 0.0
    return float(np.corrcoef(a_, b_)[0, 1])


# ─────────────────────────────────────────────────────────────────────────────
# Template library
# ─────────────────────────────────────────────────────────────────────────────

def build_templates(score_set: list[dict]) -> dict:
    """
    Extract individual digit blobs from known-score crops and build a
    per-digit feature library (averaged Hu moments + 1D projection).
    Returns: {digit_char: {"hu": [...], "proj": [...]}}
    """
    buckets: dict[str, list[tuple[list, list]]] = {str(d): [] for d in range(10)}

    for entry in score_set:
        crop = cv2.imread(entry["path"])
        if crop is None:
            continue
        expected = entry["expected"]
        blobs    = _isolate_digits(crop)
        if len(blobs) != len(expected):
            continue   # can't safely assign digit labels
        for (x, norm), digit_char in zip(blobs, expected):
            hu, proj = _features(norm)
            buckets[digit_char].append((hu, proj))

    templates: dict[str, dict] = {}
    for digit, samples in buckets.items():
        if not samples:
            print(f"  WARNING: no samples for digit '{digit}'", file=sys.stderr)
            continue
        avg_hu   = [sum(s[0][i] for s in samples) / len(samples) for i in range(7)]
        avg_proj = [sum(s[1][i] for s in samples) / len(samples) for i in range(NORM_W)]
        templates[digit] = {"hu": avg_hu, "proj": avg_proj, "n": len(samples)}

    print(f"Templates built from {sum(len(v) for v in buckets.values())} blobs:")
    for d in sorted(templates):
        print(f"  digit '{d}': {templates[d]['n']} samples")
    return templates


def load_or_build_templates(score_set: list[dict]) -> dict:
    if TEMPLATES_F.exists():
        return json.loads(TEMPLATES_F.read_text())
    templates = build_templates(score_set)
    TEMPLATES_F.write_text(json.dumps(templates, indent=2))
    return templates


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline A: Tesseract
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline B: Blob / Hu moment
# ─────────────────────────────────────────────────────────────────────────────

def detect_blob(crop: np.ndarray, templates: dict) -> str | None:
    blobs = _isolate_digits(crop)
    if not blobs:
        return None
    result = []
    for x, norm in blobs:
        hu, proj = _features(norm)

        # Pass 1: 1D projection correlation — primary signal.
        # Projection captures the per-column density profile, which is
        # highly distinctive (0.99 for correct digit vs <0.90 for others).
        proj_scores = {d: _proj_correlation(proj, t["proj"]) for d, t in templates.items()}
        best_proj_digit = max(proj_scores, key=proj_scores.get)
        best_proj_corr  = proj_scores[best_proj_digit]

        if best_proj_corr >= PROJ_CORR_MIN:
            result.append(best_proj_digit)
            continue

        # Pass 2: Hu moment distance — fallback when projection is ambiguous.
        best_digit, best_dist = "?", float("inf")
        for digit, tmpl in templates.items():
            d = _hu_distance(hu, tmpl["hu"])
            if d < best_dist:
                best_dist, best_digit = d, digit
        if best_dist <= HU_THRESHOLD:
            result.append(best_digit)
        else:
            result.append("?")  # unconfident in both

    score = "".join(result)
    return score if "?" not in score else None


# ─────────────────────────────────────────────────────────────────────────────
# Benchmarking
# ─────────────────────────────────────────────────────────────────────────────

def _benchmark(score_set: list[dict], detect_fn, label: str) -> list[dict]:
    results = []
    for entry in score_set:
        crop = cv2.imread(entry["path"])
        if crop is None:
            results.append({**entry, "detected": None, "correct": False, "elapsed": 0.0})
            continue
        t0      = time.perf_counter()
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
    path    = SCORE_SET_DIR / "report_summary.txt"
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


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Score detection benchmark")
    parser.add_argument("--build", action="store_true", help="Rebuild templates only")
    args = parser.parse_args()

    score_set = json.loads(MANIFEST.read_text())
    print(f"Score set: {len(score_set)} crops\n")

    # (Re)build templates
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
    print("\nDone. Results in score_set/")



# ─────────────────────────────────────────────────────────────────────────────
# Public factory for integration with weekly_gunsmoke.parse()
# ─────────────────────────────────────────────────────────────────────────────

def make_score_fn(templates_path: str | None = None):
    """
    Return a score-extraction callable with the signature (Row) -> str | None,
    suitable for passing as score_fn to weekly_gunsmoke.parse().

    Uses the Blob/Hu moment pipeline — no Tesseract dependency.

    templates_path: path to digit_templates.json
                    (default: score_set/digit_templates.json alongside this file)
    """
    import json
    from pathlib import Path as _Path

    tp = _Path(templates_path) if templates_path else SCORE_SET_DIR / "digit_templates.json"
    if not tp.exists():
        raise FileNotFoundError(
            f"Digit templates not found: {tp}\n"
            "Run: python score_detect.py --build"
        )
    templates = json.loads(tp.read_text())

    def _score_fn(row) -> str | None:
        cell = row.crop("score")
        if cell is None:
            return None
        return detect_blob(cell, templates)

    _score_fn.__doc__ = f"Blob/Hu score extractor (templates: {tp})"
    return _score_fn


if __name__ == "__main__":
    main()
