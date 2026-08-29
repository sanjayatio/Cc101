# -*- coding: utf-8 -*-
"""
gfl2/calibration/calibrate_val_v0_3_0.py -- derives EVERY re-derivable constant
gfl2/stat_ocr_v0_3_0.py's classify_val() tree uses, from Daily Gunsmoke's own
real val-line crops across single/*.png. Mirrors gfl2/calibration/
calibrate_v0_3_0.py's methodology (Tesseract-GT-labelled corpus collection,
midpoint-of-clean-gap for interval constants, corpus-mean centroids for the
circular leaf) but for a SEPARATE font at a SEPARATE, much smaller native
scale -- see gfl2/stat_ocr_v0_3_0.py's own module docstring VAL-LINE TREE
section for why this tree's shape (hole-count root, width-based 1-vs-7,
bottom-row-deficit + top-left-quadrant for {2,3,5}) differs from the
pct-line tree's, not just its numbers.

WHY A SEPARATE SCRIPT, NOT A PARAMETRIZED calibrate_v0_3_0.py: the val font's
native crops are ~7-9x11-13px vs the pct font's ~7-19x11-20px, and several
FEATURES that work on the pct font (isoperimetric ratio as a root gate,
top-band ink counts for '1'/'7', spread_x for {2,3,5}) simply do not
separate cleanly at this smaller scale -- confirmed by direct measurement,
not assumed. Sharing one script would mean forcing this font's very
different measured shape through the other script's fixed pipeline of
calibrate_iso_gate/calibrate_top_band_7/calibrate_spread_x_5. Matches this
project's own "write everything twice" precedent (decision 47) at the
calibration-script level, same as calibrate_score_v0_3_0.py/
calibrate_header_v0_3_0.py each being their own script for their own font.

TREE SHAPE FOUND (measured directly on this font, not assumed by analogy):
  - ROOT is hole count, NOT isoperimetric ratio: at this glyph's native
    ~8x13px, isoperimetric ratio's best Youden's-J threshold only reaches
    recall=0.9984/false_trigger=0.0033 (not a clean gap) -- hole count is
    far cleaner (>=98.9% of every digit's samples match its expected hole
    count), with the residual almost entirely traceable to visually-
    confirmed Tesseract GT mislabels (a glyph shaped exactly like '8',
    holes=2, labelled '5' or '3'; a glyph shaped exactly like '4', holes=0,
    labelled '6'). This script does NOT calibrate an iso_gate at all.
  - K: a LEFT-anchored ink-count band (same mechanism as gfl2/
    header_ocr_v0_3_0.py's own K gate), checked within the holes==0 branch,
    BEFORE hole count would otherwise misroute a genuine '8' (2 holes) into
    K's left-band check -- clean gap, K min=22, rest({1,2,3,4,5,7}) max=18.
  - '4': the SAME top-band-PROPORTIONAL-ink-count mechanism as gfl2.
    stat_ocr_v0_3_0.py's own TOP_BAND_4, re-derived on this font's own holes==0
    population -- clean gap (v4min=13, rest max=8).
  - {1,7} vs {2,3,5}: reflex-vertex spread_y, same as the pct-line engine
    -- clean gap on the holes==0, '4'-excluded population ({1,7} max=2.0,
    {2,3,5} min=7.0).
  - {1,7}: NOT a top-band ink count (every height tried gives a NEGATIVE
    gap on this font -- '1' renders with a small top-left serif flag that
    outweighs '7's own top bar at this native size). Raw glyph WIDTH
    separates them instead: real corpus '1' is 4-5px wide, '7' is 7-8px
    wide (a handful of width-7/8 '1' samples and width-4/6 '7' samples are,
    on inspection, the SAME GT mislabels found for the hole-count root).
  - {2,3,5}: spread_x (the pct-line engine's own mechanism for this group)
    has NO separating power on this font at all (every grouping overlaps
    heavily). A BOTTOM-ROW-DEFICIT gate (glyph width minus its own last
    row's ink span) isolates '2' instead (Youden's J, since a handful of
    GT-mislabelled '5'/'3' samples keep the raw gap from being perfectly
    clean); a TOP-LEFT-QUADRANT ink count then splits '5' from '3' (also
    Youden's J).
  - circular_centroids ('0'/'6'/'9'): a genuine corpus-mean paren+loop
    feature vector, restricted to the holes==1 population -- THIS font's
    own values, never reused from the pct-line leaf's centroids (different
    native scale changes what these correlation values actually measure).

PIPELINE:
  1. Collect every labelled val-line glyph across --images via
     gfl2.stat_ocr_v0_1_0._collect_cells (Tesseract-GT-labelled, gt_cache-backed,
     stat_gt_overrides.json's "val" entries applied) +
     gfl2.stat_ocr_v0_3_0._extract_val_digit_glyphs (label-aligned extraction
     at this engine's own adaptive per-(strip-height, ink-group)
     threshold) -- RAW, un-normalized tight crops, exactly what
     classify_val() sees at inference.
  2. Compute the exact raw feature values classify_val() itself uses, via
     the real functions imported from gfl2.stat_ocr_v0_3_0 (_count_inner_blobs
     via gfl2.stat_ocr_v0_1_0, _band_count_left, _band_count_proportional,
     _reflex_vertices, _spread_y, _bottom_row_deficit, _left_top_count,
     _paren_features, _loop_features) -- no reimplementation of feature
     math.
  3. For each gate, derive on the population that ACTUALLY reaches that
     leaf in the real tree (e.g. '4' vs {1,2,3,5,7} is the holes==0
     population, not the raw per-digit population, which still includes
     the small hole-count-contaminated tail) -- a clean midpoint
     (_gap_bounds) where the gap really is clean, a Youden's-J sweep
     (reporting recall/false_trigger honestly) where it isn't.
  4. circular_centroids: a genuine corpus MEAN (holes==1 population).
  5. Write everything to gfl2/configs/daily_val_v0_3_0_calib.json.

UPDATE (known_issues.txt §37, decisions.txt #99): the {2,3,5} leaf's
bottom-row-deficit/top-left-quadrant magnitude gates (step 3's
deficit_2_gate/left_top_5_gate) are SUPERSEDED by a skeleton endpoint-
connectivity classifier (calibrate_skeleton_235, added to this SAME
script's pipeline -- one invocation still updates every parameterized
constant this font has). This was in fact the ORIGINAL motivating case
for the swap (known_issues.txt §37): a single antialiased pixel pair near
the shared adaptive binarization threshold flipped _bottom_row_deficit
from 3 (correct) to 1 (wrong) for one real corpus '5' glyph. The two
superseded gates are still calibrated and written (kept, not deleted) but
classify_val() no longer calls them.

VALIDATION: after writing, re-runs gfl2.stat_ocr_v0_3_0.verify_glyphs() (which
reloads BOTH config files fresh) over the SAME corpus and prints the
result -- do not trust the individual gap numbers composing to the same
accuracy without checking; this script checks it directly, every run.

Usage:
    python -m gfl2.calibration.calibrate_val_v0_3_0 --images "single/*.png"
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

from gfl2.stat_ocr_v0_1_0 import _collect_cells, _count_inner_blobs, _load_tess_gt_cache
from gfl2.stat_ocr_v0_3_0 import (
    _extract_val_digit_glyphs, _band_count_left, _band_count_proportional,
    _reflex_vertices, _spread_y, _bottom_row_deficit, _left_top_count,
    _paren_features, _loop_features, _classify_235_skeleton,
)

_DEFAULT_CONFIG_DIR = _ROOT / "gfl2" / "configs"
_DEFAULT_OUTPUT = _DEFAULT_CONFIG_DIR / "daily_val_v0_3_0_calib.json"

_NONCIRCULAR_CHARS = ("1", "2", "3", "4", "5", "7")
_CIRCULAR_DIGITS = ("0", "6", "8", "9")


def collect_corpus_glyphs(image_paths: list, gt_cache: "dict | None" = None) -> "dict[str, list]":
    """{char: [raw_crop, ...]} across every labelled val-line glyph
    (digits + 'K' -- this font never renders 'M', see gfl2/stat_ocr_v0_3_0.py's
    VAL_TRAIN_CHARS)."""
    gt_overrides_f = Path("tests/inputs/daily/stat_gt_overrides.json")
    gt_overrides = json.loads(gt_overrides_f.read_text(encoding="utf-8")) if gt_overrides_f.exists() else {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and "val" in ov:
            item["val"] = ov["val"]

    by_char: "dict[str, list]" = {c: [] for c in "0123456789K"}
    thresh_cache: dict = {}
    for item in samples:
        glyphs = _extract_val_digit_glyphs(item["cell"], item.get("val") or "", thresh_cache)
        if glyphs is None:
            continue
        for crop, label in glyphs:
            by_char.setdefault(label, []).append(crop)
    return by_char


def _holes(crop) -> int:
    return _count_inner_blobs(crop)


def _filter_holes(glyphs: "dict[str, list]", chars: "tuple[str, ...]", expect_holes: int) -> "dict[str, list]":
    """Restrict each char's population to samples whose hole count matches
    what the real tree expects to see at this leaf -- the population a
    handful of GT-mislabelled samples (confirmed by visual inspection to be
    a DIFFERENT digit's shape entirely, not this font's real rendering of
    the labelled digit) would otherwise contaminate. Matches this project's
    own established "measure on the population that actually reaches this
    leaf" discipline (known_issues.txt §27)."""
    return {c: [g for g in glyphs.get(c, []) if _holes(g) == expect_holes] for c in chars}


def _gap_bounds(pos_vals: np.ndarray, neg_vals: np.ndarray) -> "tuple[float, float, float]":
    """Midpoint of a CLEAN (zero-overlap) gap. Raises if the gap isn't
    actually clean."""
    pos_min, neg_max = float(pos_vals.min()), float(neg_vals.max())
    if not (neg_max < pos_min):
        raise ValueError(f"gap not clean: neg_max={neg_max} >= pos_min={pos_min}")
    return (pos_min + neg_max) / 2.0, pos_min, neg_max


def _youden_gate(pos_vals: np.ndarray, neg_vals: np.ndarray, candidates: np.ndarray) -> "tuple[float, float, float]":
    """Best integer/float threshold t (pos >= t counts as a positive call)
    by Youden's J = recall - false_trigger, for gates whose real corpus
    populations overlap slightly (typically a handful of GT-mislabelled
    samples, per this module's own docstring) rather than separating with
    a perfectly clean gap. Returns (t, recall, false_trigger)."""
    best = None
    for t in candidates:
        recall = float((pos_vals >= t).mean())
        false_trigger = float((neg_vals >= t).mean())
        j = recall - false_trigger
        if best is None or j > best[0]:
            best = (j, float(t), recall, false_trigger)
    _, t, recall, false_trigger = best
    return t, recall, false_trigger


def calibrate_k_left_gate(glyphs: "dict[str, list]", widths=(1, 2, 3, 4, 5, 6)) -> dict:
    """K vs the rest of the non-circular pool {1,2,3,4,5,7} (both
    populations restricted to holes==0, matching the real tree's own
    ordering -- K is checked within the holes==0 branch) -- a LEFT-
    anchored ink-count band, same mechanism as gfl2/header_ocr_v0_3_0.py's own
    K gate. Prefers the LARGEST clean gap across widths (this font's own
    measured optimum is NOT the smallest clearing width, unlike the header
    font's K gate -- width=1 and width=3 both give a much thinner margin
    here)."""
    pop = _filter_holes(glyphs, ("K",) + _NONCIRCULAR_CHARS, expect_holes=0)
    best = None
    for w in widths:
        vk = np.array([_band_count_left(c, 0, w) for c in pop.get("K", [])])
        vrest = np.array([_band_count_left(c, 0, w) for ch in _NONCIRCULAR_CHARS for c in pop.get(ch, [])])
        if len(vk) == 0 or len(vrest) == 0:
            continue
        gap = vk.min() - vrest.max()
        if gap <= 0:
            continue
        if best is None or gap > best[0]:
            best = (gap, w, vrest.max(), vk.min())
    if best is None:
        raise ValueError("no clean k_left_gate width/gap found")
    gap, w, restmax, kmin = best
    gate = (restmax + kmin) / 2.0
    print(f"k_left_gate: width={w}  rest max={restmax}  K min={kmin}  gap={gap}  -> gate={gate}")
    return {"width": w, "gate": round(float(gate), 2)}


def calibrate_top_band_4(glyphs: "dict[str, list]") -> dict:
    """'4' vs the rest of {1,2,3,5,7} (holes==0 population, the real
    tree's own population at this leaf -- K is already gated out ahead of
    this check) -- the same proportional-top-band mechanism (and grid-
    sweep methodology) as gfl2.calibration.calibrate_v0_3_0's own
    calibrate_top_band_4, re-derived fresh on this font."""
    pop = _filter_holes(glyphs, _NONCIRCULAR_CHARS, expect_holes=0)

    def prop_band(crop, p0, p1):
        h = crop.shape[0]
        y0, y1 = int(round(p0 * h)), int(round(p1 * h))
        from gfl2.stat_ocr_v0_3_0 import _band_count
        return _band_count(crop, y0, max(y0 + 1, y1))

    best = None
    for p0 in np.arange(0.40, 0.66, 0.02):
        for p1 in np.arange(0.65, 0.86, 0.02):
            if p1 <= p0:
                continue
            v4 = np.array([prop_band(c, p0, p1) for c in pop.get("4", [])])
            vrest = np.array([prop_band(c, p0, p1) for d in ("1", "2", "3", "5", "7") for c in pop.get(d, [])])
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


def calibrate_width_17_gate(glyphs: "dict[str, list]") -> float:
    """'7' (wide) vs '1' (narrow) via raw glyph WIDTH -- NOT a top-band ink
    count (every height tried gives a NEGATIVE gap on this font, see module
    docstring). Youden's J over integer widths -- the real corpus has a
    handful of width outliers on each side that are, on visual inspection,
    the SAME GT mislabels the hole-count root's own contamination traces
    to, so this is not a perfectly clean gap."""
    pop = _filter_holes(glyphs, ("1", "7"), expect_holes=0)
    v1 = np.array([c.shape[1] for c in pop["1"]], dtype=np.float64)
    v7 = np.array([c.shape[1] for c in pop["7"]], dtype=np.float64)
    candidates = np.arange(int(min(v1.min(), v7.min())), int(max(v1.max(), v7.max())) + 1)
    t, recall, false_trigger = _youden_gate(v7, v1, candidates)
    print(f"width_17_gate: t={t}  recall(7)={recall:.4f}  false_trigger(1)={false_trigger:.4f}")
    return t


def calibrate_deficit_2_gate(glyphs: "dict[str, list]") -> float:
    """'2' vs {3,5} via bottom-row deficit (glyph width minus its own last
    row's ink span) -- '2' ends in a full-width flat stroke (deficit near
    0); {3,5} curl inward (deficit much higher). '2' is the LOW-deficit
    class (deficit <= gate counts as '2'), the opposite sense from every
    other gate in this module, so this sweeps directly rather than reusing
    _youden_gate. Youden's J: a handful of GT-mislabelled '3'/'5' samples
    (shaped like '8', holes=2 -- excluded from THIS population since it's
    holes==0 already) keep this from being a perfectly clean gap."""
    pop = _filter_holes(glyphs, ("2", "3", "5"), expect_holes=0)
    v2 = np.array([_bottom_row_deficit(c) for c in pop["2"]], dtype=np.float64)
    v35 = np.array([_bottom_row_deficit(c) for d in ("3", "5") for c in pop[d]], dtype=np.float64)
    best = None
    for t in range(0, int(max(v2.max(), v35.max())) + 1):
        recall = float((v2 <= t).mean())
        false_trigger = float((v35 <= t).mean())
        j = recall - false_trigger
        if best is None or j > best[0]:
            best = (j, t, recall, false_trigger)
    _, gate, recall, false_trigger = best
    print(f"deficit_2_gate: gate={gate}  recall(2)={recall:.4f}  false_trigger({{3,5}})={false_trigger:.4f}")
    return float(gate)


def calibrate_left_top_5_gate(glyphs: "dict[str, list]") -> float:
    """'5' vs '3' (once '2' is already gated out by deficit) via top-left-
    quadrant ink count -- '5's flat top stroke starts further left than
    '3's right-open curves. Youden's J, same contamination caveat as
    deficit_2_gate above."""
    pop = _filter_holes(glyphs, ("3", "5"), expect_holes=0)
    v3 = np.array([_left_top_count(c) for c in pop["3"]], dtype=np.float64)
    v5 = np.array([_left_top_count(c) for c in pop["5"]], dtype=np.float64)
    candidates = np.arange(int(min(v3.min(), v5.min())), int(max(v3.max(), v5.max())) + 1)
    t, recall, false_trigger = _youden_gate(v5, v3, candidates)
    print(f"left_top_5_gate: t={t}  recall(5)={recall:.4f}  false_trigger(3)={false_trigger:.4f}")
    return t


_SKEL_TOP_FRAC_GRID = (0.25, 0.35, 0.45)
_SKEL_BOT_FRAC_GRID = (0.25, 0.35, 0.45)
_SKEL_MIN_SPUR_LEN_GRID = (0, 1, 2, 3)


def calibrate_skeleton_235(glyphs: "dict[str, list]") -> dict:
    """Grid search over (top_frac, bot_frac, min_spur_len) for the skeleton
    endpoint-connectivity {2,3,5} leaf (known_issues.txt §37, decisions.txt
    #98) -- SUPERSEDES calibrate_deficit_2_gate/calibrate_left_top_5_gate
    above (still run and still written to the config, kept not deleted,
    but no longer what classify_val() actually calls). Population is
    restricted to holes==0 (matching every other {2,3,5}-adjacent gate in
    this module -- the real tree never reaches this leaf with a holes!=0
    glyph).

    SCORING: net (correct - wrong), maximized -- NOT "fewest wrong first,
    correct as a tiebreak", which was tried first and is a real, documented
    mistake (known_issues.txt §37): it let a combo that abstains on almost
    everything (trivially very few wrong answers, since it barely answers
    at all) beat one that actually gets thousands right at the cost of a
    handful of misses -- it picked min_spur_len=3 (676/3621 correct) over
    min_spur_len=0, which the earlier feasibility sweep (debugs/
    calibrate_skeleton_235.py) had already shown is what this font needs.
    Net (correct - wrong) only prefers abstention over a wrong answer when
    the two are actually competing for the SAME glyph."""
    pop = _filter_holes(glyphs, ("2", "3", "5"), expect_holes=0)

    def score(top_frac, bot_frac, min_spur_len):
        correct = wrong = 0
        for d in ("2", "3", "5"):
            for crop in pop.get(d, []):
                pred = _classify_235_skeleton(crop, top_frac, bot_frac, min_spur_len)
                if pred == d:
                    correct += 1
                elif pred != "?":
                    wrong += 1
        return correct, wrong

    best = None
    for sl in _SKEL_MIN_SPUR_LEN_GRID:
        for tf in _SKEL_TOP_FRAC_GRID:
            for bf in _SKEL_BOT_FRAC_GRID:
                correct, wrong = score(tf, bf, sl)
                net = correct - wrong
                if best is None or net > best[0]:
                    best = (net, tf, bf, sl, correct, wrong)
    _, top_frac, bot_frac, min_spur_len, n_correct, n_wrong = best
    total = sum(len(pop.get(d, [])) for d in ("2", "3", "5"))
    print(f"skeleton_235: top_frac={top_frac} bot_frac={bot_frac} min_spur_len={min_spur_len}  "
          f"-> {n_correct}/{total} correct, {n_wrong} confident-wrong")
    return {"top_frac": top_frac, "bot_frac": bot_frac, "min_spur_len": min_spur_len}


def calibrate_circular_centroids(glyphs: "dict[str, list]") -> dict:
    """Corpus-mean paren+loop feature vector per digit, restricted to the
    holes==1 population -- THIS font's own values (paren/loop correlation
    against a glyph this much smaller than the pct-line font's does not
    measure the same thing, so these are never reused from
    gfl2.stat_ocr_v0_3_0's own pct-line centroids)."""
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
    for c in "0123456789K":
        print(f"  '{c}': {len(glyphs.get(c, []))} glyphs")
    print()

    calib = {
        "k_left_gate": calibrate_k_left_gate(glyphs),
        "top_band_4": calibrate_top_band_4(glyphs),
        "width_17_gate": calibrate_width_17_gate(glyphs),
        "deficit_2_gate": calibrate_deficit_2_gate(glyphs),
        "left_top_5_gate": calibrate_left_top_5_gate(glyphs),
        "skeleton_235": calibrate_skeleton_235(glyphs),
        "circular_centroids": calibrate_circular_centroids(glyphs),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(calib, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")

    print("\nValidating end-to-end against the same corpus...")
    import importlib
    import gfl2.stat_ocr_v0_3_0 as v0_3_0
    importlib.reload(v0_3_0)  # pick up the freshly-written config
    v0_3_0.verify_glyphs(image_paths, verbose=True, gt_cache=gt_cache)
    v0_3_0.verify(image_paths, verbose=True, gt_cache=gt_cache)


if __name__ == "__main__":
    main()
