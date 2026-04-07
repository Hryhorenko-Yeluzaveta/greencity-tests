import os
import time
import unittest

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()

BASE_URL = "https://www.greencity.cx.ua/#/greenCity/events"

class TestEventPage(unittest.TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.driver.get(BASE_URL)
        explicit_wait = WebDriverWait(self.driver, 10)

        # Precondition - Authorization
        sign_in_selector = ".header_sign-in-link.tertiary-global-button.ng-star-inserted"
        sign_in_button = explicit_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sign_in_selector)))
        sign_in_button.click()

        test_email = os.getenv("TEST_EMAIL")
        test_password = os.getenv("TEST_PASSWORD")

        email_input_id = "email"
        email_input = explicit_wait.until(EC.visibility_of_element_located((By.ID, email_input_id)))
        email_input.send_keys(test_email)

        password_input_id = "password"
        password_input = explicit_wait.until(EC.visibility_of_element_located((By.ID, password_input_id)))
        password_input.send_keys(test_password)

        submit_button_xpath = "//button[@type='submit']"
        submit_button = explicit_wait.until(EC.element_to_be_clickable((By.XPATH, submit_button_xpath)))
        submit_button.click()

        # Precondition - Go to the Events page
        explicit_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".body-2.user-name")))

        events_page_xpath = "//a[contains(@class, 'url-name') and @href='#/greenCity/events']"
        events_page_link = explicit_wait.until(EC.visibility_of_element_located((By.XPATH, events_page_xpath)))
        events_page_link.click()

    def test_bookmark_creation(self):
        explicit_wait = WebDriverWait(self.driver, 10)

        # First Step - Activate Bookmark
        event_to_bookmark_xpath = "//mat-card[.//span[@class='flag']]"
        event_to_bookmark = explicit_wait.until(EC.element_to_be_clickable((By.XPATH, event_to_bookmark_xpath)))
        event_title = event_to_bookmark.find_element(By.CSS_SELECTOR, ".event-name").text

        activate_bookmark_button = event_to_bookmark.find_element(By.XPATH, ".//div[contains(@class, 'event-flags')]")
        activate_bookmark_button.click()

        active_bookmark = activate_bookmark_button.find_element(By.CSS_SELECTOR, ".flag-active")

        self.assertTrue(active_bookmark.is_displayed(), f"Закладка не була активована на події {event_title} (не змінила свій статус на active)")

        # Second Step - Refresh the page and check bookmark status
        self.driver.refresh()

        bookmarked_event_xpath = f"//mat-card[.//span[@class='flag-active'] and .//p[contains(normalize-space(text()), '{event_title}')]]"
        bookmarked_event = explicit_wait.until(EC.visibility_of_element_located((By.XPATH, bookmarked_event_xpath)))

        self.assertTrue(bookmarked_event.is_displayed(), f"Закладка зникла з події {event_title} (після перезавантаження сторінки)")

        # Third Step - Check for an event using the bookmark filter
        bookmark_filter_xpath = "//span[@class='bookmark-img']"
        bookmark_filter_button = self.driver.find_element(By.XPATH, bookmark_filter_xpath)
        bookmark_filter_button.click()

        filtered_event_xpath = f"//mat-card[.//span[@class='flag-active'] and .//p[contains(text(), '{event_title}')]]"
        filtered_event = explicit_wait.until(EC.visibility_of_element_located((By.XPATH, filtered_event_xpath)))
        self.assertTrue(filtered_event.is_displayed(), f"Подія {event_title} не відображається при застосуванні фільтру по збереженим подіям")

        # Go back to how it was before
        deactivate_bookmark = filtered_event.find_element(By.XPATH, ".//div[contains(@class, 'event-flags')]")
        deactivate_bookmark.click()

    def tearDown(self):
        if self.driver:
            self.driver.quit()

if __name__ == '__main__':
    unittest.main()