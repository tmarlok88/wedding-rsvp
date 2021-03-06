from tests.e2e.parent import E2ETest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions

from tests.guest_helper import save_guest


class TestRSVP(E2ETest):
    def test_login_to_admin_after_guest(self):
        username = "E2E Test User"
        guest_id = save_guest(dict(name=username, email="test@example.com")).id

        # Admin visits it's owwn guest page
        self.browser.get(f"{self.get_server_url()}/rsvp/{guest_id}")
        self.assertEqual(f"Wedding RSVP | {username}", self.browser.title)

        # now that he has a session cookie, he gets recognized even without the user id in the URL
        self.browser.get(f"{self.get_server_url()}/rsvp")
        self.assertEqual(f"Wedding RSVP | {username}", self.browser.title)

        # He want's to login to the admin page
        self.browser.get(f"{self.get_server_url()}/admin")
        password_field = self.browser.find_element_by_id("password")
        password_field.send_keys(Keys.BACKSPACE)
        password_field.send_keys('password')
        password_field.send_keys(Keys.ENTER)

        # He is redirected to the admin page
        WebDriverWait(self.browser, 5, ignored_exceptions=(NoSuchElementException,)) \
            .until(expected_conditions.staleness_of(password_field))

        self.assertEqual("Admin page", self.browser.title)

        # He goes to the Guest list page
        link = self.browser.find_element_by_link_text('Guest list')
        link.click()

        WebDriverWait(self.browser, 5, ignored_exceptions=(NoSuchElementException,)) \
            .until(expected_conditions.staleness_of(password_field))

        self.assertEqual("Guest list", self.browser.title)
