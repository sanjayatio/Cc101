# -*- coding: utf-8 -*-
"""
tests/inputs/daily/curate_meaningful_images.py -- builds the curated
"meaningful images" subset of single/*.png for tests/inputs/daily/,
and copies the selected PNGs there. Lives here
(not debugs/) since it's a curation tool for this directory's own fixture
set, not a general exploration script.

An image is selected when it satisfies at least one of four criteria
(direct instruction, 2026-07-12):
  1. UNIQUE DOLL FRAME  -- contains a doll not covered by any other
     already-selected image (rare/unique dolls first).
  2. UNIQUE GLYPH       -- contains a character (digit/letter/punctuation)
     from score, header (dealt/taken/turns), pct, or val text not yet
     covered by any other already-selected image.
  3. DIFFERENT RESOLUTION -- an image whose (width, height) is a real
     outlier vs. the corpus's typical size (e.g. gm_d_20250908.png,
     known_issues.txt §18).
  4. PROVEN DIFFICULT   -- an image referenced by an xfail-marked test
     case, a stat_excluded_cells.json entry, or a known_issues.txt
     structural-outlier writeup (e.g. §10, §18, §23, §33).

Data sources (deliberately real corpus artifacts, not guesses):
  - single/daily_gunsmoke.js       -- doll names + score/header text,
                                       per (filename, report_idx).
  - tests/inputs/daily/tess_gt_cache.py -- pct/val ground truth per cell,
                                       independent of the blob classifier
                                       (reference.txt §5.3's own doctrine:
                                       Tesseract GT can't be "confidently
                                       wrong" the way a re-run of the blob
                                       pipeline itself can).
  - single/*.png                   -- actual image dimensions (resolution
                                       outlier detection).
  - hardcoded DIFFICULT_IMAGES     -- transcribed directly from
                                       known_issues.txt / the two hard-case
                                       test files' xfail sets /
                                       stat_gt_overrides.json's "corrupted
                                       input" style overrides /
                                       stat_excluded_cells.json -- every
                                       entry cites its source section.

SELECTION ALGORITHM: greedy set-cover, in criterion-priority order
(difficult/resolution outliers are FORCED first since they're each a
single named image with no substitute; doll and glyph coverage are then
filled by repeatedly picking whichever remaining image covers the most
still-uncovered (doll, glyph) items -- same "reason-tagged, not a random
sample" discipline the rest of this project's curation work uses, e.g.
debugs/debug_line_stroke_thickness_sweep.py's own outlier-flagging).

Usage:
    python tests/inputs/daily/curate_meaningful_images.py            # dry run (report only)
    python tests/inputs/daily/curate_meaningful_images.py --copy      # also copy PNGs + write metadata
"""
from __future__ import annotations
import argparse
import glob as _glob
import json
import re
import shutil
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_ROOT))

import cv2
import numpy as np

SINGLE_DIR = _ROOT / "single"
DAILY_JS = SINGLE_DIR / "daily_gunsmoke.js"
DEST_DIR = _ROOT / "tests" / "inputs" / "daily"
META_OUT = DEST_DIR / "meaningful_images.py"

TARGET_COUNT = 20
RESOLUTION_OUTLIER_STD_MULT = 2.0

# ---------------------------------------------------------------------------
# Hardcoded "proven difficult" roster -- each entry cites the doc section it
# came from, so this list is auditable against known_issues.txt directly
# rather than being a bare set of filenames.
# ---------------------------------------------------------------------------
DIFFICULT_IMAGES = {
    "fb_d_060518.png": "known_issues.txt §5 -- first-observed case of the "
        "single-panel-incorrectly-split bug (RESOLVED, kept as a regression "
        "guard); also known_issues.txt §33 -- score '6795' reads as a "
        "bizarre doubled '66779955', not yet root-caused",
    "gm_d_20250908.png": "known_issues.txt §18 -- ~10% smaller capture "
        "resolution than the corpus norm; THRESH_BIN=180 merges col3 digit "
        "blobs; xfail in test_stat_ocr_hard_cases.py/test_stat_ocr_v0_1_1.py",
    "fb_d_20251112.png": "known_issues.txt §10 -- panel 2's header stats "
        "row (dealt/taken/turns) fails at blob extraction entirely; "
        "structural rendering outlier, not a classification issue",
    "fb_d_20260315.png": "known_issues.txt §23 -- p1_r3 is a mid-animation "
        "screenshot capture (ghosted pct text, blank val); excluded via "
        "stat_excluded_cells.json. ELEVATED IMPORTANCE: this is the corpus's "
        "one confirmed example of a double-exposed/ghosted glyph, making it "
        "the required negative-control case for any future skeleton- or "
        "thinning-based glyph feature (§23's own RELATED IDEA note already "
        "warned that skeletonizing a broken/noisy blob manufactures spurious "
        "endpoints/branches from capture artifacts, not real digit structure) "
        "-- any topological/connectivity gate must be checked against this "
        "image's corrupted glyphs, not just against clean corpus glyphs, "
        "before being trusted.",
    "ib_d_20260112_1.png": "test_stat_ocr_v0_1_1.py _KNOWN_FAILING_GT_IS_"
        "LITERAL_QUESTION_MARK -- p1_r2_col4's own ground truth is a "
        "literal '?' (full pipeline, including Tesseract, cannot resolve "
        "this digit)",
    "ib_d_20250928.png": "test_stat_ocr_v0_1_1.py _KNOWN_FAILING_GT_IS_"
        "LITERAL_QUESTION_MARK -- p1_r2_col4's own ground truth is a "
        "literal '?'",
    "fb_d_20251019.png": "known_issues.txt §33 -- panel 2's header score "
        "'4407' silently drops to '07' (adjacent-digit-merge blob bug); "
        "the motivating case for gfl2/score_ocr_v0_3_0.py",
    "gm_d_20251019.png": "known_issues.txt §18 (2026-07-09 UPDATE) -- "
        "p2_r2_col4 blob-count mismatch (extraction failure, not GT)",
    "gm_d_20260201.png": "known_issues.txt §18 (2026-07-09 UPDATE) -- "
        "p1_r2_col4 blob-count mismatch",
    "gm_d_20260202.png": "known_issues.txt §18 (2026-07-09 UPDATE) -- "
        "p2_r3_col1 blob-count mismatch",
    "ib_d_20251004.png": "known_issues.txt §18 (2026-07-09 UPDATE) -- "
        "p1_r3_col2 blob-count mismatch",
    "ib_d_20251020.png": "known_issues.txt §18 (2026-07-09 UPDATE) -- "
        "p1_r4_col4: GT is single digit '0' but 3 blobs are found "
        "(width-19 blob, widest measured anywhere in the corpus) -- "
        "suspected ghosting artifact, never root-caused",
    "ib_d_20251021.png": "known_issues.txt §18 (2026-07-09 UPDATE) -- "
        "p1_r3_col4 blob-count mismatch",
    "ib_d_20251024.png": "known_issues.txt §18 (2026-07-09 UPDATE) -- "
        "p2_r3_col1 blob-count mismatch",
    "ib_d_20251225.png": "known_issues.txt §18 (2026-07-09 UPDATE) -- "
        "p2_r3_col1 blob-count mismatch",
}

_NUM_RE = re.compile(r"[-+]?\d*\.?\d+")


def load_image_resolutions() -> dict:
    """{filename: (w, h)} for every single/*.png."""
    out = {}
    for p in sorted(SINGLE_DIR.glob("*.png")):
        img = cv2.imread(str(p))
        if img is None:
            continue
        h, w = img.shape[:2]
        out[p.name] = (w, h)
    return out


_SINGLE_PANEL_WIDTH_CUTOFF = 1700  # single-panel images are ~1130-1160px wide,
                                    # two-panel images ~2270-2310px -- a
                                    # genuinely bimodal split (known_issues.txt
                                    # §5), NOT itself a "different resolution"
                                    # outlier. z-scoring must be done WITHIN
                                    # each panel-count group, or every
                                    # single-panel image falsely reads as an
                                    # outlier against the two-panel majority.


def find_resolution_outliers(resolutions: dict) -> dict:
    """{filename: reason} for images whose (w, h) deviates from ITS OWN
    panel-count group's mean by >= RESOLUTION_OUTLIER_STD_MULT std, on
    either axis. Grouping by panel count first avoids conflating the
    expected single-vs-two-panel bimodal width split with a genuine
    same-layout resolution outlier like gm_d_20250908.png."""
    groups: dict = {"single": [], "double": []}
    for n, (w, h) in resolutions.items():
        groups["single" if w < _SINGLE_PANEL_WIDTH_CUTOFF else "double"].append(n)

    out = {}
    for group_name, names in groups.items():
        if len(names) < 2:
            continue
        ws = np.array([resolutions[n][0] for n in names], dtype=float)
        hs = np.array([resolutions[n][1] for n in names], dtype=float)
        w_mean, w_std = ws.mean(), ws.std()
        h_mean, h_std = hs.mean(), hs.std()
        for n, w, h in zip(names, ws, hs):
            wz = (w - w_mean) / w_std if w_std else 0.0
            hz = (h - h_mean) / h_std if h_std else 0.0
            if abs(wz) >= RESOLUTION_OUTLIER_STD_MULT or abs(hz) >= RESOLUTION_OUTLIER_STD_MULT:
                out[n] = (f"resolution outlier within {group_name}-panel group: "
                          f"{int(w)}x{int(h)} vs group mean {w_mean:.0f}x{h_mean:.0f} "
                          f"(w_z={wz:+.2f}, h_z={hz:+.2f})")
    return out


def parse_daily_gunsmoke_js(path: Path) -> dict:
    """{filename.png: {"dolls": {name, ...}, "glyphs": {char, ...}}}
    Parsed with a permissive regex, not a JS engine -- the file is a
    flat, machine-generated array literal (reference.txt §1.2's own
    documented format), not arbitrary JS."""
    text = path.read_text(encoding="utf-8")
    # one line per top-level report entry: ["fname",idx,score,"dealt",taken,turns,[...doll rows...]]
    entries = re.findall(
        r'\["([a-zA-Z0-9_]+)",\s*(\d+),\s*(\d+),\s*"([^"]*)",\s*(\d+),\s*(\d+),\s*\[(.*?)\]\]',
        text, re.S,
    )
    out: dict = {}
    for fname, _idx, score, dealt, taken, turns, rows_blob in entries:
        png = f"{fname}.png"
        bucket = out.setdefault(png, {"dolls": set(), "glyphs": set()})
        for ch in str(score):
            bucket["glyphs"].add(ch)
        for ch in dealt:
            bucket["glyphs"].add(ch)
        for ch in str(taken):
            bucket["glyphs"].add(ch)
        for ch in str(turns):
            bucket["glyphs"].add(ch)
        doll_rows = re.findall(r'\["([^"]*)",\s*([^\]]*)\]', rows_blob)
        for doll_name, rest in doll_rows:
            bucket["dolls"].add(doll_name)
            for num in _NUM_RE.findall(rest):
                for ch in num:
                    bucket["glyphs"].add(ch)
    return out


def parse_tess_gt_cache() -> dict:
    """{filename.png: {char, ...}} -- glyphs actually appearing in every
    cell's pct/val ground truth, per source image. '?' is dropped -- it's
    a "could not resolve" marker in the GT itself, not a real glyph."""
    ns: dict = {}
    exec(compile((_ROOT / "tests" / "inputs" / "daily" / "tess_gt_cache.py")
                 .read_text(encoding="utf-8"), "tess_gt_cache.py", "exec"), ns)
    data = ns["DATA"]
    out: dict = {}
    for key, entry in data.items():
        # key format: "<stem>_p<panel>_r<row>_col<col>"
        m = re.match(r"(.+?)_p\d+_r\d+_col\d+$", key)
        if not m:
            continue
        png = f"{m.group(1)}.png"
        bucket = out.setdefault(png, set())
        for field in ("pct", "val"):
            for ch in (entry.get(field) or ""):
                if ch != "?":
                    bucket.add(ch)
    return out


def build_corpus_index():
    resolutions = load_image_resolutions()
    js_index = parse_daily_gunsmoke_js(DAILY_JS)
    gt_glyphs = parse_tess_gt_cache()

    per_image = {}
    for name in resolutions:
        dolls = js_index.get(name, {}).get("dolls", set())
        glyphs = set(js_index.get(name, {}).get("glyphs", set()))
        glyphs |= gt_glyphs.get(name, set())
        per_image[name] = {"dolls": dolls, "glyphs": glyphs, "resolution": resolutions[name]}
    return per_image


def greedy_cover(per_image: dict, forced: list, target_count: int) -> list:
    selected = list(forced)
    covered_dolls = set()
    covered_glyphs = set()
    for name in selected:
        covered_dolls |= per_image[name]["dolls"]
        covered_glyphs |= per_image[name]["glyphs"]

    all_dolls = set()
    all_glyphs = set()
    for v in per_image.values():
        all_dolls |= v["dolls"]
        all_glyphs |= v["glyphs"]

    remaining = [n for n in per_image if n not in selected]
    while (covered_dolls < all_dolls or covered_glyphs < all_glyphs) and remaining:
        def gain(name):
            v = per_image[name]
            return (len(v["dolls"] - covered_dolls) * 3   # weight dolls higher (rarer signal)
                    + len(v["glyphs"] - covered_glyphs))
        best = max(remaining, key=gain)
        if gain(best) <= 0:
            break
        selected.append(best)
        covered_dolls |= per_image[best]["dolls"]
        covered_glyphs |= per_image[best]["glyphs"]
        remaining.remove(best)

    return selected, covered_dolls, covered_glyphs, all_dolls, all_glyphs


def reason_for(name: str, per_image: dict, forced_reasons: dict,
               covered_dolls_before: set, covered_glyphs_before: set) -> list:
    reasons = []
    if name in forced_reasons:
        reasons.append(forced_reasons[name])
    new_dolls = per_image[name]["dolls"] - covered_dolls_before
    if new_dolls:
        reasons.append(f"unique doll frame(s): {sorted(new_dolls)}")
    new_glyphs = per_image[name]["glyphs"] - covered_glyphs_before
    if new_glyphs:
        reasons.append(f"unique glyph(s): {sorted(new_glyphs)}")
    return reasons


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--copy", action="store_true",
                     help="copy selected PNGs into tests/inputs/daily/ and write metadata")
    ap.add_argument("--target", type=int, default=TARGET_COUNT)
    args = ap.parse_args(argv)

    per_image = build_corpus_index()
    resolutions = {n: v["resolution"] for n, v in per_image.items()}
    res_outliers = find_resolution_outliers(resolutions)

    forced_reasons = dict(DIFFICULT_IMAGES)
    for name, reason in res_outliers.items():
        forced_reasons.setdefault(name, reason)
        if name in forced_reasons and "resolution outlier" not in forced_reasons[name] and name in res_outliers:
            forced_reasons[name] = forced_reasons[name] + f"; also {reason}"

    forced = sorted(n for n in forced_reasons if n in per_image)
    missing_forced = sorted(n for n in forced_reasons if n not in per_image)
    if missing_forced:
        print(f"WARNING: forced images not found in single/*.png: {missing_forced}")

    selected, cov_dolls, cov_glyphs, all_dolls, all_glyphs = greedy_cover(
        per_image, forced, args.target)

    print(f"Corpus: {len(per_image)} images, {len(all_dolls)} unique dolls, "
          f"{len(all_glyphs)} unique glyphs")
    print(f"Forced (difficult/resolution-outlier): {len(forced)} images")
    print(f"Final selection: {len(selected)} images "
          f"(target was {args.target})")
    print(f"Doll coverage: {len(cov_dolls)}/{len(all_dolls)}  "
          f"missing: {sorted(all_dolls - cov_dolls)}")
    print(f"Glyph coverage: {len(cov_glyphs)}/{len(all_glyphs)}  "
          f"missing: {sorted(all_glyphs - cov_glyphs)}")

    # Recompute reasons in selection order (so "unique" is relative to what
    # was already picked before this image, matching how greedy_cover chose it).
    running_dolls, running_glyphs = set(), set()
    entries = []
    for name in selected:
        reasons = reason_for(name, per_image, forced_reasons, running_dolls, running_glyphs)
        entries.append({
            "source": name,
            "resolution": list(per_image[name]["resolution"]),
            "dolls": sorted(per_image[name]["dolls"]),
            "reasons": reasons,
        })
        running_dolls |= per_image[name]["dolls"]
        running_glyphs |= per_image[name]["glyphs"]

    print(f"\n{'=' * 100}")
    for e in entries:
        print(f"  {e['source']}  ({e['resolution'][0]}x{e['resolution'][1]})")
        for r in e["reasons"]:
            print(f"      {r}")

    if not args.copy:
        print("\n(dry run -- pass --copy to copy PNGs into tests/inputs/daily/ "
              "and write meaningful_images.py)")
        return

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in selected:
        src = SINGLE_DIR / name
        dst = DEST_DIR / name
        shutil.copyfile(src, dst)
        copied.append(name)
    print(f"\nCopied {len(copied)} PNGs into {DEST_DIR}")

    _write_metadata(entries, all_dolls, all_glyphs, cov_dolls, cov_glyphs)
    print(f"Wrote {META_OUT}")


def _write_metadata(entries, all_dolls, all_glyphs, cov_dolls, cov_glyphs) -> None:
    lines = []
    lines.append("# -*- coding: utf-8 -*-")
    lines.append('"""')
    lines.append("meaningful_images.py -- auto-generated by "
                  "tests/inputs/daily/curate_meaningful_images.py")
    lines.append("")
    lines.append("Curated subset of single/*.png, copied into this directory, "
                  "chosen to cover:")
    lines.append("  1. every doll frame that appears anywhere in single/*.png")
    lines.append("  2. every glyph (score/header/pct/val character) that "
                  "appears anywhere in the corpus")
    lines.append("  3. every image whose resolution is a real corpus outlier "
                  "(e.g. gm_d_20250908.png, known_issues.txt §18)")
    lines.append("  4. every image already proven 'difficult' by an xfail "
                  "test case, a stat_excluded_cells.json entry, or a "
                  "known_issues.txt structural-outlier writeup")
    lines.append("")
    lines.append(f"Doll coverage: {len(cov_dolls)}/{len(all_dolls)} "
                  f"({sorted(all_dolls)})")
    lines.append(f"Glyph coverage: {len(cov_glyphs)}/{len(all_glyphs)} "
                  f"({sorted(all_glyphs)})")
    lines.append("")
    lines.append("Regenerate with:")
    lines.append("    python tests/inputs/daily/curate_meaningful_images.py --copy")
    lines.append('"""')
    lines.append("")
    lines.append("IMAGES = [")
    for e in entries:
        lines.append(f"    {e['source']!r},")
    lines.append("]")
    lines.append("")
    lines.append("# {source: {\"resolution\": (w, h), \"dolls\": [...], \"reasons\": [...]}}")
    lines.append("META = {")
    for e in entries:
        lines.append(f"    {e['source']!r}: {{")
        lines.append(f"        \"resolution\": {tuple(e['resolution'])!r},")
        lines.append(f"        \"dolls\": {e['dolls']!r},")
        lines.append(f"        \"reasons\": [")
        for r in e["reasons"]:
            lines.append(f"            {r!r},")
        lines.append(f"        ],")
        lines.append(f"    }},")
    lines.append("}")
    lines.append("")
    META_OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
