import unittest
from moto import mock_dynamodb2
from unittest.mock import patch

from parent import ParentTest
from tests.guest_helper import save_guest


@mock_dynamodb2
class TestRSVPView(ParentTest):

    @patch("flask_login.utils._get_user")
    def test_rsvp_page(self, current_user):
        guest_data = {'name': 'Add Test User', 'email': 'fake@mail.com', 'will_attend': True, 'favourite_music': 'AAA',
                      'food_allergies': 'bbbb', 'number_of_guests': 5, 'notes': 'CcCcC'}
        guest = save_guest(guest_data)
        current_user.return_value = guest

        response = self.client.get(f"/rsvp/{guest.id}")

        self.assert200(response)
        self.assert_template_used("rsvp.html")
        for value in guest_data.values():
            if type(value) is str:
                self.assertIn(value, response.data.decode("utf-8"))
            if type(value) is bool and value is True:
                self.assertIn("checked", response.data.decode("utf-8"))
            if type(value) is bool and value is False:
                self.assertNotIn("checked", response.data.decode("utf-8"))
