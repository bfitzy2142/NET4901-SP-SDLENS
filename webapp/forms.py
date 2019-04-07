#!/usr/bin/env python3
"""Module manages all form classes required by SDLens webapp."""
from wtforms import Form, StringField, SelectField, TextAreaField, PasswordField, validators
from topo_db import Topo_DB_Interactions
from authenticator import Authenticator
from time import sleep


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

    auth = Authenticator()
    # Get SQL Auth & Creds
    yaml_db_creds = auth.working_creds['database']
    sql_creds = {"user": yaml_db_creds['MYSQL_USER'],
                 "password": yaml_db_creds['MYSQL_PASSWORD'],
                 "host": yaml_db_creds['MYSQL_HOST']
                 }
    db = auth.working_creds['database']['MYSQL_DB']
    topo_db = Topo_DB_Interactions(**sql_creds, db=db)
    while True:
        try:
            switches = topo_db.get_switches()
            break
        except:
            print('Waiting for DB to be ready!')
            sleep(5)
            continue
    print('got here')
    
    switch_tuple = []
    for index, switch in enumerate(switches):
        tup = index+1, switch
        switch_tuple.append(tup)
    
    node = SelectField('Node', choices=switch_tuple)
    interface = SelectField('Interface', choices=[('-', '-')])
    
    time = SelectField('Graph Duration', choices=[(
             '1', '30 Minutes'), ('2', '1 Hour'),
            ('3', '2 Hours'), ('4', '6 Hours'),
            ('5', '1 Day'), ('6', 'All Time')])
