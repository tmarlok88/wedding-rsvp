from moto import mock_dynamodb2
from parent import ParentTest
import datetime

from tests.guest_helper import create_guest, EXAMPLE_GUEST_1, EXAMPLE_GUEST_2, INVALID_GUEST


@mock_dynamodb2
class TestRSVPGuestForm(ParentTest):
    def test_fill_form_from_model(self):
        from tests import context
        form = context.app.rsvp.forms.GuestForm()
        guest = create_guest(EXAMPLE_GUEST_1)
        form.fill_form_from_model(guest)
        for key, value in form.data.items():
            if key != "submit":
                self.assertEqual(value, EXAMPLE_GUEST_1[key])

    def test_fill_model_from_form(self):
        from tests import context
        form = context.app.rsvp.forms.GuestForm()
        guest = create_guest({})
        form.process(data=EXAMPLE_GUEST_2)
        now = datetime.datetime.utcnow()
        guest.last_viewed = now

        form.fill_model_from_form(guest)

        for key, value in form.data.items():
            if key != "submit":
                self.assertEqual(guest.attribute_values.get(key), EXAMPLE_GUEST_2.get(key))
        for key, value in guest.attribute_values.items():                   # Guest attributes not in the form shouldn't be touched
            if key not in form.data.keys():
                self.assertNotEqual(guest.attribute_values.get(key), EXAMPLE_GUEST_2.get(key))
        self.assertEqual(guest.last_viewed, now)                            # last_viewed attribute is the same

    def test_validator(self):
        from tests import context
        form = context.app.rsvp.forms.GuestForm()
        form.process(data=INVALID_GUEST)
        form.validate()
        self.assertGreater(len(form.errors), 0)
        self.assertIn('number_of_guests', form.errors.keys())
