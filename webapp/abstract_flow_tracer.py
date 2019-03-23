#!/usr/bin/env python3
import abc
import json

import mysql.connector
from mysql.connector import errorcode
from authenticator import Authenticator
import requests
from requests.auth import HTTPBasicAuth


class FlowTracer(metaclass=abc.ABCMeta):
    app_auth = Authenticator()
    controller = app_auth.working_creds['controller']['controller-ip']

    def __init__(self, user, password, host, db):
        self.flow_path = []
        self.links_traversed = []
        self.sql_auth = {
            "user": user,
            "password": password,
            "host": host,
            "db": db
        }
        self.cnx = mysql.connector.connect(**self.sql_auth)


    @abc.abstractmethod
    def trace_flows(self, source, dest):
        pass
