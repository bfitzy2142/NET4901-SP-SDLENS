#!/usr/bin/env python3

"""
This file will start the monitoring application SDLens
Assumes that both OpenDaylight and your network are running

Step 1: Clear the database.
"""

import mysql.connector
import multiprocessing
import getpass
import json
import yaml
import os
import sys
import signal

from mysql.connector import errorcode


def get_admin_info():
    # Read from existing
    comp_user = getpass.getuser()
    file_check = input("Does an existing credintials file exist [Y/n]: ")
    if file_check.lower() == "y":
            with open(f"/home/{comp_user}/.sdlens/creds.yml", 'r') as stream:
                try:
                    creds = yaml.load(stream)
                    #print(json.dumps(creds, indent=1))
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
    comp_user = getpass.getuser()
    with open(f"/home/{comp_user}/.sdlens/creds.yml", "r") as file:
        try:
            working_creds = yaml.load(file)
        except yaml.YAMLError as err:
            print(err)

    yaml_db_creds = working_creds['database']
    sql_creds = {"user": yaml_db_creds['MYSQL_USER'],
                 "password": yaml_db_creds['MYSQL_PASSWORD'],
                 "host": yaml_db_creds['MYSQL_HOST']}
    db = working_creds['database']['MYSQL_DB']

    check_db = input("Does the database exist [Y/n]: ")
    if check_db.lower() == "n":
        try:
            user = sql_creds['user']
            host = sql_creds['host']
            connection = mysql.connector.connect(**sql_creds)
            connection.cmd_query(f'CREATE DATABASE {db}')
            connection.database = db
            cursor = connection.cursor()
            cursor.execute(f"GRANT ALL ON {db}.* to '{user}'@'{host}';")
        except mysql.connector.Error as err:
            print(str(err))
    elif check_db.lower() == "y":
        pass
    else:
        print("Please enter a valid input.")
        exit()

    table_check = input("Does the database need to be cleared [Y/n]:")
    if table_check.lower() == "y":
        try:
            connection = mysql.connector.connect(**sql_creds, database=db)
            cursor = connection.cursor(buffered=True)
            set_1 = f"SET @sdlens = '{db}';"
            set_2 = "SET @pattern = 'openflow%';"
            select = (f"SELECT CONCAT('DROP TABLE ',GROUP_CONCAT(TABLE_NAME)) "
                    f"INTO @drop "
                    f"FROM information_schema.TABLES "
                    f"WHERE TABLE_SCHEMA = @sdlens "
                    f"AND TABLE_NAME LIKE @pattern;")
            prepare = "PREPARE stmt FROM @drop;"
            execute = "EXECUTE stmt;"
            deallocate = "DEALLOCATE PREPARE stmt;"
            drop_others = "DROP TABLE sdlens.nodes,sdlens.links;"

            cursor.execute(set_1)
            cursor.execute(set_2)
            cursor.execute(select)
            try:
                cursor.execute(prepare)
                cursor.execute(execute)
                cursor.execute(deallocate)
            finally:
                try:
                    cursor.execute(drop_others)
                except mysql.connector.Error as err:
                    if err.errno == "1051":
                        print("Test")

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
                print(str(err))
                print("Tables already cleared")
    elif table_check.lower() == "n":
        pass
    else:
        print("Please enter a valid input.")
        exit()


def app_info():
    print("""
------------------------------
| Application Information    |
------------------------------ """)
    app_IP = input("Application IP: ")
    app_SK = "secret123"
    app_username = input("Username: ")
    app_password = getpass.getpass(prompt='Password: ')

    application = {'app-ip': app_IP,
                   'secret_key': app_SK,
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
    comp_user = getpass.getuser()
    folder_check = os.path.exists(f'/home/{comp_user}/.sdlens')
    if not folder_check:
        os.system(f'mkdir /home/{comp_user}/.sdlens')
    with open(f'/home/{comp_user}/.sdlens/creds.yml', 'w') as yaml_file:
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


def signal_handler(sig, frame):
        os.system("kill $(ps aux | grep 'agent/__main__.py' | awk '{print $2}')")
        os.system("kill $(ps aux | grep 'webapp/app.py' | awk '{print $2}')")
        sys.exit(0)


if __name__ == '__main__':
    get_admin_info()
    clear_db()

    #Questionable Multi-threading
    os.system("python3 webapp/app.py &")
    os.system("python3 agent/__main__.py &")

    #Killing the processes
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()