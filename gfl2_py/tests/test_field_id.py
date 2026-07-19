# -*- coding: utf-8 -*-
"""
tests/test_field_id.py
-----------------------
Regression coverage for gfl2/field_id.py's two formatters (docs/decisions.txt
#101, docs/reading_the_logs.txt §6): LegacyFieldId (read-only parsing of the
existing `p<N>_r<N>_col<N>` convention) and FieldId (read-write parsing/
building of the new `p<N>_<field>` convention).
"""
from __future__ import annotations

import pytest

from gfl2.field_id import FieldId, LegacyFieldId, StatCellField


# ---------------------------------------------------------------------------
# LegacyFieldId — read-only
# ---------------------------------------------------------------------------

def test_legacy_parse_extracts_raw_indices_unchanged():
    # The doc example from known_issues.txt §40 / reading_the_logs.txt §6.
    parsed = LegacyFieldId.parse("fb_d_20251003_p2_r0_col2")
    assert parsed.source == "fb_d_20251003"
    assert parsed.panel == 2  # 1-indexed, as encoded
    assert parsed.row == 0    # 0-indexed, as encoded -- NOT normalized
    assert parsed.col == 2    # 1-indexed, as encoded


def test_legacy_parse_source_may_contain_underscores():
    parsed = LegacyFieldId.parse("gm_d_20250929_p1_r3_col4")
    assert parsed.source == "gm_d_20250929"
    assert (parsed.panel, parsed.row, parsed.col) == (1, 3, 4)


@pytest.mark.parametrize("bad", [
    "fb_d_20251003_p2_r0_c2",       # v2 spelling ('c' not 'col')
    "fb_d_20251003_p2_row0_col2",   # wrong row token
    "fb_d_20251003_r0_col2",        # missing panel
    "not_a_field_id",
    "",
])
def test_legacy_parse_rejects_non_legacy_strings(bad):
    with pytest.raises(ValueError):
        LegacyFieldId.parse(bad)


def test_legacy_field_id_has_no_write_capability():
    """LegacyFieldId is read-only: it must not offer any way to reproduce
    a legacy-format string, so nothing can accidentally generate a NEW
    legacy citation via this class (decisions.txt #101)."""
    parsed = LegacyFieldId.parse("fb_d_20251003_p2_r0_col2")
    assert not hasattr(parsed, "format")
    assert not hasattr(type(parsed), "__str__") or str(parsed) != "fb_d_20251003_p2_r0_col2"


def test_legacy_to_v2_shifts_row_to_1_indexed_and_requires_line():
    parsed = LegacyFieldId.parse("fb_d_20251003_p2_r0_col2")
    v2 = parsed.to_v2("val")
    assert str(v2) == "fb_d_20251003_p2_r1_c2_val"
    assert isinstance(v2.field, StatCellField)
    assert v2.field.row == 1  # r0 (legacy) -> r1 (v2), same physical row
    assert v2.field.col == 2  # col was already 1-indexed, unchanged

    v2_pct = parsed.to_v2("pct")
    assert str(v2_pct) == "fb_d_20251003_p2_r1_c2_pct"


def test_legacy_to_v2_rejects_invalid_line():
    parsed = LegacyFieldId.parse("fb_d_20251003_p2_r0_col2")
    with pytest.raises(ValueError):
        parsed.to_v2("pct_and_val")


# ---------------------------------------------------------------------------
# FieldId — read-write
# ---------------------------------------------------------------------------

def test_score_round_trip():
    fid = FieldId.score("fb_d_20251019", 2)
    assert str(fid) == "fb_d_20251019_p2_score"
    assert FieldId.parse(str(fid)) == fid


@pytest.mark.parametrize("subfield", ["dealt", "taken", "turns"])
def test_header_round_trip(subfield):
    fid = FieldId.header("fb_d_20251019", 1, subfield)
    expected = f"fb_d_20251019_p1_hdr_{subfield}"
    assert str(fid) == expected
    assert FieldId.parse(expected) == fid


def test_header_rejects_unknown_subfield():
    with pytest.raises(ValueError):
        FieldId.header("fb_d_20251019", 1, "score")  # not a stats-row subfield


def test_stat_cell_round_trip_matches_doc_example():
    # Same physical cell as the LegacyFieldId doc example above.
    fid = FieldId.stat_cell("fb_d_20251003", 2, row=1, col=2, line="val")
    assert str(fid) == "fb_d_20251003_p2_r1_c2_val"
    assert FieldId.parse(str(fid)) == fid


def test_stat_cell_pct_and_val_are_distinct_ids():
    pct = FieldId.stat_cell("gm_d_20250929", 1, row=3, col=4, line="pct")
    val = FieldId.stat_cell("gm_d_20250929", 1, row=3, col=4, line="val")
    assert str(pct) != str(val)
    assert str(pct) == "gm_d_20250929_p1_r3_c4_pct"
    assert str(val) == "gm_d_20250929_p1_r3_c4_val"


def test_stat_cell_rejects_invalid_line():
    with pytest.raises(ValueError):
        FieldId.stat_cell("gm_d_20250929", 1, row=1, col=1, line="score")


@pytest.mark.parametrize("panel,row,col", [(0, 1, 1), (1, 0, 1), (1, 1, 0)])
def test_stat_cell_rejects_0_indexed_values(panel, row, col):
    with pytest.raises(ValueError):
        FieldId.stat_cell("gm_d_20250929", panel, row=row, col=col, line="pct")


def test_v2_parse_rejects_legacy_strings():
    # 'col' spelling belongs to the legacy format only.
    with pytest.raises(ValueError):
        FieldId.parse("fb_d_20251003_p2_r0_col2")


@pytest.mark.parametrize("bad", [
    "fb_d_20251003_p2_unknownfield",
    "fb_d_20251003_score",  # missing panel
    "",
])
def test_v2_parse_rejects_malformed_strings(bad):
    with pytest.raises(ValueError):
        FieldId.parse(bad)


def test_col_vs_c_prefixes_never_collide():
    """Legacy 'col2' and v2 'c2' are spelled differently on purpose so a
    v2 id can never be mistaken for a legacy one (decisions.txt #101)."""
    legacy = LegacyFieldId.parse("fb_d_20251003_p2_r0_col2")
    v2 = FieldId.stat_cell("fb_d_20251003", legacy.panel, row=legacy.row + 1,
                            col=legacy.col, line="pct")
    assert "col" not in str(v2)
    with pytest.raises(ValueError):
        LegacyFieldId.parse(str(v2))
