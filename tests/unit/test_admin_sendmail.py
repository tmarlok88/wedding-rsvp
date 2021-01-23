import unittest
import mock
import os
from moto import mock_dynamodb2, mock_ses

from parent import ParentTest

from tests.guest_helper import save_guest


@mock.patch.dict(os.environ, {"AWS_REGION": "eu-central-1", "SENDER_EMAIL_ADDRESS": "sender@example.com"})
@mock_dynamodb2
@mock_ses
class TestAdminSendMail(ParentTest):
    def create_app(self):
        app = ParentTest.create_app(self)
        from app.model.Guest import Guest
        Guest.create_table()
        return app

    def test_email_sender_page(self):
        response = self.client.get("/admin/email_sender")
        self.assertIn("Send mail", response.data.decode("utf-8"))
        self.assert_template_used("email_sender.html")

    def test_email_sender_page_recipient_list(self):
        save_guest(dict(name="List Test User", email="test@example.com"))
        save_guest(dict(name="Another user", email="anothertest@some.domain"))

        response = self.client.get("/admin/email_sender")

        self.assertIn("List Test User", response.data.decode("utf-8"))
        self.assertIn("test@example.com", response.data.decode("utf-8"))
        self.assertIn("Another user", response.data.decode("utf-8"))
        self.assertIn("anothertest@some.domain", response.data.decode("utf-8"))

    def test_email_sender_send_mail_fail(self):
        with mock.patch.dict(os.environ, {"AWS_REGION": "eu-central-1", "SENDER_EMAIL_ADDRESS": "fake@example.com"}):
            response = self.client.post('/admin/email_sender', data={'recipients': ['test@example.com'],
                                                                 'subject': 'Test message', 'body': 'message body'})
        self.assert200(response)
        self.assert_message_flashed("E-mails couldn't be sent")

    def test_email_sender_send_mail_success(self):
        import boto3
        ses_client = boto3.client('ses', region_name="mock-region")
        ses_client.verify_email_identity(EmailAddress='sender@example.com')
        response = self.client.post('/admin/email_sender', data={'recipients': ['test@example.com'],
                                                                 'subject': 'Test message', 'body': 'message body'})
        self.assert200(response)
        self.assert_message_flashed("E-mails sent successfully")


if __name__ == '__main__':
    unittest.main(verbosity=2)
