#!/usr/bin/env python3
"""
@author: Sam Cook
MySql Parser for graphical presentation
"""
import mysql.connector
import datetime
from mysql.connector import Error
from datetime import datetime, timedelta

import json


class sql_graph_info(object):
    def __init__(self, node, interface, time):
        """
        Initializer for the sql_graph_info Object.
        """
        self.node = node
        self.interface = interface
        self.time = time

    def db_pull(self, node, interface, time):
        """ Pulls the RX and TX information from the database
            to display for the graphs page.
        
        Arguments:
            node [str] -- The node that holds the interface which
                          is to presented.
            interface [str] -- The interface in which the counter
                               information will be based off of.

        Returns:
            dict -- containing arrays of the counter values at
                    their coresponding timestamp.
        """
        data_end = datetime.now()
        if time == '1':
            data_start = datetime.now() - timedelta(hours=0, minutes=30)
        elif time == '2':
            data_start = datetime.now() - timedelta(hours=1)
        elif time == '3':
            data_start = datetime.now() - timedelta(hours=2)
        elif time == '4':
            data_start = datetime.now() - timedelta(hours=6)
        elif time == '5':
            data_start = datetime.now() - timedelta(days=1)
        else:
            data_start = datetime.now() - timedelta(days=3650)
        data_end.strftime('%Y-%m-%d %H:%M:%S')
        data_start.strftime('%Y-%m-%d %H:%M:%S')

        node_st = "openflow" + node
        query = (
            f"SELECT timestamp, Rx_pckts, Tx_pckts, Rx_drops, Tx_drops "
            f"FROM {node_st}_counters WHERE "
            f"Interface='openflow:{node}:{interface}'"
            f"AND timestamp >= '{data_start}'"
            f"AND timestamp < '{data_end}'"
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
