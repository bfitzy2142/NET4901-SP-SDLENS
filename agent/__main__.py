#!/usr/bin/env python3
"""Main module for the agent component of our app."""
import time

import mysql.connector
from mysql.connector import errorcode

from abstract_agent import AbstractAgent
from topology_agent import TopologyAgent
from link_agent import LinkAgent
from port_counter_agent import PortCounterAgent
from device_agent import DeviceAgent

sql_creds = {"user": "root",
                 "password": "root",
                 "host": "127.0.0.1"}


# TODO: Move db functions into its own module
def create_db():
    """creates DB for our monitoring app"""
    # TODO: Dont hardcode SQL creds
    try:
        cnx = mysql.connector.connect(**sql_creds, database='sdlens')
        print("db already created")  # debug
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            cnx = mysql.connector.connect(**sql_creds)
            cnx.cmd_query('CREATE DATABASE sdlens')
            cnx.database = 'sdlens'
            cursor = cnx.cursor()
            cursor.execute("GRANT ALL ON sdlens.* to 'root'@'localhost';")
            print("DB created!")  # debug


def get_switches():
    switch_list = []
    cnx = mysql.connector.connect(**sql_creds, database='sdlens')
    cursor = cnx.cursor()
    cursor.execute("SELECT Node FROM nodes WHERE Type='switch';")
    switch_tuples = cursor.fetchall()
    for switch in switch_tuples:
        switch_list.append(switch[0])
    return switch_list

if __name__ == '__main__':
    controller_ip = "134.117.89.138"
    create_db()
    topo_agent = TopologyAgent(controller_ip)
    topo_agent.run_agent()
    switch_list = get_switches()
    link_agent = LinkAgent(controller_ip)
    link_agent.run_agent()
    counter_agents = {}
    device_agents = {}
    for switch in switch_list:
        counter_agents[switch] = PortCounterAgent(controller_ip, switch)
        device_agents[switch] = DeviceAgent(controller_ip, switch)
        device_agents[switch].run_agent()
    while True:
        for switch in switch_list:
            counter_agents[switch].run_agent()
        time.sleep(10)
    # while loops
    # SELECT Node From nodes WHERE Type="switch";

