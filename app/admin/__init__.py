from flask import Blueprint

admin = Blueprint('admin', __name__, template_folder='templates')

from . import views         # noqa: F401, E402
