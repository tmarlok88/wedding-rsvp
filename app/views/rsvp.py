from flask import render_template

from flask_babel import _

from app import app


@app.route('/rsvp', methods=['GET'])
def rsvp():
    return render_template("rsvp.html", title=_("Wedding RSVP"))
