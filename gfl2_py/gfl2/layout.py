"""
layout.py - GFL2 Weekly Gunsmoke row/cell extractor.
Columns use fixed proportions calibrated from 1485px reference screenshots.
"""
from __future__ import annotations
import re
from typing import Optional
import cv2
import numpy as np
import pytesseract

_DATE_RE = re.compile(r"\d{1,2}/\d{2}")
_DARK_THRESHOLD  = 70
_DATE_BAND_MIN_H = 40
_NAME_Y_PX       = 60

_COL = {
    "name":  (0.073, 0.323),
    "buff":  (0.350, 0.421),
    "doll1": (0.496, 0.556),
    "doll2": (0.565, 0.625),
    "doll3": (0.635, 0.694),
    "doll4": (0.704, 0.764),
    "doll5": (0.774, 0.834),
    "score": (0.889, 1.000),
}


class Row:
    def __init__(self, img: np.ndarray, date: Optional[str]) -> None:
        self.img  = img
        self.date = date
        self._h, self._w = img.shape[:2]

    def crop(self, col: str) -> Optional[np.ndarray]:
        x0r, x1r = _COL[col]
        x0, x1 = int(x0r * self._w), int(x1r * self._w)
        y1 = min(_NAME_Y_PX, self._h) if col == "name" else self._h
        cell = self.img[:y1, x0:x1]
        return cell if cell.size > 0 else None


def parse_rows(image: np.ndarray) -> list[Row]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    row_mean = gray.mean(axis=1)
    h = image.shape[0]
    is_dark = row_mean < _DARK_THRESHOLD

    bands = []
    in_band = False
    b_start = 0
    for y in range(h):
        if not in_band and is_dark[y]:
            in_band, b_start = True, y
        elif in_band and not is_dark[y]:
            bands.append((b_start, y))
            in_band = False
    if in_band:
        bands.append((b_start, h))

    events = []
    prev_end = 0
    current_date = None

    for b_start, b_end in bands:
        if b_start > prev_end:
            events.append(("content", prev_end, b_start))
        if b_end - b_start >= _DATE_BAND_MIN_H:
            d = _ocr_date(image[b_start:b_end, :])
            if d:
                current_date = d
        events.append(("sep", b_start, b_end, current_date))
        prev_end = b_end

    if prev_end < h:
        events.append(("content", prev_end, h))

    rows = []
    current_date = None
    for ev in events:
        if ev[0] == "sep":
            if ev[3]:
                current_date = ev[3]
        else:
            chunk = image[ev[1]:ev[2], :]
            if chunk.shape[0] >= 20:
                rows.extend(_split_chunk(chunk, current_date))
    return rows


def _split_chunk(chunk: np.ndarray, date: Optional[str]) -> list[Row]:
    gray = cv2.cvtColor(chunk, cv2.COLOR_BGR2GRAY)
    row_mean = gray.mean(axis=1)
    ch = chunk.shape[0]
    is_dark = row_mean < _DARK_THRESHOLD

    subs = []
    in_band = False
    b_start = 0
    for y in range(ch):
        if not in_band and is_dark[y]:
            in_band, b_start = True, y
        elif in_band and not is_dark[y]:
            subs.append((b_start, y))
            in_band = False
    if in_band:
        subs.append((b_start, ch))

    if not subs:
        return [Row(chunk, date)]

    rows = []
    prev = 0
    for s0, s1 in subs:
        if s0 > prev and s0 - prev >= 20:
            rows.append(Row(chunk[prev:s0, :], date))
        prev = s1
    if prev < ch and ch - prev >= 20:
        rows.append(Row(chunk[prev:, :], date))
    return rows if rows else [Row(chunk, date)]


def _ocr_date(band: np.ndarray) -> Optional[str]:
    region = band[:, :300]
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    mask = (gray > 100).astype(np.uint8) * 255
    up = cv2.resize(mask, (0, 0), fx=6, fy=6, interpolation=cv2.INTER_NEAREST)
    up = cv2.dilate(up, np.ones((3, 3), np.uint8), iterations=1)
    for psm in (11, 6):
        txt = pytesseract.image_to_string(up, config=f"--psm {psm} --oem 1").strip()
        m = _DATE_RE.search(txt)
        if m:
            return m.group()
    return None
