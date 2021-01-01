from flask_babel import _
from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user

from app.model.Admin import Admin
from app.auth.forms import LoginForm
from . import auth


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin()
        if not form.validate_login():
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("admin.admin"))
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
