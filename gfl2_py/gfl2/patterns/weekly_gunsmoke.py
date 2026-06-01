"""
weekly_gunsmoke.py - Weekly Gunsmoke report parser.
Output: date, ownerName, buffName, doll1-5, score
"""
from __future__ import annotations
import re
from dataclasses import dataclass, fields
from typing import Optional
import cv2
import numpy as np
import pytesseract
from gfl2.asset_mapper import AssetMapper
from gfl2.layout import Row, parse_rows

_buff_mapper = AssetMapper("buff")
_doll_mapper = AssetMapper("dolls")
_ALNUM_RE  = re.compile(r"[^A-Za-z0-9_\-\. ]")
_DIGITS_RE = re.compile(r"\d+")


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


def parse(image: np.ndarray) -> list[GunsmokRecord]:
    return [_parse_row(r) for r in parse_rows(image)]


def _parse_row(row: Row) -> GunsmokRecord:
    return GunsmokRecord(
        date=row.date,
        ownerName=_ocr_name(row),
        buffName=_buff_mapper.translate(row.crop("buff")),
        doll1=_doll_mapper.translate(row.crop("doll1")),
        doll2=_doll_mapper.translate(row.crop("doll2")),
        doll3=_doll_mapper.translate(row.crop("doll3")),
        doll4=_doll_mapper.translate(row.crop("doll4")),
        doll5=_doll_mapper.translate(row.crop("doll5")),
        score=_ocr_score(row),
    )


def _ocr_name(row: Row) -> Optional[str]:
    cell = row.crop("name")
    if cell is None:
        return None
    up = cv2.resize(cell, (0, 0), fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config="--psm 7").strip()
    clean = _ALNUM_RE.sub("", text).strip()
    return clean or None


def _ocr_score(row: Row) -> Optional[str]:
    cell = row.crop("score")
    if cell is None:
        return None
    up = cv2.resize(cell, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    text = pytesseract.image_to_string(up, config="--psm 6").strip()
    nums = _DIGITS_RE.findall(text)
    return nums[-1] if nums else None
