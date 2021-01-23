import unittest
from tests.e2e.parent import E2ETest


class TestRSVP(E2ETest):
    def test_rsvp_page(self):
        from tests.guest_helper import save_guest
        username = "E2E Test User"
        guest_id = save_guest(dict(name=username, email="test@example.com"))

        # testuser goes to the rsvp page, but gets rejected
        self.browser.get(f"{self.get_server_url()}/rsvp")
        self.assertEqual("Unknown user", self.browser.title)

        # now he goes to hos special link - he is recognized and accepted
        self.browser.get(f"{self.get_server_url()}/rsvp/{guest_id}")
        self.assertEqual(f"Wedding RSVP | {username}", self.browser.title)

        # now that he has a session cookie, he gets recognized even without the user id in the URL
        self.browser.get(f"{self.get_server_url()}/rsvp")
        self.assertEqual(f"Wedding RSVP | {username}", self.browser.title)


if __name__ == '__main__':
    unittest.main()
