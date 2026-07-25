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
pct and val share the underlying stat_cell/blob span (one engine.read() call
classifies both lines together). decisions.txt #57 established that this
one span's SUMMARY (hits/total_s/avg_ms) is necessarily the same combined
number regardless of which section asks about it -- true, but showing that
raw combined number as EACH section's own "stat_cell/blob" row (this
module's original behavior) meant both sections displayed an IDENTICAL
total that was actually neither section's own share, inviting exactly the
kind of double-count a reader summing "pct's total" + "val's total" could
make. Whenever a v0_3_0-family engine's own pct/val-prefixed children exist
to attribute it with (gfl2.timing.attribute_shared_span), each section's
"stat_cell/blob" row instead shows THAT section's own attributable slice of
the shared call -- the two sections' rows now genuinely differ, reflecting
the real cost split, only falling back to the old shared-combined-number
behavior for engines with no such children to attribute from (v0_1_0/
v0_1_1/v0_2_0, where the call truly cannot be split and showing the same
number under both sections is the only available information, not an
artifact). See known_issues.txt §41's UPDATE / decisions.txt #104's
follow-up for the full before/after.

PIPELINE SHAPE (known_issues.txt §41, decisions.txt #104): each section's
"pipeline" is a NESTED tree, not a flat list -- one dict per top-level span
name, each optionally carrying a "children" list of the same shape, all the
way down to a v0_3_0-family engine's own classify()-leaf breakdown (e.g.
stat_cell/blob -> pct/classify -> branch -> circular_069 -> ...). This
mirrors gfl2.timing.pipeline_summary()'s own console tree exactly for every
node's CHILDREN -- both are built from the SAME gfl2.timing.build_agg_tree
(roots) aggregation (the "stat_cell/blob" row's own SUMMARY is the one
deliberate exception, per the attribution paragraph above: the console
tree shows this span only once, un-split, so it never needed this
attribution step at all -- only a per-SECTION view like this module's does).
Earlier versions of this module flattened every span into one global
{name: (total_ms, count)} dict (_flatten_spans, since removed) and
deliberately excluded branch/leaf names from the section span-name list to
avoid a real collision risk: a v0_3_0-family engine's pct-tree and val-tree
reuse the SAME leaf names (e.g. "circular_069") for two structurally
different populations, and flattening by name alone would have silently
summed them together. Preserving the actual Span hierarchy instead of
flattening it removes that risk entirely -- pct's "branch" node and val's
"branch" node are different nodes (different parents), never merged.

Not a CLI -- import generate_report() from main.py.
"""
from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from gfl2.timing import Span, attribute_shared_span, build_agg_tree, find_named_node

_ROOT       = Path(__file__).resolve().parent.parent
_REPORT_DIR = _ROOT / "tests" / "outputs" / "daily" / "reports"

SECTION_NAMES = ("score", "header", "pct", "val")

# Which top-level timer span name(s) root each section's pipeline tree.
# stat_cell/* is shared by pct and val (one blob read() call classifies
# both lines at once) -- both sections start from the SAME "stat_cell/blob"
# node, but see _STAT_CELL_CHILD_PREFIX below for how their CHILDREN are
# kept separate.
_SECTION_ROOT_NAMES = {
    "score":  ("score/blob", "score/tess"),
    "header": ("stats_row/blob", "stats_row/tess"),
    "pct":    ("stat_cell/blob", "stat_cell/psm6", "stat_cell/psm4"),
    "val":    ("stat_cell/blob", "stat_cell/psm6", "stat_cell/psm4"),
}

# "stat_cell/blob"'s own children are only ever this section's own line
# (e.g. "pct/binarize", "pct/classify", ...) once filtered by this prefix --
# applied ONLY to "stat_cell/blob" itself (see _pipeline_tree), never to a
# node's own nested descendants, which already live exclusively under the
# correctly-prefixed parent and need no further filtering. Also used to
# ATTRIBUTE "stat_cell/blob"'s own row (not just its children) to this
# section's own share -- see _attributed_row / gfl2.timing.
# attribute_shared_span.
_STAT_CELL_CHILD_PREFIX = {"pct": "pct/", "val": "val/"}

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


def _node_to_dict(node, child_filter=None) -> dict:
    """Recursively convert one aggregated node (gfl2.timing.build_agg_tree's
    _AggNode) into a JSON/pyrepr-friendly nested dict -- {"stage", "hits",
    "total_s", "avg_ms", "stdev_ms", "cv"}, plus a "children" list (same
    shape, recursively) when any children survive `child_filter`. Children
    are sorted by total time descending, same order gfl2.timing.
    pipeline_summary()'s console tree uses, so the biggest bottleneck at
    each level is always listed first.

    child_filter: optional predicate(child_name) -> bool, applied ONLY at
      this call's own level (never propagated to grandchildren) -- used
      once, for "stat_cell/blob" itself, to split its shared pct/val
      children apart (see _STAT_CELL_CHILD_PREFIX)."""
    children = list(node.children.values())
    if child_filter is not None:
        children = [c for c in children if child_filter(c.name)]
    children = sorted(children, key=lambda n: n.total_ms, reverse=True)
    d = {
        "stage":    node.name,
        "hits":     node.count,
        "total_s":  round(node.total_ms / 1000, 4),
        "avg_ms":   round(node.total_ms / node.count, 3) if node.count else 0.0,
        "stdev_ms": round(node.stdev_ms, 3),
        "cv":       round(node.cv, 3),
    }
    if children:
        d["children"] = [_node_to_dict(c) for c in children]
    return d


def _attributed_row(node, roots: list[Span], name: str, child_filter) -> "dict | None":
    """Build the "stat_cell/blob" row for ONE section (pct or val) as that
    section's own ATTRIBUTABLE share, not the raw shared span's combined
    total -- see gfl2.timing.attribute_shared_span's own docstring for the
    full rationale (known_issues.txt §41's UPDATE, decisions.txt #104's
    follow-up): reusing the shared node's own hits/total_s/avg_ms directly
    under both the pct AND val sections showed the IDENTICAL combined
    number in both places, which a reader could double-count when summing
    each section's own total. Returns None when `roots` has no per-line
    children for `name` at all (a v0_1_0/v0_1_1/v0_2_0-style engine, whose
    single "stat_cell/blob" call has no internal pct/val split to
    attribute) -- the caller falls back to the raw shared row in that
    case, since there the identical-number situation is not a reporting
    artifact, it's the only real information available."""
    attributed = attribute_shared_span(roots, name, child_filter)
    if attributed is None:
        return None
    hits, total_ms, stdev_ms = attributed
    avg_ms = total_ms / hits if hits else 0.0
    cv = (stdev_ms / avg_ms) if avg_ms > 1e-12 else 0.0
    row = {
        "stage":    name,
        "hits":     hits,
        "total_s":  round(total_ms / 1000, 4),
        "avg_ms":   round(avg_ms, 3),
        "stdev_ms": round(stdev_ms, 3),
        "cv":       round(cv, 3),
    }
    filtered_children = sorted(
        (c for c in node.children.values() if child_filter(c.name)),
        key=lambda n: n.total_ms, reverse=True,
    )
    if filtered_children:
        row["children"] = [_node_to_dict(c) for c in filtered_children]
    return row


def _pipeline_tree(agg_tree, roots: list[Span], names: tuple[str, ...],
                    stat_cell_child_prefix: "str | None") -> list[dict]:
    """One nested dict per name in `names` found (with count > 0) anywhere
    in `agg_tree` -- see gfl2.timing.find_named_node. "stat_cell/blob"
    specifically is attributed to this section's own pct/val share (see
    _attributed_row) rather than shown as the raw shared span, whenever
    that attribution is possible; its CHILDREN are always filtered to
    `stat_cell_child_prefix` (e.g. "pct/" or "val/") either way, so pct's
    and val's own branch/leaf breakdowns never bleed into each other
    despite sharing one parent span."""
    rows = []
    for name in names:
        node = find_named_node(agg_tree, name)
        if node is None or node.count == 0:
            continue

        if name == "stat_cell/blob" and stat_cell_child_prefix is not None:
            prefix = stat_cell_child_prefix
            child_filter = lambda cname, _p=prefix: cname.startswith(_p)
            row = _attributed_row(node, roots, name, child_filter)
            if row is not None:
                rows.append(row)
                continue
            # No per-line children anywhere for this engine -- fall through
            # to the raw combined row below (child_filter still applies,
            # but will simply exclude everything since nothing matches).
            rows.append(_node_to_dict(node, child_filter=child_filter))
            continue

        rows.append(_node_to_dict(node))
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
    agg_tree = build_agg_tree(roots)

    sections = {}
    for name in SECTION_NAMES:
        summary = section_stats.get(name, _EMPTY_SUMMARY)
        sections[name] = {
            "summary":  dict(summary),
            "pipeline": _pipeline_tree(agg_tree, roots, _SECTION_ROOT_NAMES[name],
                                        _STAT_CELL_CHILD_PREFIX.get(name)),
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
