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
    submit = SubmitField(_l('Submit'))

    def fill_form_from_model(self, guest: Guest):
        self.process(obj=guest)

    def fill_model_from_form(self, guest: Guest):
        return self.populate_obj(guest)
