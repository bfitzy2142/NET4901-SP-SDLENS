#!/usr/bin/env python3
"""Module to handle SQL queries for topo webapp actions"""
import mysql.connector
from mysql.connector import errorcode
from json import dumps


class Switch_Counter_Fetch():

    def __init__(self, user, password, host, db):
        """Initializer for SQLTOOLs"""
        self.sql_auth = {
            "user": user,
            "password": password,
            "host": host,
            "db": db
        }
        self.cnx = mysql.connector.connect(**self.sql_auth)
        self.cursor = self.cnx.cursor()

    def switch_query(self, switch):
        """Method reretrive counters from the db to be
        displayed on the topology page when a user clicks
        an active switch.
        """
        # Switch Statistics Table
        ctr_table = f"{switch}_counters"

        # Get lastest timestamp
        qry_latest = "SELECT max(Timestamp) FROM " + ctr_table

        self.cursor.execute(qry_latest)
        raw_result = self.cursor.fetchall()
        date = str(raw_result[0][0])

        qry_sw = "SELECT * FROM " + ctr_table + " WHERE Timestamp = '" + date + "'"

        self.cursor.execute(qry_sw)
        raw_result = self.cursor.fetchall()

        dict_list = []

        for row in raw_result:
            d = { 
                row[1]: {
                    "Rx_pckts": row[3],
                    "Tx_packs": row[4],
                    "Rx_drops": row[7],
                    "Tx_drops": row[8],
                    "Rx_errs": row[9],
                    "Tx_errs": row[10]
                }
            }
            dict_list.append(d)

        return dict_list
