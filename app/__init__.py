from flask import Flask, request, current_app
from flask_babel import Babel
from flask_login import LoginManager
from app.config import Config

from app.model.Admin import Admin
from app.model.Guest import Guest

from app.admin import admin as admin_blueprint
from app.rsvp import rsvp as rsvp_blueprint

babel = Babel()
login = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    login.init_app(app)
    babel.init_app(app)

    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(rsvp_blueprint)
    login.login_message = None
    login.blueprint_login_views = {
        'admin': 'admin.login',
        'rsvp': 'rsvp.rsvp_captcha',
    }

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


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
