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
        for node in raw_topo['nodes'][0]['node-connector']:
            #fix for corner case where node does not contain key 'termination point' 
            links=node.get('node-connector')
            if(isinstance(links, list)!=True):
                continue

            nodes[node['id']] = {} # help
            
            for flow-node-inventory in node['node-connector']:
                nodes[node['id']][node_int['tp-id']] = {} #help
        #order nodes from smallest to largest. I.e: openflow:1-openflow:2,etc
        sortedKeys=sorted(nodes.keys())
        sortedNodes={}
        for device in sortedKeys:
            sortedNodes[device]=nodes[device]
        
        return sortedNodes
        
    def get_swtich_info(self, node, node_name):
	odl_string = "" #0 because its the first with no name??
	for node_int in node:
		url = f"http://{self.controller_ip}:8181/restconf/operational/opendaylight-inventory:nodes"
		device_stats_req = requests.get(url, headers=self.headers, auth=HTTPBasicAuth("admin", "admin"))
		raw_int_stats = device_stats_req.json()
		int_stats = raw_int_stats["node-connector"][0][odl_string]
		
		node[node_int]["id"] = device_stats_req["openflow"]
		node[node_int]["flow-node-inventory"] = device_stats_req["port-number"]
		node[node_int]["flow-node-inventory"] = device_stats_req["current-speed"]
		node[node_int]["flow-node-inventory"] = device_stats_req["name"]
		node[node_int]["flow-node-inventory"] = device_stats_req["state"]
		node[node_int]["flow-node-inventory"] = device_stats_req["hardware-address"]
	return node
  
    def run(self):
        topo = self.get_topo_data()
        nodes = self.get_nodes(topo)
        for node in nodes:
            if "host" not in node:
                nodes[node] = self.get_port_stats(nodes[node], node)
        return nodes

        
def odl_testing():
    o = odl_switch_info("192.168.0.17")
    topo = o.get_topo_data()
    nodes = o.get_nodes(topo)
    for node in nodes:
        if "host" not in node:
            #print(node)
            nodes[node] = o.get_port_stats(nodes[node], node)
        print(node, "{")
        print(nodes[node])
        print("}")
        
