#!/usr/bin/env python3
"""
gfl2/score_ocr.py  —  Blob/Hu-moment score-OCR engine for Weekly Gunsmoke.

Production pipeline consumed by make_score_fn() and weekly_gunsmoke.parse().
For benchmarking against Tesseract, see score_detect.py.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import cv2
import numpy as np

TEMPLATES_F = Path(__file__).parent.parent / "assets" / "fonts" / "score_digits.json"

# ── Blob detection parameters ─────────────────────────────────────────────────
THRESH_VAL    = 150    # THRESH_BINARY_INV threshold
MIN_X_DIGIT   = 30    # skip blobs left of this (coin icon)
DIGIT_MIN_W   = 5
DIGIT_MAX_W   = 60
DIGIT_MIN_H   = 15
DIGIT_MAX_H   = 100
NORM_W        = 20    # normalised digit width for feature computation
NORM_H        = 30    # normalised digit height
HU_THRESHOLD  = 0.25  # max Hu chi-square distance to accept a match
PROJ_CORR_MIN = 0.75  # min projection correlation to accept


# ── Feature helpers ───────────────────────────────────────────────────────────

def _isolate_digits(crop: np.ndarray) -> list[tuple[int, np.ndarray]]:
    """Return (x_position, normalised_crop) pairs sorted left-to-right."""
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
    m  = cv2.moments(norm)
    hu = cv2.HuMoments(m).flatten()
    eps = 1e-10
    return [-np.sign(v) * np.log10(abs(v) + eps) for v in hu]


def _v_projection(norm: np.ndarray) -> list[float]:
    """1D vertical projection: average pixel value per column, normalised 0–1."""
    proj = norm.mean(axis=0).tolist()
    mx   = max(proj) or 1.0
    return [v / mx for v in proj]


def _features(norm: np.ndarray) -> tuple[list[float], list[float]]:
    return _hu_moments(norm), _v_projection(norm)


def _hu_distance(a: list[float], b: list[float]) -> float:
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def _proj_correlation(a: list[float], b: list[float]) -> float:
    a_, b_ = np.array(a), np.array(b)
    if a_.std() < 1e-6 or b_.std() < 1e-6:
        return 0.0
    return float(np.corrcoef(a_, b_)[0, 1])


# ── Template library ──────────────────────────────────────────────────────────

def build_templates(score_set: list[dict]) -> dict:
    """
    Build per-digit feature library from labelled score crops.
    Returns: {digit_char: {"hu": [...], "proj": [...], "n": int}}
    """
    buckets: dict[str, list[tuple[list, list]]] = {str(d): [] for d in range(10)}
    for entry in score_set:
        crop = cv2.imread(entry["path"])
        if crop is None:
            continue
        expected = entry["expected"]
        blobs    = _isolate_digits(crop)
        if len(blobs) != len(expected):
            continue
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


# ── Blob/Hu detection ─────────────────────────────────────────────────────────

def detect_blob(crop: np.ndarray, templates: dict) -> str | None:
    blobs = _isolate_digits(crop)
    if not blobs:
        return None
    result = []
    for x, norm in blobs:
        hu, proj = _features(norm)

        # Pass 1: projection correlation (primary)
        proj_scores     = {d: _proj_correlation(proj, t["proj"]) for d, t in templates.items()}
        best_proj_digit = max(proj_scores, key=proj_scores.get)
        best_proj_corr  = proj_scores[best_proj_digit]
        if best_proj_corr >= PROJ_CORR_MIN:
            result.append(best_proj_digit)
            continue

        # Pass 2: Hu moment distance (fallback)
        best_digit, best_dist = "?", float("inf")
        for digit, tmpl in templates.items():
            d = _hu_distance(hu, tmpl["hu"])
            if d < best_dist:
                best_dist, best_digit = d, digit
        result.append(best_digit if best_dist <= HU_THRESHOLD else "?")

    score = "".join(result)
    return score if "?" not in score else None


# ── Public factory ────────────────────────────────────────────────────────────

def make_score_fn(templates_path: str | None = None):
    """
    Return a (Row) -> str | None callable for use as score_fn= in
    weekly_gunsmoke.parse().  Tesseract-free.

    templates_path: override path to score templates
                    (default: assets/fonts/score_digits.json)
    """
    tp = Path(templates_path) if templates_path else TEMPLATES_F
    if not tp.exists():
        raise FileNotFoundError(
            f"Digit templates not found: {tp}\n"
            "Run: python debugs/score_detect.py --build"
        )
    templates = json.loads(tp.read_text())

    def _score_fn(row) -> str | None:
        cell = row.crop("score")
        if cell is None:
            return None
        return detect_blob(cell, templates)

    _score_fn.__doc__ = f"Blob/Hu score extractor (templates: {tp})"
    return _score_fn
