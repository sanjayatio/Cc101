# -*- coding: utf-8 -*-
"""
debugs/pct_fft_predict.py — Confidence-gated FFT+Gabor pct-digit classifier.

debug_pct_classify.py deliberately keeps its KNN/rule classifiers out of the
normal path because they always answer, even when wrong (see commit 7ab46b4).
This script closes that gap: nearest-centroid prediction on the same
FFT+Gabor feature vector, gated by a distance-margin confidence threshold.
Below the threshold the digit is honestly reported as '?' instead of guessed
— consistent with the stat_ocr '?' convention (docs/known_issues.txt §14, §15).

Labels for template-building and scoring come from the existing full pipeline
(_collect_cells(tess_only=False), the same "ground truth" convention used by
tests/generate_stat_inputs.py: blob pipeline + Tesseract fallback).

HELD-OUT SPLIT: centroids are built ONLY from
single/*.png images that are NOT in tests/inputs/daily/stat_data.py's CROPS
set; accuracy is reported ONLY on that held-out set (resolved against
single/). This makes the accuracy print a genuine generalization estimate,
not the best-case separability number from train==test. If stat_data.py's
image list changes, this script's split follows automatically.

Usage:
    python debugs/pct_fft_predict.py                       # default split
    python debugs/pct_fft_predict.py --train "single/gm_d_*.png"
    python debugs/pct_fft_predict.py --conf-min 0.10
"""
from __future__ import annotations
import json, sys, time, glob as _glob
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

_HERE = Path(__file__).parent
_ROOT = _HERE.parent
_DAILY = _ROOT / "tests" / "inputs" / "daily"
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_DAILY))

from debug_pct_classify import compute_features  # noqa: E402
from gfl2.stat_ocr_v0_1_0 import (  # noqa: E402
    PCT_STRIP_Y, NORM_W_PCT, NORM_H_PCT, DOT_MAX_DIM,
    _binarize, _find_blobs, _filter_y_outliers, _find_percent_x_start,
    _collect_cells,
)
from gfl2.stat_ocr_v0_1_1 import _normalize_glyph  # noqa: E402
import stat_data  # noqa: E402  (tests/inputs/daily/stat_data.py)

_GT_OVERRIDES_F = _ROOT / "tests" / "inputs" / "daily" / "stat_gt_overrides.json"

CONF_MIN_DEFAULT = 0.15   # (d2 - d1) / d1 margin; below this -> '?'
OUT_PY = _ROOT / "tests" / "inputs" / "daily" / "pct_fft_ground_truth.py"
SINGLE_DIR = _ROOT / "single"


def held_out_image_paths() -> list[Path]:
    """Images in tests/inputs/daily/stat_data.py's CROPS, resolved against single/."""
    return sorted(
        p for p in (SINGLE_DIR / name for name in stat_data.CROPS) if p.exists()
    )


# ── Glyph extraction (mirrors debug_pct_classify.collect_glyphs, per-cell) ────

def _extract_pct_digit_glyphs(cell: np.ndarray, pct_label: str):
    """
    Return [(norm_bin_12x20, digit_char), ...] for each digit in pct_label,
    or None if the blob count doesn't match the label (extraction unreliable
    for this cell — skipped rather than guessed at).
    """
    if not pct_label:
        return None
    expected = [c for c in pct_label if c.isdigit()]
    if not expected:
        return None

    ch = cell.shape[0]
    pct_strip = cell[: int(ch * PCT_STRIP_Y[1]), :]
    thresh = _binarize(pct_strip)
    blobs = _filter_y_outliers(_find_blobs(thresh), threshold=12)
    if not blobs:
        return None

    sorted_x = sorted(blobs, key=lambda b: b[0])
    pct_x = _find_percent_x_start(sorted_x)
    digit_blobs = [
        (x, y, w, h) for (x, y, w, h) in sorted_x
        if (pct_x is None or x < pct_x)
        and not (w <= DOT_MAX_DIM and h <= DOT_MAX_DIM)
    ]
    if len(digit_blobs) != len(expected):
        return None

    glyphs = []
    for (x, y, w, h), label in zip(digit_blobs, expected):
        crop = thresh[y: y + h, x: x + w]
        if crop.size == 0:
            return None
        # Aspect-preserving pad instead of direct stretch (§15) — see
        # debug_pct_classify.py's collect_glyphs for the same change + rationale.
        norm = _normalize_glyph(crop, NORM_W_PCT, NORM_H_PCT)
        glyphs.append((norm, label))
    return glyphs


# ── Confidence-gated nearest centroid ─────────────────────────────────────────

def build_centroids(samples: list[tuple[np.ndarray, str]]) -> dict[str, np.ndarray]:
    buckets: dict[str, list] = defaultdict(list)
    for feat, label in samples:
        buckets[label].append(feat)
    return {d: np.mean(v, axis=0) for d, v in buckets.items()}


def classify_confident(feat: np.ndarray, centroids: dict[str, np.ndarray],
                        conf_min: float) -> tuple[str, float]:
    """
    Nearest-centroid by L2 distance, gated by the relative margin to the
    second-nearest centroid: margin = (d2 - d1) / d1.  A small margin means
    the glyph sits ambiguously between two digit classes — report '?' rather
    than the coin-flip winner.
    """
    dists = sorted(
        (float(np.linalg.norm(feat - c)), d) for d, c in centroids.items()
    )
    d1, best = dists[0]
    if len(dists) == 1:
        return best, 1.0
    d2, _ = dists[1]
    margin = (d2 - d1) / d1 if d1 > 1e-9 else 1.0
    if margin < conf_min:
        return '?', margin
    return best, margin


def substitute_prediction(pct_label: str, preds: list[str]) -> str:
    """Rebuild the pct string with each digit replaced by its prediction
    (possibly '?'); non-digit characters ('.') pass through unchanged."""
    it = iter(preds)
    return ''.join(next(it) if c.isdigit() else c for c in pct_label)


# ── Ground-truth writer ───────────────────────────────────────────────────────

def _write_ground_truth(ground_truth: dict, conf_min: float, n_train_images: int,
                         run_start: str) -> None:
    OUT_PY.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '# -*- coding: utf-8 -*-',
        '"""',
        'pct_fft_ground_truth.py -- auto-generated by debugs/pct_fft_predict.py',
        '',
        f'Generated: {run_start}  (run start)',
        '',
        'Living document, not a final oracle: FFT+Gabor nearest-centroid',
        'predictions for every pct cell in the held-out image set (the images',
        'listed in tests/inputs/daily/stat_data.py), gated by a distance-margin',
        "confidence threshold.  '?' marks digits the classifier was not",
        'confident enough to call -- honesty over false precision (see',
        'docs/known_issues.txt Sec14, Sec15).  "label" is the existing',
        'full-pipeline (blob + Tesseract fallback) result, used as the working',
        'reference until spot-checked by a human.',
        '',
        f'Centroids were built from {n_train_images} single/*.png training images,',
        'ALL of which exclude the held-out set below -- this is a genuine',
        'generalization estimate, not train==test separability.',
        '',
        'Regenerate: python debugs/pct_fft_predict.py',
        '"""',
        '',
        f'CONF_MIN = {conf_min!r}',
        '',
        'DATA = {',
    ]
    for source in sorted(ground_truth):
        entry = ground_truth[source]
        lines.append(f'    {source!r}: {{')
        lines.append(f'        "label": {entry["label"]!r},')
        lines.append(f'        "predicted": {entry["predicted"]!r},')
        lines.append(f'        "confidences": {entry["confidences"]!r},')
        lines.append('    },')
    lines.append('}')
    OUT_PY.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"\nWrote ground truth: {OUT_PY}  ({len(ground_truth)} cells)")


# ── Entry point ───────────────────────────────────────────────────────────────

def _apply_gt_overrides(cells: list[dict]) -> int:
    """Correct known-wrong Tesseract labels (docs/known_issues.txt §15) in
    place, keyed by each item's "source" field.  Mirrors gfl2/stat_ocr_v0_1_0.py's
    build_templates() so this FFT eval isn't fooled by the same mislabels."""
    if not _GT_OVERRIDES_F.exists():
        return 0
    overrides = json.loads(_GT_OVERRIDES_F.read_text(encoding="utf-8"))
    n_applied = 0
    for item in cells:
        ov = overrides.get(item.get("source"))
        if ov:
            if "pct" in ov: item["pct"] = ov["pct"]
            if "val" in ov: item["val"] = ov["val"]
            n_applied += 1
    return n_applied


def _extract_samples(cells: list[dict]) -> tuple[dict[str, list], list]:
    """Extract glyphs + FFT+Gabor features for every cell whose blob count
    matches its label's digit count.  Returns (per_cell_feats, all_samples)."""
    per_cell_feats: dict[str, list[tuple[np.ndarray, str]]] = {}
    all_samples: list[tuple[np.ndarray, str]] = []
    for item in cells:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item["pct"])
        if glyphs is None:
            continue
        feats = [(compute_features(norm), label) for norm, label in glyphs]
        per_cell_feats[item["source"]] = feats
        all_samples.extend(feats)
    return per_cell_feats, all_samples


def main(argv=None):
    import argparse
    run_start = datetime.now().isoformat(timespec="seconds")
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--train", default="single/*.png",
                     help="Training image path/glob  [default: single/*.png]. "
                          "Images also present in tests/inputs/daily/stat_data.py "
                          "are always excluded from training, regardless of this glob.")
    ap.add_argument("--conf-min", type=float, default=CONF_MIN_DEFAULT,
                     help=f"Minimum confidence margin to answer  [default: {CONF_MIN_DEFAULT}]")
    args = ap.parse_args(argv)

    held_out_paths = held_out_image_paths()
    if not held_out_paths:
        sys.exit(f"No held-out images found in single/ for {_DAILY / 'stat_data.py'} "
                  f"({len(stat_data.CROPS)} entries) -- regenerate it with "
                  f"tests/generate_stat_inputs.py first.")
    held_out_names = {p.name for p in held_out_paths}

    matched = _glob.glob(str(_ROOT / args.train)) or _glob.glob(args.train)
    train_paths = sorted({
        p for p in (Path(m) for m in matched)
        if p.suffix.lower() == ".png" and p.name not in held_out_names
    })
    if not train_paths:
        sys.exit(f"No training images matched (after excluding the held-out set): {args.train}")

    print(f"Generated: {run_start}  (run start)")
    print(f"Training pool  : {len(train_paths)} image(s)  (excludes {len(held_out_names)} held-out)")
    print(f"Held-out eval  : {len(held_out_paths)} image(s)  (tests/inputs/daily/stat_data.py)")

    t0 = time.perf_counter()
    train_cells = _collect_cells(train_paths, tess_only=False)
    holdout_cells = _collect_cells(held_out_paths, tess_only=False)
    t_collect = time.perf_counter() - t0
    print(f"  {len(train_cells)} train cells, {len(holdout_cells)} held-out cells  ({t_collect:.2f}s)")

    n_ov = _apply_gt_overrides(train_cells) + _apply_gt_overrides(holdout_cells)
    if n_ov:
        print(f"  Applied {n_ov} GT override(s) from stat_gt_overrides.json")

    t0 = time.perf_counter()
    _, train_samples = _extract_samples(train_cells)
    holdout_feats, holdout_samples = _extract_samples(holdout_cells)
    t_feat = time.perf_counter() - t0

    if not train_samples:
        sys.exit("No training glyphs extracted -- check pipeline / training image set.")
    if not holdout_samples:
        sys.exit("No held-out glyphs extracted -- check pipeline / stat_data.py image set.")

    n_glyphs = len(train_samples) + len(holdout_samples)
    print(f"  {len(train_samples)} training glyphs, {len(holdout_samples)} held-out glyphs  "
          f"(feature extraction {t_feat:.2f}s, {t_feat / n_glyphs * 1e6:.1f} us/glyph)")

    centroids = build_centroids(train_samples)
    print(f"  Centroids built for digits: {sorted(centroids)}  (training set only)")

    # Classify held-out glyphs only, honestly reporting low-confidence as '?'.
    ground_truth: dict[str, dict] = {}
    n_digits = n_correct = n_unsure = 0
    confusion: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    t0 = time.perf_counter()
    for item in holdout_cells:
        feats = holdout_feats.get(item["source"])
        if feats is None:
            continue
        preds, confs = [], []
        for feat, label in feats:
            pred, conf = classify_confident(feat, centroids, args.conf_min)
            preds.append(pred)
            confs.append(round(conf, 3))
            n_digits += 1
            confusion[label][pred] += 1
            if pred == '?':
                n_unsure += 1
            elif pred == label:
                n_correct += 1
        ground_truth[item["source"]] = {
            "label":       item["pct"],
            "predicted":   substitute_prediction(item["pct"], preds),
            "confidences": confs,
        }
    t_clf = time.perf_counter() - t0

    n_answered = n_digits - n_unsure
    print()
    print("-- Results (held-out: centroids never saw these images) --")
    print(f"  digits classified   : {n_digits}")
    if n_digits:
        print(f"  answered            : {n_answered}  ({n_answered / n_digits * 100:.1f}%)")
        print(f"  flagged '?'         : {n_unsure}  ({n_unsure / n_digits * 100:.1f}%)")
    if n_answered:
        print(f"  accuracy on answered: {n_correct}/{n_answered}  "
              f"({n_correct / n_answered * 100:.1f}%)")
    print()
    print("-- Per-digit accuracy (true label -> predicted) -------------------")
    for d in sorted(confusion):
        row = confusion[d]
        total = sum(row.values())
        correct = row.get(d, 0)
        misreads = ", ".join(f"{p}:{c}" for p, c in sorted(row.items())
                              if p != d and c)
        print(f"  '{d}': {correct}/{total} correct"
              + (f"   misread as {{{misreads}}}" if misreads else ""))
    print()
    print("-- Timing --------------------------------------------------------")
    n_cells = len(train_cells) + len(holdout_cells)
    print(f"  cell collection      : {t_collect:.2f}s  ({t_collect / max(1, n_cells) * 1e3:.2f} ms/cell)")
    print(f"  feature extraction   : {t_feat:.2f}s  ({t_feat / n_glyphs * 1e6:.1f} us/glyph)")
    print(f"  classification       : {t_clf:.3f}s  ({t_clf / max(1, n_digits) * 1e6:.1f} us/glyph)")
    print(f"  total wall time      : {t_collect + t_feat + t_clf:.2f}s")

    _write_ground_truth(ground_truth, args.conf_min, len(train_paths), run_start)


if __name__ == "__main__":
    main()
