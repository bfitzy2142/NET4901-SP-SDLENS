import json
import requests

from requests.auth import HTTPBasicAuth


class odl_flow_collector(object):

    def __init__(self, controller_ip):
        self.controller_ip = controller_ip
        self.headers = {'Accept': 'application/json',
                        'content-type': 'application/json'}
        self.base_url = f"http://{self.controller_ip}:8181/restconf/operational/"
        self.auth = HTTPBasicAuth("admin", "admin")
        self.flow_data = {}

    # Send get requests to the controller
    def send_get_request(self, url):
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response_data = response.json()
        return response_data

    def get_flows(self, node):
        target_uri = f"opendaylight-inventory:nodes/node/{node}/table/0"
        url = self.base_url + target_uri
        flow_request = requests.get(url, headers=self.headers, auth=self.auth)
        raw_flows = flow_request.json()
        return raw_flows

    def clean_flows(self, flows):
        # Long JSON key used to get flow stats
        stats_str = "opendaylight-flow-statistics:flow-statistics"
        raw_flow_stats = flows["flow-node-inventory:table"][0]["flow"]
        flow_stats = []
        for flow in raw_flow_stats:
            # print(flow)
            print('*' * 20)
            new_flow = {}
            new_flow['id'] = flow['id']
            new_flow['priority'] = flow["priority"]
            new_flow['pckt-count'] = flow[stats_str]['packet-count']
            new_flow['byte-count'] = flow[stats_str]['byte-count']
            new_flow['duration'] = flow[stats_str]['duration']['second']
            new_flow['hard-timeout'] = flow['hard-timeout']
            new_flow['idle-timeout'] = flow['idle-timeout']
            new_flow['table'] = flow['table_id']
            new_flow['match_rules'] = flow['match']
            new_flow['cookie'] = flow['cookie']
            try:
                # actions = self.sort_flow_actions(flow['instructions']['instruction'])
                # print(actions)
                new_flow['actions'] = flow['instructions']['instruction']
                # print(flow['instructions']['instruction'])
            # print(flow['instructions'])
            except KeyError:
                new_flow['actions'] = []
            """
            flow_stats = flow["opendaylight-flow-statistics:flow-statistics"]
            flows["flow-id"] = flow["id"]
            flows["flow-priority"] = flow["priority"]
            flows["flow-pkt-cnt"] = flow[flow_stats]["packet-count"]
            flows["flow-byte-cnt"] = flow[flow_stats]["byte-count"]
            flows["flow-table-id"] = flow["table_id"]
            flows["flow-match"] = flow["match"]
            """
            # instructions
            # print(flows)
            # print("*"*200)
        return flows
        # print(raw_flow_stats)

    def sort_flow_actions(self, flow_instructions):
        flow_instructions.sort(key=lambda x: x['order'])
        for actions in flow_instructions:
            print(actions['apply-actions'])
        return flow_instructions


o = odl_flow_collector("134.117.89.138")
o.get_flows("openflow:1")
flows = o.get_flows("openflow:1")
o.clean_flows(flows)
