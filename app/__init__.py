import os

from flask import Flask, request, render_template, current_app
from flask_babel import Babel
from flask_cdn import CDN
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from app.admin import admin as admin_blueprint
from app.config import Config
from app.model.Admin import Admin
from app.model.Guest import Guest
from app.rsvp import rsvp as rsvp_blueprint

babel = Babel()
login = LoginManager()
csrf = CSRFProtect()


def create_app(config_class=Config):
    static_folder = 'static'
    if os.environ.get('ENVIRONMENT') and os.environ.get('ENVIRONMENT') != "local":
        static_folder = f"{os.environ.get('ENVIRONMENT')}_static"

    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(config_class)
    login.init_app(app)
    babel.init_app(app)
    csrf.init_app(app)
    if static_folder != 'static':
        CDN(app)

    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(rsvp_blueprint, url_prefix='/rsvp')
    login.login_message = None
    login.blueprint_login_views = {
        'admin': 'admin.login',
        'rsvp': 'rsvp.rsvp_captcha',
    }

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

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
        return Guest.find(user_id)
