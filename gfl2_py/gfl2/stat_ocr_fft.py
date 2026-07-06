# -*- coding: utf-8 -*-
"""
gfl2/stat_ocr_fft.py — FFT+Gabor nearest-centroid variant of gfl2/stat_ocr.py.

STATUS: EXPLORATORY / INCOMPLETE. Promoted from debugs/debug_pct_classify.py +
debugs/pct_fft_predict.py so this line of research stands parallel to
gfl2/stat_ocr.py (production, projection+Hu) and gfl2/stat_ocr_padded.py
(padded-normalize projection variant) — same class shape, same read()/
_read_line() dispatch, same timer instrumentation — but it is NOT registered
in main.py's `--stat-ocr-engine` selector and is not a drop-in production
candidate the way padded is (docs/decisions.txt decision 47). Two concrete
gaps keep it there:

  1. val-line classification was never built (docs/known_issues.txt §15's
     exploration only trained FFT+Gabor centroids for pct-line digits).
     _extract_val_glyphs()/_reconstruct_val() below are real, callable
     no-op functions — not omissions — kept purely so this class's
     _read_line() dispatch has the identical call shape as
     StatOcr/StatOcrPadded's. They always return "no glyphs"/None.
  2. pct accuracy itself is far below production even with padding
     (61-75% answered at ~99.8% accuracy on what IS answered, but '6'/'9'
     specifically resolve confidently only ~6-10% of the time — see
     known_issues.txt §15's full A/B numbers).

WEDGE FEATURE: an 8-sector Fourier angular-energy feature was tried and
measured here (see known_issues.txt §15's ablation) — it individually
carries real signal (100% of its dims exceed the noise floor by F-ratio,
vs 4.7% for the FFT histogram) and combined with Gabor alone reaches 89.7%
answered at 94.0% accuracy, a genuinely strong standalone pair.  It has
since been removed from compute_features() below by explicit decision, but
_wedge_bin_map()/_wedge_energies() are deliberately left in this file,
unused rather than deleted — do not remove them; re-enabling wedge is a
one-line change to compute_features() if a future session wants it back.

WHY IT'S KEPT ANYWAY: the point of this exploration was never accuracy
parity — it was whether a nearest-centroid lookup on a fixed-length feature
vector could be FASTER and LOWER-VARIANCE per cell than production's
multi-phase projection+Hu classifier (hole-count pre-filter -> v/h
projection correlation against every template -> Hu-moment tiebreaker,
gfl2/stat_ocr.py:_classify). This module exists so that question stays
answerable: StatOcrFft.load() + .read(cell) slots into the exact same
`.load()`/`.read(cell)` shape debugs/stat_ocr_bench.py already benchmarks
production against padded with, and `--verify` below reports per-cell
classify mean/stdev on every run — not just accuracy — so speed/variance
claims can be checked empirically instead of asserted. No such comparison
has been run yet; this module makes it possible without further plumbing.

DIVERGENCE FROM DECISION 47's DUPLICATION POLICY: gfl2/stat_ocr_padded.py is
a deliberate FULL duplicate of gfl2/stat_ocr.py (no shared code) because it
is a live production-parity candidate — decision 47 wanted zero coupling
risk between it and production. This module is not at that stage (see gaps
above), so it imports shared blob/glyph-extraction primitives directly from
gfl2.stat_ocr and gfl2.stat_ocr_padded (_binarize, _find_blobs,
_filter_y_outliers, _extract_pct_glyphs, _normalize_glyph, _collect_cells)
rather than re-duplicating ~200 lines of unrelated line-splitting code for a
classifier that doesn't do val yet. Only the feature/classifier layer
(FFT+Gabor features, nearest-centroid + confidence gate) is this module's
own. See docs/decisions.txt for the addendum recording this choice.

Character set: pct-line digits 0-9 only ('.' handled structurally by blob
size, '%' stripped structurally — both reused from the imported
_extract_pct_glyphs, unchanged from production/padded).

TWO-AGENT CLASSIFIER (2026-07-04): _classify() is NOT a single nearest-
centroid lookup over the full feature vector — an experiment concatenating
everything into one vector and z-normalizing it as a block showed the
histogram's contribution is either invisible (unnormalized: its bins are
~1000x smaller in magnitude than paren/gabor/ring, so they never move an
L2 distance) or actively harmful to '6'/'9' (normalized: it dilutes paren's
current outsized, accidentally-load-bearing scale).  Both are artifacts of
forcing two feature blocks that answer different questions to share one
distance metric.  Restructured into two independent agents instead:
  Agent A (gpr): gabor+paren+ring, unnormalized, margin gate CONF_A_DEFAULT.
  Agent B (hist): the 64-bin histogram, z-score normalized using its own
    training mean/std, margin gate CONF_B_DEFAULT -- tuned independently
    (0.05, not 0.15) because it lives in a differently-scaled margin space;
    reusing Agent A's threshold made Agent B answer nothing at all.
  Dispute rule: try A first; if A is confident, use it (this is the
    strong classifier -- ~97% standalone). If A is unsure, ask B; if B is
    confident, use B (B resolves a real, previously-unreachable slice of
    A's uncertain cases at ~92% accuracy). If both are unsure, '?'.
Measured (held-out glyphs): 96.9%->99.3% answered vs Agent A alone, with
accuracy essentially unchanged (97.5%->97.4%) and '6' recognition improving
further (130/142->138/142).  See docs/known_issues.txt §15 for the full
investigation, including the mistaken first attempt (single shared
z-normalization) and docs/takeaways.txt for the general lesson: feature
blocks that measure fundamentally different things should stay in their
own distance space with independently-tuned confidence, not get flattened
into one vector and rescaled together.

Template storage:
  assets/fonts/stat_pct_fft.py
  {"pct": {
     "gpr":        {digit: [17 floats]},   -- gabor+paren+ring+loop+vstroke+hbar centroids
     "hist":       {digit: [64 floats]},   -- z-normalized histogram centroids
     "hist_mu":    [64 floats],            -- histogram z-norm mean (training)
     "hist_sigma": [64 floats],            -- histogram z-norm stdev (training)
   }, "val": {}}   -- val is always empty

PAIR TIEBREAK (2026-07-04, DISABLED BY DEFAULT -- opt-in via
enable_pair_tiebreak / PAIR_TIEBREAK_DEFAULT): '4' and '7' share both the
'-'(gabor_90) and '/'(gabor_45) line features by construction -- both have
a top bar and a diagonal descender -- so no combination of those features
can ever cleanly separate them; the only Agent A dimension that
distinguishes them at all is paren_(.  But paren_( has anomalously high
within-class variance specifically for '4' (std 0.073 vs '7''s 0.011, 6x
any other dimension) and dominates the wrong-direction contribution in
confirmed '4'->'7' errors by >4x over every other dimension combined.

Tried GLOBALLY excluding paren_( from every comparison against the '4'
centroid: this "fixes" '4' completely but makes '4' systematically closer
to every OTHER centroid too (fewer dimensions to accumulate distance from
always shrinks a centroid's apparent distance), opening a new, larger
'9'->'4' confusion -- a net regression, and confirmation that a UNIVERSAL
per-class line/arc cascade is a dead end (symmetric problem: arc content
leaking into line-dominant glyphs implies line content leaks into
arc-dominant ones just as easily -- '3' and '0' regressed when an actual
universal lines-first cascade was tried).

The fix that actually works: scope the override to trigger ONLY when the
flat classifier's own top-2 nearest centroids are exactly a known pair
(PAIR_TIEBREAK_RULES) -- 219 of 1982 held-out glyphs for the '4'/'7' pair.
For those, and ONLY those, re-decide using the reduced dimension set
instead of trusting the confidence gate.  Every other digit's
classification is provably byte-for-byte unchanged (the flat path never
runs differently for them); '4' improves from 135/197 correct (23
misclassified as '7') to 188/197 (0 misclassified).  See
docs/known_issues.txt §15's PAIR TIEBREAK entry for the full investigation
trail, including the two dead ends (global exclusion, universal cascade)
that led here.

VSTROKE GATE (2026-07-06, DISABLED BY DEFAULT -- opt-in via
enable_vstroke_gate / VSTROKE_GATE_DEFAULT): docs/known_issues.txt §24
found the raw (non-degenerate) gabor_45 response cannot decide WHICH of
'4'/'7' a glyph is (near-total overlap), but separates the union {1,4,7}
-- vstroke's own target group -- from the arc/loop-dominant rest almost
perfectly (99.9% recall / 0.00% false-trigger, in-sample). This gate uses
that response (already computed for the gabor block, reused rather than
recomputed) to skip vstroke's expensive 2D-sliding search entirely for
glyphs judged outside that group, reporting NaN in vstroke's slot instead.
_sorted_distances drops that one dimension from the L2 distance for BOTH
the query and every centroid when it sees a NaN -- the same "exclude an
unreliable/unavailable dimension" technique PAIR_TIEBREAK_RULES already
uses, generalized from a hardcoded per-pair rule to "this dimension wasn't
measured for this glyph". Unlike the z-scored-gabor-into-Agent-A attempt
that regressed accuracy and was reverted (docs/decisions.txt #59), this
never changes what's compared -- only whether vstroke is computed at all.
Disabled by default: validated on one in-sample corpus only, not yet
held-out checked (docs/action_items.txt #8). See _vstroke_feature's own
VSTROKE GATE section for the full rationale and implementation notes.

HIERARCHICAL CLASSIFIER (2026-07-06, DISABLED BY DEFAULT -- opt-in via
enable_hierarchical / HIERARCHICAL_DEFAULT): an alternative to the flat
TWO-AGENT CLASSIFIER above, proposed directly rather than discovered by
this module's own exploration -- every weak classifier documented in this
file (gabor_45's {1,4,7} gate, vstroke, hbar, paren, inner-blob hole
count) works better as a BRANCHING decision tree than as one more
dimension crammed into a shared L2 distance, the same lesson decision 59
already learned the hard way for gabor_45 specifically. _classify_hierarchical()
implements this tree exactly:

    gabor_45 (root: {1,4,7} gate, VSTROKE_GATE_LO/HI, already validated above)
    +-- pass ({1,4,7} likely): vstroke (nearest-of-3 on ONE dimension)
    |   +-- nearest='1': return '1' -- cheap AND reliable (centroids 0.961
    |   |                  vs 0.550/0.642, both tight -- std 0.02); also
    |   |                  this group's majority class (1711/3464 glyphs)
    |   +-- nearest in {4,7}: NOT trustworthy on vstroke alone -- '4'/'7'
    |       centroids are only 0.09 apart and '4' has std 0.057, wide
    |       enough to drift past the midpoint (measured: naive nearest-of-3
    |       here misclassified 262/993 '4' glyphs as '7'). Consulted a
    |       SECOND cheap, independently-weak vote instead of jumping
    |       straight to the expensive path: gabor_45's MAX response (not
    |       the root gate's MEAN -- see GABOR_MAX_C4/C7 above
    |       _gabor45_response; free, reuses the SAME convolution the gate
    |       already computed). When vstroke's and gabor-max's picks AGREE
    |       (65.8% of {4,7} glyphs), trust the consensus directly: measured
    |       100.0% accuracy (1154/1154), zero extra feature cost. Only on
    |       DISAGREEMENT (34.2%) does this pay full compute_features()
    |       cost and resolve via the ALREADY-VALIDATED PAIR_TIEBREAK_RULES
    |       exclusion (paren_( dropped) -- reusing the existing fix for
    |       this exact pair rather than inventing a second, weaker one.
    +-- reject (arc-dominant likely): inner-blob hole count
        (gfl2.stat_ocr._count_inner_blobs, reused as-is -- production's
        own '0' has 1 hole / '8' has 2 holes / rest have 0 discriminator,
        see known_issues.txt §9/§14 -- not reimplemented here)
        +-- 2 holes: return '8' directly, no further feature computed
        +-- 1 hole: paren + loop together (nearest-of-3 on the 4-dim
        |            paren_(/paren_)/loop_top/loop_bot subspace) -> '0',
        |            '6', or '9' -- paren ALONE is not enough here either
        |            ('6' prefers '(' cleanly, but '9' lands near-neutral
        |            between paren_(/paren_) -- known_issues.txt §15's
        |            PAREN+RING entry; loop_top/loop_bot were built as
        |            exactly the '9'/'6'-targeted follow-up feature that
        |            fixes this, same section. Measured: paren alone
        |            misclassified 119/859 '6' glyphs as '9')
        +-- 0 holes: {2,3,5} -- NOT resolved by this tree (deliberately
                      omitted, no cheap 1-2 dim feature here reliably
                      separates them); falls back to the FULL flat
                      two-agent _classify() (Agent A AND Agent B, exactly
                      the path that already resolves these three digits
                      near-perfectly in the flat baseline) rather than a
                      weaker stand-in, so overall coverage and accuracy
                      for the omitted third of the corpus matches the
                      flat baseline exactly -- only these glyphs (plus a
                      misread hole-count landing here) ever pay the full
                      flat-path cost.

Every non-root decision is a nearest-centroid lookup restricted to BOTH a
reduced CANDIDATE set (only the digits still possible at that node) and a
REDUCED DIMENSION set (only the dims that node's feature(s) produce) --
reusing the SAME shipped "gpr" centroids build_templates() already trains
(no separate training pass, no rebuild), just sliced differently per node.
This is the generalization of PAIR_TIEBREAK_RULES's own technique (nearest
centroid on a reduced dimension set, scoped to a specific candidate pair)
into the primary decision path instead of only a downstream patch on it --
and it never mixes dimensions of different scales in one distance (each
node compares only same-kind values), sidestepping the exact scale-
domination trap decision 59's reverted z-scored-gabor attempt fell into.
TWO NODES NEEDED A SECOND FEATURE ONCE MEASURED (not assumed): the initial
single-dimension design for {4,7} (vstroke alone) and {0,6,9} (paren
alone) both looked plausible from the tree's own motivating structure but
measurably failed in exactly the way each feature's OWN documented history
already warned about -- see the tree notes above and docs/decisions.txt
#61 for the real numbers.

THE ARCHITECTURAL PAYOFF: unlike the flat path (which always computes all
16 gpr dims plus the 64-bin histogram for every glyph, regardless of what
digit it turns out to be), a glyph here only pays for the features on ITS
OWN root-to-leaf path -- a '1' never computes hbar, paren, ring, loop, or
inner-blob; an '8' never computes paren or loop; a '2'/'3'/'5' pays for
inner-blob (wasted) then falls through to the histogram; only '4' and '7'
end up paying the full flat-path cost. See docs/decisions.txt #61 for the
measured accuracy/timing trade-off against the flat baseline.

Build templates:
    python -m gfl2.stat_ocr_fft --build [--images <glob>]

Verify pipeline against Tesseract ground truth (+ timing/variance report):
    python -m gfl2.stat_ocr_fft --verify [--images <glob>]
"""
from __future__ import annotations
import json, sys, time, glob as _glob
from collections import defaultdict
from contextlib import nullcontext as _nullctx
from datetime import datetime
from pathlib import Path
from typing import Optional
import cv2
import numpy as np

from gfl2.stat_ocr import (
    PCT_STRIP_Y, VAL_STRIP_Y, DOT_MAX_DIM, NORM_W_PCT, NORM_H_PCT,
    _binarize, _find_blobs, _filter_y_outliers, _find_percent_x_start,
    _collect_cells, _count_inner_blobs,
)
from gfl2.stat_ocr_padded import _normalize_glyph, _extract_pct_glyphs

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE      = Path(__file__).parent.parent          # project root
_FONTS_DIR = _HERE / "assets" / "fonts"
PCT_TMPL_F = _FONTS_DIR / "stat_pct_fft.py"        # val has no template file — never built

# ── Training character set ────────────────────────────────────────────────────
TRAIN_CHARS = list("0123456789")   # pct line only; no K/M (those are val-only suffixes)

# ── Confidence gates (two-agent classifier, see module docstring) ────────────
CONF_A_DEFAULT = 0.15   # gabor+paren+ring+loop+vstroke+hbar margin; below this -> ask Agent B
CONF_B_DEFAULT = 0.05   # z-normalized histogram margin; below this -> '?'
                         # NOT the same threshold as A on purpose: A and B's
                         # margins live in unrelated distance spaces (raw vs
                         # z-normalized, 15d vs 64d) -- reusing 0.15 for B
                         # made it answer nothing (see module docstring).

# ── PAIR TIEBREAK (opt-in, see module docstring) ─────────────────────────────
# DISABLED BY DEFAULT.  Only two dead ends (global paren_( exclusion for
# '4', a universal lines-first cascade) are what this patch replaced -- see
# the module docstring's PAIR TIEBREAK section for the full story before
# adding a new entry to PAIR_TIEBREAK_RULES.  Only fires when the flat
# Agent A classifier's own top-2 nearest centroids exactly match a
# registered pair; every other classification is provably unaffected.
PAIR_TIEBREAK_DEFAULT = False

# ── VSTROKE GATE (opt-in, see the VSTROKE GATE section above _vstroke_feature) ─
# DISABLED BY DEFAULT, same convention as PAIR_TIEBREAK_DEFAULT: validated on
# one in-sample corpus (docs/known_issues.txt §24, action_items.txt #8), not
# yet held-out-checked. Skips vstroke's expensive 2D-sliding search for
# glyphs whose raw gabor_45 response falls outside the {1,4,7} line-dominant
# group's measured range.
VSTROKE_GATE_DEFAULT = False

# ── HIERARCHICAL CLASSIFIER (opt-in, see module docstring) ───────────────────
# DISABLED BY DEFAULT.  A wholesale alternative to the flat two-agent
# _classify() path (see _classify_hierarchical below), not a modifier of it --
# when enabled, _classify() dispatches to it immediately and ignores
# enable_pair_tiebreak/enable_vstroke_gate entirely (both are specific to the
# flat path's L2-over-all-dims decision, which this bypasses).
HIERARCHICAL_DEFAULT = False

_GABOR_45, _PAREN_OPEN, _PAREN_CLOSE = range(3)
# ring dims occupy indices 3..10, loop 11..12, vstroke 13, hbar_top/hbar_bottom
# 14..15 in Agent A's 16-dim feature vector (gabor_0 REMOVED 2026-07-05, see
# the N_ORIENT note above; loop + vrun ADDED same date; vrun -> vstroke +
# hbar_top/hbar_bottom ADDED later the same session; gabor_90 REMOVED later
# still, see that section's ABLATION note -- every index below shifted down
# by one accordingly).

PAIR_TIEBREAK_RULES: "dict[frozenset, np.ndarray]" = {
    # '4' vs '7': share '-' and '/' by construction (top bar + diagonal
    # descender); paren_( is the only dim that argues for '4', but it's the
    # one with anomalously high within-'4' variance -- exclude it and
    # re-decide using the remaining dims restricted to just this pair.
    frozenset({'4', '7'}): np.array([i for i in range(16) if i != _PAREN_OPEN]),
}


# ─────────────────────────────────────────────────────────────────────────────
# Feature extraction: 64-bin FFT histogram + 3-orientation Gabor + paren +
# ring.  Ported verbatim from debugs/debug_pct_classify.py — see
# docs/known_issues.txt §15 for the full history of each addition, including
# the rotation-invariance proof explaining why the (now-disabled) wedge
# feature only marginally helped '6'/'9', and the false-positive-prone
# standalone F-ratio that initially (wrongly) argued for keeping Gabor's
# 135deg orientation.  N_WEDGES / _wedge_bin_map() / _wedge_energies() below
# are intentionally kept but unused — see the module docstring's WEDGE
# FEATURE note before deleting anything here.
# ─────────────────────────────────────────────────────────────────────────────

N_BINS         = 64
_GABOR_STEP    = 4    # 45-degree angle step denominator: i*pi/_GABOR_STEP -> 0,45,90,135deg
N_ORIENT       = 1    # only 45deg -- 0deg (vertical) REMOVED 2026-07-05, replaced by N_VRUN
                       # below (see that section); 135deg was already dropped, see below; 90deg
                       # (horizontal) REMOVED later the same session -- superseded by
                       # hbar_top/hbar_bottom's targeted matched filter, see that section's
                       # ABLATION note for the real-classifier validation before removal
N_WEDGES       = 8    # unused by compute_features() — see above
N_PAREN        = 2    # '(' / ')' curve-matched-filter correlation
N_RINGS        = 8    # radial FFT magnitude energy (scale/frequency content)
N_LOOP         = 2    # top-loop / bottom-loop curve correlation, targets '9'/'6' directly
N_VRUN         = 1    # SUPERSEDED by N_VSTROKE (2026-07-05) -- kept for doc history only,
                       # not counted in N_FEAT; see the SUPERSEDED note above MAX_STROKE_W
N_VSTROKE      = 1    # 2D-sliding punished isolated-stroke match, targets '1'/'4' vs '7'
N_HBAR         = 2    # hbar_top / hbar_bottom, targets '2'/'4'/'5'/'7' -- two SEPARATE dims
N_FEAT         = N_BINS + N_ORIENT + N_PAREN + N_RINGS + N_LOOP + N_VSTROKE + N_HBAR

# gpr-relative indices (i.e. into feat_gpr = feat[N_BINS:], NOT the full feat
# vector) for the HIERARCHICAL CLASSIFIER's per-node dimension slicing --
# computed from the N_* block sizes above (not hardcoded) so they can never
# silently drift out of sync with compute_features()'s own concatenation
# order the way a hand-maintained comment could.  _GABOR_45/_PAREN_OPEN/
# _PAREN_CLOSE are defined separately below (PAIR_TIEBREAK_RULES predates
# this and already fixed those three at 0/1/2).
_RING_START   = N_ORIENT + N_PAREN                    # = 3
_LOOP_TOP_IDX = _RING_START + N_RINGS                 # = 11
_LOOP_BOT_IDX = _LOOP_TOP_IDX + 1                      # = 12
_VSTROKE_IDX  = _LOOP_BOT_IDX + 1                      # = 13
_HBAR_TOP_IDX = _VSTROKE_IDX + N_VSTROKE               # = 14
_HBAR_BOT_IDX = _HBAR_TOP_IDX + 1                      # = 15

# 135deg (backslash) DROPPED (2026-07-04): a standalone per-dimension F-ratio
# measurement (known_issues.txt §15) found it the second-strongest of the 4
# Gabor orientations and concluded it was worth keeping -- that measurement
# was misleading.  The 4 Gabor fractions sum to 1 (not independent
# measurements), so a high standalone F-ratio for one bin can just be a
# mechanical echo of another bin (0deg here, dominated by '1'/'7') absorbing
# less share.  A marginal-utility ablation (3d without 135 vs 4d with it)
# showed adding 135deg back does not add real classification value on its
# own, and once combined with the paren+ring features below it is a wash
# (99.2% vs 99.7% overall, '6'/'9' unchanged or negligibly different) — so it
# was dropped for a simpler, slightly cheaper feature vector rather than kept
# on the strength of a metric now known to overstate isolated dimensions in
# a constrained (sum-to-1) feature block.  See known_issues.txt §15 and
# docs/takeaways.txt for the general lesson.

# 0deg (vertical) DROPPED (2026-07-05): intuitively expected to separate '4'
# from '7' (one has a vertical stroke, one doesn't) but measured mean4=0.402
# vs mean7=0.390 -- statistically indistinguishable (d'=0.71, worst of the
# three orientations).  A real pair-tiebreak test confirmed it: excluding
# gabor_0 changes ZERO of 1069 real '4'/'7' decisions -- not just weak, fully
# redundant.  Replaced by N_VRUN below, a purpose-built isolated-stroke
# detector (d'=-5.31 on the same pair) instead of Gabor's diffuse local-
# orientation energy, which cannot tell "a genuine unbroken thin stroke"
# apart from "some vertical-ish edge content somewhere in the glyph".


def _fft_magnitudes(gray: np.ndarray) -> np.ndarray:
    f32 = gray.astype(np.float32) / 255.0
    mag = np.abs(np.fft.fftshift(np.fft.fft2(f32)))
    mag = np.log1p(mag)
    if mag.max() > 0:
        mag = mag / mag.max()
    return mag.ravel()


def _make_hist(mags: np.ndarray, n_bins: int) -> np.ndarray:
    idx  = (mags * (n_bins - 1)).astype(np.uint8)
    hist = np.bincount(idx, minlength=n_bins).astype(np.float64)
    if hist.sum() > 0:
        hist /= hist.sum()
    return hist


# Gabor (lambda, sigma, gamma): loaded from assets/fonts/gabor_calib.json if
# present (debugs/calibrate_gabor.py -- see its module docstring), else the
# historical hardcoded fallback (4.0, 2.0, 1.0) from the original general-
# purpose accuracy sweep in debugs/debug_pct_classify.py --tune.  The
# calibrated values target two STRUCTURAL properties instead of raw
# accuracy alone (decisive '4'/'7' line separation; stable, non-noisy line
# readings for the arc-dominant {0,3,6,8,9} group) -- see
# docs/known_issues.txt §15's GABOR CALIBRATION entry.  Re-running
# calibrate_gabor.py against a new font's training images and re-running
# `python -m gfl2.stat_ocr_fft --build` is the complete recalibration path;
# only 45/90deg are built (i in (1,2)) regardless -- 0deg and 135deg are
# both intentionally excluded, see the N_ORIENT notes above.

_GABOR_CALIB_F = _FONTS_DIR / "gabor_calib.json"
_GABOR_CALIB_DEFAULT = {"lambd": 4.0, "sigma": 2.0, "gamma": 1.0}


def _load_gabor_calib() -> dict:
    if _GABOR_CALIB_F.exists():
        calib = json.loads(_GABOR_CALIB_F.read_text(encoding="utf-8"))
        return {"lambd": calib["lambd"], "sigma": calib["sigma"], "gamma": calib["gamma"]}
    return dict(_GABOR_CALIB_DEFAULT)


_GABOR_ANGLE_IDXS = (1,)   # 45deg only -- 0deg (i=0), 90deg (i=2), 135deg (i=3) excluded


def _build_gabor_kernels(lambd: float, sigma: float, gamma: float) -> list[np.ndarray]:
    return [
        cv2.getGaborKernel((7, 7), sigma, i * np.pi / _GABOR_STEP, lambd, gamma, 0.0, cv2.CV_32F)
        for i in _GABOR_ANGLE_IDXS
    ]


def set_gabor_params(lambd: float, sigma: float, gamma: float) -> None:
    """
    Override the module-level Gabor kernels in-process, without touching
    gabor_calib.json.  Exists so debugs/calibrate_gabor.py can score a
    candidate by running the REAL build_templates()+verify() pipeline
    in-process for each (lambd, sigma, gamma) it sweeps, instead of a proxy
    metric on a partial feature vector -- see that script's module
    docstring for why a second proxy-metric attempt (LOO accuracy on the
    full 13-dim gabor+paren+ring vector, still excluding Agent B) also
    failed to predict real end-to-end accuracy.
    """
    global _GABOR_PARAMS, _GABOR_KERNELS
    _GABOR_PARAMS = {"lambd": lambd, "sigma": sigma, "gamma": gamma}
    _GABOR_KERNELS = _build_gabor_kernels(lambd, sigma, gamma)


_GABOR_PARAMS = _load_gabor_calib()
_GABOR_KERNELS = _build_gabor_kernels(**_GABOR_PARAMS)

# ── Wedge feature: DISABLED, NOT DELETED ────────────────────────────────────
# Removed from compute_features() by explicit decision despite measuring as
# a genuinely strong feature (docs/known_issues.txt §15's ablation: every
# wedge dimension individually clears the F-ratio noise floor, and
# gabor+wedge alone reaches 89.7% answered / 94.0% accuracy on the held-out
# set — better standalone coverage than the hist+gabor combination this
# module currently ships).  Do NOT delete _wedge_bin_map/_wedge_energies —
# re-enabling wedge is a one-line change in compute_features() below
# (`np.concatenate([fft_hist, gabor, _wedge_energies(gray_norm)])`), and the
# constants (N_WEDGES) are already defined above for exactly that.

_WEDGE_BIN_CACHE: dict[tuple[int, int], np.ndarray] = {}


def _wedge_bin_map(h: int, w: int, n_wedges: int) -> np.ndarray:
    """Angular-sector index per FFT pixel, folded to [0°,180°) — a real
    image's magnitude spectrum is centrosymmetric (|F(u,v)|==|F(-u,-v)|), so
    sectors spanning the full circle would just duplicate each other."""
    key = (h, w)
    cached = _WEDGE_BIN_CACHE.get(key)
    if cached is not None:
        return cached
    cy, cx = h // 2, w // 2
    ys, xs = np.indices((h, w))
    angles = np.degrees(np.arctan2(ys - cy, xs - cx)) % 180
    bins = np.minimum((angles / 180 * n_wedges).astype(int), n_wedges - 1)
    _WEDGE_BIN_CACHE[key] = bins
    return bins


def _wedge_energies(gray_norm: np.ndarray, n_wedges: int = N_WEDGES) -> np.ndarray:
    """Fraction of FFT magnitude energy in each angular sector (DC excluded).
    Not currently called by compute_features() — see the DISABLED note above."""
    f32 = gray_norm.astype(np.float32) / 255.0
    mag = np.abs(np.fft.fftshift(np.fft.fft2(f32)))
    h, w = mag.shape
    mag[h // 2, w // 2] = 0.0
    bins = _wedge_bin_map(h, w, n_wedges)
    energies = np.array([mag[bins == i].sum() for i in range(n_wedges)])
    total = energies.sum() + 1e-9
    return energies / total


# ── Paren feature: chirality-sensitive curve-matched filters ─────────────────
# Unlike Gabor/wedge (both derived from FFT magnitude or oriented local energy,
# both blind to a glyph's exact 180°-rotation per known_issues.txt §15's
# rotation-invariance proof), a whole-glyph correlation against an asymmetric
# spatial template CAN in principle break that symmetry — rot180(t) != t for
# these two templates (rotating '(' by 180° gives ')'), so they are exactly
# the kind of "spatially local, chirality-sensitive" feature that section
# concluded was needed.
#
# MEASURED (training-data ablation, see known_issues.txt §15's PAREN/RING
# entry): F-ratio '('=5.07, ')'=3.38 — both comfortably clear the noise floor,
# on par with the strongest Gabor orientations.  '6' shows a clean '('
# preference (+0.14 gap over ')'). '9' does NOT show the mirror ')'
# preference expected if '9' were an exact rotation of '6' — it lands
# near-neutral between the two.  So this is a real, useful digit feature in
# general, and a partial (not full) win for the '6'/'9' collision
# specifically: it helps flag '6', not '9'.

_PAREN_TEMPLATE_CACHE: dict[tuple[int, int], tuple[np.ndarray, np.ndarray]] = {}


def _paren_templates(h: int, w: int) -> tuple[np.ndarray, np.ndarray]:
    """Build (and cache) the '(' and ')' curve templates at (h, w) resolution.
    '(' bulges left (opens right); ')' bulges right (opens left) — mirror
    images of each other, drawn as a half-ellipse arc spanning the full
    glyph height."""
    key = (h, w)
    cached = _PAREN_TEMPLATE_CACHE.get(key)
    if cached is not None:
        return cached
    axes = (max(1, w - 2), h // 2 + 2)
    open_t = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(open_t, (w - 1, h // 2), axes, 0, 90, 270, 255, thickness=2)
    close_t = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(close_t, (0, h // 2), axes, 0, -90, 90, 255, thickness=2)
    _PAREN_TEMPLATE_CACHE[key] = (open_t, close_t)
    return open_t, close_t


def _norm_xcorr(a: np.ndarray, b: np.ndarray) -> float:
    """Normalized cross-correlation (cosine similarity of mean-subtracted,
    flattened images) — scale/brightness-invariant whole-image match score."""
    af = a.astype(np.float64).ravel() - a.mean()
    bf = b.astype(np.float64).ravel() - b.mean()
    denom = (np.linalg.norm(af) * np.linalg.norm(bf)) + 1e-9
    return float(np.dot(af, bf) / denom)


def _paren_features(gray_norm: np.ndarray) -> np.ndarray:
    """Return [corr_with_'(' , corr_with_')'] for a glyph."""
    h, w = gray_norm.shape
    open_t, close_t = _paren_templates(h, w)
    return np.array([_norm_xcorr(gray_norm, open_t), _norm_xcorr(gray_norm, close_t)])


# ── Loop feature: '9'/'6'-targeted partial-arc curve-matched filters ─────────
# paren_(/paren_) (above) span the FULL glyph height, which is why they help
# '6' (clean '(' preference) but land near-neutral on '9' (known_issues.txt
# §15's PAREN/RING entry): '9's loop only occupies the upper ~35% of the
# glyph, so a full-height arc dilutes against the tail below it. Found by a
# parameter sweep over the SAME kind of half-ellipse arc used by paren, but
# with a shrunk vertical radius and a shifted centroid instead of the
# full-height span: cy=0.35h/ry=0.20h/rx=0.80w, side='open', peaks cleanly on
# '9' (mean=0.318 vs next-highest competitor 0.093 -- gap 0.225, corpus-wide).
# 'loop_bot' is the vertical mirror (cy=0.65h) -- confirmed by an independent
# sweep targeting '6' directly that the mirror lands close to optimal on its
# own (gap 0.107 vs an independently-tuned 0.161), not just assumed symmetric.

_LOOP_CY_TOP  = 0.35
_LOOP_CY_BOT  = 0.65
_LOOP_RY_FRAC = 0.20
_LOOP_RX_FRAC = 0.80

_LOOP_TEMPLATE_CACHE: dict[tuple[int, int], tuple[np.ndarray, np.ndarray]] = {}


def _loop_templates(h: int, w: int) -> tuple[np.ndarray, np.ndarray]:
    """Build (and cache) the loop_top ('9'-targeted) and loop_bot
    ('6'-targeted, vertical mirror) partial-arc templates at (h, w)."""
    key = (h, w)
    cached = _LOOP_TEMPLATE_CACHE.get(key)
    if cached is not None:
        return cached
    rx = max(2, int(round(_LOOP_RX_FRAC * w)))
    ry = max(2, int(round(_LOOP_RY_FRAC * h)))
    top_t = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(top_t, (w - 1, int(round(_LOOP_CY_TOP * h))), (rx, ry), 0, 90, 270, 255, thickness=2)
    bot_t = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(bot_t, (w - 1, int(round(_LOOP_CY_BOT * h))), (rx, ry), 0, 90, 270, 255, thickness=2)
    _LOOP_TEMPLATE_CACHE[key] = (top_t, bot_t)
    return top_t, bot_t


def _loop_features(gray_norm: np.ndarray) -> np.ndarray:
    """Return [corr_with_loop_top, corr_with_loop_bot] for a glyph."""
    h, w = gray_norm.shape
    top_t, bot_t = _loop_templates(h, w)
    return np.array([_norm_xcorr(gray_norm, top_t), _norm_xcorr(gray_norm, bot_t)])


# ── Ring feature: radial FFT magnitude energy (scale/frequency content) ──────
# Classic Fourier "ring" texture feature (the radial counterpart to wedge's
# angular sectors) — sums magnitude in concentric annuli instead of angular
# wedges, capturing how energy is distributed across spatial frequencies
# (coarse/blobby vs fine/sharp strokes) rather than orientation.
#
# MEASURED (training-data ablation): mean F-ratio 1.24, 50% of the 8 bins
# individually clear the noise floor — real but more modest than Gabor/wedge/
# paren.  Motivating case (known_issues.txt §15): a visible monotonic
# low-frequency-energy gradient across '9' (blobby loop) -> '2' -> '3' -> '5'
# (progressively sharper strokes), same rotation-invariance caveat as wedge
# applies (it's still a pure FFT-magnitude feature).

_RING_BIN_CACHE: dict[tuple[int, int], np.ndarray] = {}


def _ring_bin_map(h: int, w: int, n_rings: int) -> np.ndarray:
    """Radial-distance bin index per FFT pixel, normalised to the glyph's
    own max radius so it's resolution-independent."""
    key = (h, w)
    cached = _RING_BIN_CACHE.get(key)
    if cached is not None:
        return cached
    cy, cx = h // 2, w // 2
    ys, xs = np.indices((h, w))
    r = np.sqrt((ys - cy) ** 2 + (xs - cx) ** 2)
    rmax = r.max() + 1e-9
    bins = np.minimum((r / rmax * n_rings).astype(int), n_rings - 1)
    _RING_BIN_CACHE[key] = bins
    return bins


def _ring_energies(gray_norm: np.ndarray, n_rings: int = N_RINGS) -> np.ndarray:
    """Fraction of FFT magnitude energy in each radial band (DC excluded)."""
    f32 = gray_norm.astype(np.float32) / 255.0
    mag = np.abs(np.fft.fftshift(np.fft.fft2(f32)))
    h, w = mag.shape
    mag[h // 2, w // 2] = 0.0
    bins = _ring_bin_map(h, w, n_rings)
    energies = np.array([mag[bins == i].sum() for i in range(n_rings)])
    total = energies.sum() + 1e-9
    return energies / total


# ── Vertical-run feature: isolated (background-flanked) stroke detector ─────
# Replaces gabor_0 (see the N_ORIENT note above). Spatial, not frequency-
# domain: an FFT-based box-filter formulation was tried (both a circular
# version sharing the existing 2D transform, and a linear/padded version
# paying its own transform) and neither beat this at equal or lower cost
# (docs/known_issues.txt §15 has the full investigation) -- circular
# wraparound corrupts exactly the boundary information run-length depends
# on, and the padded version that avoids that needs its own separate
# transform anyway, so there is no configuration where FFT wins here.
#
# The naive "does some column hold a long contiguous run" measure (no
# isolation check) is easily fooled: a solid-white crop or a filled blob
# both score 1.0, indistinguishable from a real stroke, because it never
# checks that the run is NARROW. MAX_STROKE_W requires background on both
# flanks (measured via segment width, not just the immediate neighbor, since
# real strokes at this 12px resolution render 4-5px wide, not 1px) before a
# pixel counts toward the run. Calibrated to the corpus's OWN measured
# median stroke width (4-5px), not guessed -- an initial guess of 2px
# rejected nearly all of even '1's genuine stroke pixels.
#
# MEASURED (corpus-wide, max_stroke_w=6): '1' (unambiguously a straight
# line) is the clear top scorer at 0.700 mean, degenerate solid-white/
# filled-blob crops score 0.000/0.050-0.150 -- both direction and rejection
# behave correctly. F-ratio=14738, '4'-vs-'7' d'=-5.31 (vs gabor_0's 0.71,
# and confirmed NOT a threshold artifact -- '7' genuinely reads more like an
# isolated straight run than '4' in this font once measured properly,
# reproducing the same direction the uncorrected run-length measure found).

MAX_STROKE_W = 6

# SUPERSEDED (2026-07-05, same-session integration): _vrun_feature below is
# no longer called from compute_features() -- replaced by _vstroke_feature
# (see that section). Kept, unused, rather than deleted, matching this
# module's own convention for ablated-but-informative features (see the
# WEDGE FEATURE note above _wedge_bin_map). Root cause: vrun's "isolated
# run, any position, full column height" measure has no way to dodge a
# mid-height crossbar ('4') or discriminate a genuine stroke from a
# curve's incidental locally-straight segment ('7's diagonal) -- see
# docs/known_issues.txt §17 and the vstroke feature's own docstring below
# for the fix (2D sliding window + a signed punish cell) and the full
# conversation-log investigation trail that produced it.


def _run_since_bg(fg_rows: np.ndarray) -> np.ndarray:
    """Distance since the last background pixel, scanning left->right along
    each row. Sentinel -width (not -1) means 'no background found yet in
    this row' -> a large distance -> correctly fails any max_stroke_w
    threshold instead of getting a free pass at the array edge (the bug
    that made a solid-white row misread as isolated)."""
    n, width = fg_rows.shape
    idx = np.arange(width)[None, :] * np.ones((n, 1), dtype=np.int64)
    last_bg = np.where(~fg_rows, idx, -width)
    last_bg = np.maximum.accumulate(last_bg, axis=1)
    return idx - last_bg


def _horiz_segment_width(fg: np.ndarray) -> np.ndarray:
    """Width of the horizontal foreground segment each pixel belongs to (0
    where background). Right-side width is the SAME left-to-right logic
    applied to the horizontally-reversed array then flipped back -- computing
    it via a value-remapped index instead is an easy off-by-sign mistake
    (caught during development: it produced negative "widths")."""
    left_run = _run_since_bg(fg)
    right_run = _run_since_bg(fg[:, ::-1])[:, ::-1]
    return np.where(fg, left_run + right_run - 1, 0)


def _vrun_feature(gray_norm: np.ndarray, max_stroke_w: int = MAX_STROKE_W) -> float:
    """SUPERSEDED -- see note above MAX_STROKE_W. Kept, unused. Longest
    contiguous vertical run of isolated (narrow, background-flanked)
    foreground pixels in any single column, normalized by height."""
    h, w = gray_norm.shape
    fg = gray_norm > 127
    seg_w = _horiz_segment_width(fg)
    thin = fg & (seg_w <= max_stroke_w) & (seg_w > 0)
    idx = np.arange(h)[:, None] * np.ones((1, w), dtype=np.int64)
    last_bg = np.where(~thin, idx, -1)   # -1 sentinel here is correct: a fully
    last_bg = np.maximum.accumulate(last_bg, axis=0)  # unbroken thin column
    run = idx - last_bg                                # SHOULD read h (full
    run = np.where(thin, run, 0)                        # credit), not reject.
    return float(run.max()) / h


# ── vstroke feature: 2D-sliding, single-sided, punished matched filter ──────
# Replaces vrun (see SUPERSEDED note above). Full investigation trail (three
# rejected designs before this one, the left-vs-right reachability argument,
# the mirror-orientation rejection, and the punish-cell derivation) lives in
# the session's conversation log and debugs/debug_vstroke_feature.py, which
# remains the disposable prototyping ground for this feature -- this is the
# production port of that script's validated design, not a duplicate
# exploration.
#
# DESIGN (single committed orientation, ink on the RIGHT of a small window
# slid across every (x, y) offset in the glyph, best score kept):
#   - 2D SLIDING instead of a fixed full-height placement: a short window
#     that also slides vertically can position itself below a mid-height
#     crossbar ('4') instead of needing a pre-placed mask to dodge it.
#   - SINGLE-SIDED (ink on one side, background on the other), not
#     background-flanked-on-both-sides: doesn't bake in an assumed stroke
#     width. RIGHT was chosen over LEFT specifically because '4's vertical
#     stroke sits in the right-reachable band for this font (a left-aligned
#     kernel structurally cannot reach it, regardless of tuning -- see
#     debug_vstroke_feature.py's reachability math).
#   - PUNISH cell: the background column immediately adjacent to the ink
#     band, bottom row of the window only, is weighted -1 instead of 0.
#     Targets '7' specifically: its diagonal descender drifts left as y
#     increases, so a short window placed somewhere along it can still
#     read as "isolated vertical stroke" over kernel_h rows of small drift
#     -- but by the window's BOTTOM row the drift is largest, spilling
#     into the column right next to the ink band. A genuine vertical
#     stroke ('1', '4') never does this (same columns for the full window
#     height by construction), so the punish cell suppresses '7' without
#     touching either intended target. Measured (single-image prototype):
#     '7' 0.705 -> 0.619, '1' 1.000 -> 0.967, '4' 0.620 -> 0.621.
#
# KNOWN LIMITATION, not addressed: still cannot fully separate a genuine
# isolated stroke from a curve's incidental locally-straight segment in
# general -- '3'/'9' remained above '4' even after the '7'-targeted punish
# cell (a different false-positive instance, unaddressed).

VSTROKE_KERNEL_H = 10   # window height -- half NORM_H_PCT; unvalidated beyond
                          # the single-image prototype, open to corpus-wide tuning
VSTROKE_KERNEL_W = 6    # window width -- same starting point as MAX_STROKE_W
VSTROKE_INK_FRAC = 0.4  # fraction of kernel_w that is "ink" (right-aligned)

_VSTROKE_KERNEL_CACHE: "np.ndarray | None" = None


def _vstroke_kernel(kernel_h: int = VSTROKE_KERNEL_H, kernel_w: int = VSTROKE_KERNEL_W) -> np.ndarray:
    """(kernel_h, kernel_w) weight template: +1 = ink expected (right side,
    all rows), 0 = background expected (left side, most rows), -1 = punish
    cell (bottom row, background column adjacent to the ink band)."""
    global _VSTROKE_KERNEL_CACHE
    if _VSTROKE_KERNEL_CACHE is not None:
        return _VSTROKE_KERNEL_CACHE
    ink_w = max(1, int(round(VSTROKE_INK_FRAC * kernel_w)))
    weight = np.zeros((kernel_h, kernel_w), dtype=np.float64)
    weight[:, kernel_w - ink_w:] = 1.0
    punish_col = kernel_w - ink_w - 1
    if 0 <= punish_col < kernel_w:
        weight[kernel_h - 1, punish_col] = -1.0
    _VSTROKE_KERNEL_CACHE = weight
    return weight


def _slide_best_2d(gray_norm: np.ndarray, weight: np.ndarray) -> float:
    """Slide `weight` across every (x, y) offset in gray_norm; return the
    best (max) normalized cross-correlation score. Shared by vstroke and
    hbar -- both are the same "small matched filter, 2D-sliding, unmasked"
    computation, just transposed. Cheap: with these kernel/glyph sizes the
    search space is at most a few dozen positions (see each feature's own
    docstring for the exact count) -- a spatial double loop beats setting
    up an FFT-based convolution at this scale (known_issues.txt §15's
    vrun-era FFT-vs-spatial investigation, same conclusion, same reasoning:
    no configuration wins at zero marginal transform cost)."""
    h, w = gray_norm.shape
    kh, kw = weight.shape
    wf = weight.astype(np.float64).ravel()
    wf = wf - wf.mean()
    w_norm = np.linalg.norm(wf) + 1e-9
    best = -1e9
    for y0 in range(max(1, h - kh + 1)):
        for x0 in range(max(1, w - kw + 1)):
            sub = gray_norm[y0: y0 + kh, x0: x0 + kw].astype(np.float64).ravel()
            sub = sub - sub.mean()
            score = float(np.dot(sub, wf)) / (np.linalg.norm(sub) * w_norm + 1e-9)
            if score > best:
                best = score
    return best


def _vstroke_feature(gray_norm: np.ndarray) -> float:
    return _slide_best_2d(gray_norm, _vstroke_kernel())


# ── vstroke GATE: skip the expensive 2D-sliding search for glyphs that are
# almost certainly NOT in {1,4,7} -- vstroke's own target group (this
# section's docstring: "targets '1'/'4' vs '7'") ────────────────────────────
# docs/known_issues.txt §24 (2026-07-06): the raw (non-degenerate) gabor_45
# response CANNOT decide which of '4'/'7' a glyph is (d'=0.213, near-total
# overlap) -- but it separates the union {1,4,7} from the arc/loop-dominant
# rest almost perfectly (debugs/debug_gabor_45_zscore_verify.py, in-sample,
# 87-image corpus): recall 99.9%, false_trigger 0.00% (every one of
# '0','2','3','5','6','8','9' has a 0.0% pass-rate at this interval).
#
# This is a GATE on whether to RUN vstroke's expensive computation, not a
# replacement for it and not a feature-vector dimension itself -- unlike
# the z-scored-gabor-into-Agent-A attempt that regressed accuracy
# (docs/decisions.txt #59), this never changes what's compared, only
# whether vstroke is computed at all for this glyph. When skipped, the
# vstroke slot in the returned feature vector is NaN, and _sorted_distances
# drops that one dimension from the L2 distance for BOTH the query and
# every centroid (same "exclude an unreliable/unavailable dimension"
# technique PAIR_TIEBREAK_RULES already uses, generalized from a hardcoded
# per-pair rule to "this dimension wasn't measured for this glyph").
#
# NOT applied to build_templates() -- training always computes the FULL
# feature vector for every glyph regardless of digit, so centroids are
# byte-identical to before this gate existed and no rebuild is needed.
# NOT applied to hbar -- hbar's target group {2,4,5,7} (see its own
# docstring below) differs from vstroke's {1,4,7}, and gabor_45 was never
# validated as a gate for that group; gating hbar too without measuring it
# separately would risk the exact same regression this gate was built to
# avoid, just for '2'/'5' instead of the rest.
#
# CAVEAT: in-sample corpus only, not held-out validated (docs/
# action_items.txt #8). The interval was found by an exhaustive grid sweep
# over the same 87-image corpus it's scored against.

VSTROKE_GATE_LO = 464.5
VSTROKE_GATE_HI = 672.0

# ── gabor_45 MAX response: a cheap, SECOND vote for the {4,7} leaf ──────────
# 2026-07-06, direct feedback: the MEAN-based response above (d'=0.213,
# forced-choice accuracy 42.4% -- worse than the majority-class baseline)
# is not the only way to summarize this Gabor filter's response. Matching
# this project's own "get the max, not the mean" lesson from the prior
# session's rotated-'4'-brute-force exploration (debugs/
# debug_gabor_4_rotated_bruteforce.py: max(|response|), closer in spirit
# to vstroke/hbar's own sliding-window max design, asks whether ANY
# position in the crop matches the kernel strongly, not whether the WHOLE
# glyph does on average) -- the MAX of the identical filter response is a
# genuinely different, much stronger signal for this exact pair:
#   d' = 1.668, standalone nearest-of-2 accuracy = 80.8% (n=1753)
# On its own this is still a "weak" classifier (80.8% is well short of a
# safe standalone answer) -- but it doesn't need to stand alone. Measured
# AGREEMENT with vstroke's own (also independently weak, d'=2.22 in
# isolation) nearest-of-2 pick between JUST {4,7}:
#   agree    (65.8% of {4,7} glyphs): 100.0% accuracy (1154/1154)
#   disagree (34.2% of {4,7} glyphs): ambiguous, needs the full feature
#            cost + the already-validated PAIR_TIEBREAK_RULES exclusion
# Two independently-weak, cheap classifiers agreeing is strong evidence in
# a way neither is alone -- see _classify_hierarchical's {4,7} leaf for
# where this consensus is used, and docs/decisions.txt #62 for the general
# lesson. GABOR_MAX_C4/C7 are calibrated reference centroids (raw filter
# response max, NOT part of the trained "gpr" template -- that still
# stores the mean-based self-fraction for the flat path's own gabor
# dimension) measured on the same 87-image corpus as VSTROKE_GATE_LO/HI;
# same in-sample caveat applies.
GABOR_MAX_C4 = 1955.46
GABOR_MAX_C7 = 1849.55


def _gabor45_response(gray_norm: np.ndarray) -> np.ndarray:
    """Raw abs Gabor-45deg filter response array -- the shared basis for
    BOTH _raw_gabor45's mean-based gate signal and the {4,7} leaf's
    max-based consensus signal, computed once and reused rather than
    convolving twice for the same kernel on the same glyph."""
    f32 = gray_norm.astype(np.float32)
    return np.abs(cv2.filter2D(f32, -1, _GABOR_KERNELS[0]))


def _raw_gabor45(gray_norm: np.ndarray) -> float:
    """Raw Gabor response MAGNITUDE (mean) at 45deg -- standalone utility
    exposing the gate's decision signal for callers that want it without
    running full compute_features() (e.g. debugs/
    debug_gabor_45_zscore_verify.py). compute_features() itself does NOT
    call this -- it reuses resps[0] (already computed for the gabor
    block's own feature-vector dimension) to make the identical decision
    without a redundant Gabor filter pass. Deliberately NOT the
    resp/sum(resps) self-fraction compute_features()'s gabor block reports
    as its feature-vector dimension (that fraction is degenerate at
    N_ORIENT=1, see known_issues.txt §24)."""
    return float(_gabor45_response(gray_norm).mean())


def _passes_vstroke_gate(gray_norm: np.ndarray) -> bool:
    """Standalone convenience wrapper around _raw_gabor45() -- see its
    docstring for why compute_features() doesn't call either of these."""
    return VSTROKE_GATE_LO <= _raw_gabor45(gray_norm) <= VSTROKE_GATE_HI


# ── hbar feature: horizontal-bar analog of vstroke, TWO SEPARATE dims ───────
# Targets '2'/'4'/'5'/'7' (each has a real horizontal stroke -- '2' foot,
# '4' crossbar, '5'/'7' top bar -- the other six digits lack). Same 2D-
# sliding, punished single-sided matched filter as vstroke, transposed
# (split axis = height, span axis = width) -- see debugs/debug_hbar_feature.py
# for the full investigation trail.
#
# TWO INDEPENDENT DIMENSIONS, NOT ONE MERGED: '2' (bottom bar) and '5'/'7'
# (top bar) are a mirror pair along this axis, the same way '4' exposed
# vstroke's left/right reachability limit -- no single orientation can
# reach both. The fix is NOT a per-glyph max of the two orientations (that
# was tried and explicitly rejected during development: a real feature
# can't pick per-glyph which orientation "wins" at inference time, so a
# max isn't a computation, it's hindsight). Instead hbar_top and hbar_bottom
# are reported as two independent feature dimensions, exactly like this
# module's existing paren_(/paren_) and loop_top/loop_bot pairs -- the
# nearest-centroid classifier over the full vector does the combining, not
# the feature extractor.
#
# PUNISH cell: background column immediately adjacent to the ink band, on
# the RIGHT edge of the window (not left -- '2' and '4', both targets, have
# real ink near the left-adjacent position in this font, so a left-side
# punish cell risked suppressing the very digits this feature exists to
# detect; right avoids that overlap).

HBAR_KERNEL_H = 6     # split axis (mirrors vstroke's KERNEL_W)
HBAR_KERNEL_W = 10    # span axis (mirrors vstroke's KERNEL_H)
HBAR_INK_FRAC = 0.4

_HBAR_KERNEL_CACHE: "dict[str, np.ndarray]" = {}


def _hbar_kernel(side: str, kernel_h: int = HBAR_KERNEL_H, kernel_w: int = HBAR_KERNEL_W) -> np.ndarray:
    """(kernel_h, kernel_w) weight template: +1 = ink expected (top or
    bottom rows per `side`, all columns), 0 = background expected, -1 =
    punish cell (rightmost column, background row adjacent to the ink band)."""
    cached = _HBAR_KERNEL_CACHE.get(side)
    if cached is not None:
        return cached
    ink_h = max(1, int(round(HBAR_INK_FRAC * kernel_h)))
    weight = np.zeros((kernel_h, kernel_w), dtype=np.float64)
    if side == "top":
        weight[:ink_h, :] = 1.0
        punish_row = ink_h
    elif side == "bottom":
        weight[kernel_h - ink_h:, :] = 1.0
        punish_row = kernel_h - ink_h - 1
    else:
        raise ValueError(f"side must be 'top' or 'bottom', got {side!r}")
    if 0 <= punish_row < kernel_h:
        weight[punish_row, kernel_w - 1] = -1.0
    _HBAR_KERNEL_CACHE[side] = weight
    return weight


def _hbar_features(gray_norm: np.ndarray) -> np.ndarray:
    return np.array([_slide_best_2d(gray_norm, _hbar_kernel("top")),
                      _slide_best_2d(gray_norm, _hbar_kernel("bottom"))])


# Block order matches compute_features()'s own concatenation order exactly --
# shared with the feature_acc convention below and with StatOcrFft._read_line's
# span-injection code, so a name here can never drift out of sync with what
# index of feature_acc it corresponds to.
FEATURE_BLOCK_NAMES = ("hist", "gabor", "paren", "ring", "loop", "vstroke", "hbar")


def compute_features(gray_norm: np.ndarray,
                      feature_acc: "list[float] | None" = None,
                      enable_vstroke_gate: bool = False) -> np.ndarray:
    """
    Return an N_FEAT-element feature vector for a NORM_W_PCT x NORM_H_PCT glyph:
      [0:N_BINS]                      64-bin FFT magnitude histogram (sum=1)
      [N_BINS:N_BINS+N_OR]            Gabor orientation fraction (sum=1) at
                                       θ = 45° (0°, 90°, 135° all dropped, see
                                       the N_ORIENT notes above)
      [N_BINS+N_OR:+N_PAREN]          '(' / ')' curve-template correlations
      [...:+N_RINGS]                  radial FFT magnitude energy fractions
      [...:+N_LOOP]                   loop_top ('9') / loop_bot ('6') curve
                                       correlations
      [...:+N_VSTROKE]                2D-sliding punished isolated-stroke
                                       match (see the vstroke feature note
                                       above; replaces vrun) -- NaN if the
                                       vstroke GATE skipped it (see below)
      [...:+N_HBAR]                   hbar_top / hbar_bottom -- two separate
                                       horizontal-bar matches (see the hbar
                                       feature note above)

    Does NOT include the wedge angular-sector feature — see the DISABLED
    note above _wedge_bin_map/_wedge_energies.

    feature_acc: optional len(FEATURE_BLOCK_NAMES) accumulator, one slot per
      block, receiving THIS call's wall-clock time -- plain perf_counter
      deltas, not timer.timed(), to avoid context-manager overhead on the
      hot per-glyph path (same convention as _classify()'s own `acc`, see
      StatOcrFft._read_line and docs/decisions.txt #58).  None (the
      default, used by build_templates() and every untimed call) adds no
      overhead at all.

    enable_vstroke_gate: DISABLED BY DEFAULT (VSTROKE_GATE_DEFAULT, same
      opt-in convention as enable_pair_tiebreak) -- see the VSTROKE GATE
      section above _vstroke_feature for the full rationale.  When True,
      the Gabor response this function already computes for the gabor
      block (resps[0], reused rather than recomputed) decides whether
      vstroke's expensive 2D-sliding search runs at all; when it's judged
      outside the {1,4,7} line-dominant group's range, vstroke's slot is
      NaN instead.  False (used by build_templates() and every other
      caller that isn't real inference) computes the full vector exactly
      as before this gate existed -- centroids trained with this always
      False are unaffected by this parameter's existence.
    """
    _t0 = time.perf_counter() if feature_acc is not None else 0.0

    fft_hist = _make_hist(_fft_magnitudes(gray_norm), N_BINS)
    if feature_acc is not None:
        _now = time.perf_counter(); feature_acc[0] += _now - _t0; _t0 = _now

    f32      = gray_norm.astype(np.float32)
    resps    = [float(np.abs(cv2.filter2D(f32, -1, k)).mean())
                for k in _GABOR_KERNELS]
    tot      = sum(resps) + 1e-9
    gabor    = [r / tot for r in resps]
    if feature_acc is not None:
        _now = time.perf_counter(); feature_acc[1] += _now - _t0; _t0 = _now

    paren    = _paren_features(gray_norm)
    if feature_acc is not None:
        _now = time.perf_counter(); feature_acc[2] += _now - _t0; _t0 = _now

    ring     = _ring_energies(gray_norm)
    if feature_acc is not None:
        _now = time.perf_counter(); feature_acc[3] += _now - _t0; _t0 = _now

    loop     = _loop_features(gray_norm)
    if feature_acc is not None:
        _now = time.perf_counter(); feature_acc[4] += _now - _t0; _t0 = _now

    skip_vstroke = enable_vstroke_gate and not (VSTROKE_GATE_LO <= resps[0] <= VSTROKE_GATE_HI)
    vstroke  = [float("nan")] if skip_vstroke else [_vstroke_feature(gray_norm)]
    if feature_acc is not None:
        _now = time.perf_counter(); feature_acc[5] += _now - _t0; _t0 = _now

    hbar     = _hbar_features(gray_norm)
    if feature_acc is not None:
        _now = time.perf_counter(); feature_acc[6] += _now - _t0; _t0 = _now

    return np.concatenate([fft_hist, gabor, paren, ring, loop, vstroke, hbar])


# ─────────────────────────────────────────────────────────────────────────────
# Glyph extraction
#   - pct (inference, label-free): reused via import — _extract_pct_glyphs
#     from gfl2.stat_ocr_padded already normalizes with _normalize_glyph,
#     the same aspect-preserving pad this feature set expects.
#   - pct (training, label-aligned): ported from debugs/pct_fft_predict.py,
#     needed only by build_templates() below.
#   - val: NOT IMPLEMENTED — real no-op function, see module docstring.
# ─────────────────────────────────────────────────────────────────────────────

# ── Strip-boundary extension: PCT_STRIP_Y[1] clips blobs with ZERO slack ────
# Diagnostic (2026-07-05, found by eyeballing debugs/debug_stat_ocr_fft_
# failures.py's raw/binarized crop columns): for this corpus's smaller-
# resolution images (cell_h=50), every digit blob's bottom edge lands EXACTLY
# at the strip boundary (bottom=23, strip_h=23, slack=0) -- the strip is
# clipping the glyph, not merely bounding it. Larger images (cell_h=63) had
# 7px of slack, so this only bites at smaller resolutions. EXPLORE-scope
# only: extends the strip used by THIS module's training/verify extraction
# (_extract_pct_digit_glyphs) -- the shared PCT_STRIP_Y constant in
# gfl2/stat_ocr.py is untouched, so gfl2/stat_ocr.py's and gfl2/
# stat_ocr_padded.py's production paths are unaffected. Capped at
# VAL_STRIP_Y[0]*ch so the extension can never reach into where the val line
# starts (known_issues.txt §15's val-strip-bleed fix moved VAL_STRIP_Y[0] to
# 0.50 specifically to keep pct content out of the val strip; extending pct
# downward must not reopen that bleed in the other direction). A cell whose
# extended strip now picks up a spurious extra blob simply fails the
# len(digit_blobs) != len(expected) check below and is skipped, same as any
# other extraction mismatch -- not silently mislabeled.
_PCT_STRIP_EXTRA_PX = 5


def _pct_strip_bottom(ch: int) -> int:
    return min(ch, int(ch * PCT_STRIP_Y[1]) + _PCT_STRIP_EXTRA_PX, int(ch * VAL_STRIP_Y[0]))


def _extract_pct_digit_glyphs(cell: np.ndarray, pct_label: str):
    """
    Return [(norm_bin_12x20, digit_char), ...] for each digit in pct_label,
    or None if the blob count doesn't match the label (extraction unreliable
    for this cell -- skipped rather than guessed at).  Training-time only:
    unlike _extract_pct_glyphs, this needs the label to align glyphs to
    characters and is not used by StatOcrFft.read().
    """
    if not pct_label:
        return None
    expected = [c for c in pct_label if c.isdigit()]
    if not expected:
        return None

    ch = cell.shape[0]
    pct_strip = cell[: _pct_strip_bottom(ch), :]
    thresh = _binarize(pct_strip)
    blobs = _filter_y_outliers(_find_blobs(thresh), threshold=12)
    if not blobs:
        return None

    sorted_x = sorted(blobs, key=lambda b: b[0])
    pct_x = _find_percent_x_start(sorted_x)
    digit_blobs = [
        (x, y, w, h) for (x, y, w, h) in sorted_x
        if (pct_x is None or x < pct_x)
        and not (w <= DOT_MAX_DIM and h <= DOT_MAX_DIM)
    ]
    if len(digit_blobs) != len(expected):
        return None

    glyphs = []
    for (x, y, w, h), label in zip(digit_blobs, expected):
        crop = thresh[y: y + h, x: x + w]
        if crop.size == 0:
            return None
        norm = _normalize_glyph(crop, NORM_W_PCT, NORM_H_PCT)
        glyphs.append((norm, label))
    return glyphs


def _extract_val_glyphs(val_blobs: list, thresh) -> list:
    """
    NOT IMPLEMENTED (docs/known_issues.txt §15) -- this exploration only
    built FFT+Gabor features/centroids for pct-line digits.  Kept as a
    real function, matching gfl2/stat_ocr.py's _extract_val_glyphs slot,
    purely so StatOcrFft._read_line's is_pct dispatch stays structurally
    identical to the other two engines.  Always returns no glyphs.
    """
    return []


# ─────────────────────────────────────────────────────────────────────────────
# Classifier: two independent nearest-centroid agents + dispute resolution
# ─────────────────────────────────────────────────────────────────────────────

def _sorted_distances(feat: np.ndarray, centroids: dict) -> list[tuple[float, str]]:
    """Distance to every centroid, ascending.  Shared by _nearest_centroid()
    and the PAIR TIEBREAK (which needs the top-2 candidates, not just the
    single winner) so both agree on what "nearest" means.

    NaN-safe: a NaN in `feat` (the vstroke GATE above sets the vstroke slot
    to NaN when it's skipped) drops that dimension from the L2 distance for
    BOTH the query and every centroid -- the same "exclude a dimension that
    isn't reliable/available for this decision" technique PAIR_TIEBREAK_RULES
    already uses, just triggered by "wasn't computed" instead of a hardcoded
    per-pair rule.  When feat has no NaN (every caller except the gated
    vstroke path), `mask` is all-True and this is byte-identical to a plain
    np.linalg.norm(feat - c)."""
    mask = ~np.isnan(feat)
    return sorted((float(np.linalg.norm(feat[mask] - c[mask])), d) for d, c in centroids.items())


def _nearest_centroid(feat: np.ndarray, centroids: dict) -> tuple[str, float]:
    """
    Nearest centroid by L2 distance, plus the relative margin to the
    second-nearest centroid ((d2-d1)/d1) -- the confidence signal both
    agents in _classify() are gated on.  margin=1.0 when there's only one
    centroid (nothing to be uncertain against).
    """
    if not centroids:
        return '?', 0.0
    dists = _sorted_distances(feat, centroids)
    d1, best = dists[0]
    if len(dists) == 1:
        return best, 1.0
    d2, _second = dists[1]
    margin = (d2 - d1) / d1 if d1 > 1e-9 else 1.0
    return best, margin


def _pair_tiebreak(feat_gpr: np.ndarray, centroids: dict, cand1: str, cand2: str) -> "str | None":
    """
    If (cand1, cand2) is a registered PAIR_TIEBREAK_RULES entry, re-decide
    between JUST those two candidates using the pair's reduced dimension
    set (excluding whichever dimension is known-unstable for that specific
    pair -- see module docstring's PAIR TIEBREAK section).  Returns None if
    this pair has no registered rule, so the caller falls through to the
    normal confidence-gated decision unchanged.

    NaN-safe (same reasoning as _sorted_distances): if the vstroke GATE
    skipped vstroke for this glyph (e.g. a rare gate miss where a true '4'
    or '7' fell outside the gate interval, or an unrelated digit's top-2
    happened to land on {'4','7'} despite being gated out), vstroke's slot
    is NaN here too -- masked out of both d1 and d2 rather than propagating
    NaN into the comparison (which would silently always prefer cand2, an
    otherwise-invisible bug).
    """
    rule = PAIR_TIEBREAK_RULES.get(frozenset({cand1, cand2}))
    if rule is None:
        return None
    q = feat_gpr[rule]
    mask = ~np.isnan(q)
    d1 = np.linalg.norm(q[mask] - centroids[cand1][rule][mask])
    d2 = np.linalg.norm(q[mask] - centroids[cand2][rule][mask])
    return cand1 if d1 < d2 else cand2


def _nearest_of(value_or_vec, centroid_slices: dict) -> "str | None":
    """
    Nearest-centroid pick among a SMALL, explicit candidate set, comparing
    only the dimension(s) `centroid_slices` already carries (a scalar for a
    single-dim node, an ndarray for a multi-dim one) -- the shared primitive
    behind every _classify_hierarchical() tree node. Returns None if
    `centroid_slices` is empty (a candidate digit missing from the trained
    templates -- defensive, shouldn't happen against a real corpus).
    """
    if not centroid_slices:
        return None
    return min(centroid_slices, key=lambda d: float(np.linalg.norm(
        np.atleast_1d(value_or_vec) - np.atleast_1d(centroid_slices[d]))))


def _classify_hierarchical(norm: np.ndarray, templates: dict,
                            acc: "list[float] | None" = None) -> str:
    """
    Hierarchical/branching classifier -- an alternative ALGORITHM to the
    flat two-agent _classify() below, not a modifier of it. See the module
    docstring's HIERARCHICAL CLASSIFIER section for the full tree diagram
    and rationale (each node computes only the ONE feature it needs, using
    nearest-centroid on a candidate-set-and-dimension-restricted slice of
    the SAME already-trained "gpr" centroids the flat path uses -- no
    separate training, no rebuild).

    acc: optional [feature_time_s, decision_time_s, agent_b_time_s]
      accumulator -- same 3-slot convention as _classify()'s own `acc`
      (feature extraction / cheap nearest-centroid picks / Agent B
      fallback), so StatOcrFft._read_line's timing injection works
      unmodified regardless of which classifier produced the numbers.
      feature_acc (the per-FEATURE_BLOCK_NAMES breakdown) is NOT supported
      here -- most glyphs only compute a subset of blocks, so a full
      per-block breakdown would mean N/A for whichever blocks this
      glyph's path skipped; acc[0] still reports the real total.
    """
    gpr_centroids = templates.get("gpr", {})
    if not gpr_centroids:
        return '?'

    _t0 = time.perf_counter() if acc is not None else 0.0

    gabor_resp = _gabor45_response(norm)
    raw_gabor = float(gabor_resp.mean())
    if acc is not None:
        _now = time.perf_counter(); acc[0] += _now - _t0; _t0 = _now

    if VSTROKE_GATE_LO <= raw_gabor <= VSTROKE_GATE_HI:
        # likely {1,4,7}: vstroke reliably picks out '1' (centroids 0.961 vs
        # 0.550/0.642, both tight -- std 0.02) but CANNOT reliably decide '4'
        # vs '7' on its own (centroids only 0.09 apart, and '4' alone has
        # std 0.057 -- wide enough that a large fraction of '4' glyphs drift
        # past the midpoint into '7' territory; measured: naive nearest-of-3
        # here misclassified 262/993 '4' glyphs as '7').
        vstroke_score = _vstroke_feature(norm)
        if acc is not None:
            _now = time.perf_counter(); acc[0] += _now - _t0; _t0 = _now

        line_c = {d: gpr_centroids[d][_VSTROKE_IDX] for d in ('1', '4', '7') if d in gpr_centroids}
        nearest = _nearest_of(vstroke_score, line_c)
        if acc is not None:
            _now = time.perf_counter(); acc[1] += _now - _t0; _t0 = _now
        if nearest is None:
            return '?'
        if nearest == '1':
            return '1'   # the one cheap, reliable win here -- '1' is also
                          # this group's majority class (1711 of 3464 glyphs)

        # nearest was '4' or '7' -- not trustworthy from vstroke alone, but
        # gabor_45's MAX response (not the gate's mean, see the block above
        # GABOR_MAX_C4/C7) is a SECOND, independently-weak, already-free
        # signal for this exact pair (reuses gabor_resp -- zero extra
        # convolution cost). When the two cheap votes AGREE, trust them:
        # measured 100.0% accuracy (1154/1154) on the 65.8% of {4,7} glyphs
        # where they do. Only on disagreement (34.2%) is the expensive
        # feature cost + PAIR_TIEBREAK_RULES fallback actually needed.
        gabor_max = float(gabor_resp.max())
        gabor_vote = '4' if abs(gabor_max - GABOR_MAX_C4) < abs(gabor_max - GABOR_MAX_C7) else '7'
        if acc is not None:
            _now = time.perf_counter(); acc[1] += _now - _t0; _t0 = _now
        if gabor_vote == nearest:
            return nearest   # consensus -- compute_features() never called

        feat_full = compute_features(norm)
        if acc is not None:
            _now = time.perf_counter(); acc[0] += _now - _t0; _t0 = _now
        result = _pair_tiebreak(feat_full[N_BINS:], gpr_centroids, '4', '7')
        if acc is not None:
            acc[1] += time.perf_counter() - _t0
        return result if result is not None else nearest

    # likely arc-dominant {0,2,3,5,6,8,9}: inner-blob hole count decides next
    holes = _count_inner_blobs(norm)
    if acc is not None:
        _now = time.perf_counter(); acc[0] += _now - _t0; _t0 = _now

    if holes >= 2:
        return '8'   # categorical -- production's own '8'=2-holes rule (§9/§14)

    if holes == 1:
        # {0,6,9}: paren ALONE is not enough -- '6' shows a clean '('
        # preference but '9' lands near-neutral between paren_(/paren_)
        # (known_issues.txt §15's PAREN+RING entry), which is exactly why
        # loop_top/loop_bot were built as a '9'/'6'-targeted follow-up
        # (same section). Compute both and use all 4 dims together (measured:
        # paren alone misclassified 119/859 '6' glyphs as '9').
        paren_score = _paren_features(norm)
        loop_score = _loop_features(norm)
        if acc is not None:
            _now = time.perf_counter(); acc[0] += _now - _t0; _t0 = _now
        combined = np.concatenate([paren_score, loop_score])
        idx = [_PAREN_OPEN, _PAREN_CLOSE, _LOOP_TOP_IDX, _LOOP_BOT_IDX]
        c069 = {d: gpr_centroids[d][idx] for d in ('0', '6', '9') if d in gpr_centroids}
        result = _nearest_of(combined, c069)
        if acc is not None:
            acc[1] += time.perf_counter() - _t0
        return result if result is not None else '?'

    # holes == 0: {2,3,5} -- deliberately OMITTED from this tree (see module
    # docstring: no cheap 1-2 dim feature here reliably separates them).
    # Falls back to the FULL flat two-agent _classify() (Agent A AND Agent
    # B, exactly the path that already resolves these three digits near-
    # perfectly in the flat baseline) rather than Agent B alone -- strictly
    # better than a weaker stand-in, and free: _classify is a module-level
    # function resolved at call time, so this forward reference costs
    # nothing extra to wire up. Only these three digits (plus whichever
    # other 0-hole glyph a misread hole-count routes here) ever pay the
    # full flat-path cost via this branch.
    if acc is not None:
        acc[0] += time.perf_counter() - _t0
    return _classify(norm, templates, acc=acc)


def _classify(norm: np.ndarray, templates: dict,
              conf_a: float = CONF_A_DEFAULT, conf_b: float = CONF_B_DEFAULT,
              enable_pair_tiebreak: bool = PAIR_TIEBREAK_DEFAULT,
              enable_vstroke_gate: bool = VSTROKE_GATE_DEFAULT,
              enable_hierarchical: bool = HIERARCHICAL_DEFAULT,
              acc: "list[float] | None" = None,
              feature_acc: "list[float] | None" = None) -> str:
    """
    Two-agent classification -- see the module docstring's TWO-AGENT
    CLASSIFIER section for why this isn't a single nearest-centroid lookup
    over the full feature vector.

    Agent A (gpr: gabor+paren+ring, unnormalized) runs first; if its margin
    clears conf_a, its answer is used.  Otherwise Agent B (hist: the 64-bin
    histogram, z-score normalized with templates["hist_mu"]/["hist_sigma"])
    gets a turn; if ITS margin clears conf_b, its answer is used instead.
    If neither is confident, '?' -- consistent with the project-wide '?'
    convention (docs/known_issues.txt §14, §15).

    enable_pair_tiebreak: DISABLED BY DEFAULT (see module docstring's PAIR
      TIEBREAK section).  When True, if Agent A's own top-2 nearest
      centroids exactly match a PAIR_TIEBREAK_RULES entry, that pair is
      re-decided using its registered reduced dimension set and returned
      immediately -- bypassing conf_a and Agent B entirely for this glyph.
      Every glyph whose top-2 aren't a registered pair is completely
      unaffected by this flag.

    templates: the "pct" sub-dict with "gpr", "hist", "hist_mu", "hist_sigma"
      keys (see StatOcrFft.__init__ / build_templates()).

    acc: optional [feature_extraction_s, agent_a_s, agent_b_s] accumulator --
      mirrors gfl2/stat_ocr.py's acc convention (see StatOcrFft._read_line).
      agent_b_s only accumulates on the fraction of glyphs where Agent A was
      unsure and Agent B actually ran.

    feature_acc: optional len(FEATURE_BLOCK_NAMES) accumulator forwarded
      to compute_features() -- breaks acc[0] (feature_extraction) down
      into its individual blocks (hist/gabor/paren/ring/loop/vstroke/hbar)
      instead of one flat number.  See StatOcrFft._read_line.

    enable_vstroke_gate: DISABLED BY DEFAULT (see the VSTROKE GATE section
      above _vstroke_feature).  When True, vstroke's expensive 2D-sliding
      search is skipped for glyphs whose raw gabor_45 response falls
      outside the {1,4,7} group's measured range -- forwarded to
      compute_features(), which reports NaN in vstroke's slot when
      skipped.  _sorted_distances (used by both _nearest_centroid and the
      pair tiebreak below) transparently drops that one dimension from the
      distance for such glyphs; see its own docstring.

    enable_hierarchical: DISABLED BY DEFAULT (see module docstring's
      HIERARCHICAL CLASSIFIER section).  When True, dispatches immediately
      to _classify_hierarchical() -- a wholesale alternative algorithm,
      not a modifier -- and enable_pair_tiebreak/enable_vstroke_gate are
      ignored (both are specific to this function's own flat L2-over-all-
      dims decision, which the hierarchical path bypasses entirely).
    """
    if not templates.get("gpr") and not templates.get("hist"):
        return '?'

    if enable_hierarchical:
        return _classify_hierarchical(norm, templates, acc=acc)

    _t0 = time.perf_counter() if acc is not None else 0.0
    feat = compute_features(norm, feature_acc=feature_acc, enable_vstroke_gate=enable_vstroke_gate)
    if acc is not None:
        _now = time.perf_counter(); acc[0] += _now - _t0; _t0 = _now

    feat_gpr = feat[N_BINS:]
    gpr_centroids = templates.get("gpr", {})

    if enable_pair_tiebreak and len(gpr_centroids) >= 2:
        dists = _sorted_distances(feat_gpr, gpr_centroids)
        (d1, cand1), (d2, cand2) = dists[0], dists[1]
        override = _pair_tiebreak(feat_gpr, gpr_centroids, cand1, cand2)
        if override is not None:
            if acc is not None: acc[1] += time.perf_counter() - _t0
            return override
        margin_a = (d2 - d1) / d1 if d1 > 1e-9 else 1.0
        pred_a = cand1
    else:
        pred_a, margin_a = _nearest_centroid(feat_gpr, gpr_centroids)

    if acc is not None:
        _now = time.perf_counter(); acc[1] += _now - _t0; _t0 = _now
    if margin_a >= conf_a:
        return pred_a

    hist_centroids = templates.get("hist")
    if hist_centroids:
        mu, sigma = templates["hist_mu"], templates["hist_sigma"]
        feat_hist = (feat[:N_BINS] - mu) / sigma
        pred_b, margin_b = _nearest_centroid(feat_hist, hist_centroids)
        if acc is not None: acc[2] += time.perf_counter() - _t0
        if margin_b >= conf_b:
            return pred_b

    return '?'


def _reconstruct_pct(
    glyphs: list, templates: dict,
    conf_a: float = CONF_A_DEFAULT, conf_b: float = CONF_B_DEFAULT,
    enable_pair_tiebreak: bool = PAIR_TIEBREAK_DEFAULT,
    enable_vstroke_gate: bool = VSTROKE_GATE_DEFAULT,
    enable_hierarchical: bool = HIERARCHICAL_DEFAULT,
    acc: "list[float] | None" = None,
    feature_acc: "list[float] | None" = None,
) -> Optional[str]:
    """
    Reconstruct the pct value string from pct-strip glyphs.  Same contract
    as gfl2/stat_ocr.py's _reconstruct_pct: the rightmost unclassifiable
    glyph is dropped (it's the '%' glyph, structurally indistinguishable
    from a digit by bounding-box size alone), leading/trailing '.' noise is
    stripped, and any remaining '?' aborts the result to None rather than
    returning a partially-wrong string.
    """
    items = [(x, norm, hint) for x, norm, hint in glyphs if hint != 'skip']
    parts = []
    for i, (x, norm, hint) in enumerate(items):
        if hint == '.':
            parts.append('.')
        else:
            c = _classify(norm, templates, conf_a, conf_b, enable_pair_tiebreak,
                           enable_vstroke_gate, enable_hierarchical, acc, feature_acc)
            if c == '?' and i == len(items) - 1:
                continue  # rightmost unclassifiable blob -> % glyph, drop it
            parts.append(c)
    result = ''.join(parts)
    result = result.strip('.')
    return result if result and '?' not in result else None


def _reconstruct_val(
    glyphs: list, templates: dict,
    conf_a: float = CONF_A_DEFAULT, conf_b: float = CONF_B_DEFAULT,
    enable_pair_tiebreak: bool = PAIR_TIEBREAK_DEFAULT,
    acc: "list[float] | None" = None,
) -> Optional[str]:
    """
    NOT IMPLEMENTED -- see _extract_val_glyphs.  Kept as a real function
    (matching gfl2/stat_ocr.py's _reconstruct_val slot) so
    StatOcrFft._read_line's is_pct dispatch stays structurally identical to
    the other two engines.  Always returns None.
    """
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Public engine
# ─────────────────────────────────────────────────────────────────────────────

class StatOcrFft:
    """FFT+Gabor two-agent nearest-centroid OCR engine for Daily Gunsmoke
    stat cells -- pct-line only, exploratory.  See module docstring's
    TWO-AGENT CLASSIFIER section for status and architecture."""

    def __init__(self, templates: dict,
                 enable_pair_tiebreak: bool = PAIR_TIEBREAK_DEFAULT,
                 enable_vstroke_gate: bool = VSTROKE_GATE_DEFAULT,
                 enable_hierarchical: bool = HIERARCHICAL_DEFAULT) -> None:
        pct = templates.get("pct", {})
        self._pct = {
            "gpr":  {d: np.asarray(v, dtype=np.float64) for d, v in pct.get("gpr", {}).items()},
            "hist": {d: np.asarray(v, dtype=np.float64) for d, v in pct.get("hist", {}).items()},
            "hist_mu":    np.asarray(pct.get("hist_mu", []), dtype=np.float64),
            "hist_sigma": np.asarray(pct.get("hist_sigma", []), dtype=np.float64),
        }
        self._val: dict = {}   # always empty -- val classification not implemented
        self._enable_pair_tiebreak = enable_pair_tiebreak
        self._enable_vstroke_gate = enable_vstroke_gate
        self._enable_hierarchical = enable_hierarchical

    # ── Construction ─────────────────────────────────────────────────────────

    @classmethod
    def load(cls, enable_pair_tiebreak: bool = PAIR_TIEBREAK_DEFAULT,
              enable_vstroke_gate: bool = VSTROKE_GATE_DEFAULT,
              enable_hierarchical: bool = HIERARCHICAL_DEFAULT) -> "StatOcrFft":
        """enable_pair_tiebreak: DISABLED BY DEFAULT -- see module docstring's
        PAIR TIEBREAK section and PAIR_TIEBREAK_DEFAULT.
        enable_vstroke_gate: DISABLED BY DEFAULT -- see the VSTROKE GATE
        section above _vstroke_feature and VSTROKE_GATE_DEFAULT.
        enable_hierarchical: DISABLED BY DEFAULT -- see the HIERARCHICAL
        CLASSIFIER module docstring section and HIERARCHICAL_DEFAULT."""
        if not PCT_TMPL_F.exists():
            raise FileNotFoundError(
                f"StatOcrFft pct centroids not found: {PCT_TMPL_F}\n"
                "Run: python -m gfl2.stat_ocr_fft --build"
            )
        import importlib.util
        spec = importlib.util.spec_from_file_location(PCT_TMPL_F.stem, PCT_TMPL_F)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return cls(mod.DATA, enable_pair_tiebreak=enable_pair_tiebreak,
                    enable_vstroke_gate=enable_vstroke_gate,
                    enable_hierarchical=enable_hierarchical)

    # ── Inference ─────────────────────────────────────────────────────────────

    def read(
        self, cell: np.ndarray, timer=None
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Read a stat cell crop.  Returns (pct_str, val_str) -- val_str is
        always None (see module docstring).  (None, None) on pct parse
        failure; the caller should fall back to Tesseract, same as the
        other two engines.

        timer: optional TimerStack -- when provided, sub-spans are recorded
          under the caller's active span: pct/binarize, pct/blobs,
          pct/extract, pct/classify (with feature_extraction/agent_a_gpr/
          agent_b_hist children -- agent_b_hist only appears on cells where
          Agent A was unsure and Agent B actually ran), and a single
          val/not_implemented leaf.
        """
        ch = cell.shape[0]
        pct_strip = cell[: _pct_strip_bottom(ch), :]
        val_strip = cell[int(ch * VAL_STRIP_Y[0]) : int(ch * VAL_STRIP_Y[1]), :]

        pct_str = self._read_line(pct_strip, self._pct, is_pct=True,  timer=timer)
        val_str = self._read_line(val_strip, self._val, is_pct=False, timer=timer)
        return pct_str, val_str

    def _read_line(
        self, strip: np.ndarray, templates: dict, is_pct: bool, timer=None
    ) -> Optional[str]:
        if strip.size == 0:
            return None
        prefix = "pct" if is_pct else "val"
        _t = timer.timed if timer is not None else _nullctx

        if not is_pct:
            # NOT IMPLEMENTED (docs/known_issues.txt §15).  Short-circuits
            # before any blob/classify work: (a) an unfinished val path
            # would otherwise waste real cycles on a result that's always
            # discarded, understating this engine's actual (pct-only)
            # speed; (b) still emits one span so a pipeline_summary tree has
            # the same pct/val shape as the other two engines.
            # _extract_val_glyphs/_reconstruct_val are exercised here (not
            # inlined as `return None`) so the no-op call chain genuinely
            # marks where val support would plug in.
            with _t(f"{prefix}/not_implemented"):
                return _reconstruct_val(_extract_val_glyphs([], None), templates)

        with _t(f"{prefix}/binarize"):
            thresh = _binarize(strip)

        with _t(f"{prefix}/blobs"):
            blobs = _find_blobs(thresh)
            if not blobs:
                return None
            blobs = _filter_y_outliers(blobs, threshold=12)
            if not blobs:
                return None

        with _t(f"{prefix}/extract"):
            glyphs = _extract_pct_glyphs(blobs, thresh)

        acc = [0.0, 0.0, 0.0] if timer is not None else None
        feature_acc = [0.0] * len(FEATURE_BLOCK_NAMES) if timer is not None else None
        with _t(f"{prefix}/classify") as classify_span:
            result = _reconstruct_pct(
                glyphs, templates,
                enable_pair_tiebreak=self._enable_pair_tiebreak,
                enable_vstroke_gate=self._enable_vstroke_gate,
                enable_hierarchical=self._enable_hierarchical,
                acc=acc, feature_acc=feature_acc,
            )

        # Inject per-phase sub-timings as synthetic child Spans, mirroring
        # gfl2/stat_ocr.py's inner_blobs/projection/hu_fallback convention --
        # agent_b_hist only accumulates time on the fraction of glyphs where
        # Agent A was unsure and Agent B actually ran (see _classify()).
        # feature_extraction itself gets its own children (docs/decisions.txt
        # #58) broken down by FEATURE_BLOCK_NAMES, instead of one flat leaf --
        # this is where debugs/debug_stat_ocr_fft_feature_timing.py's
        # standalone measurement (vstroke+hbar ~84% of feature time) is meant
        # to show up in the SAME pipeline_summary tree every other engine's
        # timing already reports through, not a separate one-off script.
        if timer is not None:
            from gfl2.timing import Span as _Span
            if acc[0] > 0:
                feat_span = _Span("feature_extraction", acc[0])
                for _name, _elapsed in zip(FEATURE_BLOCK_NAMES, feature_acc):
                    if _elapsed > 0:
                        feat_span.children.append(_Span(_name, _elapsed))
                classify_span.children.append(feat_span)
            for _name, _elapsed in zip(("agent_a_gpr", "agent_b_hist"), acc[1:]):
                if _elapsed > 0:
                    classify_span.children.append(_Span(_name, _elapsed))

        return result


# ─────────────────────────────────────────────────────────────────────────────
# Template builder (pct only)
# ─────────────────────────────────────────────────────────────────────────────

def build_templates(
    training:     list[dict],
    verbose:      bool = True,
    gt_overrides: "dict | None" = None,
) -> dict:
    """
    Build and save nearest-centroid templates from a list of training dicts:
        {"cell": np.ndarray, "pct": str, "val": str, "source": str (optional)}

    val is intentionally skipped -- no centroids are built or written for it
    (see module docstring / _reconstruct_val).  Mirrors gfl2/stat_ocr.py's
    build_templates()'s gt_overrides contract: explicit gt_overrides=None
    auto-loads stat_gt_overrides.json from the project root if present; pass
    {} to disable entirely.
    """
    if gt_overrides is None:
        _gt_file = Path("stat_gt_overrides.json")
        gt_overrides = json.loads(_gt_file.read_text(encoding="utf-8")) if _gt_file.exists() else {}
    if gt_overrides:
        n_applied = 0
        for item in training:
            ov = gt_overrides.get(item.get("source"))
            if ov and "pct" in ov:
                item["pct"] = ov["pct"]
                n_applied += 1
        if verbose and n_applied:
            print(f"  Applied {n_applied} GT override(s) from stat_gt_overrides.json "
                  "(corrects known Tesseract mislabels before training)")

    buckets: dict[str, list] = defaultdict(list)
    n_cells = 0
    for item in training:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, label in glyphs:
            buckets[label].append(compute_features(norm))
        n_cells += 1

    # Agent A (gpr): plain per-digit mean, unnormalized -- same as before.
    gpr_templates = {d: np.mean([f[N_BINS:] for f in v], axis=0).tolist()
                      for d, v in buckets.items()}

    # Agent B (hist): z-score normalize using the POOLED training distribution
    # (all digits together, not per-digit) before taking per-digit means --
    # this must match how StatOcrFft._classify normalizes a query glyph at
    # inference time (same mu/sigma for every digit).  See module docstring's
    # TWO-AGENT CLASSIFIER section for why this is a separate agent instead
    # of being folded into the same feature vector as gpr.
    all_hist = np.array([f[:N_BINS] for v in buckets.values() for f in v])
    hist_mu    = all_hist.mean(axis=0)
    hist_sigma = all_hist.std(axis=0) + 1e-9
    hist_templates = {
        d: np.mean([(f[:N_BINS] - hist_mu) / hist_sigma for f in v], axis=0).tolist()
        for d, v in buckets.items()
    }

    pct_templates = {
        "gpr": gpr_templates,
        "hist": hist_templates,
        "hist_mu": hist_mu.tolist(),
        "hist_sigma": hist_sigma.tolist(),
    }
    templates = {"pct": pct_templates, "val": {}}

    def _write_font_py(path, data):
        src = "# auto-generated (FFT+Gabor exploration) — do not edit\nDATA = " + json.dumps(data, indent=2) + "\n"
        path.write_text(src, encoding="utf-8")

    _FONTS_DIR.mkdir(parents=True, exist_ok=True)
    _write_font_py(PCT_TMPL_F, templates)

    if verbose:
        counts = {d: len(buckets[d]) for d in sorted(buckets)}
        print(f"\nBuilt two-agent FFT+Gabor centroids from {n_cells} cells")
        print(f"  pct -> {PCT_TMPL_F}  chars: {counts}")
        print(f"  val -> skipped (not implemented -- see module docstring)")

    return templates


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark / verification
# ─────────────────────────────────────────────────────────────────────────────

def verify(
    image_paths:  list[Path],
    verbose:      bool = True,
    gt_overrides: dict = None,
    gt_cache:     "dict | None" = None,
    enable_pair_tiebreak: bool = PAIR_TIEBREAK_DEFAULT,
    enable_vstroke_gate: bool = VSTROKE_GATE_DEFAULT,
    enable_hierarchical: bool = HIERARCHICAL_DEFAULT,
) -> dict:
    """
    Compare the FFT+Gabor pct classifier against Tesseract ground
    truth.  val is always reported as not-implemented rather than a
    misleading 0% -- this engine never attempts val, so a 0% figure would
    read as a bug rather than the intentional gap it is.

    Also reports per-cell classify wall-clock mean/stdev/coefficient-of-
    variation.  Tracking speed and variance (not just accuracy) is this
    exploration's stated goal (docs/known_issues.txt §15): a lower-variance,
    faster classifier than gfl2/stat_ocr.py's multi-phase projection+Hu
    pipeline, if accuracy ever catches up.  Every --verify run measures this
    directly instead of relying on a one-off benchmark going stale.

    gt_cache: explicit None auto-loads tests/inputs/daily/tess_gt_cache.py
      (debugs/build_tess_gt_cache.py) so this doesn't re-run Tesseract
      against the same static single/*.png images on every call -- we are
      not testing Tesseract, and it's the same corpus every time.  Pass {}
      to force live Tesseract for every cell.

    enable_pair_tiebreak: DISABLED BY DEFAULT -- see module docstring's
      PAIR TIEBREAK section.  Pass True to verify with it enabled.

    enable_vstroke_gate: DISABLED BY DEFAULT -- see the VSTROKE GATE
      section above _vstroke_feature and docs/known_issues.txt §24.  Pass
      True to verify with vstroke's expensive 2D-sliding search skipped
      for glyphs gated out of the {1,4,7} line-dominant group -- the
      timing report below is where the real speed effect (not just the
      in-sample gate measurement debugs/debug_gabor_45_zscore_verify.py
      reported) shows up.

    enable_hierarchical: DISABLED BY DEFAULT -- see the module docstring's
      HIERARCHICAL CLASSIFIER section.  Pass True to verify with the
      branching decision-tree classifier instead of the flat two-agent
      path; enable_pair_tiebreak/enable_vstroke_gate are ignored when this
      is True (both are specific to the flat path).
    """
    import statistics
    from gfl2.stat_ocr import _load_tess_gt_cache
    from gfl2.timing import TimerStack, pipeline_summary
    run_start = datetime.now().isoformat(timespec="seconds")
    engine  = StatOcrFft.load(enable_pair_tiebreak=enable_pair_tiebreak,
                               enable_vstroke_gate=enable_vstroke_gate,
                               enable_hierarchical=enable_hierarchical)
    if gt_cache is None:
        gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, gt_cache=gt_cache)

    _GT_FILE = Path("stat_gt_overrides.json")
    if gt_overrides is None:
        gt_overrides = json.loads(_GT_FILE.read_text()) if _GT_FILE.exists() else {}
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and "pct" in ov:
            item["pct"] = ov["pct"]

    pct_total = pct_match = pct_miss = 0
    mismatches = []
    classify_times = []
    roots = []

    for item in samples:
        cell_timer = TimerStack()
        t0 = time.perf_counter()
        with cell_timer.timed("cell"):
            blob_pct, _blob_val = engine.read(item["cell"], timer=cell_timer)
        classify_times.append(time.perf_counter() - t0)
        roots.append(cell_timer.root)

        if item["pct"]:
            pct_total += 1
            if blob_pct is None:
                pct_miss += 1
                mismatches.append((item["source"], "pct", item["pct"], blob_pct))
            elif blob_pct != item["pct"]:
                mismatches.append((item["source"], "pct", item["pct"], blob_pct))
            else:
                pct_match += 1

    mean_us  = statistics.mean(classify_times) * 1e6 if classify_times else 0.0
    stdev_us = statistics.pstdev(classify_times) * 1e6 if len(classify_times) > 1 else 0.0
    cv       = (stdev_us / mean_us) if mean_us else 0.0

    if verbose:
        def pct_str(n, d): return f"{100*n/d:.1f}%" if d else "n/a"
        print(f"\n{'-'*60}")
        print(f"Generated: {run_start}  (run start)")
        print(f"StatOcrFft verify  ({len(image_paths)} images, {len(samples)} cells)"
              f"  pair_tiebreak={'ON' if enable_pair_tiebreak else 'off'}"
              f"  vstroke_gate={'ON' if enable_vstroke_gate else 'off'}"
              f"  hierarchical={'ON' if enable_hierarchical else 'off'}")
        print(f"  pct  {pct_match}/{pct_total} correct  "
              f"({pct_str(pct_match, pct_total)})  "
              f"{pct_miss} no-read")
        print(f"  val  not implemented (FFT exploration covers pct-line only "
              f"-- see docs/known_issues.txt §15)")
        print(f"  timing  mean={mean_us:.1f}us/cell  stdev={stdev_us:.1f}us  "
              f"cv={cv:.2f}  (n={len(classify_times)} cells)")
        if mismatches:
            print(f"\nFirst 20 mismatches:")
            for src, kind, expected, got in mismatches[:20]:
                print(f"  {src}  {kind}  expected={expected!r}  got={got!r}")
        print(f"{'-'*60}")
        # Same hierarchical breakdown convention as gfl2/stat_ocr.py's real
        # production runs (pipeline_summary over per-unit TimerStack roots) --
        # not a bespoke standalone timing script.  feature_extraction's own
        # children (hist/gabor/paren/ring/loop/vstroke/hbar) are where
        # docs/known_issues.txt §19's "vstroke+hbar dominate" claim is meant
        # to be checked, in the same tree every other engine's timing is.
        print(pipeline_summary([item["source"] for item in samples], roots, unit="cell"))

    return {
        "pct_correct": pct_match, "pct_total": pct_total,
        "val_correct": None, "val_total": None,   # not implemented, not 0 -- see docstring
        "mismatches":  mismatches,
        "classify_time_mean_us":  mean_us  if classify_times else None,
        "classify_time_stdev_us": stdev_us if classify_times else None,
    }


def _feature_set_desc() -> str:
    """Human-readable feature composition string, built from the live
    N_* constants rather than hand-maintained -- so it can't silently go
    stale the next time a feature is added/removed/resized, the way the
    module docstring's own hardcoded copies of this string have had to be
    manually kept in sync in the past."""
    return (
        f"hist({N_BINS}) + gabor({N_ORIENT}) + paren({N_PAREN}) + "
        f"ring({N_RINGS}) + loop({N_LOOP}) + vstroke({N_VSTROKE}) + "
        f"hbar({N_HBAR}) = {N_FEAT}-dim total, {N_FEAT - N_BINS}-dim gpr"
    )


def verify_glyphs(
    image_paths:  list[Path],
    verbose:      bool = True,
    gt_overrides: dict = None,
    gt_cache:     "dict | None" = None,
    enable_pair_tiebreak: bool = PAIR_TIEBREAK_DEFAULT,
    enable_vstroke_gate: bool = VSTROKE_GATE_DEFAULT,
    enable_hierarchical: bool = HIERARCHICAL_DEFAULT,
) -> dict:
    """
    GLYPH-level (not cell-level) verification: classify every individual
    labelled digit glyph and tally classified/correct/misclassified/
    unknown PER DIGIT ('0'-'9').  This is the permanent, reusable version
    of the ad-hoc per-digit breakdowns that this exploration's own
    known_issues.txt §15 investigation repeatedly hand-rolled in one-off
    scripts (e.g. the "STANDALONE ABLATION" tables) -- every future
    per-digit question should go through this function and
    debugs/compare_stat_ocr_fft_runs.py instead of a new throwaway script.

    Cell-level verify() above answers "did the whole reconstructed pct
    string match" -- a single wrong glyph fails the entire multi-digit
    cell, which is the right question for production-shape accuracy but
    the wrong one for "which DIGIT is this classifier actually bad at."
    This function answers that second question directly, using the same
    label-aligned extraction build_templates() trains from
    (_extract_pct_digit_glyphs), not the label-free inference path.

    Returns a dict with a "per_digit" breakdown, "totals", and "timing" --
    see debugs/compare_stat_ocr_fft_runs.py for the comparison-report
    consumer of this shape, and debugs/persist_run_result.py for how a
    result like this survives across sessions.
    """
    import statistics
    from gfl2.stat_ocr import _load_tess_gt_cache
    run_start = datetime.now().isoformat(timespec="seconds")
    engine = StatOcrFft.load(enable_pair_tiebreak=enable_pair_tiebreak,
                              enable_vstroke_gate=enable_vstroke_gate,
                              enable_hierarchical=enable_hierarchical)
    templates = engine._pct

    if gt_cache is None:
        gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)

    _GT_FILE = Path("stat_gt_overrides.json")
    if gt_overrides is None:
        gt_overrides = json.loads(_GT_FILE.read_text()) if _GT_FILE.exists() else {}
    for item in samples:
        ov = gt_overrides.get(item["source"])
        if ov and "pct" in ov:
            item["pct"] = ov["pct"]

    per_digit = {d: {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0}
                 for d in TRAIN_CHARS}
    classify_times = []

    for item in samples:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, true_label in glyphs:
            bucket = per_digit.setdefault(
                true_label, {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0})
            t0 = time.perf_counter()
            pred = _classify(norm, templates, enable_pair_tiebreak=enable_pair_tiebreak,
                              enable_vstroke_gate=enable_vstroke_gate,
                              enable_hierarchical=enable_hierarchical)
            classify_times.append(time.perf_counter() - t0)

            bucket["classified"] += 1
            if pred == '?':
                bucket["unknown"] += 1
            elif pred == true_label:
                bucket["correct"] += 1
            else:
                bucket["misclassified"] += 1

    totals = {
        "classified":     sum(b["classified"] for b in per_digit.values()),
        "correct":        sum(b["correct"] for b in per_digit.values()),
        "misclassified":  sum(b["misclassified"] for b in per_digit.values()),
        "unknown":        sum(b["unknown"] for b in per_digit.values()),
    }
    totals["accuracy_pct"] = (
        round(100 * totals["correct"] / totals["classified"], 2) if totals["classified"] else None
    )

    mean_us  = statistics.mean(classify_times) * 1e6 if classify_times else 0.0
    stdev_us = statistics.pstdev(classify_times) * 1e6 if len(classify_times) > 1 else 0.0
    cv       = (stdev_us / mean_us) if mean_us else 0.0

    if verbose:
        print(f"\n{'-'*60}")
        print(f"Generated: {run_start}  (run start)")
        print(f"StatOcrFft verify_glyphs  ({len(image_paths)} images, "
              f"{totals['classified']} glyphs)  pair_tiebreak={'ON' if enable_pair_tiebreak else 'off'}"
              f"  vstroke_gate={'ON' if enable_vstroke_gate else 'off'}"
              f"  hierarchical={'ON' if enable_hierarchical else 'off'}")
        print(f"  feature_set  {_feature_set_desc()}")
        print(f"  {'digit':>6} {'classified':>10} {'correct':>8} {'misclassified':>13} {'unknown':>8}")
        for d in TRAIN_CHARS:
            b = per_digit.get(d, {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0})
            print(f"  {d:>6} {b['classified']:>10} {b['correct']:>8} "
                  f"{b['misclassified']:>13} {b['unknown']:>8}")
        print(f"  {'TOTAL':>6} {totals['classified']:>10} {totals['correct']:>8} "
              f"{totals['misclassified']:>13} {totals['unknown']:>8}  "
              f"({totals['accuracy_pct']}% correct)")
        print(f"  timing  mean={mean_us:.1f}us/glyph  stdev={stdev_us:.1f}us  "
              f"cv={cv:.2f}  (n={len(classify_times)} glyphs)")
        print(f"{'-'*60}")

    return {
        "run_start":   run_start,
        "corpus":      f"{len(image_paths)} images, {totals['classified']} glyphs",
        "feature_set": _feature_set_desc(),
        "pair_tiebreak": enable_pair_tiebreak,
        "per_digit":   per_digit,
        "totals":      totals,
        "timing": {
            "classify_time_mean_us":  round(mean_us, 1) if classify_times else None,
            "classify_time_stdev_us": round(stdev_us, 1) if classify_times else None,
            "classify_time_cv":       round(cv, 3) if classify_times else None,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="StatOcrFft (FFT+Gabor exploration variant, "
                     "docs/known_issues.txt §15) template builder / verifier. "
                     "pct-line only -- val is not implemented."
    )
    parser.add_argument("--build",  action="store_true",
                        help="Build pct centroids from images and save")
    parser.add_argument("--verify", action="store_true",
                        help="Verify pct classifier vs Tesseract ground truth "
                             "(also reports per-cell timing mean/stdev)")
    parser.add_argument("--verify-glyphs", action="store_true",
                        help="GLYPH-level verify: per-digit classified/correct/"
                             "misclassified/unknown breakdown (see verify_glyphs() "
                             "docstring). Persists its result via "
                             "debugs/persist_run_result.py so it can be diffed "
                             "later with debugs/compare_stat_ocr_fft_runs.py.")
    parser.add_argument("--label", default=None,
                        help="Label suffix for --verify-glyphs' persisted report "
                             "filename (<commit>_<dirty>_<label>.json). Defaults to "
                             "'pt-on'/'pt-off' (from --enable-pair-tiebreak) so "
                             "re-running with the other flag value doesn't clobber "
                             "the first report at the same commit/dirty state.")
    parser.add_argument("--images", default="single/*.png",
                        help="Glob of images to use  [default: single/*.png]")
    parser.add_argument("--gt-overrides", default=None,
                        help="JSON file of GT overrides {source: {pct}} "
                             "[default: stat_gt_overrides.json if present]")
    parser.add_argument("--no-gt-cache", action="store_true",
                        help="Force live Tesseract for every cell instead of "
                             "tests/inputs/daily/tess_gt_cache.py (debugs/"
                             "build_tess_gt_cache.py)")
    parser.add_argument("--enable-pair-tiebreak", action="store_true",
                        help="Enable the PAIR TIEBREAK override (disabled by "
                             "default, see module docstring) for --verify")
    parser.add_argument("--enable-vstroke-gate", action="store_true",
                        help="Enable the vstroke GATE (disabled by default, see "
                             "the VSTROKE GATE section above _vstroke_feature and "
                             "docs/known_issues.txt §24) for --verify/--verify-glyphs "
                             "-- skips vstroke's expensive 2D-sliding search for "
                             "glyphs gated out of the {1,4,7} line-dominant group")
    parser.add_argument("--enable-hierarchical", action="store_true",
                        help="Use the HIERARCHICAL CLASSIFIER (disabled by "
                             "default, see module docstring) instead of the flat "
                             "two-agent path for --verify/--verify-glyphs -- "
                             "ignores --enable-pair-tiebreak/--enable-vstroke-gate "
                             "when set (both are specific to the flat path)")
    args = parser.parse_args()

    if not args.build and not args.verify and not args.verify_glyphs:
        parser.print_help()
        sys.exit(1)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                         if "debug" not in Path(p).stem)
    if not image_paths:
        print(f"No images matched: {args.images}", file=sys.stderr)
        sys.exit(1)

    print(f"Images: {len(image_paths)}")

    from gfl2.stat_ocr import _load_tess_gt_cache
    gt_cache = {} if args.no_gt_cache else (_load_tess_gt_cache() or {})
    if gt_cache:
        print(f"Using Tesseract GT cache: {len(gt_cache)} cells "
              f"(tests/inputs/daily/tess_gt_cache.py)")

    if args.build:
        print("Collecting training data via Tesseract ...")
        t0 = time.perf_counter()
        training = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
        print(f"  {len(training)} cells collected  ({time.perf_counter()-t0:.1f}s)")

        gt_file = Path(args.gt_overrides) if args.gt_overrides else Path("stat_gt_overrides.json")
        gt_overrides = json.loads(gt_file.read_text(encoding="utf-8")) if gt_file.exists() else {}
        for item in training:
            ov = gt_overrides.get(item["source"])
            if ov and "pct" in ov:
                item["pct"] = ov["pct"]

        print("Building FFT+Gabor centroids ...")
        t1 = time.perf_counter()
        build_templates(training)
        print(f"  Done  ({time.perf_counter()-t1:.1f}s)  -> {PCT_TMPL_F}")

    if args.verify:
        gt_file = Path(args.gt_overrides) if args.gt_overrides else Path("stat_gt_overrides.json")
        gt_overrides = json.loads(gt_file.read_text(encoding="utf-8")) if gt_file.exists() else None
        verify(image_paths, verbose=True, gt_overrides=gt_overrides, gt_cache=gt_cache,
               enable_pair_tiebreak=args.enable_pair_tiebreak,
               enable_vstroke_gate=args.enable_vstroke_gate,
               enable_hierarchical=args.enable_hierarchical)

    if args.verify_glyphs:
        gt_file = Path(args.gt_overrides) if args.gt_overrides else Path("stat_gt_overrides.json")
        gt_overrides = json.loads(gt_file.read_text(encoding="utf-8")) if gt_file.exists() else None
        result = verify_glyphs(image_paths, verbose=True, gt_overrides=gt_overrides, gt_cache=gt_cache,
                                enable_pair_tiebreak=args.enable_pair_tiebreak,
                                enable_vstroke_gate=args.enable_vstroke_gate,
                                enable_hierarchical=args.enable_hierarchical)
        from debugs.persist_run_result import save_run_result
        label = args.label or ("pt-on" if args.enable_pair_tiebreak else "pt-off")
        if args.enable_vstroke_gate:
            label += "_vgate-on"
        if args.enable_hierarchical:
            label += "_hier-on"
        out = save_run_result(result, subdir="stat_ocr_fft_glyph_runs", label=label)
        print(f"Saved glyph-level report -> {out}")
        print(f"Compare with: python debugs/compare_stat_ocr_fft_runs.py <old.json> {out}")


if __name__ == "__main__":
    sys.path.insert(0, str(_HERE))
    _main()
