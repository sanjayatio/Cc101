"""
Acceptance tests for specs/task.md (build/task.html + build/js/task.js).

Uses ?test to load the small deterministic tests/web/data_owner.js fixture:
  DATA_OWNER:      [1,"GM",...], [2,"IB",...]
  DATA_TASK_DAILY: ["Daily Login",{1:5,2:3}], ["Resource Run",{1:2,2:2}]
  DATA_TASK_TIMED: ["Event Quest A","2025-12-31",{1:1,2:0}]
"""

import re

import pytest


@pytest.fixture
def task_page(page, uri):
    page.goto(uri("build/task.html") + "?test")
    page.wait_for_selector("#table-body tr")
    return page


def data_rows(page):
    return page.locator("#table-body tr:not(.section-header)")


# AC-1 / AC-2
def test_header_and_sections_match_fixture(task_page):
    headers = task_page.locator("#table-head th").all_text_contents()
    assert headers == ["Task", "Due Date", "GM", "IB"]

    section_labels = task_page.locator("#table-body tr.section-header").all_text_contents()
    assert section_labels == ["Daily", "Timed"]

    rows = data_rows(task_page)
    assert rows.count() == 3  # 2 daily + 1 timed
    assert rows.nth(0).locator("td").nth(0).text_content() == "Daily Login"
    assert rows.nth(0).locator("td.due-date").text_content().strip() == "—"
    assert rows.nth(0).locator("td.count-cell").nth(0).text_content().strip() == "5"
    assert rows.nth(0).locator("td.count-cell").nth(1).text_content().strip() == "3"

    timed = rows.nth(2)
    assert timed.locator("td").nth(0).text_content() == "Event Quest A"
    assert timed.locator("td.due-date").text_content().strip() == "2025-12-31"
    assert timed.locator("td.count-cell").nth(1).text_content().strip() == "0"


# AC-3
def test_count_cell_click_opens_single_input(task_page):
    cell = data_rows(task_page).nth(0).locator("td.count-cell").nth(0)
    cell.click()
    assert cell.locator("input[type=number]").count() == 1
    assert cell.locator("input").input_value() == "5"
    cell.click()  # re-click while open
    assert cell.locator("input").count() == 1


# AC-4
def test_commit_updates_value_and_marks_unsaved_only_on_change(task_page):
    save_btn = task_page.locator("#save-btn")
    cell = data_rows(task_page).nth(0).locator("td.count-cell").nth(0)
    cell.click()
    cell.locator("input").fill("9")
    cell.locator("input").press("Enter")
    assert cell.text_content().strip() == "9"
    assert "unsaved" in save_btn.get_attribute("class")

    task_page.goto(task_page.url)
    task_page.wait_for_selector("#table-body tr")
    save_btn = task_page.locator("#save-btn")
    cell = data_rows(task_page).nth(0).locator("td.count-cell").nth(0)
    cell.click()
    cell.locator("input").fill("5")  # same as original
    cell.locator("input").press("Enter")
    assert "unsaved" not in (save_btn.get_attribute("class") or "")


# AC-5
def test_invalid_input_falls_back_to_previous_value(task_page):
    cell = data_rows(task_page).nth(0).locator("td.count-cell").nth(0)
    cell.click()
    cell.locator("input").fill("-3")
    cell.locator("input").press("Enter")
    assert cell.text_content().strip() == "5"
    assert "unsaved" not in (task_page.locator("#save-btn").get_attribute("class") or "")


# AC-6
def test_escape_reverts_and_commits_original_value(task_page):
    cell = data_rows(task_page).nth(0).locator("td.count-cell").nth(0)
    cell.click()
    cell.locator("input").fill("42")
    cell.locator("input").press("Escape")
    assert cell.text_content().strip() == "5"
    assert "unsaved" not in (task_page.locator("#save-btn").get_attribute("class") or "")


# AC-7 / AC-8
def test_save_produces_reparseable_content_reflecting_edits(task_page):
    cell = data_rows(task_page).nth(0).locator("td.count-cell").nth(0)
    cell.click()
    cell.locator("input").fill("11")
    cell.locator("input").press("Enter")

    with task_page.expect_download() as dl_info:
        task_page.locator("#save-btn").click()
    download = dl_info.value

    assert download.suggested_filename == "data_owner.js"
    assert "saved" in task_page.locator("#save-btn").get_attribute("class")

    import pathlib
    content = pathlib.Path(download.path()).read_text(encoding="utf-8")
    assert "const DATA_OWNER" in content
    assert "const DATA_TASK_DAILY" in content
    assert "const DATA_TASK_TIMED" in content
    assert "DATA_RESOURCES" not in content  # known gap: never re-emitted (see specs/task.md)
    assert re.search(r'"Daily Login",\s*\{1:11', content)
