# Tests

Two independent test suites, covering different layers:

| Suite         | Language           | What it tests                                              |
|---------------|--------------------|--------------------------------------------------------------|
| `web/`        | Node.js (`vm`)     | The save/serialize logic in `build/js/{remold,affection,task}.js` — round-trip fidelity, mutation propagation, and the download-fallback path — without a browser. |
| `python/`     | Python (pytest + Playwright) | Real browser behavior of the module pages under `build/`, driven end-to-end and asserted against `specs/*.md`'s Acceptance Criteria. |

Both suites share the same fixture data: `web/data_affection.js`, `web/data_owner.js`,
and `web/data_remold.js` are small, deterministic stand-ins for the real `data/*.js`
files. `web/test_save.js` loads them directly; the `remold.html`/`affection.html`/
`task.html` pages load them instead of the real data when opened with `?test` in the
URL (see `docs/decisions.txt` #10) — which is exactly what `python/test_remold.py`,
`python/test_affection.py`, and `python/test_task.py` rely on to get predictable data to
assert against.

## `web/` — Node.js save-round-trip tests

- **`test_save.js`** — the runner. For each of remold/affection/task, it loads the
  module's real JS source into a Node `vm` context and asserts:
  1. round-trip fidelity: serialize → re-parse → same data as the fixture
  2. mutation propagation: an in-memory edit shows up in the serialized output
  3. the fallback download path (no `showSaveFilePicker`) writes the right filename with
     re-parseable content
- **`data_affection.js`, `data_owner.js`, `data_remold.js`** — the fixtures described above.

Requires Node.js. Run from the `gfl2_web/` project root:

```bash
node tests/web/test_save.js
```

No install step — the harness is plain Node with no dependencies.

## `python/` — Playwright acceptance tests

Spec-derived acceptance tests driving the real pages in a real (headless) browser. Each
test file maps its cases back to the "Acceptance criteria" section of the matching spec
in `specs/*.md` — see the `AC-N` references in test names/comments to trace a test back
to its requirement.

| Test file                | Spec                       | Page(s) under test                  |
|---------------------------|----------------------------|--------------------------------------|
| `test_unit.py`             | `specs/unit.md`             | `build/unit.html` (real data)        |
| `test_remold.py`           | `specs/remold.md`           | `build/remold.html?test` (fixture)   |
| `test_affection.py`        | `specs/affection.md`        | `build/affection.html?test` (fixture)|
| `test_task.py`             | `specs/task.md`              | `build/task.html?test` (fixture)     |
| `test_ui_guidelines.py`    | `specs/ui-guidelines.md`     | all module pages (structural checks) |

`unit.html` has no `?test` fixture — it always reads the real `data/master_doll.js` +
`data/data_doll.js`, so those tests derive their expected counts from the page's own
loaded globals (`DOLL_MASTER.length`, etc.) instead of hardcoding numbers, so they keep
working as the roster data changes.

`conftest.py` also disables `window.showSaveFilePicker` on every page before its scripts
run. Headless Chromium exposes that function even on `file://` origins where it can't
actually be invoked (no user gesture / insecure context), so without this the save
routines take the `if (window.showSaveFilePicker)` branch, the call silently rejects, and
the `<a download>` fallback branch — the only path this suite (or a real Firefox/`file://`
user) can automate — never runs.

### Setup

Requires Python 3.9+.

```bash
pip install pytest playwright
playwright install chromium
```

(One-time; `playwright install chromium` downloads the browser binary Playwright drives —
it's separate from any Chrome/Edge already on the machine.)

### Running

From the `gfl2_web/` project root (paths in the tests are resolved relative to it):

```bash
# whole suite
pytest tests/python

# one file
pytest tests/python/test_unit.py

# one test
pytest tests/python/test_unit.py::test_move_filter_narrows_rows_and_updates_counter

# every test whose name contains "save" (spans files)
pytest tests/python -k save

# by spec ID: every unit.md AC-N referenced in a docstring/comment as "# AC-7"
pytest tests/python -k unit -v   # narrow to one page, then eyeball -v output for the AC comment

# stop at the first failure, show print() output
pytest tests/python -x -s

# re-run only what failed last time
pytest tests/python --lf
```

Add `--headed` to watch the browser instead of running headless (useful while writing a
new test): note that flag is a `pytest-playwright` plugin option and isn't wired up here
since this suite drives Playwright directly (see `conftest.py`) — to watch a run instead,
temporarily change `p.chromium.launch()` in `conftest.py` to
`p.chromium.launch(headless=False, slow_mo=200)`.

### Adding a test

1. Add the behavior as a new `AC-N` bullet to the relevant spec's "Acceptance criteria"
   section in `specs/*.md` first — the test should trace back to a written requirement,
   not the other way around.
2. Add the test to the matching `test_*.py` file, tagged with a `# AC-N` comment.
3. Prefer deriving expected values from the page's own loaded JS globals via
   `page.evaluate(...)` over hardcoding numbers/names, so the test keeps passing as game
   data changes — reserve hardcoded values for fixture-backed tests (remold/affection/
   task, which use dedicated, stable data under `tests/web/`) or for named-entity
   behavior that's inherently data-specific (e.g. Soppo/OTs-14's multi-affinity checks in
   `test_unit.py`).

## Syntax-checking the build

Before running either suite, a quick Node syntax check catches typos in the build output
without executing anything:

```bash
node --check build/js/unit.js build/js/remold.js build/js/affection.js build/js/task.js build/js/doll.js
node --check data/master_doll.js data/master_doll_details.js data/data_doll.js \
             data/data_owner.js data/master_affection.js data/data_affection.js \
             data/master_remold.js data/data_remold.js
```

## Running everything

```bash
node tests/web/test_save.js && pytest tests/python
```
