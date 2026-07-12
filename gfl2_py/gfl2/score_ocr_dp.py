# -*- coding: utf-8 -*-
"""
gfl2/score_ocr_dp.py -- Daily Gunsmoke header-score reader, multi-Otsu
adaptive-threshold variant. SEGMENTATION-ONLY SCAFFOLD (known_issues.txt
§33, decisions.txt #85/#86) -- classification is a real no-op stub today.

BACKGROUND: gfl2/patterns/daily_gunsmoke.py's shared score pipeline
(score_ocr.THRESH_VAL=150 + an escalating +5/+10/+15/+20-delta ladder,
_header_isolate_blobs) can silently DROP an adjacent identical-digit pair
(e.g. "44") -- the ladder stops at the FIRST delta whose blob count
increases at all, which can reflect an unrelated partial separation
elsewhere in the crop rather than the genuinely merged pair splitting.
Confirmed via a live parse() call: single/fb_d_20251019.png panel 2's real
score "4407" reads back as "07", with no '?' marker anywhere to flag the
loss. Corpus-wide, at least 10 of 20 score/Tesseract mismatches across
single/*.png share this exact signature.

A per-crop multi-level (3-class) Otsu threshold -- copied (not imported;
see WHY COPIED below) from gfl2.stat_ocr_dp._multi_otsu_2thresh, which has
the full algorithm derivation -- correctly isolates all digit blobs in
156/157 score crops in single/*.png (the one exception, gm_d_20250908.png,
is the corpus's own known different-capture-resolution outlier,
known_issues.txt §18 -- NOT solved by this alone; see §33's caveat that
this direction is not a complete cross-resolution fix).

WHY SEGMENTATION-ONLY: wiring this same adaptive threshold into
CLASSIFICATION too (i.e. re-binarizing each digit crop at the new
threshold before matching against assets/fonts/score_digits.py) was tried
directly and found to net-REGRESS accuracy corpus-wide -- 68 regressed vs.
7 fixed out of 88 changed reads (known_issues.txt §33's ATTEMPTED, THEN
REVERTED entry). Root cause: score_digits.py's templates were trained on
glyphs extracted at THRESH_VAL=150 specifically -- the fixed threshold and
the templates are a matched, mutually-consistent pair, even though
THRESH_VAL=150 itself is not derived from anything principled. Swapping
only the segmentation side breaks that match (a real "double negative":
one skewed value upstream, silently compensated by a correspondingly
skewed value downstream -- see docs/takeaways.txt #78). A real fix needs
its OWN templates, trained consistently at THIS module's adaptive
threshold -- not yet built (docs/action_items.txt #33).

WHY COPIED, NOT IMPORTED: this module and gfl2/stat_ocr_dp.py are peer
"dp-family" exploratory modules (both MIXED scope, both reachable via
`main.py --stat-ocr-engine dp`) -- gfl2/patterns/daily_gunsmoke.py (MAIN)
must not depend on either of them (main.py alone picks concrete engine
classes; daily_gunsmoke.py stays engine-agnostic, see parse()'s own
docstring), and this module avoids a peer-to-peer import for the same
"write it twice rather than couple two independent exploratory engines"
reason gfl2/stat_ocr_dp.py itself was built by copying out of
gfl2/stat_ocr_fft.py (decisions.txt #75).

SELECTION: `main.py --stat-ocr-engine dp` constructs a ScoreOcrDp
alongside gfl2.stat_ocr_dp.StatOcrDp and injects it into
gfl2.patterns.daily_gunsmoke.parse(..., score_ocr=...). Every other
--stat-ocr-engine selection (production, padded, fft) leaves score_ocr=None,
which keeps daily_gunsmoke.py's original score pipeline completely
unchanged -- confirmed byte-identical (known_issues.txt §33).
"""
from __future__ import annotations
import cv2
import numpy as np

from gfl2.score_ocr import DIGIT_MIN_W, DIGIT_MAX_W, DIGIT_MIN_H, DIGIT_MAX_H


def _multi_otsu_2thresh(gray: np.ndarray) -> "tuple[int, int]":
    """Fast 3-class Otsu thresholding (Liao, Chen & Chung, 2001) via
    cumulative histogram zeroth/first-order moments -- O(256^2) candidate
    (t1, t2) pairs instead of the naive O(256^3) recomputation. Returns
    (t1, t2): t1 is the boundary between the darkest class and the middle
    class; t2 is the boundary between the middle class and the brightest
    class. Copied verbatim from gfl2.stat_ocr_dp._multi_otsu_2thresh --
    see this module's own docstring (WHY COPIED) for why, and that
    function's docstring for the algorithm citation."""
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    total = float(hist.sum())
    if total <= 0:
        return 128, 128
    p = hist / total
    idx = np.arange(256, dtype=np.float64)
    cum_p0 = np.cumsum(p)
    cum_p1 = np.cumsum(idx * p)

    def _sigma(a: int, b: int) -> float:
        w = cum_p0[b] - (cum_p0[a - 1] if a > 0 else 0.0)
        if w <= 1e-12:
            return 0.0
        mu = cum_p1[b] - (cum_p1[a - 1] if a > 0 else 0.0)
        return (mu * mu) / w

    best_var, best_t1, best_t2 = -1.0, 0, 1
    for t1 in range(0, 254):
        s01 = _sigma(0, t1)
        for t2 in range(t1 + 1, 255):
            between_var = s01 + _sigma(t1 + 1, t2) + _sigma(t2 + 1, 255)
            if between_var > best_var:
                best_var, best_t1, best_t2 = between_var, t1, t2
    return best_t1, best_t2


def _score_otsu_threshold(gray: np.ndarray) -> int:
    """t2 -- the ink-halo/background boundary -- because Daily Gunsmoke's
    header-bar score text is BRIGHT-on-DARK, the opposite ink polarity
    from gfl2.stat_ocr_dp's dark-on-light pct strips (where t1, the
    darker ink/halo boundary, is the useful one). Recomputed fresh per
    crop, never cached: known_issues.txt §32/decisions.txt #83 already
    found a per-run-shared threshold cache can let one image's value leak
    into another's read -- recomputing per crop (O(256^2), a few ms) is
    cheap enough here (called once or twice per image) to just avoid that
    whole failure class outright."""
    _t1, t2 = _multi_otsu_2thresh(gray)
    return t2


def isolate_score_blobs(gray: np.ndarray) -> "list[tuple[int, int, int, int]]":
    """Return digit-shaped (x, y, w, h) blobs for a score crop, sorted
    left-to-right, using this module's per-crop adaptive threshold instead
    of daily_gunsmoke.py's fixed-THRESH_VAL escalating-delta ladder.
    Corpus-validated (known_issues.txt §33): blob count matches Tesseract
    ground-truth digit-string length for 156/157 score crops in
    single/*.png, including every "adjacent-44-dropped" case the fixed
    ladder is known to miss. The one exception, gm_d_20250908.png, is the
    corpus's own already-tracked different-resolution outlier (§18)."""
    t = _score_otsu_threshold(gray)
    _, thresh = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if DIGIT_MIN_W <= w <= DIGIT_MAX_W and DIGIT_MIN_H <= h <= DIGIT_MAX_H:
            blobs.append((x, y, w, h))
    blobs.sort(key=lambda b: b[0])
    return blobs


class ScoreOcrDp:
    """Alternate Daily Gunsmoke header-score reader, injected via
    gfl2.patterns.daily_gunsmoke.parse(..., score_ocr=...) when
    `main.py --stat-ocr-engine dp` is selected. SEGMENTATION-ONLY today --
    read_score() always returns None (a genuine no-op stub, matching
    gfl2.stat_ocr_dp.StatOcrDp's own val-line precedent) so daily_
    gunsmoke.py's existing unconditional Tesseract score fallback picks up
    every read instead of a template-mismatched guess. isolate_score_blobs()
    above is the real, validated piece; classification needs its own
    matched templates, not yet built (docs/action_items.txt #33)."""

    @classmethod
    def load(cls) -> "ScoreOcrDp":
        return cls()

    def read_score(self, gray: np.ndarray, return_partial: bool = False) -> "str | None":
        """Always None -- see class docstring. Kept as a real method (not
        just the module-level isolate_score_blobs()) so daily_gunsmoke.py's
        score section can call it exactly like it would call any future
        engine's read_score(), without knowing which concrete class it
        got (mirrors the stat_ocr injection contract)."""
        return None
