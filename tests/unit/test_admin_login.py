import unittest
from flask_testing import TestCase
from moto import mock_dynamodb2
from test.support import EnvironmentVarGuard
from werkzeug.security import generate_password_hash


@mock_dynamodb2
class AdminLogin(TestCase):
    def create_app(self):

        self.env = EnvironmentVarGuard()
        self.env.set('DYNAMO_TABLE', 'test_table')
        self.env.set('AWS_REGION', 'mock-region')

        with self.env:
            from config import Config
            import context
            app = context.app.create_app(Config)
            app.config['LOGIN_DISABLED'] = False
            app.config["ADMIN_PASSWORD_HASH"] = generate_password_hash("testing-password")
            return app

    def test_redirect_to_login(self):
        response = self.client.get("/admin/")
        self.assert_redirects(response, "/admin/login?next=%2Fadmin%2F")

    def test_login(self):
        response = self.client.post('/admin/login?next=%2Fadmin%2F', data={'password': 'testing-password'})
        self.assert_redirects(response, "/admin/")

    def test_login_bad_password(self):
        response = self.client.post('/admin/login?next=%2Fadmin%2F', data={'password': 'bad-password'})
        self.assert_redirects(response, "/admin/login")


if __name__ == '__main__':
    unittest.main(verbosity=2)
