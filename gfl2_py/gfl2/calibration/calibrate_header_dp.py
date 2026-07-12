# -*- coding: utf-8 -*-
"""
gfl2/calibration/calibrate_header_dp.py -- derives EVERY re-derivable
constant gfl2/header_ocr_dp.py's classify_header() tree uses, from Daily
Gunsmoke's own real header-stats-row crops (dealt/taken/turns) across
single/*.png. Mirrors gfl2/calibration/calibrate_score_dp.py's methodology
exactly (same _gap_bounds clean-gap-midpoint convention, same corpus-mean
centroid derivation for the circular {0,6,9} leaf) -- see that script's own
module docstring for the full "write everything twice, don't let reuse
become inertia" rationale, identical here for the HEADER-STATS font
instead of the score font.

WHY CORPUS, NOT ATLAS: assets/fonts/glyph_daily_header.png is a real,
curated one-sample-per-character reference (debugs/build_glyph_reference.py),
but known_issues.txt #27/decisions.txt #70 already measured that an
interval-style gate derived from a single atlas sample can look perfectly
clean in isolation while still misrouting real corpus glyphs whose within-
class spread that one sample cannot represent. This script collects glyphs
the same way gfl2/calibration/calibrate_dp.py and calibrate_score_dp.py do:
via gfl2.header_ocr_dp._collect_header_crops (Tesseract-GT-labelled whole-
field crops from single/*.png's real dealt/taken/turns stats-row crops) +
_extract_header_digit_glyphs (label-aligned per-char extraction at this
module's own fixed HDR_THRESH=155 segmentation) -- both imported from
gfl2.header_ocr_dp, not reimplemented here.

TREE SHAPE FOUND (measured directly, not assumed by analogy to either
sibling dp-family engine):
  - M: isolated by raw glyph WIDTH alone, before anything else runs.
    Corpus-validated -- M is the single widest character in this font's
    whole set by a real, if not enormous (n=5 samples), margin: M width is
    a constant 15px; the next-widest character is K at a constant 13px.
  - iso_gate (circular {0,6,8,9} vs non-circular {1,2,3,4,5,7,K}): a
    clean, wide gap (non-circular max=0.2482 from '7', circular
    min=0.5148 from '6') -- same mechanism as both sibling dp-family
    engines, unmodified.
  - K: a LEFT-anchored ink-count band (this font's own new primitive,
    gfl2.header_ocr_dp._band_count_left) cleanly isolates K from the rest
    of the non-circular pool -- K's own leftmost stroke is a solid,
    near-full-height vertical bar unlike any digit's left edge.
  - '4': the SAME top-band-PROPORTIONAL-ink-count mechanism as gfl2.
    stat_ocr_dp.py's own TOP_BAND_4 (re-derived here via its own (p0,p1)
    grid sweep, not reused from that module's values) -- transfers
    cleanly to this font too.
  - {1,7} vs {2,3,5}: reflex-vertex spread_y splits them exactly as it
    does in the pct-line engine (spread_y==0 for {1,7}, spread_y>=7 for
    {2,3,5} on this font -- a real, if narrower, gap than the pct
    engine's own 0-vs-8+ gap).
  - {1,7}: a plain TOP-anchored ink count (same TOP_BAND_7 mechanism as
    gfl2.stat_ocr_dp.py) isolates '7' from '1' cleanly.
  - {2,3,5}: '3' isolates via spread_x FIRST (spread_x==0.0 exactly,
    zero overlap with {2,5}'s spread_x in [3,5]) -- the SAME grouping
    gfl2.score_ocr_dp.py found for the SCORE font (spread_x isolates '3',
    not '5' the way the pct-line engine's own tree does) -- confirms this
    is a real font-shape difference, not a fluke specific to one font.
    Remaining {2,5} splits via a BOTTOM-anchored ink count -- '2' ends in
    a real flat bottom stroke (high count), '5' curls inward (low count).

PIPELINE:
  1. Collect every labelled header-stat glyph across --images via
     gfl2.header_ocr_dp._collect_header_crops + _extract_header_digit_glyphs
     -- RAW, un-normalized tight crops, exactly what classify_header() sees
     at inference.
  2. Compute the exact raw feature values classify_header() itself uses,
     via the real functions imported from gfl2.header_ocr_dp
     (_isoperimetric_ratio, _glyph_width, _band_count, _band_count_left,
     _band_count_proportional, _bottom_band_count, _reflex_vertices,
     _spread_y, _spread_x, _paren_features, _loop_features, _count_inner_blobs
     via gfl2.stat_ocr) -- no reimplementation of feature math.
  3. For each CLEAN-GAP constant, take the midpoint of the two class
     extremes (_gap_bounds), same methodology as gfl2/calibration/
     calibrate_dp.py. top_band_4/k_left_gate/top_band_7/bottom_band_25
     additionally sweep a small grid first (a (p0,p1) proportion for
     top_band_4; a column/row-count width/height for the rest), since the
     FEATURE itself (which band, how wide/tall) needs deriving on this
     font's own scale, not just where to cut an already-fixed one.
  4. circular_centroids ('0'/'6'/'9'): a genuine CENTROID (corpus MEAN
     paren+loop feature vector, restricted to the holes==1 population).
  5. Write everything to gfl2/configs/daily_header_dp_calib.json.

VALIDATION: after writing, re-runs gfl2.header_ocr_dp.verify_glyphs() and
verify() (which reload the config fresh) over the SAME corpus and print
the result -- do not trust the individual gap numbers composing to the
same accuracy without checking; this script checks it directly, every run.

Usage:
    python -m gfl2.calibration.calibrate_header_dp --images "single/*.png"
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

from gfl2.stat_ocr import _count_inner_blobs
from gfl2.header_ocr_dp import (
    _collect_header_crops, _extract_header_digit_glyphs,
    _isoperimetric_ratio, _glyph_width, _band_count, _band_count_left,
    _band_count_proportional, _bottom_band_count,
    _reflex_vertices, _spread_y, _spread_x,
    _paren_features, _loop_features,
)

_DEFAULT_CONFIG_DIR = _ROOT / "gfl2" / "configs"
_DEFAULT_OUTPUT = _DEFAULT_CONFIG_DIR / "daily_header_dp_calib.json"

_CIRCULAR_CHARS = ("0", "6", "8", "9")
_NONCIRCULAR_CHARS = ("1", "2", "3", "4", "5", "7", "K")


def collect_corpus_glyphs(image_paths: list) -> "dict[str, list]":
    """{char: [raw_crop, ...]} across every labelled header-stat glyph."""
    samples = _collect_header_crops(image_paths)
    by_char: "dict[str, list]" = {c: [] for c in "0123456789KM"}
    for item in samples:
        glyphs = _extract_header_digit_glyphs(item["gray"], item["label"])
        if glyphs is None:
            continue
        for crop, label in glyphs:
            by_char.setdefault(label, []).append(crop)
    return by_char


def _gap_bounds(pos_vals: np.ndarray, neg_vals: np.ndarray) -> "tuple[float, float, float]":
    """Midpoint of a CLEAN (zero-overlap) gap between two value sets.
    Returns (midpoint, pos_extreme, neg_extreme). Raises if the gap isn't
    actually clean."""
    pos_min, neg_max = float(pos_vals.min()), float(neg_vals.max())
    if not (neg_max < pos_min):
        raise ValueError(f"gap not clean: neg_max={neg_max} >= pos_min={pos_min}")
    return (pos_min + neg_max) / 2.0, pos_min, neg_max


def calibrate_m_width_gate(glyphs: "dict[str, list]") -> float:
    m_widths = np.array([_glyph_width(c) for c in glyphs.get("M", [])])
    rest_widths = np.array([_glyph_width(c) for ch in "0123456789K" for c in glyphs.get(ch, [])])
    mid, m_min, rest_max = _gap_bounds(m_widths, rest_widths)
    print(f"m_width_gate: M min={m_min}  rest max={rest_max}  -> gate={mid}")
    return round(mid, 2)


def calibrate_iso_gate(glyphs: "dict[str, list]") -> dict:
    iso = {c: np.array([_isoperimetric_ratio(g) for g in glyphs[c]]) for c in glyphs if glyphs[c]}
    circ_min = min(iso[c].min() for c in _CIRCULAR_CHARS if c in iso)
    circ_max = max(iso[c].max() for c in _CIRCULAR_CHARS if c in iso)
    noncirc_max = max(iso[c].max() for c in _NONCIRCULAR_CHARS if c in iso)
    if not (noncirc_max < circ_min):
        raise ValueError(f"iso_gate not clean: noncirc_max={noncirc_max} >= circ_min={circ_min}")
    mid = (noncirc_max + circ_min) / 2.0
    print(f"iso_gate: noncircular max={noncirc_max:.4f}  circular min={circ_min:.4f}  "
          f"circular max={circ_max:.4f}  -> lo={mid:.4f}")
    return {"lo": round(mid, 4), "hi": round(circ_max + 0.05, 4)}


def calibrate_k_left_gate(glyphs: "dict[str, list]", widths=(1, 2, 3, 4, 5, 6)) -> dict:
    """K vs the rest of the non-circular pool {1,2,3,4,5,7} -- a LEFT-
    anchored ink-count band (this font's new primitive, transposed from
    the top-band mechanism used elsewhere in this dp-family)."""
    best = None
    for w in widths:
        vk = np.array([_band_count_left(c, 0, w) for c in glyphs.get("K", [])])
        vrest = np.array([_band_count_left(c, 0, w) for ch in ("1", "2", "3", "4", "5", "7")
                           for c in glyphs.get(ch, [])])
        if len(vk) == 0 or len(vrest) == 0:
            continue
        gap = vk.min() - vrest.max()
        if gap <= 0:
            continue
        if best is None or w < best[1]:  # prefer the SMALLEST width that clears the margin
            best = (gap, w, vrest.max(), vk.min())
    if best is None:
        raise ValueError("no clean k_left_gate width/gap found")
    gap, w, restmax, kmin = best
    gate = (restmax + kmin) / 2.0
    print(f"k_left_gate: width={w}  rest max={restmax}  K min={kmin}  gap={gap}  -> gate={gate}")
    return {"width": w, "gate": round(float(gate), 2)}


def calibrate_top_band_4(glyphs: "dict[str, list]") -> dict:
    """'4' vs the rest of {1,2,3,5,7} (K already gated out by this point in
    the real tree) -- a proportional top-band ink count, same mechanism
    (and same grid-sweep methodology) as gfl2.calibration.calibrate_dp's
    own calibrate_top_band_4."""
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
            vrest = np.array([prop_band(c, p0, p1) for d in ("1", "2", "3", "5", "7")
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
    """'3' vs {2,5} via spread_x -- the SAME grouping gfl2.score_ocr_dp.py
    found for the SCORE font (not the pct-line engine's own {2,3} vs '5'
    pairing). Measured directly, not assumed by analogy: this font's '3'
    reads spread_x==0.0 exactly, {2,5} read spread_x in [3,5]."""
    def sx(crop):
        pts, _ = _reflex_vertices(crop)
        return _spread_x(pts)
    v3 = np.array([sx(c) for c in glyphs.get("3", [])])
    v25 = np.array([sx(c) for d in ("2", "5") for c in glyphs.get(d, [])])
    mid, pos_min, neg_max = _gap_bounds(v25, v3)  # {2,5} is the HIGH-spread_x class
    print(f"spread_x_3_gate: {{2,5}} min={pos_min}  '3' max={neg_max}  -> gate={mid}")
    return round(mid, 2)


def calibrate_bottom_band_25(glyphs: "dict[str, list]", heights=(1, 2, 3, 4, 5, 6)) -> dict:
    """'2' vs '5', once '3' is already gated out by spread_x: '2' ends in a
    full-width flat bottom stroke (high, near-constant ink count in its
    own last row(s)); '5' curls inward at the bottom (lower count)."""
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
    for d in "0123456789KM":
        print(f"  '{d}': {len(glyphs.get(d, []))} glyphs")
    print()

    calib = {
        "m_width_gate": calibrate_m_width_gate(glyphs),
        "iso_gate": calibrate_iso_gate(glyphs),
        "k_left_gate": calibrate_k_left_gate(glyphs),
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
    import gfl2.header_ocr_dp as hdp
    importlib.reload(hdp)  # pick up the freshly-written config
    hdp.verify_glyphs(image_paths, verbose=True)
    hdp.verify(image_paths, verbose=True)


if __name__ == "__main__":
    main()
