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


def _build_agg_tree(roots: list[Span]) -> _AggNode:
    """Aggregate all sub-spans into a single tree, skipping image-filename roots."""
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
      cell, gfl2.stat_ocr_fft.verify()) as long as roots are still one
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

    tree   = _build_agg_tree(roots)
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
