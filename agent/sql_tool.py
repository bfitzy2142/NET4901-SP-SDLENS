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
    """Class offering various SQL interaction functionalities."""
    def __init__(self, user, password, host, db):
        """Initializer for SQLTOOLs"""
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

    def send_sql_query2(self, query):
        """Helper functions that sends SQL calls."""
        # TODO: MAKE SQL SELECT and SQL INSERT modules
        self.cursor.execute(query)
        # self.cnx.commit()

    def send_select(self, query):
        """Send SELECT statement to the database.

        Arguments:
            query {String} -- SELECT query to be executed against
            the database.

        Returns:
            List -- Returns a list of tuples that correspond to
            the records returned by the database.
        """
        # TODO: Add exception handling from bad queries

        # We use regex to find table name and remove and ':' from the name
        select_pattern = r"SELECT .+ FROM ([\w_:]+)"
        match = re.search(select_pattern, query, re.IGNORECASE)
        table_name = match.group(1)
        if ":" in table_name:
            query = self.clean_table_name(query, table_name)
        self.send_sql_query2(query)
        return self.cursor.fetchall()

    def send_insert(self, query):
        """Send INSERT statements to the database.

        Arguments:
            query {String} -- INSERT QUERY to be executed.
        """
        # TODO: Add exception handling from bad queries

        # More regex to make sure our table names don't have colons
        insert_pattern = r"INSERT INTO ([\w_:]+)"
        match = re.search(insert_pattern, query, re.IGNORECASE)
        table_name = match.group(1)
        if ":" in table_name:
            query = self.clean_table_name(query, table_name)
        self.send_sql_query(query)

    def clean_table_name(self, query, table_name):
        """Removes colons from table names.
        openflow:1 -> openflow1

        Arguments:
            query {String} -- Entire SQL query
            table_name {String} -- Table name from sql query

        Returns:
            String -- returns same query but with the properly formatted
            names
        """
        stripped_tbl_name = table_name.replace(":", "")
        query = query.replace(table_name, stripped_tbl_name)
        return query

    def create_sql_table(self, query):
        """Sends SQL query to create a database table.

        It will recreate the table if it already exists in the database.
        Arguments:
            query {string} -- SQL CREATE TABLE query
        """
        table_pattern = r"CREATE TABLE ([\w_:]+)"
        match = re.search(table_pattern, query, re.IGNORECASE)
        table_name = match.group(1)
        if ":" in table_name:
            query = self.clean_table_name(query, table_name)

        # Check to see if tbable exists already
        try:
            self.send_sql_query(query)
        # Recreate if table already exists
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                table_name = table_name.replace(":", "")
                self.send_sql_query(f"DROP TABLE {table_name}")
                self.send_sql_query(query)
