# -*- coding: utf-8 -*-
"""
tests/test_stat_ocr_v0_3_0.py

Unit tests for _count_inner_blobs (always run) -- the shared hole-count
primitive gfl2.stat_ocr_v0_3_0 imports directly from gfl2.stat_ocr_v0_1_0, rather than
duplicating (decision 47's full-duplication policy does NOT apply to this
one function; it's generic segmentation/geometry, not an engine-specific
classifier).

Integration tests load crops from tests/inputs/daily/*.png (the committed,
curated 18-image fixture set -- see tests/inputs/daily/meaningful_images.py)
and assert that gfl2.stat_ocr_v0_3_0.StatOcrV0_3_0.read() matches the ground-truth
(pct, val) stored in tests/inputs/daily/stat_data.py.

Crop pixels come from the `daily_stat_crops` fixture (tests/conftest.py) --
pure panel/frame/column segmentation, no OCR engine and no Tesseract call of
any kind, so this test exercises ONLY StatOcrV0_3_0's own classify()/
classify_val() trees, nothing else can quietly resolve a miss underneath it.

Per docs/known_issues.txt §31/§32 (decisions.txt #83/#91), the v0_3_0 engine
reached 100.0% pct accuracy on this corpus (pre-skeleton) once
stat_gt_overrides.json is applied.

UPDATE (known_issues.txt §37, decisions.txt #99): the {2,3,5} leaf in both
classify() (pct) and classify_val() (val) was replaced -- a magnitude-gate
design (spread_x/top_band_5/bottom_band_23 for pct;
_bottom_row_deficit/_left_top_count for val) is SUPERSEDED by a Zhang-Suen
skeleton endpoint-connectivity classifier. This is a REAL accuracy trade,
not a bug fix: the new leaf abstains ('?') on some glyphs the old one used
to guess correctly (a deliberate choice -- known_issues.txt §37's
motivating case was a magnitude gate CONFIDENTLY WRONG, which this design
structurally cannot do the same way for a routing failure -- see
known_issues.txt §37 for the full corpus-wide numbers). On THIS 18-image
curated set specifically:
  - known_issues.txt §37's original motivating case
    (fb_d_20251019.png::p1_r2_col4) now reads correctly -- REMOVED from
    _KNOWN_FAILING_VAL_UNTRIAGED (now empty, deleted).
  - 4 of the 5 val cross-image threshold-cache-order cases
    (docs/known_issues.txt §36) now also read correctly -- REMOVED from
    _KNOWN_FAILING_VAL_CACHE_ORDER. This does NOT mean §36's underlying
    cache bug is fixed; these 4 cells' mismatching digit happened to be a
    2/3/5 that now resolves via the order-INSENSITIVE skeleton path
    instead of the order-sensitive old magnitude gate. One case
    (gm_d_20250908.png::p1_r0_col2, a non-2/3/5 digit) still exhibits §36's
    bug and remains xfailed.
  - 14 pct cells that were previously read correctly by the old magnitude
    gates now abstain ('?', so read() returns None for the whole cell) --
    added as _KNOWN_FAILING_PCT_SKELETON_ABSTENTION, xfail(strict=True) so
    any future recalibration that resolves an abstention surfaces as an
    unexpected pass forcing that entry's removal.

val is fully clean on this curated set now (_KNOWN_FAILING_VAL_UNTRIAGED
is empty and deleted) -- the skeleton swap's only remaining cost here is
the 14 pct abstentions above.

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
    from gfl2.stat_ocr_v0_1_0 import _count_inner_blobs
    norm = np.full((13, 8), 255, dtype=np.uint8)
    assert _count_inner_blobs(norm) == 0

def test_inner_blobs_empty_image():
    import numpy as np
    from gfl2.stat_ocr_v0_1_0 import _count_inner_blobs
    assert _count_inner_blobs(np.zeros((13, 8), dtype=np.uint8)) == 0

def test_inner_blobs_one_hole():
    import numpy as np
    from gfl2.stat_ocr_v0_1_0 import _count_inner_blobs
    norm = np.zeros((13, 8), dtype=np.uint8)
    norm[1:12, 1:7] = 255
    norm[3:10, 2:6] = 0
    assert _count_inner_blobs(norm) == 1

def test_inner_blobs_two_holes():
    import numpy as np
    from gfl2.stat_ocr_v0_1_0 import _count_inner_blobs
    norm = np.zeros((20, 12), dtype=np.uint8)
    norm[1:9,   1:11] = 255;  norm[2:8,   2:10] = 0
    norm[10:19, 1:11] = 255;  norm[11:18, 2:10] = 0
    assert _count_inner_blobs(norm) == 2

def test_inner_blobs_does_not_count_outer():
    import numpy as np
    from gfl2.stat_ocr_v0_1_0 import _count_inner_blobs
    norm = np.zeros((13, 8), dtype=np.uint8)
    norm[2:11, 2:6] = 255
    assert _count_inner_blobs(norm) == 0


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def ocr_v0_3_0():
    from gfl2.stat_ocr_v0_3_0 import StatOcrV0_3_0
    return StatOcrV0_3_0.load()


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

# val: cross-image threshold-cache order-dependency (docs/known_issues.txt
# §36). Confirmed by re-running each cell BOTH in isolation and after the
# other 17 curated images in this file's own processing order -- the
# isolated read matches the visually-confirmed real pixel content.
# UPDATE (known_issues.txt §37): 4 of the original 5 cases here now read
# correctly under the skeleton {2,3,5} leaf (order-insensitive) --
# REMOVED. Only gm_d_20250908.png::p1_r0_col2 (a non-2/3/5 digit,
# untouched by the skeleton swap) still exhibits the underlying §36 bug.
_KNOWN_FAILING_VAL_CACHE_ORDER = {
    ("gm_d_20250908.png",   "p1_r0_col2"),
}

# pct: the skeleton {2,3,5} leaf (known_issues.txt §37, decisions.txt #99)
# abstains ('?') on these 14 cells rather than guessing -- the old
# magnitude-gate leaf answered (correctly) every one of them. A DELIBERATE
# accuracy trade, not a bug: xfail(strict=True) so a future recalibration
# that resolves any of these surfaces as an unexpected pass, forcing this
# set to shrink.
_KNOWN_FAILING_PCT_SKELETON_ABSTENTION = {
    ("fb_d_20250930.png",   "p2_r3_col1"),
    ("fb_d_20251019.png",   "p2_r3_col1"),
    ("fb_d_20251112.png",   "p1_r3_col4"),
    ("fb_d_20260315.png",   "p2_r3_col1"),
    ("gm_d_20250908.png",   "p1_r0_col3"),
    ("gm_d_20250908.png",   "p2_r1_col3"),
    ("gm_d_20251019.png",   "p1_r3_col1"),
    ("gm_d_20251019.png",   "p2_r3_col1"),
    ("gm_d_20260202.png",   "p2_r3_col1"),
    ("ib_d_20250928.png",   "p1_r3_col1"),
    ("ib_d_20250928.png",   "p2_r3_col1"),
    ("ib_d_20251225.png",   "p2_r3_col1"),
    ("ib_d_20260112_1.png", "p2_r3_col1"),
    ("ib_d_20260114.png",   "p1_r3_col4"),
}


def _build_params():
    params = []
    for s, p, exp_pct, exp_val in _CROPS:
        marks = []
        if (s, p) in _KNOWN_FAILING_VAL_CACHE_ORDER:
            marks.append(pytest.mark.xfail(
                reason="StatOcrV0_3_0's adaptive threshold cache is order-"
                       "dependent across images in one run -- see this "
                       "file's module docstring. Not yet fixed.",
                strict=True,
            ))
        elif (s, p) in _KNOWN_FAILING_PCT_SKELETON_ABSTENTION:
            marks.append(pytest.mark.xfail(
                reason="Skeleton {2,3,5} leaf (known_issues.txt §37) "
                       "abstains on this cell rather than guessing -- see "
                       "this file's module docstring.",
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
def test_stat_cell_v0_3_0(ocr_v0_3_0, stat_fallback_collector, daily_stat_crops, source, part, exp_pct, exp_val):
    img = daily_stat_crops.get((source, part))
    if img is None:
        pytest.skip(f"crop not extractable: {source}::{part}")

    got_pct, got_val = ocr_v0_3_0.read(img)

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
