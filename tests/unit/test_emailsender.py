from unittest import TestCase, mock

from tests import context
from tests.guest_helper import EXAMPLE_GUEST_1


@mock.patch("boto3.client")
class EmailSenderTest(TestCase):
    def test_send_email(self, client_mock):
        sender = context.app.services.EmailSender.EmailSender('eu-central-1', 'fake@sender.address')
        sendmail = sender.send_email('recipient1@address.com', "Test email", "Mail body")
        self.assertTrue(sendmail)

    def test_send_emails(self, client_mock):
        test_guest = context.app.model.Guest.Guest(**EXAMPLE_GUEST_1)

        footer = "rsvp: https://test.tld/rsvp/{id}\nunsubscribe: https://test.tld/rsvp/unsubscribe/{id}"
        expected_body = f'Mail body {test_guest.name}\n---\n'+footer.format(**test_guest.attribute_values)
        sender = context.app.services.EmailSender.EmailSender('eu-central-1', 'fake@sender.address',
                                                              footer_template=footer)
        sendmail = sender.send_emails([test_guest], "Test email", "Mail body {name}")
        self.assertTrue(sendmail)
        client_mock.assert_has_calls([mock.call().send_email(Destination={'ToAddresses': ['fake@mail.com']},
                                                             Message={'Body': {'Text': {'Charset': 'UTF-8',
                                                                                        'Data': expected_body}},
                                                                      'Subject': {'Charset': 'UTF-8',
                                                                                  'Data': 'Test email'}},
                                                             Source='fake@sender.address')])

