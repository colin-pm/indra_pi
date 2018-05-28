#!/usr/bin/env python3

import cgi
import cgitb
import sys
import sqlite3
cgitb.enable()

success = False

# Set up SQL command to remove watering from schedule
form = cgi.FieldStorage()
sql_cmd = 'DELETE FROM waterings WHERE id={}'.format(form.getvalue('watering'))

# Connect to database and run SQL command


print('Content-type: text/html\r\n\r\n')
sys.flush()

if success:
    print('<h1>Watering has been removed from schedule</h1>')
else:
    print('<h1>ERROR: Not able to remove watering from schedule</h1>')

print('<br><form action="watering_schedule.html"><input type="Submit" value="Return"/></form>')
