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
import json

from mysql.connector import errorcode
#from authenticator import Authenticator


def get_admin_info():
    # Read from existing
    file_check = input("Does an existing credintials file exist [Y/n]: ")
    if file_check.lower() == "y":
            with open("creds-new.yml", 'r') as stream:
                try:
                    creds = yaml.load(stream)
                    print(json.dumps(creds, indent=1))
                except yaml.YAMLError as err:
                    print(err)

            change = input("Do you want to change any values [Y/n]: ")
            if change.lower() == "y":
                accept_val = 0
                while accept_val != 1:
                    print(f"Which section do you want to change?"
                          f"[Application/Controller/Database]")
                    change_section = input()
                    change_section.lower()
                    if change_section == "application":
                        application = app_info()
                        creds["application"] = application
                        update_file(creds)
                        accept_val = leave()

                    elif change_section == "controller":
                        controller = contr_info()
                        creds["controller"] = controller
                        update_file(creds)
                        accept_val = leave()

                    elif change_section == "database":
                        database = db_info()
                        creds["databse"] = database
                        update_file(creds)
                        accept_val = leave()

                    else:
                        print("Please enter a valid input.")
                        exit()
            elif change.lower() == "n":
                return
            else:
                print("Please enter a valid input.")
                exit()

    elif file_check.lower() == "n":
        application_info = app_info()
        controller_info = contr_info()
        database_info = db_info()

        credentials = {
            'application': application_info,
            'controller': controller_info,
            'database': database_info
        }
        update_file(credentials)
    else:
        print("Please enter a valid input.")
        exit()


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


def app_info():
    print("""
------------------------------
| Application Information    |
------------------------------ """)
    app_IP = input("Application IP: ")
    app_username = input("Username: ")
    app_password = getpass.getpass(prompt='Password: ')

    application = {'app-ip': app_IP,
                   'username': app_username,
                   'password': app_password
                   }
    return application


def contr_info():
    print("""
------------------------------
| Controller Information     |
------------------------------ """)
    contr_IP = input("Controller IP: ")
    contr_username = input("Username: ")
    contr_password = getpass.getpass(prompt='Password: ')

    controller = {'controller-ip': contr_IP,
                  'username': contr_username,
                  'password': contr_password
                  }
    return controller


def db_info():
    print("""
------------------------------
| Database Information       |
------------------------------ """)
    db_IP = input("Database IP: ")
    db_username = input("Username: ")
    db_password = getpass.getpass(prompt='Password: ')
    db_name = input("Database Name: ")
    db_CC = "DictCursor"

    database = {'MYSQL_HOST': db_IP,
                'MYSQL_USER': db_username,
                'MYSQL_PASSWORD': db_password,
                'MYSQL_DB': db_name,
                'CURSORCLASS': db_CC
                }
    return database


def update_file(credentials):
    with open('creds-new.yml', 'w') as yaml_file:
        yaml.dump(credentials, yaml_file, default_flow_style=False)


def leave():
    leave_bool = input("Do you want to make further changes? [Y/n]")
    if leave_bool.lower() == "y":
        leave_val = 0
    elif leave_bool.lower() == "n":
        leave_val = 1
    else:
        print("Please enter a valid input.")
        exit()
    return leave_val

if __name__ == '__main__':
    get_admin_info()
    """
    clear_db()
    files = ["agent/__main__.py", "webapp/app.py"]
    for apps in files:
        process = multiprocessing.Process(target=None, args=())
        process.start()
    """
