#!/usr/bin/env python3
import json
import time
import configparser
import paho.mqtt.client as mqtt

# Constants
STATUS_FILE = '/tmp/status.json'
CONFIG_PATH = '/home/pi/other_files/config'

# Variables to hold values from status message
valve = None
load = None
uptime = None
voltage = None
speed = None
received = False


# Create callback for received status message
def on_status_received(client, userdata, message):
    global valve, load, uptime, voltage, speed, received
    received = True
    payload = json.loads(message.payload.decode('UTF-8'))
    valve = payload['valve']
    uptime = payload['uptime']
    voltage = payload['voltage']
    speed = payload['speed']


# Parse config file
config = configparser.ConfigParser()
config.read(CONFIG_PATH)
config = config['DEFAULT']

# Init MQTT client
MQTTC = mqtt.Client()
MQTTC.tls_set(ca_certs=config['MQTT_CA_CERT'],
              certfile=config['MQTT_CERTFILE'],
              keyfile=config['MQTT_KEYFILE'])
MQTTC.connect(host=config['MQTT_HOST'],
              port=int(config['MQTT_PORT']),
              keepalive=int(config['MQTT_KEEPALIVE']))
MQTTC.loop_start()

# Subscribe to topic for manual commands
MQTTC.subscribe('indra/status', 0)
MQTTC.message_callback_add('indra/status', on_status_received)

# Print page header
print('Content-type: text/html\r\n\r\n')

# Publish request for status
MQTTC.publish('indra/command',
              payload=json.dumps('status'),
              qos=1)

# Create status page
for _ in range(10):
    time.sleep(1)
    if received:
        print('<h1>Indra Status</h1>')
        print('<h2>Valve: {}</h2>'.format(valve))
        print('<h2>Uptime: {}</h2>'.format(uptime))
        print('<h2>CPU voltage: {} V</h2>'.format(voltage))
        print('<h2>CPU speed: {} MHz</h2>'.format(int(speed) / 1000000))
        break
else:
    print('<h1>Indra is offline!</h1>')

print('<br><br><form action="/index.html"><input type="Submit" value="Back"/></form>')

# Disconnect broker
MQTTC.loop_stop()
MQTTC.disconnect()
