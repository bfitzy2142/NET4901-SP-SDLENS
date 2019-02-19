import json
import requests

from requests.auth import HTTPBasicAuth


class Odl_Flow_Collector(object):

    def __init__(self, controller_ip, node):
        self.controller_ip = controller_ip
        self.headers = {'Accept': 'application/json',
                        'content-type': 'application/json'}
        self.base_url = f"http://{self.controller_ip}:8181/restconf/operational/"
        self.auth = HTTPBasicAuth("admin", "admin")
        self.node = node
        self.flow_data = {}

    # Send get requests to the controller
    def send_get_request(self, url):
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response_data = response.json()
        return response_data

    def get_flows(self):
        target_uri = f"opendaylight-inventory:nodes/node/{self.node}/table/0"
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
            # TODO: Look for better data struct for actions
            try:
                action_list =[]
                action_set = flow['instructions']['instruction']
                for actions in action_set:
                    print(actions['apply-actions']['action'])
                    for action in actions['apply-actions']['action']:
                        action_list.append(action)
                new_flow['actions'] = action_list
            except KeyError:
                new_flow['actions'] = []
            flow_stats.append(new_flow)
        
        flow_stats.sort(key=lambda x: x['priority'], reverse=True)
        return flow_stats
        # print(raw_flow_stats)

    def sort_flow_actions(self, flow_instructions):
        """Helper function in case actions are out of order"""
        flow_instructions.sort(key=lambda x: x['order'])
        for actions in flow_instructions:
            print(actions['apply-actions'])
        return flow_instructions
    
    def run(self):
        raw_flows = self.get_flows()
        flow_stats = self.clean_flows(raw_flows)
        return flow_stats

