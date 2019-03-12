#!/usr/bin/env python3

"""
This file will start the monitoring application SDLens
Assumes that both OpenDaylight and your network are running

Step 1: Clear the database.
"""

import mysql.connector
import multiprocessing
import getpass
import yaml

from mysql.connector import errorcode
#from authenticator import Authenticator


def get_admin_info():
    print("""
------------------------------
| Application Information    |
------------------------------ """)
    app_IP = input("Application IP: ")
    app_username = input("Username: ")
    app_password = getpass.getpass(prompt='Password: ')

    print("""
------------------------------
| Controller Information     |
------------------------------ """)
    contr_IP = input("Controller IP: ")
    contr_username = input("Username: ")
    contr_password = getpass.getpass(prompt='Password: ')

    print("""
------------------------------
| Database Information       |
------------------------------ """)
    db_IP = input("Database IP: ")
    db_username = input("Username: ")
    db_password = getpass.getpass(prompt='Password: ')
    db_name = input("Database Name: ")
    db_CC = "DictCursor"

    credentials = {
        'application':
        {
            'app-ip': app_IP,
            'username': app_username,
            'password': app_password
        },
        'controller':
        {
            'controller-ip': contr_IP,
            'username': contr_username,
            'password': contr_password
        },
        'database':
        {
            'MYSQL_HOST': db_IP,
            'MYSQL_USER': db_username,
            'MYSQL_PASSWORD': db_password,
            'MYSQL_DB': db_name,
            'CURSORCLASS': db_CC
        }
    }
    with open('creds-new.yml', 'w') as yaml_file:
        yaml.dump(credentials, yaml_file, default_flow_style=False)


def clear_db():
    """
    Clears all tables but does not clear the users
    """

    auth = Authenticator()
    yaml_db_creds = auth.working_creds['database']
    sql_creds = {"user": yaml_db_creds['MYSQL_USER'],
             "password": yaml_db_creds['MYSQL_PASSWORD'],
             "host": yaml_db_creds['MYSQL_HOST']}
    db = auth.working_creds['database']['MYSQL_DB']
    controller_ip = auth.working_creds['controller']['controller-ip']

    try:
        connection = mysql.connector.connect(**sql_creds, database=db)
        cursor = connection.cursor()
        cursor.execute(
            f"SET @sdlens = 'sdlens';"
        )
        cursor.execute(
            f"SET @pattern = 'openflow%';"
        )
        cursor.execute(
            f"SELECT CONCAT('DROP TABLE ',"
            f"GROUP_CONCAT(CONCAT(@schema,'.',table_name)),';')"
            f"INTO @droplike"
            f"FROM information_schema.tables"
            f"WHERE @sdlens = database()"
            f"AND table_name LIKE @pattern;"
        )
        cursor.execute(
            f"PREPARE stmt FROM @droplike;"
        )
        cursor.execute(
            f"EXECUTE stmt;"
        )
        cursor.execute(
            f"DEALLOCATE PREPARE stmt;"
        )
        cursor.execute(
            f"DROP TABLE sdlens.nodes,sdlens.links;"
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            user = sql_creds['user']
            host = sql_creds['host']
            connection = mysql.connector.connect(**sql_creds)
            connection.cmd_query(f'CREATE DATABASE {db}')
            connection.database = db
            cursor = connection.cursor()
            cursor.execute(f"GRANT ALL ON {db}.* to '{user}'@'{host}';")
        else:
            print(err)


if __name__ == '__main__':
    get_admin_info()
    """
    clear_db()
    files = ["agent/__main__.py", "webapp/app.py"]
    for apps in files:
        process = multiprocessing.Process(target=None, args=())
        process.start()
    """