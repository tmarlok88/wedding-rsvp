import base64
import binascii
from unittest import TestCase, mock

from tests import context
from tests.guest_helper import EXAMPLE_GUEST_1


@mock.patch("smtplib.SMTP_SSL")
class EmailSenderTest(TestCase):
    def test_send_email(self, client_mock):
        sender = context.app.services.EmailSender.EmailSender('some.fake.address', 'fake@sender.address', 'testuser',
                                                              'testpass')
        sendmail = sender.send_email('recipient1@address.com', "Test email", "Mail body")
        self.assertTrue(sendmail)

    def test_send_emails(self, client_mock):
        test_guest = context.app.model.Guest.Guest(**EXAMPLE_GUEST_1)

        footer = "rsvp: https://test.tld/rsvp/{id}\nunsubscribe: https://test.tld/rsvp/unsubscribe/{id}"
        expected_body = f'Mail body {test_guest.name}\n---\n'+footer.format(**test_guest.attribute_values)

        sender = context.app.services.EmailSender.EmailSender('some.fake.address', 'fake@sender.address', 'testuser',
                                                              'testpass', footer_template=footer)
        sendmail = sender.send_emails([test_guest], "Test email", "Mail body {name}")

        self.assertTrue(sendmail)
        for call in client_mock.mock_calls:
            if call[0] == '().sendmail':
                self.assertEqual(call[1][0], 'fake@sender.address')
                self.assertEqual(call[1][1], 'fake@mail.com')
                self.assertIn(base64.b64encode(expected_body.encode('UTF-8')).decode("UTF-8"),
                              call[1][2].replace("\n", ""))

