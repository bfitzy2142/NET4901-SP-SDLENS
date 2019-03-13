#!/usr/bin/env python3
"""Monitoring Agent that tracks flow stats."""
import mysql.connector
from mysql.connector import errorcode

from abstract_agent import AbstractAgent


class FlowAgent(AbstractAgent):
    def __init__(self, controller_ip, node, table_id):
        """Initializer for FlowAgent instances"""
        super().__init__(controller_ip)
        self.node = node
        self.table_id = table_id
        self.table_stats_straing = ("opendaylight-flow-table-statistics:" +
                                    "flow-table-statistics")
        self.create_flow_summary_table(self.node, self.table_id)
        self.create_flow_stats_table(self.node, self.table_id)
        # Create tables
        # long string if needed?

    def create_flow_summary_table(self, node, table_id):
        """Creates DB table to track flow table summary stats."""
        table = (
            f"CREATE TABLE {node}_table{table_id}_summary("
            "ID INT NOT NULL AUTO_INCREMENT,"
            "Timestamp DATETIME NOT NULL,"
            "Active_Flows INT NOT NULL,"
            "Packets_Looked_Up INT NOT NULL,"
            "Packets_Matched INT NOT NULL,"
            "PRIMARY KEY (ID) );")
        self.sql_tool.create_sql_table(table)

    def create_flow_stats_table(self, node, table_id):
        """Create DB table to track stats of all flows in a given tables."""
        table = (
            f"CREATE TABLE {node}_table{table_id}_flows("
            "ID INT NOT NULL AUTO_INCREMENT,"
            "Flow_ID VARCHAR(32) NOT NULL,"
            "Timestamp DATETIME NOT NULL,"
            "Priority INT NOT NULL,"
            "Packet_count BLOB NOT NULL,"
            "Byte_count BLOB NOT NULL,"
            "Duration INT NOT NULL,"
            "Hard_timeout INT NOT NULL,"
            "Idle_timeout INT NOT NULL,"
            "Table_ID INT NOT NULL,"
            "PRIMARY KEY (ID) );")
        self.sql_tool.create_sql_table(table)

    def get_data(self):
        """Method executes the necessary logic to make the API calls
        to collect flow table stats and converts the response to a
        usable data structure.
    
        Returns:
            Dict -- Data structure that corresponds to the API calls sent.
        """
        restconf_node = f"opendaylight-inventory:nodes/node/{self.node}/"
        restconf_table = f"table/{self.table_id}"
        url = self.base_url + restconf_node + restconf_table
        response = self.send_get_request(url)
        return response

    def parse_response(self, response):
        """Parse the API response for the relevant statistics we want.

        Arguments:
            response {dict} -- The dictionary response from the API call.

        Returns:
            dict -- Returns a dictionary with the desired flow stats.
        """
        data = {}
        table_stats_str = "opendaylight-flow-table-statistics:flow-table-statistics"
        raw_stats = response["flow-node-inventory:table"][0]
        data["table-stats"] = raw_stats[table_stats_str]
        data["table-stats"]["timestamp"] = self.add_timestamp()
        raw_flow_stats = raw_stats["flow"]
        data["flow-stats"] = self.parse_flows(raw_flow_stats)
        return data

    def parse_flows(self, raw_flow_stats):
        """Parse flows parses the flow specific stats obtained by get_data.
        
        Arguments:
            raw_flow_stats {list} -- A list of flow stats provided by
            parse_response.

        Returns:
            list -- A list of key-value pairs of statistics for each flow.
        """
        stats_str = "opendaylight-flow-statistics:flow-statistics"
        flow_stats = []
        for flow in raw_flow_stats:
            new_flow = {}
            new_flow['id'] = flow['id']
            new_flow['priority'] = flow["priority"]
            new_flow['pckt-count'] = flow[stats_str]['packet-count']
            new_flow['byte-count'] = flow[stats_str]['byte-count']
            new_flow['duration'] = flow[stats_str]['duration']['second']
            new_flow['hard-timeout'] = flow['hard-timeout']
            new_flow['idle-timeout'] = flow['idle-timeout']
            new_flow['table'] = flow['table_id']
            new_flow['timestamp'] = self.add_timestamp()
            flow_stats.append(new_flow)
        return(flow_stats)

    def store_data(self, data):
        """Stores our flow data in the appropriate DB tables.

        Arguments:
            data {dict} -- Dictionary of flow stats to be stored.
        """
        self.store_table_stats(data["table-stats"])
        self.store_flow_stats(data["flow-stats"])
    
    def store_table_stats(self, table_stats):
        """Helper function that stores the flow table summary stats."""
        sql_insert = (f"INSERT INTO {self.node}_table{self.table_id}_summary"
                      "(Timestamp, Active_Flows, Packets_Looked_Up,"
                      "Packets_Matched) VALUES ('{}', {}, {}, {})")
        query = sql_insert.format(table_stats['timestamp'],
                                  table_stats['active-flows'],
                                  table_stats['packets-looked-up'],
                                  table_stats['packets-matched'])
        self.sql_tool.send_insert(query)

    def store_flow_stats(self, flow_stats):
        """Helper function to store the individual flow stats in the DB."""
        sql_insert = (f"INSERT INTO {self.node}_table{self.table_id}_flows"
                      "(Flow_ID, Timestamp, Priority, Packet_count, "
                      "Byte_count, Duration, Hard_timeout, Idle_timeout, "
                      "Table_ID) VALUES ('{}', '{}', {}, {}, {}, {}, "
                      "{}, {}, {})")
        for flow in flow_stats:
            query = sql_insert.format(flow['id'], flow['timestamp'],
                                      flow['priority'], flow['pckt-count'],
                                      flow['byte-count'], flow['duration'],
                                      flow['hard-timeout'],
                                      flow['idle-timeout'], flow['table'])
            self.sql_tool.send_insert(query)
