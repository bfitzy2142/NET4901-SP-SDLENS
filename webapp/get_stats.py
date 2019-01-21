#!/usr/bin/env python3
import json

import requests
from requests.auth import HTTPBasicAuth


class Odl_Stat_Collector(object):

    def __init__(self, controller_ip):
        self.controller_ip = controller_ip
        self.headers = {'Accept': 'application/json',
                        'content-type': 'application/json'}
        self.base_url = f"http://{self.controller_ip}:8181/restconf/operational/"
        self.auth = HTTPBasicAuth("admin", "admin")
        # This about addin auth to attributes
        self.topo_data = {}
    
    # Send get requests to the controller
    def send_get_request(self, url):
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response_data = response.json()
        return response_data

    def get_topo_data(self):
        url = self.base_url + "network-topology:network-topology"
        raw_topo = self.send_get_request(url)
        return raw_topo

    # Helper Function to sort nodes
    def sort_keys(self, nodes):
        sorted_nodes = {}
        for node in sorted(nodes.keys()):
            sorted_nodes[node] = nodes[node]
        return sorted_nodes
        pass

    def get_nodes(self, raw_topo):
        nodes = {}
        for node in raw_topo['network-topology']['topology'][0]['node']:
            # fix for corner case where 'termination-point' key does not exist'
            links = node.get('termination-point')
            if(isinstance(links, list) is not True):
                continue

            nodes[node['node-id']] = {}
            
            for node_int in node['termination-point']:
                nodes[node['node-id']][node_int['tp-id']] = {}
        sorted_nodes = self.sort_keys(nodes)
        return sorted_nodes

    def get_port_stats(self, node, node_name):
        odl_string = ("opendaylight-port-statistics:"
                      "flow-capable-node-connector-statistics")
        # Consider putting this in its own moethod and threading
        url = self.base_url + f"opendaylight-inventory:nodes/node/{node_name}/"
        print(url)
        raw_switch_stats = self.send_get_request(url)
        raw_int_stats = raw_switch_stats["node"][0]["node-connector"]
        for interface in raw_int_stats:
            int_id = interface["id"]
            int_stats = interface[odl_string]
            node[int_id]["rx-pckts"] = int_stats["packets"]["received"]
            node[int_id]["tx-pckts"] = int_stats["packets"]["transmitted"]
            node[int_id]["rx-bytes"] = int_stats["bytes"]["received"]
            node[int_id]["tx-bytes"] = int_stats["bytes"]["transmitted"]
            node[int_id]["rx-drops"] = int_stats["receive-drops"]
            node[int_id]["tx-drops"] = int_stats["transmit-drops"]
            node[int_id]["rx-errs"] = int_stats["receive-errors"]
            node[int_id]["tx-errs"] = int_stats["transmit-errors"]
            node[int_id]["rx-frame-errs"] = int_stats["receive-frame-error"]
            node[int_id]["rx-OverRun-errs"] = int_stats["receive-over-run-error"]
            node[int_id]["rx-CRC-errs"] = int_stats["receive-crc-error"]
        return node

    def run(self):
        topo = self.get_topo_data()
        nodes = self.get_nodes(topo)
        print(nodes["openflow:2"])
        # Do some threading for this method
        for node in nodes:
            if "host" not in node:
                nodes[node] = self.get_port_stats(nodes[node], node)
        return nodes
