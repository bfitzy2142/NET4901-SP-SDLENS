#!/usr/bin/env python3
"""Monitoring Agent that discovers topology."""
from abstract_agent import AbstractAgent


class TopologyAgent(AbstractAgent):
    def __init__(self, controller_ip):
        """"Constructor for Topology_Agent, initializes parent object."""
        super().__init__(controller_ip)

    def get_data(self):
        """Gets topology data from ODL controller.

        Returns:
            dict -- Returns dictionary with the raw response of the ODL
            controller.
        """
        restconf_uri = "network-topology:network-topology/topology/flow:1"
        url = self.base_url + restconf_uri
        response = self.send_get_request(url)
        return response

    def parse_response(self, response):
        """Parses API response for desired node information

        Arguments: =
            response {dictionary} -- Raw response from the ODL controller to be
                parsed

        Returns:
            dict -- Returns a dictionary with the nodes and node interfaces
                defined.
        """
        nodes = {}
        for node in response['topology'][0]['node']:
            nodes[node['node-id']] = {}
            for node_int in node['termination-point']:
                nodes[node['node-id']][node_int['tp-id']] = {}
        sorted_nodes = self.sort_keys(nodes)
        return sorted_nodes

    def store_data(self, data):
        """To be implemented"""
        pass

    def sort_keys(self, nodes):
        """Sorts the dictionary of nodes alphabetically

        Arguments:
            nodes {dict} -- Dictionary of nodes.

        Returns:
            [dict] -- Returns the sorted dictionary of nodes.
        """
        sorted_nodes = {}
        for node in sorted(nodes.keys()):
            sorted_nodes[node] = nodes[node]
        return sorted_nodes
