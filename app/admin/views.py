import os

from flask import render_template, redirect, url_for, abort, flash, request, Response
from flask_babel import _
from flask_login import login_required
from flask_login import login_user, logout_user

from app.admin import admin
from app.admin.forms import GuestForm, LoginForm, EmailForm
from app.model.Admin import Admin
from app.model.Guest import Guest
from app.services.EmailSender import EmailSender
from app.services.CSVHandler import CSVHandler


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
    guest = Guest.find(guest_id) or abort(404)
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


@admin.route('/guest/delete/<string:guest_id>', methods=['POST'])
@login_required
def delete_guest(guest_id):
    guest = Guest.find(guest_id) or abort(404)
    guest.delete()
    flash(_("Guest {} removed".format(guest.name)))
    return redirect(url_for("admin.list_guest"))


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        logout_user()           # just to be sure we wipe any leftover session cookie
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
    form.recipients.choices.extend([(str(g.id), g.name) for g in Guest.scan()])
    if form.validate_on_submit():
        footer = _("Your RSVP link: ")+f"{request.url_root}rsvp/{{id}}"+"\n"
        footer += _("Unsubscribe and delete my data: ")+f"{request.url_root}rsvp/unsubscribe/{{id}}?email={{email}}"
        emailsender = EmailSender(os.getenv("SENDER_SMTP_SERVER"), os.getenv("SENDER_EMAIL_ADDRESS"),
                                  os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"), footer_template=footer)

        if "all" in form.recipients.data:
            guests = Guest.scan()
        else:
            guests = Guest.find_multi_id(form.recipients.data)
        success, failed = emailsender.send_emails(guests, form.subject.data, form.body.data)
        if success:
            flash(str(len(success)) + _(" E-mails sent successfully"), "success")
        if failed:
            flash(str(len(failed)) + _(" E-mails couldn't be sent"), "warning")

    return render_template('email_sender.html', title=_('Send mail'), form=form)


@admin.route('/guest/import', methods=['POST'])
@login_required
def import_guests():
    if CSVHandler.import_csv(request.files["csv_file"].read().decode("utf-8")):
        flash(_("Guest list imported successfully"), "success")
    else:
        flash(_("Guest list import was unsuccessful"), "error")
    return redirect(url_for("admin.list_guest"))


@admin.route('/guest/export', methods=['GET'])
@login_required
def export_guests():
    response = Response(CSVHandler.export_csv().getvalue(), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename="guests.csv")
    return response
