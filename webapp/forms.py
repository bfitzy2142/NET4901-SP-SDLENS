#!/usr/bin/env python3
"""Module manages all form classes required by SDLens webapp."""
from wtforms import Form, StringField, SelectField, TextAreaField, PasswordField, validators


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


class GraphForm(Form):
    """
    Class to select the device and interface for graphs
    """
    node = StringField('Node (Switch #)', [
        validators.length(min=1, max=3),
        validators.Regexp("\d{1,3}")
        ])
    interface = StringField('Interface (Int #)', [
        validators.length(min=1, max=2),
        validators.Regexp("\d{1,2}")
        ])
    time = SelectField('Graph Duration', choices=[(
             '1', '30 Minutes'), ('2', '1 Hour'),
            ('3', '2 Hours'), ('4', '6 Hours'),
            ('5', '1 Day'), ('6', 'All Time')])
