#!/usr/bin/env python3
"""
@author: Brad Fitzgerald
OpenDayLight RESTCONF API parser for topology information
"""
import requests
import re
 
#for debugging -->
#import json

class odl_topo_builder(object):

    def __init__(self, controllerIP):
        self.controllerIP = controllerIP
        self.odl_topo_url = 'http://' + controllerIP + \
            ':8181/restconf/operational/network-topology:network-topology'

    def fetchTopology(self):
        # List to store the devices in the topology
        deviceList = []
        # List to store the edges (links) between nodes
        connectionList = []

        # fetch state of topology from ODL REST API.
        response = requests.get(self.odl_topo_url, auth=('admin', 'admin'))

        # Find information about nodes in retrieved JSON file.
        for nodes in response.json()['network-topology']['topology']:
            if re.match(r"^flow:[0-9]+$", nodes['topology-id']):
                # Walk through all node information.
                node_info = nodes['node']
                # Look for MAC and IP addresses in node information.
                for node in node_info:
                    deviceList.append(node['node-id'])

        # get links between switches
        for links in response.json()['network-topology']['topology'][0]['link']:

            connection = {"src": links['source']['source-node'],
                          "dst": links['destination']['dest-node']}
            connectionList.append(connection)

            # remove redundant connections
            for firstNode in connectionList:
                for index, secondNode in enumerate(connectionList, start=1):
                    if (firstNode['src'] == secondNode['dst'] and firstNode['dst'] == secondNode['src']):
                        connectionList.remove(secondNode)

        topologyInfo = {'devices': deviceList,
                        'connections': connectionList, 'controller': self.controllerIP}
        #for debugging -->
        #print(json.dumps(topologyInfo,indent=1))
        return topologyInfo
