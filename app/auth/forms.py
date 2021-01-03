import os

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_babel import _, lazy_gettext as _l
from werkzeug.security import check_password_hash


class LoginForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    recaptcha = RecaptchaField()
    submit = SubmitField(_l('Sign In'))

    def validate_login(self):
        return check_password_hash(os.getenv("ADMIN_PASSWORD_HASH"), self.password.data)
