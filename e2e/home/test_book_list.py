import pytest
from selenium.webdriver.common.by import By


@pytest.mark.e2e
def test_should_show_default_grid_layout(driver):
    driver.get("http://localhost:5173/")

    print(f"Current URL: {driver.current_url}")

    book_grid_element = driver.find_element(By.CSS_SELECTOR, '[data-slot="book-grid"]')
    assert book_grid_element.is_displayed()


# @pytest.mark.e2e
# def test_should_show_no_books_available(driver):
#     driver.get("http://localhost:5173/")
#
#     no_books_text_element = driver.find_element(
#         By.XPATH, "//*[text()='No books available']"
#     )
#     assert no_books_text_element.is_displayed()
