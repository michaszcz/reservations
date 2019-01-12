from flask import render_template, request, redirect, url_for, flash, session

from app import app
from forms.authorization import RegistrationForm, LoginForm, ChangePasswordForm
from models import User
from utils import auth
from utils.decorators import login_required, nologin_required


@app.route("/")
def index():
    """
    W zależności czy użytkownik jest zalogowany przenosi go na odpowiednią
    podstronę.
    """
    if auth.is_authorized():
        return redirect(url_for('reservations'))
    return redirect(url_for('login'))


@app.route("/login", methods=('GET', 'POST'))
@nologin_required
def login():
    """
    Tworzy sesję i loguje użytkownika.
    """
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            if auth.login(form.email.data, form.password.data):
                flash('Zalogowano', 'success')
                return redirect(url_for('reservations'))
            flash('Nie poprawny email lub hasło', 'danger')
            return render_template('sign_in.html', form=form)
        flash('Niepoprawnie wypełniony formularz', 'danger')
    return render_template('sign_in.html', form=form)


@app.route("/logout")
@login_required
def logout():
    """
    Usuwa sesję i wylogowuje użytkownika.
    """
    auth.logout()
    flash('Wylogowano', 'success')
    return redirect(url_for('login'))


@app.route("/registration", methods=('GET', 'POST'))
@nologin_required
def register():
    """
    Obsługuje rejestrację użytkownika.
    """
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            if User.create(form.email.data, form.password.data):
                flash('Rejestracja przebiegla pomyślnie', 'success')
                return redirect(url_for('login'))
            else:
                flash('Wystąpił błąd. Spróbuj ponownie.', 'danger')
        else:
            flash('Niepoprawnie wypełniony formularz', 'danger')
    return render_template('registration.html', form=form)


@app.route("/change_password", methods=('GET', 'POST'))
@login_required
def change_password():
    """
    Zmienia hasło użytkownika.
    """
    form = ChangePasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if User.change_password(session['uid'], form.password.data):
                flash('Hasło zostało zmienione', 'success')
                return redirect(url_for('index'))
            else:
                flash('Wystąpił błąd. Spróbuj ponownie.', 'danger')
        else:
            flash('Niepoprawnie wypełniony formularz', 'danger')
    return render_template('change_password.html', form=form)

