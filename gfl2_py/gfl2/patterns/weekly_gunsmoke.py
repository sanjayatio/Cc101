# -*- coding: utf-8 -*-
"""
weekly_gunsmoke.py - Weekly Gunsmoke report parser.
Output: date, ownerName, buffName, doll1-5, score
"""
from __future__ import annotations
import re
from dataclasses import dataclass, fields
from typing import Callable, Optional
import cv2
import numpy as np
import pytesseract
from gfl2 import buff_ocr
from gfl2.asset_mapper import AssetMapper
from gfl2.dg_output import normalize_portrait
from gfl2.layout import Row, parse_rows
from gfl2.trace import timed

_doll_mapper = AssetMapper("dolls")
_ALNUM_RE  = re.compile(r"[^A-Za-z0-9_\-\. ]")
_DIGITS_RE = re.compile(r"\d+")

_SCORE_TMPL = None   # lazy-loaded score digit templates; False when unavailable


def _get_score_templates():
    global _SCORE_TMPL
    if _SCORE_TMPL is None:
        try:
            from gfl2.score_ocr import TEMPLATES_F
            import json
            _SCORE_TMPL = json.loads(TEMPLATES_F.read_text())
        except Exception:
            _SCORE_TMPL = False
    return _SCORE_TMPL if _SCORE_TMPL is not False else None


@dataclass
class GunsmokRecord:
    date:      Optional[str]
    ownerName: Optional[str]
    buffName:  Optional[str]
    doll1:     Optional[str]
    doll2:     Optional[str]
    doll3:     Optional[str]
    doll4:     Optional[str]
    doll5:     Optional[str]
    score:     Optional[str]

    def to_csv_row(self) -> str:
        def fmt(v):
            return v.lstrip("_") if v else ""
        return ",".join(fmt(getattr(self, f.name)) for f in fields(self))

    @staticmethod
    def csv_header() -> str:
        return "date,ownerName,buffName,doll1,doll2,doll3,doll4,doll5,score"


# ScoreFn signature: (Row) -> Optional[str]
ScoreFn = Callable[[Row], Optional[str]]


def parse(
    image:       np.ndarray,
    score_fn:    ScoreFn | None = None,
    source_name: str = "unknown",
) -> list[GunsmokRecord]:
    """
    Parse a Weekly Gunsmoke screenshot.

    score_fn:    callable (Row) -> str | None that overrides the default score
                 extractor.  When None, _ocr_score is used — which tries the
                 blob pipeline first (identical to daily_gunsmoke) and falls
                 back to Tesseract only if templates are unavailable or the
                 blob pipeline returns None.
    source_name: stem of the source image file (e.g. 'gm_250801').  Used to
                 build the save filename for unmatched doll crops:
                 {source_name}-row{N:02d}-doll{D}.png
    """
    fn   = score_fn or _ocr_score
    rows = parse_rows(image)

    # Batch ALL Tesseract work (score + name) before any buff_ocr calls.
    # buff_ocr._save_asset() writes to disk and degrades Tesseract state
    # for subsequent rows on Windows — batching decouples them entirely.
    scores = [fn(r) for r in rows]
    owners = [_ocr_name(r) for r in rows]

    return [
        _parse_row(r, s, o, source_name, idx)
        for idx, (r, s, o) in enumerate(zip(rows, scores, owners), start=1)
    ]


@timed()
def _parse_row(row: Row, score: Optional[str], owner: Optional[str],
               source_name: str, row_idx: int) -> GunsmokRecord:
    def _save_name(doll_idx: int) -> str:
        return f"{source_name}-row{row_idx:02d}-doll{doll_idx}"

    return GunsmokRecord(
        date=row.date,
        ownerName=owner,
        buffName=buff_ocr.translate(row.crop("buff")),
        doll1=_doll_mapper.translate(normalize_portrait(row.crop("doll1")), save_name=_save_name(1)),
        doll2=_doll_mapper.translate(normalize_portrait(row.crop("doll2")), save_name=_save_name(2)),
        doll3=_doll_mapper.translate(normalize_portrait(row.crop("doll3")), save_name=_save_name(3)),
        doll4=_doll_mapper.translate(normalize_portrait(row.crop("doll4")), save_name=_save_name(4)),
        doll5=_doll_mapper.translate(normalize_portrait(row.crop("doll5")), save_name=_save_name(5)),
        score=score,
    )


@timed()
def _ocr_name(row: Row) -> Optional[str]:
    cell = row.crop("name")
    if cell is None:
        return None
    up = cv2.resize(cell, (0, 0), fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config="--psm 7").strip()
    clean = _ALNUM_RE.sub("", text).strip()
    return clean or None


@timed()
def _ocr_score(row: Row) -> Optional[str]:
    """Score extractor: blob pipeline (primary) → Tesseract fallback."""
    cell = row.crop("score")
    if cell is None:
        return None

    # Blob pipeline (primary — Tesseract-free, mirrors daily_gunsmoke pattern)
    tmpl = _get_score_templates()
    if tmpl is not None:
        from gfl2.score_ocr import detect_blob
        result = detect_blob(cell, tmpl)
        if result is not None:
            return result

    # Tesseract fallback
    up = cv2.resize(cell, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Method 1: image_to_string — last digit group discards the coin icon bleed.
    text = pytesseract.image_to_string(up, config="--psm 6").strip()
    nums = _DIGITS_RE.findall(text)
    if nums:
        return nums[-1]

    # Method 2: image_to_data fallback — skip left-edge tokens.
    data = pytesseract.image_to_data(
        up,
        config="--psm 6 -c tessedit_char_whitelist=0123456789",
        output_type=pytesseract.Output.DICT,
    )
    candidates = [
        (data["left"][i], data["text"][i])
        for i in range(len(data["text"]))
        if re.fullmatch(r"\d{3,6}", data["text"][i])
        and int(data["conf"][i]) > 20
        and data["left"][i] > 0
    ]
    return max(candidates, key=lambda t: t[0])[1] if candidates else None