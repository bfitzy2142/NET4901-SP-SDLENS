#!/usr/bin/env python3
"""
MySql Parser for graphical presentation
"""
import mysql.connector
import datetime
from mysql.connector import Error
from datetime import datetime, timedelta

import json



def pull_flow_graphs(node, time):
    """ Pulls the RX and TX information from the database
        to display for the graphs page.

    Arguments:
        node [str] -- The node that holds the interface which
                      is to presented.
        time [str] -- Time ranging from 30 minutes to 10 Years
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
        "SELECT Timestamp, Active_Flows "
        f"FROM {node_st}_table0_summary WHERE "
        f"Timestamp >= '{data_start}'"
        f"AND Timestamp < '{data_end}'"
    )
    print(query)
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
        # Response == Full sql query response
        date = str(dataPoint[0])
        flow_count = int(dataPoint[1])
        
        if dataPointDict:
            old_flow_count = int(dataPointDict['rx_count'])
            dif_flow_count = flow_count - old_flow_count

            difDict = {"date": date, "rx_count": dif_flow_count}
            displayPoints.append(difDict)

        dataPointDict = {"date": date, "rx_count": flow_count}
        graphPoints.append(dataPointDict)
    return displayPoints


