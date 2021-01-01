from flask import render_template

from flask_babel import _
from flask_login import login_required

from app import app


@app.route('/admin', methods=['GET'])
@login_required
def admin():
    return render_template("admin.html", title=_("Admin page"))
