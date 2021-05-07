import datetime
import os

import mock
from moto import mock_dynamodb2
import petname
import random
from bs4 import BeautifulSoup

from parent import ParentTest

from tests.guest_helper import clear_all_guests

@mock.patch.dict(os.environ, {"MAX_GUEST_COUNT": "250"})
@mock_dynamodb2
class TestAdminSendMail(ParentTest):
    def create_app(self):
        app = ParentTest.create_app(self)
        from app.model.Guest import Guest
        Guest.create_table()
        return app

    def setUp(self) -> None:
        self.filled_by_admin = 0
        self.responded = 0
        self.all_guests = 0
        self.viewed = 0
        self.all_invites = []
        for i in range(0, 100):
            guest = self._generate_random_guest()
            if i % 3 == 0:
                guest.last_viewed = datetime.datetime.utcnow()
                self.viewed += 1
            if i % 6 == 0:
                guest.number_of_guests = random.randint(1, 4)
                guest.will_attend = True
                self.all_guests += guest.number_of_guests
                guest.last_responded = datetime.datetime.utcnow()
                if random.randint(1, 4) % 4 == 1:
                    guest.favourite_music = petname.generate()
                if random.randint(1, 4) % 4 == 3:
                    guest.food_allergies = petname.generate()
                self.responded += 1
            if i % 5 == 0 and not guest.last_responded:
                guest.filled_by_admin = True
                guest.will_attend = i % 10 == 0
                guest.number_of_guests = random.randint(1, 4) if guest.will_attend else 0
                self.all_guests += guest.number_of_guests
                self.filled_by_admin += 1
            if i % 9 == 0 and not guest.last_responded and not guest.filled_by_admin:
                guest.will_attend = False
                guest.last_responded = datetime.datetime.utcnow()
                self.responded += 1
            self.all_invites.append(guest)
            guest.save()

    def tearDown(self) -> None:
        clear_all_guests()

    def test_dashboard_page(self):
        response = self.client.get("/admin/")
        self.assertIn("Admin page", response.data.decode("utf-8"))
        self.assert_template_used("admin_dashboard.html")

    def test_dashboard_guest_counter(self):
        response = self.client.get("/admin/")
        soup = BeautifulSoup(response.data.decode("utf-8"), 'html.parser')
        guest_counter = soup.body.find(id="guest_counter")
        self.assertEqual(f"width:{100*self.all_guests/int(os.getenv('MAX_GUEST_COUNT'))}%", guest_counter.div.get("style"))
        self.assertIn(f"{self.all_guests} / {int(os.getenv('MAX_GUEST_COUNT'))}", guest_counter.div.string)
        self.assertIn("bg-success", guest_counter.div.get("class"))

    def test_dashboard_guest_counter_too_many_guests(self):
        guest = self._generate_random_guest()
        guest.will_attend = True
        guest.number_of_guests = 250
        guest.save()
        all_guests = guest.number_of_guests + self.all_guests

        response = self.client.get("/admin/")

        soup = BeautifulSoup(response.data.decode("utf-8"), 'html.parser')
        guest_counter = soup.body.find(id="guest_counter")
        self.assertEqual(f"width:{100*all_guests/int(os.getenv('MAX_GUEST_COUNT'))}%", guest_counter.div.get("style"))
        self.assertIn(f"{all_guests} / {int(os.getenv('MAX_GUEST_COUNT'))}", guest_counter.div.string)
        self.assertIn("bg-danger", guest_counter.div.get("class"))

    def test_dashboard_response_counter(self):
        response = self.client.get("/admin/")
        soup = BeautifulSoup(response.data.decode("utf-8"), 'html.parser')

        answer_percent_sum = 0
        for bar in soup.body.find(id="response_counter").find_all('div'):
            answer_percent_sum += float(bar.get('style').replace('width:', '').replace('%', ''))

        self.assertEqual(answer_percent_sum, 100)
        self.assertEqual(f"width:{100 * self.responded / len(self.all_invites)}%",
                         soup.body.find(id="response_answered").get("style"))
        self.assertEqual(f"width:{100 * self.filled_by_admin / len(self.all_invites)}%",
                         soup.body.find(id="response_admin_filled").get("style"))
        seen = (self.viewed-self.responded-len([g for g in self.all_invites if g.last_viewed and g.filled_by_admin]))
        self.assertEqual(f"width:{100 * seen / len(self.all_invites)}%",
                         soup.body.find(id="response_seen").get("style"))
        other = len([g for g in self.all_invites if not (g.last_viewed or g.filled_by_admin)])
        self.assertEqual(f"width:{100 * other / len(self.all_invites)}%",
                         soup.body.find(id="response_remaining").get("style"))

    def test_dashboard_answered_recently(self):
        response = self.client.get("/admin/")
        soup = BeautifulSoup(response.data.decode("utf-8"), 'html.parser')
        recents_from_table = soup.body.find(id="recently_responded")
        most_recents = sorted(self.all_invites, key=lambda i: (i.last_responded is not None, i.last_responded),
                              reverse=True)[:10]
        i = 0
        for row in recents_from_table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) > 0:
                self.assertEqual(most_recents[i].name, cols[0].string.strip())
                i += 1

    def test_dashboard_still_missing(self):
        response = self.client.get("/admin/")
        soup = BeautifulSoup(response.data.decode("utf-8"), 'html.parser')
        recents_from_table = soup.body.find(id="still_missing")
        missing_names = [i.name for i in self.all_invites if i.last_responded is None and i.filled_by_admin is not True]
        rowcount = 0
        for row in recents_from_table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) > 0:
                rowcount += 1
                self.assertIn(cols[0].string.strip(), missing_names)
        self.assertEqual(len(missing_names), rowcount)

    def test_dashboard_food_allergies(self):
        response = self.client.get("/admin/")
        soup = BeautifulSoup(response.data.decode("utf-8"), 'html.parser')
        recents_from_table = soup.body.find(id="food_allergies")
        food_allergies = [i.food_allergies for i in self.all_invites if i.food_allergies is not None]
        rowcount = 0
        for row in recents_from_table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) > 0:
                rowcount += 1
                self.assertIn(cols[1].string.strip(), food_allergies)
        self.assertEqual(len(food_allergies), rowcount)

    def test_dashboard_requested_songs(self):
        response = self.client.get("/admin/")
        soup = BeautifulSoup(response.data.decode("utf-8"), 'html.parser')
        recents_from_table = soup.body.find(id="requested_songs")
        requested_songs = [i.favourite_music for i in self.all_invites if i.favourite_music is not None]
        rowcount = 0
        for row in recents_from_table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) > 0:
                rowcount += 1
                self.assertIn(cols[1].string.strip(), requested_songs)
        self.assertEqual(len(requested_songs), rowcount)

    @staticmethod
    def _generate_random_guest():
        from app.model.Guest import Guest
        name = petname.generate()
        return Guest(email=f"{name}@mockmail.com", name=name.replace('-', ' ').title())
