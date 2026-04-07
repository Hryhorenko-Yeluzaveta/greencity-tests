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
        explicitWait = WebDriverWait(self.driver, 10)

        # Precondition - Authorization
        sign_in_selector = ".header_sign-in-link.tertiary-global-button.ng-star-inserted"
        sign_in_button = explicitWait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sign_in_selector)))
        sign_in_button.click()

        test_email = os.getenv("TEST_EMAIL")
        test_password = os.getenv("TEST_PASSWORD")

        email_input_id = "email"
        email_input = explicitWait.until(EC.visibility_of_element_located((By.ID, email_input_id)))
        email_input.send_keys(test_email)

        password_input_id = "password"
        password_input = explicitWait.until(EC.visibility_of_element_located((By.ID, password_input_id)))
        password_input.send_keys(test_password)

        submit_button_xpath = "//button[@type='submit']"
        submit_button = explicitWait.until(EC.element_to_be_clickable((By.XPATH, submit_button_xpath)))
        submit_button.click()

        # Precondition - Go to the Events page
        explicitWait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".body-2.user-name")))

        events_page_xpath = "//a[contains(@class, 'url-name') and @href='#/greenCity/events']"
        events_page_link = explicitWait.until(EC.visibility_of_element_located((By.XPATH, events_page_xpath)))
        events_page_link.click()

        time.sleep(5)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

if __name__ == '__main__':
    unittest.main()