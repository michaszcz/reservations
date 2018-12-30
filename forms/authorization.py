from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import User
from storage import conn
from utils.security import check_password


class RegistrationForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(message="To pole jest wymagane"),
                                              Email(message="Niepoprawny adres email")])
    password = PasswordField('Hasło', validators=[DataRequired(message="To pole jest wymagane")])
    password2 = PasswordField(
        'Powtórz hasło',
        validators=[DataRequired(message="To pole jest wymagane"), EqualTo('password', message="Hasła różnią się")])

    def validate_email(self, email):
        user = User.get(email.data)
        if user is not None:
            raise ValidationError('Ten email jest już zajety')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Stare hasło', validators=[DataRequired(message="To pole jest wymagane")])
    password = PasswordField('Nowe hasło', validators=[DataRequired(message="To pole jest wymagane")])
    password2 = PasswordField(
        'Powtórz nowe hasło',
        validators=[DataRequired(message="To pole jest wymagane"), EqualTo('password', message="Hasła różnią się")])

    def validate_old_password(self, old_password):
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select hash_hasla from uzytkownicy where id=%s""", (session['uid'],))
                user = cur.fetchone()

        if user and check_password(old_password.data, user[0].tobytes()):
            return True
        raise ValidationError('Podane hasło jest nieprawidłowe')


class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(message="To pole jest wymagane"),
                                              Email(message="Niepoprawny adres email")])
    password = PasswordField('Hasło', validators=[DataRequired(message="To pole jest wymagane")])
