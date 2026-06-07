#!/usr/bin/env python3
"""
GFL2 Doll Info Extractor
========================
Fetches all doll tabs from the GFL2 Google Sheet and writes:
  - data/data_info.js       (combined JS constant)
  - assets/{doll}/          (directories for future icons)
  - data/data_info_problems.txt  (list of inaccessible images)

Usage (from inside gfl2_web/):
  python extract_gfl2.py

Requires: Python 3.7+  (uses only stdlib — no pip install needed)
"""

import urllib.request
import urllib.parse
import json
import os
import re
import time
import ssl
from pathlib import Path

# ── env loader ────────────────────────────────────────────────────────────────

def _load_env(path: Path) -> dict:
    """Parse a .env file into a dict.  No pip required — stdlib only.
    Rules: KEY=VALUE; lines starting with # and blank lines are ignored;
    values are returned as plain strings (no quote stripping).
    """
    env = {}
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            eq = line.find("=")
            if eq == -1:
                continue
            env[line[:eq].strip()] = line[eq + 1:].strip()
    return env

_ENV_FILE = Path(__file__).resolve().parent / ".env"
if not _ENV_FILE.exists():
    raise FileNotFoundError(
        f".env not found at {_ENV_FILE}\n"
        "Copy .env.example to .env and fill in your GOOGLE_API_KEY."
    )
_ENV = _load_env(_ENV_FILE)

# ── config ────────────────────────────────────────────────────────────────────

API_KEY        = _ENV.get("GOOGLE_API_KEY") or ""
if not API_KEY or API_KEY == "your_api_key_here":
    raise ValueError(
        "GOOGLE_API_KEY is not set in .env.\n"
        "See the comments in .env for instructions on generating a key."
    )

SPREADSHEET_ID = "1DogyU3K7ZXw2qbhP1EhRXIAw5nCyIV5G5e-QWviBZME"
BASE_URL       = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}"

EXCLUDED_TABS  = {"Home", "Quick Links", "FAQ", "Weapons", "Jiangyu(old)"}

SCRIPT_DIR  = Path(__file__).resolve().parent
OUTPUT_JS   = SCRIPT_DIR / "data" / "master_doll_details.js"
PROBLEMS_F  = SCRIPT_DIR / "data" / "master_doll_details_problems.txt"
ASSETS_DIR  = SCRIPT_DIR / "assets"

problems = []

# ── HTTP helper ───────────────────────────────────────────────────────────────

_ctx = ssl.create_default_context()

def _get(url: str) -> dict | None:
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30, context=_ctx) as resp:
                return json.loads(resp.read().decode())
        except Exception as exc:
            if attempt < 2:
                time.sleep(5)
            else:
                print(f"  ERROR: {exc}")
                return None

def fetch_values(sheet_name: str) -> list[list] | None:
    enc = urllib.parse.quote(sheet_name)
    data = _get(f"{BASE_URL}/values/{enc}!A1:I400?key={API_KEY}")
    return data.get("values", []) if data else None

# ── cell helper ───────────────────────────────────────────────────────────────

def c(row: list, idx: int) -> str:
    if isinstance(row, list) and idx < len(row):
        v = row[idx]
        return str(v).strip() if v is not None else ""
    return ""

def find_section(rows: list, text: str) -> int | None:
    for i, row in enumerate(rows):
        if c(row, 0) == text:
            return i
    return None

# ── general ───────────────────────────────────────────────────────────────────

def parse_general(rows: list, skills_idx: int) -> dict:
    result: dict = {}
    pre = rows[:skills_idx]

    # Doll name: col A empty, col B non-empty, within first 8 rows
    for row in pre[:8]:
        a_v, b_v = c(row, 0), c(row, 1)
        if not a_v and b_v and b_v != "Unit Information":
            result["name"] = b_v
            break

    # HP/ATK/DEF header row
    for i, row in enumerate(pre):
        if c(row, 2) == "HP" and c(row, 3) == "ATK" and c(row, 4) == "DEF":
            result["class"] = c(row, 1)
            attrs, weaks = [], []
            if c(row, 6): attrs.append(c(row, 6))
            if c(row, 8): weaks.append(c(row, 8))

            if i + 1 < len(pre):
                v = pre[i + 1]
                hp, atk, df = c(v, 2), c(v, 3), c(v, 4)
                result["hp"]  = int(hp)  if hp.isdigit()  else hp
                result["atk"] = int(atk) if atk.isdigit() else atk
                result["def"] = int(df)  if df.isdigit()  else df

            if i + 2 < len(pre):
                sg = pre[i + 2]
                if c(sg, 6): attrs.append(c(sg, 6))
                if c(sg, 8): weaks.append(c(sg, 8))

            if i + 3 < len(pre):
                sgv = pre[i + 3]
                sm = re.search(r'\d+', c(sgv, 0))
                mm = re.search(r'\d+', c(sgv, 2))
                if sm: result["stabilityGauge"] = int(sm.group())
                if mm: result["movementSpeed"]  = int(mm.group())

            result["skillAttributes"] = [a for a in attrs if a]
            result["weaknesses"]      = [w for w in weaks if w]
            break

    return result

# ── skills ────────────────────────────────────────────────────────────────────

def parse_skill_cell(b_val: str) -> tuple[str, list[str]]:
    m = re.match(r'^(.*?)\n\n\((.*?)\)\s*$', b_val.strip(), re.DOTALL)
    if m:
        name   = m.group(1).strip()
        traits = [t.strip() for t in m.group(2).split('/') if t.strip()]
        return name, traits
    return b_val.strip(), []

def parse_skills(rows: list, skills_idx: int, vert_idx: int, doll_name: str) -> list:
    skills: list  = []
    cur           = None
    got_stats     = False
    got_desc      = False

    for abs_idx, row in enumerate(rows[skills_idx + 1:vert_idx], start=skills_idx + 1):
        a_v = c(row, 0)
        b_v = c(row, 1)
        h_v = c(row, 7)
        i_v = c(row, 8)

        # New skill: col B has "Name\n\n(traits)" pattern
        if b_v and "\n\n(" in b_v:
            if cur:
                skills.append(cur)
            name, traits = parse_skill_cell(b_v)
            cur = {
                "name":            name,
                "traits":          traits,
                "attribute":       i_v or None,
                "stabilityDamage": None,
                "cooldown":        None,
                "confectanceCost": None,
                "range":           None,
                "effArea":         None,
                "description":     None,
                "upgrades":        [],
                "icon":            f"assets/{doll_name}/{name}.png",
            }
            problems.append(
                f"{doll_name}: skill icon '{name}' (row {abs_idx + 1}, col A) — embedded image, cannot download"
            )
            got_stats = False
            got_desc  = False
            continue

        if cur is None:
            continue

        # Stats row
        if a_v.startswith("Stability Damage:"):
            for cell in row:
                s = str(cell).strip()
                m2 = re.search(r'Stability Damage:\s*(-?\d+)', s)
                if m2: cur["stabilityDamage"] = int(m2.group(1))
                m2 = re.search(r'Cooldown:\s*(-?\d+)', s)
                if m2: cur["cooldown"] = int(m2.group(1))
                m2 = re.search(r'Confectance Cost:\s*(-?\d+)', s)
                if m2: cur["confectanceCost"] = int(m2.group(1))
            got_stats = True
            continue

        if h_v == "Range":
            cur["range"] = i_v
            continue

        if h_v == "Eff. Area":
            cur["effArea"] = i_v
            continue

        mv = re.match(r'Vertebrae Upgrade (\d+)', a_v)
        if mv:
            cur["upgrades"].append({
                "type": "vertebrae", "number": int(mv.group(1)),
                "label": a_v, "effect": c(row, 2),
            })
            continue

        mk = re.match(r'Fixed Key (\d+)', a_v)
        if mk:
            cur["upgrades"].append({
                "type": "fixedKey", "number": int(mk.group(1)),
                "label": a_v, "effect": c(row, 2),
            })
            continue

        # Description: first non-empty col A after stats
        if got_stats and not got_desc and a_v:
            cur["description"] = a_v
            got_desc = True

    if cur:
        skills.append(cur)
    return skills

# ── vertebrae upgrade table ───────────────────────────────────────────────────

def parse_vertebrae(rows: list, vert_idx: int, helix_idx: int) -> list:
    upgrades = []
    for row in rows[vert_idx + 1:helix_idx]:
        b_v = c(row, 1)
        if not b_v or b_v in ("Vertebrae", "Icon", "Node"):
            continue
        upgrades.append({
            "upgrade": b_v,
            "skill":   c(row, 2),
            "level":   c(row, 4),
            "effect":  c(row, 5),
        })
    return upgrades

# ── neural helix ──────────────────────────────────────────────────────────────

def parse_helix(rows: list, helix_idx: int, doll_name: str) -> list:
    keys = []
    for abs_idx, row in enumerate(rows[helix_idx + 1:], start=helix_idx + 1):
        b_v = c(row, 1)
        d_v = c(row, 3)
        lv  = c(row, 2)

        if not b_v or b_v in ("Node", "Icon", "Vertebrae"):
            continue
        if b_v.startswith("Enhancement"):
            continue

        if b_v in ("Affinity Key", "Common Key"):
            key_name    = b_v
            description = d_v
        else:
            # "Fixed Key N" — description may start with "SkillName: ..."
            colon = d_v.find(":")
            if 0 < colon < 60:
                key_name    = d_v[:colon].strip()
                description = d_v[colon + 1:].strip()
            else:
                key_name    = b_v
                description = d_v

        problems.append(
            f"{doll_name}: helix key icon '{key_name}' ({b_v}, row {abs_idx + 1}, col A) — embedded image, cannot download"
        )
        keys.append({
            "node":        b_v,
            "level":       lv,
            "keyName":     key_name,
            "description": description,
            "icon":        f"assets/{doll_name}/{key_name}.png",
        })
    return keys

# ── per-tab parse ─────────────────────────────────────────────────────────────

def parse_doll(sheet_name: str, rows: list) -> dict | None:
    skills_idx = find_section(rows, "Skills")
    vert_idx   = find_section(rows, "Vertebrae Upgrade")
    helix_idx  = find_section(rows, "Neural Helix")

    if any(x is None for x in [skills_idx, vert_idx, helix_idx]):
        problems.append(
            f"{sheet_name}: MISSING SECTION — "
            f"Skills={skills_idx}, VertUpgrade={vert_idx}, NeuralHelix={helix_idx}"
        )
        return None

    general   = parse_general(rows, skills_idx)
    doll_name = general.get("name") or sheet_name.strip()

    skills    = parse_skills(rows, skills_idx, vert_idx, doll_name)
    vertebrae = parse_vertebrae(rows, vert_idx, helix_idx)
    helix     = parse_helix(rows, helix_idx, doll_name)

    return {
        "class":             general.get("class", ""),
        "stats": {
            "hp":  general.get("hp",  0),
            "atk": general.get("atk", 0),
            "def": general.get("def", 0),
        },
        "stabilityGauge":    general.get("stabilityGauge"),
        "movementSpeed":     general.get("movementSpeed"),
        "skillAttributes":   general.get("skillAttributes", []),
        "weaknesses":        general.get("weaknesses", []),
        "skills":            skills,
        "vertebraeUpgrades": vertebrae,
        "neuralHelixKeys":   helix,
    }

# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Fetching spreadsheet metadata...")
    meta      = _get(f"{BASE_URL}?key={API_KEY}&fields=sheets.properties")
    if not meta:
        print("Failed to fetch metadata — check your internet connection and API key.")
        return

    all_tabs  = [(s["properties"]["title"], s["properties"]["sheetId"])
                 for s in meta.get("sheets", [])]
    doll_tabs = [(name, sid) for name, sid in all_tabs
                 if name.strip() not in EXCLUDED_TABS]

    print(f"Found {len(doll_tabs)} doll tabs (excluding {len(all_tabs) - len(doll_tabs)} non-doll tabs)\n")

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    all_data: dict = {}

    for i, (sheet_name, _) in enumerate(doll_tabs):
        clean = sheet_name.strip()
        print(f"[{i + 1:2d}/{len(doll_tabs)}] {clean}...", end=" ", flush=True)

        rows = fetch_values(clean)
        if rows is None:
            problems.append(f"{clean}: FETCH FAILED")
            print("FAILED")
            continue

        data = parse_doll(clean, rows)
        if data is None:
            print("PARSE ERROR")
            continue

        # Determine display name (from parsed general data)
        skills_idx = find_section(rows, "Skills")
        key = clean
        if skills_idx is not None:
            for row in rows[:skills_idx][:8]:
                a_v, b_v = c(row, 0), c(row, 1)
                if not a_v and b_v and b_v != "Unit Information":
                    key = b_v
                    break

        (ASSETS_DIR / key).mkdir(parents=True, exist_ok=True)
        all_data[key] = data
        print(f"ok  ({len(data['skills'])} skills, {len(data['neuralHelixKeys'])} helix keys)")

        # Gentle rate-limiting
        if (i + 1) % 15 == 0:
            time.sleep(1)

    # ── write JS ──────────────────────────────────────────────────────────────
    print(f"\nGenerating data_info.js ({len(all_data)} dolls)...")
    js_data = json.dumps(all_data, ensure_ascii=False, indent=2)

    OUTPUT_JS.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JS.write_text(
        "/**\n"
        " * GFL2 Doll Info\n"
        f" * Source: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}\n"
        f" * Generated: {time.strftime('%Y-%m-%d')}\n"
        " *\n"
        " * Per-doll structure:\n"
        " *   class, stats{hp,atk,def}, stabilityGauge, movementSpeed,\n"
        " *   skillAttributes[], weaknesses[],\n"
        " *   skills[{name, traits[], attribute, stabilityDamage, cooldown,\n"
        " *           confectanceCost, range, effArea, description, icon,\n"
        " *           upgrades[{type, number, label, effect}]}],\n"
        " *   vertebraeUpgrades[{upgrade, skill, level, effect}],\n"
        " *   neuralHelixKeys[{node, level, keyName, description, icon}]\n"
        " */\n"
        f"const DOLL_INFO = {js_data};\n",
        encoding="utf-8",
    )
    print(f"  Written: {OUTPUT_JS}")

    # ── write problems ────────────────────────────────────────────────────────
    parse_errs = [p for p in problems if any(k in p for k in ("FETCH FAILED", "MISSING SECTION", "PARSE ERROR"))]
    img_issues = [p for p in problems if p not in parse_errs]

    PROBLEMS_F.write_text(
        f"GFL2 Extraction Problems ({len(problems)} total)\n"
        "=" * 60 + "\n\n"
        + (
            "== Parse / Fetch Errors ==\n"
            + "".join(f"  {p}\n" for p in parse_errs)
            + "\n"
            if parse_errs else ""
        )
        + f"== Image Issues ({len(img_issues)} cells — embedded, not downloadable via API) ==\n"
        + "".join(f"  {p}\n" for p in img_issues),
        encoding="utf-8",
    )
    print(f"  Problems: {PROBLEMS_F}")
    print(f"\nDone. {len(all_data)} dolls extracted.")


if __name__ == "__main__":
    main()
