from unittest import TestCase
from unittest.mock import patch

from tests import context


class EmailSenderTest(TestCase):
    @patch("boto3.client")
    def test_send_email(self, client_mock):
        sender = context.app.services.EmailSender.EmailSender('eu-central-1', 'fake@sender.address')
        sendmail = sender.send_email(['recipient1@address.com', 'recipient2@address.com'], "Test email", "Mail body")
        self.assertTrue(sendmail)

