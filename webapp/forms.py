#!/usr/bin/env python3
"""Module manages all form classes required by SDLens webapp."""
from wtforms import Form, StringField, TextAreaField, PasswordField, validators


class RegisterForm(Form):
    """RegisterForm class manages the values to register a user
    for SDLens app."""
    name = StringField('Name', [validators.Length(min=1, max=100)])
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
