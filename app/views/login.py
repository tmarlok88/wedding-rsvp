import os

from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_babel import _, lazy_gettext as _l
from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash

from app import app
from app.model.Admin import Admin


class LoginForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

    def validate_login(self):
        return check_password_hash(os.getenv("ADMIN_PASSWORD_HASH"), self.password.data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin()
        if not form.validate_login():
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("admin"))
    return render_template('login.html', title=_('Sign In'), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
