from flask_babel import _
from flask import render_template, redirect, url_for
from flask_login import login_required

from app.admin import admin
from app.admin.forms import GuestForm
from app.model.Guest import Guest


@admin.route('/', methods=['GET'])
@login_required
def admin_page():
    return render_template("admin/admin.html", title=_("Admin page"))


@admin.route('/guest/add', methods=['GET', 'POST'])
@login_required
def add_guest():
    form = GuestForm()
    if form.validate_on_submit():
        guest = Guest(name=form.name.data, email=form.email.data)
        guest.save()
        return redirect(url_for("admin.admin_page"))

    return render_template('admin/guest_form.html', action="Add", form=form, title="Add guest")
