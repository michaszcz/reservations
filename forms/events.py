import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError


class EventCreationForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired(message="To pole jest wymagane"),
                                             Length(1, 50, "Długość pola powinna wynosić pomiędzy 1 a 50 znaków")])
    description = StringField('Opis', validators=[Length(-1, 255, "Maksymalna długość tego pola to 255 znaków")])
    place = StringField("Miejsce", validators=[Length(-1, 50, "Maksymalna długość tego pola to 50 znaków")])
    start_timestamp = DateTimeField("Czas rozpoczęcia", validators=[DataRequired(message="To pole jest wymagane")],
                                    default=datetime.datetime.now()+datetime.timedelta(days=1))
    end_timestamp = DateTimeField("Czas zakończenia", validators=[DataRequired(message="To pole jest wymagane")],
                                  default=datetime.datetime.now() + datetime.timedelta(days=1, hours=2))
    capacity = IntegerField("Ilość miejsc", validators=[NumberRange(1, message="Minimalna liczba wolnych miejsc to 1")],
                            default=30)

    def validate_start_timestamp(self, start_timestamp):
        if start_timestamp.data < datetime.datetime.now():
            raise ValidationError('Czas rozpoczęcia musi mieć przyszłą datę')

    def validate_end_timestamp(self, end_timestamp):
        if end_timestamp.data < self.start_timestamp.data:
            raise ValidationError('Czas zakonczenia musi być późniejszy od czasu rozpoczęcia')


class FindEventForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super().__init__(*args, **kwargs)

    title = StringField("Tytuł")
    owner = StringField("Organizator")
