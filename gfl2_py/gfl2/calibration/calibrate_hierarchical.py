# -*- coding: utf-8 -*-
"""
gfl2/calibration/calibrate_hierarchical.py -- re-derives gfl2/stat_ocr_fft.py's
hierarchical-classifier leaf/gate constants (VSTROKE_GATE_LO/HI,
PAREN_CLOSE_3_GATE, SOBEL_MEAN_C2/C5, SOBEL_MAX_C4/C7) from a single glyph
atlas image, instead of leaving them as hand-typed literals with no
reproducible derivation script (docs/action_items.txt #20; the gap this
closes is documented in docs/known_issues.txt §27).

Precedent: debugs/calibrate_gabor.py + assets/fonts/gabor_calib.json already
do this for Gabor's (lambd, sigma, gamma) from a many-image corpus. This
script covers a DIFFERENT, smaller set of constants (the hierarchical
classifier's own leaf/gate thresholds and reference centroids) from a
DIFFERENT, smaller input: one real glyph atlas image
(assets/fonts/glyph_daily_pct.png), one sample per digit -- see the CAVEAT
below for what that trades away.

PIPELINE:
  1. Isolate glyphs from the atlas using the SAME blob-detection primitives
     the live pipeline uses at inference (gfl2.stat_ocr._binarize +
     _find_blobs), not a hand-rolled cv2.findContours pass -- sorted by x,
     labelled via assets/fonts/glyph_lookup.py's index->char map.
  2. Normalize each isolated crop via gfl2.stat_ocr_fft._pad_glyph_no_resize
     -- imported directly from the live module (not reimplemented), so this
     script automatically tracks whatever normalization is live at
     calibration time, including future changes to it.
  3. Compute the exact raw feature values _classify_hierarchical() itself
     uses, via the real functions imported from gfl2.stat_ocr_fft
     (_raw_gabor45, _paren_features, _hbar_features_sobel) -- no
     reimplementation of feature math.
  4. Derive the five constants (see derive_vstroke_gate / derive_leaf_235 /
     derive_leaf_47 below) and write them to
     gfl2/configs/<atlas-stem-without-glyph->_hierarchical_calib.json
     (default: gfl2/configs/daily_pct_hierarchical_calib.json).

CAVEAT (n=1 per digit) -- MEASURED, NOT JUST THEORETICAL: every constant here
was ORIGINALLY derived from a grid sweep or percentile measurement over an
87-image, thousands-of-glyphs corpus (see docs/known_issues.txt §24-§26).
This script instead reads ONE real glyph per digit from a curated atlas
(itself built by debugs/build_glyph_reference.py as the real sample nearest
each digit's own trained centroid -- never a synthetic average). Validating
this script's own first real output against the full single/*.png corpus
(python -m gfl2.stat_ocr_fft --verify-glyphs --enable-hierarchical) found the
n=1 methodology behaves very differently depending on WHAT KIND of constant
it's deriving:
  - leaf_235 / leaf_47 (reference CENTROIDS for a nearest-of-2 comparison):
    a single representative point is a legitimate value for a centroid --
    atlas-derived leaf_47 alone fixed digit '4' from ~0% to 90.3% correct
    (992/993 -> 891/993 sobel-leaf glyphs correctly resolved) with ZERO
    digit regressions anywhere else in the corpus.
  - vstroke_gate (an INTERVAL/threshold): a single point per class has no
    within-class spread to derive a safe boundary from -- the atlas-derived
    interval (no overlap detected at n=1) still widened enough to misroute
    many real arc-dominant '0'/'3'/'5'/'6'/'9' glyphs into the line-dominant
    branch on the full corpus, regressing overall glyph accuracy from 86.6%
    to 82.15% even though '4' itself improved. A gate genuinely needs the
    corpus-wide recall/false-trigger sweep the ORIGINAL constants were built
    with (docs/known_issues.txt §24); a single atlas point cannot stand in
    for that, regardless of how clean its own point-estimate gap looks.
Consequently: vstroke_gate is COMPUTED and PRINTED for visibility (and
because a future corpus-driven recalibration should reuse the same
_gap_bounds machinery) but is NOT written to the output config by default --
pass --include-vstroke-gate to override and use it anyway, at your own risk.
leaf_235/leaf_47 ARE written by default; they're the validated part of this
first iteration. docs/action_items.txt #20 explicitly scopes this as
iterative; a --images "single/*.png"-driven corpus variant of vstroke_gate's
derivation (matching debugs/calibrate_gabor.py's own convention, giving it
the real distributional data an interval threshold needs) is the concrete
next step this measurement points to.

CORPUS MODE (2026-07-10, docs/decisions.txt #71 follow-up): --images enables
an ALTERNATIVE to the atlas for leaf_235/leaf_47 specifically -- derives each
centroid from the MEAN over every real glyph of that digit across the given
images, instead of the atlas's single sample. Checked directly, not assumed:
after fixing vstroke_gate upstream (via debugs/calibrate_gabor.py --objective
gate147, which lets ALL real '4'/'7' glyphs reach this leaf instead of only
the small fraction the previously-stale gate admitted), leaf_47's atlas
centroids left real accuracy on the table -- 95.38% forced-choice vs 100.00%
for the corpus mean over the same two digits. leaf_235 was checked the same
way and found ALREADY at 100.00% either way -- corpus mode is a genuine
improvement for some leaves, not a blanket "always better." vstroke_gate
remains excluded from THIS tool's output regardless of --images: a per-digit
MEAN is still not the real recall/false-trigger sweep over every individual
glyph a THRESHOLD needs -- see debugs/calibrate_gabor.py --objective
gate47/gate147 for that.

Usage:
    python -m gfl2.calibration.calibrate_hierarchical
    python -m gfl2.calibration.calibrate_hierarchical --atlas assets/fonts/glyph_daily_pct.png
    python -m gfl2.calibration.calibrate_hierarchical --images "single/*.png"
    python -m gfl2.calibration.calibrate_hierarchical --include-vstroke-gate  # not recommended, see CAVEAT
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _binarize, _find_blobs, NORM_W_PCT, NORM_H_PCT
from gfl2.stat_ocr_fft import (
    _pad_glyph_no_resize, _raw_gabor45, _paren_features, _hbar_features_sobel,
    _bar_thickness, LINE7_THICKNESS_ROW_BAND,
    VSTROKE_GATE_LO, VSTROKE_GATE_HI, PAREN_CLOSE_3_GATE,
    SOBEL_MEAN_C2, SOBEL_MEAN_C5, SOBEL_MAX_C4, SOBEL_MAX_C7,
    LINE_SOBEL_MAX_C7, LINE_SOBEL_MAX_POOLED14, LINE_SOBEL_MEAN_C1, LINE_SOBEL_MEAN_C4,
    LINE_THICKNESS_GATE_MIN_C7,
)

_DEFAULT_ATLAS = _ROOT / "assets" / "fonts" / "glyph_daily_pct.png"
_DEFAULT_LOOKUP = _ROOT / "assets" / "fonts" / "glyph_lookup.py"
_DEFAULT_CONFIG_DIR = _ROOT / "gfl2" / "configs"

_DIGITS = tuple("0123456789")


def _load_lookup(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location("glyph_lookup", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.DATA


def default_output_path(atlas_path: Path) -> Path:
    """glyph_daily_pct.png -> gfl2/configs/daily_pct_hierarchical_calib.json
    -- strip the 'glyph_' prefix so the config name self-documents which
    report line/type it was calibrated for (docs/action_items.txt #20's
    naming concern: a generic name would collide across future siblings
    like glyph_daily_val.png/glyph_daily_header.png)."""
    stem = atlas_path.stem
    if stem.startswith("glyph_"):
        stem = stem[len("glyph_"):]
    return _DEFAULT_CONFIG_DIR / f"{stem}_hierarchical_calib.json"


def isolate_atlas_glyphs(atlas_path: Path, lookup: dict) -> "dict[str, np.ndarray]":
    """Re-isolate + normalize every digit glyph from the atlas, using the
    SAME blob-detection primitives the live pipeline uses at inference
    (gfl2.stat_ocr._binarize/_find_blobs) and the SAME normalization
    (gfl2.stat_ocr_fft._pad_glyph_no_resize) -- so the feature values
    computed from these glyphs match what real inference would compute on
    an equivalent real crop. Returns {digit_char: normalized_glyph},
    dropping non-digit entries (e.g. '.')."""
    atlas = cv2.imread(str(atlas_path))
    if atlas is None:
        sys.exit(f"Could not read atlas: {atlas_path}")

    thresh = _binarize(atlas)
    blobs = sorted(_find_blobs(thresh), key=lambda b: b[0])

    if len(blobs) != len(lookup):
        sys.exit(
            f"Found {len(blobs)} blobs in {atlas_path.name} but "
            f"glyph_lookup.py lists {len(lookup)} entries for it -- atlas "
            f"and lookup are out of sync, regenerate both via "
            f"debugs/build_glyph_reference.py before re-running this."
        )

    glyphs: "dict[str, np.ndarray]" = {}
    for i, (x, y, w, h) in enumerate(blobs):
        char = lookup[str(i)]
        if char not in _DIGITS:
            continue
        crop = thresh[y:y + h, x:x + w]
        glyphs[char] = _pad_glyph_no_resize(crop, NORM_W_PCT, NORM_H_PCT)

    missing = [d for d in _DIGITS if d not in glyphs]
    if missing:
        sys.exit(f"Atlas is missing digit(s) {missing} after isolation -- "
                  f"cannot calibrate without all 10.")
    return glyphs


def compute_raw_features(glyphs: "dict[str, np.ndarray]") -> "dict[str, dict[str, float]]":
    """Per-digit raw feature values, using the REAL functions
    _classify_hierarchical() itself calls -- not a reimplementation."""
    out = {}
    for d, norm in glyphs.items():
        sobel_mean, sobel_max = _hbar_features_sobel(norm)
        out[d] = {
            "raw_gabor": _raw_gabor45(norm),
            "paren_close": float(_paren_features(norm)[1]),
            "sobel_mean": float(sobel_mean),
            "sobel_max": float(sobel_max),
        }
    return out


# ── CORPUS mode (2026-07-10, docs/decisions.txt #71 follow-up) ─────────────
# Validating leaf_47's first atlas-derived SOBEL_MAX_C4/C7 against the real
# corpus (once vstroke_gate was fixed upstream via debugs/calibrate_gabor.py
# --objective gate147, letting ALL real '4'/'7' glyphs actually reach this
# leaf instead of only the small, cleanly-routed fraction the stale gate
# admitted) found the atlas's single-sample centroids leave real accuracy on
# the table: 95.38% forced-choice vs 100.00% for the corpus MEAN over the
# same two digits. leaf_235's centroids were ALSO checked this way and found
# already at 100.00% either way -- not every leaf benefits, but leaf_47
# measurably does. --images enables this corpus-mean mode as an ALTERNATIVE
# to the atlas for leaf_235/leaf_47 specifically; vstroke_gate remains
# excluded from this tool regardless of input source (a per-digit MEAN over
# the corpus is still not the same as the real recall/false-trigger sweep
# over every individual glyph a THRESHOLD needs -- that sweep lives in
# debugs/calibrate_gabor.py's --objective gate47/gate147, which operates on
# the full per-glyph distribution, not per-digit means).

def collect_corpus_glyphs(image_paths: list, gt_cache: "dict | None" = None) -> "dict[str, list[np.ndarray]]":
    """{digit: [normalized glyph, ...]} across every labelled pct-line
    glyph in `image_paths` -- same label-aligned extraction build_templates()
    trains from (gfl2.stat_ocr_fft._extract_pct_digit_glyphs), so corpus mode
    sees identical crops to what training/inference actually use."""
    from collections import defaultdict
    from gfl2.stat_ocr import _collect_cells, _load_tess_gt_cache
    from gfl2.stat_ocr_fft import _extract_pct_digit_glyphs
    if gt_cache is None:
        gt_cache = _load_tess_gt_cache() or {}
    cells = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    buckets: "dict[str, list[np.ndarray]]" = defaultdict(list)
    for item in cells:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, label in glyphs:
            if label in _DIGITS:
                buckets[label].append(norm)
    return buckets


def compute_raw_features_corpus(buckets: "dict[str, list[np.ndarray]]") -> "dict[str, dict[str, float]]":
    """Same shape as compute_raw_features() (one scalar per digit per
    feature) so derive_leaf_235/derive_leaf_47/derive_vstroke_gate/
    print_summary all consume either source unmodified -- but each value is
    the MEAN across every glyph of that digit in the corpus, not a single
    atlas sample."""
    out = {}
    for d, glyphs in buckets.items():
        sobel = np.array([_hbar_features_sobel(g) for g in glyphs])
        out[d] = {
            "raw_gabor": float(np.mean([_raw_gabor45(g) for g in glyphs])),
            "paren_close": float(np.mean([_paren_features(g)[1] for g in glyphs])),
            "sobel_mean": float(sobel[:, 0].mean()),
            "sobel_max": float(sobel[:, 1].mean()),
        }
    return out


def _gap_bounds(target: "dict[str, float]", rest: "dict[str, float]") -> "tuple[float, float, list[str]]":
    """Bounds all of `target`'s values with the midpoint gap to the nearest
    `rest` value on each side (a fixed margin if no rest value exists on
    that side). Returns (lo, hi, overlap_digits) -- overlap_digits lists any
    `rest` digit whose value falls INSIDE [min(target), max(target)], a real
    risk at n=1 a corpus-wide recall/false-trigger sweep wouldn't have this
    exposure to; the caller is responsible for surfacing it, not this
    function silently proceeding."""
    t_items = sorted(target.items(), key=lambda kv: kv[1])
    r_items = sorted(rest.items(), key=lambda kv: kv[1])
    lo_t, hi_t = t_items[0][1], t_items[-1][1]

    overlap = [d for d, v in r_items if lo_t <= v <= hi_t]

    below = [v for _, v in r_items if v < lo_t]
    above = [v for _, v in r_items if v > hi_t]
    margin = (hi_t - lo_t) * 0.5 or 1.0
    lo = (max(below) + lo_t) / 2 if below else lo_t - margin
    hi = (min(above) + hi_t) / 2 if above else hi_t + margin
    return lo, hi, overlap


def derive_vstroke_gate(feats: "dict[str, dict[str, float]]") -> dict:
    """CAUTION: measured to REGRESS full-corpus accuracy even when this
    function's own overlap check finds nothing wrong -- see the module
    docstring's CAVEAT. Computed for visibility; not written to the config
    by default (see main()'s --include-vstroke-gate)."""
    target = {d: feats[d]["raw_gabor"] for d in ("1", "4", "7")}
    rest = {d: feats[d]["raw_gabor"] for d in _DIGITS if d not in target}
    lo, hi, overlap = _gap_bounds(target, rest)
    if overlap:
        print(f"  WARNING: vstroke_gate -- digit(s) {overlap} fall inside "
              f"{{1,4,7}}'s own raw_gabor range at this atlas's n=1 sample; "
              f"gate cannot cleanly separate them here. Derived anyway "
              f"(lo={lo:.1f}, hi={hi:.1f}) but treat as unvalidated.")
    return {"lo": round(lo, 1), "hi": round(hi, 1)}


def derive_leaf_235(feats: "dict[str, dict[str, float]]") -> dict:
    three = feats["3"]["paren_close"]
    two_five_max = max(feats["2"]["paren_close"], feats["5"]["paren_close"])
    if three <= two_five_max:
        print(f"  WARNING: leaf_235.paren_close_gate -- expected '3' "
              f"({three:.3f}) > max('2','5') ({two_five_max:.3f}) on this "
              f"atlas, but it doesn't hold. Keeping the existing default "
              f"instead of writing an inverted gate.")
        gate = PAREN_CLOSE_3_GATE
    else:
        gate = (three + two_five_max) / 2
    return {
        "paren_close_gate": round(gate, 3),
        "sobel_mean_c2": round(feats["2"]["sobel_mean"], 2),
        "sobel_mean_c5": round(feats["5"]["sobel_mean"], 2),
    }


def derive_leaf_47(feats: "dict[str, dict[str, float]]") -> dict:
    return {
        "sobel_max_c4": round(feats["4"]["sobel_max"], 2),
        "sobel_max_c7": round(feats["7"]["sobel_max"], 2),
    }


def derive_line_split(feats: "dict[str, dict[str, float]]",
                       buckets: "dict[str, list] | None" = None) -> dict:
    """LINE-SPLIT SOBEL MODE (docs/known_issues.txt §26 follow-up,
    2026-07-10): a two-step CENTROID cascade, not an interval/gate, so it
    follows leaf_235/leaf_47's precedent (a single representative point --
    or, in corpus mode, a real per-glyph-weighted mean -- is a legitimate
    value for a nearest-of-2 comparison; see the module CAVEAT for why that
    does NOT extend to interval-style constants like vstroke_gate).

    step 1 (isolate '7' via MAX): needs a centroid for pooled {1,4}, not
    just '4' alone -- '1' is even farther from '7' than '4' is, so pooling
    it in only widens the gap.  When `buckets` (real per-glyph lists, from
    --images corpus mode) is available, this is the TRUE per-glyph-weighted
    mean over every real '1' and '4' glyph -- NOT a plain average of the
    two already-collapsed per-digit means, which would silently over-weight
    whichever digit has fewer samples (here '4', 993 glyphs vs '1's 1711).
    Falls back to a simple average of the two per-digit values when only
    atlas-derived `feats` is available (n=1 per digit -- no real weighting
    distinction exists to make).

    step 2 (split '1'/'4' via MEAN): a direct pair -- c1/c4 are already
    exactly feats["1"]/["4"]["sobel_mean"], no pooling needed.
    """
    if buckets is not None:
        max_1 = np.array([_hbar_features_sobel(g)[1] for g in buckets["1"]])
        max_4 = np.array([_hbar_features_sobel(g)[1] for g in buckets["4"]])
        pooled_14_max = float(np.concatenate([max_1, max_4]).mean())
    else:
        pooled_14_max = (feats["1"]["sobel_max"] + feats["4"]["sobel_max"]) / 2
    return {
        "sobel_max_c7": round(feats["7"]["sobel_max"], 2),
        "sobel_max_pooled14": round(pooled_14_max, 2),
        "sobel_mean_c1": round(feats["1"]["sobel_mean"], 2),
        "sobel_mean_c4": round(feats["4"]["sobel_mean"], 2),
    }


def derive_line_split_thickness(buckets: "dict[str, list] | None") -> "dict | None":
    """STROKE-THICKNESS CONFIRMATION gate for '7' isolation (see the
    section above _bar_thickness in gfl2/stat_ocr_fft.py): the midpoint
    between '4's real max and '7's real min measured top-band stroke
    thickness. REQUIRES `buckets` (real per-glyph corpus glyphs, --images
    mode) -- a single atlas sample per digit cannot establish a safe
    min/max bound the way a real distribution can (returns None, meaning
    "keep the existing default", when atlas-only)."""
    if buckets is None:
        return None
    t4 = [_bar_thickness(g, LINE7_THICKNESS_ROW_BAND) for g in buckets["4"]]
    t7 = [_bar_thickness(g, LINE7_THICKNESS_ROW_BAND) for g in buckets["7"]]
    gate_min = (max(t4) + min(t7)) / 2
    if max(t4) >= min(t7):
        print(f"  WARNING: line_split_thickness.gate_min_c7 -- '4's max "
              f"thickness ({max(t4):.2f}) >= '7's min ({min(t7):.2f}) on this "
              f"corpus; no clean gap. Derived anyway (gate_min={gate_min:.2f}) "
              f"but treat as unvalidated.")
    return {"gate_min_c7": round(gate_min, 2)}


def print_summary(feats: "dict[str, dict[str, float]]", derived: dict) -> None:
    print(f"{'digit':>5}  {'raw_gabor':>12}  {'paren_close':>12}  "
          f"{'sobel_mean':>14}  {'sobel_max':>14}")
    for d in _DIGITS:
        f = feats[d]
        print(f"{d:>5}  {f['raw_gabor']:>12.2f}  {f['paren_close']:>12.4f}  "
              f"{f['sobel_mean']:>14.2f}  {f['sobel_max']:>14.2f}")
    print()
    print("Derived vs current effective value (config if loaded, else hardcoded default):")
    print(f"  vstroke_gate.lo            {derived['vstroke_gate']['lo']:>14.1f}   (was {VSTROKE_GATE_LO})")
    print(f"  vstroke_gate.hi            {derived['vstroke_gate']['hi']:>14.1f}   (was {VSTROKE_GATE_HI})")
    print(f"  leaf_235.paren_close_gate  {derived['leaf_235']['paren_close_gate']:>14.3f}   (was {PAREN_CLOSE_3_GATE})")
    print(f"  leaf_235.sobel_mean_c2     {derived['leaf_235']['sobel_mean_c2']:>14.2f}   (was {SOBEL_MEAN_C2})")
    print(f"  leaf_235.sobel_mean_c5     {derived['leaf_235']['sobel_mean_c5']:>14.2f}   (was {SOBEL_MEAN_C5})")
    print(f"  leaf_47.sobel_max_c4       {derived['leaf_47']['sobel_max_c4']:>14.2f}   (was {SOBEL_MAX_C4})")
    print(f"  leaf_47.sobel_max_c7       {derived['leaf_47']['sobel_max_c7']:>14.2f}   (was {SOBEL_MAX_C7})")
    print(f"  line_split.sobel_max_c7        {derived['line_split']['sobel_max_c7']:>10.2f}   (was {LINE_SOBEL_MAX_C7})")
    print(f"  line_split.sobel_max_pooled14  {derived['line_split']['sobel_max_pooled14']:>10.2f}   (was {LINE_SOBEL_MAX_POOLED14})")
    print(f"  line_split.sobel_mean_c1       {derived['line_split']['sobel_mean_c1']:>10.2f}   (was {LINE_SOBEL_MEAN_C1})")
    print(f"  line_split.sobel_mean_c4       {derived['line_split']['sobel_mean_c4']:>10.2f}   (was {LINE_SOBEL_MEAN_C4})")
    if derived.get("line_split_thickness") is not None:
        print(f"  line_split_thickness.gate_min_c7 {derived['line_split_thickness']['gate_min_c7']:>7.2f}   (was {LINE_THICKNESS_GATE_MIN_C7})")
    else:
        print(f"  line_split_thickness.gate_min_c7        n/a (atlas mode)   (was {LINE_THICKNESS_GATE_MIN_C7})")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--atlas", default=str(_DEFAULT_ATLAS))
    ap.add_argument("--lookup", default=str(_DEFAULT_LOOKUP))
    ap.add_argument("--output", default=None,
                     help="default: derived from --atlas's filename, see default_output_path()")
    ap.add_argument("--include-vstroke-gate", action="store_true",
                     help="write the atlas-derived vstroke_gate to the config too "
                          "(NOT RECOMMENDED regardless of --images -- a per-digit "
                          "MEAN is still not the recall/false-trigger sweep over the "
                          "full per-glyph distribution a THRESHOLD needs; use "
                          "debugs/calibrate_gabor.py --objective gate47/gate147 "
                          "instead, see module docstring's CORPUS mode note). Without "
                          "this flag, vstroke_gate is still computed and printed, "
                          "just not written -- the loader falls back to its "
                          "hardcoded default (or whatever calibrate_gabor.py's own "
                          "gate objective already wrote) for that group.")
    ap.add_argument("--images", default=None,
                     help="Corpus-mean mode: a glob (e.g. \"single/*.png\") -- when "
                          "given, leaf_235/leaf_47 are derived from the MEAN over "
                          "every real glyph of each digit across these images "
                          "instead of the atlas's single sample (see the CORPUS "
                          "mode note above collect_corpus_glyphs). Overrides --atlas "
                          "for feature derivation; --atlas/--lookup are still used "
                          "for --output's default naming unless --output is given "
                          "explicitly.")
    args = ap.parse_args(argv)

    run_start = datetime.now().isoformat(timespec="seconds")
    print(f"Generated: {run_start}  (run start)")

    atlas_path = Path(args.atlas)
    output_path = Path(args.output) if args.output else default_output_path(atlas_path)

    if args.images:
        import glob as _glob
        image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                              if "debug" not in Path(p).stem)
        if not image_paths:
            sys.exit(f"No images matched: {args.images}")
        print(f"Corpus mode: collecting glyphs from {len(image_paths)} image(s) ...")
        buckets = collect_corpus_glyphs(image_paths)
        missing = [d for d in _DIGITS if d not in buckets]
        if missing:
            sys.exit(f"Corpus is missing digit(s) {missing} -- cannot calibrate.")
        print(f"  {sum(len(v) for v in buckets.values())} glyphs across "
              f"{len(buckets)} digits: { {d: len(buckets[d]) for d in _DIGITS} }")
        feats = compute_raw_features_corpus(buckets)
        source_desc = {"source_images": [p.name for p in image_paths]}
    else:
        lookup_path = Path(args.lookup)
        lookup_all = _load_lookup(lookup_path)
        if atlas_path.name not in lookup_all:
            sys.exit(f"{lookup_path} has no entry for {atlas_path.name!r}")
        lookup = lookup_all[atlas_path.name]
        glyphs = isolate_atlas_glyphs(atlas_path, lookup)
        feats = compute_raw_features(glyphs)
        source_desc = {"source_atlas": atlas_path.name}
        buckets = None

    derived = {
        "vstroke_gate": derive_vstroke_gate(feats),
        "leaf_235": derive_leaf_235(feats),
        "leaf_47": derive_leaf_47(feats),
        "line_split": derive_line_split(feats, buckets=buckets),
        "line_split_thickness": derive_line_split_thickness(buckets),
    }

    print_summary(feats, derived)

    payload = dict(derived)
    if payload["line_split_thickness"] is None:
        del payload["line_split_thickness"]
        print("\nline_split_thickness not written (needs --images corpus mode -- "
              "a single atlas sample can't establish a safe min/max gap). The "
              "loader falls back to its hardcoded default for this group.")
    if not args.include_vstroke_gate:
        del payload["vstroke_gate"]
        print("\nvstroke_gate computed above but NOT written (measured to regress "
              "full-corpus accuracy -- see module docstring's CAVEAT). Pass "
              "--include-vstroke-gate to write it anyway. The loader falls back "
              "to its hardcoded default for this group.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload["generated"] = run_start
    payload.update(source_desc)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {output_path}")


if __name__ == "__main__":
    main()
