# -*- coding: utf-8 -*-
"""Daily Gunsmoke field identifier formatters.

See docs/reading_the_logs.txt §6 and docs/decisions.txt #101 for the
legacy-vs-v2 convention this module encodes, and docs/known_issues.txt §40
for why the legacy format is being phased out gradually rather than
migrated in place.

Two formatters, deliberately asymmetric:

    LegacyFieldId   READ-ONLY.  Parses the existing `p<N>_r<N>_col<N>`
                    format (panel/col 1-indexed, row 0-indexed, no pct/val
                    disambiguation) used throughout known_issues.txt/
                    decisions.txt citations and the daily stat-cell GT
                    files (stat_gt_overrides.json, stat_excluded_cells.json,
                    tess_gt_cache.py, stat_data.py). No code path should
                    ever construct a NEW legacy string — it exists only to
                    make sense of ones that already exist.

    FieldId         READ-WRITE.  Parses AND builds the new `p<N>_<field>`
                    format (all indices 1-indexed; a stat cell's pct/val
                    line is a mandatory suffix). This is what every new
                    reference should be written with — action_items.txt
                    #39 tracks migrating the stat-cell generators
                    (tests/conftest.py, tests/generate_stat_inputs.py,
                    gfl2/patterns/daily_gunsmoke.py's stat-cell fallback
                    logging) onto it; the header score/stats-row debug-crop
                    filenames in gfl2/patterns/daily_gunsmoke.py already
                    have (there was no legacy GT-file coupling to break for
                    those two fields, so nothing gated switching them now).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Union

_HDR_SUBFIELDS = ("dealt", "taken", "turns")
_LINES = ("pct", "val")


# ---------------------------------------------------------------------------
# Legacy format — READ-ONLY
# ---------------------------------------------------------------------------

_LEGACY_RE = re.compile(
    r"^(?P<source>.+)_p(?P<panel>\d+)_r(?P<row>\d+)_col(?P<col>\d+)$"
)


@dataclass(frozen=True)
class LegacyFieldId:
    """A parsed legacy `{source}_p<N>_r<N>_col<N>` stat-cell identifier.

    `panel`/`col` are 1-indexed, `row` is 0-indexed — exactly as the
    legacy format encodes them (known_issues.txt §40), not normalized.
    There is no `str()`/format method here on purpose: this class only
    ever reads an identifier that was already written elsewhere.
    """

    source: str
    panel: int  # 1-indexed
    row: int    # 0-indexed
    col: int    # 1-indexed

    @classmethod
    def parse(cls, s: str) -> "LegacyFieldId":
        m = _LEGACY_RE.match(s)
        if not m:
            raise ValueError(f"not a legacy field id: {s!r}")
        return cls(
            source=m.group("source"),
            panel=int(m.group("panel")),
            row=int(m.group("row")),
            col=int(m.group("col")),
        )

    def to_v2(self, line: str) -> "FieldId":
        """Convert to the equivalent v2 stat-cell id for one pct/val line.

        The legacy format never disambiguates pct vs. val (that ambiguity
        is exactly why v2 exists — decisions.txt #101), so the caller must
        supply which line this citation actually means.
        """
        if line not in _LINES:
            raise ValueError(f"line must be one of {_LINES}, got {line!r}")
        return FieldId(
            source=self.source,
            panel=self.panel,
            field=StatCellField(row=self.row + 1, col=self.col, line=line),
        )


# ---------------------------------------------------------------------------
# v2 format — READ-WRITE
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StatCellField:
    """The `r<N>_c<N>_{pct,val}` portion of a v2 stat-cell id. 1-indexed."""

    row: int
    col: int
    line: str

    def __post_init__(self):
        if self.line not in _LINES:
            raise ValueError(f"line must be one of {_LINES}, got {self.line!r}")
        if self.row < 1 or self.col < 1:
            raise ValueError(
                f"row/col must be 1-indexed (>=1), got row={self.row}, col={self.col}"
            )

    def __str__(self) -> str:
        return f"r{self.row}_c{self.col}_{self.line}"


_STAT_CELL_FIELD_RE = re.compile(r"^r(?P<row>\d+)_c(?P<col>\d+)_(?P<line>pct|val)$")
_V2_RE = re.compile(
    r"^(?P<source>.+)_p(?P<panel>\d+)_"
    r"(?P<field>score|hdr_dealt|hdr_taken|hdr_turns|r\d+_c\d+_(?:pct|val))$"
)


@dataclass(frozen=True)
class FieldId:
    """A `{source}_p<N>_<field>` v2 identifier (docs/reading_the_logs.txt §6).

    `field` is either the literal `"score"`, one of `"hdr_dealt"`/
    `"hdr_taken"`/`"hdr_turns"`, or a `StatCellField`. Use the `score()`/
    `header()`/`stat_cell()` classmethods rather than constructing `field`
    by hand.
    """

    source: str
    panel: int  # 1-indexed
    field: Union[str, StatCellField]

    def __post_init__(self):
        if self.panel < 1:
            raise ValueError(f"panel must be 1-indexed (>=1), got {self.panel}")
        if isinstance(self.field, str) and self.field not in (
            "score",
            *(f"hdr_{sub}" for sub in _HDR_SUBFIELDS),
        ):
            raise ValueError(f"unrecognized field: {self.field!r}")

    def __str__(self) -> str:
        field_s = str(self.field)
        return f"{self.source}_p{self.panel}_{field_s}"

    @classmethod
    def parse(cls, s: str) -> "FieldId":
        m = _V2_RE.match(s)
        if not m:
            raise ValueError(f"not a v2 field id: {s!r}")
        field_s = m.group("field")
        cell_m = _STAT_CELL_FIELD_RE.match(field_s)
        field: Union[str, StatCellField]
        if cell_m:
            field = StatCellField(
                row=int(cell_m.group("row")),
                col=int(cell_m.group("col")),
                line=cell_m.group("line"),
            )
        else:
            field = field_s
        return cls(source=m.group("source"), panel=int(m.group("panel")), field=field)

    @classmethod
    def score(cls, source: str, panel: int) -> "FieldId":
        return cls(source=source, panel=panel, field="score")

    @classmethod
    def header(cls, source: str, panel: int, subfield: str) -> "FieldId":
        if subfield not in _HDR_SUBFIELDS:
            raise ValueError(f"subfield must be one of {_HDR_SUBFIELDS}, got {subfield!r}")
        return cls(source=source, panel=panel, field=f"hdr_{subfield}")

    @classmethod
    def stat_cell(cls, source: str, panel: int, row: int, col: int, line: str) -> "FieldId":
        return cls(source=source, panel=panel, field=StatCellField(row=row, col=col, line=line))
