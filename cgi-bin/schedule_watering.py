#!/usr/bin/env python3
import cgi
import cgitb
import sys
import sqlite3
cgitb.enable()


def get_24hour(hour, period):
    """
    Converts 12-hour time string to 24-hour
    :param hour: string
    :param period: either 'AM' or 'PM' string
    :return: 24-hour string
    """
    if period == "PM":
        if hour != "12":
            return str(int(hour) + 12)
    elif hour == "12":
            return '0'
    return hour


def check_duration(duration):
    """
    Sanitizes input from text box
    :param duration: Text box input
    :return: Sanitized duration or error message
    """
    if len(duration) > 3:
        return "bad length"
    try:
        int(duration)
    except ValueError:
        return "not int"
    if int(duration) < 0 or int(duration) > 300:
        return "out of range"
    return duration


# SQLITE database
DATABASE = '/tmp/waterings.db'

# Print header
print('Content-type: text/html\r\n\r\n')
sys.stdout.flush()

# Bool indicating if command was successful
success = False
# Connect to database and run SQL command
conn = sqlite3.connect(DATABASE)
form = cgi.FieldStorage()
day = form.getvalue('day')
if isinstance(day, list):
    for d in day:
        hour = get_24hour(form.getvalue('hour'), form.getvalue('period'))
        minute = form.getvalue('minute')
        duration = check_duration(form.getvalue('duration'))
        if duration == "bad length" or duration == "out of range":
            print('<h1>ERROR: Duration can only be in range of 1 to 300 minutes</h1>')
            print('<br><form action="watering_schedule.html"><input type="Submit" value="Return"/></form>')
            quit()
        elif duration == "not int":
            print('<h1>ERROR: Input is not an integer</h1>')
            print('<br><form action="watering_schedule.html"><input type="Submit" value="Return"/></form>')
            quit()
        cur = conn.execute('INSERT INTO waterings (day, hour, minute, duration) VALUES (?, ?, ?, ?)', (d,hour,minute,duration))
        if cur.rowcount == 1:
            success = True
else:
    hour = get_24hour(form.getvalue('hour'), form.getvalue('period'))
    minute = form.getvalue('minute')
    duration = check_duration(form.getvalue('duration'))
    if duration == "bad length" or duration == "out of range":
        print('<h1>ERROR: Duration can only be in range of 1 to 300 minutes</h1>')
        print('<br><form action="watering_schedule.html"><input type="Submit" value="Return"/></form>')
        quit()
    elif duration == "not int":
        print('<h1>ERROR: Input is not an integer</h1>')
        print('<br><form action="watering_schedule.html"><input type="Submit" value="Return"/></form>')
        quit()
    cur = conn.execute('INSERT INTO waterings (day, hour, minute, duration) VALUES (?, ?, ?, ?)', (day,hour,minute,duration))
    if cur.rowcount == 1:
        success = True
conn.commit()
conn.close()

if success:
    print('<h1>Watering has been added to schedule</h1>')
else:
    print('<h1>ERROR: Not able to add watering to schedule</h1>')

print('<br><form action="/schedule_watering.html"><input type="Submit" value="Add another watering to schedule"/></form>')
print('<br><form action="/cgi-bin/watering_schedule.py"><input type="Submit" value="Return to schedule"/></form>')
