#!/usr/bin/env python3
import json

STATUS_FILE = '/tmp/status.json'

with open(STATUS_FILE, 'r') as f:
    status = json.loads(f.read())

print('Content-type: text/html\r\n\r\n')

print('<h1>Indra Status</h1>')
print('<h2>Valve status: {}</h2>'.format(status['status']))
if 'valve' in status:
    print('<h2>Valve state: {}</h2>'.format(status['valve']))
if status['status'] == 'online':
    if status['valve'] == 'open':
        print('<form action="/cgi-bin/close_valve.py"><input type="Submit" value="Close valve"/>')
    else:
        print('<form action="/cgi-bin/open_valve.py"><input type="Submit" value="Open valve"/>')
print('<br><br><form action="/index.html"><input type="Submit" value="Back"/>')
print('<br><br><p>Last updated at {}</p>'.format(status['timestamp']))
