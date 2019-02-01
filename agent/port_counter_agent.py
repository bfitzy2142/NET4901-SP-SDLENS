#!/usr/bin/env python3
"""Monitoring Agent that tracks port counters."""
from datetime import datetime

import mysql.connector
from mysql.connector import errorcode

from abstract_agent import AbstractAgent


class PortCounterAgent(AbstractAgent):
    def __init__(self, controller_ip, node):
        """Initializer for the PortCounterObject"""
        super().__init__(controller_ip)
        self.node = node
        self.create_pc_table(self.node)

    def create_pc_table(self, node):
        """Creates a DB table listing port counters
        for a switch."""
        node = node.replace(":", "")
        table = (
            f"CREATE TABLE {node}_counters("
            "ID INT NOT NULL AUTO_INCREMENT,"
            "Interface VARCHAR(32) NOT NULL,"
            "Timestamp DATETIME NOT NULL,"
            "Rx_pckts INT NOT NULL,"
            "Tx_pckts INT NOT NULL,"
            "Rx_bytes INT NOT NULL,"
            "Tx_bytes INT NOT NULL,"
            "Rx_drops INT NOT NULL,"
            "Tx_drops INT NOT NULL,"
            "Rx_errs INT NOT NULL,"
            "Tx_errs INT NOT NULL,"
            "PRIMARY KEY (ID) );")
        try:
            self.send_sql_query(table)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                self.send_sql_query(f"DROP TABLE {node}_counters")
                self.send_sql_query(table)

    # TODO: Add this to an SQL Utility module
    def get_interfaces(self, node):
        interface_list = []
        node = node.replace(":", "")
        query = f"SELECT * FROM {node}_interfaces"
        self.cursor.execute(query)
        int_tuples = self.cursor.fetchall()
        for interface in int_tuples:
            interface_list.append(interface[0])
        return interface_list

    def get_data(self):
        """TODO"""
        response_dict = {}
        interface_list = self.get_interfaces(self.node)
        for interface in interface_list:
            response_dict[interface] = self.get_counters(interface)
        print(response_dict.keys())
        return response_dict

    def get_counters(self, interface):
        """Helper method that sends API calls for counters of every port.

        Arguments:
            interface [str] -- Target interface name for the API call.

        Returns:
            dict -- Returns the response of the API call as a dict.
        """
        odl_string = ("opendaylight-port-statistics:"
                      "flow-capable-node-connector-statistics")
        restconf_node = f"opendaylight-inventory:nodes/node/{self.node}/"
        restconf_int = f"node-connector/{interface}/"
        url = self.base_url + restconf_node + restconf_int + odl_string
        response = self.send_get_request(url)
        return response

    def parse_response(self, response):
        """TODO"""
        # TODO: Make odl_string an attribute
        odl_string = ("opendaylight-port-statistics:"
                      "flow-capable-node-connector-statistics")
        port_stats = {}
        for interface in response:
            # print(response[interface])
            int_id = interface
            int_stats = response[interface][odl_string]
            port_stats[int_id] = {}
            port_stats[int_id]["rx-pckts"] = int_stats["packets"]["received"]
            port_stats[int_id]["tx-pckts"] = int_stats["packets"]["transmitted"]
            port_stats[int_id]["rx-bytes"] = int_stats["bytes"]["received"]
            port_stats[int_id]["tx-bytes"] = int_stats["bytes"]["transmitted"]
            port_stats[int_id]["rx-drops"] = int_stats["receive-drops"]
            port_stats[int_id]["tx-drops"] = int_stats["transmit-drops"]
            port_stats[int_id]["rx-errs"] = int_stats["receive-errors"]
            port_stats[int_id]["tx-errs"] = int_stats["transmit-errors"]
            port_stats[int_id]["timestamp"] = self.add_timestamp()
        return port_stats

    # TODO: Add this to Abstract agent instead
    def add_timestamp(self):
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        return timestamp

    def store_data(self, data):
        """TODO"""
        for interface in data:
            int_data = data[interface]
            # print(int_data)
            stripped_node = self.node.replace(":", "")
            sql_insert = (f"INSERT INTO {stripped_node}_counters "
                          "(Interface, Timestamp, Rx_pckts, Tx_pckts, "
                          "Rx_bytes, Tx_bytes, Rx_drops, Tx_drops, "
                          "Rx_errs, Tx_errs) VALUES "
                          "('{}', '{}', {}, {}, {}, {}, {}, {}, {}, {})")
            query = sql_insert.format(interface, int_data['timestamp'],
                                      int_data['rx-pckts'], int_data['tx-pckts'],
                                      int_data['rx-bytes'], int_data['tx-bytes'],
                                      int_data['rx-drops'], int_data['tx-drops'],
                                      int_data['rx-errs'], int_data['tx-errs'])
            self.send_sql_query(query)
