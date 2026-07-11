# -*- coding: utf-8 -*-
"""
debugs/debug_stat_ocr_dp_5_vs_7_robustness.py

INVESTIGATION: gfl2/stat_ocr_dp.py isolates '7' (within the {1,7} bucket)
via a plain spatial top-band ink COUNT (TOP_BAND_7_HEIGHT/GATE) -- a
saturated, near-binary measurement -- but isolates '5' (within the {2,3,5}
bucket, after '3' gates out) via a nearest-of-2 comparison on
_hbar_features_sobel's MEAN response, a continuous merged-kernel Sobel-90
convolution magnitude. Both leaves sit at the same tree depth and both are
documented as "PERFECT"/100% on the static single/*.png corpus (confirmed
directly: `python -m gfl2.stat_ocr_dp --verify-glyphs` reports 0
misclassified / 0 unknown for BOTH digits on the current 87-image corpus,
10327 glyphs total) -- so today's real corpus cannot produce a failure for
either digit to compare.

This script stress-tests the two leaves against controlled SCALE and
STROKE-THICKNESS jitter (the two robustness axes action_items.txt #25
already flags as untested for any noncircular_mode) applied to REAL,
correctly-classified corpus glyphs of every non-circular digit
{1,2,3,4,5,7} -- not just 5/7 themselves, since a false POSITIVE for '5'
or '7' can come from a neighboring digit drifting across the gate under
perturbation, not just a false negative from 5/7 drifting away from it.

Perturbations are applied to the TIGHT, UN-PADDED binary crop (before
gfl2.stat_ocr_dp._pad_glyph_no_resize), matching where a genuinely
different render scale/stroke-weight would actually enter the pipeline --
not to the already-padded 12x20 canvas, which would just be moving ink
around inside a fixed frame rather than simulating a different source
glyph.

Stops the whole sweep once 10 total failures (false positives + false
negatives, either digit) are collected, walking glyphs in a fixed,
reproducible order (source path, then digit index, then perturbation
severity) so a re-run finds the identical 10.

UPDATE (2026-07-11): the '2'/'5' leaf described above has since been
replaced -- gfl2/stat_ocr_dp.py's classify() now uses a plain top-band
count (TOP_BAND_25_HEIGHT/GATE) instead of _hbar_features_sobel, found
while investigating the Sobel leaf's own robustness (see debugs/
debug_stat_ocr_dp_topband_2v5.py and known_issues.txt/decisions.txt for the
corpus derivation).

UPDATE #2 (2026-07-11, same day, follow-up): normalization was removed
from this engine ENTIRELY -- no padding, no cropping, no resize, no fixed
canvas of any kind (gfl2/stat_ocr_dp.py's own NORMALIZATION docstring
note). Every gate this script probes (TOP_BAND_4, now proportional via
p0/p1 instead of an absolute canvas row range; TOP_BAND_7; TOP_BAND_25)
and the '0'/'6'/'9' centroids (now this engine's own, via gfl2/
calibration/calibrate_dp.py, not reused from gfl2/stat_ocr_fft.py) were
recalibrated on the corpus's raw, un-normalized crops -- every margin
widened as a result. This script's perturbation harness now feeds
classify() the raw crop directly (no _pad_height_only step, which no
longer exists); its _explain() trace and imports have been updated to
match. The FINDINGS in this file's original module docstring above
describe the SUPERSEDED Sobel-based leaf and are kept for historical
context, not current behavior.

UPDATE #3 (2026-07-11, same day, later follow-up): the paren_close
cross-correlation gate this script's _explain() previously mirrored
(TOP_BAND_25/PAREN_CLOSE_3_GATE) has ALSO been superseded -- the {2,3,5}
leaf now uses spread_x (same reflex_pts already computed for spread_y,
just its x-axis extent -- '5' min=5.0, {2,3} max=4.0) to gate '5',
confirmed by a top-band ink count, then a BOTTOM-anchored ink count
('2' min=11, '3' max=9) to split the remainder. No paren/loop template
correlation anywhere in this leaf now -- see gfl2/stat_ocr_dp.py's own
module docstring TREE section and docs/decisions.txt for the corpus
investigation. _explain()/_explain_lines() have been updated to match;
this script's own robustness-sweep FINDINGS (the '2'/'5' leaf dominating
remaining perturbation failures, known_issues.txt §31) were measured
against the Sobel-based leaf and have not been re-run against this one.

Usage:
    python debugs/debug_stat_ocr_dp_5_vs_7_robustness.py
    python debugs/debug_stat_ocr_dp_5_vs_7_robustness.py --images "single/*.png" --max-failures 10
"""
from __future__ import annotations
import argparse, glob as _glob, json, sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from gfl2.stat_ocr import (
    _binarize, _find_blobs, _filter_y_outliers, _find_percent_x_start,
    _collect_cells, _count_inner_blobs, _load_tess_gt_cache, DOT_MAX_DIM,
)
from gfl2.stat_ocr_fft import _parse_panel_row
from gfl2.stat_ocr_dp import (
    StatOcrDp, classify, _pct_strip_bottom,
    _isoperimetric_ratio, ISO_GATE_LO, ISO_GATE_HI,
    _band_count, _bottom_band_count, _band_count_proportional,
    TOP_BAND_4_P0, TOP_BAND_4_P1, TOP_BAND_4_GATE,
    _reflex_vertices, _spread_y, _spread_x, SPREAD_Y_THRESHOLD,
    TOP_BAND_7_HEIGHT, TOP_BAND_7_GATE,
    SPREAD_X_5_GATE, TOP_BAND_5_HEIGHT, TOP_BAND_5_GATE,
    BOTTOM_BAND_23_HEIGHT, BOTTOM_BAND_23_GATE,
)

NONCIRCULAR_DIGITS = set("1234567") - {"6"}  # {1,2,3,4,5,7}

# Perturbation sweep, in a fixed, increasing-severity order. Each entry is
# (kind, param, description). "scale" resizes the tight crop by a factor
# before re-binarizing; "morph" dilates(+)/erodes(-) it with a 3x3 kernel,
# simulating a different font weight at the same overall extent.
_SCALE_FACTORS = [0.80, 0.85, 0.90, 0.95, 1.05, 1.10, 1.15, 1.20]
_MORPH_ITERS = [-2, -1, 1, 2]
PERTURBATIONS = (
    [("scale", s, f"scale x{s:.2f}") for s in _SCALE_FACTORS]
    + [("morph", k, f"{'dilate' if k > 0 else 'erode'} x{abs(k)}") for k in _MORPH_ITERS]
)


def _extract_pct_digit_crops(cell: np.ndarray, pct_label: str):
    """Same matching contract as gfl2.stat_ocr_dp._extract_pct_digit_glyphs,
    but returns the RAW tight binary crop (pre-pad) instead of the padded
    12x20 canvas, so perturbations can be applied before padding."""
    if not pct_label:
        return None
    expected = [c for c in pct_label if c.isdigit()]
    if not expected:
        return None
    ch = cell.shape[0]
    pct_strip = cell[: _pct_strip_bottom(ch), :]
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
    out = []
    for (x, y, w, h), label in zip(digit_blobs, expected):
        crop = thresh[y: y + h, x: x + w]
        if crop.size == 0:
            return None
        out.append((crop, label))
    return out


def _perturb(crop: np.ndarray, kind: str, param) -> "np.ndarray | None":
    if kind == "scale":
        h, w = crop.shape[:2]
        nh, nw = max(1, round(h * param)), max(1, round(w * param))
        resized = cv2.resize(crop, (nw, nh), interpolation=cv2.INTER_LINEAR)
        _, out = cv2.threshold(resized, 127, 255, cv2.THRESH_BINARY)
        return out
    if kind == "morph":
        kernel = np.ones((3, 3), np.uint8)
        if param > 0:
            return cv2.dilate(crop, kernel, iterations=param)
        return cv2.erode(crop, kernel, iterations=-param)
    raise ValueError(kind)


def _explain(norm: np.ndarray) -> dict:
    """Recompute every intermediate value classify() itself uses, for
    display -- does not re-derive the decision logic (that's classify()'s
    own job), just exposes the numbers behind whichever path was taken."""
    iso = _isoperimetric_ratio(norm)
    d = {"iso": iso, "iso_circular": ISO_GATE_LO <= iso <= ISO_GATE_HI}
    if d["iso_circular"]:
        d["holes"] = _count_inner_blobs(norm)
        return d
    band4 = _band_count_proportional(norm, TOP_BAND_4_P0, TOP_BAND_4_P1)
    d["band4"] = band4
    d["band4_gate"] = TOP_BAND_4_GATE
    d["is_4"] = band4 >= TOP_BAND_4_GATE
    if d["is_4"]:
        return d
    reflex_pts, _ = _reflex_vertices(norm)
    sy = _spread_y(reflex_pts)
    d["spread_y"] = sy
    d["spread_y_threshold"] = SPREAD_Y_THRESHOLD
    if sy <= SPREAD_Y_THRESHOLD:
        band7 = _band_count(norm, 0, TOP_BAND_7_HEIGHT)
        d["band7"] = band7
        d["band7_gate"] = TOP_BAND_7_GATE
        d["bucket"] = "{1,7}"
    else:
        sx = _spread_x(reflex_pts)
        d["spread_x"] = sx
        d["spread_x_5_gate"] = SPREAD_X_5_GATE
        d["bucket"] = "{2,3,5}"
        if sx >= SPREAD_X_5_GATE:
            top5 = _band_count(norm, 0, TOP_BAND_5_HEIGHT)
            d["top5"] = top5
            d["top5_gate"] = TOP_BAND_5_GATE
        else:
            bottom23 = _bottom_band_count(norm, BOTTOM_BAND_23_HEIGHT)
            d["bottom23"] = bottom23
            d["bottom23_gate"] = BOTTOM_BAND_23_GATE
    return d


def run(image_paths, max_failures=10):
    engine = StatOcrDp.load()
    gt_cache = _load_tess_gt_cache() or {}
    gt_file = Path("stat_gt_overrides.json")
    gt_overrides = json.loads(gt_file.read_text(encoding="utf-8")) if gt_file.exists() else {}

    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and "pct" in ov:
            item["pct"] = ov["pct"]

    failures = []       # every misclassification found (any digit) -- full transparency
    relevant = []        # subset tagged FN_5/FP_5/FN_7/FP_7 -- this is what we're stopping on
    checked = 0
    baseline_mismatches = 0
    for item in samples:
        crops = _extract_pct_digit_crops(item["cell"], item.get("pct") or "")
        if crops is None:
            continue
        panel, row = _parse_panel_row(item["source"])
        for digit_idx, (crop, label) in enumerate(crops):
            if label not in NONCIRCULAR_DIGITS:
                continue
            base_pred = classify(crop, engine._circular_centroids)
            checked += 1
            if base_pred != label:
                baseline_mismatches += 1
                continue  # not a clean baseline glyph -- skip, don't blame perturbation

            for kind, param, desc in PERTURBATIONS:
                pert_crop = _perturb(crop, kind, param)
                if pert_crop is None or pert_crop.size == 0:
                    continue
                pred = classify(pert_crop, engine._circular_centroids)
                if pred == label:
                    continue
                kinds = []
                if label == "5" or pred == "5":
                    kinds.append("FN_5" if label == "5" else "FP_5")
                if label == "7" or pred == "7":
                    kinds.append("FN_7" if label == "7" else "FP_7")
                if not kinds:
                    kinds.append(f"{label}->{pred}")
                rec = {
                    "source": item["source"], "panel": panel, "row": row,
                    "digit_index": digit_idx + 1, "n_digits": len(crops),
                    "true": label, "pred": pred,
                    "perturbation": desc, "kind_tags": kinds,
                    "clean_crop": crop, "clean_norm": crop,
                    "pert_crop": pert_crop, "pert_norm": pert_crop,
                    "explain": _explain(pert_crop),
                }
                failures.append(rec)
                is_relevant = any(k.endswith("_5") or k.endswith("_7") for k in kinds)
                if is_relevant:
                    relevant.append(rec)
                tag = "*" if is_relevant else " "
                print(f" {tag}[{len(relevant)}/{max_failures} relevant, {len(failures)} total] "
                      f"{item['source']} digit#{digit_idx + 1} true={label!r} "
                      f"pert={desc!r} -> pred={pred!r}  {kinds}")
                if len(relevant) >= max_failures:
                    print(f"\nStopped: {max_failures} 5/7-relevant failures reached "
                          f"({checked} clean baseline glyphs checked, "
                          f"{baseline_mismatches} baseline mismatches skipped, "
                          f"{len(failures)} total misclassifications seen).")
                    return relevant, failures
    print(f"\nExhausted corpus: {len(relevant)} relevant / {len(failures)} total failures found "
          f"({checked} clean baseline glyphs checked, "
          f"{baseline_mismatches} baseline mismatches skipped).")
    return relevant, failures


# ── Debug table rendering ───────────────────────────────────────────────────
_CELL_W, _CELL_H = 140, 220
_ROW_H = _CELL_H + 30
_LABEL_H = 40
_MARGIN = 12


def _to_bgr(img: np.ndarray) -> np.ndarray:
    return img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def _fit_paste(canvas: np.ndarray, img: np.ndarray, x0: int, y0: int, w: int, h: int) -> None:
    img = _to_bgr(img)
    ih, iw = img.shape[:2]
    scale = min(w / iw, h / ih)
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_NEAREST)
    ox, oy = x0 + (w - nw) // 2, y0 + (h - nh) // 2
    canvas[oy: oy + nh, ox: ox + nw] = resized


def _put_lines(canvas, lines, x, y, line_h=16, color=(230, 230, 230), scale=0.4):
    for i, line in enumerate(lines):
        cv2.putText(canvas, line, (x, y + i * line_h), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, color, 1, cv2.LINE_AA)


def _explain_lines(d: dict) -> list:
    lines = [f"iso={d['iso']:.3f} ({'circ' if d['iso_circular'] else 'noncirc'})"]
    if d["iso_circular"]:
        lines.append(f"holes={d.get('holes')}")
        return lines
    lines.append(f"band4={d['band4']} vs {d['band4_gate']:.1f} -> is4={d['is_4']}")
    if d["is_4"]:
        return lines
    lines.append(f"spread_y={d['spread_y']:.1f} vs {d['spread_y_threshold']:.1f} -> {d['bucket']}")
    if d["bucket"] == "{1,7}":
        lines.append(f"band7={d.get('band7')} vs {d.get('band7_gate', 0):.1f}")
    else:
        lines.append(f"spread_x={d.get('spread_x', float('nan')):.1f} vs {d.get('spread_x_5_gate', 0):.1f}")
        if "top5" in d:
            lines.append(f"top5(h={TOP_BAND_5_HEIGHT})={d['top5']} vs {d['top5_gate']:.1f}")
        if "bottom23" in d:
            lines.append(f"bottom23(h={BOTTOM_BAND_23_HEIGHT})={d['bottom23']} vs {d['bottom23_gate']:.1f}")
    return lines


def render_table(failures: list, out_path: Path) -> None:
    n = len(failures)
    if n == 0:
        print("No failures to render.")
        return
    col_w = [90, _CELL_W, _CELL_W, 260]
    headers = ["info", "clean", "perturbed", "trace"]
    width = sum(col_w) + _MARGIN * (len(col_w) + 1)
    height = _LABEL_H + n * _ROW_H + _MARGIN
    canvas = np.full((height, width, 3), 30, dtype=np.uint8)

    x = _MARGIN
    for w, h in zip(col_w, headers):
        cv2.putText(canvas, h, (x + 4, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        x += w + _MARGIN

    for i, rec in enumerate(failures):
        y0 = _LABEL_H + i * _ROW_H
        x = _MARGIN
        info_lines = [
            f"#{i+1} {rec['source']}", f"p{rec['panel']}/{rec['row']} d#{rec['digit_index']}",
            f"true={rec['true']} pred={rec['pred']}", rec["perturbation"], ",".join(rec["kind_tags"]),
        ]
        _put_lines(canvas, info_lines, x + 2, y0 + 14, line_h=14, scale=0.38)
        x += col_w[0] + _MARGIN

        _fit_paste(canvas, rec["clean_norm"], x, y0, col_w[1], _CELL_H - 10)
        x += col_w[1] + _MARGIN

        _fit_paste(canvas, rec["pert_norm"], x, y0, col_w[2], _CELL_H - 10)
        x += col_w[2] + _MARGIN

        trace_lines = _explain_lines(rec["explain"])
        _put_lines(canvas, trace_lines, x + 2, y0 + 14, line_h=16, scale=0.4)

        cv2.line(canvas, (_MARGIN, y0 + _ROW_H - 8), (width - _MARGIN, y0 + _ROW_H - 8), (70, 70, 70), 1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas)
    print(f"Wrote {out_path}  ({n} rows)")


def write_manifest(failures: list, out_path: Path) -> None:
    manifest = [
        {
            "row": i + 1, "source": rec["source"], "panel": rec["panel"], "panel_row": rec["row"],
            "digit_index": rec["digit_index"], "n_digits": rec["n_digits"],
            "true": rec["true"], "pred": rec["pred"], "perturbation": rec["perturbation"],
            "kind_tags": rec["kind_tags"],
            "explain": {k: (round(v, 4) if isinstance(v, float) else v)
                        for k, v in rec["explain"].items()},
        }
        for i, rec in enumerate(failures)
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    ap.add_argument("--max-failures", type=int, default=10)
    ap.add_argument("--out", default="tests/outputs/daily/stat_ocr_dp_5_vs_7_robustness")
    args = ap.parse_args(argv)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images) if "debug" not in Path(p).stem)
    if not image_paths:
        print(f"No images matched: {args.images}", file=sys.stderr)
        sys.exit(1)
    print(f"Images: {len(image_paths)}")

    relevant, all_failures = run(image_paths, max_failures=args.max_failures)

    tags_seen = {}
    for f in all_failures:
        for t in f["kind_tags"]:
            tags_seen[t] = tags_seen.get(t, 0) + 1
    print("\nFailure kind breakdown (ALL misclassifications seen, not just 5/7-relevant):", tags_seen)

    render_table(relevant, Path(args.out + ".png"))
    write_manifest(relevant, Path(args.out + ".json"))


if __name__ == "__main__":
    main()
