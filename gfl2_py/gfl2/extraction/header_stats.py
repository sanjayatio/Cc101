# -*- coding: utf-8 -*-
"""
gfl2/extraction/header_stats.py -- Daily Gunsmoke header STATS ROW
(dealt/taken/turns) field extraction for the legacy pipeline
(v0_1_0/v0_1_1/v0_2_0, i.e. whenever main.py does not inject a
`header_ocr` engine into gfl2.patterns.daily_gunsmoke.parse()).

Extracted from a previously UNNAMED inline closure (`_read_stat_crop`,
defined inside gfl2/patterns/daily_gunsmoke.py's _extract_header()) --
not a behavior change, just giving code that was already there a real,
independently-readable name (docs/known_issues.txt §33, decisions.txt
#103). The classification half of that closure (_extract_val_glyphs +
_reconstruct_val, both from gfl2.stat_ocr_v0_1_0) stays in
daily_gunsmoke.py -- this module is extraction only.

Structural sibling: gfl2.header_ocr_v0_3_0.isolate_header_blobs() is the
`--stat-ocr-engine v0_3_0` equivalent for this same field -- a separate,
independent implementation (its own merge-split re-threshold step, not
this module's fixed single-threshold pass), kept apart on purpose
(docs/decisions.txt #47, #75's "write everything twice" policy).
"""
import cv2
import numpy as np

# Lower threshold separates touching digits (e.g. '4'+'8' merge at 180).
# Min-height 12 filters comma blobs (h≈5-7) and UI-chrome noise (h<10).
HDR_THRESH     = 155
HDR_BLOB_MIN_H =  12


def _drop_label_bleed(blobs: list, gap_thresh: int = 15) -> list:
    """Drop blobs to the left of the first inter-blob gap > gap_thresh px.

    Handles label chars (e.g. trailing 't' of "Damage dealt") bleeding
    into the crop when the value is short; digit gaps are 2–10 px.
    """
    s = sorted(blobs, key=lambda b: b[0])
    for i in range(len(s) - 1):
        gap = s[i + 1][0] - (s[i][0] + s[i][2])
        if gap > gap_thresh:
            return s[i + 1:]
    return s


def isolate_header_stats_blobs_legacy(
    gray: np.ndarray,
    hdr_thresh: int = HDR_THRESH,
    blob_min_h: int = HDR_BLOB_MIN_H,
) -> "tuple[np.ndarray, list]":
    """Binarize a header stats-row crop and isolate its digit blobs.

    Returns (thresh, blobs) — the binarized crop (needed by the caller's
    own _extract_val_glyphs) and the filtered, label-bleed-stripped,
    y-outlier-stripped blob list [(x, y, w, h), ...]. blobs is [] if
    nothing survived filtering.
    """
    from gfl2.stat_ocr_v0_1_0 import BLOB_MIN_W, BLOB_MAX_W, BLOB_MAX_H, _filter_y_outliers

    _, thresh = cv2.threshold(gray, hdr_thresh, 255, cv2.THRESH_BINARY_INV)
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    raw_blobs = []
    for _c in cnts:
        _x, _y, _w, _h = cv2.boundingRect(_c)
        if (BLOB_MIN_W <= _w <= BLOB_MAX_W
                and blob_min_h <= _h <= BLOB_MAX_H):
            raw_blobs.append((_x, _y, _w, _h))
    blobs = _drop_label_bleed(_filter_y_outliers(
        sorted(raw_blobs, key=lambda b: (b[1], b[0]))))
    return thresh, blobs
