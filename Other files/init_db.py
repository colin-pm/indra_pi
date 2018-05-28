#!/usr/env/ python3

"""
Indra database setup
by Colin McAllister
5/28/2018

Do not place this script in cgi-bin.  This should only be ran by an admin
to start the sqlite database
""""

import sqlite3

DATABASE = '/tmp/waterings.db'

conn = sqlite3.connect(DATABASE)

with open('./schema.sql', 'r') as f:
    conn.executescript(f.read().decode('utf8'))

conn.commit()
conn.close()
