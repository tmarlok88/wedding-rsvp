from moto import mock_dynamodb2
import html
import uuid
from parent import ParentTest
from tests.guest_helper import save_guest, list_guests, clear_all_guests, EXAMPLE_GUEST_1, EXAMPLE_GUEST_2, INVALID_GUEST


@mock_dynamodb2
class TestAdminGuest(ParentTest):
    def create_app(self):
        app = ParentTest.create_app(self)
        from app.model.Guest import Guest
        Guest.create_table()
        return app

    def tearDown(self) -> None:
        clear_all_guests()

    def test_list_guests(self):
        save_guest(EXAMPLE_GUEST_1)

        response = self.client.get("/admin/guest/list")

        self.assert200(response)
        self.assert_template_used("guest_list.html")
        self.assertIn(EXAMPLE_GUEST_1["name"], response.data.decode("utf-8"))
        self.assertNotIn("FakeUser", response.data.decode("utf-8"))

    def test_add_guest_page(self):
        response = self.client.get("/admin/guest/add")
        self.assert200(response)
        self.assert_template_used("guest_form.html")

    def test_add_guest(self):
        unique_mail = f"{uuid.uuid4()}@fakemail.com"
        guest_data = dict(EXAMPLE_GUEST_2)
        guest_data["email"] = unique_mail
        expected_data = dict(guest_data)
        guest_data.pop("will_attend")

        response = self.client.post("/admin/guest/add", data=guest_data)
        self.assert_redirects(response, "admin/guest/list")

        guests = list_guests()
        added_guest = next(item for item in guests if item.email == unique_mail)
        expected_data['notes'] = ''
        expected_data["id"] = uuid.UUID(added_guest.get_id())

        self.assertDictEqual(added_guest.__dict__["attribute_values"], expected_data)

    def test_add_guest_invalid_data(self):
        response = self.client.post("/admin/guest/add", data=dict(INVALID_GUEST))
        guests = list_guests()

        self.assert200(response)
        self.assert_template_used("guest_form.html")
        self.assertIn("This field is required.", response.data.decode("utf-8"))
        self.assertIn("Invalid email address", response.data.decode("utf-8"))
        self.assertIn("Number must be between", response.data.decode("utf-8"))
        self.assertEqual(len(guests), 0)

    def test_edit_guest_page(self):
        guest_data = EXAMPLE_GUEST_1
        guest_id = save_guest(guest_data).id
        response = self.client.get(f"/admin/guest/edit/{guest_id}")
        self.assert200(response)
        self.assert_template_used("guest_form.html")
        for key, value in guest_data.items():
            self.assertIn(f"name=\"{key}\"", html.unescape(response.data.decode("utf-8")))
            if type(value) is not bool:
                self.assertIn(str(value), html.unescape(response.data.decode("utf-8")))
            else:
                string_val = "y" if value else "n"
                self.assertIn(f"value=\"{string_val}\"", html.unescape(response.data.decode("utf-8")))

    def test_edit_guest_page_no_such_guest(self):
        guest_data = EXAMPLE_GUEST_1
        guest_id = save_guest(guest_data).id
        response = self.client.get(f"/admin/guest/edit/{guest_id}XXX")
        self.assert404(response)
        self.assert_template_used("errors/404.html")

    def test_edit_guest(self):
        guest_data = dict(EXAMPLE_GUEST_1)
        edited_guest_data = dict(EXAMPLE_GUEST_2)
        edited_guest_data.pop("will_attend")
        guest_id = save_guest(guest_data).id
        response = self.client.post(f"/admin/guest/edit/{guest_id}", data=edited_guest_data)
        guests = list_guests()

        self.assert_redirects(response, "/admin/guest/list")
        self.assertEqual(len(guests), 1)
        edited_guest_data["filled_by_admin"] = True
        edited_guest_data["id"] = guests[0].id
        edited_guest_data["will_attend"] = False
        edited_guest_data["notes"] = ''
        self.assertDictEqual(guests[0].__dict__["attribute_values"], edited_guest_data)

    def test_delete_guest(self):
        guest_data = EXAMPLE_GUEST_1
        guest_id = save_guest(guest_data).id
        response = self.client.post(f"/admin/guest/delete/{guest_id}")
        guests = list_guests()

        self.assert_redirects(response, "/admin/guest/list")
        self.assertMessageFlashed(f"Guest {EXAMPLE_GUEST_1['name']} removed")
        self.assertEqual(len(guests), 0)

    def test_delete_guest_no_such_guest(self):
        guest_data = EXAMPLE_GUEST_1
        guest_id = save_guest(guest_data).id
        response = self.client.post(f"/admin/guest/delete/{guest_id}XXX")

        self.assert404(response)
        self.assert_template_used("errors/404.html")
