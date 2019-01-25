#!/usr/bin/env python3
"""Monitoring Agent that discovers topology."""
import mysql.connector
from mysql.connector import errorcode
from abstract_agent import AbstractAgent


class TopologyAgent(AbstractAgent):
    def __init__(self, controller_ip):
        """"Constructor for Topology_Agent, initializes parent object."""
        super().__init__(controller_ip)
        self.create_nodes_table()

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
        sql_insert = ("INSERT INTO nodes (Node, Type) "
                      "VALUES ('{}', '{}')")
        for node in data:
            if "openflow" in node:
                node_type = "switch"
            if "host" in node:
                node_type = "host"
            self.cursor.execute(sql_insert.format(node, node_type))
            self.cnx.commit()

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

    # TODO: Consider helper function to create tables in abstract_agent
    def create_nodes_table(self):
        """Creates a nodes table in the sql DB."""
        table = (
            "CREATE TABLE nodes("
            "Node VARCHAR(32) NOT NULL,"
            "Type VARCHAR(16) NOT NULL,"
            "PRIMARY KEY (Node) );")
        try:
            self.cursor.execute(table)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                self.cursor.execute("DROP TABLE nodes")
                self.cursor.execute(table)

