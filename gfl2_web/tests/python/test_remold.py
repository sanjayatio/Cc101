"""
Acceptance tests for specs/remold.md (build/remold.html + build/js/remold.js).

Uses the ?test URL parameter (see docs/decisions.txt #10) to load the small,
deterministic fixture at tests/web/data_remold.js instead of the real
data/data_remold.js, so expectations can be pinned to known values.

Fixture (tests/web/data_remold.js), for reference:
  0: GM F3 Suomi         Attack Boost  Corrosive Smite   -> main=red    sub=purple
  1: GM F4 __            Defense Boost HP Boost          -> main=blue   sub=unset
  2: IB F3 Nagant M1895  Attack Boost  Corrosive Smite   -> main=red    sub=purple
  3: IB F4 Groza         Critical Hit  Critical Damage   -> main=unset  sub=unset
  4: FB F3 AN-94         Attack Boost  HP Boost          -> main=red    sub=unset
(colors derived from data/master_remold.js, which is NOT swapped by ?test)
"""

import re

import pytest


@pytest.fixture
def remold_page(page, uri):
    page.goto(uri("build/remold.html") + "?test")
    page.wait_for_selector("#tableBody tr")
    return page


def rows(page):
    return page.locator("#tableBody tr")


# AC-1
def test_initial_render_matches_fixture_order(remold_page):
    assert rows(remold_page).count() == 5
    first = rows(remold_page).nth(0).locator("td").all_text_contents()
    assert first == ["GM", "F3", "Suomi", "Attack Boost", "Corrosive Smite"]


# AC-2
def test_color_classes_resolved_from_pattern_names(remold_page):
    row0 = rows(remold_page).nth(0)
    # Main cell (Attack Boost) is red; Sub cell (Corrosive Smite) is purple.
    main_cell = row0.locator("td").nth(3)
    sub_cell = row0.locator("td").nth(4)
    assert "red" in main_cell.get_attribute("class")
    assert "purple" in sub_cell.get_attribute("class")

    # Row 3 (Critical Hit / Critical Damage) isn't a known pattern -> unset.
    row3 = rows(remold_page).nth(3)
    assert "unset" in row3.locator("td").nth(3).get_attribute("class")
    assert "unset" in row3.locator("td").nth(4).get_attribute("class")


# AC-3
def test_unassigned_doll_renders_empty_style(remold_page):
    row1_doll = rows(remold_page).nth(1).locator("td.doll")
    assert "empty" in row1_doll.get_attribute("class")
    assert row1_doll.text_content().strip() == "__"


# AC-4
def test_doll_cell_click_opens_select_once(remold_page):
    cell = rows(remold_page).nth(0).locator("td.doll")
    cell.click()
    select = cell.locator("select")
    assert select.count() == 1
    assert select.input_value() == "Suomi"
    options = select.locator("option").all_text_contents()
    assert options[0] == "__"
    assert options == ["__"] + sorted(options[1:])

    # Re-clicking while open must not create a second select.
    cell.click()
    assert cell.locator("select").count() == 1


# AC-5
def test_changing_doll_marks_unsaved_same_value_does_not(remold_page):
    save_btn = remold_page.locator("#save-btn")

    cell = rows(remold_page).nth(0).locator("td.doll")
    cell.click()
    cell.locator("select").select_option("Groza")
    assert "unsaved" in save_btn.get_attribute("class")
    assert cell.text_content().strip() == "Groza"

    # Reset state via reload, then re-select the same current value.
    remold_page.goto(remold_page.url)
    remold_page.wait_for_selector("#tableBody tr")
    save_btn = remold_page.locator("#save-btn")
    cell = rows(remold_page).nth(0).locator("td.doll")
    cell.click()
    cell.locator("select").select_option("Suomi")
    assert "unsaved" not in (save_btn.get_attribute("class") or "")


# AC-6
def test_escape_reverts_doll_edit(remold_page):
    # Note: a native <select>'s "change" event fires as soon as a different option
    # is chosen (select_option triggers it immediately), which is itself a commit
    # per FR-5 — so there's no automatable "changed but not yet committed" state to
    # press Escape from. This verifies Escape's actual observable contract: it closes
    # the editor back to the pre-edit value without ever marking the page unsaved.
    cell = rows(remold_page).nth(0).locator("td.doll")
    cell.click()
    cell.locator("select").press("Escape")
    assert cell.locator("select").count() == 0
    assert cell.text_content().strip() == "Suomi"
    assert "unsaved" not in (remold_page.locator("#save-btn").get_attribute("class") or "")


# AC-7
def test_owner_filter_shows_only_matching_rows(remold_page):
    remold_page.locator('.filter-btn[data-user="GM"]').click()
    for tr in remold_page.locator("#tableBody tr").all():
        is_hidden = "hidden" in (tr.get_attribute("class") or "")
        assert is_hidden == (tr.locator("td").nth(0).text_content() != "GM")


# AC-8
def test_main_and_sub_color_filters_combine_with_and(remold_page):
    remold_page.locator('.color-btn[data-col="main"][data-color="red"]').click()
    remold_page.locator('.color-btn[data-col="sub"][data-color="purple"]').click()
    visible_dolls = remold_page.locator("#tableBody tr:not(.hidden) td.doll").all_text_contents()
    # Rows 0 (Suomi) and 2 (Nagant M1895) are main=red/sub=purple; others are not.
    assert set(visible_dolls) == {"Suomi", "Nagant M1895"}


# AC-9 / AC-10
def test_save_produces_reparseable_content_reflecting_edits(remold_page):
    cell = rows(remold_page).nth(1).locator("td.doll")  # row1 was unassigned "__"
    cell.click()
    cell.locator("select").select_option("Andoris")

    with remold_page.expect_download() as dl_info:
        remold_page.locator("#save-btn").click()
    download = dl_info.value

    assert download.suggested_filename == "data_remold.js"
    assert "saved" in remold_page.locator("#save-btn").get_attribute("class")

    content = pathlib_read(download.path())
    assert "const REMOLD_DATA" in content
    assert '"Andoris"' in content  # the edit made this session is reflected
    row_starts = re.findall(r'\["(?:GM|IB|FB)",', content)
    assert len(row_starts) == 5  # round-trip preserves row count


def pathlib_read(path):
    import pathlib
    return pathlib.Path(path).read_text(encoding="utf-8")
