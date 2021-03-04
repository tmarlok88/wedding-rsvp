from tests.e2e.parent import E2ETest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions

from tests.guest_helper import save_guest, get_guest, EXAMPLE_GUEST_1


class TestRSVP(E2ETest):
    def test_rsvp_auth(self):
        username = "E2E Test User"
        guest_id = save_guest(dict(name=username, email="test@example.com")).id

        # testuser goes to the rsvp page, but gets rejected
        self.browser.get(f"{self.get_server_url()}/rsvp")
        self.assertEqual("Not found", self.browser.title)

        # now he goes to hos special link - he is recognized and accepted
        self.browser.get(f"{self.get_server_url()}/rsvp/{guest_id}")
        self.assertEqual(f"Wedding RSVP | {username}", self.browser.title)

        # now that he has a session cookie, he gets recognized even without the user id in the URL
        self.browser.get(f"{self.get_server_url()}/rsvp")
        self.assertEqual(f"Wedding RSVP | {username}", self.browser.title)

    def test_rsvp_page(self):
        guest_data = dict(EXAMPLE_GUEST_1)
        edit_allowed = ["will_attend", "favourite_music", "food_allergies", "number_of_guests", "notes"]

        guest_id = save_guest(guest_data).id

        # testuser goes to the link he received by e-mail
        self.browser.get(f"{self.get_server_url()}/rsvp/{guest_id}")
        self.assertEqual(f"Wedding RSVP | {guest_data['name']}", self.browser.title)

        # Verifies that there is no login required message left
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn("Please log in to access this page.", page_text)

        # He finds that every value is the same as he left it last time
        for key, value in guest_data.items():
            if key in edit_allowed:
                if type(value) is str or type(value) is int:
                    self.assertEqual(str(value), self.browser.find_element_by_id(key).get_attribute("value"))
                if type(value) is bool:
                    self.assertEqual("true" if value else None,
                                     self.browser.find_element_by_id(key).get_attribute("checked"))

        # It occurs to him that he just divorced, so that the ex-wife won't come
        number_of_guests = self.browser.find_element_by_id("number_of_guests")
        number_of_guests.send_keys(Keys.BACKSPACE)
        number_of_guests.send_keys('4')
        number_of_guests.send_keys(Keys.ENTER)

        # wait for the refresh to finish
        WebDriverWait(self.browser, 5, ignored_exceptions=(NoSuchElementException,)) \
            .until(expected_conditions.staleness_of(number_of_guests))

        self.wait_for(
            lambda: self.assertEqual(self.browser.find_element_by_id("number_of_guests").get_attribute("value"), "4"))
        self.assertEqual(get_guest(guest_id).number_of_guests, 4)        # to the database as well

        # But wait! He became vegan since..
        food_allergies = WebDriverWait(self.browser, 5,
                                       ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)) \
            .until(expected_conditions.presence_of_element_located((By.ID, "food_allergies")))

        food_allergies.clear()
        food_allergies.send_keys('I a\'m vegan')
        self.browser.find_element_by_id("submit").click()

        # issue a browser refresh to make sure, the change is saved
        self.browser.get(f"{self.get_server_url()}/rsvp/{guest_id}")
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_element_by_id("food_allergies").get_attribute("value"), 'I a\'m vegan'))
        self.assertEqual(get_guest(guest_id).food_allergies, 'I a\'m vegan')        # to the database as well
