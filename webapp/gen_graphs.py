#!/usr/bin/env python3
"""
@author: Sam Cook
MySql Parser for graphical presentation
"""
import mysql.connector
from mysql.connector import Error

import json


class sql_graph_info(object):
    def __init__(self, node, interface):
        """
        Initializer for the sql_graph_info Object.
        """
        self.node = node
        self.interface = interface

    def db_pull(self, node, interface):
        """
        Pulls the port counters and timestamp from each table in the database.
        """
        query = (
            f"SELECT timestamp, Rx_pckts, Tx_pckts, Rx_drops, Tx_drops "
            f"FROM {node}_counters WHERE "
            f"Interface='{interface}'"
        )

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="sdlens"
        )
        cur = mydb.cursor()
        cur.execute(query)
        response = cur.fetchall()

        graphPoints = []
        displayPoints = []
        dataPointDict = {}

        for dataPoint in response:
            date = str(dataPoint[0])
            rx_count = dataPoint[1]
            tx_count = dataPoint[2]
            rx_drops = dataPoint[3]
            tx_drops = dataPoint[4]

            if dataPointDict:
                old_rx_c = dataPointDict['rx_count']
                old_tx_c = dataPointDict["tx_count"]
                old_rx_d = dataPointDict["rx_drops"]
                old_tx_d = dataPointDict["tx_drops"]

                dif_rx_c = rx_count - old_rx_c
                dif_tx_c = tx_count - old_tx_c
                dif_rx_d = rx_drops - old_rx_d
                dif_tx_d = tx_drops - old_tx_d

                difDict = {"date": date, "rx_count": dif_rx_c,
                           "tx_count": dif_tx_c,
                           "rx_drops": dif_rx_d,
                           "tx_drops": dif_tx_d}
                displayPoints.append(difDict)

            dataPointDict = {"date": date, "rx_count": rx_count,
                             "tx_count": tx_count, "rx_drops": rx_drops,
                             "tx_drops": tx_drops}
            graphPoints.append(dataPointDict)
        return displayPoints
