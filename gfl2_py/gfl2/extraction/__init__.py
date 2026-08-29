# -*- coding: utf-8 -*-
"""
gfl2/extraction/ -- namespace for Daily Gunsmoke field-EXTRACTION
(segmentation / digit-blob-isolation) implementations that are not owned
by one specific engine.

Every Daily Gunsmoke field-reading pipeline (score, header stats-row,
stat-cell pct/val) goes through the same three stages:

    A. clustering / ROI-finding -- locate the panel, the doll-row frames,
       the header bar, the stat-cell columns.
    B. extraction -- binarize a located crop and isolate it into digit
       blobs, ready for classification.
    C. detection -- classify the isolated glyphs into a string.

Stage A is genuinely engine-independent and lives centrally in
gfl2/patterns/daily_gunsmoke.py (_split_panels, _find_all_frames,
_group_frames_into_panels, _find_frames) -- every engine shares it as-is.

Stage C is genuinely engine-specific and lives one-per-engine
(classify()/classify_val() in each gfl2/stat_ocr_v0_x_x.py,
classify_score() in gfl2/score_ocr_v0_3_0.py, classify_header() in
gfl2/header_ocr_v0_3_0.py) -- per this project's "write everything twice"
policy (docs/decisions.txt #47, #75): duplication here is deliberate, not
an oversight -- it keeps each engine's classifier independently tunable
without risking a shared-code regression to a sibling engine.

Stage B is where this project's structure had drifted: for the SCORE and
HEADER STATS-ROW fields, v0_1_0/v0_1_1/v0_2_0's extraction had no home of
its own -- it lived as ad hoc/inline code inside daily_gunsmoke.py, while
v0_3_0's own extraction (gfl2/score_ocr_v0_3_0.py's isolate_score_blobs,
gfl2/header_ocr_v0_3_0.py's isolate_header_blobs) was already properly
self-contained. This package gives that orphaned code a real, discoverable
home, WITHOUT merging it into v0_3_0's implementation -- the two stay
separate, each free to evolve independently, exactly like every other
pair of "write everything twice" peers in this project. See
docs/known_issues.txt §33 and docs/decisions.txt #103.

Per-field map of where stage B currently lives:

    field              v0_1_0 / v0_1_1 / v0_2_0            v0_3_0
    -----------------  -----------------------------------  ------------------------------
    score              gfl2.extraction.score                gfl2.score_ocr_v0_3_0
                         .isolate_score_blobs_legacy()         .isolate_score_blobs()
    header stats-row   gfl2.extraction.header_stats          gfl2.header_ocr_v0_3_0
                         .isolate_header_stats_blobs_legacy()  .isolate_header_blobs()
    stat-cell pct/val  each gfl2.stat_ocr_v0_x_x.py owns its own extraction internally
                       (already self-contained -- not moved here; see decisions.txt #103)

Nothing in this package changes any engine's behavior -- every function
here is either a verbatim relocation or a straightforward de-inlining of
code that already existed, unchanged, elsewhere.
"""
