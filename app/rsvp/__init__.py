import os
from flask import Blueprint

rsvp = Blueprint('rsvp', __name__, template_folder='templates', static_folder='static')

from . import views
