#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/generate_stat_inputs.py  --  Regenerate the daily stat-OCR test harness.

PREREQUISITE: tests/outputs/daily/stat_tess_fallbacks.json must exist and be populated by prior
production runs.  It is written by daily_gunsmoke.flush_tess_fallbacks(),
called automatically at the end of each:
    python main.py <folder/> --pattern daily_gunsmoke
Each run appends Tesseract fallback events to the file, ranking which images
the blob pipeline struggles with.  Without the file, this script falls back
to all single/*.png with no ranking.

Selects the N worst-performing images from single/ (ranked by Tesseract-fallback
count in tests/outputs/daily/stat_tess_fallbacks.json), runs the full pipeline on them, saves
individual cell crops to tests/inputs/daily/, and writes tests/inputs/daily/stat_data.py
(a Python module, not the old stat.json).

Alongside the crop ground truth, each source image gets a metadata record used
to judge how much it's pulling its weight in the held-out set: which dolls it
contains, whether any are rare across the wider single/ corpus, how many cells
the full pipeline itself could not resolve (still '?' after Tesseract fallback),
and whether it's a known structural outlier from docs/known_issues.txt.

Usage:
    python tests/generate_stat_inputs.py               # top 20 images from single/
    python tests/generate_stat_inputs.py -n 30         # top 30 images
    python tests/generate_stat_inputs.py single/gm_d_20250929.png  # specific image(s)
    python tests/generate_stat_inputs.py "single/gm_d_*.png"       # glob
"""
from __future__ import annotations
import sys, json, argparse, re
from pathlib import Path
from collections import Counter
import glob as _glob

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _collect_cells

FALLBACKS_JSON = _ROOT / "tests" / "outputs" / "daily" / "stat_tess_fallbacks.json"
DAILY          = _ROOT / "tests" / "inputs" / "daily"
STAT_DATA_PY   = DAILY / "stat_data.py"
GT_OVERRIDES_JSON = DAILY / "stat_gt_overrides.json"
FONT_REF       = "assets/fonts/stat_pct.py"
DEFAULT_N      = 20

# Rarity cutoff for the "rare_dolls" metadata tag: a doll appearing in this
# many or fewer of the SELECTED images is "rare" within the held-out set.
# Rarity is scored against the selected set itself (not the full single/
# corpus) so regenerating stays fast regardless of corpus size.
RARE_DOLL_MAX_IMAGES = 2

# Known structural outliers called out in docs/known_issues.txt — flagged here
# rather than inferred, since the failure is at blob-extraction, not a '?'
# ground-truth marker (§10: fb_d_20251112 p2, all header stat fields fail).
STRUCTURAL_OUTLIERS = {
    "fb_d_20251112.png": "known_issues.txt §10 — p2 header stats fail at blob extraction",
}

_PART_RE = re.compile(r'_p(\d+)_r(\d+)_(col\d+)$')


def _top_n_images(n: int) -> list[Path]:
    """Return top-N worst images ranked by fallback count in tests/outputs/daily/stat_tess_fallbacks.json."""
    single = _ROOT / "single"
    if not FALLBACKS_JSON.exists():
        print(f"WARN: {FALLBACKS_JSON} not found; using all single/*.png", file=sys.stderr)
        return sorted(single.glob("*.png"))

    data = json.loads(FALLBACKS_JSON.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    for item in data:
        fn = item.get("file", "")
        if fn:
            counts[fn] = counts.get(fn, 0) + 1

    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    result = []
    for stem, _ in ranked[:n]:
        p = single / (stem + ".png")
        if p.exists():
            result.append(p)
    return result


def _apply_gt_overrides(results: list[dict]) -> int:
    """Correct known-wrong Tesseract labels in-place before grouping.

    Mirrors gfl2.stat_ocr.build_templates()'s own override application
    (action_items.txt #6) -- without this, a plain re-run of this script
    silently discards every hand-verified correction tracked in
    stat_gt_overrides.json and re-bakes the original Tesseract mislabel
    into stat_data.py's "ground truth" (docs/known_issues.txt §15/§17/§32).
    """
    if not GT_OVERRIDES_JSON.exists():
        return 0
    overrides = json.loads(GT_OVERRIDES_JSON.read_text(encoding="utf-8"))
    n_applied = 0
    for item in results:
        ov = overrides.get(item.get("source"))
        if ov:
            if "pct" in ov: item["pct"] = ov["pct"]
            if "val" in ov: item["val"] = ov["val"]
            n_applied += 1
    return n_applied


def _build_grouped(results: list[dict]) -> dict[str, list]:
    """Group _collect_cells output by source image filename."""
    grouped: dict[str, list] = {}
    for item in results:
        source_key = item["img_path"].name
        m = _PART_RE.search(item["source"])
        if not m:
            continue
        part = f"p{m.group(1)}_r{m.group(2)}_{m.group(3)}"
        grouped.setdefault(source_key, []).append({
            "part": part,
            "pct":  item["pct"],
            "val":  item["val"],
        })
    return grouped


def _doll_names_by_image(image_paths: list[Path]) -> dict[str, list[str]]:
    """Run the daily_gunsmoke doll-row pipeline to get doll names per image.

    Portrait saving is disabled for the duration (same trick as
    tests/conftest.py) so running this repeatedly never mutates assets/dolls/.
    """
    import cv2
    import gfl2.dg_output as _dg
    from gfl2.patterns import daily_gunsmoke as _dgs

    original_save = _dg._save_doll_portrait
    _dg._save_doll_portrait = lambda name, portrait: "skip"
    try:
        out: dict[str, list[str]] = {}
        for p in image_paths:
            img = cv2.imread(str(p))
            if img is None:
                continue
            names: set[str] = set()
            try:
                for entry in _dgs.parse(img, filename=p.stem):
                    for row in entry.dolls:
                        if row.name:
                            names.add(row.name)
            except Exception as exc:
                print(f"WARN: doll-name extraction failed for {p.name}: {exc}", file=sys.stderr)
            out[p.name] = sorted(names)
        return out
    finally:
        _dg._save_doll_portrait = original_save


def _doll_frequencies(doll_names: dict[str, list[str]]) -> Counter:
    """Frequency of each doll name across the images passed in."""
    freq: Counter = Counter()
    for names in doll_names.values():
        for name in names:
            freq[name] += 1
    return freq


def _build_metadata(grouped: dict[str, list], image_paths: list[Path]) -> dict[str, dict]:
    doll_names = _doll_names_by_image(image_paths)
    freq = _doll_frequencies(doll_names)

    meta: dict[str, dict] = {}
    for source_img, parts in grouped.items():
        hard_parts = [p["part"] for p in parts
                      if "?" in (p.get("pct") or "") or "?" in (p.get("val") or "")]
        km_parts = [p["part"] for p in parts
                    if (p.get("val") or "").rstrip("?").endswith(("K", "M"))]
        dolls = doll_names.get(source_img, [])
        rare = sorted(d for d in dolls if freq.get(d, 0) <= RARE_DOLL_MAX_IMAGES)
        prefix = source_img.split("_", 1)[0]

        meta[source_img] = {
            "prefix":             prefix,
            "n_cells":            len(parts),
            "dolls":              dolls,
            "rare_dolls":         rare,
            "hard_cells":         hard_parts,
            "km_suffix_cells":    km_parts,
            "structural_outlier": STRUCTURAL_OUTLIERS.get(source_img),
            # Simple additive score for at-a-glance ranking; the fields above
            # are the actual signal — recompute your own weighting if this
            # default doesn't fit the question you're asking.
            "importance_score": (
                2 * len(hard_parts) + 3 * len(rare)
                + (5 if source_img in STRUCTURAL_OUTLIERS else 0)
            ),
        }
    return meta


def _write_python_module(font_ref: str, grouped: dict, meta: dict, tess_only: bool) -> None:
    gt_source_lines = (
        [
            "# CROPS: ground truth (pct, val) per cell part, grouped by source image.",
            "#   Produced by pure-Tesseract labeling (--tess-only), NOT any blob engine's",
            "#   own output -- so the same ground truth is a fair, engine-neutral",
            "#   reference for every engine under test (dp, padded, ...), corrected by",
            "#   stat_gt_overrides.json. See gfl2.stat_ocr._collect_cells(tess_only=True).",
        ]
        if tess_only else
        [
            "# CROPS: ground truth (pct, val) per cell part, grouped by source image.",
            "#   Produced by running the full pipeline (blob, then Tesseract fallback)",
            "#   on each image — see gfl2.stat_ocr._collect_cells.",
        ]
    )
    lines = [
        "# auto-generated by tests/generate_stat_inputs.py — do not edit by hand",
        "#",
        *gt_source_lines,
        "# META: per-image metadata used to judge how much each image contributes",
        "#   to the held-out set — doll frames present,",
        "#   which of those are rare across single/*.png, how many cells the full",
        "#   pipeline itself could not resolve, and known structural outliers.",
        f"FONT = {font_ref!r}",
        "",
        "CROPS = " + _pyrepr(grouped),
        "",
        "META = " + _pyrepr(meta),
        "",
    ]
    STAT_DATA_PY.write_text("\n".join(lines), encoding="utf-8")


def _pyrepr(obj, indent=0) -> str:
    """Deterministic, readable repr (stable key order, 2-space indent)."""
    pad = "  " * indent
    pad_in = "  " * (indent + 1)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = []
        for k, v in obj.items():
            items.append(f"{pad_in}{k!r}: {_pyrepr(v, indent + 1)},")
        return "{\n" + "\n".join(items) + f"\n{pad}}}"
    if isinstance(obj, (list, set)):
        seq = list(obj)
        if not seq:
            return "[]"
        items = [f"{pad_in}{_pyrepr(v, indent + 1)}," for v in seq]
        return "[\n" + "\n".join(items) + f"\n{pad}]"
    return repr(obj)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Regenerate daily stat-OCR test inputs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("\n\nUsage:")[1] if "\n\nUsage:" in __doc__ else "",
    )
    parser.add_argument("images", nargs="*",
                        help="Specific image file(s) or glob (default: top-N from fallbacks.json)")
    parser.add_argument("-n", "--top-n", type=int, default=DEFAULT_N,
                        help=f"Number of top-failing images to select  [default: {DEFAULT_N}]")
    parser.add_argument("--tess-only", action="store_true",
                        help="Ground truth = pure Tesseract label (matches each engine's own "
                             "--verify methodology) instead of the production full pipeline "
                             "(blob, then Tesseract fallback). Use this when the resulting "
                             "stat_data.py will be compared against a NON-production engine "
                             "(e.g. dp, padded) so the ground truth isn't biased toward "
                             "production's own blob answers.")
    parser.add_argument("--no-gt-cache", action="store_true",
                        help="With --tess-only, force live Tesseract instead of consulting "
                             "tests/inputs/daily/tess_gt_cache.py.")
    args = parser.parse_args(argv)

    if args.images:
        image_paths = []
        for pat in args.images:
            expanded = [Path(p) for p in _glob.glob(pat)]
            image_paths.extend(expanded if expanded else [Path(pat)])
    else:
        image_paths = _top_n_images(args.top_n)

    image_paths = [p for p in image_paths if p.suffix.lower() == ".png"]
    if not image_paths:
        print("No PNG images found.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(image_paths)} image(s)...")
    if args.tess_only:
        gt_cache = None
        if not args.no_gt_cache:
            from gfl2.stat_ocr import _load_tess_gt_cache
            gt_cache = _load_tess_gt_cache()
        results = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    else:
        results = _collect_cells(image_paths, tess_only=False)
    print(f"  Collected {len(results)} cells")

    if not results:
        print("No cells extracted — check image paths.", file=sys.stderr)
        sys.exit(1)

    n_overridden = _apply_gt_overrides(results)
    if n_overridden:
        print(f"  Applied {n_overridden} GT override(s) from {GT_OVERRIDES_JSON.name}")

    DAILY.mkdir(parents=True, exist_ok=True)
    grouped = _build_grouped(results)

    print("Extracting doll names for metadata...")
    meta = _build_metadata(grouped, image_paths)

    _write_python_module(FONT_REF, grouped, meta, args.tess_only)
    n_src   = len(grouped)
    n_crops = sum(len(v) for v in grouped.values())
    n_rare  = sum(1 for m in meta.values() if m["rare_dolls"])
    n_hard  = sum(len(m["hard_cells"]) for m in meta.values())
    print(f"  Wrote {STAT_DATA_PY}  ({n_src} source images, {n_crops} crops, "
          f"{n_hard} hard cells, {n_rare} images with rare dolls)")


if __name__ == "__main__":
    main()
