import mock
import os
from moto import mock_dynamodb2

from parent import ParentTest

from tests.guest_helper import save_guest, EXAMPLE_GUEST_1, EXAMPLE_GUEST_2, clear_all_guests


@mock.patch.dict(os.environ, {"SENDER_SMTP_SERVER": "fake.mail.domain", "SENDER_EMAIL_ADDRESS": "sender@example.com",
                              'SENDER_EMAIL_PASSWORD': 'testpass'})
@mock_dynamodb2
@mock.patch("smtplib.SMTP_SSL", create=False)
class TestAdminSendMail(ParentTest):
    def create_app(self):
        app = ParentTest.create_app(self)
        from app.model.Guest import Guest
        Guest.create_table()
        return app

    def setUp(self) -> None:
        self.guest1 = save_guest(EXAMPLE_GUEST_1)
        self.guest2 = save_guest(EXAMPLE_GUEST_2)

    def tearDown(self) -> None:
        clear_all_guests()

    def test_email_sender_page(self, mock_sendmail):
        response = self.client.get("/admin/email_sender")
        self.assertIn("Send mail", response.data.decode("utf-8"))
        self.assert_template_used("email_sender.html")

    def test_email_sender_page_recipient_list(self, mock_sendmail):
        response = self.client.get("/admin/email_sender")

        self.assertIn("Send to all", response.data.decode("utf-8"))
        self.assertIn(EXAMPLE_GUEST_1["name"], response.data.decode("utf-8"))
        self.assertIn(str(self.guest1.id), response.data.decode("utf-8"))
        self.assertIn(EXAMPLE_GUEST_2["name"], response.data.decode("utf-8"))
        self.assertIn(str(self.guest2.id), response.data.decode("utf-8"))

    def test_email_sender_send_mail_fail(self, mock_sendmail):
        import smtplib
        instance = mock_sendmail.return_value
        instance.sendmail.side_effect = smtplib.SMTPRecipientsRefused({})
        with mock.patch.dict(os.environ, {"AWS_REGION": "eu-central-1", "SENDER_EMAIL_ADDRESS": "fake@example.com"}):
            response = self.client.post('/admin/email_sender', data={'recipients': [self.guest1.id],
                                                                     'subject': 'Test message', 'body': 'message body'})
        self.assert200(response)
        self.assert_message_flashed("1 E-mails couldn't be sent", "warning")

    def test_email_sender_send_mail_success(self, mock_sendmail):
        response = self.client.post('/admin/email_sender', data={'recipients': [self.guest1.id],
                                                                 'subject': 'Test message', 'body': 'message body'})
        self.assert200(response)
        self.assert_message_flashed("1 E-mails sent successfully", "success")

    def test_email_sender_send_to_all(self, mock_sendmail):
        response = self.client.post('/admin/email_sender', data={'recipients': ["all"],
                                                                 'subject': 'Test message', 'body': 'message body'})
        self.assert200(response)
        self.assert_message_flashed("2 E-mails sent successfully", "success")
