#!/usr/bin/env python3
import collections
import re
import time

import mysql.connector
from mysql.connector import errorcode

from abstract_flow_tracer import FlowTracer
from get_flows import Odl_Flow_Collector


class L2FlowTracer(FlowTracer):

    def __init__(self):
        super().__init__()

    def trace_flows(self, source, dest):
        src_host = self.find_host(source)
        dest_host = self.find_host(dest)
        src_switch = self.find_switch_by_host(src_host)
        dest_switch = self.find_switch_by_host(dest_host)
        self.find_flow_rules(src_host, dest_host, src_switch, dest_switch)

    def find_host(self, ip):
        """[summary]

        Arguments:
            ip {[type]} -- [description]
        """
        query = ("SELECT HOST FROM host_info "
                 f"WHERE IP_ADDRESS = '{ip}'")
        host_query_result = self.sql_select_query(query)
        host = host_query_result[0][0]
        return host
        # get host-ip pair from host
        # get link tuple?

    def find_switch_by_host(self, host):
        switch = ""
        query = f"SELECT * FROM links WHERE SRC = '{host}' OR DST = '{host}'"
        result = self.sql_select_query(query)
        link_tuple = result[0]
        for node_name in link_tuple[1:3]:
            if node_name != host:
                switch = node_name
        return switch

    def sql_select_query(self, query):
        cursor = self.cnx.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def find_flow_rules(self, src_host, dest_host, src_switch, dest_switch):
        last_flow = False
        src_mac = src_host.replace("host:", "")
        dest_mac = dest_host.replace("host:", "")
        print(f"dest switch: {dest_switch}")
        current_switch = src_switch
        print(f"Current Switch {current_switch}")
        while last_flow is not True:
            if current_switch == dest_switch:
                last_flow = True
            flows = self.pull_flows(current_switch)
            for flow in flows:
                flow_match = False
                flow_match = self.find_matching_flow(flow, src_mac, dest_mac)
                if flow_match is True:
                    print(current_switch)
                    print(flow)
                    next_switch = self.find_next_node(current_switch, flow)
                    break
            current_switch = next_switch
        
    def pull_flows(self, switch):
        f_collector = Odl_Flow_Collector(self.controller, switch)
        flows = f_collector.run()
        return flows

    def find_matching_flow(self, flow, src_mac, dest_mac):
        try:
            if "ethernet-source" in flow["match_rules"]["ethernet-match"]:
                address_pair = flow["match_rules"]["ethernet-match"]
                flow_source = address_pair['ethernet-source']['address']
                flow_dest = address_pair['ethernet-destination']['address']
                if flow_source == src_mac and flow_dest == dest_mac:
                    return True
            
            return False
        except KeyError:
            print("nope")
            return True  

    def find_next_node(self, switch, flow):
        port_num = flow['actions'][0]['output-action']['output-node-connector']
        port_name = f"{switch}:{port_num}"
        query = (f"SELECT * FROM links WHERE SRCPORT = '{port_name}' "
                 f"OR DSTPORT = '{port_name}'")
        result = self.sql_select_query(query)
        link_tuple = result[0]
        for node_name in link_tuple[1:3]:
            if node_name != switch:
                new_switch = node_name
        return new_switch

l = L2FlowTracer()
l.trace_flows('10.0.0.4', '10.0.0.7')
