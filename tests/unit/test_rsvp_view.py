import html
from moto import mock_dynamodb2
from unittest.mock import patch

from parent import ParentTest
from tests.guest_helper import save_guest, EXAMPLE_GUEST_1


@mock_dynamodb2
class TestRSVPView(ParentTest):

    @patch("flask_login.utils._get_user")
    def test_rsvp_page(self, current_user):
        edit_allowed = ["will_attend", "favourite_music", "food_allergies", "number_of_guests", "notes"]

        guest = save_guest(EXAMPLE_GUEST_1)
        current_user.return_value = guest

        response = self.client.get(f"/rsvp/{guest.id}")

        self.assert200(response)
        self.assert_template_used("rsvp.html")
        for key, value in EXAMPLE_GUEST_1.items():
            if key in edit_allowed:
                if type(value) is str:
                    self.assertIn(value, html.unescape(response.data.decode("utf-8")))
                if type(value) is bool and value is True:
                    self.assertIn("checked", response.data.decode("utf-8"))
                if type(value) is bool and value is False:
                    self.assertNotIn("checked", response.data.decode("utf-8"))
