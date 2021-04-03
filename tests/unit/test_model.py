from unittest import TestCase, mock
from moto import mock_dynamodb2
from uuid import UUID
import datetime
import os

from tests import context
from tests.guest_helper import EXAMPLE_GUEST_1, EXAMPLE_GUEST_2


class AdminModelTest(TestCase):
    def test_admin_get_id(self):
        test_admin = context.app.model.Admin.Admin()
        self.assertEqual(test_admin.get_id(), 'admin')


@mock_dynamodb2
@mock.patch.dict(os.environ, {"AWS_REGION": "us-west-1", "DYNAMO_TABLE": "placeholder"})
class GuestModelTest(TestCase):
    def test_guest_default_values(self):
        test_guest = context.app.model.Guest.Guest()
        self.assertIsNotNone(UUID(str(test_guest.get_id()), version=4))
        self.assertFalse(test_guest.filled_by_admin)

    def test_guest_create_from_json(self):
        test_guest = context.app.model.Guest.Guest(**EXAMPLE_GUEST_1)
        test_guest_dict = test_guest.attribute_values
        test_guest.save()

        test_guest_dict.pop("id")               # filled_by_default
        test_guest_dict.pop("filled_by_admin")  # filled_by_default
        self.assertDictEqual(test_guest_dict, EXAMPLE_GUEST_1)

    def test_guest_create_set_datetime(self):
        now = datetime.datetime.utcnow()
        test_guest = context.app.model.Guest.Guest(email="a@b.c", last_viewed=now)
        self.assertEqual(test_guest.last_viewed, now)

        test_guest.last_responded = "2021-01-24"
        with self.assertRaisesRegex(AttributeError, "'str' object has no attribute 'tzinfo'"):
            test_guest.save()

    def test_guest_create_without_email(self):
        test_guest = context.app.model.Guest.Guest()
        with self.assertRaisesRegex(ValueError, "Attribute 'email' cannot be None"):
            test_guest.save()

    def test_find_guest(self):
        test_guest = context.app.model.Guest.Guest(**EXAMPLE_GUEST_1)
        test_guest_2 = context.app.model.Guest.Guest(**EXAMPLE_GUEST_2)                # Just so that we have a second value
        test_guest.save()
        test_guest_2.save()
        found_guest = context.app.model.Guest.Guest.find(test_guest.get_id())
        self.assertDictEqual(test_guest.attribute_values, found_guest.attribute_values)

    def test_find_non_existing_guest(self):
        test_guest = context.app.model.Guest.Guest(**EXAMPLE_GUEST_1)
        test_guest_2 = context.app.model.Guest.Guest(**EXAMPLE_GUEST_2)                # Just so that we have a second value
        test_guest_2.save()
        found_guest = context.app.model.Guest.Guest.find(test_guest.get_id())
        self.assertIsNone(found_guest)
