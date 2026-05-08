from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, Regexp


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


class ReviewForm(FlaskForm):
    rating = IntegerField(
        'Overall rating (1–10)',
        validators=[DataRequired(), NumberRange(min=1, max=10, message='Rating must be between 1 and 10.')],
    )
    difficulty = IntegerField(
        'Difficulty (1–10)',
        validators=[DataRequired(), NumberRange(min=1, max=10, message='Difficulty must be between 1 and 10.')],
    )
    workload_hours = IntegerField(
        'Hours per week',
        validators=[Optional(), NumberRange(min=0, max=100)],
    )
    semester_taken = StringField(
        'Semester taken (e.g. S1 2024)',
        validators=[Optional(), Length(max=32)],
    )
    body = TextAreaField(
        'Your review',
        validators=[DataRequired(), Length(min=10, max=2000, message='Review must be between 10 and 2000 characters.')],
    )
    submit = SubmitField('Submit review')

