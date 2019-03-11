#!/usr/bin/env python3
"""
This script will be used to automatically detect what host(s)
that is/are available running Opendaylight on the LAN
Author: Brad Fitzgerald
Version: 1.0
"""
import socket
import re
import os
import nmap
import requests


class Webapp_Auxiliary:

    def __init__(self):
        self.odl_list = []
        self.scanning_port = 8181

    def find_devices_on_lan(self):
        # Get the IP address of this machine
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ip_address = s.getsockname()[0]
        s.close()

        # Get netmask of this machine
        ipline = os.popen("ip a | grep " + ip_address).read()
        Regex = re.findall(r"[/]\d{2}", ipline)
        netmask = Regex[0][1:]

        # Get dictionary of nmap scan result
        nmap_obj = nmap.PortScanner()
        nmap_dict = nmap_obj.scan(ip_address+'/' + netmask, str(self.scanning_port))

        # Find devices with port open on LAN
        for ip in nmap_dict['scan']:
            state = nmap_dict['scan'][ip]['tcp'][self.scanning_port]['state']

            if (state == 'open'):
                self.odl_list.append(nmap_dict['scan'][ip]['addresses']['ipv4'])

        return self.odl_list

    def test_odl_device(self, ip_to_test, username, password):
        topo_url = 'http://' + ip_to_test + \
            ':8181/restconf/operational/network-topology:network-topology'
        try:
            requests.get(topo_url, auth=(username, password))
            return True
        except:
            return False
