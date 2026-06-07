# -*- coding: utf-8 -*-
"""
gfl2/trace.py - Lightweight timing trace for vision pipeline functions.

Enable by setting the environment variable:
    set GFL2_TRACE=1     (Windows)
    export GFL2_TRACE=1  (Linux/Mac)

Output goes to stderr so it doesn't mix with CSV output.

Format:
    [trace] HH:MM:SS.mmm  FUNC_NAME           (caller: CALLER)  →  0.123s
"""
from __future__ import annotations
import functools
import inspect
import os
import sys
import time
from typing import Callable

_ENABLED = os.environ.get("GFL2_TRACE", "").strip() not in ("", "0")

# Column widths for alignment
_W_FUNC   = 28
_W_CALLER = 24


def _now() -> str:
    t = time.localtime()
    ms = int((time.time() % 1) * 1000)
    return f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}.{ms:03d}"


def _caller_name(depth: int = 3) -> str:
    """Return the name of the function that called the decorated function."""
    try:
        frame = inspect.stack()[depth]
        return frame.function
    except Exception:
        return "?"


def timed(label: str | None = None) -> Callable:
    """
    Decorator that logs elapsed time and caller name when GFL2_TRACE=1.

    Usage:
        @timed()
        def my_func(...): ...

        @timed("custom label")
        def my_func(...): ...
    """
    def decorator(fn: Callable) -> Callable:
        name = label or fn.__qualname__

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not _ENABLED:
                return fn(*args, **kwargs)
            caller = _caller_name(depth=2)
            t0     = time.perf_counter()
            try:
                result = fn(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - t0
                caller_str = f"(caller: {caller})"
                print(
                    f"[trace] {_now()}  {name:<{_W_FUNC}}"
                    f"  {caller_str:<{_W_CALLER + 10}}"
                    f"  {elapsed:.3f}s",
                    file=sys.stderr,
                )
            return result

        return wrapper
    return decorator
