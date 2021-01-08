from flask import current_app
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, IntegerField, BooleanField, PasswordField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, NumberRange
from flask_babel import lazy_gettext as _l
from werkzeug.security import check_password_hash


from app.model.Guest import Guest


class GuestForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    email = EmailField(_l('E-mail'), validators=[DataRequired(), Email()])
    food_allergies = StringField(_l('Food allergies'))
    number_of_guests = IntegerField(_l('Number of guests'), validators=[NumberRange(0, 20)])
    notes = StringField(_l('Other important notes'))
    favourite_music = StringField(_l('Favourite music'),
                                  description=_l("Do you have some music, you'd really like to listen?"))
    will_attend = BooleanField(_l('I will attend'))
    submit = SubmitField('Submit')

    def set_model(self, guest: Guest):
        self.name.data = guest.name
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
    # recipients = SelectMultipleField(_l('Send To'), validators=[DataRequired()],
    #                                  render_kw={'multiple': None, 'data-live-search': "true", 'class': "selectpicker"},
    #                                  choices=[(g.email, g.name) for g in Guest.scan()])
    body = TextAreaField(_l('E-mail body'), validators=[DataRequired()])
    submit = SubmitField(_l('Send'))
