# -*- coding: utf-8 -*-
"""
debugs/debug_approx_poly_dp_corpus_failures.py -- per-failing-glyph debug
table for the approx-poly-dp reflex-vertex-count {1,4,7}-vs-{2,3,5} split
that debugs/debug_isoperimetric_hierarchy_check.py found does NOT hold up
at corpus scale (docs/known_issues.txt §29, decisions.txt #73), even
though it separated cleanly on the single-atlas-sample-per-digit probe
(debugs/debug_approx_poly_dp.py: {1,4,7}=1,1,1 reflex vs {2,3,5}=3,2,3
reflex at eps=0.03 -- a clean gap of exactly 1).

CLASSIFIER UNDER TEST: the EXACT threshold that worked on the atlas --
reflex-vertex-count at eps=0.03, predict "line" ({1,4,7}) if reflex<=1,
else "arc" ({2,3,5}) -- re-tested against real corpus glyphs (the actual
classify-time representation, gfl2.stat_ocr_v0_2_0._extract_pct_digit_glyphs's
already-binarized, no-resize-padded 12x20 canvas, not the atlas crop).

Walks the real 87-image corpus (deterministic source order) collecting
the FIRST 10 glyphs where this classifier's predicted group disagrees
with the glyph's true group, then renders one table image with TWO crops
per failure: the real corpus glyph that failed, AND the atlas's own
reference glyph for that same true digit (assets/fonts/glyph_daily_pct.png)
side by side, each with its own binarized crop and contour+polygon overlay
(green=convex vertex, red=reflex vertex, orange=hole contour -- same
convention as debug_approx_poly_dp.py) -- so a real failure's shape can be
visually compared directly against the "textbook" atlas sample of the
same digit.

Companion .json manifest -- one entry per row, same order -- carries the
exact source key (cell id + digit-only index) and both reflex counts, so
a failure can be re-found in the source screenshot without retyping
anything by hand (same convention as gfl2.stat_ocr_v0_2_0.save_verify_glyphs_debug()).

Standalone probe -- nothing here is wired into any classifier.

Usage:
    python debugs/debug_approx_poly_dp_corpus_failures.py
    python debugs/debug_approx_poly_dp_corpus_failures.py --images "single/*.png" --max-failures 10
"""
from __future__ import annotations
import argparse
import glob as _glob
import json
import sys
from pathlib import Path

import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr_v0_1_0 import _collect_cells, _load_tess_gt_cache
from gfl2.stat_ocr_v0_2_0 import _extract_pct_digit_glyphs
from debugs.debug_approx_poly_dp import (
    _find_outer_and_holes, _classify_vertices, _padded_mask,
    _binarize_native, _contour_overlay,
)
from debugs.debug_sobel45_pct_glyphs import (
    _DEFAULT_ATLAS, _DEFAULT_LOOKUP, _load_lookup, load_atlas_glyphs,
    _to_bgr, _fit_and_paste, _put_caption,
)

EPS_FRAC = 0.03          # the atlas's own clean-gap epsilon (docs/known_issues.txt §29)
REFLEX_THRESHOLD = 1.5   # atlas found {1,4,7}=1,1,1 vs {2,3,5}=3,2,3 -- split at the midpoint
LINE_GROUP = {"1", "4", "7"}
ARC_GROUP = {"2", "3", "5"}

_DEFAULT_OUTPUT = _ROOT / "tests" / "outputs" / "daily" / "approx_poly_dp_corpus_failures.png"

CELL_W, CELL_H = 150, 210
LABEL_W = 160
HEADER_H = 44
CAPTION_H = 34


def _reflex_count(bin_glyph: np.ndarray, eps_frac: float = EPS_FRAC):
    """Reflex-vertex count of a glyph's outer contour at `eps_frac` of its
    own arcLength, plus the pieces needed to render the overlay later.
    `bin_glyph` must already be a 0/255 binary crop."""
    padded = _padded_mask(bin_glyph)
    outer, holes = _find_outer_and_holes(padded)
    if outer is None:
        return None, padded, None, None
    perim = cv2.arcLength(outer, True)
    eps = max(eps_frac * perim, 0.5)
    approx = cv2.approxPolyDP(outer, eps, True)
    _, n_reflex = _classify_vertices(approx)
    return n_reflex, padded, outer, (holes, approx)


def predicted_group(n_reflex: "int | None") -> str:
    if n_reflex is None:
        return "none"
    return "line" if n_reflex <= REFLEX_THRESHOLD else "arc"


def true_group(label: str) -> str:
    return "line" if label in LINE_GROUP else "arc"


def build_atlas_reference() -> dict:
    """One reference glyph per digit in LINE_GROUP|ARC_GROUP, from the
    atlas -- binarized the same abs-diff-vs-background way
    debugs/debug_approx_poly_dp.py already established, then run through
    the SAME reflex-count computation as the real corpus glyphs."""
    lookup_all = _load_lookup(Path(_DEFAULT_LOOKUP))
    lookup = lookup_all[Path(_DEFAULT_ATLAS).name]
    glyphs, bg_gray = load_atlas_glyphs(Path(_DEFAULT_ATLAS), lookup)
    ref = {}
    for g in glyphs:
        if g["char"] not in (LINE_GROUP | ARC_GROUP):
            continue
        bin_native = _binarize_native(g["native"], bg_gray)
        n_reflex, padded, outer, extra = _reflex_count(bin_native)
        ref[g["char"]] = {
            "native": g["native"], "bin": bin_native, "n_reflex": n_reflex,
            "padded": padded, "outer": outer, "extra": extra,
        }
    return ref


def find_failures(image_paths: list[Path], max_failures: int) -> list[dict]:
    gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    gt_file = Path("tests/inputs/daily/stat_gt_overrides.json")
    if gt_file.exists():
        gt_overrides = json.loads(gt_file.read_text(encoding="utf-8"))
        for item in samples:
            ov = gt_overrides.get(item["source"])
            if ov and "pct" in ov:
                item["pct"] = ov["pct"]
    samples = sorted(samples, key=lambda it: it["source"])  # deterministic order

    failures = []
    n_checked = 0
    for item in samples:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        digit_idx = -1
        for norm, label in glyphs:
            if label not in (LINE_GROUP | ARC_GROUP):
                continue
            digit_idx += 1
            n_checked += 1
            n_reflex, padded, outer, extra = _reflex_count(norm)
            pred = predicted_group(n_reflex)
            true = true_group(label)
            if pred != true:
                failures.append({
                    "source": item["source"], "digit_index": digit_idx,
                    "true_label": label, "true_group": true, "pred_group": pred,
                    "n_reflex": n_reflex, "norm": norm, "padded": padded,
                    "outer": outer, "extra": extra,
                })
                if len(failures) >= max_failures:
                    print(f"Stopped after checking {n_checked} glyphs -- "
                          f"reached {max_failures} failures.")
                    return failures
    print(f"Checked all {n_checked} glyphs -- only {len(failures)} failure(s) found.")
    return failures


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    ap.add_argument("--max-failures", type=int, default=10)
    ap.add_argument("--output", default=str(_DEFAULT_OUTPUT))
    args = ap.parse_args(argv)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                         if "debug" not in Path(p).stem)
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    print(f"Classifier under test: reflex-vertex-count @ eps={EPS_FRAC}, "
          f"threshold={REFLEX_THRESHOLD} (atlas's own clean-gap split)")
    print("Building atlas reference glyphs ...")
    atlas_ref = build_atlas_reference()
    for d in sorted(atlas_ref):
        r = atlas_ref[d]
        print(f"  atlas '{d}': n_reflex={r['n_reflex']}  "
              f"predicted={predicted_group(r['n_reflex'])}  true={true_group(d)}")

    print(f"\nScanning {len(image_paths)} image(s) for corpus failures ...")
    failures = find_failures(image_paths, args.max_failures)
    if not failures:
        print("No failures found -- nothing to render.")
        return

    manifest = []
    for f in failures:
        manifest.append({
            "source": f["source"], "digit_index": f["digit_index"],
            "true_label": f["true_label"], "true_group": f["true_group"],
            "pred_group": f["pred_group"], "n_reflex": f["n_reflex"],
            "atlas_reflex": atlas_ref[f["true_label"]]["n_reflex"],
        })

    # ── Table image: one row per failure, corpus glyph vs atlas reference ──
    columns = ["corpus native", "corpus binary", "corpus contour+poly",
               "atlas native", "atlas binary", "atlas contour+poly"]
    n_cols = len(columns)
    n_rows = len(failures)
    W = LABEL_W + n_cols * CELL_W
    H = HEADER_H + n_rows * CELL_H
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)

    for j, name in enumerate(columns):
        x0 = LABEL_W + j * CELL_W
        cv2.putText(canvas, name, (x0 + 4, HEADER_H - 14), cv2.FONT_HERSHEY_SIMPLEX,
                    0.42, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (x0, 0), (x0, H), (210, 210, 210), 1)
    cv2.line(canvas, (0, HEADER_H), (W, HEADER_H), (150, 150, 150), 1)
    cv2.putText(canvas, f"classifier: reflex@eps={EPS_FRAC} <= {REFLEX_THRESHOLD} -> line "
                         f"({{1,4,7}}), else arc ({{2,3,5}})  --  green=convex red=reflex "
                         f"orange=hole",
                (LABEL_W + 4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (90, 90, 90), 1, cv2.LINE_AA)

    for i, f in enumerate(failures):
        y0 = HEADER_H + i * CELL_H
        cv2.line(canvas, (0, y0), (W, y0), (210, 210, 210), 1)
        label = (f"{f['source']}\n"
                 f"digit#{f['digit_index']} = '{f['true_label']}'\n"
                 f"true={f['true_group']} pred={f['pred_group']}\n"
                 f"reflex={f['n_reflex']} (atlas='{f['true_label']}'\n"
                 f"reflex={atlas_ref[f['true_label']]['n_reflex']})")
        for k, line in enumerate(label.split("\n")):
            cv2.putText(canvas, line, (6, y0 + 18 + k * 15), cv2.FONT_HERSHEY_SIMPLEX,
                        0.36, (0, 0, 0), 1, cv2.LINE_AA)

        ref = atlas_ref[f["true_label"]]
        corpus_holes, corpus_approx = f["extra"] if f["extra"] else ([], None)
        atlas_holes, atlas_approx = ref["extra"] if ref["extra"] else ([], None)

        cell_imgs = [
            _to_bgr(f["norm"]), _to_bgr(f["norm"]),
            _contour_overlay(f["padded"], f["outer"], corpus_holes, corpus_approx),
            _to_bgr(ref["native"]), _to_bgr(ref["bin"]),
            _contour_overlay(ref["padded"], ref["outer"], atlas_holes, atlas_approx),
        ]
        captions = ["", "", f"n_reflex={f['n_reflex']}",
                    "", "", f"n_reflex={ref['n_reflex']}"]

        for j, (img, cap) in enumerate(zip(cell_imgs, captions)):
            x0 = LABEL_W + j * CELL_W
            _fit_and_paste(canvas, img, x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)
            _put_caption(canvas, cap, x0, y0 + CELL_H, CELL_W)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas)
    print(f"\nWrote {canvas.shape[1]}x{canvas.shape[0]} debug table ({n_rows} failures) -> {out_path}")

    manifest_path = out_path.with_suffix(".json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote manifest -> {manifest_path}")


if __name__ == "__main__":
    main()
