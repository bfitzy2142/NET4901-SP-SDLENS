#!/usr/bin/env python3

from requests import get
from requests.auth import HTTPBasicAuth


class odl_switch_info(object):
    """
    This module is used to gather switch interface
    details from the OpendayLight controller.
    """
    
    def __init__(self, controller_ip, odl_user, odl_pass):
        """
        Initalizer for odl_switch_info module.
        """
        self.controller_ip = controller_ip
        self.headers = {'Accept':
                        'application/json',
                        'content-type':
                        'application/json'}

        self.topo_data = {}
        self.odl_user = odl_user
        self.odl_pass = odl_pass

    def get_topo_data(self):
        url = (f"http://{self.controller_ip}:8181/restconf/"
               "operational/opendaylight-inventory:nodes")

        topo_request = get(url,
                           headers=self.headers,
                           auth=HTTPBasicAuth(self.odl_user, self.odl_pass)
                           )
        raw_topo = topo_request.json()
        return raw_topo

    def get_node_connector(self, raw_topo):
        nodes = {}
        fni = 'flow-node-inventory:'
        for node in raw_topo['nodes']['node']:

            nodes[node['id']] = {}
            for i in node['node-connector']:
                nodes[node['id']][i['id']] = {}
                nodes[node['id']][i['id']]['port_num'] = i[fni + 'port-number']
                nodes[node['id']][i['id']]['speed'] = i[fni + 'current-speed']
                nodes[node['id']][i['id']]['name'] = i[fni + 'name']
                nodes[node['id']][i['id']]['hwaddr'] = i[fni + 'hardware-address']

        # order nodes from smallest to largest. I.e: openflow:1-openflow:2,etc
        sortedKeys = sorted(nodes.keys())
        sortedNodes = {}
        for device in sortedKeys:
            sortedNodes[device] = nodes[device]

        return sortedNodes

    def run(self):
        topo = self.get_topo_data()
        nodes = self.get_node_connector(topo)
        return nodes
