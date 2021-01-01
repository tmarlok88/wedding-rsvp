from flask import Flask
from flask import request
from flask_babel import Babel
from flask_login import LoginManager

from app.config import Config

from app.model.Admin import Admin

from .admin import admin as admin_blueprint
from .auth import auth as auth_blueprint
from .rsvp import rsvp as rsvp_blueprint


app = Flask(__name__)
app.config.from_object(Config)

babel = Babel(app)
login = LoginManager(app)
login.login_view = 'auth.login'


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


@login.user_loader
def load_user(id):
    if id == "admin":
        return Admin()


app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(auth_blueprint)
app.register_blueprint(rsvp_blueprint)
