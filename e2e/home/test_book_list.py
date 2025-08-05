import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@pytest.mark.e2e
def test_should_show_default_grid_layout(driver):
    driver.get("http://localhost:5173/")

    try:
        book_grid_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-slot="book-grid"]'))
        )
        assert book_grid_element.is_displayed()

    except TimeoutException:
        driver.save_screenshot("debug_screenshot.png")
        raise


# @pytest.mark.e2e
# def test_should_show_no_books_available(driver):
#     driver.get("http://localhost:5173/")
#
#     no_books_text_element = driver.find_element(
#         By.XPATH, "//*[text()='No books available']"
#     )
#     assert no_books_text_element.is_displayed()
