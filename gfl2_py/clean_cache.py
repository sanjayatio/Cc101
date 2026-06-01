#!/usr/bin/env python3
"""
clean_cache.py - Delete all __pycache__ directories in the project.

Run this once after pulling updates, or whenever you suspect stale
bytecode is causing unexpected behaviour.

    python clean_cache.py
"""
import shutil
from pathlib import Path

root = Path(__file__).parent
deleted = []
for d in root.rglob("__pycache__"):
    try:
        shutil.rmtree(d)
        deleted.append(d.relative_to(root))
    except Exception as e:
        print(f"  skip {d}: {e}")

if deleted:
    print(f"Deleted {len(deleted)} __pycache__ director{'y' if len(deleted)==1 else 'ies'}:")
    for d in deleted:
        print(f"  {d}")
else:
    print("No __pycache__ directories found.")
