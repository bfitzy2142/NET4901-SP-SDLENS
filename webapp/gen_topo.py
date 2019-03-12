#!/usr/bin/env python3
"""
Database parser for topology information
"""
import mysql.connector
from mysql.connector import errorcode
from time import strftime, localtime
from json import dumps


class generate_topology():

    def __init__(self, user, password, host, db):
        self.sql_auth = {
            "user": user,
            "password": password,
            "host": host,
            "db": db
        }
        self.cnx = mysql.connector.connect(**self.sql_auth)
        self.cursor = self.cnx.cursor()

    def fetch_links(self):
        """ Gets each link from the database"""
        links = []

        link_query = "SELECT * FROM links"

        self.cursor.execute(link_query)
        raw_result = self.cursor.fetchall()

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

        self.cursor.execute(node_query)
        raw_result = self.cursor.fetchall()

        for row in raw_result:
            if 'host' in row[0]:
                nodes.append(self.fetch_host_info(row[0]))
            else:
                nodes.append({'id': row[0]})

        return nodes

    def fetch_host_info(self, host):
        query_host = ('select IP_ADDRESS, FIRST_TIME_SEEN, LATEST_TIME_SEEN '
                      f'from host_info where HOST = "{host}"')

        self.cursor.execute(query_host)
        raw_result = self.cursor.fetchall()

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

        topologyInfo = {'devices': deviceList,
                        'connections': connectionList,
                        }

        return topologyInfo
"""
obj = generate_topology('root', 'root', '127.0.0.1', 'sdlens')
print(dumps(obj.fetch_nodes(), indent=1))
"""