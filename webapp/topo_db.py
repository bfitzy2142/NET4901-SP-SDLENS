#!/usr/bin/env python3
import mysql.connector
from mysql.connector import errorcode
from time import strftime, localtime
import json


class Topo_DB_Interactions():
    """
        Module to handle SQL queries for topo webapp actions
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

    def switch_query(self, switch):
        """Method to get counters from the db to be
        displayed on the topology page when a user clicks
        an active switch.

        Attributes:
            Switch {str} - The switch to obtain statisitcs for.

        Returns:
            Dict {} - Port counter statistics
        """

        # Switch Statistics Table
        ctr_table = f"{switch}_counters"

        # Get lastest timestamp
        qry_latest = f"SELECT max(Timestamp) FROM {ctr_table}"

        raw_result = self.sql_select_query(qry_latest)
        date = str(raw_result[0][0])

        qry_sw = f'SELECT * FROM {ctr_table} WHERE Timestamp = "{date}"'

        raw_result = self.sql_select_query(qry_sw)

        dict_list = []

        for row in raw_result:
            d = {
                row[1]: {
                    "Rx_pckts": row[3],
                    "Tx_packs": row[4],
                    "Rx_drops": row[7],
                    "Tx_drops": row[8],
                    "Rx_errs": row[9],
                    "Tx_errs": row[10],
                    "Port_status": row[11],
                    "STP_status": row[12]
                }
            }
            dict_list.append(d)
        return dict_list

    def edge_query(self, edge):
        """
        Method used to obtain the links of a specified edge

        Attributes:
            edge {str}: the edge to be looked at

        Retruns:
            Dict {} - The source port and dest port
        """
        node_list = edge.split('-')

        query_edges = (f'select SRCPORT, DSTPORT from links where'
                       f'(SRC = "{node_list[0]}" and DST = "{node_list[1]}") or'
                       f'(SRC = "{node_list[1]}" and DST = "{node_list[0]}")')

        raw_result = self.sql_select_query(query_edges)
        return {'src_port': raw_result[0][0], 'dst_port': raw_result[0][1]}

    def host_query(self, host):
        """
        Method to obtain statistics on hosts within the topology

        Attributes:
            host {str}: host of interest

        Returns:
            Dict {} - Dictionary containing useful info on selected host
        """
        query_host = ('select IP_ADDRESS, FIRST_TIME_SEEN, LATEST_TIME_SEEN '
                      f'from host_info where HOST = "{host}"')

        raw_result = self.sql_select_query(query_host)

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

    def STP_query(self, switch):
        """
        Method to get the STP particpation status of
        the specified switch's Interfaces

        Parameters:
            Switch - The switch to obtain STP statisitcs for.

        Returns:
            Dict {} - Dictionary of switch's interfaces 
            and status of STP participation
        """
        # Switch Statistics Table
        ctr_table = f"{switch}_counters"

        # Get lastest timestamp
        qry_latest = f"SELECT max(Timestamp) FROM {ctr_table}"

        raw_result = self.sql_select_query(qry_latest)
        date = str(raw_result[0][0])

        qry_sw = f'SELECT Interface, STP_state FROM {ctr_table} WHERE Timestamp = "{date}"'

        raw_result = self.sql_select_query(qry_sw)

        sw_interfaces = {}
        for row in raw_result:
            sw_interfaces[row[0]] = {
                "stp_status": row[1]
                }
        return sw_interfaces

    def build_stp_topology(self):
        """
        A method used to obtain the L2 topology

        Returns:
        Dict {} - dictionary of link-IDs and
        their corespoinding Spanning Tree status
        """
        switches = self.get_switches()
        stp_status = {}

        # Get STP state for all interfaces
        for sw in switches:
            sw_stp_status = self.STP_query(sw)
            stp_status[sw] = sw_stp_status

        # Find links and assign STP state to them

        # Keep track of links already found
        ports_touched = []
        stp_topology = {}

        for switch in stp_status.keys():
            for inter in stp_status[switch].keys():
                if (inter not in ports_touched and 'LOCAL' not in inter):
                    query = ('select SRCPORT, DSTPORT from links where'
                            f' SRCPORT = "{inter}" or DSTPORT = "{inter}"')
                    raw_result = self.sql_select_query(query)
                    src_port = str(raw_result[0][0])
                    dst_port = str(raw_result[0][1])

                    ports_touched.append(src_port)
                    ports_touched.append(dst_port)

                    link_id = f'{src_port}-{dst_port}'
                    stp_port_stat = stp_status[switch][inter]['stp_status']
                    stp_topology[link_id] = stp_port_stat

        return stp_topology

    def get_switches(self):
        """Returns a list of switches stored in the DB."""

        switch_list = []
        query = "SELECT Node FROM nodes WHERE Type='switch'"
        switch_tuples = self.sql_select_query(query)

        for switch in switch_tuples:
            switch_list.append(str(switch[0].replace(":", "")))
        return switch_list

    def calculate_throughput(self, raw_node):
        """ Query method to get specified node's
        interfaces with transmitted and received bits
        calcalated from stats in the sql database.

        Arguments:
            raw_node = node containing ':'. Will have
                       each interface Tx and Rx 
                       throughput calculated for

        Returns:
            Dict {} - device and their interface rx & tx bps
        """
        node = raw_node.replace(":", "")
        # Find latest entry date and ID in DB
        date_n_ID = f'select max(ID), max(Timestamp) from {node}_counters'
        raw_data = self.sql_select_query(date_n_ID)
        newest_ID = int(raw_data[0][0])
        newest_date = str(raw_data[0][1])

        # Find number of links for the given switch
        link_num_query = (f'select ID from {node}_counters'
                          f' where Timestamp = "{newest_date}"')

        raw_link_num = self.sql_select_query(link_num_query)
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

        raw_pen_date = self.sql_select_query(penaltimate_qry)
        penultimate_date = str(raw_pen_date[0][0])

        device_info = {}
        device_info[node] = self.pdtc(node, newest_date, penultimate_date)

        # Get flow stats
        # Get latest id in db
        id_query = f'select max(ID) from {node}_table0_summary'
        raw_data = self.sql_select_query(id_query)
        latest_id = raw_data[0][0]

        # Flow stat query
        fsq = ('select Active_Flows, Packets_Looked_Up, Packets_Matched '
               f'from {node}_table0_summary where ID = {latest_id}')

        raw_data = self.sql_select_query(fsq)

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

        latest_raw_data = self.sql_select_query(latest_query)

        pen_query = (f'select Interface, Tx_bytes, Rx_bytes from {node}_counters'
                     f' where Timestamp = "{penultimate_date}"')

        pen_raw_data = self.sql_select_query(pen_query)

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
        Arguments:
            new_bytes: latest byte count
            pen_pytes: byte count from penultimate db entry

        Returns:
            Double - Bits transmitted in 10 second interval
        """
        num_switches = len(self.get_switches())

        # get the latest average agent runtime
        max_id = 'select max(ID) from average_agent_time;'

        raw_result = self.sql_select_query(max_id)

        average_time_query = ('select average_time from '
                              f'average_agent_time where ID ={raw_result[0][0]}')
        raw_result = self.sql_select_query(average_time_query)

        average_time = raw_result[0][0]
        # Approx 2 seconds to service a switch, 10 seconds between polls
        db_update_interarrival = (num_switches * average_time) + 10

        return int(((new_bytes - pen_bytes) / db_update_interarrival) * 8)

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
