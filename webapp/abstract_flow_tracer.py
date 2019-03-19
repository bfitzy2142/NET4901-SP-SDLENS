#!/usr/bin/env python3
import abc
import json

import mysql.connector
from mysql.connector import errorcode
import requests
from requests.auth import HTTPBasicAuth


class FlowTracer(metaclass=abc.ABCMeta):
    def __init__(self):
        self.flow_rule_hits = []
        self.links_traversed = []
        # TODO: Change to the dynamic auth
        self.sql_auth = {
            "user": "root",
            "password": "root",
            "host": "localhost",
            "db": "sdlens"
        }
        self.cnx = mysql.connector.connect(**self.sql_auth)
        self.controller = "134.117.89.138"


    @abc.abstractmethod
    def trace_flows(self, source, dest):
        pass
