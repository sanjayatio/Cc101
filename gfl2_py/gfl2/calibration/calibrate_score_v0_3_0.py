# -*- coding: utf-8 -*-
"""
gfl2/calibration/calibrate_score_v0_3_0.py -- derives EVERY re-derivable
constant gfl2/score_ocr_v0_3_0.py's classify_score() tree uses, from Daily
Gunsmoke's own real header-bar score crops across single/*.png. Mirrors
gfl2/calibration/calibrate_v0_3_0.py's methodology exactly (same tree shape,
same _gap_bounds clean-gap-midpoint convention, same corpus-mean
centroid derivation for the circular {0,6,9} leaf) -- see that script's
own module docstring for the full "write everything twice, don't let
reuse become inertia" rationale, identical here for the SCORE font
instead of the pct-line font.

WHY CORPUS, NOT ATLAS: assets/fonts/glyph_daily_score.png is a real,
curated one-sample-per-digit reference (docs/decisions.txt #84), but
known_issues.txt §27/decisions.txt #70 already measured that an
interval-style gate (iso_gate, top_band_4/7, spread_x_3_gate,
bottom_band_25 -- every constant this tree needs except the circular
centroids) derived from a single atlas sample can look perfectly clean
in isolation while still misrouting real corpus glyphs whose within-
class spread that one sample cannot represent. This script therefore
collects glyphs the same way gfl2/calibration/calibrate_v0_3_0.py does for
the pct-line engine: via _collect_score_crops (Tesseract-GT-labelled
whole-score crops from single/*.png's real medal-anchored header bars)
+ _extract_score_digit_glyphs (label-aligned per-digit extraction at
this module's own adaptive threshold) -- both imported from
gfl2.score_ocr_v0_3_0, not reimplemented here.

NOTE ON TREE SHAPE: this corpus is far smaller than the pct-line
corpus (dozens of glyphs per digit, not thousands) and this font
renders '2'/'3'/'5' differently enough that a direct port of gfl2/
stat_ocr_v0_3_0.py's {2,3,5} leaf (spread_x isolates '5', then a bottom-band
count splits {2,3}) does NOT hold here -- measured directly: this font's
spread_x instead isolates '3' from {2,5} (a real, opposite-of-pct-font
finding, not a bug), so this leaf is restructured accordingly. See
calibrate_spread_x_3's and calibrate_bottom_band_25's own docstrings.

PIPELINE:
  1. Collect every labelled score-digit glyph across --images via
     gfl2.score_ocr_v0_3_0._collect_score_crops + _extract_score_digit_glyphs
     -- these are RAW, un-normalized tight crops, exactly what
     classify_score() sees at inference.
  2. Compute the exact raw feature values classify_score() itself uses,
     via the real functions imported from gfl2.score_ocr_v0_3_0
     (_isoperimetric_ratio, _band_count, _band_count_proportional,
     _bottom_band_count, _reflex_vertices, _spread_y, _spread_x,
     _paren_features, _loop_features) -- no reimplementation of feature
     math.
  3. For each CLEAN-GAP constant (iso_gate, top_band_7, spread_x_3_gate,
     bottom_band_25 -- every real corpus split with zero overlap between
     classes), take the midpoint of the two class extremes, same
     methodology as gfl2/calibration/calibrate_v0_3_0.py's own _gap_bounds.
     top_band_4/bottom_band_25 additionally sweep a small grid first (a
     (p0,p1) proportion for top_band_4; a row-count height for
     bottom_band_25/top_band_7), since the FEATURE itself (which band,
     how tall) needs deriving on this font's own scale, not just where
     to cut an already-fixed one.
  4. circular_centroids ('0'/'6'/'9'): a genuine CENTROID (corpus MEAN
     paren+loop feature vector, restricted to the holes==1 population),
     matching this project's own established distinction between
     centroid-style constants (a corpus mean is sound) and interval-
     style constants (a single sample or naive sweep is not).
  5. Write everything to gfl2/configs/daily_score_v0_3_0_calib.json.

VALIDATION: after writing, re-runs gfl2.score_ocr_v0_3_0.verify_glyphs() and
verify() (which reload the config fresh) over the SAME corpus and print
the result -- do not trust the individual gap numbers composing to the
same accuracy without checking; this script checks it directly, every
run.

Usage:
    python -m gfl2.calibration.calibrate_score_v0_3_0 --images "single/*.png"
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

from gfl2.stat_ocr_v0_1_0 import _count_inner_blobs
from gfl2.score_ocr_v0_3_0 import (
    _collect_score_crops, _extract_score_digit_glyphs,
    _isoperimetric_ratio, _band_count, _band_count_proportional,
    _bottom_band_count, _reflex_vertices, _spread_y, _spread_x,
    _paren_features, _loop_features,
)

_DEFAULT_CONFIG_DIR = _ROOT / "gfl2" / "configs"
_DEFAULT_OUTPUT = _DEFAULT_CONFIG_DIR / "daily_score_v0_3_0_calib.json"

_NONCIRCULAR_DIGITS = ("1", "2", "3", "4", "5", "7")
_CIRCULAR_DIGITS = ("0", "6", "8", "9")


def collect_corpus_glyphs(image_paths: list) -> "dict[str, list]":
    """{digit: [raw_crop, ...]} across every labelled score-digit glyph."""
    samples = _collect_score_crops(image_paths)
    by_digit: "dict[str, list]" = {d: [] for d in "0123456789"}
    for item in samples:
        glyphs = _extract_score_digit_glyphs(item["gray"], item["label"])
        if glyphs is None:
            continue
        for crop, label in glyphs:
            by_digit.setdefault(label, []).append(crop)
    return by_digit


def _gap_bounds(pos_vals: np.ndarray, neg_vals: np.ndarray) -> "tuple[float, float, float]":
    """Midpoint of a CLEAN (zero-overlap) gap between two value sets.
    Returns (midpoint, pos_extreme, neg_extreme) for reporting. Raises if
    the gap isn't actually clean."""
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
    for p0 in np.arange(0.40, 0.66, 0.02):
        for p1 in np.arange(0.65, 0.86, 0.02):
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


def calibrate_top_band_7(glyphs: "dict[str, list]", heights=(1, 2, 3, 4, 5, 6)) -> dict:
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


def calibrate_spread_x_3(glyphs: "dict[str, list]") -> float:
    """'3' vs {2,5} via spread_x -- NOTE this is the OPPOSITE pairing from
    gfl2.stat_ocr_v0_3_0's pct-line engine, where spread_x isolates '5' from
    {2,3} instead. Measured directly on this corpus (not assumed by
    analogy): this SCORE font's '3' glyph has near-zero reflex-vertex
    horizontal spread (0-3px) while both '2' and '5' spread wide
    (5-7px) -- the two engines' fonts render these three digits'
    concave corners differently enough that the same feature ends up
    discriminating a different pair. See classify_score()'s own comment
    on this leaf for the full explanation."""
    def sx(crop):
        pts, _ = _reflex_vertices(crop)
        return _spread_x(pts)
    v3 = np.array([sx(c) for c in glyphs.get("3", [])])
    v25 = np.array([sx(c) for d in ("2", "5") for c in glyphs.get(d, [])])
    mid, pos_min, neg_max = _gap_bounds(v25, v3)  # {2,5} is the HIGH-spread_x class
    print(f"spread_x_3_gate: {{2,5}} min={pos_min}  '3' max={neg_max}  -> gate={mid}")
    return round(mid, 2)


def calibrate_bottom_band_25(glyphs: "dict[str, list]", heights=(1, 2, 3, 4, 5, 6)) -> dict:
    """'2' vs '5', once '3' is already gated out by spread_x: '2' ends in
    a full-width flat bottom stroke (high, near-constant ink count in its
    own last row(s)); '5' curls inward at the bottom (lower, more
    variable count). Same bottom-anchored-ink-count mechanism as the
    pct-line engine's '2'/'3' split, just paired against '5' instead of
    '3' here since spread_x already removed '3' from consideration."""
    best = None
    for h in heights:
        v2 = np.array([_bottom_band_count(c, h) for c in glyphs.get("2", [])])
        v5 = np.array([_bottom_band_count(c, h) for c in glyphs.get("5", [])])
        if len(v2) == 0 or len(v5) == 0:
            continue
        gap = v2.min() - v5.max()
        if gap <= 0:
            continue
        if best is None or h < best[1]:
            best = (gap, h, v5.max(), v2.min())
    if best is None:
        raise ValueError("no clean bottom_band_25 height/gap found")
    gap, h, v5max, v2min = best
    gate = (v5max + v2min) / 2.0
    print(f"bottom_band_25: height={h}  '5' max={v5max}  '2' min={v2min}  gap={gap}  -> gate={gate}")
    return {"height": h, "gate": round(float(gate), 2)}


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

    glyphs = collect_corpus_glyphs(image_paths)
    for d in "0123456789":
        print(f"  '{d}': {len(glyphs.get(d, []))} glyphs")
    print()

    calib = {
        "iso_gate": calibrate_iso_gate(glyphs),
        "top_band_4": calibrate_top_band_4(glyphs),
        "top_band_7": calibrate_top_band_7(glyphs),
        "spread_x_3_gate": calibrate_spread_x_3(glyphs),
        "bottom_band_25": calibrate_bottom_band_25(glyphs),
        "circular_centroids": calibrate_circular_centroids(glyphs),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(calib, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")

    print("\nValidating end-to-end against the same corpus...")
    import importlib
    import gfl2.score_ocr_v0_3_0 as sdp
    importlib.reload(sdp)  # pick up the freshly-written config
    sdp.verify_glyphs(image_paths, verbose=True)
    sdp.verify(image_paths, verbose=True)


if __name__ == "__main__":
    main()
