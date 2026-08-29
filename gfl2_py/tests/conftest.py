import sys
import json
import shutil
import py_compile
import tempfile
from pathlib import Path
import cv2
import pytest

sys.dont_write_bytecode = True

root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

# Recompile gfl2 with CHECKED_HASH before every test run so tests always
# execute against fresh source regardless of how files were last edited.
_gfl2 = root / "gfl2"
for _d in _gfl2.rglob("__pycache__"):
    try:
        shutil.rmtree(_d)
    except Exception:
        for _pyc in _d.glob("*.pyc"):
            try: _pyc.unlink(missing_ok=True)
            except Exception: pass

for _src in sorted(_gfl2.rglob("*.py")):
    try:
        py_compile.compile(str(_src), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH)
    except Exception:
        pass

# -- Seed doll assets for weekly-gunsmoke tests --------------------------------
# Writes go to the OS temp dir (not the project tree) to avoid phantom NTFS
# entries blocking writes for previously-deleted filenames.
#
# ASSETS_DIR in gfl2.asset_mapper is patched to this tmp path BEFORE
# weekly_gunsmoke is imported (it creates _doll_mapper at module level).

_SEED_LABELS = {
    "gm_250801.png": [
        ["Cheeta",       "Makiatto",    "Tololo",      "Colphne",      "QiongJiu"],
        ["Springfield",  "Sharkry",     "QiongJiu",    "Centaureissi", "Tololo"],
    ],
    "gm_250730.png": [
        ["QiongJiu",     "Springfield", "Centaureissi","Sharkry",      "Tololo"],
        ["Cheeta",       "Makiatto",    "Tololo",      "Colphne",      "QiongJiu"],
        ["Colphne",      "Springfield", "Makiatto",    "Tololo",       "QiongJiu"],
        ["QiongJiu",     "Cheeta",      "Vector",      "Centaureissi", "Sharkry"],
    ],
}

_TESTS_DIR = Path(__file__).parent / "inputs" / "weekly_gunsmoke"
_SEED_DIR  = Path(tempfile.gettempdir()) / "gfl2_test_seeds" / "dolls"
_SEED_DIR.mkdir(parents=True, exist_ok=True)
_DOLL_KEYS = ["doll1", "doll2", "doll3", "doll4", "doll5"]

import gfl2.asset_mapper as _am
_am.ASSETS_DIR = _SEED_DIR.parent


def _seed_doll_assets() -> None:
    from gfl2.layout import parse_rows
    from gfl2.dg_output import normalize_portrait
    seeded: set = set()
    for fixture, rows_labels in _SEED_LABELS.items():
        img = cv2.imread(str(_TESTS_DIR / fixture))
        if img is None:
            continue
        rows = parse_rows(img)
        for row, labels in zip(rows, rows_labels):
            for key, label in zip(_DOLL_KEYS, labels):
                if label is None or label in seeded:
                    continue
                final = _SEED_DIR / f"_{label}.png"
                if final.exists():
                    seeded.add(label)
                    continue
                crop = row.crop(key)
                if crop is None:
                    continue
                norm = normalize_portrait(crop)
                asset = norm if norm is not None else crop
                if cv2.imwrite(str(final), asset) and final.exists():
                    seeded.add(label)


_seed_doll_assets()

# Freeze the seed dir: prevent any parse() call during tests from overwriting seeded
# portraits or saving new unknown crops.  The daily-GS and weekly-GS test fixtures
# only assert return values; portrait I/O is a side-effect we don't want in tests.
import gfl2.dg_output as _dg
_dg._save_doll_portrait = lambda name, portrait: "skip"


# ── Stat-OCR fallback collector ───────────────────────────────────────────────

def pytest_addoption(parser):
    parser.addoption(
        "--no-save-failing-crops", action="store_true", default=False,
        help="Don't copy failing stat cell crops to tests/outputs/daily/",
    )


@pytest.fixture(scope="session")
def stat_fallback_collector(request):
    save_crops = not request.config.getoption("--no-save-failing-crops", default=False)
    collector = {"save_crops": save_crops, "items": []}
    yield collector
    _write_stat_fallbacks(collector, root)


# ── Generic Daily Gunsmoke stat-cell crop extraction (engine-agnostic) ───────
#
# Pure segmentation (panel split -> frame find -> frame-relative column
# crop) -- no OCR engine, no Tesseract call of any kind.  This is the
# "generic module" half of the stat_ocr abstraction: every engine-specific
# test file (v0_3_0, v0_1_1, ...) shares this ONE extractor for the raw crop
# pixels and supplies only its own classifier, so an engine-specific test
# can never accidentally paper over a real classify() miss with a Tesseract
# fallback the way each engine's own tess_only=False _collect_cells() would
# (that path calls _extract_stat_cell(), which defaults to
# tess_fallback=True and, for gfl2.stat_ocr_v0_1_1 specifically, the
# PRODUCTION engine singleton, not the one under test).

_DAILY_DIR = Path(__file__).parent / "inputs" / "daily"


def _extract_daily_stat_crops(image_paths: list[Path]) -> dict:
    """Slice every stat cell from `image_paths`, keyed by (filename, part).

    `part` matches stat_data.py's own part strings, e.g. "p1_r0_col2".
    Cells listed in stat_excluded_cells.json (source pixels known-corrupted,
    e.g. a mid-animation capture, docs/known_issues.txt §23) are dropped
    entirely, same as every engine's own v0_1_0 _collect_cells.
    """
    from gfl2.patterns.daily_gunsmoke import (
        _split_panels, _find_frames, _frame_col_cell,
        COL1_FR, COL2_FR, COL3_FR, COL4_FR,
    )
    from gfl2.stat_ocr_v0_1_0 import _load_excluded_cells

    excluded = _load_excluded_cells()
    cols_fr = [("col1", COL1_FR), ("col2", COL2_FR), ("col3", COL3_FR), ("col4", COL4_FR)]

    crops: dict = {}
    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        for pi, panel in enumerate(_split_panels(img)):
            frames = _find_frames(panel)
            if not frames:
                continue
            for ri, (fx, fy, fw, fh) in enumerate(frames):
                for cname, col_fr in cols_fr:
                    cell = _frame_col_cell(panel, fx, fy, fw, fh, col_fr)
                    if cell.size == 0:
                        continue
                    part = f"p{pi + 1}_r{ri}_{cname}"
                    if f"{img_path.stem}_{part}" in excluded:
                        continue
                    crops[(img_path.name, part)] = cell
    return crops


@pytest.fixture(scope="session")
def daily_stat_crops():
    """Session-scoped crop cache for tests/inputs/daily/*.png, keyed by
    (source filename, part) -- shared by every stat_ocr engine test file
    so classification is the only thing that differs between them.
    """
    image_paths = sorted(_DAILY_DIR.glob("*.png"))
    return _extract_daily_stat_crops(image_paths)


def _write_stat_fallbacks(collector: dict, project_root: Path) -> None:
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
        "note":  "Crops where blob pipeline diverges from GT (would fall back to Tesseract)",
        "crops": grouped,
    }
    (out_dir / "stat.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    if collector["save_crops"]:
        for item in items:
            cell = item.get("cell")
            if cell is not None:
                crop_name = f"{Path(item['source']).stem}_{item['part']}.png"
                cv2.imwrite(str(out_dir / crop_name), cell)
