#!/usr/bin/env python3
"""
GFL2 Doll Icon Image Extractor
===============================
Downloads the skill-icon and neural-helix-key-icon images that are embedded
directly in Google Sheets cells (Insert > Image), which the Sheets values API
cannot return (extract_gfl2.py logs these under "Image Issues" instead).

Technique: Google Sheets' read-only /htmlview render (docs.google.com/
spreadsheets/d/{ID}/htmlview#gid={gid}) loads a nested iframe
(.../htmlview/sheet?...) that renders the sheet as a plain HTML <table> --
no canvas, no scroll virtualization -- with every embedded image as a real
<img src="https://docs.google.com/sheets-images-rt/..."> element. Each img's
row number is read directly off the table's own row-number gutter cell (the
first <td>/<th> of its <tr>), and its column position via td.cellIndex, so
mapping an image back to "which skill/helix key is this" needs no pixel math
at all. The src URLs are plain, unauthenticated, directly-fetchable HTTPS
URLs (confirmed via a bare urllib GET, no cookies needed).

Usage (from inside gfl2_web/):
  python extract_gfl2_images.py                 # all doll tabs
  python extract_gfl2_images.py --tab "Groza"    # a single tab (testing)
  python extract_gfl2_images.py --limit 3        # first N tabs (testing)

Requires: playwright (pip install playwright && playwright install chromium)
"""

import argparse
import re
import ssl
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

import extract_gfl2 as base

SCRIPT_DIR = base.SCRIPT_DIR
ASSETS_DIR = base.ASSETS_DIR
LOG_FILE = SCRIPT_DIR / "data" / "master_doll_details_image_log.txt"

PAGE_LOAD_WAIT_MS = 3000
DATA_COLUMN_CELL_INDEX = 1  # 0 = row-number gutter, 1 = column A

_SSL_CTX = ssl.create_default_context()

IMG_SCAN_JS = """() => {
    const out = [];
    document.querySelectorAll('img').forEach(img => {
        const tr = img.closest('tr');
        const td = img.closest('td');
        if (!tr || !td) return;
        const firstCell = tr.querySelector('td, th');
        const rowLabel = firstCell ? firstCell.textContent.trim() : '';
        out.push({ src: img.src, rowLabel, cellIndex: td.cellIndex });
    });
    return out;
}"""

_CONTROL_CHARS_RE = re.compile(r"[\r\n\t]+")


def safe_file_name(name: str) -> str:
    """Some skill/helix-key names contain a '/' (would create an unintended
    subdirectory), a '?' (invalid on Windows), or an embedded newline (also
    invalid on Windows) -- e.g. 'Assault Spray/Overwhelming Burst',
    'Want Another Bite?'. Sanitize for filesystem safety. Note this means the
    saved filename can diverge from master_doll_details.js's unsanitized
    `icon` field for these edge cases."""
    cleaned = _CONTROL_CHARS_RE.sub(" ", name)
    cleaned = base.safe_path_name(cleaned)
    return cleaned.strip().rstrip(".")


log_lines = []


def log(msg: str) -> None:
    print(msg)
    log_lines.append(msg)


# ── row targets (skill icons + helix key icons) ────────────────────────────

def collect_skill_icon_targets(rows: list, skills_idx: int, vert_idx: int) -> list[tuple[int, str]]:
    targets = []
    for i, row in enumerate(rows[skills_idx + 1:vert_idx], start=skills_idx + 1):
        b_v = base.c(row, 1)
        if b_v and "\n\n(" in b_v:
            name = b_v.split("\n\n(")[0].strip()
            targets.append((i + 1, name))
    return targets


def collect_helix_icon_targets(rows: list, helix_idx: int) -> list[tuple[int, str]]:
    targets = []
    for i, row in enumerate(rows[helix_idx + 1:], start=helix_idx + 1):
        b_v = base.c(row, 1)
        d_v = base.c(row, 3)
        if not b_v or b_v in ("Node", "Icon", "Vertebrae"):
            continue
        if b_v.startswith("Enhancement"):
            continue
        if b_v in ("Affinity Key", "Common Key"):
            key_name = b_v
        else:
            colon = d_v.find(":")
            key_name = d_v[:colon].strip() if 0 < colon < 60 else b_v
        targets.append((i + 1, key_name))
    return targets


# ── htmlview scraping ───────────────────────────────────────────────────────

RANGE_PADDING = 5
MAX_WINDOW_SPAN = 100  # rows; wider windows risk hitting htmlview's per-load image budget


def chunk_target_rows(target_rows: list[int], max_span: int = MAX_WINDOW_SPAN) -> list[tuple[int, int]]:
    """Groups target rows into (min, max) windows, splitting whenever a
    window would otherwise span more than max_span rows (dolls with more
    skills/helix keys than usual spread targets over a wider range, which
    can exceed htmlview's per-load image budget even with range scoping)."""
    rows = sorted(target_rows)
    windows = []
    start = prev = rows[0]
    for r in rows[1:]:
        if r - start > max_span:
            windows.append((start, prev))
            start = r
        prev = r
    windows.append((start, prev))
    return windows


def fetch_row_image_urls(browser, gid: str, target_rows: list[int]) -> dict[int, str]:
    """Returns {row_number: image_src} for every column-A embedded image in
    the tab, scraped from the /htmlview iframe's plain HTML table.

    /htmlview appears to cap the total number of embedded images it renders
    per load; for image-heavy tabs this silently drops later rows (skill
    icons far down the sheet, or all helix keys). Scoping the render to a
    range fragment tightly around just our target rows keeps the unrelated
    portrait/weapon-art images (near the top of every tab) from eating that
    budget; dolls with an unusually wide target span get split into several
    smaller-range windows so no single load's budget gets exhausted."""
    merged: dict[int, str] = {}
    for lo, hi in chunk_target_rows(target_rows):
        start = max(1, lo - RANGE_PADDING)
        end = hi + RANGE_PADDING
        url = f"https://docs.google.com/spreadsheets/d/{base.SPREADSHEET_ID}/htmlview#gid={gid}&range=A{start}:I{end}"
        # A fresh page per window: htmlview's SPA doesn't reliably reprocess
        # a hash-only URL change (same path/query, different #range=) on a
        # reused page.
        page = browser.new_page(viewport={"width": 1600, "height": 1200})
        try:
            merged.update(_scan_page_images(page, url))
        finally:
            page.close()
    return merged


def _scan_page_images(page, url: str) -> dict[int, str]:
    page.goto(url, wait_until="load", timeout=60000)
    page.wait_for_timeout(PAGE_LOAD_WAIT_MS)

    sheet_frame = next((f for f in page.frames if "/htmlview/sheet" in f.url), None)
    if sheet_frame is None:
        return {}

    raw = sheet_frame.evaluate(IMG_SCAN_JS)
    by_row: dict[int, str] = {}
    for entry in raw:
        if entry["cellIndex"] != DATA_COLUMN_CELL_INDEX:
            continue
        label = entry["rowLabel"]
        if not label.isdigit():
            continue
        by_row[int(label)] = entry["src"]
    return by_row


def download_image(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20, context=_SSL_CTX) as resp:
            return resp.read()
    except Exception as exc:
        log(f"    WARN: download failed for {url}: {exc}")
        return None


# ── per-doll processing ─────────────────────────────────────────────────────

def process_doll(browser, sheet_name: str, gid: str) -> tuple[int, int]:
    clean = sheet_name.strip()
    rows = base.fetch_values(sheet_name)
    if rows is None:
        log(f"  {clean}: FETCH FAILED, skipping")
        return 0, 0

    skills_idx = base.find_section(rows, "Skills")
    vert_idx = base.find_section(rows, "Vertebrae Upgrade")
    helix_idx = base.find_helix_section(rows)
    if any(x is None for x in [skills_idx, vert_idx, helix_idx]):
        log(f"  {clean}: MISSING SECTION, skipping")
        return 0, 0

    general = base.parse_general(rows, skills_idx)
    doll_name = general.get("name") or clean

    all_targets = collect_skill_icon_targets(rows, skills_idx, vert_idx) + collect_helix_icon_targets(rows, helix_idx)
    if not all_targets:
        log(f"  {clean}: no icon targets found")
        return 0, 0

    row_urls = fetch_row_image_urls(browser, gid, [row for row, _ in all_targets])

    out_dir = ASSETS_DIR / base.safe_path_name(doll_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    name_counts: dict[str, int] = {}
    for _, name in all_targets:
        key = safe_file_name(name)
        name_counts[key] = name_counts.get(key, 0) + 1

    seen: dict[str, int] = {}
    saved = 0
    for row, name in all_targets:
        src = row_urls.get(row)
        if src is None:
            log(f"    MISSING: '{name}' (row {row}) — no column-A image found in htmlview")
            continue
        data = download_image(src)
        if data is None:
            continue
        key = safe_file_name(name)
        if name_counts[key] > 1:
            # Two different skills/helix keys share this display name in the
            # sheet -- disambiguate by row so one save doesn't silently
            # overwrite the other.
            seen[key] = seen.get(key, 0) + 1
            file_name = f"{key} (row {row})"
            log(f"    NOTE: duplicate name '{name}' also at another row — saved as '{file_name}.png'")
        else:
            file_name = key
        (out_dir / f"{file_name}.png").write_bytes(data)
        saved += 1

    log(f"  {doll_name}: {saved}/{len(all_targets)} icons saved")
    return saved, len(all_targets)


# ── main ──────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tab", help="Process only this single doll tab (exact or stripped title)")
    ap.add_argument("--limit", type=int, help="Process only the first N doll tabs")
    args = ap.parse_args()

    print("Fetching spreadsheet metadata...")
    meta = base._get(f"{base.BASE_URL}?key={base.API_KEY}&fields=sheets.properties")
    if not meta:
        print("Failed to fetch metadata.")
        return

    all_tabs = [(s["properties"]["title"], s["properties"]["sheetId"]) for s in meta.get("sheets", [])]
    doll_tabs = [(name, sid) for name, sid in all_tabs if name.strip() not in base.EXCLUDED_TABS]

    if args.tab:
        doll_tabs = [(name, sid) for name, sid in doll_tabs if name.strip() == args.tab.strip()]
        if not doll_tabs:
            print(f"No tab matching '{args.tab}' found.")
            return
    if args.limit:
        doll_tabs = doll_tabs[: args.limit]

    print(f"Processing {len(doll_tabs)} doll tab(s)\n")

    total_saved = total_targets = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for i, (sheet_name, sheet_id) in enumerate(doll_tabs):
            print(f"[{i + 1:2d}/{len(doll_tabs)}] {sheet_name.strip()}...")
            try:
                saved, targets = process_doll(browser, sheet_name, str(sheet_id))
            except Exception as exc:
                log(f"  {sheet_name.strip()}: ERROR {exc}")
                saved, targets = 0, 0
            total_saved += saved
            total_targets += targets
            if (i + 1) % 15 == 0:
                time.sleep(1)

        browser.close()

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(
        f"GFL2 Image Extraction Log ({time.strftime('%Y-%m-%d')})\n"
        f"Saved {total_saved}/{total_targets} icons\n\n" + "\n".join(log_lines),
        encoding="utf-8",
    )
    print(f"\nDone. {total_saved}/{total_targets} icons saved. Log: {LOG_FILE}")


if __name__ == "__main__":
    main()
