# -*- coding: utf-8 -*-
"""
tests/test_stat_ocr_dp.py

Unit tests for _count_inner_blobs (always run) -- the shared hole-count
primitive gfl2.stat_ocr_dp imports directly from gfl2.stat_ocr, rather than
duplicating (decision 47's full-duplication policy does NOT apply to this
one function; it's generic segmentation/geometry, not an engine-specific
classifier).

Integration tests load crops from tests/inputs/daily/*.png (the committed,
curated 18-image fixture set -- see tests/inputs/daily/meaningful_images.py)
and assert that gfl2.stat_ocr_dp.StatOcrDp.read() matches the ground-truth
(pct, val) stored in tests/inputs/daily/stat_data.py.

Crop pixels come from the `daily_stat_crops` fixture (tests/conftest.py) --
pure panel/frame/column segmentation, no OCR engine and no Tesseract call of
any kind, so this test exercises ONLY StatOcrDp's own classify()/
classify_val() trees, nothing else can quietly resolve a miss underneath it.

Per docs/known_issues.txt §31/§32 (decisions.txt #83/#91), the dp engine
reaches 100.0% pct accuracy on this corpus once stat_gt_overrides.json is
applied -- confirmed here too (647/647 pct cells pass outright).

val is NOT clean. Running this file surfaced two distinct problems, both
xfail(strict=True) below (not excluded -- kept running so a fix shows up
as an unexpected-pass and forces the xfail to be deleted):

  1. A genuine, previously-undocumented reproducibility bug in
     gfl2.stat_ocr_dp.StatOcrDp: its adaptive per-(strip_height, ink_group)
     binarization threshold cache (self._thresh_cache) persists across
     images within a single engine instance/run, so the SAME cell can
     classify differently depending on which other images were processed
     earlier in that run -- confirmed directly (5 cases): isolating just
     the failing image reads the cell correctly; re-running it after the
     other 17 curated images (same order pytest's module-scoped `ocr_dp`
     fixture processes them in) reproduces the wrong answer, and the
     "correct" isolated answer was independently confirmed against the
     actual rendered pixels. This is the same *kind* of cross-cell cache
     contamination already documented for the pct-line's '%'-anchor in
     docs/known_issues.txt §32, now found on the val line too -- not yet
     written up as its own known_issues.txt entry.
  2. One remaining genuine StatOcrDp.classify_val() miss, order-independent:
     fb_d_20251019.png::p1_r2_col4 (GT '6635', visually confirmed correct;
     dp reads '6632' -- a real last-digit misclassification). This is the
     only entry left in _KNOWN_FAILING_VAL_UNTRIAGED; the other 9 cases
     originally found here turned out to be stale tess_gt_cache.py ground
     truth (Tesseract dropping or misreading a digit) -- visually confirmed
     against the real rendered pixels and corrected via
     stat_gt_overrides.json (both dp AND the padded engine independently
     agreed with the corrected value, which is strong evidence the
     original GT, not either engine, was wrong).

Skip conditions:
  - stat_data.py missing -> pytest.skip (regenerate: python tests/generate_stat_inputs.py "tests/inputs/daily/*.png")
  - crop PNG missing     -> pytest.skip (per parametrized case)
"""
from __future__ import annotations
import re
from pathlib import Path
import pytest

_ROOT     = Path(__file__).parent.parent
_DAILY    = _ROOT / "tests" / "inputs" / "daily"
_STAT_DATA_PY = _DAILY / "stat_data.py"

_PART_RE  = re.compile(r'_(p\d+_r\d+_col\d+)$')


# ── unit tests: _count_inner_blobs ────────────────────────────────────────────

def test_inner_blobs_zero_holes():
    import numpy as np
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.full((13, 8), 255, dtype=np.uint8)
    assert _count_inner_blobs(norm) == 0

def test_inner_blobs_empty_image():
    import numpy as np
    from gfl2.stat_ocr import _count_inner_blobs
    assert _count_inner_blobs(np.zeros((13, 8), dtype=np.uint8)) == 0

def test_inner_blobs_one_hole():
    import numpy as np
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.zeros((13, 8), dtype=np.uint8)
    norm[1:12, 1:7] = 255
    norm[3:10, 2:6] = 0
    assert _count_inner_blobs(norm) == 1

def test_inner_blobs_two_holes():
    import numpy as np
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.zeros((20, 12), dtype=np.uint8)
    norm[1:9,   1:11] = 255;  norm[2:8,   2:10] = 0
    norm[10:19, 1:11] = 255;  norm[11:18, 2:10] = 0
    assert _count_inner_blobs(norm) == 2

def test_inner_blobs_does_not_count_outer():
    import numpy as np
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.zeros((13, 8), dtype=np.uint8)
    norm[2:11, 2:6] = 255
    assert _count_inner_blobs(norm) == 0


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def ocr_dp():
    from gfl2.stat_ocr_dp import StatOcrDp
    return StatOcrDp.load()


def _load_manifest() -> list[tuple[str, str, str, str]]:
    """Return flat list of (source_img, part, pct, val) from stat_data.py's CROPS."""
    if not _STAT_DATA_PY.exists():
        return []
    ns: dict = {}
    exec(compile(_STAT_DATA_PY.read_text(encoding="utf-8"), str(_STAT_DATA_PY), "exec"), ns)
    crops = ns.get("CROPS", {})

    rows = []
    for source_img, parts in crops.items():
        for entry in parts:
            rows.append((source_img, entry["part"], entry["pct"], entry["val"]))
    return rows


_CROPS = _load_manifest()

# pct is not in either set below -- docs/known_issues.txt §32/decisions.txt
# #83 resolved the dp engine to 100.0% pct accuracy on this corpus (including
# the gm_d_20250908.png col3 cells that remain xfail for production/padded);
# a pct failure here is a real regression.
#
# val: cross-image threshold-cache order-dependency (see module docstring).
# Confirmed by re-running each cell BOTH in isolation and after the other 17
# curated images in this file's own processing order -- the isolated read
# matches the visually-confirmed real pixel content in every case checked.
_KNOWN_FAILING_VAL_CACHE_ORDER = {
    ("gm_d_20250908.png",   "p1_r0_col2"),
    ("gm_d_20260111.png",   "p1_r1_col3"),
    ("ib_d_20250928.png",   "p1_r1_col3"),
    ("ib_d_20251004.png",  "p1_r1_col3"),
    ("ib_d_20251020.png",  "p1_r1_col3"),
}

# val: reproduces regardless of order -- a genuine StatOcrDp.classify_val()
# miss (see module docstring). The 9 sibling cases originally here were
# stale tess_gt_cache.py ground truth, now fixed via stat_gt_overrides.json.
_KNOWN_FAILING_VAL_UNTRIAGED = {
    ("fb_d_20251019.png",  "p1_r2_col4"),
}


def _build_params():
    params = []
    for s, p, exp_pct, exp_val in _CROPS:
        marks = []
        if (s, p) in _KNOWN_FAILING_VAL_CACHE_ORDER:
            marks.append(pytest.mark.xfail(
                reason="StatOcrDp's adaptive threshold cache is order-"
                       "dependent across images in one run -- see this "
                       "file's module docstring. Not yet fixed.",
                strict=True,
            ))
        elif (s, p) in _KNOWN_FAILING_VAL_UNTRIAGED:
            marks.append(pytest.mark.xfail(
                reason="Untriaged val mismatch: mix of genuine "
                       "classify_val() misses and stale tess_gt_cache.py "
                       "GT -- see this file's module docstring.",
                strict=True,
            ))
        params.append(pytest.param(s, p, exp_pct, exp_val, marks=marks, id=f"{s}::{p}"))
    return params


_PARAMS = _build_params()


# ── integration: parametrized over all crops in stat_data.py ─────────────────

@pytest.mark.parametrize(
    "source,part,exp_pct,exp_val",
    _PARAMS,
)
def test_stat_cell_dp(ocr_dp, stat_fallback_collector, daily_stat_crops, source, part, exp_pct, exp_val):
    img = daily_stat_crops.get((source, part))
    if img is None:
        pytest.skip(f"crop not extractable: {source}::{part}")

    got_pct, got_val = ocr_dp.read(img)

    pct_ok = (not exp_pct) or (got_pct == exp_pct)
    val_ok = (not exp_val) or (got_val == exp_val)

    if not pct_ok or not val_ok:
        stat_fallback_collector["items"].append({
            "source":  source,
            "part":    part,
            "exp_pct": exp_pct, "got_pct": got_pct,
            "exp_val": exp_val, "got_val": got_val,
            "cell":    img,
        })

    if exp_pct:
        assert pct_ok, f"{source}::{part} pct: expected {exp_pct!r}, got {got_pct!r}"
    if exp_val:
        assert val_ok, f"{source}::{part} val: expected {exp_val!r}, got {got_val!r}"
