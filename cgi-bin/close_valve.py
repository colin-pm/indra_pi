#!/usr/bin/env python3
import paho.mqtt.publish as publish
import json

MQTT_HOST = ''
MQTT_CA_CERTS = '/home/pi/keys/root-CA.crt'
MQTT_CERTFILE = '/home/pi/keys/control_server.cert.pem'
MQTT_KEYFILE = '/home/pi/keys/control_server.private.key'
MQTT_TOPIC = 'indra/command/valve'
MQTT_PORT = 8883
MQTT_KEEPALIVE = 60

tls_dict = {'ca_certs': MQTT_CA_CERTS,
            'certfile': MQTT_CERTFILE,
            'keyfile': MQTT_KEYFILE}

publish.single(MQTT_TOPIC,
               json.dumps({'valve': 'close'}),
               qos=1,
               retain=False,
               hostname=MQTT_HOST,
               port=MQTT_PORT,
               keepalive=60,
               tls=tls_dict)

print('Content-type: text/html\r\n\r\n')
print('<h1>Close valve command has been sent.</h1>')
print('<h3>Note: Status page may not reflect new valve state for up to one minute')
print('<br><br><br><form action="/cgi-bin/get_status.py"><input type="Submit" value="Return"/></form>')
