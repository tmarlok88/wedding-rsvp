from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField, StringField, BooleanField
from wtforms.validators import NumberRange
from wtforms_components import IntegerField

from app.model.Guest import Guest


class RSVPCaptchaForm(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField(_l('Bring me to the RSVP'))


class GuestForm(FlaskForm):
    number_of_guests = IntegerField(_l('Number of guests'), validators=[NumberRange(0, 20)])
    food_allergies = StringField(_l('Food allergies'))
    favourite_music = StringField(_l('Favourite music'),
                                  description=_l("Do you have some music, you'd really like to listen?"))
    notes = StringField(_l('Other important notes'))
    will_attend = BooleanField(_l('I will attend'))
    submit = SubmitField(_l('Submit'))

    def fill_form_from_model(self, guest: Guest):
        self.process(obj=guest)

    def fill_model_from_form(self, guest: Guest):
        return self.populate_obj(guest)
