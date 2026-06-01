# -*- coding: utf-8 -*-
"""
asset_mapper.py - Translates a cropped doll/buff frame to a named asset string.
"""
from __future__ import annotations
import sys
import uuid
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from gfl2.trace import timed

PHASH_THRESHOLD = 6
PHASH_DEDUP     = 20
HIST_THRESHOLD  = 0.88
PHASH_SIZE      = 8

ELEM_X1   = 0.25
ARROW_Y0  = 0.20
ARROW_Y1  = 0.58
BORROW_X0 = 0.48
BORROW_Y1 = 0.26
BADGE_Y0  = 0.75

_OPTIONAL_ICON_REGIONS = [
    (0.0,      ELEM_X1,  ARROW_Y0,  0.40),
    (0.0,      ELEM_X1,  0.40,      ARROW_Y1),
    (BORROW_X0, 1.0,     0.0,       BORROW_Y1),
]

ASSETS_DIR = Path(__file__).parent.parent / "assets"


def _phash(img_bgr: np.ndarray) -> int:
    gray    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (PHASH_SIZE*4, PHASH_SIZE*4), interpolation=cv2.INTER_AREA)
    dct     = cv2.dct(np.float32(resized))
    dct_low = dct[:PHASH_SIZE, :PHASH_SIZE]
    bits    = (dct_low >= np.median(dct_low)).flatten()
    h = 0
    for b in bits:
        h = (h << 1) | int(b)
    return h


def _hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def _make_mask(h: int, w: int) -> np.ndarray:
    mask = np.ones((h, w), dtype=np.uint8) * 255
    mask[int(h*ARROW_Y0):int(h*ARROW_Y1), :int(w*ELEM_X1)] = 0
    mask[:int(h*BORROW_Y1), int(w*BORROW_X0):]             = 0
    mask[int(h*BADGE_Y0):, :]                               = 0
    return mask


@timed()
def _hist_corr(frame: np.ndarray, asset: np.ndarray) -> float:
    ref  = cv2.resize(asset, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_AREA)
    h, w = frame.shape[:2]
    mask = _make_mask(h, w)
    def hist(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hst = cv2.calcHist([hsv], [0, 1], mask, [30, 32], [0, 180, 0, 256])
        cv2.normalize(hst, hst)
        return hst
    return float(cv2.compareHist(hist(frame), hist(ref), cv2.HISTCMP_CORREL))


def _icon_score(img: np.ndarray) -> int:
    h, w = img.shape[:2]
    sat  = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1].astype(float)
    count = 0
    for x0f, x1f, y0f, y1f in _OPTIONAL_ICON_REGIONS:
        region = sat[int(h*y0f):int(h*y1f), int(w*x0f):int(w*x1f)]
        if region.size > 0 and region.mean() > 90:
            count += 1
    return count


def _is_guid(name: str) -> bool:
    cleaned = name.replace("-", "")
    return len(cleaned) == 32 and all(c in "0123456789abcdefABCDEF" for c in cleaned)


class AssetMapper:
    def __init__(self, category: str) -> None:
        self.category  = category
        self._use_tm   = (category == "buff")
        self.asset_dir = ASSETS_DIR / category
        self.asset_dir.mkdir(parents=True, exist_ok=True)
        self._named:   list[tuple[str, np.ndarray, int]] = []
        self._unnamed: list[tuple[Path, int]] = []
        self._rebuild_index()

    @timed()
    def translate(self, frame: Optional[np.ndarray]) -> Optional[str]:
        if frame is None or frame.size == 0:
            return None
        self._rebuild_index()
        fh = _phash(frame)

        if self._named:
            best_name, best_dist = self._phash_best(fh)
            if best_dist <= PHASH_THRESHOLD:
                return best_name
            best_name, best_score = self._hist_best(frame)
            if best_score >= HIST_THRESHOLD:
                self._maybe_upgrade(best_name, frame)
                return best_name

        for _, gh in self._unnamed:
            if _hamming(fh, gh) <= PHASH_DEDUP:
                return None

        self._save_unknown(frame, fh)
        return None

    def reload(self) -> None:
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        named, unnamed = [], []
        for png in sorted(self.asset_dir.glob("*.png")):
            img = cv2.imread(str(png))
            if img is None:
                continue
            h = _phash(img)
            if _is_guid(png.stem):
                unnamed.append((png, h))
            else:
                named.append((png.stem, img, h))
        self._named   = named
        self._unnamed = unnamed

    def _phash_best(self, fh: int) -> tuple[str, int]:
        best_name, best_dist = "", 64
        for name, _, ah in self._named:
            d = _hamming(fh, ah)
            if d < best_dist:
                best_dist, best_name = d, name
        return best_name, best_dist

    def _hist_best(self, frame: np.ndarray) -> tuple[str, float]:
        best_name, best_score = "", 0.0
        for name, asset_img, _ in self._named:
            s = _hist_corr(frame, asset_img)
            if s > best_score:
                best_score, best_name = s, name
        return best_name, best_score

    def _maybe_upgrade(self, name: str, frame: np.ndarray) -> None:
        for i, (n, asset_img, _) in enumerate(self._named):
            if n != name:
                continue
            if _icon_score(frame) < _icon_score(asset_img):
                path = next(p for p in self.asset_dir.glob("*.png") if p.stem == name)
                cv2.imwrite(str(path), frame)
                new_img = cv2.imread(str(path))
                if new_img is not None:
                    self._named[i] = (name, new_img, _phash(new_img))
                    print(f"[asset_mapper] Upgraded reference: {name}", file=sys.stderr)
            break

    def _save_unknown(self, frame: np.ndarray, fh: int) -> Path:
        guid = str(uuid.uuid4())
        path = self.asset_dir / f"{guid}.png"
        cv2.imwrite(str(path), frame)
        self._unnamed.append((path, fh))
        print(f"[asset_mapper] Unknown {self.category} frame saved -> {path.name}", file=sys.stderr)
        return path
