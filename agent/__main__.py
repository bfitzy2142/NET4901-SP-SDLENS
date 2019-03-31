#!/usr/bin/env python3
"""Main module for the agent component of our app."""
import time
import threading

import mysql.connector
from mysql.connector import errorcode

from authenticator import Authenticator
from abstract_agent import AbstractAgent
from topology_agent import TopologyAgent
from link_agent import LinkAgent
from port_counter_agent import PortCounterAgent
from device_agent import DeviceAgent
from flow_agent import FlowAgent


auth = Authenticator()
yaml_db_creds = auth.working_creds['database']
sql_creds = {"user": yaml_db_creds['MYSQL_USER'],
             "password": yaml_db_creds['MYSQL_PASSWORD'],
             "host": yaml_db_creds['MYSQL_HOST']}
db = auth.working_creds['database']['MYSQL_DB']
controller_ip = auth.working_creds['controller']['controller-ip']


# TODO: Move db functions into its own module
def create_db():
    """creates DB for our monitoring app"""
    try:
        cnx = mysql.connector.connect(**sql_creds, database=db)
        print("db already created")  # debug
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            user = sql_creds['user']
            host = sql_creds['host']
            cnx = mysql.connector.connect(**sql_creds)
            cnx.cmd_query(f'CREATE DATABASE {db}')
            cnx.database = 'sdlens'
            # cnx.commit()
            cursor = cnx.cursor()
            # Temporary fix to use localhost
            cursor.execute(f"GRANT ALL ON {db}.* to '{user}'@'localhost';")
            print("DB created!")  # debug


def get_switches():
    switch_list = []
    cnx = mysql.connector.connect(**sql_creds, database=db)
    cursor = cnx.cursor()
    cursor.execute("SELECT Node FROM nodes WHERE Type='switch'")
    switch_tuples = cursor.fetchall()
    for switch in switch_tuples:
        switch_list.append(switch[0])
    return switch_list


def store_avgAgent_time(average_time):
    cnx = mysql.connector.connect(**sql_creds, database=db)
    cursor = cnx.cursor()
    sql_insert = (f"INSERT INTO average_agent_time"
                  f"(average_time) VALUES ({average_time})")
    query = sql_insert.format(average_time)
    cursor.execute(query)
    cnx.commit()


def agent_runner(counter_agents, flow_agents, switch):
    print(f'\nUpdating DB for SW: {switch}.')
    try:  # If topo changes mid execution agents are error prone
        counter_agents[switch].run_agent()
        flow_agents[switch].run_agent()
    except:
        print(f'Ran into error on SW: {switch}')

if __name__ == '__main__':
    print("***SDLENS DATABASE AGENT UTILITY***")
    print('Checking database-->')
    create_db()
    print('\n1) Building Topology Datastructures-->')
    topo_agent = TopologyAgent(controller_ip)
    topo_agent.run_agent()
    switch_list = get_switches()
    link_agent = LinkAgent(controller_ip)
    link_agent.run_agent()
    counter_agents = {}
    device_agents = {}
    flow_agents = {} # May have to change this if many flow tables
    creator_threads = []
    print('\n2)Populating Port Counter Tables-->')
    # TODO: THREAD HERE
    for index, switch in enumerate(switch_list):
        print(f'{switch}: {index+1}/{len(switch_list)}')
        counter_agents[switch] = PortCounterAgent(controller_ip, switch)
        device_agents[switch] = DeviceAgent(controller_ip, switch)
        flow_agents[switch] = FlowAgent(controller_ip, switch, 0)
        # device_agents[switch].run_agent()
        c_t = threading.Thread(target=device_agents[switch].run_agent)
        c_t.start()
        creator_threads.append(c_t)
    for thread in creator_threads:
        thread.join()
    while True:
        print('DB Update Loop-->')
        # Delete and repopulate tables to keep topology relevant
        topo_agent.delete_stale_nodes()
        topo_agent.populate_host_table()
        link_agent.run_agent()
        loop_start = time.time()
        # times = []
        threads = []
        # Update switch and flow counters
        
        for index, switch in enumerate(switch_list):
            print(f'\nUpdating DB for SW: {switch}.\nSwitch {index+1}/{len(switch_list)}')
            t = threading.Thread(target=agent_runner, args=(counter_agents, flow_agents, switch))
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()
            
        """    
        average_time = sum(times)/len(switch_list)
        print(f'Average switch update time: {average_time} seconds.')
        store_avgAgent_time(average_time)
        times.clear()
        """
        threads.clear()
        loop_end = time.time()
        print(f'Total agent loop took {loop_end - loop_start} seconds')
        print('\nSleeping 10 seconds...')
        time.sleep(10)
