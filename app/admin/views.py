from flask_babel import _
from flask import render_template
from flask_login import login_required

from . import admin


@admin.route('/', methods=['GET'])
@login_required
def admin():
    return render_template("admin/admin.html", title=_("Admin page"))
