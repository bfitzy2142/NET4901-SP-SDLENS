#!/usr/bin/env python3
"""Main module for the agent component of our app."""
import mysql.connector
from mysql.connector import errorcode

from abstract_agent import AbstractAgent
from topology_agent import TopologyAgent
from link_agent import LinkAgent


# TODO: Move db functions into its own module
def create_db():
    """creates DB for our monitoring app"""
    # TODO: Dont hardcode SQL creds
    sql_creds = {"user": "root",
                 "password": "root",
                 "host": "127.0.0.1"}
    try:
        cnx = mysql.connector.connect(**sql_creds, database='sdlens')
        print("db already created") # debug
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            cnx = mysql.connector.connect(**sql_creds)
            cnx.cmd_query('CREATE DATABASE sdlens')
            cnx.database = 'sdlens'
            cursor = cnx.cursor()
            cursor.execute("GRANT ALL ON sdlens.* to 'root'@'localhost';")
            print("DB created!") #d debug

if __name__ == '__main__':
    create_db()