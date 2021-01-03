from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, NumberRange
from flask_babel import _, lazy_gettext as _l


class GuestForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    email = StringField(_l('E-mail'), validators=[DataRequired(), Email()])
    food_allergies = StringField(_l('Food allergies'))
    number_of_guests = IntegerField(_l('Number of guests'), validators=[NumberRange(0, 20)])
    notes = StringField(_l('Other important notes'))
    favourite_music = StringField(_l('Favourite music'),
                                  description=_l("Do you have some music, you'd really like to listen?"))
    will_attend = BooleanField(_l('I will attend'))
    submit = SubmitField('Submit')
