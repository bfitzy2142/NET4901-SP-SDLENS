#!/usr/bin/env python3
"""
This script will be used to automatically detect what host(s) is/are available running Opendaylight on the LAN
Author: Brad Fitzgerald
Version: 1.0
""" 
import socket
import re
import os
import nmap


odlList=[]
scanningPort=8181

def findController():
    odlList.clear()
    #Get the IP address of this machine
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("1.1.1.1", 80))
    ipAddress = s.getsockname()[0]
    s.close()

    #get netmask of this machine
    ipline=os.popen("ip a | grep " + ipAddress).read()
    Regex=re.findall(r"[/]\d{2}",ipline)
    netmask=Regex[0][1:]
    
    nmapObj = nmap.PortScanner()
    obj=nmapObj.scan(ipAddress+'/'+netmask,str(scanningPort))

    #find odl controllers on LAN
    for ip in obj['scan']:
        state=obj['scan'][ip]['tcp'][scanningPort]['state']
        
        if (state=='open'):
            odlList.append(obj['scan'][ip]['addresses']['ipv4'])

    return odlList
