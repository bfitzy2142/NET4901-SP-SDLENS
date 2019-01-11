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
        # This about addin auth to attributes
        self.topo_data = {}

    def get_topo_data(self):
        url = self.base_url + "network-topology:network-topology"
        topo_request = requests.get(url, headers=self.headers, auth=HTTPBasicAuth("admin", "admin"))
        raw_topo = topo_request.json()
        return raw_topo

    def sort_keys(self, keys):


    def get_nodes(self, raw_topo):
        nodes = {}
        for node in raw_topo['network-topology']['topology'][0]['node']:
            # fix for corner case where 'termination-point' key does not exist
            links = node.get('termination-point')
            if(isinstance(links, list) is not True):
                continue

            nodes[node['node-id']] = {}
            
            for node_int in node['termination-point']:
                nodes[node['node-id']][node_int['tp-id']] = {}
        # order nodes from smallest to largest. I.e: openflow:1-openflow:2,etc
        sortedKeys = sorted(nodes.keys())
        sortedNodes = {}
        for device in sortedKeys:
            sortedNodes[device] = nodes[device]
        return sortedNodes

    def get_port_stats(self, node, node_name):
        odl_string = "opendaylight-port-statistics:flow-capable-node-connector-statistics"
        # Consider putting this in its own moethod and threading
        for node_int in node:
            
            url = self.base_url + "opendaylight-inventory:nodes/node/{node_name}/node-connector/{node_int}"
            int_stats_req = requests.get(url, headers=self.headers, auth=HTTPBasicAuth("admin", "admin"))
            raw_int_stats = int_stats_req.json()
            int_stats = raw_int_stats["node-connector"][0][odl_string]
            node[node_int]["rx-pckts"] = int_stats["packets"]["received"]
            node[node_int]["tx-pckts"] = int_stats["packets"]["transmitted"]
            node[node_int]["rx-bytes"] = int_stats["bytes"]["received"]
            node[node_int]["tx-bytes"] = int_stats["bytes"]["transmitted"]
            node[node_int]["rx-drops"] = int_stats["receive-drops"]
            node[node_int]["tx-drops"] = int_stats["transmit-drops"]
            node[node_int]["rx-errs"] = int_stats["receive-errors"]
            node[node_int]["tx-errs"] = int_stats["transmit-errors"]
            node[node_int]["rx-frame-errs"] = int_stats["receive-frame-error"]
            node[node_int]["rx-OverRun-errs"] = int_stats["receive-over-run-error"]
            node[node_int]["rx-CRC-errs"] = int_stats["receive-crc-error"]
        return node

    def run(self):
        topo = self.get_topo_data()
        nodes = self.get_nodes(topo)
        for node in nodes:
            if "host" not in node:
                nodes[node] = self.get_port_stats(nodes[node], node)
        return nodes


