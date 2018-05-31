#!/usr/bin/env python3
import paho.mqtt.publish as publish
import json

MQTT_HOST = ''
MQTT_CA_CERTS = ''
MQTT_CERTFILE = ''
MQTT_KEYFILE = ''
MQTT_TOPIC = 'indra/command/valve'
MQTT_PORT = 8883
MQTT_KEEPALIVE = 60

tls_dict = {'ca_certs': MQTT_CA_CERTS,
            'certfile': MQTT_CERTFILE,
            'keyfile': MQTT_KEYFILE}

publish.single(MQTT_TOPIC,
               json.dumps({'valve': 'open'}),
               qos=1,
               retain=False,
               hostname=MQTT_HOST,
               port=MQTT_PORT,
               keepalive=60,
               tls=tls_dict,
               transport="tcp")
