import html
import datetime
import yaml
import os
import mock
from dateutil.tz import tzutc
from moto import mock_dynamodb2

from parent import ParentTest
from tests.guest_helper import save_guest, get_guest, clear_all_guests, EXAMPLE_GUEST_1, EXAMPLE_GUEST_2


@mock_dynamodb2
@mock.patch.dict(os.environ, {"PERSONALIZE_SRC_FILE": "../../app/personalize/rsvp_content.yaml"})
class TestRSVPViews(ParentTest):
    def create_app(self):
        app = ParentTest.create_app(self)
        app.config['LOGIN_DISABLED'] = False
        return app

    def tearDown(self) -> None:
        clear_all_guests()

    def test_redirect_to_captcha_page(self):
        response = self.client.get("/rsvp/fake_id")
        self.assert_redirects(response, "/rsvp/captcha?next=%2Frsvp%2Ffake_id")

    def test_captcha_page(self):
        self.app.config["USE_RECAPTCHA_FOR_GUEST"] = True
        self.app.config["RECAPTCHA_PUBLIC_KEY"] = "fake_key"

        response = self.client.get("/rsvp/captcha?next=%2Frsvp%2Ffake_id")

        self.assert200(response)
        self.assert_template_used("rsvp_captcha.html")

    def test_user_not_found(self):
        response = self.client.get("/rsvp", follow_redirects=True)
        self.assert404(response)
        self.assert_template_used("errors/404.html")

    def test_existing_user_found(self):
        guest_id = save_guest(EXAMPLE_GUEST_1).id

        response = self.client.get(f"/rsvp/{guest_id}", follow_redirects=True)

        self.assert200(response)
        self.assert_template_used("rsvp.html")
        self.assertIn(EXAMPLE_GUEST_1["name"], response.data.decode("utf-8"))

    def test_rsvp_last_viewed_updated(self):
        guest = save_guest(EXAMPLE_GUEST_1)
        self.client.get(f"/rsvp/{guest.id}", follow_redirects=True)
        edited_guest = get_guest(guest.id)
        self.assertAlmostEqual(edited_guest.last_viewed, datetime.datetime.now(tzutc()),
                               delta=datetime.timedelta(seconds=5))

    def test_rsvp_page(self):
        edit_allowed = ["will_attend", "favourite_music", "food_allergies", "number_of_guests", "notes"]

        guest = save_guest(EXAMPLE_GUEST_1)
        response = self.client.get(f"/rsvp/{guest.id}", follow_redirects=True)

        self.assert200(response)
        self.assert_template_used("rsvp.html")
        for key, value in EXAMPLE_GUEST_1.items():
            if key in edit_allowed:
                if type(value) is str:
                    self.assertIn(value, html.unescape(response.data.decode("utf-8")))
                if type(value) is bool and value is True:
                    self.assertIn("checked", response.data.decode("utf-8"))
                if type(value) is bool and value is False:
                    self.assertNotIn("checked", response.data.decode("utf-8"))

    def test_rsvp_captcha_missing_id(self):
        self.app.config["USE_RECAPTCHA_FOR_GUEST"] = True
        self.app.config["RECAPTCHA_PUBLIC_KEY"] = "fake_key"

        response = self.client.get(f"/rsvp/captcha?next=")

        self.assert404(response)
        self.assert_template_used("errors/404.html")

    def test_different_user_id_in_session_and_url(self):
        guest = save_guest(EXAMPLE_GUEST_1)
        guest2 = save_guest(EXAMPLE_GUEST_2)
        self.client.get(f"/rsvp/{str(guest.id)}", follow_redirects=True)      # user logs in
        response = self.client.get(f"/rsvp/")                                  # user_id from session

        self.assert200(response)
        self.assert_template_used("rsvp.html")
        self.assertIn(EXAMPLE_GUEST_1["name"], response.data.decode("utf-8"))

        response = self.client.get(f"/rsvp/{guest2.id}")
        self.assertNotIn(EXAMPLE_GUEST_2["name"], response.data.decode("utf-8"))

        self.assert404(response)
        self.assert_template_used("errors/404.html")

    def test_rsvp_fill_form(self):
        self.app.config["USE_RECAPTCHA_FOR_GUEST"] = False
        guest_data = dict(EXAMPLE_GUEST_1)
        edited_guest_data = {"food_allergies": "Kartoffel",
                             "number_of_guests": 2,
                             "notes": "blahblah",
                             "favourite_music": "Pink Floyd"}
        guest_id = save_guest(guest_data).id
        self.client.get(f"/rsvp/{str(guest_id)}", follow_redirects=True)      # user logs in
        self.client.post(f"/rsvp/{guest_id}", data=edited_guest_data)
        edited_guest = get_guest(guest_id)

        edited_guest_data["filled_by_admin"] = False
        edited_guest_data["id"] = guest_id
        edited_guest_data["will_attend"] = False
        edited_guest_data["last_responded"] = edited_guest.last_responded
        edited_guest_data["last_viewed"] = edited_guest.last_viewed
        self.assertDictEqual(edited_guest.__dict__["attribute_values"], {**EXAMPLE_GUEST_1, **edited_guest_data})

    def test_rsvp_fill_form_validators(self):
        self.app.config["USE_RECAPTCHA_FOR_GUEST"] = False
        guest_data = dict(EXAMPLE_GUEST_1)
        edited_guest_data = {"food_allergies": "Kartoffel",
                             "number_of_guests": -1,
                             "notes": "blahblah",
                             "favourite_music": "Pink Floyd"}
        guest_id = save_guest(guest_data).id
        self.client.get(f"/rsvp/{str(guest_id)}", follow_redirects=True)      # user logs in
        response = self.client.post(f"/rsvp/{guest_id}", data=edited_guest_data)
        edited_guest = get_guest(guest_id)

        self.assertIn("Number must be between", response.data.decode("utf-8"))
        self.assertEqual(edited_guest.number_of_guests, EXAMPLE_GUEST_1["number_of_guests"])

    def test_personalized_data_is_present(self):
        self.app.config["USE_RECAPTCHA_FOR_GUEST"] = False
        guest_data = dict(EXAMPLE_GUEST_1)
        guest_id = save_guest(guest_data).id
        response = self.client.get(f"/rsvp/{str(guest_id)}", follow_redirects=True)      # user logs in

        with open(os.getenv('PERSONALIZE_SRC_FILE'), 'r') as stream:
            try:
                personalized_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.assertIn(personalized_data["basic_data"]["bride"], response.data.decode("utf-8"))
        self.assertIn(personalized_data["basic_data"]["groom"], response.data.decode("utf-8"))
        self.assertIn(personalized_data["main_message"], response.data.decode("utf-8"))
        for _event in personalized_data["wedding_events"]:
            self.assertIn(_event['name'], response.data.decode("utf-8"))
            self.assertIn(_event['description'], response.data.decode("utf-8"))

    def test_form_descriptions(self):
        from tests import context
        guest = save_guest(EXAMPLE_GUEST_1)
        form = context.app.rsvp.forms.GuestForm()

        response = self.client.get(f"/rsvp/{guest.id}", follow_redirects=True)

        for key in form.data.keys():
            if form[key].description:
                self.assertIn(str(form[key].description), response.data.decode("utf-8"))
