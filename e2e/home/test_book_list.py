import pytest
from selenium.webdriver.common.by import By


@pytest.mark.e2e
def test_should_show_default_grid_layout(driver):
    driver.get("http://localhost:5173/")

    # Debug: print page source to see what's actually rendered
    print(f"Page title: {driver.title}")
    print(f"Current URL: {driver.current_url}")

    # Wait a bit for the page to load
    import time

    time.sleep(2)

    # Try to find the element and print helpful debug info if not found
    try:
        book_grid_element = driver.find_element(
            By.CSS_SELECTOR, '[data-slot="book-grid"]'
        )
        assert book_grid_element.is_displayed()
    except Exception as e:
        # Print page source to help debug
        print(f"Error finding book-grid element: {e}")
        print(f"Page source preview (first 1000 chars):\n{driver.page_source[:1000]}")
        raise


# @pytest.mark.e2e
# def test_should_show_no_books_available(driver):
#     driver.get("http://localhost:5173/")
#
#     no_books_text_element = driver.find_element(
#         By.XPATH, "//*[text()='No books available']"
#     )
#     assert no_books_text_element.is_displayed()
