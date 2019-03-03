#!/usr/bin/env python3
"""Monitoring Agent that discovers topology."""
import mysql.connector
from mysql.connector import errorcode
from abstract_agent import AbstractAgent
from json import dumps

class TopologyAgent(AbstractAgent):

    def __init__(self, controller_ip):
        """"Initalizer for LinkAgent, initializes parent object."""
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
        # TODO: Make this data structure more efficient
        nodes = {}
        for node in response['topology'][0]['node']:
            nodes[node['node-id']] = {}
            for node_int in node['termination-point']:
                nodes[node['node-id']][node_int['tp-id']] = {}
        sorted_nodes = self.sort_keys(nodes)
        return sorted_nodes

    def store_data(self, data):
        """Stores our node data in the sdlens database."""
        # TODO: Consider threading?
        for node, interfaces in data.items():
            if "openflow" in node:
                node_type = "switch"
                self.create_int_table(node)
                self.store_interfaces(node, interfaces)
            if "host" in node:
                node_type = "host"
            self.store_nodes(node, node_type)

    def store_nodes(self, node, node_type):
        """Stores node names/type in the Nodes DB table.

        Arguments:
            node {string} -- Node Name: e.g. 'openflow:1'
            node_type {string} -- Node type: e.g. 'switch' vs 'host'
        """
        sql_insert = ("INSERT INTO nodes (Node, Type) "
                      "VALUES ('{}', '{}')")
        self.sql_tool.send_insert(sql_insert.format(node, node_type))
        pass

    def store_interfaces(self, node, interfaces):
        """Stores interface names in 'switch_interfaces' tables.

        Arguments:
            node {string} -- Node name: 'Openflow1'
            interfaces {dict} -- dictionary of interfaces
        """

        sql_insert = (f"INSERT INTO {node}_interfaces (Interface) "
                      "VALUES ('{}')")
        for interface in interfaces:
            # self.send_sql_query(sql_insert.format(interface))
            self.sql_tool.send_insert(sql_insert.format(interface))
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

    # TODO: Consider helper function to create tables in abstract_agent
    def create_nodes_table(self):
        """Creates a nodes table in the sql DB."""
        table = (
            "CREATE TABLE nodes("
            "Node VARCHAR(32) NOT NULL,"
            "Type VARCHAR(16) NOT NULL,"
            "PRIMARY KEY (Node) );")
        # If table was previously created, we drop and recreate.
        self.sql_tool.create_sql_table(table)

    def create_int_table(self, node):
        """Creates a DB table listing node interfaces."""
        table = (
            f"CREATE TABLE {node}_interfaces("
            "Interface VARCHAR(32) NOT NULL,"
            "PRIMARY KEY (Interface) );")
        # TODO: Converge steps below into a helper function
        self.sql_tool.create_sql_table(table)

    def create_host_table(self):
        """Creates a host_info table in the sql DB."""
        table = (
            "CREATE TABLE host_info("
            "HOST VARCHAR(32) NOT NULL,"
            "IP_ADDRESS VARCHAR(16) NOT NULL,"
            "FIRST_TIME_SEEN VARCHAR(32) NOT NULL,"
            "LATEST_TIME_SEEN VARCHAR(32) NOT NULL,"
            "PRIMARY KEY (HOST) );")
        self.sql_tool.create_sql_table(table)

    def populate_host_table(self):
        """Stores host paramaters into host_info tbl"""
        self.sql_tool.send_sql_query('DELETE FROM host_info')
        response = self.get_data()
        for node in response['topology'][0]['node']:
            if 'host' in node['node-id']:
                host_id = node['node-id']
                host_data = node['host-tracker-service:addresses'][0]
                ip = host_data['ip']
                first_seen = host_data['first-seen']
                last_seen = host_data['last-seen']
                self.store_host_info(host_id, ip, first_seen, last_seen)
    
    def store_host_info(self, host, ip, first, latest):
        """Stores host parameters in the host_info DB table
        such as IP, first seen, and last seen.

        Arguments:
            host {string} -- Node Name: e.g. 'host:mac'
        """
        sql_insert = ("INSERT INTO host_info (HOST, IP_ADDRESS,"
                      "FIRST_TIME_SEEN, LATEST_TIME_SEEN)"
                      "VALUES ('{}', '{}','{}', '{}')")
        self.sql_tool.send_insert(sql_insert.format(host, ip, first, latest))

    def delete_stale_nodes(self):
        self.sql_tool.send_sql_query('DELETE FROM nodes')

        response = self.get_data()
        parsed_data = self.parse_response(response)

        for node, inter in parsed_data.items():
            if "openflow" in node:
                node_type = "switch"
            if "host" in node:
                node_type = "host"
            self.store_nodes(node, node_type)
