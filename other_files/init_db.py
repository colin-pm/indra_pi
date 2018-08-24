#!/usr/env/ python3

# Indra database setup
# by Colin McAllister
# 5/28/2018

# Do not place this script in cgi-bin.  This should only be ran by an admin
# to start the sqlite database
#
# This script should be ran with sudoers privileges on boot


import sqlite3
import os.path
import stat

DATABASE = '/tmp/waterings.db'

conn = sqlite3.connect(DATABASE)

with open('/home/pi/schema.sql', 'r') as f:
    conn.executescript(f.read())

conn.commit()
conn.close()

os.chmod(DATABASE, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
