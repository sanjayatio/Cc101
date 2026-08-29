import shutil as _shutil
import os as _os

_WIN_TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if not _shutil.which("tesseract") and _os.path.isfile(_WIN_TESS):
    try:
        import pytesseract as _pt
        _pt.pytesseract.tesseract_cmd = _WIN_TESS
    except ImportError:
        pass
