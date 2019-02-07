import json
import requests

from requests.auth import HTTPBasicAuth

class odl_flow_collector(object):

    def __init__(self, controller_ip):
        self.controller_ip = controller_ip
        self.headers = {'Accept': 'application/json', 'content-type': 'application/json'}
        self.base_url = f"http://{self.controller_ip}:8181/restconf/operational/"
        self.auth = HTTPBasicAuth("admin", "admin")
        self.flow_data = {}

    # Send get requests to the controller
    def send_get_request(self, url):
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response_data = response.json()
        return response_data

    def get_flows(self, node):
        url = f"http://{self.controller_ip}:8181/restconf/operational/opendaylight-inventory:nodes/node/{node}/table/0"
        flow_request = requests.get(url, headers=self.headers, auth=HTTPBasicAuth("admin", "admin"))
        raw_flows = flow_request.json()
        #print(raw_flows)
        return raw_flows

    def clean_flows(self, flows):
        raw_flow_stats = flows["flow-node-inventory:table"][0]["flow"]
        #print(raw_flow_stats)
        for flow in raw_flow_stats:
            flow_id = flow["id"]
            #id
            #priority
            flows[flow_id]["priority"] = flows["flow"]["priority"]
            #packet count
            #byte count
            #table_id
            #match rules
            #instructions
            print(flows)
            print("*"*200)
        return flows
        #print(raw_flow_stats)

o = odl_flow_collector("134.117.89.138")
o.get_flows("openflow:1")
flows = o.get_flows("openflow:1")
o.clean_flows(flows)
