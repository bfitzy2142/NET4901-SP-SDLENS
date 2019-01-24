#!/usr/bin/env python3
"""Monitoring Agent that discovers topology."""
from abstract_agent import AbstractAgent


class TopologyAgent(AbstractAgent):
    def __init__(self, controller_ip):
        super().__init__(controller_ip)
    
    def get_data(self):
        restconf_uri = "network-topology:network-topology/topology/flow:1"
        url = self.base_url + restconf_uri
        response = self.send_get_request(url)
        return response

    def parse_response(self, response):
        nodes = {}
        for node in response['topology'][0]['node']:
            nodes[node['node-id']] = {}
            for node_int in node['termination-point']:
                nodes[node['node-id']][node_int['tp-id']] = {}
        sorted_nodes = self.sort_keys(nodes)
        return sorted_nodes

    def store_data(self, data):
        pass

    def sort_keys(self, nodes):
        sorted_nodes = {}
        for node in sorted(nodes.keys()):
            sorted_nodes[node] = nodes[node]
        return sorted_nodes
