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
        graph_info = {}
        query = (
            f"SELECT timestamp, Rx_pckts FROM {node}_counters WHERE "
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

        for dataPoint in response:
            date = str(dataPoint[0])
            counter = dataPoint[1]
            dataPointDict = {"date" : date, "counter" : counter}
            graphPoints.append(dataPointDict)

        return graphPoints

# Add tx to dict rather than redooing it again