import os

from flask_babel import _
from flask import render_template, redirect, url_for, abort, flash
from flask_login import login_required
from flask_login import login_user, logout_user

from app.admin import admin
from app.admin.forms import GuestForm, LoginForm, EmailForm
from app.model.Guest import Guest
from app.model.Admin import Admin
from app.services.EmailSender import EmailSender


@admin.route('/', methods=['GET'])
@login_required
def admin_dashboard():
    return render_template("admin_dashboard.html", title=_("Admin page"))


@admin.route('/guest/add', methods=['GET', 'POST'])
@login_required
def add_guest():
    form = GuestForm()
    if form.validate_on_submit():
        guest = Guest()
        form.fill_model(guest)
        guest.filled_by_admin = True
        guest.save()
        return redirect(url_for("admin.list_guest"))

    return render_template('guest_form.html', form=form, title=_("Add guest"))


@admin.route('/guest/edit/<string:guest_id>', methods=['GET', 'POST'])
@login_required
def edit_guest(guest_id):
    form = GuestForm()
    guests = Guest.scan(Guest.id == guest_id)
    try:
        guest = guests.next()
    except StopIteration as si_exception:
        abort(404)
    else:
        if form.validate_on_submit():
            form.fill_model(guest)
            guest.filled_by_admin = True
            guest.save()
            return redirect(url_for("admin.list_guest"))
        form.set_model(guest)
        return render_template('guest_form.html', form=form, title=_("Edit guest"))


@admin.route('/guest/list', methods=['GET', 'POST'])
@login_required
def list_guest():
    guest_list = Guest.scan()
    return render_template('guest_list.html', guests=guest_list, title=_("Guest list"))


@admin.route('/guest/delete/<string:guest_id>', methods=['GET'])        # TODO csrf protection
@login_required
def delete_guest(guest_id):
    guests = Guest.scan(Guest.id == guest_id)
    try:
        guest = guests.next()
    except StopIteration as si_exception:
        abort(404)
    guest.delete()
    flash(_("Guest {} removed".format(guest.name)))
    return redirect(url_for("admin.list_guest"))


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin()
        if not form.validate_login():
            flash(_('Invalid username or password'))
            return redirect(url_for('admin.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("admin.admin_dashboard"))
    return render_template('login.html', title=_('Sign In'), form=form)


@admin.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


@admin.route('/email_sender', methods=['GET', 'POST'])
@login_required
def email_sender():
    form = EmailForm()
    form.recipients.choices = [(g.email, g.name) for g in Guest.scan()]
    if form.validate_on_submit():
        emailsender = EmailSender(os.getenv("AWS_REGION"), os.getenv("SENDER_EMAIL_ADDRESS"))
        if emailsender.send_email(form.recipients.data, form.subject.data, form.body.data):
            flash(_("E-mails sent successfully"))
        else:
            flash(_("E-mails couldn't be sent"))

    return render_template('email_sender.html', title=_('Send mail'), form=form)
