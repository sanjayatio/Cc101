# -*- coding: utf-8 -*-
"""
gfl2/report.py -- Daily Gunsmoke production-run report generator.

Writes tests/outputs/daily/reports/report_<commit>_<dirty>.py after every
`main.py --pattern daily_gunsmoke` run (single image or folder batch) --
same commit+dirty-lines naming convention as debugs/persist_run_result.py's
save_run_result(), so a report generated against an uncommitted, in-progress
tree is never confused with one generated from a clean commit. This project
should generally be run clean before generating a report; dirty_lines > 0 in
the report's own META flags the ones that weren't.

Sections mirror the daily_gunsmoke pipeline: score (header score field),
header (dealt/taken/turns), pct and val (the two lines of every stat cell).
pct and val share the underlying stat_cell/blob + stat_cell/psm6/psm4 spans
(one engine.read() / Tesseract call classifies both lines together) -- their
pipeline rows for those three stage names are therefore identical between
the two sections by construction, not a bug (see docs/decisions.txt #57 for
the same pct-vs-whole-engine timing distinction in a different tool).

Not a CLI -- import generate_report() from main.py.
"""
from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from gfl2.timing import Span

_ROOT       = Path(__file__).resolve().parent.parent
_REPORT_DIR = _ROOT / "tests" / "outputs" / "daily" / "reports"

SECTION_NAMES = ("score", "header", "pct", "val")

# Which timer span names feed each section's pipeline breakdown. stat_cell/*
# is shared by pct and val (one blob read() / tesseract call classifies both
# lines at once) -- it appears, identically, under both sections.
_SECTION_SPAN_NAMES = {
    "score":  ("score/blob", "score/tess"),
    "header": ("stats_row/blob", "stats_row/tess"),
    "pct":    ("stat_cell/blob", "stat_cell/psm6", "stat_cell/psm4",
               "pct/binarize", "pct/blobs", "pct/extract", "pct/classify"),
    "val":    ("stat_cell/blob", "stat_cell/psm6", "stat_cell/psm4",
               "val/binarize", "val/blobs", "val/extract", "val/classify"),
}

_EMPTY_SUMMARY = {"processed": 0, "ok": 0, "failed": 0, "unknown_glyphs": 0}


def _git(args: list[str]) -> str:
    return subprocess.run(
        ["git"] + args, cwd=_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def commit_dirty_tag() -> tuple[str, int]:
    """(short_commit, dirty_line_count) -- same derivation as
    debugs/persist_run_result.py's commit_dirty_tag(), duplicated here rather
    than imported: gfl2/ modules import FROM debugs/, never the reverse
    (known_issues.txt §31). Falls back to ("nogit", 0) if git is unavailable
    or this isn't a git checkout -- a report shouldn't fail a production run
    over that."""
    try:
        commit = _git(["rev-parse", "--short", "HEAD"])
        numstat = _git(["diff", "--numstat", "HEAD", "--", "."])
    except Exception:
        return "nogit", 0
    dirty = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            dirty += int(parts[0]) + int(parts[1])
    return commit, dirty


def _flatten_spans(roots: list[Span]) -> dict[str, tuple[float, int]]:
    """Flatten every Span at every depth across all roots into
    {name: (total_ms, count)}, merging same-named spans regardless of
    nesting depth or which root they came from."""
    acc: dict[str, tuple[float, int]] = {}

    def walk(span: Span) -> None:
        total, count = acc.get(span.name, (0.0, 0))
        acc[span.name] = (total + span.ms, count + 1)
        for child in span.children:
            walk(child)

    for root in roots:
        walk(root)
    return acc


def _pipeline_rows(flat: dict[str, tuple[float, int]],
                    names: tuple[str, ...]) -> list[dict]:
    rows = []
    for name in names:
        total_ms, count = flat.get(name, (0.0, 0))
        if count == 0:
            continue
        rows.append({
            "stage":   name,
            "total_s": round(total_ms / 1000, 4),
            "hits":    count,
            "avg_ms":  round(total_ms / count, 3),
        })
    return rows


def generate_report(
    *,
    image_names: list[str],
    roots: list[Span],
    section_stats: dict,
    wall_clock_s: float,
    started_at: datetime,
    stat_ocr_engine: str,
) -> Path:
    """Write a report_<commit>_<dirty>.py module to
    tests/outputs/daily/reports/ and return its path.

    image_names / roots: one entry each per processed image (roots[i] is
      that image's TimerStack.root) -- same pairing convention as
      gfl2.timing.batch_summary/pipeline_summary.
    section_stats: {"score": {...}, "header": {...}, "pct": {...},
      "val": {...}}, as returned by
      gfl2.patterns.daily_gunsmoke.flush_section_stats() -- each value is
      {"processed", "ok", "failed", "unknown_glyphs"}.
    wall_clock_s: total wall-clock elapsed for the whole run (all images),
      measured by the caller (time.perf_counter() delta) -- independent of
      the sum of per-image Span times, which excludes I/O/setup between
      images.
    started_at: a tz-aware datetime captured at the moment the run began
      (before the first image was processed) -- the "start of execution
      time" header field, not when the report itself is written.
    """
    commit, dirty = commit_dirty_tag()
    flat = _flatten_spans(roots)

    sections = {}
    for name in SECTION_NAMES:
        summary = section_stats.get(name, _EMPTY_SUMMARY)
        sections[name] = {
            "summary":  dict(summary),
            "pipeline": _pipeline_rows(flat, _SECTION_SPAN_NAMES[name]),
        }

    meta = {
        "generated_at":     started_at.isoformat(),
        "commit":           commit,
        "dirty_lines":      dirty,
        "stat_ocr_engine":  stat_ocr_engine,
        "wall_clock_s":     round(wall_clock_s, 3),
        "images_processed": len(image_names),
        "image_names":      list(image_names),
    }

    _REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _REPORT_DIR / f"report_{commit}_{dirty}.py"
    out_path.write_text(_render(meta, sections), encoding="utf-8")
    return out_path


def _pyrepr(obj, indent: int = 0) -> str:
    """Deterministic, readable repr as valid Python source (stable key
    order, 2-space indent) -- same convention as
    tests/generate_stat_inputs.py's own _pyrepr()."""
    pad    = "  " * indent
    pad_in = "  " * (indent + 1)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = [f"{pad_in}{k!r}: {_pyrepr(v, indent + 1)}," for k, v in obj.items()]
        return "{\n" + "\n".join(items) + f"\n{pad}}}"
    if isinstance(obj, (list, tuple, set)):
        seq = list(obj)
        if not seq:
            return "[]"
        items = [f"{pad_in}{_pyrepr(v, indent + 1)}," for v in seq]
        return "[\n" + "\n".join(items) + f"\n{pad}]"
    return repr(obj)


def _render(meta: dict, sections: dict) -> str:
    dirty_warn = ""
    if meta["dirty_lines"]:
        dirty_warn = (
            f"\nWARNING: generated from a DIRTY working tree "
            f"({meta['dirty_lines']} changed lines vs HEAD) -- this report's "
            f"numbers may not reflect any single committed state.\n"
        )
    header = (
        '# -*- coding: utf-8 -*-\n'
        '"""\n'
        f"tests/outputs/daily/reports/report_{meta['commit']}_{meta['dirty_lines']}.py "
        "-- auto-generated by `main.py --pattern daily_gunsmoke` (gfl2/report.py).\n"
        "Do not hand-edit -- regenerate by re-running the same production command.\n"
        "\n"
        f"Generated: {meta['generated_at']}  (run start)\n"
        f"Commit:    {meta['commit']}  (dirty={meta['dirty_lines']} lines changed vs HEAD)\n"
        f"{dirty_warn}"
        '"""\n'
        "from __future__ import annotations\n"
        "\n"
    )
    body = (
        f"META = {_pyrepr(meta)}\n"
        "\n"
        f"SECTIONS = {_pyrepr(sections)}\n"
    )
    return header + body
