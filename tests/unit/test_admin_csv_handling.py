from moto import mock_dynamodb2
import io
from parent import ParentTest
from tests.guest_helper import save_guest, list_guests, clear_all_guests, EXAMPLE_GUEST_1, EXAMPLE_GUEST_2, INVALID_GUEST

import test_csvhandler


@mock_dynamodb2
class TestAdminCSVHandling(ParentTest):
    def create_app(self):
        app = ParentTest.create_app(self)
        from app.model.Guest import Guest
        Guest.create_table()
        return app

    def tearDown(self) -> None:
        clear_all_guests()

    def test_import_guests(self):
        data = {'csv_file': (io.BytesIO(test_csvhandler.TEST_INPUT_1.encode("utf-8")), 'import.csv')}

        response = self.client.post("/admin/guest/import", data=data)
        guests = list_guests()

        self.assertRedirects(response, "/admin/guest/list")
        self.assertMessageFlashed("Guest list imported successfully")
        self.assertEqual(["testmail@testddomain.tld", "alfa@beta.gamma"], [guest.email for guest in guests])
        self.assertEqual(["Test user", "Mock family"], [guest.name for guest in guests])

    def test_export_guests(self):
        guest1 = save_guest(EXAMPLE_GUEST_1)
        guest2 = save_guest(EXAMPLE_GUEST_2)
        response = self.client.get("/admin/guest/export")

        content_lines = response.data.decode("utf-8").split("\r\n")
        self.assertIn("text/csv", response.content_type)

        for header_name in guest1.get_attributes().keys():
            self.assertIn(header_name, content_lines[0])

        for table_member in guest1.attribute_values.values():
            self.assertIn(str(table_member), content_lines[1])

        for table_member in guest2.attribute_values.values():
            self.assertIn(str(table_member), content_lines[2])
