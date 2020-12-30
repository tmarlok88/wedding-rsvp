from flask import Flask
from flask import request
from flask_babel import Babel

from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

babel = Babel(app)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


from app.views import rsvp