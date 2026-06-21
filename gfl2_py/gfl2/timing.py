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
    """Aggregated span node for batch pipeline summary."""
    __slots__ = ("name", "total_ms", "count", "children")

    def __init__(self, name: str) -> None:
        self.name:      str                      = name
        self.total_ms:  float                    = 0.0
        self.count:     int                      = 0
        self.children:  dict[str, "_AggNode"]   = {}

    def record(self, ms: float) -> None:
        self.total_ms += ms
        self.count    += 1

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
             f"  {node.count:>6}\u00d7  avg {avg:>7.1f}ms{pct}")
    lines = [line]
    for child in sorted(node.children.values(),
                        key=lambda n: n.total_ms, reverse=True):
        lines.extend(_agg_lines(child, indent + 1, node.total_ms))
    return lines


def pipeline_summary(image_names: list[str], roots: list[Span],
                     wall_ms: Optional[float] = None) -> str:
    """
    Aggregate all sub-spans across every root and return a hierarchical tree
    sorted by total time descending at each level.

    Example
    -------
    ─── Pipeline breakdown (87 images, 266.12s) ──────────────────────────
      extract_header               97.13s    162×  avg 599.6ms
        stats_row                  54.45s    162×  avg 336.1ms  ( 56.1%)
        score/bright               42.67s    264×  avg 161.6ms  ( 43.9%)
      extract_doll_rows           168.92s    162×  avg 1042.7ms
        stat_cell/psm6            114.68s    574×  avg 199.8ms  ( 67.9%)
        stat_cell/blob             26.25s   3216×  avg   8.2ms  ( 15.5%)
        stat_cell/psm4             25.81s    132×  avg 195.5ms  ( 15.3%)
        ...
    ──────────────────────────────────────────────────────────────────────
    """
    if not roots:
        return "(no images processed)"

    tree   = _build_agg_tree(roots)
    n      = len(roots)
    total  = sum(r.ms for r in roots)
    w_str  = f", {wall_ms/1000:.2f}s wall" if wall_ms is not None else ""
    sep    = "─" * 68

    header_lines = [
        sep,
        f"Pipeline breakdown  ({n} image{'s' if n != 1 else ''}, "
        f"{total/1000:.2f}s total{w_str})",
        f"  {'stage':<34}  {'total':>8}  {'calls':>7}  {'avg/call':>10}",
        "  " + "─" * 60,
    ]

    body_lines: list[str] = []
    for child in sorted(tree.children.values(),
                        key=lambda n: n.total_ms, reverse=True):
        body_lines.extend(_agg_lines(child, 0, None))

    return "\n".join(header_lines + body_lines + [sep])
