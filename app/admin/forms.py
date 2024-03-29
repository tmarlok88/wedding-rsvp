from flask import current_app
from flask_babel import lazy_gettext as _l, _
from flask_wtf import FlaskForm, RecaptchaField
from werkzeug.security import check_password_hash
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField, \
    SelectMultipleField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, NumberRange
from wtforms_components import IntegerField, Email

from app.model.Guest import Guest


class GuestForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    email = EmailField(_l('E-mail'), validators=[DataRequired(), Email()])
    number_of_guests = IntegerField(_l('Number of guests'), default=0, validators=[NumberRange(0, 20)])
    food_allergies = TextAreaField(_l('Food allergies'))
    favourite_music = TextAreaField(_l('Favourite music'),
                                    description=_l("Do you have some music, you'd really like to listen?"))
    notes = TextAreaField(_l('Other important notes'))
    will_attend = BooleanField(_l('I will attend'))
    submit = SubmitField('Submit')

    def set_model(self, guest: Guest):
        self.name.data = guest.name
        self.email.data = guest.email
        self.notes.data = guest.notes
        self.number_of_guests.data = guest.number_of_guests
        self.food_allergies.data = guest.food_allergies
        self.will_attend.data = guest.will_attend
        self.favourite_music.data = guest.favourite_music

    def fill_model(self, guest: Guest):
        guest.name = self.name.data
        guest.email = self.email.data
        guest.notes = self.notes.data
        guest.number_of_guests = self.number_of_guests.data
        guest.food_allergies = self.food_allergies.data
        guest.will_attend = self.will_attend.data
        guest.favourite_music = self.favourite_music.data
        return guest


class LoginForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    recaptcha = RecaptchaField()
    submit = SubmitField(_l('Sign In'))

    def validate_login(self):
        return check_password_hash(current_app.config["ADMIN_PASSWORD_HASH"], self.password.data)


class EmailForm(FlaskForm):
    subject = StringField(_l('Subject'), validators=[DataRequired()])
    recipients = SelectMultipleField(_l('Send To'), validators=[DataRequired()],
                                     render_kw={'multiple': None, 'data-live-search': "true", 'class': "selectpicker"},
                                     choices=[("all", _("Send to all"))])
    body = TextAreaField(_l('E-mail body'), validators=[DataRequired()])
    submit = SubmitField(_l('Send'))
