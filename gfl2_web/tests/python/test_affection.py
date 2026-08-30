"""
Acceptance tests for specs/affection.md (build/affection.html + build/js/affection.js).

Uses ?test to swap in the small deterministic tests/web/data_affection.js
fixture for RAW_OWNERSHIP. Note master_affection.js (AFFILIATIONS, DOLL_AFFIL)
is NOT swapped by ?test (see docs/decisions.txt #10), so the roster iterated
by the page is still the real 13-affiliation / 44-doll list; only two of
those real dolls ("Suomi", "Groza") happen to also have fixture ownership
data, which is what AC-3/AC-4/AC-5 below key off of.
"""

import re

import pytest


@pytest.fixture
def affection_page(page, uri):
    page.goto(uri("build/affection.html") + "?test")
    page.wait_for_selector("#table-body tr")
    return page


def row_by_doll(page, name):
    return page.locator("#table-body tr", has=page.locator("td.doll-name", has_text=name))


# AC-1
def test_initial_render_shows_every_doll_grouped_by_affiliation(affection_page):
    total = affection_page.evaluate(
        "Object.values(DOLL_AFFIL).reduce((n, list) => n + list.length, 0)"
    )
    assert affection_page.locator("#table-body tr").count() == total
    assert affection_page.locator("#rowCount").text_content().strip() == f"{total} / {total}"
    # Row order follows AFFIL_ORDER / DOLL_AFFIL list order.
    first_affil = affection_page.evaluate("AFFILIATIONS[0][0]")
    first_doll = affection_page.evaluate("DOLL_AFFIL[AFFILIATIONS[0][0]][0]")
    first_row = affection_page.locator("#table-body tr").nth(0)
    assert first_row.locator("td.affiliation").text_content() == first_affil
    assert first_row.locator("td.doll-name").text_content() == first_doll


# AC-2
def test_owner_toggle_hides_column_and_last_active_is_noop(affection_page):
    gm_btn = affection_page.locator("#owner-buttons button", has_text="GM")
    gm_btn.click()  # hide GM
    assert affection_page.locator("th.owner-col", has_text="GM").count() == 0
    assert "active" not in gm_btn.get_attribute("class")

    gm_btn.click()  # show GM again
    assert affection_page.locator("th.owner-col", has_text="GM").count() == 1

    # Hide IB and FB too, leaving only GM -> clicking GM (the last one) is a no-op.
    affection_page.locator("#owner-buttons button", has_text="IB").click()
    affection_page.locator("#owner-buttons button", has_text="FB").click()
    assert affection_page.locator("th.owner-col").count() == 1
    gm_btn.click()
    assert affection_page.locator("th.owner-col").count() == 1  # still just GM


# AC-3
def test_not_owned_cell_is_dash_and_not_clickable(affection_page):
    # Fixture: Suomi has GM/IB but no FB entry.
    cell = row_by_doll(affection_page, "Suomi").locator("td.owner-cell").nth(2)  # GM,IB,FB order
    assert "not-owned" in cell.get_attribute("class")
    assert cell.text_content().strip() == "—"
    cell.click()
    assert affection_page.locator(".popover").count() == 0


# AC-4
def test_owned_cell_shows_level_and_dots_and_opens_popover(affection_page):
    cell = row_by_doll(affection_page, "Suomi").locator("td.owner-cell").nth(0)  # GM = 4
    assert "owned" in cell.get_attribute("class")
    assert "affection-4" in cell.get_attribute("class")
    assert cell.locator(".dot.filled").count() == 4

    cell.click()
    popover = affection_page.locator(".popover")
    assert popover.count() == 1
    assert "selected" in popover.locator('.popt[data-val="4"]').get_attribute("class")


# AC-5
def test_clicking_popover_level_updates_and_marks_unsaved(affection_page):
    cell = row_by_doll(affection_page, "Groza").locator("td.owner-cell").nth(1)  # IB = 4
    cell.click()
    affection_page.locator(".popover .popt", has_text="2").click()

    assert affection_page.locator(".popover").count() == 0  # closed
    assert "unsaved" in affection_page.locator("#save-btn").get_attribute("class")
    updated_cell = row_by_doll(affection_page, "Groza").locator("td.owner-cell").nth(1)
    assert "affection-2" in updated_cell.get_attribute("class")


# AC-6
def test_affiliation_filter_narrows_rows(affection_page):
    expected = affection_page.evaluate('DOLL_AFFIL["doll community"].length')
    affection_page.locator("#affil-filter").select_option("doll community")
    assert affection_page.locator("#table-body tr").count() == expected
    affils = set(affection_page.locator("#table-body td.affiliation").all_text_contents())
    assert affils == {"doll community"}


# AC-7 / AC-8
def test_affection_threshold_and_affiliation_filters_combine(affection_page):
    # doll community: Suomi (GM4, IB2), Lotta/Littara/Dushevnaya (not owned by fixture).
    affection_page.locator("#affil-filter").select_option("doll community")
    affection_page.locator("#affection-filter").select_option("3")  # 3+
    names = affection_page.locator("#table-body td.doll-name").all_text_contents()
    assert names == ["Suomi"]  # only Suomi has a visible owner at level >= 3 (GM=4)


# AC-9 / AC-10
def test_save_produces_reparseable_content_reflecting_edits(affection_page):
    cell = row_by_doll(affection_page, "Groza").locator("td.owner-cell").nth(1)  # IB
    cell.click()
    affection_page.locator(".popover .popt", has_text="1").click()

    with affection_page.expect_download() as dl_info:
        affection_page.locator("#save-btn").click()
    download = dl_info.value

    assert download.suggested_filename == "data_affection.js"
    assert "saved" in affection_page.locator("#save-btn").get_attribute("class")

    import pathlib
    content = pathlib.Path(download.path()).read_text(encoding="utf-8")
    assert "const RAW_OWNERSHIP" in content
    assert re.search(r'"Groza":\s*\{[^}]*"IB":\s*1', content)
    for name in ("Suomi", "Nagant M1895", "Groza", "AN-94"):
        assert f'"{name}":' in content  # all fixture dolls preserved by round-trip
