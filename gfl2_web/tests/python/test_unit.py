"""
Acceptance tests for specs/unit.md (build/unit.html + build/js/unit.js).

Loads the real data/master_doll.js + data/data_doll.js (no ?test fixture exists
for this read-only page), and uses the page's own loaded globals (DOLL_MASTER,
DOLL_DATA) as the source of truth for expected counts, so these tests keep
working as the roster data changes.
"""

import pytest


@pytest.fixture
def unit_page(page, uri):
    page.goto(uri("build/unit.html"))
    page.wait_for_selector(".units-table tbody tr")
    return page


def row_count_text(page):
    return page.locator("#rowCount").text_content().strip()


def visible_rows(page):
    return page.locator(".units-table tbody tr:not(.hidden)")


# AC-1
def test_initial_render_shows_every_doll(unit_page):
    total = unit_page.evaluate("DOLL_MASTER.length")
    assert unit_page.locator(".units-table tbody tr").count() == total
    assert row_count_text(unit_page) == f"{total} / {total}"


# AC-2
def test_missing_ownership_renders_dash(unit_page):
    # Use the page's own data as the oracle: find a doll/owner pair with no
    # DOLL_DATA entry, then assert that owner's V cell renders "-".
    result = unit_page.evaluate(
        """
        () => {
          for (const d of DOLL_MASTER) {
            const name = d[5];
            const own = DOLL_DATA[name];
            for (const owner of ['GM', 'IB', 'FB']) {
              if (!own || !(owner in own)) return { name, owner };
            }
          }
          return null;
        }
        """
    )
    assert result is not None, "expected at least one doll with a missing owner entry"
    col = {"GM": 4, "IB": 7, "FB": 10}[result["owner"]]  # 1-indexed nth-child for V col
    row = unit_page.locator(".units-table tbody tr", has=unit_page.locator("td:nth-child(2)", has_text=result["name"]))
    assert row.locator("td").nth(col - 1).text_content().strip() == "-"


# AC-3
def test_dual_and_all_affinity_dolls_show_every_emoji(unit_page):
    def affinity_cell(name):
        row = unit_page.locator(".units-table tbody tr", has=unit_page.locator("td:nth-child(2)", has_text=name))
        return row.locator("td").nth(12).text_content()

    soppo = affinity_cell("Soppo")
    assert "❄" in soppo and "\U0001F525" in soppo  # ❄ and 🔥

    ots14 = affinity_cell("OTs-14")
    for emoji in ("☕", "❄", "\U0001F4A7", "\U0001F525", "⚡"):  # ☕❄💧🔥⚡
        assert emoji in ots14
    assert "\U0001F9BE" not in ots14  # 🦾 Physical must NOT be listed


# AC-4
def test_affinity_filter_buttons_are_individual_emoji(unit_page):
    expected = unit_page.evaluate(
        "() => new Set(DOLL_MASTER.flatMap(d => [].concat(d[2]))).size"
    )
    buttons = unit_page.locator("#affinity-buttons .filter-btn")
    assert buttons.count() == expected
    texts = buttons.all_text_contents()
    assert "❄" in texts and "\U0001F525" in texts  # separate ❄ and 🔥 buttons
    assert "❄\U0001F525" not in texts  # never combined into one button


# AC-5
def test_burn_filter_includes_dual_affinity_soppo(unit_page):
    unit_page.locator("#affinity-buttons .filter-btn", has_text="\U0001F525").click()
    names = visible_rows(unit_page).locator("td:nth-child(2)").all_text_contents()
    assert "Soppo" in names


# AC-6
def test_move_filter_buttons_sort_numerically(unit_page):
    labels = unit_page.locator("#move-buttons .filter-btn").all_text_contents()
    assert labels == sorted(labels, key=int)


# AC-7
def test_move_filter_narrows_rows_and_updates_counter(unit_page):
    total = unit_page.evaluate("DOLL_MASTER.length")
    value = unit_page.locator("#move-buttons .filter-btn").first.text_content()
    expected = unit_page.evaluate(f"DOLL_MASTER.filter(d => String(d[0]) === '{value}').length")

    unit_page.locator("#move-buttons .filter-btn", has_text=value).click()
    assert visible_rows(unit_page).count() == expected
    assert row_count_text(unit_page) == f"{expected} / {total}"


# AC-8
def test_filters_or_within_group_and_across_groups(unit_page):
    move_values = unit_page.locator("#move-buttons .filter-btn").all_text_contents()[:2]
    for v in move_values:
        unit_page.locator("#move-buttons .filter-btn", has_text=v).click()

    or_expected = unit_page.evaluate(
        f"DOLL_MASTER.filter(d => {move_values}.includes(String(d[0]))).length"
    )
    assert visible_rows(unit_page).count() == or_expected

    # AND across groups: further restrict by an affinity value.
    unit_page.locator("#affinity-buttons .filter-btn", has_text="\U0001F525").click()
    and_expected = unit_page.evaluate(
        f"""
        DOLL_MASTER.filter(d =>
          {move_values}.includes(String(d[0])) &&
          [].concat(d[2]).includes('\U0001F525')
        ).length
        """
    )
    assert visible_rows(unit_page).count() == and_expected


# AC-9
def test_hide_dash_combines_with_emoji_filters(unit_page):
    unit_page.locator('[onclick="toggleHideDash(3, this)"]').click()  # hide GM dashes
    for row in visible_rows(unit_page).all():
        assert row.locator("td").nth(3).text_content().strip() != "-"


# AC-10
def test_clear_resets_everything(unit_page):
    total = unit_page.evaluate("DOLL_MASTER.length")
    unit_page.locator("#move-buttons .filter-btn").first.click()
    unit_page.locator('[onclick="toggleHideDash(3, this)"]').click()

    unit_page.locator(".clear-btn").click()

    assert unit_page.locator(".filter-btn.active").count() == 0
    assert visible_rows(unit_page).count() == total
    assert row_count_text(unit_page) == f"{total} / {total}"
