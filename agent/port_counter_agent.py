#!/usr/bin/env python3
"""Monitoring Agent that tracks port counters."""
import mysql.connector
from mysql.connector import errorcode
from abstract_agent import AbstractAgent


class PortCounterAgent(AbstractAgent):
    def __init__(self, controller_ip, node):
        """Initializer for the PortCounterObject"""
        super().__init__(controller_ip)
        self.create_pc_table(node)

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

    def parse_response(self, response):
        """TODO"""
        pass

    def get_data(self):
        """TODO"""
        pass

    def store_data(self, data):
        """TODO"""
        pass
