import unittest
from moto import mock_dynamodb2

from parent import ParentTest
from tests.guest_helper import save_guest


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
        guest_id = save_guest(dict(name="Example User", email="test@example.com")).id

        response = self.client.get(f"/rsvp/{guest_id}", follow_redirects=True)

        self.assert200(response)
        self.assert_template_used("rsvp.html")
        self.assertIn("Example User", response.data.decode("utf-8"))
