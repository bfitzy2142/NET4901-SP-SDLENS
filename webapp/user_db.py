#!/usr/bin/env python3
"""Module to create the user table in SQL"""
import mysql.connector
from mysql.connector import errorcode


# TODO: Add handling logic if DB doesnt exist
def create_user_db():
    sql_creds = {"user": "root",
                 "password": "root",
                 "host": "127.0.0.1"}
    cnx = mysql.connector.connect(**sql_creds, database='sdlens')
    cursor = cnx.cursor()
    table = (
            "CREATE TABLE users("
            "ID INT NOT NULL AUTO_INCREMENT,"
            "name VARCHAR(100) NOT NULL,"
            "email VARCHAR(100) NOT NULL,"
            "username VARCHAR(30) NOT NULL,"
            "password VARCHAR(100) NOT NULL,"
            "PRIMARY KEY (ID) );")
    print(table)
    try:
        cursor.execute(table)
        cnx.commit()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table exists!")
