from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField
from flask_babel import lazy_gettext as _l


class RSVPCaptchaForm(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField(_l('Bring me to the RSVP'))
