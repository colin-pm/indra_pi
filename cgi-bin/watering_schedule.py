#!/usr/bin/env python2
import cgi
import cgitb
import sys
import sqlite3
from jinja2 import Environment, FileSystemLoader, select_autoescape, PackageLoader
cgitb.enable()


def get_day(num):
    if num == 1: return 'sunday'
    if num == 2: return 'monday'
    if num == 3: return 'tuesday'
    if num == 4: return 'wednesday'
    if num == 5: return 'thursday'
    if num == 6: return 'friday'
    if num == 7: return 'saturday'


def get_hour(hour):
    if int(hour) == 0:
        return 12
    elif int(hour) > 12:
        return int(hour) - 12
    else:
        return hour


DATABASE = '/tmp/waterings.db'

# Connect to database and run SQL command
conn = sqlite3.connect(DATABASE)

days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
waterings = {'sunday': [], 'monday': [], 'tuesday': [], 'wednesday': [], 'thursday': [], 'friday': [], 'saturday': []}

# Place SQL data into dictionary object to use with jinja2
for row in conn.execute('Select * FROM waterings ORDER BY hour, minute'):
    day = get_day(row[1])
    watering = {}
    watering['id'] = row[0]
    watering['day'] = day
    watering['period'] = "AM" if row[2] < 12 else "PM"
    watering['hour'] = get_hour(row[2])
    watering['minute'] = "0" + str(row[3]) if len(str(row[3])) == 1 else str(row[3])
    watering['duration'] = row[4]
    waterings[day].append(watering)

#Output webpage using jinja2
print('Content-type: text/html\r\n\r\n')
sys.stdout.flush()
env = Environment(loader=FileSystemLoader('/home/pi/templates/'), autoescape=select_autoescape(['html', 'xml']))
template = env.get_template('watering_schedule.html')
print(template.render(days=days, waterings=waterings))
