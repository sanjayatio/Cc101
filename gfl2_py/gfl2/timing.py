"""
gfl2/timing.py — Lightweight hierarchical wall-clock timer.

Usage
-----
    from gfl2.timing import TimerStack

    t = TimerStack()
    with t.timed("parse"):
        with t.timed("step_a"):
            ...
        with t.timed("step_b"):
            ...
    print(t.root.tree())

Output
------
    parse                                           245.30 ms
      step_a                                         122.10 ms  ( 49.8%)
      step_b                                         123.20 ms  ( 50.2%)
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Span:
    """One timed node in the execution tree."""
    name:     str
    elapsed:  float      = 0.0
    children: list[Span] = field(default_factory=list)

    @property
    def ms(self) -> float:
        return self.elapsed * 1000

    # ── formatting ────────────────────────────────────────────────────────

    def _lines(self, indent: int, parent_ms: Optional[float]) -> list[str]:
        pct = f"  ({self.ms / parent_ms * 100:5.1f}%)" if parent_ms else ""
        label = "  " * indent + self.name
        line  = f"{label:<48}  {self.ms:9.2f} ms{pct}"
        lines = [line]
        for c in self.children:
            lines.extend(c._lines(indent + 1, self.ms))
        return lines

    def tree(self) -> str:
        """Return the full timing tree as a multi-line string."""
        return "\n".join(self._lines(0, None))

    # ── aggregation ───────────────────────────────────────────────────────

    def total_ms_for(self, name: str) -> float:
        """Sum elapsed ms for all spans named `name` anywhere in the tree."""
        total = self.ms if self.name == name else 0.0
        for c in self.children:
            total += c.total_ms_for(name)
        return total


class TimerStack:
    """
    Hierarchical wall-clock timer.  Not thread-safe (single-threaded use only).

    Create one instance per logical unit of work (e.g. per image).
    Call .timed(name) as a context manager; nesting is tracked automatically.
    The completed tree is available at .root after the outermost context exits.
    """

    def __init__(self) -> None:
        self._stack: list[Span] = []
        self.root:   Optional[Span] = None

    @contextmanager
    def timed(self, name: str):
        span = Span(name)
        if self._stack:
            self._stack[-1].children.append(span)
        else:
            self.root = span
        self._stack.append(span)
        t0 = time.perf_counter()
        try:
            yield span
        finally:
            span.elapsed = time.perf_counter() - t0
            self._stack.pop()


# ── batch summary helper ──────────────────────────────────────────────────────

def batch_summary(image_names: list[str], roots: list[Span]) -> str:
    """
    Given per-image Span roots, return a formatted summary table.

    Example output
    --------------
    ─── Batch timing summary ─────────────────────────────────────
    images:   5
    total:    1 234.50 ms
    average:    246.90 ms / image
    fastest:  gm_d_20250928.png         201.30 ms
    slowest:  gm_d_20250929.png         310.20 ms
    ──────────────────────────────────────────────────────────────
    """
    if not roots:
        return "(no images processed)"
    timings = [r.ms for r in roots]
    total   = sum(timings)
    avg     = total / len(timings)
    i_fast  = timings.index(min(timings))
    i_slow  = timings.index(max(timings))

    sep = "─" * 62
    lines = [
        sep,
        f"{'images:':<12}{len(roots)}",
        f"{'total:':<12}{total:>10.2f} ms",
        f"{'average:':<12}{avg:>10.2f} ms / image",
        f"{'fastest:':<12}{image_names[i_fast]:<36}  {timings[i_fast]:>8.2f} ms",
        f"{'slowest:':<12}{image_names[i_slow]:<36}  {timings[i_slow]:>8.2f} ms",
        sep,
    ]
    return "\n".join(lines)



# ── pipeline breakdown ───────────────────────────────────────────────────────

class _AggNode:
    """Aggregated span node for batch pipeline summary.

    Tracks per-name mean AND variance via Welford's online algorithm (O(1)
    memory per node, no need to retain every individual sample) so the
    summary can report stdev/cv alongside total/count/avg -- added
    specifically so a hierarchical/branching classifier's per-branch
    variance is visible, not just its per-branch mean (a branch with a
    high mean but low variance is a very different cost-vs-benefit story
    than one with a low mean but high variance)."""
    __slots__ = ("name", "total_ms", "count", "_mean_ms", "_m2", "children")

    def __init__(self, name: str) -> None:
        self.name:      str                      = name
        self.total_ms:  float                    = 0.0
        self.count:     int                      = 0
        self._mean_ms:  float                    = 0.0
        self._m2:       float                    = 0.0   # Welford's sum of squared deviations
        self.children:  dict[str, "_AggNode"]   = {}

    def record(self, ms: float) -> None:
        self.total_ms += ms
        self.count    += 1
        delta = ms - self._mean_ms
        self._mean_ms += delta / self.count
        self._m2      += delta * (ms - self._mean_ms)

    @property
    def variance_ms2(self) -> float:
        return self._m2 / self.count if self.count > 0 else 0.0

    @property
    def stdev_ms(self) -> float:
        return self.variance_ms2 ** 0.5

    @property
    def cv(self) -> float:
        """Coefficient of variation (stdev/mean) -- scale-free, so a
        cheap-but-noisy branch and an expensive-but-noisy branch are
        directly comparable."""
        avg = self.total_ms / self.count if self.count else 0.0
        return (self.stdev_ms / avg) if avg > 1e-12 else 0.0

    def child(self, name: str) -> "_AggNode":
        if name not in self.children:
            self.children[name] = _AggNode(name)
        return self.children[name]


def build_agg_tree(roots: list[Span]) -> _AggNode:
    """Aggregate all sub-spans into a single tree, skipping image-filename
    roots. Public (not just pipeline_summary()'s own internal helper) so
    gfl2/report.py can build the SAME hierarchical aggregation the console
    tree uses when writing the persisted report file -- the two are never
    at risk of silently disagreeing about how spans are merged, since both
    call this one function."""
    virtual_root = _AggNode("__root__")

    def walk(span: Span, parent: _AggNode) -> None:
        node = parent.child(span.name)
        node.record(span.ms)
        for child in span.children:
            walk(child, node)

    for root in roots:
        for child in root.children:   # skip root = image filename
            walk(child, virtual_root)

    return virtual_root


def find_named_node(tree: _AggNode, name: str) -> Optional[_AggNode]:
    """Recursively find the _AggNode named `name` anywhere in `tree` (as
    built by build_agg_tree), regardless of depth or parent -- e.g.
    "stat_cell/blob" or "pct/classify". Returns the first match; every
    span name this project currently searches for is only ever created at
    one structural call site, so a second, distinct match should not
    occur, but if it ever did, only the first would be reflected here
    rather than silently combining two structurally different things."""
    if tree.name == name:
        return tree
    for child in tree.children.values():
        found = find_named_node(child, name)
        if found is not None:
            return found
    return None


def inject_branch_spans(classify_span, branch_acc: "Optional[dict[str, list[float]]]",
                        skel_acc: "Optional[list[float]]" = None,
                        skel_leaf_name: str = "skeleton_235",
                        skel_child_name: str = "skeleton_thin") -> None:
    """Attach per-leaf classify() timing as synthetic child Spans under
    `classify_span` -- one child span per glyph, named by whichever leaf
    branch that glyph actually returned through. Shared by every
    v0_3_0-family engine's classify()-style function (gfl2.stat_ocr_v0_3_0,
    gfl2.score_ocr_v0_3_0, gfl2.header_ocr_v0_3_0) so the branch/leaf
    breakdown mechanism has one definition instead of three near-identical
    copies -- originally a private copy inside gfl2/stat_ocr_v0_3_0.py only
    (known_issues.txt §39); centralized here once score/header gained the
    same instrumentation (known_issues.txt §41 / decisions.txt #104).

    branch_acc: optional {branch_name: [elapsed_s, ...]} accumulator --
      when falsy (None or empty), this is a no-op (matches every caller's
      own "only build branch_acc when a timer was actually passed"
      convention, so there is zero overhead when nobody asked for timing).
    skel_acc: optional [elapsed_s, ...], consumed in the same order
      branch_acc recorded `skel_leaf_name` occurrences, nested as a
      `skel_child_name` child of each one -- isolates a sub-leaf's own
      dominant cost (e.g. Zhang-Suen thinning) from the rest of that
      leaf's logic. Engines with no such sub-leaf (score/header, as of
      this writing) simply never pass skel_acc / never record
      `skel_leaf_name`, so this stays a no-op for them.
    """
    if not branch_acc:
        return
    branch_span = Span("branch", 0.0)
    skel_iter = iter(skel_acc or [])
    for name, elapsed_list in branch_acc.items():
        for elapsed in elapsed_list:
            leaf_span = Span(name, elapsed)
            if name == skel_leaf_name:
                thin_elapsed = next(skel_iter, None)
                if thin_elapsed is not None:
                    leaf_span.children.append(Span(skel_child_name, thin_elapsed))
            branch_span.children.append(leaf_span)
    branch_span.elapsed = sum(c.elapsed for c in branch_span.children)
    classify_span.children.append(branch_span)


def attribute_shared_span(roots: list[Span], name: str,
                          name_filter) -> "Optional[tuple[int, float, float]]":
    """For every literal occurrence of a Span named `name` anywhere in the
    RAW (non-aggregated) `roots`, sum that one occurrence's own DIRECT
    children whose name passes `name_filter`, then Welford-aggregate those
    per-occurrence sums into (hits, total_ms, stdev_ms). Returns None if
    `name` is never found, or found but no occurrence ever has a child
    passing `name_filter` at all.

    WHY THIS EXISTS: a span shared between two logically distinct report
    views (e.g. gfl2/stat_ocr_v0_3_0.py's one "stat_cell/blob" span, which
    classifies BOTH the pct and val lines in a single call) has only ONE
    real aggregate -- its own directly-measured total, covering both
    lines together. If a per-line report view (e.g. gfl2/report.py's pct
    section vs its val section) just reused that shared total as its own
    "parent row" number, both views would show the exact SAME combined
    number -- correct as a raw fact about the underlying call, but exactly
    the kind of number a reader (or a future tool) could silently
    double-count when summing "pct's total" + "val's total" across the
    two views, since neither number is actually THAT view's own
    attributable share (known_issues.txt §41's UPDATE, decisions.txt
    #104's follow-up). This computes each view's own share instead, by
    summing only the name_filter-matching children PER OCCURRENCE (so a
    view's own binarize+blobs+extract+classify time is added together
    once per call, not conflated across calls) before aggregating.

    Returns None (rather than a zeroed tuple) when no occurrence has any
    matching child at all -- e.g. gfl2/stat_ocr_v0_1_0.py-style engines,
    whose "stat_cell/blob" span has no per-line children of any kind (no
    internal instrumentation exists to split pct from val within that one
    call). Callers should fall back to the shared span's own raw combined
    total in that case: there the identical-number-under-both-views
    situation is not a reporting artifact to fix, it's the only
    information that exists -- the call genuinely cannot be attributed to
    one line or the other."""
    count = 0
    mean_ms = 0.0
    m2 = 0.0
    matched_any = False

    def walk(span: Span) -> None:
        nonlocal count, mean_ms, m2, matched_any
        if span.name == name:
            matches = [c for c in span.children if name_filter(c.name)]
            if matches:
                matched_any = True
                val_ms = sum(c.ms for c in matches)
                count += 1
                delta = val_ms - mean_ms
                mean_ms += delta / count
                m2 += delta * (val_ms - mean_ms)
        for child in span.children:
            walk(child)

    for root in roots:
        walk(root)

    if not matched_any:
        return None
    variance = m2 / count if count else 0.0
    return count, mean_ms * count, variance ** 0.5


def _agg_lines(node: "_AggNode", indent: int,
               parent_ms: Optional[float]) -> list[str]:
    pct   = f"  ({node.total_ms / parent_ms * 100:5.1f}%)" if parent_ms else ""
    label = "  " * indent + node.name
    avg   = node.total_ms / node.count
    line  = (f"  {label:<34}  {node.total_ms/1000:>7.2f}s"
             f"  {node.count:>6}\u00d7  avg {avg:>7.1f}ms"
             f"  stdev {node.stdev_ms:>7.1f}ms  cv {node.cv:>4.2f}{pct}")
    lines = [line]
    for child in sorted(node.children.values(),
                        key=lambda n: n.total_ms, reverse=True):
        lines.extend(_agg_lines(child, indent + 1, node.total_ms))
    return lines


def pipeline_summary(image_names: list[str], roots: list[Span],
                     wall_ms: Optional[float] = None, unit: str = "image") -> str:
    """
    Aggregate all sub-spans across every root and return a hierarchical tree
    sorted by total time descending at each level.

    unit: the noun for the header count -- "image" (default, matches every
      existing caller) when one root = one processed image, but any
      per-unit-of-work root list works (e.g. "cell" for one root per stat
      cell, gfl2.stat_ocr_v0_2_0.verify()) as long as roots are still one
      TimerStack.root per independent unit.

    Example
    -------
    ─── Pipeline breakdown (87 images, 266.12s) ──────────────────────────
      extract_header               97.13s    162×  avg 599.6ms  stdev  120.3ms  cv 0.20
        stats_row                  54.45s    162×  avg 336.1ms  stdev   80.1ms  cv 0.24  ( 56.1%)
        score/bright               42.67s    264×  avg 161.6ms  stdev   30.5ms  cv 0.19  ( 43.9%)
      extract_doll_rows           168.92s    162×  avg 1042.7ms stdev  210.4ms  cv 0.20
        stat_cell/psm6            114.68s    574×  avg 199.8ms  stdev   95.2ms  cv 0.48  ( 67.9%)
        stat_cell/blob             26.25s   3216×  avg   8.2ms  stdev    2.1ms  cv 0.26  ( 15.5%)
        stat_cell/psm4             25.81s    132×  avg 195.5ms  stdev   88.0ms  cv 0.45  ( 15.3%)
        ...
    ──────────────────────────────────────────────────────────────────────
    stdev/cv let you tell "expensive but predictable" (low cv) apart from
    "cheap on average but occasionally very slow" (high cv) -- useful when
    a branching/hierarchical classifier's per-branch cost varies by which
    path a given input takes, not just by the branch's mean cost.
    """
    if not roots:
        return f"(no {unit}s processed)"

    tree   = build_agg_tree(roots)
    n      = len(roots)
    total  = sum(r.ms for r in roots)
    w_str  = f", {wall_ms/1000:.2f}s wall" if wall_ms is not None else ""
    sep    = "─" * 68

    header_lines = [
        sep,
        f"Pipeline breakdown  ({n} {unit}{'s' if n != 1 else ''}, "
        f"{total/1000:.2f}s total{w_str})",
        f"  {'stage':<34}  {'total':>8}  {'calls':>7}  {'avg/call':>10}"
        f"  {'stdev':>13}  {'cv':>6}",
        "  " + "─" * 84,
    ]

    body_lines: list[str] = []
    for child in sorted(tree.children.values(),
                        key=lambda n: n.total_ms, reverse=True):
        body_lines.extend(_agg_lines(child, 0, None))

    return "\n".join(header_lines + body_lines + [sep])
