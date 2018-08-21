#!/usr/bin/env python3
import json

# TODO Update to use device shadow

STATUS_FILE = '/tmp/status.json'

with open(STATUS_FILE, 'r') as f:
    status = json.loads(f.read())

print('Content-type: text/html\r\n\r\n')

print('<h1>Indra Status</h1>')
print('<h2>Valve status: {}</h2>'.format(status['status']))
if 'valve' in status:
    print('<h2>Valve state: {}</h2>'.format(status['valve']))
print('<br><br><form action="/index.html"><input type="Submit" value="Back"/></form>')
print('<br><br><p>Last updated at {}</p>'.format(status['timestamp']))