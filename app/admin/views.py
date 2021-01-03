from flask_babel import _
from flask import render_template, redirect, url_for, abort, flash
from flask_login import login_required

from app.admin import admin
from app.admin.forms import GuestForm
from app.model.Guest import Guest


@admin.route('/', methods=['GET'])
@login_required
def admin_dashboard():
    return render_template("admin/admin_dashboard.html", title=_("Admin page"))


@admin.route('/guest/add', methods=['GET', 'POST'])
@login_required
def add_guest():
    form = GuestForm()
    if form.validate_on_submit():
        guest = Guest()
        guest.name = form.name.data
        guest.email = form.email.data
        guest.notes = form.notes.data
        guest.number_of_guests = form.number_of_guests.data
        guest.food_allergies = form.food_allergies.data
        guest.will_attend = form.will_attend.data
        guest.favourite_music = form.favourite_music.data
        guest.save()
        return redirect(url_for("admin.list_guest"))

    return render_template('admin/guest_form.html', form=form, title=_("Add guest"))


@admin.route('/guest/edit/<string:guest_id>', methods=['GET', 'POST'])
@login_required
def edit_guest(guest_id):
    form = GuestForm()
    guests = Guest.scan(Guest.id == guest_id)
    guest = guests.next()
    if not guest:
        abort(404)
    if form.validate_on_submit():
        guest.name = form.name.data
        guest.email = form.email.data
        guest.notes = form.notes.data
        guest.number_of_guests = form.number_of_guests.data
        guest.food_allergies = form.food_allergies.data
        guest.will_attend = form.will_attend.data
        guest.favourite_music = form.favourite_music.data
        guest.filled_by_admin = True
        guest.save()
        return redirect(url_for("admin.list_guest"))
    form.name.data = guest.name
    form.email.data = guest.email
    form.notes.data = guest.notes
    form.number_of_guests.data = guest.number_of_guests
    form.food_allergies.data = guest.food_allergies
    form.will_attend.data = guest.will_attend
    form.favourite_music.data = guest.favourite_music
    return render_template('admin/guest_form.html', form=form, title=_("Edit guest"))


@admin.route('/guest/list', methods=['GET', 'POST'])
@login_required
def list_guest():
    guest_list = Guest.scan()
    return render_template('admin/guest_list.html', guests=guest_list, title=_("Guest list"))


@admin.route('/guest/delete/<string:guest_id>', methods=['GET'])
@login_required
def delete_guest(guest_id):
    guests = Guest.scan(Guest.id == guest_id)
    guest = guests.next()
    if not guest:
        abort(404)
    guest.delete()
    flash(_("Guest {} removed".format(guest.name)))
    return redirect(url_for("admin.list_guest"))
