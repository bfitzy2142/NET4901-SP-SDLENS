#!/usr/bin/env python3
"""
    OpenDayLight RESTCONF API parser for topology information
    December 2018
    SDLENS Monitoring Solution
    Brad Fitzgerald
    bradfitzgerald@cmail.carleton.ca

***DEPRECATED***
Use this module if you wish to query topology infomation
from the OpenDaylight controller rather than a MySQL DB.

"""
import requests
import re
# uncomment for debugging -->
# import json
# import time


class odl_topo_builder(object):

    def __init__(self, controllerIP):
        self.controllerIP = controllerIP
        self.topo_url = 'http://' + controllerIP + \
            ':8181/restconf/operational/network-topology:network-topology'

    # get json data to parse
    def query_controller(self):
        # fetch raw json from topology API
        api_response = requests.get(self.topo_url, auth=('admin', 'admin'))
        return api_response

    # get nodes from the topology
    def parse_devices(self, api_response):
        # odl managed nodes
        deviceList = []

        # Walk through all node information.
        for flows in api_response.json()['network-topology']['topology']:
            if re.match(r"^flow:[0-9]+$", flows['topology-id']):
                node_list = flows['node']
                for node in node_list:
                    deviceList.append(node['node-id'])
        return sorted(deviceList)

    # Get links from the topology
    def parse_links(self, api_response):
        # List to store the edges (links) between nodes
        connectionList = []
        # List of dicts with info for link src & dst termination points
        links = api_response.json()['network-topology']['topology'][0]['link']      
        for link in links:
            connection = {"src": link['source']['source-node'],
                          "dst": link['destination']['dest-node']}
            connectionList.append(connection)
        # Cleanup redundant connections
        cleansed_list = self.remove_redundancy(connectionList)
        return cleansed_list

    # Compare first node with second deleting similar links
    def remove_redundancy(self, connectionList):
        for first_connection in connectionList: 
            for second_connection in connectionList[1:]:
                if (self.link_comparison(first_connection, second_connection)):
                    connectionList.remove(second_connection)
        return connectionList

    # Logic for similar link detection
    def link_comparison(self, first_obj, second_obj):
        condition_one = False
        condition_two = False
        if (first_obj['src'] == second_obj['dst']):
            condition_one = True
        if (first_obj['dst'] == second_obj['src']):
            condition_two = True
        if (condition_one is True and condition_two is True):
            return True
        else:
            return False

    # Gets topology data and stores as a dict
    def fetch_topology(self):
        api_response = self.query_controller()
        deviceList = self.parse_devices(api_response)
        connectionList = self.parse_links(api_response)        
        topologyInfo = {'devices': deviceList,
                        'connections': connectionList,
                        'controller': self.controllerIP}
        return topologyInfo

# Uncomment for debugging-->
    """
    def debugging_modlue(self):
        start_time = time.time()
        print(json.dumps(self.fetch_topology(), indent=1))
        print("Executed in: %s seconds!" % (time.time() - start_time))
    """
# Enter IP of controller
# obj = odl_topo_builder('192.168.0.17')
# obj.debugging_modlue()
