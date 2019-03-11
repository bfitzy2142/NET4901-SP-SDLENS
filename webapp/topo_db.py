#!/usr/bin/env python3
import mysql.connector
from mysql.connector import errorcode
from time import strftime, localtime


class Topo_DB_Interactions():
    """Module to handle SQL queries for topo webapp actions
    """

    def __init__(self, user, password, host, db):
        self.sql_auth = {
            "user": user,
            "password": password,
            "host": host,
            "db": db
        }
        self.cnx = mysql.connector.connect(**self.sql_auth)
        self.cursor = self.cnx.cursor()

    def switch_query(self, switch):
        """Method to get counters from the db to be
        displayed on the topology page when a user clicks
        an active switch.

        Parameters:
        Switch - The switch to obtain statisitcs for.
        """
        # Switch Statistics Table
        ctr_table = f"{switch}_counters"

        # Get lastest timestamp
        qry_latest = f"SELECT max(Timestamp) FROM {ctr_table}"

        self.cursor.execute(qry_latest)
        raw_result = self.cursor.fetchall()
        date = str(raw_result[0][0])

        qry_sw = f'SELECT * FROM {ctr_table} WHERE Timestamp = "{date}"'

        self.cursor.execute(qry_sw)
        raw_result = self.cursor.fetchall()

        dict_list = []

        for row in raw_result:
            d = {
                row[1]: {
                    "Rx_pckts": row[3],
                    "Tx_packs": row[4],
                    "Rx_drops": row[7],
                    "Tx_drops": row[8],
                    "Rx_errs": row[9],
                    "Tx_errs": row[10]
                }
            }
            dict_list.append(d)

        return dict_list

    def edge_query(self, edge):
        node_list = edge.split('-')

        query_edges = (f'select SRCPORT, DSTPORT from links where'
                       f'(SRC = "{node_list[0]}" and DST = "{node_list[1]}") or'
                       f'(SRC = "{node_list[1]}" and DST = "{node_list[0]}")')

        self.cursor.execute(query_edges)
        raw_result = self.cursor.fetchall()

        return {'src_port': raw_result[0][0], 'dst_port': raw_result[0][1]}

    def host_query(self, host):

        query_host = ('select IP_ADDRESS, FIRST_TIME_SEEN, LATEST_TIME_SEEN '
                      f'from host_info where HOST = "{host}"')

        self.cursor.execute(query_host)
        raw_result = self.cursor.fetchall()

        # Get epoch in seconds by dividing by 1000
        first_epoch = int(raw_result[0][1])/1000
        latest_epoch = int(raw_result[0][2])/1000

        first_seen = strftime('%Y-%m-%d %H:%M:%S', localtime(first_epoch))
        last_seen = strftime('%Y-%m-%d %H:%M:%S', localtime(latest_epoch))

        return {'ip': raw_result[0][0],
                'hostname': f'H{raw_result[0][0][-1]}',
                'first_seen': first_seen,
                'last_seen': last_seen,
                'mac': host[5:]
                }
