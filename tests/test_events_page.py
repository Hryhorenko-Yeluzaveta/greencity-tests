import os
import time
import unittest
from pathlib import Path

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

    # Search on the Events page is not working correctly (tested manually).
    # It doesn't find some events, although the name is specified the same.
    # You can try by the first letter, but even then it doesn’t always find it.
    # But I still tried to do an automated test.
    def test_search_event_by_name(self):
        explicit_wait = WebDriverWait(self.driver, 10)

        # First Step - Click on the Search icon
        search_button_xpath = "//div[contains(@class, 'container-img')][.//span[contains(@class, 'search-img')]]"
        search_button = explicit_wait.until(EC.visibility_of_element_located((By.XPATH, search_button_xpath)))
        search_button.click()

        # Second Step - Write a partial name of the event ()
        event_element_xpath = "//mat-card"
        event_element = explicit_wait.until(EC.visibility_of_element_located((By.XPATH, event_element_xpath)))
        event_name = event_element.find_element(By.CSS_SELECTOR, ".event-name").text
        partial_name = event_name[:2]

        input_event_name_xpath = "//input[@placeholder='Search']"
        input_event_name = explicit_wait.until(EC.element_to_be_clickable((By.XPATH, input_event_name_xpath)))
        input_event_name.send_keys(partial_name)

        time.sleep(2)

        all_event_names_selector = '.event-name'
        all_event_names = self.driver.find_elements(By.CSS_SELECTOR, all_event_names_selector)

        self.assertTrue(len(all_event_names) > 0, "Пошук не повернув жодного результату.")

        for name in all_event_names:
            self.assertIn(partial_name.lower(), name.text.lower(), f"Назва події {name.text} не відповідає шуканому рядку.")

        searched_element_xpath = f"//mat-card[.//p[contains(text(), '{event_name}')]]"
        partial_searched_element = self.driver.find_element(By.XPATH, searched_element_xpath)
        self.assertTrue(partial_searched_element.is_displayed(), f"Події з назвою {event_name} немає у переліку (пошук за частковою назвою).")

        # Third Step - Search by full name
        input_event_name.clear()
        input_event_name.send_keys(event_name)

        time.sleep(2)

        full_searched_element = self.driver.find_element(By.XPATH, searched_element_xpath)
        self.assertTrue(full_searched_element.is_displayed(), f"Події з назвою {event_name} немає у переліку (пошук за повною назвою)")

    def test_comment_response(self):
        explicit_wait = WebDriverWait(self.driver, 10)

        # First Step - Go to detailed information about the Event
        event_with_comment_xpath = "//mat-card[.//div[@class='frame'][.//p[text() > 0]]]"
        event_with_comment = explicit_wait.until(EC.visibility_of_element_located((By.XPATH, event_with_comment_xpath)))

        more_button_xpath = ".//button[contains(@class, 'secondary-global-button')]"
        more_button = event_with_comment.find_element(By.XPATH, more_button_xpath)
        more_button.click()

        comment_for_reply_selector = ".comment-body-wrapper.wrapper-comment"
        comment_for_reply = explicit_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, comment_for_reply_selector)))

        self.assertTrue(comment_for_reply.is_displayed(), "У цієї події немає попереднього коментаря.")

        # Second Step - Open reply section
        reply_button_xpath = ".//app-reply-comment"
        reply_button = comment_for_reply.find_element(By.XPATH, reply_button_xpath)
        reply_button.click()

        reply_input_xpath = "//div[@class='comment-textarea'][.//span[contains(text(), 'Add a reply')]]"
        reply_input = explicit_wait.until(EC.element_to_be_clickable((By.XPATH, reply_input_xpath)))
        self.assertTrue(reply_input.is_displayed(), "Поле відповіді не зʼявилося")

        reply_submit_button_xpath = "//button[contains(@class, 'primary-global-button__reply')]"
        reply_submit_button = explicit_wait.until(EC.visibility_of_element_located((By.XPATH, reply_submit_button_xpath)))
        self.assertFalse(reply_submit_button.is_enabled(), "Кнопка відправки відповіді активна (поле коментаря пусте)")

        # Third Step - Write a reply
        reply_text = "Дякую за корисну інформацію!"
        reply_input.send_keys(reply_text)
        reply_submit_button = explicit_wait.until(EC.element_to_be_clickable((By.XPATH, reply_submit_button_xpath)))
        self.assertTrue(reply_submit_button.is_enabled(), "Кнопка відправки відповіді не активна для відправки повідомлення.")

        # Fourth Step - Send reply
        reply_submit_button.click()

        time.sleep(2)

        reply_comment_xpath = ".//app-comments-list[@datatype='reply']"
        reply_comment = comment_for_reply.find_element(By.XPATH, reply_comment_xpath)

        reply_comment_text_xpath = ".//div[@class='comment-text']"
        reply_comment_text = reply_comment.find_element(By.XPATH, reply_comment_text_xpath)

        self.assertTrue(reply_comment.is_displayed(), "Відповідь на коментар не було відправлено")
        self.assertTrue(reply_comment_text.text == reply_text, "Текст не відповідає відправленому.")

    def test_image_upload(self):
        explicit_wait = WebDriverWait(self.driver, 10)

        # First Step - Go to detailed info of the Event
        more_info_button_selector = "//mat-card//button[@class='secondary-global-button m-btn']"
        more_info_button = explicit_wait.until(EC.visibility_of_element_located((By.XPATH, more_info_button_selector)))
        more_info_button.click()

        comment_section_xpath = "//app-comment-textarea"
        comment_section = explicit_wait.until(EC.visibility_of_element_located((By.XPATH, comment_section_xpath)))
        self.assertTrue(comment_section, "Блок коментарів у обраної події не знайдено")

        # Second Step - Write the comment
        input_comment_xpath = "//div[@class='comment-textarea']"
        input_comment = explicit_wait.until(EC.visibility_of_element_located((By.XPATH, input_comment_xpath)))
        input_comment.send_keys("Дивіться, які класні фотки з івенту вийшли!")

        submit_comment_button_xpath = "//button[contains(text(), 'Comment')]"
        submit_comment_button = explicit_wait.until(EC.element_to_be_clickable((By.XPATH, submit_comment_button_xpath)))
        self.assertTrue(submit_comment_button.is_enabled(), "Кнопка не стала клікабельною після введення коментаря.")

        # Third Step - Open the upload area
        image_upload_button_selector = ".image-upload-btn"
        image_upload_button = explicit_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, image_upload_button_selector)))
        image_upload_button.click()

        upload_area_xpath = "//div[@class='text-wrapper']"
        upload_area = explicit_wait.until(EC.visibility_of_element_located((By.XPATH, upload_area_xpath)))
        self.assertTrue(upload_area.is_displayed(), "Поле для завантаження зображення не зʼявилося.")

        # Fourth Step - Upload file in the wrong format
        input_file_id = "upload"
        input_file = explicit_wait.until(EC.presence_of_element_located((By.ID, input_file_id)))

        file_path = str(Path(__file__).parent / "hi.txt")
        input_file.send_keys(file_path)

        warning_background_selector = ".dropzone.warning-background"
        warning_background = explicit_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, warning_background_selector)))
        self.assertTrue(warning_background.is_displayed(), "Фон поля завантаження зображення не став червоним (попереджуючим).")

        warning_text_selector = ".warning.warning-color"
        warning_text = self.driver.find_element(By.CSS_SELECTOR, warning_text_selector)
        self.assertTrue(warning_text.is_displayed(), "Колір тексту з попередженням не змінився на червоний.")

        input_file = explicit_wait.until(EC.presence_of_element_located((By.ID, input_file_id)))
        uploaded_file_value = input_file.get_attribute("value")
        self.assertEqual(uploaded_file_value, "", "Система прийняла файл неправильного формату (.txt)!")

    def tearDown(self):
        if self.driver:
            self.driver.quit()

if __name__ == '__main__':
    unittest.main()