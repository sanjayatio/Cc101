# -*- coding: utf-8 -*-
"""
gfl2/extraction/score.py -- Daily Gunsmoke header SCORE field extraction
for the legacy pipeline (v0_1_0/v0_1_1/v0_2_0, i.e. whenever main.py does
not inject a `score_ocr` engine into gfl2.patterns.daily_gunsmoke.parse()).

Moved verbatim from gfl2/patterns/daily_gunsmoke.py's private
_header_isolate_blobs() (docs/known_issues.txt §33, decisions.txt #103) --
a pure relocation, no logic change. Its known limitation (the escalating
THRESH_VAL+delta ladder can silently DROP an adjacent identical-digit
pair like "44", with no '?' marker -- see known_issues.txt §33) is
UNCHANGED by this move.

Structural sibling: gfl2.score_ocr_v0_3_0.isolate_score_blobs() is the
`--stat-ocr-engine v0_3_0` equivalent for this same field -- a separate,
independent implementation (multi-Otsu adaptive threshold, not this
module's fixed-ladder), kept apart on purpose (docs/decisions.txt #47,
#75's "write everything twice" policy): the two are peers in the same
pipeline stage, not a shared function with a branch.
"""
import cv2
import numpy as np


def isolate_score_blobs_legacy(gray: np.ndarray, inv: bool = False) -> list:
    """Find digit blobs in a crop.  inv=True for dark-on-light text.

    Returns [(x, norm, w, h, n_inner)] where n_inner is the count of interior
    contours (holes) within the blob — used to disambiguate digits like 5 vs 6.
    """
    from gfl2.score_ocr import (THRESH_VAL, NORM_W, NORM_H,
                                DIGIT_MIN_W, DIGIT_MAX_W, DIGIT_MIN_H, DIGIT_MAX_H)
    mode = cv2.THRESH_BINARY_INV if inv else cv2.THRESH_BINARY

    # Width above which a blob is likely two merged digits.
    _MERGE_W = int(NORM_W * 1.3)   # ≈ 26 px

    def _raw_blobs(thresh):
        cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out = []
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            out.append((x, y, w, h))
        out.sort(key=lambda b: b[0])
        return out

    def _normalize(thresh, x, y, w, h):
        sub = thresh[y:y+h, x:x+w]
        return cv2.resize(sub, (NORM_W, NORM_H), interpolation=cv2.INTER_AREA)

    def _count_holes(thresh, x, y, w, h):
        sub = thresh[y:y+h, x:x+w]
        _, hier = cv2.findContours(sub, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if hier is None:
            return 0
        return int(sum(1 for hh in hier[0] if hh[3] >= 0))

    _, thresh_lo = cv2.threshold(gray, THRESH_VAL, 255, mode)
    blobs_lo = _raw_blobs(thresh_lo)

    # Find the lowest threshold increment that separates any merged digit pair.
    # Using the smallest effective delta keeps stroke shapes closest to the
    # templates (which were built at THRESH_VAL).
    thresh_hi = None
    blobs_hi  = []
    for _delta in (5, 10, 15, 20):
        _, _t = cv2.threshold(gray, THRESH_VAL + _delta, 255, mode)
        _rb   = _raw_blobs(_t)
        if len(_rb) > len(blobs_lo):
            thresh_hi = _t
            blobs_hi  = _rb
            break
    if thresh_hi is None:
        _, thresh_hi = cv2.threshold(gray, THRESH_VAL + 10, 255, mode)
        blobs_hi     = _raw_blobs(thresh_hi)

    result = []
    for bx, by, bw, bh in blobs_lo:
        if not (DIGIT_MIN_H <= bh <= DIGIT_MAX_H):
            continue
        if DIGIT_MIN_W <= bw <= _MERGE_W:
            # Normal blob — normalize from the primary threshold image so the
            # pixel shape matches templates built at the same threshold.
            n_inner = _count_holes(thresh_lo, bx, by, bw, bh)
            result.append((bx, _normalize(thresh_lo, bx, by, bw, bh), bw, bh, n_inner))
        elif bw > _MERGE_W:
            # Merged blob — use higher-threshold detections that fall within this
            # blob's x-range to find the split sub-blobs.  Each sub-blob is
            # normalized from thresh_hi so its boundaries are clean; the higher
            # threshold is the minimum delta that achieved the separation, so
            # stroke shapes stay as close as possible to the 150-threshold templates.
            sub_hi = [(hx, hy, hw, hh) for hx, hy, hw, hh in blobs_hi
                      if DIGIT_MIN_W <= hw <= _MERGE_W
                      and DIGIT_MIN_H <= hh <= DIGIT_MAX_H
                      and hx >= bx and hx + hw <= bx + bw + 2]
            for hx, hy, hw, hh in sub_hi:
                nx  = max(0, hx);  nx1 = min(thresh_hi.shape[1], hx + hw)
                ny  = max(0, hy);  ny1 = min(thresh_hi.shape[0], hy + hh)
                n_inner = _count_holes(thresh_hi, nx, ny, nx1 - nx, ny1 - ny)
                result.append((hx, _normalize(thresh_hi, nx, ny, nx1 - nx, ny1 - ny),
                               hw, hh, n_inner))
            # If no valid sub-blobs at higher threshold, the merged blob is dropped.
    result.sort(key=lambda b: b[0])
    return result
