import sys
import py_compile
import shutil
from pathlib import Path

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
