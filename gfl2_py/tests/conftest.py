import sys
import py_compile
import shutil
import tempfile
from pathlib import Path
import cv2

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
                if cv2.imwrite(str(final), crop) and final.exists():
                    seeded.add(label)


_seed_doll_assets()
