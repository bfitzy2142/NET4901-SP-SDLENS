#!/usr/bin/env python3
"""
@author: Sam Cook
MySql Parser for graphical presentation
"""
import mysql.connector
from mysql.connector import Error


class sql_graph_info(object):    
    def __init__(self, databaseIP):
        """
        Initializer for the sql_graph_info Object.
        """
        self.databaseIP = databaseIP
    
    def get_table_count(self):
        """
        Gets the number of openflow tables.
        """
        mydb = mysql.connector.connect(
            host=self.databaseIP,
            user="root",
            passwd="root",
            database="sdlens"
        )
        cursor = mydb.cursor()
        query = (
            f'SHOW TABLES FROM sdlens LIKE "openflow%_info";'
        )
        cursor.execute(query)
        response = list(cursor)

        table_count = 0
        for i in response:
            table_count = table_count + 1

        return table_count