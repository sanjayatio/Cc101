# -*- coding: utf-8 -*-
"""
debugs/debug_line_stroke_thickness_sweep.py -- corpus sweep to derive a
PHYSICALLY-GROUNDED stroke-thickness measurement for the hierarchical
classifier's horizontal-bar leaves (line_split's '7' isolation via
hbar_sobel-MAX, the {2,3,5} leaf's '2'/'5' split via hbar_sobel-MEAN),
instead of fitting a boundary against whichever competing digit happens to
be nearby (direct feedback, 2026-07-10: "resist the temptation to fall
back to corpus [cross-class fitting] easily" -- the essence being isolated
is "this glyph has a horizontal line at the top/bottom", so the cutoff
should come from the target digit's OWN centroid + a buffer tied to
something real: stroke thickness).

TWO THINGS THIS SCRIPT DOES AT ONCE (same sweep, same per-glyph pass):

1. Measures REAL stroke thickness directly from the corpus -- same
   discipline as MAX_STROKE_W's own calibration (known_issues.txt §15's
   vrun entry: "measuring the corpus's OWN segment-width histogram... a
   median width of 4-5px", not guessed). A first attempt transposed the
   already-validated _horiz_segment_width primitive (which measures a
   VERTICAL stroke's width via vertical-run length) to measure a
   HORIZONTAL bar's thickness the same way -- REJECTED once tried on real
   glyphs: '7's top bar is usually CONNECTED to its diagonal descender
   with no background row between them, so the vertical run measures the
   bar+diagonal's combined extent, not the bar alone (caught immediately:
   measured "thickness" values of ~20-23px on a 20-row canvas, physically
   impossible for a bar alone). measure_stroke_thickness() instead counts
   consecutive ROWS whose foreground occupancy is >= BAR_INK_FRAC of the
   glyph's width -- a thin diagonal doesn't clear that bar, so it isolates
   the bar without needing a background gap below it. Verified against
   synthetic bars of KNOWN thickness, INCLUDING one connected to a thin
   stroke (reproducing the exact real-glyph failure mode) before trusting
   it on any real glyph, matching this project's own "calibrate on
   synthetic cases first" convention.

2. Flags OUTLIER images along the two variances raised directly:
     - centroid shift: an image's own per-digit mean of the classifier's
       actual gate feature (hbar_sobel max/mean) deviates from the global
       mean by >= OUTLIER_STD_MULT std -- symptomatic of a whole-image
       rendering anomaly (e.g. the mid-animation-capture artifact already
       root-caused for fb_d_20260315_p1_r3, known_issues.txt §23).
     - stroke thickness: an image's own per-digit mean stroke thickness
       deviates from the global mean the same way -- symptomatic of a
       real font-rendering/resolution difference across screenshots.
   This produces reason-tagged metadata per flagged image, feeding the
   separately-requested top-20 meaningful-image curation (covering doll
   frames / all font glyphs / outliers) -- outlier images found here are
   exactly the "covering the outliers" category that curation needs, with
   a concrete, reproducible reason attached instead of a hand-picked guess.

CAVEAT: per-image z-scores use the GLOBAL per-glyph std, not a per-image
standard-error-of-the-mean -- an image contributing only 1-2 glyphs can
swing its own mean by chance. Treat outlier flags as CANDIDATES for human
review (which is exactly what the top-20 curation step is), not as an
automated ground truth.

Usage:
    python debugs/debug_line_stroke_thickness_sweep.py
    python debugs/debug_line_stroke_thickness_sweep.py --images "single/*.png"
    python debugs/debug_line_stroke_thickness_sweep.py --digits 7,2,5
"""
from __future__ import annotations
import argparse
import glob as _glob
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr_v0_1_0 import _collect_cells, _load_tess_gt_cache
from gfl2.stat_ocr_v0_2_0 import _extract_pct_digit_glyphs, _hbar_features_sobel
from debugs.persist_run_result import save_run_result

OUTLIER_STD_MULT = 2.0

# Per-digit row band (fraction of glyph height, top=0) where its horizontal
# bar lives, and which hbar_sobel component is the classifier's actual gate
# feature for that digit -- 'max' for '7' (LINE-SPLIT SOBEL MODE's step 1),
# 'mean' for '2'/'5' (the {2,3,5} leaf's existing sobel_mean split).
LINE_DIGIT_CONFIG = {
    "7": {"row_band": (0.0, 0.40), "feature": "max"},
    "5": {"row_band": (0.0, 0.35), "feature": "mean"},
    "2": {"row_band": (0.60, 1.0), "feature": "mean"},
}


BAR_INK_FRAC = 0.5   # a row counts as "part of the bar" if >= this fraction
                      # of its width is foreground

# FIRST ATTEMPT, REJECTED: a straight transpose of _horiz_segment_width
# (which measures a VERTICAL stroke's WIDTH via vertical-run length) was
# tried first for measuring a HORIZONTAL bar's THICKNESS. It failed on
# real glyphs -- '7's top bar is usually CONNECTED to its diagonal
# descender with no background row between them, so the vertical run in
# any column touching both is the bar+diagonal's combined length, not the
# bar's own thickness (confirmed: real '7' glyphs measured ~20-23px
# "thickness" on a 20-row canvas -- physically impossible for a bar alone,
# immediately flagging the method as wrong rather than silently trusting
# it). ROW-INK-FRACTION is used instead: a genuine bar produces several
# CONSECUTIVE rows that are mostly-full-width foreground, while a thin
# diagonal descender is not (at BAR_INK_FRAC=0.5 on a 12px-wide glyph, the
# diagonal's ~2px width gives a row fraction of ~0.17, well under
# threshold) -- isolates the bar without needing a background gap below it.

def measure_stroke_thickness(norm: np.ndarray, row_band: tuple,
                              ink_frac: float = BAR_INK_FRAC) -> "float | None":
    """Count of rows within `row_band` (a fraction-of-height row range)
    whose foreground occupancy is >= `ink_frac` of the glyph's width --
    a bar-thickness measurement robust to the bar touching another stroke
    below it, unlike a plain vertical-run length (see rejected attempt
    above)."""
    h, w = norm.shape
    fg = norm > 127
    r0, r1 = int(round(row_band[0] * h)), max(int(round(row_band[1] * h)), 1)
    band = fg[r0:r1, :]
    if band.size == 0:
        return None
    row_frac = band.sum(axis=1) / w
    bar_rows = row_frac >= ink_frac
    if not bar_rows.any():
        return None
    return float(bar_rows.sum())


def run_synthetic_check() -> None:
    """Synthetic horizontal bars at KNOWN thickness in a 12x20 canvas
    (matching the real NORM_W_PCT x NORM_H_PCT glyph size) -- confirm
    measure_stroke_thickness recovers the true thickness before trusting
    it on any real glyph (known_issues.txt §15's own discipline). Also
    reproduces the exact real-glyph failure mode that sank the first
    (vertical-run-length) attempt at this measurement: a bar CONNECTED to
    a thinner stroke below it, with no background row in between."""
    print(f"\n{'=' * 60}")
    print("PART 0 -- synthetic stroke-thickness sanity check")
    print(f"{'=' * 60}")
    h, w = 20, 12
    ok = True
    for true_thickness in (2, 3, 4, 5, 6, 8):
        canvas = np.zeros((h, w), dtype=np.uint8)
        canvas[2:2 + true_thickness, :] = 255
        measured = measure_stroke_thickness(canvas, (0.0, 0.5))
        good = measured is not None and abs(measured - true_thickness) <= 0.5
        ok = ok and good
        print(f"  true={true_thickness}px  measured={measured}px  {'OK' if good else 'MISMATCH'}")

    # degenerate case: a solid fill should read as "every row in the band
    # is bar-like" (the whole band), not reject or blow up -- unlike the
    # rejected vertical-run-length attempt, which needs a background pixel
    # somewhere to avoid its own sentinel blowing up.
    solid = np.full((h, w), 255, dtype=np.uint8)
    band_h = int(round(0.5 * h))
    solid_measured = measure_stroke_thickness(solid, (0.0, 0.5))
    good = solid_measured == band_h
    ok = ok and good
    print(f"  degenerate solid-fill: measured={solid_measured}px  "
          f"(expected {band_h}, the whole probed band)  {'OK' if good else 'MISMATCH'}")

    # THE case that sank the rejected vertical-run-length attempt: a
    # true_thickness=4 bar directly CONNECTED (no background gap) to a
    # thin (2px) diagonal-like stroke filling the rest of the canvas --
    # must still recover ~4, not the combined bar+stroke extent.
    connected = np.zeros((h, w), dtype=np.uint8)
    connected[2:6, :] = 255                              # the bar, thickness=4
    for r in range(6, h):
        c0 = min(w - 2, (r - 6) // 2)
        connected[r, c0:c0 + 2] = 255                    # thin connected diagonal-ish stroke
    connected_measured = measure_stroke_thickness(connected, (0.0, 0.4))
    good = connected_measured is not None and abs(connected_measured - 4) <= 0.5
    ok = ok and good
    print(f"  bar(4px) CONNECTED to a thin stroke below: measured={connected_measured}px  "
          f"(expected ~4, not the combined extent)  {'OK' if good else 'MISMATCH'}")

    if not ok:
        sys.exit("Synthetic check FAILED -- do not trust real-glyph measurements below.")


def collect_source_tagged_glyphs(image_paths, digits) -> dict:
    """{digit: [(source, norm), ...]} -- like debugs/debug_sobel90_257_
    group.py's collect_glyphs, but keeping the source-image tag per glyph
    (needed for per-image aggregation, which that function discards)."""
    gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)

    gt_file = _ROOT / "tests" / "inputs" / "daily" / "stat_gt_overrides.json"
    if gt_file.exists():
        overrides = json.loads(gt_file.read_text(encoding="utf-8"))
        for item in samples:
            ov = overrides.get(item["source"])
            if ov and "pct" in ov:
                item["pct"] = ov["pct"]

    out = {d: [] for d in digits}
    for item in samples:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, label in glyphs:
            if label in out:
                out[label].append((item["source"], norm))
    return out


def sweep_digit(digit: str, tagged_glyphs: list) -> dict:
    cfg = LINE_DIGIT_CONFIG[digit]
    row_band, feat_name = cfg["row_band"], cfg["feature"]
    feat_idx = 1 if feat_name == "max" else 0

    per_image: dict = {}
    all_thickness, all_feat = [], []
    for source, norm in tagged_glyphs:
        thickness = measure_stroke_thickness(norm, row_band)
        if thickness is None:
            continue
        feat_val = float(_hbar_features_sobel(norm)[feat_idx])
        all_thickness.append(thickness)
        all_feat.append(feat_val)
        bucket = per_image.setdefault(source, {"thickness": [], "feat": []})
        bucket["thickness"].append(thickness)
        bucket["feat"].append(feat_val)

    all_thickness_a = np.array(all_thickness)
    all_feat_a = np.array(all_feat)
    g_thick_mean, g_thick_std = float(all_thickness_a.mean()), float(all_thickness_a.std())
    g_feat_mean, g_feat_std = float(all_feat_a.mean()), float(all_feat_a.std())

    per_image_summary = {}
    for source, b in per_image.items():
        th = np.array(b["thickness"]); ft = np.array(b["feat"])
        thick_z = (th.mean() - g_thick_mean) / g_thick_std if g_thick_std else 0.0
        feat_z = (ft.mean() - g_feat_mean) / g_feat_std if g_feat_std else 0.0
        reasons = []
        if abs(thick_z) >= OUTLIER_STD_MULT:
            reasons.append(f"stroke_thickness z={thick_z:+.2f} "
                            f"(image mean={th.mean():.2f}px vs corpus {g_thick_mean:.2f}px)")
        if abs(feat_z) >= OUTLIER_STD_MULT:
            reasons.append(f"centroid_shift z={feat_z:+.2f} "
                            f"(image mean={ft.mean():.4g} vs corpus {g_feat_mean:.4g})")
        per_image_summary[source] = {
            "n": len(th),
            "thickness_mean": round(float(th.mean()), 3),
            "thickness_z": round(float(thick_z), 3),
            "feat_mean": round(float(ft.mean()), 3),
            "feat_z": round(float(feat_z), 3),
            "outlier": bool(reasons),
            "reasons": reasons,
        }

    return {
        "digit": digit,
        "feature": feat_name,
        "n_glyphs": len(all_thickness),
        "global_thickness_mean": round(g_thick_mean, 3),
        "global_thickness_std": round(g_thick_std, 3),
        "global_feat_mean": round(g_feat_mean, 3),
        "global_feat_std": round(g_feat_std, 3),
        "per_image": per_image_summary,
    }


def print_digit_report(result: dict) -> None:
    d = result["digit"]
    print(f"\n{'=' * 100}")
    print(f"DIGIT '{d}' -- stroke thickness + centroid-shift sweep "
          f"({result['n_glyphs']} glyphs, feature=hbar_sobel_{result['feature']})")
    print(f"{'=' * 100}")
    print(f"  global stroke thickness:  mean={result['global_thickness_mean']}px  "
          f"std={result['global_thickness_std']}px")
    print(f"  global feature centroid:  mean={result['global_feat_mean']:.4g}  "
          f"std={result['global_feat_std']:.4g}")

    # candidate physically-derived gate, for direct comparison against
    # whatever cross-class-fitted gate is currently shipped for this digit.
    k = OUTLIER_STD_MULT
    lo = result['global_feat_mean'] - k * result['global_feat_std']
    hi = result['global_feat_mean'] + k * result['global_feat_std']
    print(f"  candidate gate (own centroid +/- {k}*std): [{lo:.4g}, {hi:.4g}]")

    outliers = {src: v for src, v in result["per_image"].items() if v["outlier"]}
    print(f"\n  {len(outliers)}/{len(result['per_image'])} images flagged as outliers (|z|>={OUTLIER_STD_MULT}):")
    for src, v in sorted(outliers.items(),
                          key=lambda kv: -max(abs(kv[1]["thickness_z"]), abs(kv[1]["feat_z"]))):
        print(f"    {src}  (n={v['n']})")
        for r in v["reasons"]:
            print(f"        {r}")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    ap.add_argument("--digits", default="7", help="comma-separated digits to sweep, e.g. 7,2,5")
    args = ap.parse_args(argv)

    run_synthetic_check()

    digits = [d.strip() for d in args.digits.split(",") if d.strip()]
    for d in digits:
        if d not in LINE_DIGIT_CONFIG:
            sys.exit(f"No row-band config for digit {d!r} -- add it to LINE_DIGIT_CONFIG first.")

    image_paths = sorted(Path(p) for p in _glob.glob(args.images) if "debug" not in Path(p).stem)
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    print(f"\nCollecting glyphs for {digits} from {len(image_paths)} image(s) ...")
    tagged = collect_source_tagged_glyphs(image_paths, digits)
    for d in digits:
        print(f"  '{d}': {len(tagged[d])} glyphs")

    results = {}
    for d in digits:
        result = sweep_digit(d, tagged[d])
        print_digit_report(result)
        results[d] = result

    # Merged "candidate meaningful images" list -- union of outliers across
    # every swept digit, deduplicated, reasons preserved per digit. Feeds
    # the separately-requested top-20 curated-image selection's "covering
    # the outliers" requirement.
    meaningful: dict = {}
    for d, result in results.items():
        for src, v in result["per_image"].items():
            if v["outlier"]:
                entry = meaningful.setdefault(src, {"source": src, "reasons": []})
                for r in v["reasons"]:
                    entry["reasons"].append(f"digit '{d}': {r}")

    print(f"\n{'=' * 100}")
    print(f"CANDIDATE MEANINGFUL IMAGES (outlier on centroid-shift or "
          f"stroke-thickness axis): {len(meaningful)}")
    print(f"{'=' * 100}")
    for src, entry in sorted(meaningful.items()):
        print(f"  {src}")
        for r in entry["reasons"]:
            print(f"      {r}")

    save_run_result(
        {"digits": digits, "outlier_std_mult": OUTLIER_STD_MULT,
         "results": results, "meaningful_images": list(meaningful.values())},
        subdir="line_stroke_thickness_runs",
    )


if __name__ == "__main__":
    main()
