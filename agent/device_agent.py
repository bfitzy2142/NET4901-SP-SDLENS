#!/usr/bin/env python3
"""Monitoring Agent that discovers topology."""
import mysql.connector
from mysql.connector import errorcode
from abstract_agent import AbstractAgent
import json


class DeviceAgent(AbstractAgent):
    def __init__(self, controller_ip, node):
        """
        Initalizer for the Device Agent, initializes parent object"""
        super().__init__(controller_ip)
        self.node = node
        self.create_db_table(self.node)
        self.odl_string = ("flow-node-inventory")

    def create_db_table(self, node):
        """ Creates a DB table listing off of the
        switch physical information"""
        node = node.replace(":", "")
        table = (
            f"CREATE TABLE {node}_info("
            "ID INT NOT NULL AUTO_INCREMENT,"
            "Interface VARCHAR(32) NOT NULL,"
            "Port_Number BIGINT NOT NULL,"
            "Port_Name VARCHAR(32) NOT NULL,"
            "Speed INT NOT NULL,"
            "Hw_Addr VARCHAR(32) NOT NULL,"
            "State_Bl VARCHAR(16) NOT NULL,"
            "State_Dw VARCHAR(16) NOT NULL,"
            "PRIMARY KEY (ID) );")
        try:
            self.send_sql_query(table)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                self.send_sql_query(f"DROP TABLE {node}_info")
                self.send_sql_query(table)

    def get_interfaces(self, node):
        node = node.replace(":", "")
        query = f"SELECT * FROM {node}_interfaces"
        self.cursor.execute(query)
        int_tuples = self.cursor.fetchall()
        interface_list = [interface[0] for interface in int_tuples]
        return interface_list

    def get_data(self):
        """ """
        response_dict = {}
        interface_list = self.get_interfaces(self.node)
        for interface in interface_list:
            response_dict[interface] = self.get_info(interface)
        return response_dict

    def get_info(self, interface):
        restconf_node = f"opendaylight-inventory:nodes/node/{self.node}/"
        restconf_int = f"node-connector/{interface}"
        url = self.base_url + restconf_node + restconf_int
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
        int_info = {}
        fni = 'flow-node-inventory:'
        for switch in response:

            # Node connector, flow inventory List
            nc_fi_list = response[switch]['node-connector'][0]

            int_info[switch] = {}
            int_info[switch]["p-num"] = nc_fi_list[fni + "port-number"]
            int_info[switch]["pt-name"] = nc_fi_list[fni + "name"]
            int_info[switch]["speed"] = nc_fi_list[fni + "current-speed"]
            int_info[switch]["hw-addr"] = nc_fi_list[fni + "hardware-address"]
            int_info[switch]["st-bl"] = nc_fi_list[fni + "state"]["blocked"]
            int_info[switch]["st-ld"] = nc_fi_list[fni + "state"]["link-down"]
        return int_info

    def store_data(self, data):
        """Takes the parsed API responses for the device info and
        stores them in the sdlens DBs.

        Arguments:
            data {dict} -- Takes the dictionary returned my parse_data
            as the argument.
        """
        for interface in data:
            int_data = data[interface]
            stripped_node = self.node.replace(":", "")
            print(f'Populating DB w/:{interface}.')
            sql_insert = (f"INSERT INTO {stripped_node}_info"
                          "(Interface, Port_Number, Port_Name, "
                          "Speed, Hw_Addr, State_Bl, State_DW)"
                          "VALUES ('{}', {}, '{}', {}, '{}', '{}', '{}')")
            query = sql_insert.format(interface, int_data['p-num'],
                                      int_data['pt-name'], int_data['speed'],
                                      int_data['hw-addr'], int_data['st-bl'],
                                      int_data['st-ld'])
            self.send_sql_query(query)
