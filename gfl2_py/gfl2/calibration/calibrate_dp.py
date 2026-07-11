# -*- coding: utf-8 -*-
"""
gfl2/calibration/calibrate_dp.py -- derives EVERY re-derivable constant
gfl2/stat_ocr_dp.py's classify() tree uses, from the real corpus, on the
engine's own NATIVE (zero-normalization) glyph representation -- no fixed
canvas size, no padding, no cropping, no resize anywhere.

WHY THIS EXISTS: gfl2/stat_ocr_dp.py originally reused two things from
OTHER modules purely to avoid re-deriving them: NORM_W_PCT/NORM_H_PCT (a
fixed 12x20 canvas, from gfl2.stat_ocr's projection-correlation classifier,
which genuinely needs one) and gfl2/stat_ocr_fft.py's ALREADY-TRAINED
'0'/'6'/'9' paren+loop centroids. Neither reuse was actually load-bearing
for THIS engine's own feature set (contour geometry, ink counts, template
correlation -- every one of which sizes itself to whatever it's given) --
it just meant this engine's own accuracy was silently capped by whatever
normalization choice those OTHER modules happened to make for THEIR OWN
different classifiers, and any future change to either constant would have
required touching MAIN-scope or a different EXPLORE-scope module to keep
this one working. This project's own "write everything twice" precedent
(decision 47's full-duplication policy, gfl2/stat_ocr_padded.py) exists
for exactly this reason: reuse should never become a source of inertia
against improving the thing that's actually yours to improve. This script
is the "write it yourself" half of that trade -- deriving this engine's
OWN thresholds and OWN centroids from the OWN glyph representation it
actually uses at inference, rather than reusing someone else's.

MEASURED PAYOFF (2026-07-11): every margin either matched or WIDENED once
normalization was dropped entirely -- e.g. '7' vs '1' top-band gap went
3 (width=12, padded) -> 4 (native width, height-normalized) -> 16 (fully
native, no normalization at all); '4' vs everything else went from a
razor-thin 1-unit gap (any padded representation) to a genuine 15-unit
gap once measured as a PROPORTION of the glyph's own height instead of an
absolute canvas row range. Removing an artificial constraint didn't just
simplify the code, it made the classifier more robust.

PIPELINE:
  1. Collect every labelled pct-line glyph across --images via the SAME
     label-aligned extraction the real engine uses at build/verify time
     (gfl2.stat_ocr_dp._extract_pct_digit_glyphs, fed by
     gfl2.stat_ocr._collect_cells) -- these are now RAW, un-normalized
     tight crops (see that module's own NORMALIZATION note).
  2. Compute the exact raw feature values classify() itself uses, via the
     real functions imported from gfl2.stat_ocr_dp (_isoperimetric_ratio,
     _band_count, _reflex_vertices, _spread_y, _paren_features,
     _loop_features) -- no reimplementation of feature math.
  3. For each CLEAN-GAP constant (iso_gate, top_band_7, paren_close_3_gate,
     top_band_25 -- every real corpus split with zero overlap between
     classes), take the midpoint of the two class extremes, same
     methodology as gfl2/calibration/calibrate_hierarchical.py's
     _gap_bounds for its own clean-gap constants. top_band_4 additionally
     sweeps a small (p0, p1) proportion grid first, since -- unlike the
     others -- the FEATURE itself (which row band, as a fraction of the
     glyph's own height) is what needed deriving, not just where to cut a
     fixed feature.
  4. circular_centroids ('0'/'6'/'9'): a genuine CENTROID (corpus MEAN
     paren+loop feature vector, restricted to the holes==1 population --
     the only population that ever reaches this comparison in the real
     tree), matching this project's own established distinction between
     centroid-style constants (a corpus mean is sound) and interval-style
     constants (a single sample or a naive sweep is not, known_issues.txt
     §27/decisions.txt #70) -- these are centroids, so a corpus mean is
     the right derivation, not a single atlas sample.
  5. Write everything to gfl2/configs/daily_pct_dp_calib.json.

VALIDATION: after writing, re-runs gfl2.stat_ocr_dp.verify_glyphs() (which
reloads the config fresh) over the SAME corpus and prints the result --
do not trust the individual gap numbers above composing to the same
accuracy without checking; this script checks it directly, every run.

Usage:
    python -m gfl2.calibration.calibrate_dp --images "single/*.png"
"""
from __future__ import annotations
import argparse
import glob as _glob
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _collect_cells, _count_inner_blobs, _load_tess_gt_cache
from gfl2.stat_ocr_dp import (
    _extract_pct_digit_glyphs, _isoperimetric_ratio, _band_count,
    _reflex_vertices, _spread_y, _paren_features, _loop_features,
)

_DEFAULT_CONFIG_DIR = _ROOT / "gfl2" / "configs"
_DEFAULT_OUTPUT = _DEFAULT_CONFIG_DIR / "daily_pct_dp_calib.json"

_NONCIRCULAR_DIGITS = ("1", "2", "3", "4", "5", "7")
_CIRCULAR_DIGITS = ("0", "6", "8", "9")


def collect_corpus_glyphs(image_paths: list, gt_cache: "dict | None" = None) -> "dict[str, list]":
    """{digit: [raw_crop, ...]} across every labelled pct-line glyph."""
    gt_overrides_f = Path("stat_gt_overrides.json")
    gt_overrides = json.loads(gt_overrides_f.read_text(encoding="utf-8")) if gt_overrides_f.exists() else {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and "pct" in ov:
            item["pct"] = ov["pct"]

    by_digit: "dict[str, list]" = {d: [] for d in "0123456789"}
    thresh_cache: dict = {}
    for item in samples:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "", thresh_cache)
        if glyphs is None:
            continue
        for crop, label in glyphs:
            by_digit.setdefault(label, []).append(crop)
    return by_digit


def _gap_bounds(pos_vals: np.ndarray, neg_vals: np.ndarray) -> "tuple[float, float, float]":
    """Midpoint of a CLEAN (zero-overlap) gap between two value sets.
    Returns (midpoint, pos_extreme, neg_extreme) for reporting. Raises if
    the gap isn't actually clean -- this project's own history
    (known_issues.txt §27) found that trusting an assumed-clean gap
    without checking is exactly how a stale threshold goes unnoticed."""
    pos_min, neg_max = float(pos_vals.min()), float(neg_vals.max())
    if not (neg_max < pos_min):
        raise ValueError(f"gap not clean: neg_max={neg_max} >= pos_min={pos_min}")
    return (pos_min + neg_max) / 2.0, pos_min, neg_max


def calibrate_iso_gate(glyphs: "dict[str, list]") -> dict:
    iso = {d: np.array([_isoperimetric_ratio(c) for c in glyphs[d]]) for d in glyphs if glyphs[d]}
    circ_min = min(iso[d].min() for d in _CIRCULAR_DIGITS if d in iso)
    circ_max = max(iso[d].max() for d in _CIRCULAR_DIGITS if d in iso)
    noncirc_max = max(iso[d].max() for d in _NONCIRCULAR_DIGITS if d in iso)
    if not (noncirc_max < circ_min):
        raise ValueError(f"iso_gate not clean: noncirc_max={noncirc_max} >= circ_min={circ_min}")
    mid = (noncirc_max + circ_min) / 2.0
    print(f"iso_gate: noncircular max={noncirc_max:.4f}  circular min={circ_min:.4f}  "
          f"circular max={circ_max:.4f}  -> lo={mid:.4f}")
    return {"lo": round(mid, 4), "hi": round(circ_max + 0.05, 4)}


def calibrate_top_band_4(glyphs: "dict[str, list]") -> dict:
    def prop_band(crop, p0, p1):
        h = crop.shape[0]
        y0, y1 = int(round(p0 * h)), int(round(p1 * h))
        return _band_count(crop, y0, max(y0 + 1, y1))

    best = None
    for p0 in np.arange(0.45, 0.66, 0.02):
        for p1 in np.arange(0.70, 0.86, 0.02):
            if p1 <= p0:
                continue
            v4 = np.array([prop_band(c, p0, p1) for c in glyphs.get("4", [])])
            vrest = np.array([prop_band(c, p0, p1) for d in _NONCIRCULAR_DIGITS if d != "4"
                               for c in glyphs.get(d, [])])
            if len(v4) == 0 or len(vrest) == 0:
                continue
            gap = v4.min() - vrest.max()
            if best is None or gap > best[0]:
                best = (gap, round(float(p0), 2), round(float(p1), 2), v4.min(), vrest.max())
    if best is None or best[0] <= 0:
        raise ValueError(f"no clean proportional band found for '4': best={best}")
    gap, p0, p1, v4min, vrestmax = best
    gate = (v4min + vrestmax) / 2.0
    print(f"top_band_4: p0={p0} p1={p1}  '4' min={v4min}  rest max={vrestmax}  "
          f"gap={gap}  -> gate={gate}")
    return {"p0": p0, "p1": p1, "gate": round(float(gate), 2)}


def calibrate_top_band_7(glyphs: "dict[str, list]", heights=(2, 3, 4)) -> dict:
    best = None
    for h in heights:
        v1 = np.array([_band_count(c, 0, h) for c in glyphs.get("1", [])])
        v7 = np.array([_band_count(c, 0, h) for c in glyphs.get("7", [])])
        if len(v1) == 0 or len(v7) == 0:
            continue
        gap = v7.min() - v1.max()
        if gap <= 0:
            continue
        if best is None or h < best[1]:  # prefer the SMALLEST height that clears the margin
            best = (gap, h, v1.max(), v7.min())
    if best is None:
        raise ValueError("no clean top_band_7 height/gap found")
    gap, h, v1max, v7min = best
    gate = (v1max + v7min) / 2.0
    print(f"top_band_7: height={h}  '1' max={v1max}  '7' min={v7min}  gap={gap}  -> gate={gate}")
    return {"height": h, "gate": round(float(gate), 2)}


def calibrate_paren_close_3(glyphs: "dict[str, list]") -> float:
    v3 = np.array([_paren_features(c)[1] for c in glyphs.get("3", [])])
    vrest = np.array([_paren_features(c)[1] for d in ("2", "5") for c in glyphs.get(d, [])])
    mid, pos_min, neg_max = _gap_bounds(v3, vrest)
    print(f"paren_close_3_gate: '3' min={pos_min:.4f}  {{2,5}} max={neg_max:.4f}  -> gate={mid:.4f}")
    return round(mid, 4)


def calibrate_top_band_25(glyphs: "dict[str, list]", height=1) -> dict:
    v5 = np.array([_band_count(c, 0, height) for c in glyphs.get("5", [])])
    v2 = np.array([_band_count(c, 0, height) for c in glyphs.get("2", [])])
    mid, pos_min, neg_max = _gap_bounds(v5, v2)
    print(f"top_band_25: height={height}  '5' min={pos_min}  '2' max={neg_max}  -> gate={mid}")
    return {"height": height, "gate": round(mid, 2)}


def calibrate_circular_centroids(glyphs: "dict[str, list]") -> dict:
    """Corpus-mean paren+loop feature vector per digit, restricted to the
    holes==1 population (the only population that ever reaches this
    comparison in the real tree -- holes>=2 short-circuits to '8'
    categorically before this is ever computed)."""
    centroids = {}
    for d in ("0", "6", "9"):
        feats = []
        for crop in glyphs.get(d, []):
            if _count_inner_blobs(crop) != 1:
                continue
            feats.append(np.concatenate([_paren_features(crop), _loop_features(crop)]))
        if not feats:
            raise ValueError(f"no holes==1 samples found for digit '{d}'")
        centroid = np.mean(np.array(feats), axis=0)
        centroids[d] = [round(float(x), 4) for x in centroid]
        print(f"circular_centroid '{d}': n={len(feats)}  "
              f"(paren_open, paren_close, loop_top, loop_bot)={centroids[d]}")
    return centroids


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    ap.add_argument("--output", default=str(_DEFAULT_OUTPUT))
    args = ap.parse_args(argv)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images) if "debug" not in Path(p).stem)
    if not image_paths:
        print(f"No images matched: {args.images}", file=sys.stderr)
        sys.exit(1)
    print(f"Images: {len(image_paths)}")

    gt_cache = _load_tess_gt_cache() or {}
    if gt_cache:
        print(f"Using Tesseract GT cache: {len(gt_cache)} cells")

    glyphs = collect_corpus_glyphs(image_paths, gt_cache=gt_cache)
    for d in "0123456789":
        print(f"  '{d}': {len(glyphs.get(d, []))} glyphs")
    print()

    calib = {
        "iso_gate": calibrate_iso_gate(glyphs),
        "top_band_4": calibrate_top_band_4(glyphs),
        "top_band_7": calibrate_top_band_7(glyphs),
        "paren_close_3_gate": calibrate_paren_close_3(glyphs),
        "top_band_25": calibrate_top_band_25(glyphs),
        "circular_centroids": calibrate_circular_centroids(glyphs),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(calib, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")

    print("\nValidating end-to-end against the same corpus...")
    import importlib
    import gfl2.stat_ocr_dp as dp
    importlib.reload(dp)  # pick up the freshly-written config
    result = dp.verify_glyphs(image_paths, verbose=True, gt_cache=gt_cache)


if __name__ == "__main__":
    main()
