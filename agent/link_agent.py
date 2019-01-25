#!/usr/bin/env python3
"""Monitoring Agent that discovers topology."""
from abstract_agent import AbstractAgent
# import json


class LinkAgent(AbstractAgent):
    """
    Author: Brad Fitzgerald
    Description: OpenDayLight RESTCONF API parser for device links.
    """

    def __init__(self, controller_ip):
        """"Initalizer for LinkAgent, initializes parent object."""
        super().__init__(controller_ip)

    def get_data(self):
        """Gets link data from ODL controller.

        Returns:
            dict -- Returns dictionary containing link information of the
            ODL managed network.
        """
        links_url = 'network-topology:network-topology/topology/flow:1/'
        url = self.base_url + links_url
        response = self.send_get_request(url)
        return response

    # Get links from the topology
    def parse_response(self, response):
        """Gets link data from ODL controller.

        Returns:
            list -- Returns list of dict src and dst key value
            pairs which each form a unique link.
        """
        # List to store the edges (links) between nodes
        connectionList = []

        for node in response['topology']:
            for link in node['link']:
                connection = {"src": link['source']['source-node'],
                              "dst": link['destination']['dest-node']}
                connectionList.append(connection)
        # Cleanup redundant connections
        cleansed_list = self.remove_redundancy(connectionList)
        return cleansed_list

    def remove_redundancy(self, connectionList):
        """Removes redundant links from the list of connections.

        Returns:
            list -- A list of unique links.
        """
        # Compare first node with second deleting similar links
        for first_connection in connectionList:
            for index, second_connection in enumerate(connectionList, start=1):
                if (self.link_comparison(first_connection, second_connection)):
                    connectionList.remove(second_connection)
        return connectionList

    # Logic for similar link detection
    def link_comparison(self, first_obj, second_obj):
        """Logic helper function to compare link objects.

        Returns:
            Boolean -- True if same link, false otherwise.
        """
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

    def store_data(self, data):
        """To be implemented"""
        pass

# Debug
# obj = LinkAgent('134.117.89.138')
# print(json.dumps(obj.parse_response(obj.get_data()), indent=1))
