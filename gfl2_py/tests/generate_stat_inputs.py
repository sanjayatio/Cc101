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
individual cell crops to tests/inputs/daily/, and writes tests/inputs/daily/stat.json.

Usage:
    python tests/generate_stat_inputs.py               # top 20 images from single/
    python tests/generate_stat_inputs.py -n 30         # top 30 images
    python tests/generate_stat_inputs.py single/gm_d_20250929.png  # specific image(s)
    python tests/generate_stat_inputs.py "single/gm_d_*.png"       # glob
"""
from __future__ import annotations
import sys, json, argparse, re
from pathlib import Path
import glob as _glob

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _collect_cells

FALLBACKS_JSON = _ROOT / "tests" / "outputs" / "daily" / "tests/outputs/daily/stat_tess_fallbacks.json"
DAILY          = _ROOT / "tests" / "inputs" / "daily"
STAT_JSON      = DAILY / "stat.json"
FONT_REF       = "assets/stat_fonts/default/templates.json"
DEFAULT_N      = 20

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
    results = _collect_cells(image_paths, tess_only=False)
    print(f"  Collected {len(results)} cells")

    if not results:
        print("No cells extracted — check image paths.", file=sys.stderr)
        sys.exit(1)

    DAILY.mkdir(parents=True, exist_ok=True)
    grouped = _build_grouped(results)
    manifest = {"font": FONT_REF, "crops": grouped}
    STAT_JSON.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    n_src   = len(grouped)
    n_crops = sum(len(v) for v in grouped.values())
    print(f"  Wrote {STAT_JSON}  ({n_src} source images, {n_crops} crops)")


if __name__ == "__main__":
    main()
