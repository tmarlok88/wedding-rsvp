import unittest
from werkzeug.security import generate_password_hash
from moto import mock_dynamodb2

from parent import ParentTest


@mock_dynamodb2
class TestAdminLogin(ParentTest):
    def create_app(self):
        app = ParentTest.create_app(self)
        app.config['LOGIN_DISABLED'] = False
        app.config["ADMIN_PASSWORD_HASH"] = generate_password_hash("testing-password")
        return app

    def test_redirect_to_login(self):
        response = self.client.get("/admin/")
        self.assert_redirects(response, "/admin/login?next=%2Fadmin%2F")

    def test_login_page(self):
        response = self.client.get("/admin/login")
        self.assertIn("Login", response.data.decode("utf-8"))
        self.assert_template_used("login.html")

    def test_login(self):
        response = self.client.post('/admin/login?next=%2Fadmin%2F', data={'password': 'testing-password'})
        self.assert_redirects(response, "/admin/")

    def test_login_bad_password(self):
        response = self.client.post('/admin/login?next=%2Fadmin%2F', data={'password': 'bad-password'})
        self.assert_redirects(response, "/admin/login")
