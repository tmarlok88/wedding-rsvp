from flask_babel import _
from flask import render_template

from app.rsvp import rsvp


@rsvp.route('/rsvp', methods=['GET'])
def rsvp():
    return render_template("rsvp/rsvp.html", title=_("Wedding RSVP"))
