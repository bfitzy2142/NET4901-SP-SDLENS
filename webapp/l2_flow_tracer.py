#!/usr/bin/env python3
import collections
import re
import time
import json

import mysql.connector
from mysql.connector import errorcode

from abstract_flow_tracer import FlowTracer
from get_flows import Odl_Flow_Collector


class L2FlowTracer(FlowTracer):

    def __init__(self, user, password, host, db):
        super().__init__(user, password, host, db)

    def trace_flows(self, source, dest):
        """Determine the path taken for traffic with a given source/dest ip in
        in openflow networks.

        Arguments:
            source {str} -- IP of the source host.
            dest {str]} -- IP of the destination host.

        Returns:
            [dict] -- Returns a dictionary with a list of links traversed and
            a list of switches + flows matched.
        """
        self.flow_path = []
        self.links_traversed = []
        # Find the corresponding hosts and the switches they connect to.
        src_host = self.find_host(source)
        dest_host = self.find_host(dest)
        src_switch = self.find_switch_by_host(src_host, first_switch=True)
        dest_switch = self.find_switch_by_host(dest_host)

        # Run method that fills the flow_path and links_traversed attributes.
        self.find_flow_rules(src_host, dest_host, src_switch, dest_switch)

        # Return final results
        flow_trace_results = {}
        flow_trace_results["flow_path"] = self.flow_path
        flow_trace_results["links_traversed"] = self.links_traversed
        return flow_trace_results

    def find_host(self, ip):
        """Find the host that corresponds to a given IP.

        Arguments:
            ip {str} -- IP of the desired host.

        Returns:
            [str] -- Returns name of the given host stored in the sdlens DB.
        """
        query = ("SELECT HOST FROM host_info "
                 f"WHERE IP_ADDRESS = '{ip}'")
        host_query_result = self.sql_select_query(query)
        host = host_query_result[0][0]
        return host

    def find_switch_by_host(self, host, first_switch=False):
        """Find the switch attached to a given host.

        Arguments:
            host {str} -- Name of the host, as stored in the DB.

        Keyword Arguments:
            first_switch {bool} -- first_switch arg used as
            logic to determine if the host is the first host in our
            trace. If so, we add the corresponding link to the
            links_traversed attribute. (default: {False})
        
        Returns:
            string -- Returns name of the switch connected to the host.
        """
        switch = ""
        query = f"SELECT * FROM links WHERE SRC = '{host}' OR DST = '{host}'"
        result = self.sql_select_query(query)
        link_tuple = result[0]
        for node_name in link_tuple[1:3]:
            if node_name != host:
                switch = node_name
        if first_switch:
            link_pair = {}
            link_pair['SRCPORT'] = link_tuple[3]
            link_pair['DSTPORT'] = link_tuple[4]
            self.links_traversed.append(link_pair)
        return switch

    def sql_select_query(self, query):
        """Simple method to run SQL SELECT queries.

        Arguments:
            query {str} -- Desired SQL query to be executed

        Returns:
            [list] -- Returns results of the query
        """
        cnx = mysql.connector.connect(**self.sql_auth)
        cursor = cnx.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

# TODO: HANDLE ARP CASE
    def find_flow_rules(self, src_host, dest_host, src_switch, dest_switch):
        """Iterates through every switch to determine the flow path and flow rules.

        Arguments:
            src_host {str} -- Source host name
            dest_host {str} -- Destionation host name
            src_switch {str} -- Source switch name.
            dest_switch {str} -- Destination switch name.
        """
        last_flow = False
        src_mac = src_host.replace("host:", "")
        dest_mac = dest_host.replace("host:", "")
        current_switch = src_switch

        #Iterate through all switches in the path
        while last_flow is not  True:
            if current_switch == dest_switch:
                last_flow = True
            # Get Flows
            flows = self.pull_flows(current_switch)
            for flow in flows:
                # Find the matching flow and the following switch
                flow_match = False
                flow_match = self.find_matching_flow(flow, src_mac, dest_mac)
                if flow_match is True:
                    flow_pair = {'switch': current_switch, 'flow': flow}
                    self.flow_path.append(flow_pair)
                    next_switch = self.find_next_node(current_switch, flow)
                    break
            current_switch = next_switch

    def pull_flows(self, switch):
        """Get flows from a given switch

        Arguments:
            switch {str} -- Switch name

        Returns:
            [list] -- Returns list of flow rules on a switch
        """
        f_collector = Odl_Flow_Collector(self.controller, switch)
        flows = f_collector.run()
        return flows

    def find_matching_flow(self, flow, src_mac, dest_mac):
        """Verifies if a given flow rule matches our source and destination MACs.

        Arguments:
            flow {dict} -- Dictionary contain all the parameters of a flow rule.
            src_mac {str} -- Source host MAC address.
            dest_mac {str} -- Destination MAC address.

        Returns:
            [Bool] -- Returns true if it is the matching flow rule.
        """
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
        """Finds the next hop node of a given flow rule.

        Arguments:
            switch {str} -- Switch containing the given flow rule.
            flow {dict} -- Flow rule containing the output node action.

        Returns:
            [str] -- Name of the next hop node.
        """
        link_pair = {}
        port_num = flow['actions'][0]['output-action']['output-node-connector']
        port_name = f"{switch}:{port_num}"
        query = (f"SELECT * FROM links WHERE SRCPORT = '{port_name}' "
                 f"OR DSTPORT = '{port_name}'")
        result = self.sql_select_query(query)
        link_tuple = result[0]
        for node_name in link_tuple[1:3]:
            if node_name != switch:
                new_switch = node_name
        link_pair['SRCPORT'] = link_tuple[3]
        link_pair['DSTPORT'] = link_tuple[4]
        self.links_traversed.append(link_pair)
        return new_switch
