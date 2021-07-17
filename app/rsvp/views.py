import datetime
import os

import yaml
from urllib.parse import urlparse
from flask import render_template, request, abort, redirect, url_for, current_app
from flask_babel import _
from flask_login import login_required, login_user, current_user, logout_user

from app.model.Guest import Guest
from app.rsvp import rsvp
from app.rsvp.forms import RSVPCaptchaForm, GuestForm


@rsvp.route('/', methods=['GET', 'POST'], defaults={'guest_id': None})
@rsvp.route('/<string:guest_id>', methods=['GET', 'POST'])
@login_required
def rsvp_page(guest_id):
    if (guest_id is not None and not current_user.is_anonymous and str(current_user.id) != guest_id) or \
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

    with open(os.getenv('PERSONALIZE_SRC_FILE'), 'r') as stream:
        custom_rsvp_content = yaml.safe_load(stream)
        return render_template("rsvp.html", form=form, guest=current_user, title=_("Wedding RSVP | ")+current_user.name,
                               rsvp_content=custom_rsvp_content, MAPS_API_KEY=os.getenv("MAPS_API_KEY"))


@rsvp.route('/captcha', methods=['GET', 'POST'])
def rsvp_captcha():
    guest_id = urlparse(request.args.get("next", "").split('/')[-1]).path

    if not guest_id:
        abort(404)
    form = RSVPCaptchaForm()

    if form.validate_on_submit() or not current_app.config["USE_RECAPTCHA_FOR_GUEST"]:
        guest = Guest.find(guest_id)
        if guest:
            login_user(guest, remember=True)
            return redirect(url_for("rsvp.rsvp_page", guest_id=guest_id))
        else:
            abort(404)
    else:
        return render_template('rsvp_captcha.html', title=_('Wedding'), form=form)


@rsvp.route('/unsubscribe/<string:guest_id>', methods=['GET'])
def unsubscribe(guest_id):
    email = request.args.get('email')
    guest = Guest.find(guest_id)
    if guest and email == guest.email:
        print(f"Guest {guest.id} removed")
        guest.delete()
        return render_template('unsubscribe.html')
    else:
        abort(404)
