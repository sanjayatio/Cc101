"""
Conformance checks for specs/ui-guidelines.md's Acceptance criteria checklist.

These are structural checks across all module pages rather than page-specific
behavior (that's covered by test_unit.py / test_remold.py / test_affection.py /
test_task.py), so they're kept light: static markup checks plus one live-page
check that the module pages that use a row counter update it correctly.
"""

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"

MODULE_PAGES = ["unit.html", "remold.html", "affection.html", "task.html", "doll.html"]

# Pages with a filterable/browsable table and #rowCount badge (AC-3).
PAGES_WITH_ROW_COUNTER = ["unit.html", "remold.html", "affection.html"]


def html_source(name):
    return (BUILD / name).read_text(encoding="utf-8")


# AC-1
@pytest.mark.parametrize("name", MODULE_PAGES)
def test_base_css_loaded_before_page_css(name):
    src = html_source(name)
    base_idx = src.index('css/_base.css')
    own_css = re.search(r'href="css/(?!_base)([\w-]+)\.css"', src)
    assert own_css, f"{name} should link its own css/<page>.css"
    assert base_idx < src.index(own_css.group(0))


# AC-2
@pytest.mark.parametrize("name", MODULE_PAGES)
def test_data_scripts_declared_before_module_script(name):
    src = html_source(name)
    module_script = re.search(r'<script src="js/[\w-]+\.js"( defer)?>', src)
    assert module_script, f"{name} should load its own js/<page>.js"
    is_deferred = module_script.group(1) is not None

    data_script_positions = [m.start() for m in re.finditer(r'<script src="\.\./data/', src)]
    if data_script_positions:
        if is_deferred:
            # defer guarantees execution order regardless of position, but by
            # convention data scripts are still declared earlier in the file.
            assert all(pos < module_script.start() for pos in data_script_positions)
        else:
            assert all(pos < module_script.start() for pos in data_script_positions)


# AC-3 (static): row-counter pages have the badge in markup
@pytest.mark.parametrize("name", PAGES_WITH_ROW_COUNTER)
def test_row_counter_badge_present_in_markup(name):
    assert 'id="rowCount"' in html_source(name)


# AC-3 (live): the badge actually updates on a filter interaction
def test_row_counter_updates_live_on_unit_page(page, uri):
    page.goto(uri("build/unit.html"))
    page.wait_for_selector(".units-table tbody tr")
    before = page.locator("#rowCount").text_content()
    page.locator("#move-buttons .filter-btn").first.click()
    after = page.locator("#rowCount").text_content()
    assert before != after


# AC-4: save-enabled pages share the same unsaved/saved button lifecycle
@pytest.mark.parametrize("name", ["remold.html", "affection.html", "task.html"])
def test_save_button_lifecycle_classes_present(name):
    src = html_source(name)
    assert 'class="save-btn"' in src
    assert 'id="save-status"' in src
    css = (BUILD / "css" / "_base.css").read_text(encoding="utf-8")
    assert ".save-btn.unsaved" in css or ".unsaved" in css
    assert ".save-btn.saved" in css or ".saved" in css


# AC-5: save routine shape — showSaveFilePicker with a bare suggestedName, and
# a <a download> fallback with the same bare filename.
@pytest.mark.parametrize(
    "js_file,data_filename",
    [("remold.js", "data_remold.js"), ("affection.js", "data_affection.js"), ("task.js", "data_owner.js")],
)
def test_save_routine_shape(js_file, data_filename):
    src = (BUILD / "js" / js_file).read_text(encoding="utf-8")
    assert "showSaveFilePicker" in src
    assert f'suggestedName: "{data_filename}"' in src or f"suggestedName: '{data_filename}'" in src
    assert f'a.download = "{data_filename}"' in src or f"a.download = '{data_filename}'" in src
    assert "AbortError" in src
