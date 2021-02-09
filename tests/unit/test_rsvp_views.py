import html
from moto import mock_dynamodb2

from parent import ParentTest
from tests.guest_helper import save_guest, EXAMPLE_GUEST_1, EXAMPLE_GUEST_2


@mock_dynamodb2
class TestRSVPLogin(ParentTest):
    def create_app(self):
        app = ParentTest.create_app(self)
        app.config['LOGIN_DISABLED'] = False
        return app

    def test_redirect_to_captcha_page(self):
        response = self.client.get("/rsvp/fake_id")
        self.assert_redirects(response, "/rsvp_captcha?next=%2Frsvp%2Ffake_id")

    def test_captcha_page(self):
        self.app.config["USE_RECAPTCHA_FOR_GUEST"] = True
        self.app.config["RECAPTCHA_PUBLIC_KEY"] = "fake_key"

        response = self.client.get("/rsvp_captcha?next=%2Frsvp%2Ffake_id")

        self.assert200(response)
        self.assert_template_used("rsvp_captcha.html")

    def test_user_not_found(self):
        response = self.client.get("/rsvp", follow_redirects=True)
        self.assert404(response)
        self.assert_template_used("errors/404.html")

    def test_existing_user_found(self):
        guest_id = save_guest(EXAMPLE_GUEST_1).id

        response = self.client.get(f"/rsvp/{guest_id}", follow_redirects=True)

        self.assert200(response)
        self.assert_template_used("rsvp.html")
        self.assertIn(EXAMPLE_GUEST_1["name"], response.data.decode("utf-8"))

    def test_rsvp_page(self):
        edit_allowed = ["will_attend", "favourite_music", "food_allergies", "number_of_guests", "notes"]

        guest = save_guest(EXAMPLE_GUEST_1)
        response = self.client.get(f"/rsvp/{guest.id}", follow_redirects=True)

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

    def test_rsvp_captcha_missing_id(self):
        self.app.config["USE_RECAPTCHA_FOR_GUEST"] = True
        self.app.config["RECAPTCHA_PUBLIC_KEY"] = "fake_key"

        response = self.client.get(f"/rsvp_captcha?next=")

        self.assert404(response)
        self.assert_template_used("errors/404.html")

    def test_different_user_id_in_session_and_url(self):
        guest = save_guest(EXAMPLE_GUEST_1)
        guest2 = save_guest(EXAMPLE_GUEST_2)
        response = self.client.get(f"/rsvp/{str(guest.id)}", follow_redirects=True)     # user logs in
        response = self.client.get(f"/rsvp")                                  # user_id from session

        self.assert200(response)
        self.assert_template_used("rsvp.html")
        self.assertIn(EXAMPLE_GUEST_1["name"], response.data.decode("utf-8"))

        response = self.client.get(f"/rsvp/{guest2.id}")
        self.assertNotIn(EXAMPLE_GUEST_2["name"], response.data.decode("utf-8"))

        self.assert404(response)
        self.assert_template_used("errors/404.html")
