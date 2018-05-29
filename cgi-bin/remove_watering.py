#!/usr/bin/env python3
import cgi
import cgitb
import sys
import sqlite3
cgitb.enable()

DATABASE = '/tmp/waterings.db'

success = False

# Parse input from
form = cgi.FieldStorage()

# Connect to database and run SQL command
conn = sqlite3.connect(DATABASE)
cur = conn.execute('DELETE FROM waterings WHERE id=?', (form.getvalue('watering'),))
if cur.rowcount == 1:
    success = True
conn.commit()
conn.close()

print('Content-type: text/html\r\n\r\n')
sys.stdout.flush()

if success:
    print('<h1>Watering has been removed from schedule</h1>')
else:
    print('<h1>ERROR: Not able to remove watering from schedule (ID# {})</h1>'.format(form.getvalue('watering')))

print('<br><form action="/cgi-bin/watering_schedule.py"><input type="Submit" value="Return"/></form>')
