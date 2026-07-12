# -*- coding: utf-8 -*-
"""
debugs/debug_outlier_cell_compare.py -- side-by-side whole-CELL debug crop
comparing a flagged problem cell against a normal cell from the SAME
source image, for investigating a candidate
structural/rendering outlier (fb_d_20260315_p1_r3_col1).

WHY THIS EXISTS: every other debug tool in this project works at the
GLYPH level (one digit, normalized to 12x20) -- the right grain for
classifier feature debugging, but too small to see whole-cell context
like relative ink darkness or binarization behavior across an entire pct
line.  This tool stays at the RAW CELL level: full-resolution crop,
grayscale, and binarized pct/val strips with digit blob boxes drawn, for
both cells side by side at a shared visual scale -- so a human can
directly compare "does this cell's ink/contrast/binarization look
different from a normal cell in the exact same screenshot."

Usage:
    python debugs/debug_outlier_cell_compare.py
    python debugs/debug_outlier_cell_compare.py \
        --problem fb_d_20260315_p1_r3_col1 --normal fb_d_20260315_p1_r2_col1
"""
from __future__ import annotations
import sys
import argparse
from pathlib import Path
import json
import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import (
    PCT_STRIP_Y, VAL_STRIP_Y, DOT_MAX_DIM,
    _binarize, _find_blobs, _filter_y_outliers, _find_percent_x_start,
    _collect_cells, _load_tess_gt_cache,
)
from gfl2.stat_ocr_fft import _pct_strip_bottom

DEFAULT_PROBLEM = "fb_d_20260315_p1_r3_col1"
DEFAULT_NORMAL = "fb_d_20260315_p1_r2_col1"
_GT_FILE = _ROOT / "tests" / "inputs" / "daily" / "stat_gt_overrides.json"

UPSCALE = 6
CELL_W, CELL_H = 260, 220
LABEL_W = 190
HEADER_H = 40
CAPTION_H = 18


def _gt_pct(source: str, raw_pct: str, overrides: dict) -> str:
    ov = overrides.get(source)
    return ov["pct"] if ov and "pct" in ov else (raw_pct or "")


def _digit_blobs(strip_thresh: np.ndarray) -> list:
    blobs = _filter_y_outliers(_find_blobs(strip_thresh), threshold=12)
    sorted_x = sorted(blobs, key=lambda b: b[0])
    pct_x = _find_percent_x_start(sorted_x)
    return [
        (x, y, w, h) for (x, y, w, h) in sorted_x
        if (pct_x is None or x < pct_x)
        and not (w <= DOT_MAX_DIM and h <= DOT_MAX_DIM)
    ]


def _to_bgr(img: np.ndarray) -> np.ndarray:
    return img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def _fit_and_paste(canvas, img_bgr, x0, y0, w, h) -> None:
    ih, iw = img_bgr.shape[:2]
    scale = min(w / iw, h / ih)
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    resized = cv2.resize(img_bgr, (nw, nh), interpolation=cv2.INTER_NEAREST)
    ox, oy = x0 + (w - nw) // 2, y0 + (h - nh) // 2
    canvas[oy: oy + nh, ox: ox + nw] = resized


def _draw_blob_boxes(img_bgr: np.ndarray, blobs: list, color=(0, 0, 255)) -> np.ndarray:
    out = img_bgr.copy()
    for (x, y, w, h) in blobs:
        cv2.rectangle(out, (x, y), (x + w - 1, y + h - 1), color, 1)
    return out


def _put_caption(canvas, text, x0, y0, w, color=(30, 30, 30)) -> None:
    if not text:
        return
    cv2.putText(canvas, text, (x0 + 4, y0 - 4), cv2.FONT_HERSHEY_SIMPLEX,
                0.36, color, 1, cv2.LINE_AA)


def _row_data(source: str, samples_by_source: dict, overrides: dict) -> dict:
    s = samples_by_source.get(source)
    if s is None:
        sys.exit(f"Source not found in corpus: {source}")
    cell = s["cell"]
    ch = cell.shape[0]
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY) if cell.ndim == 3 else cell

    pct_bottom = _pct_strip_bottom(ch)
    pct_strip_gray = gray[:pct_bottom, :]
    pct_thresh = _binarize(cell[:pct_bottom, :])
    pct_blobs = _digit_blobs(pct_thresh)

    val_y0 = int(ch * VAL_STRIP_Y[0])
    val_y1 = int(ch * VAL_STRIP_Y[1])
    val_strip_gray = gray[val_y0:val_y1, :]
    val_thresh = _binarize(cell[val_y0:val_y1, :])
    val_blobs = _filter_y_outliers(_find_blobs(val_thresh), threshold=8)
    val_blobs = sorted(val_blobs, key=lambda b: b[0])

    gt_pct = _gt_pct(source, s["pct"], overrides)

    return {
        "source": source,
        "cell": cell,
        "gray_min": int(pct_strip_gray.min()) if pct_strip_gray.size else -1,
        "gray_max": int(pct_strip_gray.max()) if pct_strip_gray.size else -1,
        "pct_gray": pct_strip_gray,
        "pct_thresh": pct_thresh,
        "pct_blobs": pct_blobs,
        "val_gray": val_strip_gray,
        "val_thresh": val_thresh,
        "val_blobs": val_blobs,
        "gt_pct": gt_pct,
        "gt_val": s["val"],
    }


COLUMNS = ["raw_cell", "grayscale", "pct_strip (binarized + blobs)", "val_strip (binarized + blobs)"]


def build_comparison(problem: dict, normal: dict) -> np.ndarray:
    n_cols = len(COLUMNS)
    n_rows = 2
    W = LABEL_W + n_cols * CELL_W
    H = HEADER_H + n_rows * CELL_H
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)

    for j, name in enumerate(COLUMNS):
        x0 = LABEL_W + j * CELL_W
        cv2.putText(canvas, name, (x0 + 4, HEADER_H - 14), cv2.FONT_HERSHEY_SIMPLEX,
                    0.42, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (x0, 0), (x0, H), (210, 210, 210), 1)
    cv2.line(canvas, (0, HEADER_H), (W, HEADER_H), (150, 150, 150), 1)

    for i, (row, tag, color) in enumerate([(problem, "PROBLEM", (0, 0, 200)),
                                            (normal, "NORMAL (longest)", (0, 140, 0))]):
        y0 = HEADER_H + i * CELL_H
        cv2.line(canvas, (0, y0), (W, y0), (210, 210, 210), 1)

        cv2.putText(canvas, tag, (6, y0 + 18), cv2.FONT_HERSHEY_SIMPLEX,
                    0.44, color, 1, cv2.LINE_AA)
        cv2.putText(canvas, row["source"], (6, y0 + 36), cv2.FONT_HERSHEY_SIMPLEX,
                    0.32, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas, f"gt pct={row['gt_pct']!r}", (6, y0 + 52), cv2.FONT_HERSHEY_SIMPLEX,
                    0.32, (80, 80, 80), 1, cv2.LINE_AA)
        cv2.putText(canvas, f"gt val={row['gt_val']!r}", (6, y0 + 68), cv2.FONT_HERSHEY_SIMPLEX,
                    0.32, (80, 80, 80), 1, cv2.LINE_AA)
        cv2.putText(canvas, f"pct-strip gray:", (6, y0 + 88), cv2.FONT_HERSHEY_SIMPLEX,
                    0.32, (80, 80, 80), 1, cv2.LINE_AA)
        cv2.putText(canvas, f"  min={row['gray_min']} max={row['gray_max']}", (6, y0 + 104),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, (80, 80, 80), 1, cv2.LINE_AA)
        cv2.putText(canvas, f"pct blobs={len(row['pct_blobs'])}", (6, y0 + 124),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, (80, 80, 80), 1, cv2.LINE_AA)
        cv2.putText(canvas, f"val blobs={len(row['val_blobs'])}", (6, y0 + 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, (80, 80, 80), 1, cv2.LINE_AA)

        imgs = [
            _to_bgr(row["cell"]),
            _to_bgr(cv2.cvtColor(row["cell"], cv2.COLOR_BGR2GRAY)
                    if row["cell"].ndim == 3 else row["cell"]),
            _draw_blob_boxes(_to_bgr(row["pct_thresh"]), row["pct_blobs"]),
            _draw_blob_boxes(_to_bgr(row["val_thresh"]), row["val_blobs"]),
        ]
        for j, img in enumerate(imgs):
            x0 = LABEL_W + j * CELL_W
            _fit_and_paste(canvas, img, x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)

    return canvas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--problem", default=DEFAULT_PROBLEM,
                     help=f"source key of the flagged cell  [default: {DEFAULT_PROBLEM}]")
    ap.add_argument("--normal", default=DEFAULT_NORMAL,
                     help=f"source key of the comparison cell  [default: {DEFAULT_NORMAL}]")
    ap.add_argument("--output", default="tests/outputs/daily/outlier_cell_compare.png",
                     help="output path  [default: tests/outputs/daily/ -- gitignored]")
    args = ap.parse_args(argv)

    image_stem = args.problem.split("_p")[0]
    image_paths = sorted(_ROOT.glob(f"single/{image_stem}*.png"))
    if not image_paths:
        sys.exit(f"No images matched single/{image_stem}*.png")

    gt_cache = _load_tess_gt_cache() or {}
    overrides = json.loads(_GT_FILE.read_text()) if _GT_FILE.exists() else {}
    # excluded_cells={}: this tool exists specifically to inspect cells that
    # stat_excluded_cells.json now excludes from build/verify -- bypass that
    # exclusion here rather than getting an empty lookup for the very cell
    # being investigated.
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache, excluded_cells={})
    by_source = {s["source"]: s for s in samples}

    problem = _row_data(args.problem, by_source, overrides)
    normal = _row_data(args.normal, by_source, overrides)

    canvas = build_comparison(problem, normal)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas)
    print(f"Wrote {canvas.shape[1]}x{canvas.shape[0]} -> {out_path}")
    print(f"PROBLEM {args.problem}: pct-strip gray min/max = "
          f"{problem['gray_min']}/{problem['gray_max']}, "
          f"pct_blobs={len(problem['pct_blobs'])}, val_blobs={len(problem['val_blobs'])}")
    print(f"NORMAL  {args.normal}: pct-strip gray min/max = "
          f"{normal['gray_min']}/{normal['gray_max']}, "
          f"pct_blobs={len(normal['pct_blobs'])}, val_blobs={len(normal['val_blobs'])}")


if __name__ == "__main__":
    main()
