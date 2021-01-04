from flask import Flask, request
from flask_babel import Babel
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from app.config import Config

from app.model.Admin import Admin
from app.model.Guest import Guest

from app.admin import admin as admin_blueprint
from app.rsvp import rsvp as rsvp_blueprint


app = Flask(__name__)
app.config.from_object(Config)

babel = Babel(app)
login = LoginManager(app)

bootstrap = Bootstrap(app)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


@login.user_loader
def load_user(user_id):
    if request.blueprint == "admin":
        if user_id == "admin":
            return Admin()
    if request.blueprint == "rsvp":
        guests = Guest.scan(Guest.id == user_id)
        try:
            guest = guests.next()
            return guest
        except StopIteration as si_exception:
            return None



app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(rsvp_blueprint)

login.blueprint_login_views = {
    'admin': 'admin.login',
    'rsvp': 'rsvp.rsvp_captcha',
}
