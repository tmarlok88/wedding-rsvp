from unittest import TestCase
from moto import mock_dynamodb2

from tests import context
from tests.guest_helper import list_guests, clear_all_guests, EXAMPLE_GUEST_1, EXAMPLE_GUEST_2, save_guest

TEST_INPUT_1 = '''email,name
testmail@testddomain.tld,Test user
alfa@beta.gamma,Mock family
'''


@mock_dynamodb2
class CSVHandlerTest(TestCase):

    def setUp(self) -> None:
        context.app.model.Guest.Guest.create_table()
        self.handler = context.app.services.CSVHandler.CSVHandler()

    def tearDown(self) -> None:
        clear_all_guests()

    def test_import_csv(self):
        import_outcome = self.handler.import_csv(TEST_INPUT_1)
        guests = list_guests()
        self.assertTrue(import_outcome)
        self.assertEqual(["testmail@testddomain.tld", "alfa@beta.gamma"], [guest.email for guest in guests])
        self.assertEqual(["Test user", "Mock family"], [guest.name for guest in guests])

    def test_export_csv(self):
        guest1 = save_guest(EXAMPLE_GUEST_1)
        guest2 = save_guest(EXAMPLE_GUEST_2)
        exported = self.handler.export_csv().getvalue().split("\r\n")
        exploded_exported_list = [list(filter(lambda x:x != '', exp.split(","))) for exp in exported]   # explode each line to items, remove empty strings

        self.assertCountEqual(list(guest1.get_attributes().keys()), exploded_exported_list[0])
        self.assertCountEqual([str(guest_attr) for guest_attr in guest1.attribute_values.values()], exploded_exported_list[1])
        self.assertCountEqual([str(guest_attr) for guest_attr in guest2.attribute_values.values()], exploded_exported_list[2])
