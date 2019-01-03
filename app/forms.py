from app.models import Users
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, EqualTo, ValidationError


class RegistrationForms(FlaskForm):
    username = StringField('Uporabniško ime',
                           validators=[InputRequired()])
    password = PasswordField('Geslo',
                             validators=[InputRequired(),
                                         EqualTo('confirm_password', message='Geslo se ne ujema')])
    confirm_password = PasswordField('Potrdi geslo',
                                     validators=[InputRequired()])
    submit = SubmitField('Registracija')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already in use")


class LoginForms(FlaskForm):
    username = StringField('Uporabniško ime',
                           validators=[InputRequired()])
    password = PasswordField('Geslo',
                             validators=[InputRequired()])
    remember_me = BooleanField('Zapomni si me')
    submit = SubmitField('Vpis')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError("Uporabniško ime ni registrirano")


class AccountForms(FlaskForm):
    change_password = PasswordField('Spremeni geslo',
                                    validators=[EqualTo('change_password_confirm', message='Geslo se ne ujema')])
    change_password_confirm = PasswordField('Potrdi spremembo gesla')
    user_image = FileField('Spremeni profilno sliko', validators=[
        FileAllowed(['jpg', 'png'])
    ])
    submit = SubmitField('Potrdi')


class PostForm(FlaskForm):
    title = StringField('Naslov', validators=[InputRequired()])
    content = TextAreaField('Vsebina', validators=[InputRequired()])
    submit = SubmitField('Objavi')
