from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField, StringField, IntegerField, BooleanField
from wtforms.validators import NumberRange
from flask_babel import lazy_gettext as _l

from app.model.Guest import Guest


class RSVPCaptchaForm(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField(_l('Bring me to the RSVP'))


class GuestForm(FlaskForm):
    food_allergies = StringField(_l('Food allergies'))
    number_of_guests = IntegerField(_l('Number of guests'), validators=[NumberRange(0, 20)])
    notes = StringField(_l('Other important notes'))
    favourite_music = StringField(_l('Favourite music'),
                                  description=_l("Do you have some music, you'd really like to listen?"))
    will_attend = BooleanField(_l('I will attend'))
    submit = SubmitField('Submit')

    def set_model(self, guest: Guest):
        self.notes.data = guest.notes
        self.number_of_guests.data = guest.number_of_guests
        self.food_allergies.data = guest.food_allergies
        self.will_attend.data = guest.will_attend
        self.favourite_music.data = guest.favourite_music

    def fill_model(self, guest: Guest):
        guest.notes = self.notes.data
        guest.number_of_guests = self.number_of_guests.data
        guest.food_allergies = self.food_allergies.data
        guest.will_attend = self.will_attend.data
        guest.favourite_music = self.favourite_music.data
        return guest
