"""
Shared fixtures for the Playwright-driven acceptance tests under tests/python/.

Each test file maps its cases back to the "Acceptance criteria" section of the
matching spec in specs/*.md (see the AC-N references in test docstrings/comments).

See tests/README.md for setup and how to run the suite (or just one file/test).
"""

import pathlib

import pytest
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]  # gfl2_web/


def file_uri(rel_path: str) -> str:
    """Resolve a path relative to the project root to a file:// URI."""
    return (ROOT / rel_path).resolve().as_uri()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def page(browser):
    """
    A fresh page per test; fails the test if the page logs an uncaught JS error.

    Also disables window.showSaveFilePicker before any page script runs. Headless
    Chromium exposes the function even on file:// origins where it cannot actually
    be invoked (no user gesture / insecure context), so without this the save
    routines' `if (window.showSaveFilePicker)` branch is taken and silently swallows
    the rejection, never reaching the <a download> fallback branch this test suite
    (and real Firefox/file:// users) actually exercises. See docs/decisions.txt #3.
    """
    pg = browser.new_page()
    pg.add_init_script("window.showSaveFilePicker = undefined;")
    errors = []
    pg.on("pageerror", lambda exc: errors.append(str(exc)))
    yield pg
    assert not errors, f"uncaught JS errors: {errors}"
    pg.close()


@pytest.fixture
def uri():
    return file_uri
