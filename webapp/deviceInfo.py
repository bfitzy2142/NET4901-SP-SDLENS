#!/usr/bin/env python3

import requests
from requests.auth import HTTPBasicAuth
import json

class odl_switch_info(object):
    
    
    def __init__(self, controller_ip):
        self.controller_ip = controller_ip
        self.headers = {'Accept': 'application/json', 'content-type': 'application/json'}
        #This about addin auth to attributes
        self.topo_data = {}

    def get_topo_data(self):
        url = f"http://{self.controller_ip}:8181/restconf/operational/opendaylight-inventory:nodes"
        topo_request = requests.get(url, headers=self.headers, auth=HTTPBasicAuth("admin", "admin"))
        raw_topo = topo_request.json()
        return raw_topo
        

    def get_node_connector(self, raw_topo):
        nodes = {}
        fni = 'flow-node-inventory:'
        print(json.dumps(raw_topo['nodes'], indent=1))
        for node in raw_topo['nodes']['node']:
            
            nodes[node['id']] = {}
            for i in node['node-connector']:
            	nodes[node['id']][i['id']] = {}
            	nodes[node['id']][i['id']]['port_num'] = i[fni + 'port-number']
            	nodes[node['id']][i['id']]['speed'] = i[fni + 'current-speed']
            	nodes[node['id']][i['id']]['name'] = i[fni + 'name']
            	nodes[node['id']][i['id']]['hwaddr'] = i[fni + 'hardware-address']

        #print(nodes)

        #order nodes from smallest to largest. I.e: openflow:1-openflow:2,etc
        sortedKeys=sorted(nodes.keys())
        sortedNodes={}
        for device in sortedKeys:
            sortedNodes[device]=nodes[device]
        
        return sortedNodes
  
    def run(self):
        topo = self.get_topo_data()
        nodes = self.get_node_connector(topo)
        return nodes