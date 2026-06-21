# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@reference.txt
@docs/known_issues.txt

## Build & test
- Compile: `python compile_gfl2.py`  (must run after any source change — Windows .pyc invalidation)
- Test all: `pytest tests/ -q --no-header --tb=no`
- Test single: `pytest tests/test_weekly_gunsmoke.py -q --no-header --tb=short`

## Windows / NTFS note
File edits via the Edit tool can silently truncate on NTFS.
After any edit, verify syntax with:
  python -c "import ast; ast.parse(open('PATH').read()); print('ok')"
If truncated, restore the tail with `cat >> FILE << 'PYEOF' ... PYEOF`.

## Key conventions
- Projection correlation threshold: PROJ_CORR_MIN = 0.70 (combined v+h)
- Val templates: NORM_W_VAL=8, NORM_H_VAL=13  |  Pct templates: NORM_W_PCT=12, NORM_H_PCT=20
- Build and inference MUST use the same binarization threshold and blob filters
- Never lower PROJ_CORR_MIN globally; add targeted shortcuts with gap guards instead
- Asset files prefixed with `_` are known-mapped; the prefix is stripped in output

## Architecture

### Entry points
| Script | Purpose |
|---|---|
| `main.py` | Primary CLI: routes image(s) to the right pattern parser |
| `compile_gfl2.py` | Force-recompiles `gfl2/` package (hash-based invalidation) |
| `assets/builders/build_header_templates.py` | Rebuild header stat templates from `single/ib_d_*.png` |
| `assets/builders/populate_doll_assets.py` | Auto-extract doll portraits from Daily Gunsmoke images |
| `assets/builders/rebuild_assets.py` | Re-crop buff/doll assets from a reference image |
| `debugs/score_detect.py` | Benchmark/rebuild digit templates in `score_set/` |
| `debugs/debug_layout.py` | Annotate Weekly Gunsmoke column positions for diagnosis |
| `debugs/debug_header.py` | Annotate Daily Gunsmoke header/stats crop regions |
| `debugs/render_debug.py` | Render Weekly Gunsmoke CSV as a visual icon grid |

### gfl2/ package modules
| Module | Role |
|---|---|
| `patterns/weekly_gunsmoke.py` | Weekly Gunsmoke CSV parser (date, owner, buff, 5 dolls, score) |
| `patterns/daily_gunsmoke.py` | Daily Gunsmoke JS parser v1 (header stats + per-doll rows) |
| `patterns/daily_gunsmoke2.py` | Daily Gunsmoke JS parser v2 (experimental, standalone CLI) |
| `dg_output.py` | Shared JS model + save logic used by both DG parsers |
| `layout.py` | Weekly Gunsmoke row/column extractor (binarization-based anchor detection) |
| `asset_mapper.py` | Visual doll/buff lookup: pHash → HSV histogram → unknown |
| `buff_ocr.py` | Buff name recognition: projection matching (fast) → Tesseract fallback |
| `doll_name_ocr.py` | Projection-based doll name classifier (no Tesseract needed) |
| `stat_ocr.py` | Blob + projection/Hu OCR for DG stat numbers (pct and val lines) |
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
- `assets/stat_fonts/default/templates.json` — digit templates for `stat_ocr`
- `score_set/digit_templates.json` — digit templates for the score blob pipeline

### Two-pipeline pattern
Throughout the codebase, fast custom pipeline (blob + 1D projection correlation) runs first; Tesseract is a fallback. The blob pipeline is always preferred on Windows due to known Tesseract state degradation (see known_issues.txt §1). When adding a new recognizer, follow this pattern: build templates with a `--build` flag, store as JSON, and keep binarization thresholds identical between build and inference.
