import json
import requests

from requests.auth import HTTPBasicAuth

class odl_flow_collector(object):

    def __init__(self, controller_ip):
        self.controller_ip = controller_ip
        self.headers = {'Accept': 'application/json', 'content-type': 'application/json'}
        self.flow_data = {}

    def get_flows(self, node):
        url = f"http://{self.controller_ip}:8181/restconf/operational/opendaylight-inventory:nodes/node/{node}/table/0"
        flow_request = requests.get(url, headers=self.headers, auth=HTTPBasicAuth("admin", "admin"))
        raw_flows = flow_request.json()
        print(raw_flows)
        #return raw_flows

o = odl_flow_collector("134.117.89.138")
o.get_flows("openflow:1")

    def clean_flows(self, node, table):
        url = self.base_url + f"opendaylight-inventory:nodes/node/{node}/table/{table}"
        raw_flow_table = self.send_get_request(url)
        raw_flow_stats = raw_flow_table["flow-node-inventory:table"][0]["flow"]
        for flow in raw_flow_stats
            #id
            #priority
            #packet count
            #byte count
            #table_id
            #match rules
            #instructions
        #return X