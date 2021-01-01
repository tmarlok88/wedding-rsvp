from flask import Blueprint

rsvp = Blueprint('rsvp', __name__)

from . import views
