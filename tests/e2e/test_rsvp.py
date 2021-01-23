import unittest
from tests.e2e.parent import E2ETest


class TestRSVP(E2ETest):
    def test_rsvp_page(self):
        from tests.guest_helper import save_guest
        guest_id = save_guest(dict(name="E2E Test User", email="test@example.com"))
        self.browser.get(f"{self.get_server_url()}/rsvp/{guest_id}")
        assert 'Wedding RSVP' in self.browser.title


if __name__ == '__main__':
    unittest.main()
