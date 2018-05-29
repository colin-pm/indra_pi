#!/usr/bin/env python3
import sys
import sqlite3

DATABASE = '/tmp/waterings.db'
success = False

# Connect to database and run SQL command
conn = sqlite3.connect(DATABASE)
cur = conn.execute('DELETE FROM waterings')
if cur.rowcount > 0:
    success = True
conn.commit()
conn.close()

print('Content-type: text/html\r\n\r\n')
sys.stdout.flush()

if success:
    print('<h1>All waterings have been removed from schedule</h1>')
else:
    print('<h1>ERROR: Not able to remove all waterings from schedule</h1>')

print('<br><form action="/cgi-bin/watering_schedule.py"><input type="Submit" value="Return"/></form>')
