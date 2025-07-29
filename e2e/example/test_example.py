import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_has_hello_world_text(page: Page):
    page.goto("http://localhost:5173/")
    expect(page.locator("text=Hello world")).to_be_visible()
