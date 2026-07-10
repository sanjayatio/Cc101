# -*- coding: utf-8 -*-
"""
debugs/debug_approx_poly_dp.py -- probes cv2.approxPolyDP polygon
approximation against assets/fonts/glyph_daily_pct.png's real, native-
resolution digit glyphs, asking whether polygon vertex count (and a
handful of related contour-shape descriptors) can segregate line-dominant
digits ('1', '7') from curve/loop-dominant ones ('0', '2', '5', ...) -- the
intuition being that a polygon fit to a mostly-straight glyph needs far
fewer vertices than one fit to a glyph with real curvature.

PIPELINE:
  1. Re-isolate every glyph from assets/fonts/glyph_daily_pct.png (contour +
     glyph_lookup.py re-derivation, same load_atlas_glyphs() convention as
     debugs/debug_sobel45_pct_glyphs.py / debug_sobel90_pct_glyphs.py --
     imported directly, not re-derived, so this can never silently drift
     from that established atlas-reading contract).
  2. Binarize each NATIVE (unresized, unpadded) glyph crop the same way
     load_atlas_glyphs itself separated it from the atlas background --
     abs-diff against the atlas's own background gray level, threshold at
     20 -- rather than gfl2.stat_ocr._binarize's fixed THRESH_BIN, which
     assumes a specific ink/background polarity that may not match every
     atlas's real background tone.
  3. cv2.findContours(RETR_CCOMP) on each glyph's own small binary mask to
     get the outer contour plus any interior hole contour(s) (same
     hierarchy convention gfl2.stat_ocr._count_inner_blobs already uses),
     computed at NATIVE resolution -- before any resize -- unlike
     production's hole count, which runs on the already-resized 12x20
     classifier input (see docs/known_issues.txt §15 on resize distorting
     small-scale shape features).
  4. Sweep cv2.approxPolyDP epsilon (as a FRACTION of each contour's own
     arcLength, so differently-sized glyphs stay comparable) across several
     values, and report vertex count at each -- so the chosen operating
     epsilon is picked from real swept numbers, not guessed.
  5. From the swept results, compute 5 candidate segregation parameters
     per glyph:
       - n_vertices_outer   : approxPolyDP vertex count on the outer contour
                              at the chosen operating epsilon
       - n_reflex_vertices  : of those vertices, how many are CONCAVE
                              (interior-angle > 180deg) rather than convex
                              -- a straight-stroke digit's polygon should be
                              close to fully convex (0 reflex corners);
                              curved/notched digits should show real reflex
                              corners at each concavity
       - hole_count         : interior contours (RETR_CCOMP), NATIVE
                              resolution, min-area filtered -- same
                              hole-count idea production already uses
                              (§9/§14), but measured before any resize
       - solidity           : contour_area / convex_hull_area of the RAW
                              (un-approximated) outer contour -- how much
                              of the convex hull the real ink actually
                              fills; independent of the approxPolyDP
                              epsilon choice
       - circularity_deficit: arcLength^2 / (4*pi*area) of the raw outer
                              contour -- 1.0 for a perfect circle, higher
                              for elongated/notched/complex boundaries;
                              complements solidity (which measures
                              concavity DEPTH) with overall boundary
                              complexity

CAVEAT: this atlas carries exactly ONE real sample per digit (the
nearest-to-centroid pick debugs/build_glyph_reference.py already made) --
same n=1-per-class caveat as every other atlas-only probe in this project
(docs/known_issues.txt §15's DEBUG TABLE entry, debug_sobel45/90_pct_glyphs.py).
Treat every number below as "does this look promising on one real sample",
not a corpus-validated threshold -- the same escalation path this project
always uses next (calibrate against single/*.png via gfl2.calibration, or
a real classifier ablation) applies here too before trusting any of this
for real.

Standalone probe -- nothing here is wired into any classifier.

Usage:
    python debugs/debug_approx_poly_dp.py
    python debugs/debug_approx_poly_dp.py --atlas assets/fonts/glyph_daily_pct.png
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from debugs.debug_sobel45_pct_glyphs import (
    _DEFAULT_ATLAS, _DEFAULT_LOOKUP, _load_lookup, load_atlas_glyphs,
    _to_bgr, _fit_and_paste, _put_caption,
)

_DEFAULT_OUTPUT = _ROOT / "tests" / "outputs" / "daily" / "approx_poly_dp_pct_glyph_table.png"

# Fraction of the contour's own arcLength -- swept to pick an informed
# operating point rather than a guessed single value.
EPS_FRACS = [0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.18, 0.25]
# The 3 shown as separate visual columns (subset of EPS_FRACS above).
VISUAL_EPS = [0.02, 0.05, 0.12]
MIN_HOLE_AREA = 2.0   # px^2 -- filters 1px binarization-noise "holes" at this native scale

BORDER = 4     # px of background padding around each native glyph before contour work
UPSCALE = 12   # display upscale -- native crops are tiny (a handful of px wide)
CELL_W, CELL_H = 150, 210
LABEL_W = 90
HEADER_H = 44
CAPTION_H = 34


# ── Per-glyph binarization + contour extraction ──────────────────────────────

def _binarize_native(native_gray: np.ndarray, bg_gray: int) -> np.ndarray:
    """Same abs-diff-against-atlas-background + threshold=20 convention
    load_atlas_glyphs() already used to separate this glyph from the atlas
    in the first place -- reused here rather than gfl2.stat_ocr._binarize's
    fixed THRESH_BIN, which assumes a specific ink/background polarity that
    may not hold for every atlas's real background tone."""
    diff = cv2.absdiff(native_gray, np.full_like(native_gray, bg_gray))
    _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
    return thresh


def _padded_mask(bin_native: np.ndarray, border: int = BORDER) -> np.ndarray:
    """Pad with real background (0) on all sides so a glyph's ink touching
    its own tight bounding box doesn't produce a contour clipped by the
    image edge."""
    return cv2.copyMakeBorder(bin_native, border, border, border, border,
                               cv2.BORDER_CONSTANT, value=0)


def _find_outer_and_holes(padded_mask: np.ndarray) -> tuple["np.ndarray | None", list[np.ndarray]]:
    """RETR_CCOMP hierarchy -> (largest outer contour, [hole contours]),
    same "hierarchy[i][3] >= 0 means hole" convention as
    gfl2.stat_ocr._count_inner_blobs, computed at NATIVE resolution."""
    cnts, hierarchy = cv2.findContours(padded_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    if not cnts or hierarchy is None:
        return None, []
    outers = [(i, c) for i, c in enumerate(cnts) if hierarchy[0][i][3] < 0]
    if not outers:
        return None, []
    outer_i, outer = max(outers, key=lambda t: cv2.contourArea(t[1]))
    holes = [c for i, c in enumerate(cnts)
             if hierarchy[0][i][3] == outer_i and cv2.contourArea(c) >= MIN_HOLE_AREA]
    return outer, holes


def _classify_vertices(approx: np.ndarray) -> tuple[int, int]:
    """Split an approxPolyDP polygon's vertices into (n_convex, n_reflex)
    via the sign of each vertex's local turning cross-product relative to
    the polygon's OVERALL orientation (shoelace-formula signed area) --
    findContours' winding order isn't guaranteed, so the overall sign must
    be established first rather than assumed."""
    pts = approx.reshape(-1, 2).astype(np.float64)
    n = len(pts)
    if n < 3:
        return n, 0
    signed_area = 0.0
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        signed_area += x1 * y2 - x2 * y1
    overall_sign = 1.0 if signed_area >= 0 else -1.0

    n_convex = n_reflex = 0
    for i in range(n):
        prev, cur, nxt = pts[i - 1], pts[i], pts[(i + 1) % n]
        v1, v2 = cur - prev, nxt - cur
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        if cross == 0:
            n_convex += 1  # collinear -- treat as neutral/convex, not a real corner
        elif (cross > 0) == (overall_sign > 0):
            n_convex += 1
        else:
            n_reflex += 1
    return n_convex, n_reflex


def analyze_glyph(bin_native: np.ndarray) -> dict:
    padded = _padded_mask(bin_native)
    outer, holes = _find_outer_and_holes(padded)
    if outer is None:
        return {"padded": padded, "outer": None, "holes": [], "sweep": {}, "metrics": {}}

    area = cv2.contourArea(outer)
    perim = cv2.arcLength(outer, True)
    hull = cv2.convexHull(outer)
    hull_area = cv2.contourArea(hull)
    solidity = (area / hull_area) if hull_area > 0 else 0.0
    circularity_deficit = (perim ** 2) / (4 * np.pi * area) if area > 0 else float("inf")

    sweep = {}
    for frac in EPS_FRACS:
        eps = max(frac * perim, 0.5)
        approx = cv2.approxPolyDP(outer, eps, True)
        n_convex, n_reflex = _classify_vertices(approx)
        sweep[frac] = {"approx": approx, "n_vertices": len(approx),
                        "n_convex": n_convex, "n_reflex": n_reflex}

    op_frac = 0.05  # chosen after inspecting the sweep -- see module docstring
    op = sweep[op_frac]

    return {
        "padded": padded, "outer": outer, "holes": holes, "sweep": sweep,
        "metrics": {
            "area": area, "perimeter": perim, "solidity": solidity,
            "circularity_deficit": circularity_deficit, "hole_count": len(holes),
            "n_vertices_outer": op["n_vertices"],
            "n_convex_vertices": op["n_convex"],
            "n_reflex_vertices": op["n_reflex"],
        },
    }


# ── Visualization ────────────────────────────────────────────────────────────

def _contour_overlay(padded_mask: np.ndarray, outer: "np.ndarray | None",
                      holes: list[np.ndarray], approx: "np.ndarray | None") -> np.ndarray:
    base = _to_bgr(padded_mask)
    if outer is not None:
        cv2.drawContours(base, [outer], -1, (200, 200, 200), 1)
    for h in holes:
        cv2.drawContours(base, [h], -1, (255, 140, 0), 1)
    if approx is not None:
        pts = approx.reshape(-1, 2)
        n = len(pts)
        cv2.polylines(base, [pts.reshape(-1, 1, 2)], True, (0, 200, 0), 1)
        if n >= 3:
            pts_f = pts.astype(np.float64)
            signed_area = sum(pts_f[i][0] * pts_f[(i + 1) % n][1] - pts_f[(i + 1) % n][0] * pts_f[i][1]
                               for i in range(n))
            overall_sign = 1.0 if signed_area >= 0 else -1.0
            for i in range(n):
                prev, cur, nxt = pts_f[i - 1], pts_f[i], pts_f[(i + 1) % n]
                v1, v2 = cur - prev, nxt - cur
                cross = v1[0] * v2[1] - v1[1] * v2[0]
                reflex = cross != 0 and (cross > 0) != (overall_sign > 0)
                color = (0, 0, 220) if reflex else (0, 160, 0)
                cv2.circle(base, tuple(pts[i]), 2, color, -1)
    return base


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--atlas", default=str(_DEFAULT_ATLAS))
    ap.add_argument("--lookup", default=str(_DEFAULT_LOOKUP))
    ap.add_argument("--output", default=str(_DEFAULT_OUTPUT))
    args = ap.parse_args(argv)

    atlas_path = Path(args.atlas)
    lookup_all = _load_lookup(Path(args.lookup))
    lookup = lookup_all[atlas_path.name]

    glyphs, bg_gray = load_atlas_glyphs(atlas_path, lookup)
    print(f"{len(glyphs)} glyphs isolated from {atlas_path.name}, bg_gray={bg_gray}")

    for g in glyphs:
        g["bin_native"] = _binarize_native(g["native"], bg_gray)
        g["result"] = analyze_glyph(g["bin_native"])

    # ── Vertex-count sweep table ─────────────────────────────────────────────
    print(f"\nVertex count (approxPolyDP on the OUTER contour) vs epsilon fraction "
          f"of the contour's own arcLength:")
    print(f"{'char':>5}  {'w x h':>7}  {'perim':>7}  " + "  ".join(f"e={f:.2f}" for f in EPS_FRACS))
    for g in glyphs:
        r = g["result"]
        if not r["sweep"]:
            print(f"{g['char']!r:>5}  {g['w']:>3}x{g['h']:<3}  {'--':>7}  (no outer contour found)")
            continue
        perim = r["metrics"]["perimeter"]
        counts = "  ".join(f"{r['sweep'][f]['n_vertices']:5d}" for f in EPS_FRACS)
        print(f"{g['char']!r:>5}  {g['w']:>3}x{g['h']:<3}  {perim:7.1f}  {counts}")

    print(f"\nReflex (concave) vertex count vs epsilon fraction:")
    print(f"{'char':>5}  " + "  ".join(f"e={f:.2f}" for f in EPS_FRACS))
    for g in glyphs:
        r = g["result"]
        if not r["sweep"]:
            continue
        counts = "  ".join(f"{r['sweep'][f]['n_reflex']:5d}" for f in EPS_FRACS)
        print(f"{g['char']!r:>5}  {counts}")

    # ── 5 candidate segregation parameters, at the chosen operating epsilon ──
    print(f"\nCandidate segregation parameters (operating epsilon = 0.05 * arcLength):")
    print(f"{'char':>5}  {'n_vert':>7}  {'n_reflex':>9}  {'holes':>6}  "
          f"{'solidity':>9}  {'circ_deficit':>13}")
    rows = []
    for g in glyphs:
        m = g["result"]["metrics"]
        if not m:
            continue
        rows.append((g["char"], m))
        print(f"{g['char']!r:>5}  {m['n_vertices_outer']:>7}  {m['n_reflex_vertices']:>9}  "
              f"{m['hole_count']:>6}  {m['solidity']:>9.3f}  {m['circularity_deficit']:>13.3f}")

    line_group = {"1", "7"}
    curve_group = {"0", "2", "5"}
    print(f"\nIntuition check -- {{1,7}} (expected fewer vertices) vs {{0,2,5}} "
          f"(expected more):")
    for label, group in (("{1,7}", line_group), ("{0,2,5}", curve_group)):
        vals = [m["n_vertices_outer"] for c, m in rows if c in group]
        reflex = [m["n_reflex_vertices"] for c, m in rows if c in group]
        if vals:
            print(f"  {label:>8}  n_vertices={vals}  n_reflex={reflex}")

    print(f"\nWithin the non-loop group only -- {{1,4,7}} (production's own "
          f"'line-dominant' branch) vs {{2,3,5}} (its 'arc, no hole' leaf), "
          f"reflex-vertex count at low epsilon:")
    for frac in (0.01, 0.02, 0.03, 0.05):
        line3 = {c: g["result"]["sweep"][frac]["n_reflex"]
                 for c, g in ((g["char"], g) for g in glyphs) if c in {"1", "4", "7"}}
        arc3  = {c: g["result"]["sweep"][frac]["n_reflex"]
                 for c, g in ((g["char"], g) for g in glyphs) if c in {"2", "3", "5"}}
        gap = min(arc3.values()) - max(line3.values())
        print(f"  e={frac:.2f}  {{1,4,7}}={line3}  {{2,3,5}}={arc3}  gap={gap:+d}")

    # ── Visual table ──────────────────────────────────────────────────────────
    columns = ["native", "binary"] + [f"poly e={f:.2f}" for f in VISUAL_EPS]
    n_cols = len(columns)
    n_rows = len(glyphs)
    W = LABEL_W + n_cols * CELL_W
    H = HEADER_H + n_rows * CELL_H
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)

    for j, name in enumerate(columns):
        x0 = LABEL_W + j * CELL_W
        cv2.putText(canvas, name, (x0 + 4, HEADER_H - 14), cv2.FONT_HERSHEY_SIMPLEX,
                    0.42, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (x0, 0), (x0, H), (210, 210, 210), 1)
    cv2.line(canvas, (0, HEADER_H), (W, HEADER_H), (150, 150, 150), 1)
    cv2.putText(canvas, "green=convex vertex, red=reflex vertex, orange=hole contour",
                (LABEL_W + 4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (90, 90, 90), 1, cv2.LINE_AA)

    for i, g in enumerate(glyphs):
        y0 = HEADER_H + i * CELL_H
        cv2.line(canvas, (0, y0), (W, y0), (210, 210, 210), 1)
        cv2.putText(canvas, f"'{g['char']}'", (10, y0 + CELL_H // 2), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 0), 1, cv2.LINE_AA)

        r = g["result"]
        cell_imgs = [_to_bgr(g["native"]), _to_bgr(g["bin_native"])]
        captions = ["", f"{g['w']}x{g['h']}"]
        for f in VISUAL_EPS:
            if r["sweep"]:
                approx = r["sweep"][f]["approx"]
                cell_imgs.append(_contour_overlay(r["padded"], r["outer"], r["holes"], approx))
                captions.append(f"v={r['sweep'][f]['n_vertices']} "
                                 f"cv={r['sweep'][f]['n_convex']} rx={r['sweep'][f]['n_reflex']}")
            else:
                cell_imgs.append(_to_bgr(r["padded"]))
                captions.append("no contour")

        for j, (img, cap) in enumerate(zip(cell_imgs, captions)):
            x0 = LABEL_W + j * CELL_W
            _fit_and_paste(canvas, img, x0 + 4, y0 + 4, CELL_W - 8, CELL_H - CAPTION_H - 8)
            _put_caption(canvas, cap, x0, y0 + CELL_H, CELL_W)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas)
    print(f"\nWrote {canvas.shape[1]}x{canvas.shape[0]} debug table -> {out_path}")


if __name__ == "__main__":
    main()
