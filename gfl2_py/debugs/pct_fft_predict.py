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
tests/generate_stat_inputs.py: blob pipeline + Tesseract fallback). Centroids
are built from ALL collected glyphs and then applied back to the same glyphs
— this is NOT a held-out evaluation, so the reported accuracy is a best-case
separability check, not a generalization estimate. Good enough for a first
pass; tighten with leave-one-out later if the numbers look promising.

Usage:
    python debugs/pct_fft_predict.py                       # all single/*.png
    python debugs/pct_fft_predict.py "single/gm_d_*.png"
    python debugs/pct_fft_predict.py --conf-min 0.10
"""
from __future__ import annotations
import sys, time, glob as _glob
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

_HERE = Path(__file__).parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_ROOT))

from debug_pct_classify import compute_features  # noqa: E402
from gfl2.stat_ocr import (  # noqa: E402
    PCT_STRIP_Y, NORM_W_PCT, NORM_H_PCT, DOT_MAX_DIM,
    _binarize, _find_blobs, _filter_y_outliers, _find_percent_x_start,
    _collect_cells,
)

CONF_MIN_DEFAULT = 0.15   # (d2 - d1) / d1 margin; below this -> '?'
OUT_PY = _ROOT / "tests" / "inputs" / "daily" / "pct_fft_ground_truth.py"


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
        norm = cv2.resize(crop, (NORM_W_PCT, NORM_H_PCT), interpolation=cv2.INTER_AREA)
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

def _write_ground_truth(ground_truth: dict, conf_min: float) -> None:
    OUT_PY.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '# -*- coding: utf-8 -*-',
        '"""',
        'pct_fft_ground_truth.py -- auto-generated by debugs/pct_fft_predict.py',
        '',
        'Living document, not a final oracle: FFT+Gabor nearest-centroid',
        'predictions for every pct cell in the scanned image set, gated by a',
        "distance-margin confidence threshold.  '?' marks digits the classifier",
        'was not confident enough to call -- honesty over false precision',
        '(see docs/known_issues.txt Sec14, Sec15).  "label" is the existing',
        'full-pipeline (blob + Tesseract fallback) result, used as the working',
        'reference until spot-checked by a human.',
        '',
        'CAVEAT: centroids are built from and applied back to the SAME glyphs',
        '(train==test) -- this is a best-case separability check, not a',
        'generalization estimate.  Building a real held-out eval set is',
        'tracked as docs/action_items.txt #1.',
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

def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="*", default=["single/*.png"],
                     help="Image path(s) or glob(s)  [default: single/*.png]")
    ap.add_argument("--conf-min", type=float, default=CONF_MIN_DEFAULT,
                     help=f"Minimum confidence margin to answer  [default: {CONF_MIN_DEFAULT}]")
    args = ap.parse_args(argv)

    image_paths: list[Path] = []
    for pat in args.images:
        matched = _glob.glob(str(_ROOT / pat)) or _glob.glob(pat)
        image_paths.extend(Path(p) for p in matched)
    image_paths = sorted({p for p in image_paths if p.suffix.lower() == ".png"})
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    print(f"Collecting cells from {len(image_paths)} image(s) ...")
    t0 = time.perf_counter()
    cells = _collect_cells(image_paths, tess_only=False)
    t_collect = time.perf_counter() - t0
    print(f"  {len(cells)} cells  ({t_collect:.2f}s)")

    # Pass 1: extract glyphs + features for every cell whose blob count
    # matches its label's digit count.
    per_cell_feats: dict[str, list[tuple[np.ndarray, str]]] = {}
    all_samples: list[tuple[np.ndarray, str]] = []
    t0 = time.perf_counter()
    for item in cells:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item["pct"])
        if glyphs is None:
            continue
        feats = [(compute_features(norm), label) for norm, label in glyphs]
        per_cell_feats[item["source"]] = feats
        all_samples.extend(feats)
    t_feat = time.perf_counter() - t0

    if not all_samples:
        sys.exit("No glyphs extracted -- check pipeline / image set.")

    print(f"  {len(all_samples)} labeled glyphs across {len(per_cell_feats)} cells  "
          f"(feature extraction {t_feat:.2f}s, "
          f"{t_feat / len(all_samples) * 1e6:.1f} us/glyph)")

    centroids = build_centroids(all_samples)
    print(f"  Centroids built for digits: {sorted(centroids)}")

    # Pass 2: classify every glyph, honestly reporting low-confidence as '?'.
    ground_truth: dict[str, dict] = {}
    n_digits = n_correct = n_unsure = 0
    t0 = time.perf_counter()
    for item in cells:
        feats = per_cell_feats.get(item["source"])
        if feats is None:
            continue
        preds, confs = [], []
        for feat, label in feats:
            pred, conf = classify_confident(feat, centroids, args.conf_min)
            preds.append(pred)
            confs.append(round(conf, 3))
            n_digits += 1
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
    print("-- Results (train==test; best-case separability, not generalization) --")
    print(f"  digits classified   : {n_digits}")
    if n_digits:
        print(f"  answered            : {n_answered}  ({n_answered / n_digits * 100:.1f}%)")
        print(f"  flagged '?'         : {n_unsure}  ({n_unsure / n_digits * 100:.1f}%)")
    if n_answered:
        print(f"  accuracy on answered: {n_correct}/{n_answered}  "
              f"({n_correct / n_answered * 100:.1f}%)")
    print()
    print("-- Timing --------------------------------------------------------")
    print(f"  cell collection      : {t_collect:.2f}s  ({t_collect / max(1, len(cells)) * 1e3:.2f} ms/cell)")
    print(f"  feature extraction   : {t_feat:.2f}s  ({t_feat / len(all_samples) * 1e6:.1f} us/glyph)")
    print(f"  classification       : {t_clf:.3f}s  ({t_clf / max(1, n_digits) * 1e6:.1f} us/glyph)")
    print(f"  total wall time      : {t_collect + t_feat + t_clf:.2f}s")

    _write_ground_truth(ground_truth, args.conf_min)


if __name__ == "__main__":
    main()
