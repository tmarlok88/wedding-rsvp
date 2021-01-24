import datetime

from flask_babel import _
from flask import render_template, request, abort, redirect, url_for, current_app
from flask_login import login_required, login_user, current_user, logout_user

from app.rsvp import rsvp
from app.rsvp.forms import RSVPCaptchaForm, GuestForm
from app.model.Guest import Guest


@rsvp.route('/rsvp', methods=['GET', 'POST'], defaults={'guest_id': None})
@rsvp.route('/rsvp/<string:guest_id>', methods=['GET', 'POST'])
@login_required
def rsvp_page(guest_id):
    if (guest_id is not None and not current_user.is_anonymous and current_user.id != guest_id) or \
            (current_user.is_anonymous and guest_id is None):
        logout_user()
        abort(404)
    form = GuestForm()

    current_user.last_viewed = datetime.datetime.utcnow()
    current_user.save()

    if form.validate_on_submit():
        form.fill_model_from_form(current_user)
        current_user.last_responded = datetime.datetime.utcnow()
        current_user.filled_by_admin = False
        current_user.save()
    else:
        form.fill_form_from_model(current_user)

    return render_template("rsvp.html", form=form, guest=current_user, title=_(f"Wedding RSVP | {current_user.name}"))


@rsvp.route('/rsvp_captcha', methods=['GET', 'POST'])
def rsvp_captcha():
    guest_id = request.args.get("next", "").split('/')[-1]

    if not guest_id:
        abort(404)
    form = RSVPCaptchaForm()

    if form.validate_on_submit() or not current_app.config["USE_RECAPTCHA_FOR_GUEST"]:
        guests = Guest.scan(Guest.id == guest_id)
        try:
            guest = guests.next()
            login_user(guest, remember=True)

            return redirect(url_for("rsvp.rsvp_page", guest_id=guest_id))
        except StopIteration as si_exception:
            abort(404)
    else:
        return render_template('rsvp_captcha.html', title=_('B & T Wedding'), form=form)


@rsvp.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/404.html'), 404