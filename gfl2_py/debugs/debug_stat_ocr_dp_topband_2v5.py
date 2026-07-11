# -*- coding: utf-8 -*-
"""
debugs/debug_stat_ocr_dp_topband_2v5.py

Tests whether a CHEAP spatial top-band ink COUNT (cv2.countNonZero over a
fixed row band, no kernel/convolution -- the same mechanism already used
for '4' vs everything (TOP_BAND_4) and '7' vs '1' (TOP_BAND_7) in
gfl2/stat_ocr_dp.py) can REPLACE _hbar_features_sobel's merged-kernel
Sobel-90 convolution for the one remaining leaf that still needs it: '2'
vs '5' inside the {2,3,5} bucket, after '3' is already gated out via
paren_close.

MOTIVATION: the Sobel feature is the ONLY frequency-domain-derived
computation left in this engine (module docstring: "not FFT-major rather
than FFT-free"); every other pipeline that used to justify paying for an
FFT/Gabor/Sobel machinery elsewhere in this exploration has since been
replaced by cheaper spatial primitives (isoperimetric ratio, reflex-vertex
spread, top-band counts). This leaf is the last holdout, and
known_issues.txt §30 already flagged (without pursuing it) that a top-band
count "gets close" for {2,5} (96.46% recall / 0.93% false-trigger) but
wasn't wired in because it fell short of sobel_mean's then-measured 100%.

CALIBRATION (this script, real corpus, Youden's J sweep over row-band
height x threshold, same convention as debugs/calibrate_gabor.py):
height=1 (just the crop's own top row), threshold >= 8 ink pixels -> '5':
    recall=0.9930  false_trigger=0.0000   (863 '5', 1355 '2' glyphs)
i.e. real '2' NEVER reaches 8 ink pixels in its own top row (max=7); 6 of
863 real '5' glyphs fall short of 8 and would misclassify as '2'. This
beats known_issues.txt §30's previously-recorded number outright (0.9930
recall / 0.0000 false-trigger vs 0.9646 / 0.0093) -- likely a different
row-band choice (height=1, not the 3-row band '7' uses).

This script re-runs the FULL classify() tree with ONLY this one leaf
swapped (top-band count instead of sobel_mean) over every real corpus
glyph truly labelled '2', '3', or '5' -- not just the isolated feature in
a vacuum -- so a glyph that gets rerouted by an EARLIER gate (iso, '4',
spread_y, paren_close) shows up as whatever failure that produces, exactly
as it would in the shipped pipeline. Every false positive/negative
touching '5' specifically is rendered to a debug table + JSON manifest.

UPDATE (2026-07-11): this script's own classify_topband() intentionally
still normalizes via _pad_glyph_no_resize (width forced to 12, matching
this investigation's ORIGINAL canvas-relative-vs-ink-relative comparison,
which is what found the height=18 padding-artifact root cause below) --
that comparison is kept exactly as it ran. Production's classify() in
gfl2/stat_ocr_dp.py has SINCE also dropped width-forcing entirely
(_pad_height_only, native width) once the same ink-relative anchoring
principle was found to generalize -- see that module's own NORMALIZATION
note. The root cause and fix described in this file remain valid; they
were simply superseded by a broader fix one level up the same day.

Usage:
    python debugs/debug_stat_ocr_dp_topband_2v5.py --images "single/*.png"
"""
from __future__ import annotations
import argparse, glob as _glob, json, sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from gfl2.stat_ocr import (
    _collect_cells, _count_inner_blobs, _load_tess_gt_cache,
    NORM_W_PCT, NORM_H_PCT,
)
from gfl2.stat_ocr_fft import _parse_panel_row
from gfl2.stat_ocr_dp import (
    StatOcrDp,
    _isoperimetric_ratio, ISO_GATE_LO, ISO_GATE_HI,
    _band_count, _reflex_vertices, _spread_y, SPREAD_Y_THRESHOLD,
    _paren_features,
)
from debugs.debug_stat_ocr_dp_5_vs_7_robustness import (
    _extract_pct_digit_crops, _to_bgr, _fit_paste, _put_lines,
)

# HISTORICAL SNAPSHOT (2026-07-11): this script investigates the ORIGINAL
# canvas-relative-vs-ink-relative comparison for the '2'/'5' leaf, on the
# width-forced-to-12, height-padded representation THAT WAS THEN CURRENT.
# Production (gfl2/stat_ocr_dp.py) has since dropped ALL normalization
# (see that module's own NORMALIZATION note) and moved TOP_BAND_4/
# PAREN_CLOSE_3_GATE to its own live-calibrated values -- neither is
# imported from there anymore so this snapshot keeps reproducing exactly
# the comparison it originally ran, unaffected by later recalibration.
_PAD_GLYPH_NO_RESIZE_TOP_BAND_4_Y0 = 11
_PAD_GLYPH_NO_RESIZE_TOP_BAND_4_Y1 = 17
_PAD_GLYPH_NO_RESIZE_TOP_BAND_4_GATE = 52.5
_PAD_GLYPH_NO_RESIZE_PAREN_CLOSE_3_GATE = 0.228
TOP_BAND_4_Y0, TOP_BAND_4_Y1 = _PAD_GLYPH_NO_RESIZE_TOP_BAND_4_Y0, _PAD_GLYPH_NO_RESIZE_TOP_BAND_4_Y1
TOP_BAND_4_GATE = _PAD_GLYPH_NO_RESIZE_TOP_BAND_4_GATE
PAREN_CLOSE_3_GATE = _PAD_GLYPH_NO_RESIZE_PAREN_CLOSE_3_GATE


def _pad_glyph_no_resize(crop: np.ndarray, norm_w: int, norm_h: int) -> np.ndarray:
    """Local copy of the now-removed gfl2.stat_ocr_dp function, kept here
    so this historical snapshot reproduces exactly what it originally ran
    against, independent of production's later normalization removal."""
    canvas = np.zeros((norm_h, norm_w), dtype=crop.dtype)
    ch, cw = crop.shape[:2]
    if ch == 0 or cw == 0:
        return canvas
    sy0 = max(0, (ch - norm_h) // 2)
    sx0 = max(0, (cw - norm_w) // 2)
    src = crop[sy0: sy0 + norm_h, sx0: sx0 + norm_w]
    sh, sw = src.shape[:2]
    dy0 = (norm_h - sh) // 2
    dx0 = (norm_w - sw) // 2
    canvas[dy0: dy0 + sh, dx0: dx0 + sw] = src
    return canvas


# ── Candidate replacement for _hbar_features_sobel at the '2'/'5' leaf ──────
# Calibrated above: real corpus gap -- '2' max=7, '5' has 6/863 below 8.
TOP_BAND_25_HEIGHT = 1
TOP_BAND_25_GATE = 8.0


def classify_topband(norm: np.ndarray, circular_centroids: dict) -> "tuple[str, dict]":
    """Exact copy of gfl2.stat_ocr_dp.classify()'s tree, with ONLY the
    final '2'/'5' decision swapped from _hbar_features_sobel to a plain
    top-band ink count -- every other gate/leaf is untouched, byte-for-
    byte identical logic. Returns (prediction, trace-dict) so a caller can
    see exactly which path was taken without re-deriving it."""
    trace = {}
    iso = _isoperimetric_ratio(norm)
    trace["iso"] = iso
    if ISO_GATE_LO <= iso <= ISO_GATE_HI:
        holes = _count_inner_blobs(norm)
        trace["holes"] = holes
        if holes >= 2:
            return '8', trace
        if holes == 1:
            combined = np.concatenate([_paren_features(norm), _loop_features_local(norm)])
            best_d, best_dist = None, None
            for d, centroid in circular_centroids.items():
                dist = float(np.linalg.norm(combined - centroid))
                if best_dist is None or dist < best_dist:
                    best_d, best_dist = d, dist
            return (best_d if best_d is not None else '?'), trace
        return '?', trace

    band4 = _band_count(norm, TOP_BAND_4_Y0, TOP_BAND_4_Y1)
    trace["band4"] = band4
    if band4 >= TOP_BAND_4_GATE:
        return '4', trace

    reflex_pts, _ = _reflex_vertices(norm)
    sy = _spread_y(reflex_pts)
    trace["spread_y"] = sy
    if sy <= SPREAD_Y_THRESHOLD:
        top7 = _band_count(norm, 0, 3)
        trace["band7"] = top7
        return ('7' if top7 >= 21.5 else '1'), trace

    paren_close = _paren_features(norm)[1]
    trace["paren_close"] = float(paren_close)
    if paren_close > PAREN_CLOSE_3_GATE:
        return '3', trace

    band25 = _band_count(norm, 0, TOP_BAND_25_HEIGHT)
    trace["band25"] = band25
    trace["band25_gate"] = TOP_BAND_25_GATE
    return ('5' if band25 >= TOP_BAND_25_GATE else '2'), trace


def _loop_features_local(gray_norm: np.ndarray) -> np.ndarray:
    from gfl2.stat_ocr_dp import _loop_features
    return _loop_features(gray_norm)


def run(image_paths):
    engine = StatOcrDp.load()
    gt_cache = _load_tess_gt_cache() or {}
    gt_file = Path("stat_gt_overrides.json")
    gt_overrides = json.loads(gt_file.read_text(encoding="utf-8")) if gt_file.exists() else {}

    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and "pct" in ov:
            item["pct"] = ov["pct"]

    totals = {"2": [0, 0], "3": [0, 0], "5": [0, 0]}  # [classified, correct]
    failures_5 = []  # any misclassification where true=='5' or pred=='5'
    all_25_failures = []

    for item in samples:
        crops = _extract_pct_digit_crops(item["cell"], item.get("pct") or "")
        if crops is None:
            continue
        panel, row = _parse_panel_row(item["source"])
        for digit_idx, (crop, label) in enumerate(crops):
            if label not in ("2", "3", "5"):
                continue
            norm = _pad_glyph_no_resize(crop, NORM_W_PCT, NORM_H_PCT)
            pred, trace = classify_topband(norm, engine._circular_centroids)
            totals[label][0] += 1
            if pred == label:
                totals[label][1] += 1
                continue
            all_25_failures.append((item["source"], digit_idx, label, pred))
            if label == "5" or pred == "5":
                failures_5.append({
                    "source": item["source"], "panel": panel, "row": row,
                    "digit_index": digit_idx + 1, "n_digits": len(crops),
                    "true": label, "pred": pred,
                    "kind": "FN_5" if label == "5" else "FP_5",
                    "crop": crop, "norm": norm, "trace": trace,
                })

    print("Per-digit accuracy with top-band 2/5 leaf swapped in:")
    for d in ("2", "3", "5"):
        c, k = totals[d]
        print(f"  '{d}': {k}/{c} correct ({100*k/c:.2f}%)" if c else f"  '{d}': 0 samples")
    print(f"\nAll {{2,3,5}} misclassifications (any direction): {len(all_25_failures)}")
    for src, idx, t, p in all_25_failures:
        print(f"    {src} digit#{idx+1} true={t!r} pred={p!r}")
    print(f"\n'5'-relevant failures (FN_5 or FP_5): {len(failures_5)}")
    return failures_5


# ── Debug table rendering ───────────────────────────────────────────────────
_CELL_W, _CELL_H = 160, 220
_ROW_H = _CELL_H + 30
_LABEL_H = 40
_MARGIN = 12


def _trace_lines(trace: dict) -> list:
    lines = [f"iso={trace['iso']:.3f}"]
    if "holes" in trace:
        lines.append(f"-> circular, holes={trace['holes']}")
        return lines
    lines.append(f"band4={trace['band4']} vs {TOP_BAND_4_GATE}")
    if "spread_y" not in trace and "band25" not in trace and "paren_close" not in trace:
        lines.append("-> '4'")
        return lines
    if "spread_y" in trace:
        lines.append(f"spread_y={trace['spread_y']:.1f} vs {SPREAD_Y_THRESHOLD}")
        if "band7" in trace:
            lines.append(f"-> {{1,7}}: band7={trace['band7']} vs 21.5")
            return lines
    if "paren_close" in trace:
        lines.append(f"paren_close={trace['paren_close']:.3f} vs {PAREN_CLOSE_3_GATE}")
        if "band25" in trace:
            lines.append(f"-> band25(h={TOP_BAND_25_HEIGHT})={trace['band25']} "
                         f"vs {trace['band25_gate']}")
    return lines


def render_table(failures: list, out_path: Path) -> None:
    n = len(failures)
    if n == 0:
        print("No '5'-relevant failures to render.")
        return
    col_w = [110, _CELL_W, 260]
    headers = ["info", "glyph", "trace"]
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
            f"true={rec['true']} pred={rec['pred']}", rec["kind"],
        ]
        _put_lines(canvas, info_lines, x + 2, y0 + 14, line_h=14, scale=0.38)
        x += col_w[0] + _MARGIN

        _fit_paste(canvas, rec["norm"], x, y0, col_w[1], _CELL_H - 10)
        # mark the top band on the pasted glyph region for visual reference
        x += col_w[1] + _MARGIN

        trace_lines = _trace_lines(rec["trace"])
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
            "true": rec["true"], "pred": rec["pred"], "kind": rec["kind"],
            "trace": {k: (round(v, 4) if isinstance(v, float) else v)
                      for k, v in rec["trace"].items()},
        }
        for i, rec in enumerate(failures)
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    ap.add_argument("--out", default="tests/outputs/daily/stat_ocr_dp_topband_2v5")
    args = ap.parse_args(argv)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images) if "debug" not in Path(p).stem)
    if not image_paths:
        print(f"No images matched: {args.images}", file=sys.stderr)
        sys.exit(1)
    print(f"Images: {len(image_paths)}")

    failures_5 = run(image_paths)
    render_table(failures_5, Path(args.out + ".png"))
    write_manifest(failures_5, Path(args.out + ".json"))


if __name__ == "__main__":
    main()
