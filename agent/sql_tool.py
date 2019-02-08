#!/usr/bin/env python3
"""Module that contains all of the required SQL tooling.

SQLTools class contains the required attributes and methods
to perform all of the SQL functions we will require for the
applications. This includes the skeleton code to DBs and
tables, queries and record entries for our various functions.
"""
import re

import mysql.connector
from mysql.connector import errorcode


class SQLTools(object):
    """[summary]

    Arguments:
        object {[type]} -- [description]
    """
    def __init__(self, user, password, host, db):
        self.sql_auth = {
            "user": user,
            "password": password,
            "host": host,
            "db": db
        }
        # TODO: Add handling in case DB doens't exist
        self.cnx = mysql.connector.connect(**self.sql_auth)
        self.cursor = self.cnx.cursor()

    def send_sql_query(self, query):
        """Helper functions that sends SQL calls."""
        # TODO: MAKE SQL SELECT and SQL INSERT modules
        self.cursor.execute(query)
        self.cnx.commit()

    def send_select(self, query):
        # TODO: Add exception handling from bad query
        select_pattern = r"SELECT .+ FROM ([\w_:]+)"
        match = re.search(select_pattern, query, re.IGNORECASE)
        table_name = match.group(1)
        if ":" in table_name:
            stripped_tbl_name = table_name.replace(":", "")
            query = query.replace(table_name, stripped_tbl_name)
        self.send_sql_query(query)

    def create_sql_table(self, table_cmd):
        if ":" in table:
            table = table.replace(":", "")
        try:
            self.send_sql_query(table)
        except mysql.connector.Error as err:
            # TODO: Consider using regex to find table name
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                self.send_sql_query(f"DROP TABLE {table}")
                self.send_sql_query(table)
