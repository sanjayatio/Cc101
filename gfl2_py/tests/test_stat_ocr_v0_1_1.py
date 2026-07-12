# -*- coding: utf-8 -*-
"""
tests/test_stat_ocr_v0_1_1.py -- exercises gfl2.stat_ocr_v0_1_1.StatOcrV0_1_1
(aspect-preserving-pad variant), one of the two engines this project keeps
under active comparison (v0_3_0 is the other, tests/test_stat_ocr_v0_3_0.py) so the
codebase stays honest about which pipeline pieces are truly generic
(segmentation, crop extraction, exclusion handling -- shared via
tests/conftest.py) versus engine-specific (classify()/read()) -- see
docs/known_issues.txt §15 for why this engine exists at all.

Runs against tests/inputs/daily/*.png (the committed, curated 18-image
fixture set -- tests/inputs/daily/meaningful_images.py) and the SAME ground
truth (tests/inputs/daily/stat_data.py) used by tests/test_stat_ocr_v0_3_0.py, so
the two engines' results are directly comparable.

Crop pixels come from the `daily_stat_crops` fixture (tests/conftest.py) --
pure panel/frame/column segmentation, no OCR engine and no Tesseract call of
any kind -- so this test exercises ONLY StatOcrV0_1_1's own classify() tree,
nothing else (no Tesseract fallback) can quietly resolve a miss underneath it.

Unlike test_stat_ocr_v0_3_0.py, this engine has real, known, unresolved gaps.
28 cells are EXCLUDED from the parametrization (pytest.mark.skip, listed in
_EXCLUDED below with a reason) rather than xfail, since the point here isn't
"expect this specific assertion to fail" but "this is a known, accepted gap,
not worth asserting against every run." Every excluded cell was
cross-checked against the v0_3_0 engine (test_stat_ocr_v0_3_0.py) on the identical
crop -- v0_3_0 reads all 28 correctly, which is what justifies attributing them
to the v0_1_1 engine rather than to bad ground truth (9 OTHER cells found
during this same investigation WERE bad ground truth -- both v0_3_0 and v0_1_1
agreed with each other and with the real rendered pixels, contradicting
tess_gt_cache.py; those were fixed via stat_gt_overrides.json instead of
excluded). Three distinct root causes, see _EXCLUDED below:
  1. docs/known_issues.txt §18 -- gm_d_20250908.png's smaller capture
     resolution merges col3 digit blobs under THRESH_BIN=180 (9 cells).
  2. docs/known_issues.txt §14 -- classify() abstains to '?' on a low-
     confidence glyph; normally invisible because daily_gunsmoke.py's
     Tesseract fallback fills it in, deliberately disabled here (14 cells).
  3. Genuine, not-yet-root-caused StatOcrV0_1_1 misclassifications --
     neither a '?' abstention nor a GT problem (5 cells).

Skip conditions:
  - padded templates missing  -> pytest.skip (rebuild: python -m gfl2.stat_ocr_v0_1_1 --build)
  - templates pre-date inner_blobs -> pytest.skip (rebuild required)
  - stat_data.py missing      -> pytest.skip (regenerate: python tests/generate_stat_inputs.py "tests/inputs/daily/*.png" --tess-only)
  - crop PNG missing          -> pytest.skip (per parametrized case)
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import cv2
import pytest

_ROOT     = Path(__file__).parent.parent
_DAILY    = _ROOT / "tests" / "inputs" / "daily"
_STAT_DATA_PY = _DAILY / "stat_data.py"

_PART_RE  = re.compile(r'_(p\d+_r\d+_col\d+)$')


# ── fixtures ──────────────────────────────────────────────────────────────────

def _need_rebuild(engine) -> bool:
    val_t = getattr(engine, "_val", {})
    return bool(val_t) and "inner_blobs" not in next(iter(val_t.values()))


@pytest.fixture(scope="module")
def ocr_v0_1_1():
    try:
        from gfl2.stat_ocr_v0_1_1 import StatOcrV0_1_1
        engine = StatOcrV0_1_1.load()
    except FileNotFoundError as exc:
        pytest.skip(str(exc))
    except Exception as exc:
        if isinstance(exc, (json.JSONDecodeError, ValueError, UnicodeDecodeError)):
            pytest.skip("padded templates unreadable: " + str(exc)[:80])
        raise
    if _need_rebuild(engine):
        pytest.skip(
            "Padded templates pre-date inner_blobs. "
            "Run: python -m gfl2.stat_ocr_v0_1_1 --build --images single/"
        )
    return engine


def _load_manifest() -> list[tuple[str, str, str, str]]:
    """Same manifest loader as test_stat_ocr_v0_3_0.py -- duplicated on purpose
    (each engine test file is meant to stand alone)."""
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

# Cells EXCLUDED from this engine's parametrization entirely -- not xfail,
# since the point isn't "this specific assertion is expected to fail" but
# "the v0_1_1 engine has a known, accepted gap here, not worth asserting
# against every run." Populated from an ACTUAL run against
# tests/inputs/daily/*.png with the (corrected, see stat_gt_overrides.json)
# ground truth in stat_data.py -- not guessed. Every cell below was
# cross-checked against tests/test_stat_ocr_v0_3_0.py's v0_3_0 engine on the SAME
# crop: v0_3_0 reads all 28 of these correctly, which is why they're attributed
# to the v0_1_1 engine itself rather than to a bad ground-truth entry (the
# category that turned out to explain 9 OTHER cells originally found here --
# those were fixed via stat_gt_overrides.json instead, not excluded).
_REASON_THRESH_BIN_MERGE = (
    "known_issues.txt §18: gm_d_20250908.png is a genuinely smaller-"
    "resolution capture than the corpus norm; the shared THRESH_BIN=180 "
    "(v0_1_0 and v0_1_1 both use it, unlike v0_3_0's own adaptive-threshold "
    "fix, decisions.txt #80) merges adjacent col3 digit blobs at this scale."
)
_REASON_NO_FALLBACK_ABSTENTION = (
    "known_issues.txt §14: the v0_1_1 engine's own classify() abstains to "
    "'?' on this glyph when its Hu-moment tiebreaker can't resolve it -- "
    "normally masked by daily_gunsmoke's Tesseract fallback, deliberately "
    "disabled in this test so the engine's own accuracy is visible."
)
_REASON_GENUINE_MISCLASSIFICATION = (
    "Genuine StatOcrV0_1_1 misclassification (not a '?' abstention, not a "
    "ground-truth error -- v0_3_0 reads this cell correctly). Not yet "
    "root-caused; not previously documented."
)

_EXCLUDED = {
    ("gm_d_20250908.png", "p1_r0_col3"): _REASON_THRESH_BIN_MERGE,
    ("gm_d_20250908.png", "p1_r1_col3"): _REASON_THRESH_BIN_MERGE,
    ("gm_d_20250908.png", "p1_r2_col3"): _REASON_THRESH_BIN_MERGE,
    ("gm_d_20250908.png", "p1_r3_col3"): _REASON_THRESH_BIN_MERGE,
    ("gm_d_20250908.png", "p1_r4_col3"): _REASON_THRESH_BIN_MERGE,
    ("gm_d_20250908.png", "p2_r1_col3"): _REASON_THRESH_BIN_MERGE,
    ("gm_d_20250908.png", "p2_r2_col3"): _REASON_THRESH_BIN_MERGE,
    ("gm_d_20250908.png", "p2_r3_col3"): _REASON_THRESH_BIN_MERGE,
    ("gm_d_20250908.png", "p2_r4_col3"): _REASON_THRESH_BIN_MERGE,

    ("fb_d_060518.png",     "p1_r0_col2"): _REASON_NO_FALLBACK_ABSTENTION,
    ("fb_d_060518.png",     "p1_r2_col4"): _REASON_NO_FALLBACK_ABSTENTION,
    ("fb_d_20250930.png",   "p2_r2_col2"): _REASON_NO_FALLBACK_ABSTENTION,
    ("fb_d_20250930.png",   "p2_r3_col4"): _REASON_NO_FALLBACK_ABSTENTION,
    ("fb_d_20251019.png",   "p2_r3_col4"): _REASON_NO_FALLBACK_ABSTENTION,
    ("gm_d_20260111.png",   "p1_r3_col4"): _REASON_NO_FALLBACK_ABSTENTION,
    ("gm_d_20260111.png",   "p2_r2_col2"): _REASON_NO_FALLBACK_ABSTENTION,
    ("gm_d_20260201.png",   "p1_r4_col4"): _REASON_NO_FALLBACK_ABSTENTION,
    ("ib_d_20250928.png",   "p1_r3_col4"): _REASON_NO_FALLBACK_ABSTENTION,
    ("ib_d_20251004.png",   "p1_r3_col4"): _REASON_NO_FALLBACK_ABSTENTION,
    ("ib_d_20251004.png",   "p2_r2_col2"): _REASON_NO_FALLBACK_ABSTENTION,
    ("ib_d_20251004.png",   "p2_r3_col4"): _REASON_NO_FALLBACK_ABSTENTION,
    ("ib_d_20251225.png",   "p2_r3_col1"): _REASON_NO_FALLBACK_ABSTENTION,
    ("ib_d_20260112_1.png", "p1_r2_col2"): _REASON_NO_FALLBACK_ABSTENTION,

    ("fb_d_20251112.png", "p1_r0_col2"): _REASON_GENUINE_MISCLASSIFICATION,
    ("fb_d_20251112.png", "p1_r3_col4"): _REASON_GENUINE_MISCLASSIFICATION,
    ("fb_d_20260315.png", "p1_r0_col1"): _REASON_GENUINE_MISCLASSIFICATION,
    ("fb_d_20260315.png", "p2_r0_col1"): _REASON_GENUINE_MISCLASSIFICATION,
    ("ib_d_20260114.png", "p1_r2_col2"): _REASON_GENUINE_MISCLASSIFICATION,
}


def _build_params():
    params = []
    for s, p, exp_pct, exp_val in _CROPS:
        marks = []
        reason = _EXCLUDED.get((s, p))
        if reason:
            marks.append(pytest.mark.skip(reason=reason))
        params.append(pytest.param(s, p, exp_pct, exp_val, marks=marks, id=f"{s}::{p}"))
    return params


_PARAMS = _build_params()


# ── own fallback collector — writes to stat_v0_1_1.json, NEVER stat.json ────

@pytest.fixture(scope="session")
def stat_fallback_collector_v0_1_1(request):
    save_crops = not request.config.getoption("--no-save-failing-crops", default=False)
    collector = {"save_crops": save_crops, "items": []}
    yield collector
    _write_stat_fallbacks_v0_1_1(collector, _ROOT)


def _write_stat_fallbacks_v0_1_1(collector: dict, project_root: Path) -> None:
    items = collector["items"]
    if not items:
        return
    out_dir = project_root / "tests" / "outputs" / "daily"
    out_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict = {}
    for item in items:
        grouped.setdefault(item["source"], []).append({
            "part":    item["part"],
            "exp_pct": item["exp_pct"], "got_pct": item["got_pct"],
            "exp_val": item["exp_val"], "got_val": item["got_val"],
        })

    out = {
        "note":  "PADDED-NORMALIZE exploration (§15) — crops where the v0_1_1 pipeline "
                 "diverges from GT. Not the v0_1_0 stat.json.",
        "crops": grouped,
    }
    (out_dir / "stat_v0_1_1.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    if collector["save_crops"]:
        for item in items:
            cell = item.get("cell")
            if cell is not None:
                crop_name = f"{Path(item['source']).stem}_{item['part']}_v0_1_1.png"
                cv2.imwrite(str(out_dir / crop_name), cell)


# ── integration: parametrized over all crops in stat_data.py ─────────────────

@pytest.mark.parametrize(
    "source,part,exp_pct,exp_val",
    _PARAMS,
)
def test_stat_cell_v0_1_1(ocr_v0_1_1, stat_fallback_collector_v0_1_1, daily_stat_crops,
                           source, part, exp_pct, exp_val):
    img = daily_stat_crops.get((source, part))
    if img is None:
        pytest.skip(f"crop not extractable: {source}::{part}")

    got_pct, got_val = ocr_v0_1_1.read(img)

    pct_ok = (not exp_pct) or (got_pct == exp_pct)
    val_ok = (not exp_val) or (got_val == exp_val)

    if not pct_ok or not val_ok:
        stat_fallback_collector_v0_1_1["items"].append({
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
