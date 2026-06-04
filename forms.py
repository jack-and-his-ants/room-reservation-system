from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

# Załóżmy, że plik app.py i forms.py są w tym samym folderze
# Importujemy obiekt bazy danych i Model, aby sprawdzić, czy email już istnieje
from app import db, User
from wtforms import IntegerField, SelectField

class RoomForm(FlaskForm):
    number = IntegerField("Numer pokoju", validators=[DataRequired()])
    name = StringField("Nazwa sali/pokoju", validators=[DataRequired(), Length(max=40)])
    manager_id = IntegerField("ID Menedżera odpowiedzialnego", validators=[DataRequired()])
    submit = SubmitField("Zapisz pokój")

class AdminUserEditForm(FlaskForm):
    name = StringField("Imię", validators=[DataRequired(), Length(min=2, max=30)])
    surname = StringField("Nazwisko", validators=[DataRequired(), Length(min=2, max=30)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    role = SelectField("Rola", choices=[('GUEST', 'Guest'), ('EMPLOYEE', 'Employee'), ('MANAGER', 'Manager'), ('ADMIN', 'Admin')], validators=[DataRequired()])
    submit = SubmitField("Aktualizuj użytkownika")


class RegisterForm(FlaskForm):
    name = StringField("Imię", validators=[
        DataRequired(message="To pole jest wymagane."),
        Length(min=2, max=30, message="Imię musi mieć od 2 do 30 znaków.")
    ])

    surname = StringField("Nazwisko", validators=[
        DataRequired(message="To pole jest wymagane."),
        Length(min=2, max=30, message="Nazwisko musi mieć od 2 do 30 znaków.")
    ])

    email = EmailField("Adres E-mail", validators=[
        DataRequired(message="Adres e-mail jest wymagany."),
        Email(message="Wprowadź poprawny format adresu e-mail.")
    ])

    password = PasswordField("Hasło", validators=[
        DataRequired(message="Hasło jest wymagane."),
        Length(min=6, max=128, message="Hasło musi mieć co najmniej 6 znaków.")
    ])

    confirm_password = PasswordField("Potwierdź hasło", validators=[
        DataRequired(message="Musisz powtórzyć hasło."),
        EqualTo("password", message="Wprowadzone hasła nie są identyczne.")
    ])

    submit = SubmitField("Zarejestruj się")

    # Własny walidator sprawdzający bazę danych pod kątem duplikatów maili
    def validate_email(self, email):
        user = db.session.scalar(db.select(User).filter_by(email=email.data))
        if user:
            raise ValidationError("Ten adres e-mail jest już zarejestrowany w systemie.")


class LoginForm(FlaskForm):
    email = EmailField("Adres E-mail", validators=[
        DataRequired(message="Wprowadź swój e-mail."),
        Email(message="To nie jest poprawny adres e-mail.")
    ])

    password = PasswordField("Hasło", validators=[
        DataRequired(message="Wprowadź hasło.")
    ])

    submit = SubmitField("Zaloguj się")