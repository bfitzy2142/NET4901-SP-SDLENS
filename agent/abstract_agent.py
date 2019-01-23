#!/usr/bin/env python3
"""abstract_agent contains the template class for agent objects.

This abstract class will be used as the base class for the various
monitoring agents of our application. Since every agent goes through
a similar process: Make API call -> Convert JSON to data structure ->
parse data structure -> Store in DB -> etc. It makes more sense to
promote reuse and minimize repeated code.
"""
import abc
import json

import requests
from requests.auth import HTTPBasicAuth


class AbstractAgent(metaclass=abc.ABCMeta):
    """Abstract class to be implemented by monitoring agents"""
    def __init__(self, controller_ip):
        self.controller_ip = controller_ip
        self.headers = {'Accept': 'application/json',
                        'content-type': 'application/json'}
        self.base_url = f"http://{self.controller_ip}:8181/restconf/operational/"
        # TODO: Change once DB implemented
        self.auth = HTTPBasicAuth("admin", "admin")

    def run_agent(self):
        """Template method executed by every agent."""
        response = self.get_data()
        parsed_data = self.parse_response(response)
        print(parsed_data)

    @abc.abstractmethod
    def get_data(self):
        """Abstract method the be implemented by the monitoring
        agent. Method should determine RESTCONF url and invoke the
        necessary API calls.
        """
        pass

    def send_get_request(self, url):
        """Sends an HTTP GET request to the agent's controller.

        Arguments:
            url {string} -- RESTCONF url of the desired ODL API.

        Returns:
            dict -- Returns a dictionary corresponding to the API response.
        """
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response_data = response.json()
        return response_data

    @abc.abstractmethod
    def parse_response(self, response):
        """Abstract method to parse the API data.
        To be implemented by the agent objects

        Arguments:
            response {dict} -- Data from the API response
        """
        pass

    @abc.abstractmethod
    def store_data(self, data):
        """Abstract method to be implemented for storing monitoring data.

        Arguments:
            data {dict} -- Monitoring data to be stored in the Database
        """
        pass
