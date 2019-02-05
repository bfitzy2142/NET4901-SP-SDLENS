#!/usr/bin/env python3
"""Monitoring Agent that discovers topology."""
import mysql.connector
from mysql.connector import errorcode
from abstract_agent import AbstractAgent
# import json


class LinkAgent(AbstractAgent):
    """
    Description: OpenDayLight RESTCONF API parser for device links.
    """

    def __init__(self, controller_ip):
        """"Initalizer for LinkAgent, initializes parent object."""
        super().__init__(controller_ip)

    def get_data(self):
        """Retrieves json data containing the connections of the
        present SDN topology from the ODL controller.

        Returns:
            dict -- Returns dictionary containing link information of the
            ODL managed network.
        """
        links_uri = 'network-topology:network-topology/topology/flow:1/'
        url = self.base_url + links_uri
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
        connection_list = []

        for node in response['topology']:
            for link in node['link']:
                connection = {"src": link['source']['source-node'],
                              "dst": link['destination']['dest-node']}
                connection_list.append(connection)
        # Cleanup redundant connections
        cleansed_list = self.remove_redundancy(connection_list)
        return cleansed_list

    def remove_redundancy(self, connection_list):
        """Removes redundant links from the list of connections.

        Returns:
            list -- A list of unique links.
        """
        # Compare first node with second deleting similar links
        for first_connection in connection_list:
            for second_connection in connection_list[1:]:
                if (self.link_comparison(first_connection, second_connection)):
                    connection_list.remove(second_connection)
        return connection_list

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
        """Implentaiton of abstract method to store link info in an
        SQL database

        Parameters:
        Data - A list of links. Each index contains dict with src and
        dst port identifiers.
        """
        self.create_links_table()

        for link in data:
            self.store_links(link['src'], link['dst'])

    def store_links(self, src, dst):
        """Inserts a unique link into the 'links' table.

        Parameters:
        src - the source port for the current connection
        dst - the destination port for the current connection
        """
        sql_insert = ("INSERT INTO links (SRC, DST) "
                      "VALUES ('{}', '{}')")
        self.send_sql_query(sql_insert.format(src, dst))

    def create_links_table(self):
        """Creates table 'links' if not already created.

        Table structure:
        ID: (Primary Key & auto incrementing)
        SRC: Connection Source
        DST: Connection Destination
        """
        table = (
            "CREATE TABLE links("
            "ID int NOT NULL AUTO_INCREMENT,"
            "SRC VARCHAR(32) NOT NULL,"
            "DST VARCHAR(32) NOT NULL,"
            "PRIMARY KEY (ID) );")
        try:
            self.send_sql_query(table)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                self.send_sql_query(f"DROP TABLE links")
                self.send_sql_query(table)

    def retrieve_links(self):
        """ Query method to get a list of links from the sql database

        Retruns:
        List - Containing 'id' of connection, 'src' node, 'dst' node

        Todo: Add threading functionality
        """
        connections = []
        link_query = "select * from links"
        self.cursor.execute(link_query)
        link_rows = self.cursor.fetchall()

        for row in link_rows:
            connections.append(self.get_links_db(row))

        return connections

    def get_links_db(self, link_row):
        """ Helper function to allow threading when getting links from db
        Returns:
        Single link to be added to a list of links
        """
        return {'id': link_row[0], 'src': link_row[1], 'dst': link_row[2]}

    def retrieve_devices(self):
        """ Query method to get a list of nodes from the sql database

        Returns:
        List - Devices available in the SDN network
        """
        devices = []
        query = "select node from nodes"
        self.cursor.execute(query)
        raw_devices = self.cursor.fetchall()

        for row in raw_devices:
            devices.append(row[0])

        return devices

    def topo_data_consolidater(self):
        """Builds a dict with link and device data contained within.

        Returns:
        Dict - To be passed to the topo.html file with Jinja2 templating.
        """
        links = self.retrieve_links()
        nodes = self.retrieve_devices()
        return {'links': links, 'nodes': nodes}

# Debug
# obj = LinkAgent('134.117.89.138')
# obj.run_agent()
# print(json.dumps(obj.topo_data_consolidater(), indent=1))
