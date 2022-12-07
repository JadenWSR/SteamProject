#!/usr/bin/env python3

import enum
import sqlite3
from sqlite3 import Error
import pandas as pd
import numpy as np
import math
import urllib.parse


def create_connection(db_file="./game.db"):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

class database_API:
    DATABASE_URL = 'game.db'

    def __init__(self) -> None:
        self._connection = sqlite3.connect(self.DATABASE_URL)
        self._cursor = self._connection.cursor()
        self.create_tables()

    def create_tables(self):
        """ Create all the tables
        """
        # self._cursor.execute('''DROP TABLE IF EXISTS Steam_game''')
        self._cursor.execute('''CREATE TABLE IF NOT EXISTS Steam_game
                        (appid INT PRIMARY KEY,
                        name TEXT,
                        release_date TEXT,
                        genre TEXT,
                        tags TEXT,
                        categories TEXT,
                        developer_id TEXT)''')

        # self._cursor.execute('''DROP TABLE IF EXISTS Developer''')
        self._cursor.execute('''CREATE TABLE IF NOT EXISTS Developer
                        (developer_id INT PRIMARY KEY,
                        developer_name TEXT)''')
        # self._cursor.execute('''DROP TABLE IF EXISTS Detail''')
        self._cursor.execute('''CREATE TABLE IF NOT EXISTS Detail
                        (appid INT PRIMARY KEY,
                        language TEXT,
                        description TEXT,
                        website TEXT,
                        FOREIGN KEY (appid)
                            REFERENCES Steam_game (appid))''')
        # self._cursor.execute('''DROP TABLE IF EXISTS Require''')
        self._cursor.execute('''CREATE TABLE IF NOT EXISTS Require
                        (appid INT PRIMARY KEY,
                        pc TEXT,
                        mac TEXT,
                        linux TEXT,
                        FOREIGN KEY (appid)
                            REFERENCES Steam_game (appid))''')
        # self._cursor.execute('''DROP TABLE IF EXISTS Dlc''')
        self._cursor.execute('''CREATE TABLE IF NOT EXISTS Dlc
                        (appid INT PRIMARY KEY,
                        name TEXT,
                        release_date TEXT,
                        genre TEXT,
                        categories TEXT,
                        tags TEXT,
                        developer_id TEXT,
                        parent_id INT,
                        FOREIGN KEY (parent_id)
                            REFERENCES Steam_game (appid))''')

        self._cursor.execute('''CREATE INDEX IF NOT EXISTS parent ON Dlc (parent_id) ''')

        

    def insert(self,table_name, data):
        """ insert rows into the table
        """
        try: 
            qurey = """INSERT INTO """ + table_name + """ VALUES""" + str(data)
            self._cursor.execute(qurey)
            self._connection.commit()
        except:
            print(data)



    def insert_game(self, data):
        self.insert('Steam_game', data)
    
    def insert_dlc(self, data):
        self.insert('Dlc', data)

    def insert_developer(self, data):
        self.insert('Developer', data)

    def insert_detail(self, data):
        self.insert('Detail', data)
    
    def insert_require(self, data):
        self.insert('Require', data)

    def get_dev_name(self, id):
        query = """SELECT developer_name
                    FROM Developer
                    WHERE developer_id = ?"""
        self._cursor.execute(query, (id,))
        return self._cursor.fetchall()

    def get_details(self, id):
        query = """SELECT language, description
                    FROM Detail
                    WHERE appid = ?"""
        self._cursor.execute(query, (id,))
        return self._cursor.fetchall()

    def get_requirement(self, id):
        query = """SELECT pc, mac, linux
                    FROM Require
                    WHERE appid = ?"""
        self._cursor.execute(query, (id,))
        return self._cursor.fetchall()


    def get_dlc(self, id):
        query = """SELECT group_concat(name,\' / \')
                    FROM Dlc
                    WHERE parent_id = ?"""
        self._cursor.execute(query, (id,))
        return self._cursor.fetchall()






class CLI:
    def __init__(self) -> None:
            create_connection()
            self._tmp_event_args = None
            self._api = database_API()

    def add_game(self):
        
        df = pd.read_csv(r"./Data/steam_game.csv", header=0, sep=",", low_memory=False).fillna('')
        rows = df.values
        for row in rows:
            # row = [i if not math.isnan(i) else '' for i in row]
            data = tuple(row[1::])
            self._api.insert_game(data)
        print('Successfully added!')

    def add_dlc(self):
        
        df = pd.read_csv(r"./Data/dlc.csv", header=0, sep=",", low_memory=False).fillna('')
        rows = df.values
        for row in rows:
            # row = [i if not math.isnan(i) else '' for i in row]
            if row[-1]:
                row[-1] = int(row[-1])
            else:
                continue
            for i in range(2,3):
                row[i] = urllib.parse.quote_plus(row[i])
            data = tuple(row[1::])
            self._api.insert_dlc(data)
        print('Successfully added!')
    def add_developer(self):
        
        df = pd.read_csv(r"./Data/Developer.csv", header=0, sep=",", low_memory=False).fillna('')
        rows = df.values
        for row in rows:
            row[2] = str(row[2])
            # row = [i if not math.isnan(i) else '' for i in row]
            data = tuple(row[1::])
            self._api.insert_developer(data)
        print('Successfully added!')

    def add_detail(self):
        
        df = pd.read_csv(r"./Data/Detail.csv", header=0, sep=",", low_memory=False).fillna('')
        rows = df.values
        for row in rows:
            for i in range(2,len(row)):
                row[i] = urllib.parse.quote_plus(row[i])
            data = tuple(row[1::])
            self._api.insert_detail(data)
        print('Successfully added!')

    def add_require(self):
        df = pd.read_csv(r"./Data/Requirement.csv", header=0, sep=",", low_memory=False).fillna('')
        rows = df.values
        for row in rows:
            for i in range(2,len(row)):
                row[i] = urllib.parse.quote_plus(row[i])
                # for decode use urllib.parse.unquote(string)
            data = tuple(row[1::])
            self._api.insert_require(data)
        print('Successfully added!')


    def run(self):
        while True:
            std_in = input("Press 1 for adding game, 2 for developer, 3 for detail, 4 for requirement, 5 for dlc\n")
            match std_in:
                case '1':
                    self.add_game()
                case '2':
                    self.add_developer()
                case '3':
                    self.add_detail()
                case '4':
                    self.add_require()
                case '5':
                    self.add_dlc()




if __name__ == '__main__':
    cli = CLI()
    cli.run()