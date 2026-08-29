# -*- coding: utf-8 -*-
"""
debugs/check_stale_action_item_citations.py -- flag repo-wide citations of a
CLOSED docs/action_items.txt item (action_items.txt #29).

WHY: docs/action_items.txt is an explicit scratch backlog (CLAUDE.md: "not a
permanent record... trim... or delete it") -- closed items are DELETED
outright, never tombstoned the way docs/known_issues.txt/decisions.txt entries
are.  A citation like "action_items.txt #18" or "action item #18" left in
another file after item 18 closes is a dangling pointer: a reader follows it
expecting current, actionable detail and finds nothing.  This has happened for
real, more than once, found only by manual grep-and-classify sweeps (see
docs/decisions.txt #88 for a ~100-citation, 23-file sweep, and
docs/takeaways.txt #80 for the general lesson).  This script is the cheap,
repeatable version of that manual sweep.

THIS IS A FLAGGING TOOL, NOT AN AUTO-FIXER.  docs/decisions.txt #96 (the
--stat-ocr-engine naming cleanup) established the project's current, most
authoritative policy on this exact question: docs/known_issues.txt,
docs/decisions.txt, and docs/takeaways.txt entries are PERMANENT HISTORICAL
RECORD, describing what was true when written, and are deliberately NOT
rewritten when something they cite later closes or gets renamed -- a
citation there to a now-closed action item is expected, not a defect.
Every other file (CLAUDE.md, reference.txt, docs/technical_design.txt, and
source comments) is a living document that IS expected to stay current, so a
stale citation there is a real, actionable finding.  This script reports the
two groups separately for exactly that reason -- only the ACTIONABLE group
should ever prompt an edit; the HISTORICAL group is informational only.
Even within the actionable group, use judgement: remove only the
action_items.txt pointer/clause, never the substantive technical content it
was attached to (decisions.txt #88).

METHOD: parse docs/action_items.txt for every item header ("^N.  ...") to
build the set of item numbers CURRENTLY PRESENT in the file (regardless of
their own STATUS -- OPEN/IN PROGRESS/ON HOLD are all still citable; only a
number that no longer heads any item is stale, since DONE items are deleted
outright per this file's own numbering convention).  Then grep every
.py/.txt/.md file in the repo for "action[_ -]item(s)(.txt)? #N" (any
prefix/plurality, matching decisions.txt #88's own citation-form definition,
including a "#28/#29" or "#28, #29" chain) and flag any N not in that set.

Usage:
    python debugs/check_stale_action_item_citations.py
    python debugs/check_stale_action_item_citations.py --action-items docs/action_items.txt
"""
import argparse
import os
import re
import sys

_ITEM_HEADER_RE = re.compile(r"^(\d+)\.\s", re.MULTILINE)
_STATUS_RE = re.compile(r"STATUS:\s*([A-Z][A-Z ]*)")
_CITATION_RE = re.compile(
    r"action[ _-]items?(?:\.txt)?\s*(#\d+(?:\s*[/,]\s*#\d+)*)", re.IGNORECASE
)
_NUM_RE = re.compile(r"\d+")

_SCAN_EXTENSIONS = (".py", ".txt", ".md")
_SKIP_DIR_NAMES = {".git", "__pycache__"}
_SKIP_DIR_PREFIXES = ("pytest-cache-files",)

# Permanent historical record (decisions.txt #96) -- exempt from the
# "actionable" bucket. Paths are matched by suffix against the normalized,
# forward-slash relative path from the scan root.
_HISTORICAL_DOCS = (
    "docs/known_issues.txt",
    "docs/decisions.txt",
    "docs/takeaways.txt",
)


def is_historical(rel_path):
    norm = rel_path.replace(os.sep, "/")
    return any(norm == d or norm.endswith("/" + d) for d in _HISTORICAL_DOCS)


def parse_action_items(path):
    """Return {item_number: status_text} for every item currently in path."""
    text = open(path, encoding="utf-8").read()
    headers = list(_ITEM_HEADER_RE.finditer(text))
    items = {}
    for i, m in enumerate(headers):
        num = int(m.group(1))
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        body = text[m.start():end]
        status_m = _STATUS_RE.search(body)
        items[num] = status_m.group(1).strip() if status_m else "UNKNOWN"
    return items


def iter_scan_files(root, skip_paths=()):
    skip_paths = {os.path.normcase(os.path.abspath(p)) for p in skip_paths}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in _SKIP_DIR_NAMES and not d.startswith(_SKIP_DIR_PREFIXES)
        ]
        for fname in filenames:
            if not fname.endswith(_SCAN_EXTENSIONS):
                continue
            fpath = os.path.join(dirpath, fname)
            if os.path.normcase(os.path.abspath(fpath)) in skip_paths:
                continue
            yield fpath


def find_citations(fpath):
    """Yield (line_no, line_text, [cited_numbers]) for each citation in fpath."""
    with open(fpath, encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            for m in _CITATION_RE.finditer(line):
                nums = [int(n) for n in _NUM_RE.findall(m.group(1))]
                yield line_no, line.rstrip("\n"), nums


def check(action_items_path, scan_root):
    existing = parse_action_items(action_items_path)
    existing_nums = set(existing)

    done_but_present = sorted(n for n, s in existing.items() if s.upper() == "DONE")

    stale_hits = []  # (num, fpath, line_no, line_text)
    for fpath in iter_scan_files(scan_root, skip_paths=(__file__, action_items_path)):
        for line_no, line_text, nums in find_citations(fpath):
            for n in nums:
                if n not in existing_nums:
                    stale_hits.append((n, fpath, line_no, line_text))

    return existing, done_but_present, stale_hits


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--action-items", default="docs/action_items.txt")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()

    existing, done_but_present, stale_hits = check(args.action_items, args.root)

    print("=== Stale action_items.txt citation check ===")
    print(
        f"Existing item numbers ({len(existing)}): "
        + ", ".join(str(n) for n in sorted(existing))
    )
    print()

    if done_but_present:
        print(
            "REPO-HEALTH WARNING: item(s) marked DONE but not yet deleted "
            f"from {args.action_items} (should be ported to known_issues.txt/"
            f"decisions.txt and removed): {done_but_present}"
        )
        print()

    if not stale_hits:
        print("No stale citations found.")
        return 0

    actionable = []
    historical = []
    for num, fpath, line_no, line_text in stale_hits:
        rel = os.path.relpath(fpath, args.root)
        (historical if is_historical(rel) else actionable).append(
            (num, rel, line_no)
        )

    if historical:
        historical.sort()
        print(
            f"HISTORICAL (informational only, {len(historical)} hit(s) -- "
            "exempt per decisions.txt #96, these files are permanent record "
            "and are deliberately not rewritten):"
        )
        for num, rel, line_no in historical:
            print(f"  #{num:<3} {rel}:{line_no}")
        print()

    if actionable:
        actionable.sort()
        print(f"ACTIONABLE STALE CITATIONS ({len(actionable)} across "
              f"{len({rel for _, rel, _ in actionable})} file(s)):")
        for num, rel, line_no in actionable:
            print(f"  #{num:<3} {rel}:{line_no}")
        print()
        closed_nums = sorted({n for n, _, _ in actionable})
        print(f"Closed item number(s) cited in living docs/source: {closed_nums}")
        print(
            "NOTE: still a flagging tool, not an auto-fixer -- judge each "
            "before editing; remove only the action_items.txt pointer/"
            "clause, never the substantive content it's attached to "
            "(decisions.txt #88)."
        )
    else:
        print("No actionable stale citations (only historical hits above).")

    return 1 if actionable else 0


if __name__ == "__main__":
    sys.exit(main())
