from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


UWA_EMAIL_RE = r'^[^@\s]+@student\.uwa\.edu\.au$'


class RegisterForm(FlaskForm):
    email = StringField(
        'UWA student email',
        validators=[
            DataRequired(),
            Email(),
            Regexp(UWA_EMAIL_RE, message='Use your @student.uwa.edu.au email address.'),
        ],
    )
    student_id = StringField(
        'Student ID',
        validators=[
            DataRequired(),
            Regexp(r'^\d{8}$', message='Student ID must be 8 digits.'),
        ],
    )
    display_name = StringField('Display name', validators=[DataRequired(), Length(max=80)])
    faculty = StringField('Faculty', validators=[Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirm password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')],
    )
    submit = SubmitField('Create account')


class LoginForm(FlaskForm):
    email = StringField(
        'UWA student email',
        validators=[
            DataRequired(),
            Email(),
            Regexp(UWA_EMAIL_RE, message='Use your @student.uwa.edu.au email address.'),
        ],
    )
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')

