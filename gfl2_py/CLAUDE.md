# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@reference.txt
@docs/known_issues.txt
@docs/action_items.txt

## Build & test
- Compile + test all: `python check.py`  (shorthand for the two commands below)
- Compile: `python compile_gfl2.py`  (must run after any source change — Windows .pyc invalidation)
- Test all: `python -m pytest tests/ -q --no-header --tb=short`
- Test single: `python check.py tests/test_stat_ocr_hard_cases.py`
- Regenerate daily stat test inputs: `python tests/generate_stat_inputs.py` (after adding images or Phase 1 rebuild)
- See reference.txt §5 for the full workflow (Phase 1 templates → Phase 2 test inputs → Phase 3 tests)

## Windows / NTFS note
File edits via the Edit tool can silently truncate on NTFS.
After any edit, verify syntax with:
  python -c "import ast; ast.parse(open('PATH').read()); print('ok')"
If truncated, restore the tail by rewriting the file with the Write tool or via:
  python -c "open('PATH','a').write('missing lines here')"

## Key conventions
- Projection correlation threshold: PROJ_CORR_MIN = 0.70 (combined v+h)
- Val templates: NORM_W_VAL=8, NORM_H_VAL=13  |  Pct templates: NORM_W_PCT=12, NORM_H_PCT=20
- Build and inference MUST use the same binarization threshold and blob filters
- `stat_gt_overrides.json` MUST be applied by every code path that can (re)build `stat_pct.py`/`stat_val.py` — not just `--verify`. A `--verify`-only override can't stop a *different* build path (e.g. `assets/builders/build.py`, which calls `build_templates()` directly) from re-contaminating the templates it's meant to fix (known_issues.txt §15).
- Never lower PROJ_CORR_MIN globally; add targeted shortcuts with gap guards instead
- Asset files prefixed with `_` are known-mapped; the prefix is stripped in output

## Documentation numbering conventions
These apply to the numbered/sectioned docs: `docs/known_issues.txt` (§N), `docs/decisions.txt` (#N), `docs/takeaways.txt` (#N), `docs/action_items.txt` (#N).
- **IDs are permanent once assigned.** Never reuse or renumber an entry's number, even after it's deleted or merged elsewhere — leave a one-line tombstone at the old slot (e.g. `§9 — merged into §14, 2026-07-11`) so an existing external reference still resolves to something instead of silently pointing at nothing or, worse, a different entry.
- **New entries always take max(existing)+1** for that file. Gaps left by earlier deletions are permanent — do not backfill them.
- **Cross-file references always name the file explicitly** (`decisions.txt #71`, `known_issues.txt §17`) — never a bare `#71` with the file left implicit. Numbers are only unique *within* a file, not across files.
- **Duplicate numbers inside one file are bugs**, not style issues. Fix by: grepping every doc + code comment for the bare number to see which of the two entries each reference actually means, renumbering only the less-referenced instance to a fresh max+1, and leaving a tombstone at the old slot. Never renumber silently.
- **Neither `known_issues.txt` nor `decisions.txt` should read as a diary.** `decisions.txt` entries are DECISION + RATIONALE, not a blow-by-blow log of every attempt. `known_issues.txt` entries are STATUS + root cause + current fix, with a pointer to `decisions.txt` for *why* — not a full chronological narrative of the investigation. When one of these grows past a handful of dated "UPDATE" entries, add a short current-state summary above the history rather than letting the STATUS line go stale relative to it.
- **Citations between `known_issues.txt`/`decisions.txt` and `takeaways.txt` are one-directional: takeaways.txt cites the issue/decision, never the reverse.** `known_issues.txt`/`decisions.txt` log what happened and why; `takeaways.txt` synthesizes the generalizable lesson on top. A `takeaways.txt` entry pointing back at its source section is obvious and useful; the reverse (many issues each pointing forward at one takeaway) is not obvious and dilutes the point. When the same lesson recurs across multiple issues, that's a feature, not noise to hide — the takeaway entry should cite *all* of them (not just the latest), since seeing the same mistake logged three times in one place is the more persuasive form of the lesson.
- `docs/action_items.txt` is a scratch/sticky-note backlog, not a permanent record. Once an item is DONE, port its outcome into `known_issues.txt`/`decisions.txt` (if not already recorded there) and trim the action item to a short pointer or delete it — don't leave a full essay behind.

## Architecture

### Entry points
| Script | Purpose |
|---|---|
| `main.py` | Primary CLI: routes image(s) to the right pattern parser |
| `compile_gfl2.py` | Force-recompiles `gfl2/` package (hash-based invalidation) |
| `assets/builders/build.py` | Unified Daily GS builder: portraits, header templates, and stat-cell templates in one pass |
| `assets/builders/rebuild_assets.py` | Emergency re-crop of buff/doll assets at a different resolution |
| `tests/generate_stat_inputs.py` | Regenerate daily stat test crops + stat.json from the top-N failing images |
| `debugs/score_detect.py` | Benchmark/rebuild score digit templates (`tests/inputs/weekly_scores/`) |
| `debugs/debug_layout.py` | Annotate Weekly Gunsmoke column positions for diagnosis |
| `debugs/debug_header.py` | Annotate Daily Gunsmoke header/stats crop regions |
| `debugs/render_debug.py` | Render Weekly Gunsmoke CSV as a visual icon grid |
| `debugs/stat_ocr_bench.py` | Head-to-head accuracy + timing: `stat_ocr.py` vs `stat_ocr_padded.py` (known_issues.txt §15) |

### gfl2/ package modules
| Module | Role |
|---|---|
| `patterns/weekly_gunsmoke.py` | Weekly Gunsmoke CSV parser (date, owner, buff, 5 dolls, score) |
| `patterns/daily_gunsmoke.py` | Daily Gunsmoke JS parser (header stats + per-doll rows; frame-based panel discovery) |
| `dg_output.py` | Shared JS model + save logic used by daily_gunsmoke.py |
| `layout.py` | Weekly Gunsmoke row/column extractor (binarization-based anchor detection) |
| `asset_mapper.py` | Visual doll/buff lookup: pHash → HSV histogram → unknown |
| `buff_ocr.py` | Buff name recognition: projection matching (fast) → Tesseract fallback |
| `doll_name_ocr.py` | Projection-based doll name classifier (no Tesseract needed) |
| `stat_ocr.py` | Blob + projection/Hu OCR for DG stat numbers (pct and val lines) |
| `stat_ocr_padded.py` | Aspect-preserving-pad variant of `stat_ocr.py`; selectable via `main.py --stat-ocr-engine padded` (production is the default — decisions.txt decision 47) |
| `stat_ocr_fft.py` | FFT+Gabor+paren+ring+loop+vrun TWO-AGENT nearest-centroid variant of `stat_ocr.py`; pct-line only (val is a no-op stub), NOT registered in `main.py --stat-ocr-engine` — exploratory (known_issues.txt §15, decisions.txt decision 49). Classifier is two independent agents (gabor+paren+ring+loop+vrun, then histogram on unsure cases — each own scale + own confidence threshold) — 97.2% cell-level pct accuracy, identical with or without the opt-in `--enable-pair-tiebreak` '4'/'7' override (known_issues.txt §15's 2026-07-05 entry: gabor_0 removed as measured-redundant, replaced by an isolated vertical-run feature; loop_top/loop_bot added targeting '9'/'6'). Two flagged-but-unresolved concerns from that change: a new '1'/'7' + '0'/'8' confusion pattern, and a structural anomaly on gm_d_20250908 |
| `stat_ocr_dp.py` | Simplified, mostly-spatial-domain (contour geometry + ink counts + template correlation, no FFT/Gabor) sibling to `stat_ocr_fft.py`; pct-line only, val is a real no-op stub. Selectable via `main.py --stat-ocr-engine dp` (decisions.txt #78) — the first time this exploratory family has had a production entry point; val stays `None` on every cell unless `--stat-tess-fallback` (off by default) is passed. No normalization of any kind (every glyph used at its native tight-crop size) and its own self-derived '0'/'6'/'9' centroid calibration (`gfl2/calibration/calibrate_dp.py`), not reused from `stat_ocr_fft.py` (known_issues.txt §31, decisions.txt #76/#77). Two open concerns: the module name is now misleading (most leaves don't use cv2.approxPolyDP), and `classify()` has no confidence-based abstention — every leaf always answers (action_items.txt #28/#29) |
| `score_ocr_dp.py` | Daily Gunsmoke HEADER SCORE reader for `--stat-ocr-engine dp` (known_issues.txt §33, decisions.txt #85-#87). Multi-Otsu adaptive-threshold segmentation (fixes the shared pipeline's silent adjacent-digit-merge drop, e.g. "44"→"07") plus a real `classify_score()` tree — a COPY (not import) of `stat_ocr_dp.py`'s spatial-primitive design, its own gate constants calibrated via `gfl2/calibration/calibrate_score_dp.py` from real Daily Gunsmoke score crops (not the `glyph_daily_score.png` atlas — interval gates need the real corpus distribution). No normalization, no internal Tesseract fallback — every leaf decides or abstains to '?'; daily_gunsmoke.py's separate external Tesseract score fallback is unaffected. 100.0% glyph / 99.4% whole-score accuracy on single/*.png (one miss: gm_d_20250908.png's known different-resolution outlier, §18) |
| `header_ocr_dp.py` | Daily Gunsmoke header STATS ROW (dealt/taken/turns) reader for `--stat-ocr-engine dp` (known_issues.txt §34, decisions.txt #89). Same dp-family design as `stat_ocr_dp.py`/`score_ocr_dp.py`, built from `assets/fonts/glyph_daily_header.png` (0-9/K/M) and corpus-calibrated via `gfl2/calibration/calibrate_header_dp.py`. Two NEW leaves this dp family hasn't needed before: M isolated by raw glyph WIDTH ALONE, checked before the isoperimetric-ratio root gate; K isolated within the non-circular branch via a LEFT-anchored ink count (`_band_count_left`, the TOP-band mechanism transposed to columns). Also fixes a real adjacent-digit-merge bug ("44" merging into one wide blob and being swallowed by the new M-width gate) via a merge-split step in `isolate_header_blobs()` — the opposite threshold direction from `score_ocr_dp.py`'s own ladder, since this field's ink polarity is reversed. 100.0% glyph accuracy on single/*.png; 99.8% true whole-field accuracy once a separate, documented (not fixed) GT-bleed artifact is excluded (a trailing label letter — 's'/'n' — occasionally hallucinated as a leading digit by the Tesseract ground truth itself, known_issues.txt §34) |
| `timing.py` | Hierarchical wall-clock timer (`with t.timed("x"): ...`) |
| `trace.py` | Per-function timing output when `GFL2_TRACE=1` |

### Data flow

**Weekly Gunsmoke** (`main.py <img> --pattern weekly_gunsmoke`):
1. `layout.py` segments image into row crops (horizontal brightness projection)
2. Per row: owner name → Tesseract OCR; buff → `buff_ocr` projection/Tesseract; dolls → `asset_mapper` pHash+histogram; score → blob/Hu pipeline (default) or Tesseract
3. Output: `<image>.csv` with columns `date,ownerName,buffName,doll1…5,score`

**Daily Gunsmoke** (`main.py <img> --pattern daily_gunsmoke`):
1. Split image into 1–2 side-by-side panels
2. Per panel: parse header bar (stat totals) → `stat_ocr` blob pipeline; parse 5 doll rows → `doll_name_ocr` projection; save portraits to `assets/dolls/`
3. Output: appends to `daily_gunsmoke.js` as a JS constant, deduplicated by `(filename, report_idx)`

### Asset directories
- `assets/dolls/` — doll portrait PNGs (`_Name.png`); unknowns saved as GUIDs for manual rename
- `assets/buff/` — buff icon crops used by `buff_ocr` projection matching
- `assets/doll_names/templates.json` — projection feature vectors for doll name OCR
- `assets/fonts/stat_pct.json` + `stat_val.json` — digit templates for `stat_ocr`
- `assets/fonts/stat_header.json` — digit templates for Daily GS header stats
- `assets/fonts/score_digits.json` — score digit templates shared by weekly + daily GS

### Two-pipeline pattern
Throughout the codebase, fast custom pipeline (blob + 1D projection correlation) runs first; Tesseract is a fallback. The blob pipeline is always preferred on Windows due to known Tesseract state degradation (see known_issues.txt §1). When adding a new recognizer, follow this pattern: build templates with a `--build` flag, store as JSON, and keep binarization thresholds identical between build and inference.
