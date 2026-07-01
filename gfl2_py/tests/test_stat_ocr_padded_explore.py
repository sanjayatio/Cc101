# -*- coding: utf-8 -*-
"""
tests/test_stat_ocr_padded_explore.py — EXPLORATION duplicate of
tests/test_stat_ocr_hard_cases.py for docs/known_issues.txt §15.

Exercises debugs/stat_ocr_padded.StatOcrPadded (aspect-preserving glyph
normalization) against the SAME ground truth (tests/inputs/daily/stat.json)
used by the production hard-cases suite, so the two pass counts are directly
comparable.

This file is a deliberate full copy, not a parametrized variant of the
original — including its own fallback-collector fixture that writes to
tests/outputs/daily/stat_padded.json (NOT stat.json) so a bad run here can
never overwrite the production tracking file that
tests/test_stat_ocr_hard_cases.py depends on.

Skip conditions: same as the original (see that file's docstring), plus
skips entirely if the padded templates haven't been built yet
(debugs/stat_ocr_padded.py --build).
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import cv2
import pytest

_ROOT     = Path(__file__).parent.parent
_DAILY    = _ROOT / "tests" / "inputs" / "daily"
_MANIFEST = _DAILY / "stat.json"

_PART_RE  = re.compile(r'_(p\d+_r\d+_col\d+)$')


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def stat_crops_padded():
    """Extract all stat crops from single/ source images, keyed by (source, part).

    Deliberate duplicate of the `stat_crops` fixture in test_stat_ocr_hard_cases.py —
    same extraction logic, own fixture name so this file has zero shared session
    state with the production test module.
    """
    from debugs.stat_ocr_padded import _collect_cells
    single = _ROOT / "single"
    sources = {s for s, _, _, _ in _CROPS}
    image_paths = [single / s for s in sources if (single / s).exists()]
    if not image_paths:
        return {}
    results = _collect_cells(image_paths, tess_only=False)
    crops: dict[tuple[str, str], object] = {}
    for item in results:
        source_key = item["img_path"].name
        m = _PART_RE.search(item["source"])
        if m:
            crops[(source_key, m.group(1))] = item["cell"]
    return crops


def _need_rebuild(engine) -> bool:
    val_t = getattr(engine, "_val", {})
    return bool(val_t) and "inner_blobs" not in next(iter(val_t.values()))


@pytest.fixture(scope="module")
def ocr_padded():
    try:
        from debugs.stat_ocr_padded import StatOcrPadded
        engine = StatOcrPadded.load()
    except FileNotFoundError as exc:
        pytest.skip(str(exc))
    except Exception as exc:
        if isinstance(exc, (json.JSONDecodeError, ValueError, UnicodeDecodeError)):
            pytest.skip("padded templates unreadable: " + str(exc)[:80])
        raise
    if _need_rebuild(engine):
        pytest.skip(
            "Padded templates pre-date inner_blobs. "
            "Run: python debugs/stat_ocr_padded.py --build --images single/"
        )
    return engine


def _load_manifest() -> list[tuple[str, str, str, str]]:
    """Same manifest loader as test_stat_ocr_hard_cases.py — duplicated on purpose."""
    if not _MANIFEST.exists():
        return []
    data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    crops = data.get("crops", {})

    if isinstance(crops, list):
        rows = []
        for entry in crops:
            stem = Path(entry["path"]).stem
            m = _PART_RE.search(stem)
            if m:
                source = stem[:m.start()] + ".png"
                rows.append((source, m.group(1), entry["pct"], entry["val"]))
        return rows

    rows = []
    for source_img, parts in crops.items():
        for entry in parts:
            rows.append((source_img, entry["part"], entry["pct"], entry["val"]))
    return rows


_CROPS = _load_manifest()

# Cases with the known, not-yet-fixed '2'/'3' val-digit confusion documented
# in docs/known_issues.txt §15 (aspect-preserving padding shifts the glyph by
# 1-2px at the 8px-wide val canvas, enough to flip '3' to '2').  Marked xfail
# (strict) rather than left as plain failures so `pytest tests/` stays green
# while this exploration is in progress, but any change in outcome is still
# loud: a case that starts passing here XPASSes (strict -> reported as a
# failure, signalling it should be removed from this set) and any *other*
# case that regresses still fails normally.
_KNOWN_FAILING = {
    ("ib_d_20260112_1.png", "p1_r1_col2"),
    ("ib_d_20260112_1.png", "p1_r2_col4"),
    ("ib_d_20260112_1.png", "p2_r1_col2"),
    ("fb_d_20250928.png",   "p1_r1_col2"),
    ("fb_d_20251022.png",   "p1_r1_col2"),
    ("ib_d_20250928.png",   "p1_r2_col4"),
    ("ib_d_20250929.png",   "p2_r1_col2"),
    ("ib_d_20251023.png",   "p1_r1_col2"),
    ("ib_d_20251024.png",   "p2_r1_col2"),
    ("fb_d_20250930.png",   "p1_r1_col2"),
    ("fb_d_20251003.png",   "p2_r1_col2"),
    ("fb_d_20251004.png",   "p1_r1_col2"),
    ("fb_d_20251004.png",   "p2_r1_col2"),
    ("fb_d_20251019.png",   "p2_r1_col2"),
    ("fb_d_20251023.png",   "p2_r1_col2"),
    ("fb_d_20251024.png",   "p1_r1_col2"),
    ("gm_d_20250930.png",   "p2_r1_col2"),
    ("gm_d_20251020.png",   "p1_r1_col2"),
    ("gm_d_20251020.png",   "p2_r1_col2"),
    ("gm_d_20251020.png",   "p2_r2_col4"),
    ("gm_d_20251023.png",   "p1_r1_col2"),
    ("gm_d_20251023.png",   "p2_r1_col2"),
}


def _build_params():
    params = []
    for s, p, exp_pct, exp_val in _CROPS:
        marks = []
        if (s, p) in _KNOWN_FAILING:
            marks.append(pytest.mark.xfail(
                reason="§15 padded-normalize exploration: known unresolved "
                       "'2'/'3' val-digit confusion (docs/known_issues.txt §15)",
                strict=True,
            ))
        params.append(pytest.param(s, p, exp_pct, exp_val, marks=marks, id=f"{s}::{p}"))
    return params


_PARAMS = _build_params()


# ── own fallback collector — writes to stat_padded.json, NEVER stat.json ─────

@pytest.fixture(scope="session")
def stat_fallback_collector_padded(request):
    save_crops = not request.config.getoption("--no-save-failing-crops", default=False)
    collector = {"save_crops": save_crops, "items": []}
    yield collector
    _write_stat_fallbacks_padded(collector, _ROOT)


def _write_stat_fallbacks_padded(collector: dict, project_root: Path) -> None:
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
        "note":  "PADDED-NORMALIZE exploration (§15) — crops where padded pipeline "
                 "diverges from GT. Not the production stat.json.",
        "crops": grouped,
    }
    (out_dir / "stat_padded.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    if collector["save_crops"]:
        for item in items:
            cell = item.get("cell")
            if cell is not None:
                crop_name = f"{Path(item['source']).stem}_{item['part']}_padded.png"
                cv2.imwrite(str(out_dir / crop_name), cell)


# ── integration: parametrized over all crops in stat.json ────────────────────

@pytest.mark.parametrize(
    "source,part,exp_pct,exp_val",
    _PARAMS,
)
def test_stat_cell_padded(ocr_padded, stat_fallback_collector_padded, stat_crops_padded,
                           source, part, exp_pct, exp_val):
    img = stat_crops_padded.get((source, part))
    if img is None:
        pytest.skip(f"crop not extractable: {source}::{part}")

    got_pct, got_val = ocr_padded.read(img)

    pct_ok = (not exp_pct) or (got_pct == exp_pct)
    val_ok = (not exp_val) or (got_val == exp_val)

    if not pct_ok or not val_ok:
        stat_fallback_collector_padded["items"].append({
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
