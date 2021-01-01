from flask import Flask
from flask import request
from flask_babel import Babel
from flask_login import LoginManager

from app.config import Config

from app.model.Admin import Admin

app = Flask(__name__)
app.config.from_object(Config)

babel = Babel(app)
login = LoginManager(app)
login.login_view = 'login'


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


@login.user_loader
def load_user(id):
    if id == "admin":
        return Admin()


from app.views import rsvp, admin, login
