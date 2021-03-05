from flask import Blueprint

rsvp = Blueprint('rsvp', __name__, template_folder='templates')

from . import views
