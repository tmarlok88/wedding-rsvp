import unittest
from tests.e2e.parent import E2ETest


class TestRSVP(E2ETest):
    def test_rsvp_auth(self):
        from tests.guest_helper import save_guest
        username = "E2E Test User"
        guest_id = save_guest(dict(name=username, email="test@example.com")).id

        # testuser goes to the rsvp page, but gets rejected
        self.browser.get(f"{self.get_server_url()}/rsvp")
        self.assertEqual("Unknown user", self.browser.title)

        # now he goes to hos special link - he is recognized and accepted
        self.browser.get(f"{self.get_server_url()}/rsvp/{guest_id}")
        self.assertEqual(f"Wedding RSVP | {username}", self.browser.title)

        # now that he has a session cookie, he gets recognized even without the user id in the URL
        self.browser.get(f"{self.get_server_url()}/rsvp")
        self.assertEqual(f"Wedding RSVP | {username}", self.browser.title)

    def test_rsvp_page(self):
        from tests.guest_helper import save_guest
        guest_data = {'name': 'Add Test User', 'email': 'fake@mail.com', 'will_attend': True, 'favourite_music': 'AAA',
                      'food_allergies': 'bbbb', 'number_of_guests': 5, 'notes': 'CcCcC'}

        guest_id = save_guest(guest_data).id

        # testuser goes to the link he received by e-mail
        self.browser.get(f"{self.get_server_url()}/rsvp/{guest_id}")
        self.assertEqual(f"Wedding RSVP | {guest_data['name']}", self.browser.title)

        # Verifies that there is no login required message left
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn("Please log in to access this page.", page_text)

        # He finds that every value is the same as he
        for key, value in guest_data.items():
            if type(value) is str or type(value) is int:
                self.assertEqual(str(value), self.browser.find_element_by_id(key).get_attribute("value"))
            if type(value) is bool:
                self.assertEqual("true" if value else None, self.browser.find_element_by_id(key).get_attribute("checked"))
