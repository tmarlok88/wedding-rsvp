from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField, StringField, BooleanField, TextAreaField
from wtforms.validators import NumberRange
from wtforms_components import IntegerField

from app.model.Guest import Guest


class RSVPCaptchaForm(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField()


class GuestForm(FlaskForm):
    number_of_guests = IntegerField(_l('Number of guests'), validators=[NumberRange(0, 20)],
                                    description=_l("How many of you come (including you)?"))
    food_allergies = StringField(_l('Food allergies'),
                                 description=_l("If you (or one of your guests) have any food allergy please let us know"))
    favourite_music = StringField(_l('Favourite music'),
                                  description=_l("Do you have some music, you'd really like to listen?"))
    notes = TextAreaField(_l('Other important notes'), render_kw={"rows": 7},
                          description=_l("Anything important you'd want us to know"))
    will_attend = BooleanField(_l('I will attend'))
    submit = SubmitField(_l('Submit'))

    def fill_form_from_model(self, guest: Guest):
        self.process(obj=guest)

    def fill_model_from_form(self, guest: Guest):
        return self.populate_obj(guest)
