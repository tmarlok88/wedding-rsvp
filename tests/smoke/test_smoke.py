import unittest
import requests
import os


class SmokeTests(unittest.TestCase):

    def test_admin_endpoint(self):
        self.assertEqual(requests.get(f'{os.getenv("WEB_URL")}/admin').status_code, 200)

    def test_rsvp_endpoint(self):
        self.assertEqual(requests.get(f'{os.getenv("WEB_URL")}/rsvp').status_code, 404)


if __name__ == '__main__':
    unittest.main()
