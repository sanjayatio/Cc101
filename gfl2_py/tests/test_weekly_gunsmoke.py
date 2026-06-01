"""
tests/test_weekly_gunsmoke.py
-----------------------------
Regression tests for the Weekly Gunsmoke parser.

Asserts date, buffName, doll1-5, and score for every row in the two
reference images processed during development.

Run with:
    cd gfl2_py
    pytest tests/
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import pytest

from gfl2.patterns.weekly_gunsmoke import parse, GunsmokRecord

TESTS_DIR = Path(__file__).parent


# ── helpers ───────────────────────────────────────────────────────────────────

def load_and_parse(filename: str) -> list[GunsmokRecord]:
    path = TESTS_DIR / filename
    img  = cv2.imread(str(path))
    assert img is not None, f"Could not read {path}"
    return parse(img)


@dataclass
class Expected:
    date:     Optional[str]
    buff:     str
    doll1:    str
    doll2:    str
    doll3:    str
    doll4:    str
    doll5:    Optional[str]   # None = unknown/blank is acceptable
    score:    str


def assert_row(record: GunsmokRecord, exp: Expected, label: str) -> None:
    def strip(v): return v.lstrip("_") if v else v

    if exp.date is not None:
        assert record.date == exp.date,  f"{label}: date {record.date!r} != {exp.date!r}"
    assert strip(record.buffName) == exp.buff,  f"{label}: buff {record.buffName!r} != {exp.buff!r}"
    assert strip(record.doll1)    == exp.doll1, f"{label}: doll1 {record.doll1!r} != {exp.doll1!r}"
    assert strip(record.doll2)    == exp.doll2, f"{label}: doll2 {record.doll2!r} != {exp.doll2!r}"
    assert strip(record.doll3)    == exp.doll3, f"{label}: doll3 {record.doll3!r} != {exp.doll3!r}"
    assert strip(record.doll4)    == exp.doll4, f"{label}: doll4 {record.doll4!r} != {exp.doll4!r}"
    if exp.doll5 is not None:
        assert strip(record.doll5) == exp.doll5, f"{label}: doll5 {record.doll5!r} != {exp.doll5!r}"
    assert record.score == exp.score, f"{label}: score {record.score!r} != {exp.score!r}"


# ── gm_250801 ─────────────────────────────────────────────────────────────────

GM_250801_EXPECTED = [
    Expected("08/02", "Lethal Firepower",    "Cheeta",     "Makiatto",   "Tololo",     "Colphne",    "QiongJiu",   "3142"),
    Expected("08/02", "Chained Spark",       "Springfield","Sharkry",    "QiongJiu",   "Centaraussi","Tololo",     "4068"),
    Expected("08/01", "Burn Overdrive",      "Springfield","Sharkry",    "QiongJiu",   "Centaraussi","Tololo",     "3939"),
    Expected("08/01", "Light Penetration",   "Cheeta",     "Makiatto",   "Colphne",    "Tololo",     "QiongJiu",   "3094"),
    Expected("07/31", "Burn Overdrive",      "Springfield","Sharkry",    "Centaraussi","QiongJiu",   "Tololo",     "3860"),
    Expected("07/31", "Support Enhancement", "Cheeta",     "Colphne",    "Tololo",     "Makiatto",   "QiongJiu",   "3013"),
    Expected("07/31", "Chained Spark",       "QiongJiu",   "Springfield","Centaraussi","Sharkry",    "Tololo",     "4073"),
    Expected("07/31", "Lethal Firepower",    "Cheeta",     "Makiatto",   "Tololo",     "Colphne",    "QiongJiu",   "3094"),  # noqa: E501
]


class TestGm250801:
    @pytest.fixture(scope="class")
    def records(self):
        return load_and_parse("gm_250801.png")

    def test_row_count(self, records):
        assert len(records) == 8

    @pytest.mark.parametrize("i,exp", list(enumerate(GM_250801_EXPECTED)))
    def test_row(self, records, i, exp):
        assert_row(records[i], exp, f"gm_250801 row {i}")


# ── gm_250730 ─────────────────────────────────────────────────────────────────

GM_250730_EXPECTED = [
    # date is blank in this image (no date separator band detected)
    Expected(None, "Chained Spark",    "QiongJiu", "Springfield", "Centaraussi", "Sharkry",    "Tololo",   "4073"),
    Expected(None, "Lethal Firepower", "Cheeta",   "Makiatto",    "Tololo",      "Colphne",    "QiongJiu", "3080"),
    Expected(None, "Light Penetration","Colphne",  "Springfield", "Makiatto",    "Tololo",     "QiongJiu", "3089"),
    Expected(None, "Burn Overdrive",   "QiongJiu", "Cheeta",      "Vector",      "Centaraussi","Sharkry",  "3206"),
]


class TestGm250730:
    @pytest.fixture(scope="class")
    def records(self):
        return load_and_parse("gm_250730.png")

    def test_row_count(self, records):
        assert len(records) == 4

    @pytest.mark.parametrize("i,exp", list(enumerate(GM_250730_EXPECTED)))
    def test_row(self, records, i, exp):
        assert_row(records[i], exp, f"gm_250730 row {i}")

    def test_row3_doll3_vector(self, records):
        """Vector doll3 — confirms the asset is mapped."""
        val = records[3].doll3
        assert val is not None and val.lstrip("_") == "Vector", (
            f"Expected doll3='Vector' but got {val!r}"
        )
