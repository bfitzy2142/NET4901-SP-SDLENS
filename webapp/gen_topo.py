#!/usr/bin/env python3

import mysql.connector
from mysql.connector import errorcode
from time import strftime, localtime
from json import dumps


class generate_topology():
    """
        Database parser for topology information
        March 2019
        SDLENS Monitoring Solution
        Brad Fitzgerald
        bradfitzgerald@cmail.carleton.ca
    """

    def __init__(self, user, password, host, db):
        self.sql_auth = {
            "user": user,
            "password": password,
            "host": host,
            "db": db
        }


    def fetch_links(self):
        """ Gets each link from the database"""

        links = []

        link_query = "SELECT * FROM links"

        raw_result = self.sql_select_query(link_query)

        for row in raw_result:
            link = {'src': row[1],
                    'dst': row[2],
                    'src_port': row[3],
                    'dst_port': row[4]
                    }
            links.append(link)
        return links

    def fetch_nodes(self):
        """ Gets each node from the database"""
        nodes = []

        node_query = "SELECT Node from nodes"

        raw_result = self.sql_select_query(node_query)

        for row in raw_result:
            if 'host' in row[0]:
                nodes.append(self.fetch_host_info(row[0]))
            else:
                nodes.append({'id': row[0]})
        return nodes

    def get_host_ip(self):

        host_list = []
        query = 'select IP_ADDRESS from host_info'
        host_tuples = self.sql_select_query(query)
        for host in host_tuples:
            host_list.append(host[0])

        return sorted(host_list)

    def fetch_host_info(self, host):
        query_host = ('select IP_ADDRESS, FIRST_TIME_SEEN, LATEST_TIME_SEEN '
                      f'from host_info where HOST = "{host}"')

        raw_result = self.sql_select_query(query_host)        

        # Get epoch in seconds by dividing by 1000
        first_epoch = int(raw_result[0][1])/1000
        latest_epoch = int(raw_result[0][2])/1000

        first_seen = strftime('%Y-%m-%d %H:%M:%S', localtime(first_epoch))
        last_seen = strftime('%Y-%m-%d %H:%M:%S', localtime(latest_epoch))

        return {'id': host,
                'ip': raw_result[0][0],
                'first_seen': first_seen,
                'last_seen': last_seen
                }

    def fetch_topology(self):
        # Gets topology data and stores as a dict
        deviceList = self.fetch_nodes()
        connectionList = self.fetch_links()
        hosts = self.get_host_ip()

        topologyInfo = {'devices': deviceList,
                        'connections': connectionList,
                        'hosts': hosts
                        }
        return topologyInfo

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
"""
obj = generate_topology('root', 'root', '127.0.0.1', 'sdlens')
print(dumps(obj.fetch_nodes(), indent=1))
"""