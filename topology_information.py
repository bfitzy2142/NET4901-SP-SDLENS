import requests
import pprint
import re 
#OpenDayLight RESTCONF API settings.
inputURL = input("Please enter the IP address of the ODL controller:")
odl_url = 'http://'+ inputURL +':8181/restconf/operational/network-topology:network-topology'
odl_username = 'admin'
odl_password = 'admin'
pp = pprint.PrettyPrinter()

# Fetch information from API.
response = requests.get(odl_url, auth=(odl_username, odl_password))
#pp.pprint(response.json())
# Find information about nodes in retrieved JSON file.

def getHosts():
    for nodes in response.json()['network-topology']['topology']:
        if re.match(r"flow:[0-9]+", nodes['topology-id']):
            # Walk through all node information.
            node_info = nodes['node']
            # Look for MAC and IP addresses in node information.
            for node in node_info:
                try:
                    ip_address = node['host-tracker-service:addresses'][0]['ip']
                    mac_address = node['host-tracker-service:addresses'][0]['mac']
                    print('Found host with MAC address ' + mac_address + ' and IP address ' + ip_address)
                except:
                    pass



getHosts()