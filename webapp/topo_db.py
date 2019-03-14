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

    def calculate_throughput(self, raw_node):
        """ Query method to get specified node's
        interfaces with transmitted and received bits
        calcalated from stats in the sql database.

        Returns:
        Dict - device and their interface rx & tx bps
        """
        node = raw_node.replace(":", "")
        # Find latest entry date and ID in DB
        date_n_ID = f'select max(ID), max(Timestamp) from {node}_counters'
        self.cursor.execute(date_n_ID)
        raw_data = self.cursor.fetchall()
        newest_ID = int(raw_data[0][0])
        newest_date = str(raw_data[0][1])

        # Find number of links for the given switch
        link_num_query = (f'select ID from {node}_counters'
                          f' where Timestamp = "{newest_date}"')

        self.cursor.execute(link_num_query)
        raw_link_num = self.cursor.fetchall()
        link_num = len(raw_link_num)

        # Wait until there is at least two sets of
        # DB entries for link comparision.148077998.4
        while (newest_ID == link_num):
            continue

        # Find timestamp of penaltimate DB entries.
        # Can be calculated from DB by finding the timestamp
        # of the entry which's id is the latest ID minus the # of links.
        penultimate_ID = newest_ID - link_num
        penaltimate_qry = (f'SELECT Timestamp from {node}_counters'
                           f' WHERE ID = "{penultimate_ID}"')

        self.cursor.execute(penaltimate_qry)
        raw_pen_date = self.cursor.fetchall()
        penultimate_date = str(raw_pen_date[0][0])

        device_info = {}
        device_info[node] = self.pdtc(node, newest_date, penultimate_date)

        # Get flow stats
        # Get latest id in db
        id_query = f'select max(ID) from {node}_table0_summary'
        self.cursor.execute(id_query)
        raw_data = self.cursor.fetchall()
        latest_id = raw_data[0][0]

        # Flow stat query
        fsq = ('select Active_Flows, Packets_Looked_Up, Packets_Matched '
               f'from {node}_table0_summary where ID = {latest_id}')

        self.cursor.execute(fsq)
        raw_data = self.cursor.fetchall()

        active_flows = raw_data[0][0]
        pckts_looked_up = raw_data[0][1]
        pckts_matched = raw_data[0][2]

        device_info[node]['flow-stats'] = {'active_flows': active_flows,
                                           'packets_looked_up': pckts_looked_up,
                                           'packets_matched': pckts_matched
                                        }
        return device_info

    def pdtc(self, node, latest_date, penultimate_date):
        """
        pdtc stands for Per device throughput calculation.

        Returns:
        Dict - Each interface name as key and Rx and Tx
               port utalization in bps as value.
        """

        latest_counters = []
        pen_counters = []
        int_dict = {}

        latest_query = (f'select Interface, Tx_bytes, Rx_bytes from {node}_counters'
                        f' where Timestamp = "{latest_date}"')

        self.cursor.execute(latest_query)
        latest_raw_data = self.cursor.fetchall()

        pen_query = (f'select Interface, Tx_bytes, Rx_bytes from {node}_counters'
                     f' where Timestamp = "{penultimate_date}"')

        self.cursor.execute(pen_query)
        pen_raw_data = self.cursor.fetchall()

        for latest_row in latest_raw_data:
            new_tx = int(latest_row[1])
            new_rx = int(latest_row[2])
            latest_counters.append({'interface': latest_row[0],
                                    'tx_bytes': new_tx,
                                    'rx_bytes': new_rx})

        for pen_row in pen_raw_data:
            pen_tx = int(pen_row[1])
            pen_rx = int(pen_row[2])

            pen_counters.append({'interface': pen_row[0],
                                 'tx_bytes': pen_tx,
                                 'rx_bytes': pen_rx})

        # Catch topology change, length should be same
        if (len(latest_counters) != len(pen_counters)):
            return "err"

        for index, inter in enumerate(latest_counters):
            new_bytes_tx = latest_counters[index]['tx_bytes']
            new_bytes_rx = latest_counters[index]['rx_bytes']
            pen_bytes_tx = pen_counters[index]['tx_bytes']
            pen_bytes_rx = pen_counters[index]['rx_bytes']
            int_name = inter['interface']
            tx_bps = self.bps_cal(new_bytes_tx, pen_bytes_tx)
            rx_bps = self.bps_cal(new_bytes_rx, pen_bytes_rx)

            int_dict[int_name] = {
                                'tx_bps': tx_bps,
                                'rx_bps': rx_bps
                            }
        return int_dict

    def bps_cal(self, new_bytes, pen_bytes):
        """ Bits per second calculation
        Returns:
        Double - Bits transmitted in 10 second interval
        """
        return ((new_bytes - pen_bytes) / 10) * 8
