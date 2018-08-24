#!/usr/bin/env python3
import json
import configparser
from paho import mqtt

STATUS_FILE = '/tmp/status.json'
CONFIG_PATH = '/home/pi/indra_target/config'


def on_status_received(client, userdata, message):
    payload = json.loads(message.payload.decode('UTF-8'))
    status = payload['status']
    timestamp = payload['timestamp']


# Parse config file
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# Init MQTT client
MQTTC = mqtt.Client()
MQTTC.tls_set(ca_certs=config['MQTT_CA_CERT'],
              certfile=config['MQTT_CERTFILE'],
              keyfile=config['MQTT_KEYFILE'])
MQTTC.connect(host=config['MQTT_HOST'],
              port=config['MQTT_PORT'],
              keepalive=config['MQTT_KEEPALIVE'])
MQTTC.loop_start()

# Subscribe to topic for manual commands
MQTTC.subscribe('indra/status', 0)
MQTTC.message_callback_add('indra/stats', on_status_received)

# Publish request for status
MQTTC.

print('Content-type: text/html\r\n\r\n')

print('<h1>Indra Status</h1>')
print('<h2>Valve status: {}</h2>'.format(status['status']))
if 'valve' in status:
    print('<h2>Valve state: {}</h2>'.format(status['valve']))
print('<br><br><form action="/index.html"><input type="Submit" value="Back"/></form>')
print('<br><br><p>Last updated at {}</p>'.format(status['timestamp']))