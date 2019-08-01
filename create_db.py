import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def create_table(conn):
    table = """CREATE TABLE IF NOT EXISTS flights (
                id integer PRIMARY KEY AUTOINCREMENT,
                airline text NOT NULL,
                price integer NOT NULL,
                duration text NOT NULL,
                stop text NOT NULL,
                departure_time text NOT NULL,
                arrival_time text NOT NULL,
                flight_route text NOT NULL
            );"""
    try:
        c = conn.cursor()
        c.execute(table)
    except Error as e:
        print(e)

def insert_flight(conn, flight):
    sql = ''' INSERT INTO flights(airline, price, duration, stop, departure_time, arrival_time, flight_route)
              VALUES(?,?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, flight)

