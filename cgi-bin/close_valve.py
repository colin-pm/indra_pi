#!/usr/bin/env python3
import paho.mqtt.publish as publish
import json

MQTT_HOST = ''
MQTT_CA_CERTS = ''
MQTT_CERTFILE = ''
MQTT_KEYFILE = ''
MQTT_TOPIC = 'indra/command/valve'
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

tls_dict = {'ca_certs':MQTT_CA_CERTS,
        'certfile':MQTT_CERTFILE,
        'keyfile':MQTT_KEYFILE}


cmd_payload = {'valve': 'close'}
publish.single(MQTT_TOPIC,
               json.dumps(cmd_payload),
               qos=2,
               retain=False,
               hostname=MQTT_HOST,
               port=1883,
               client_id="",
               keepalive=60,
               will=None,
               auth=None,
               tls=tls_dict,
               protocol=mqtt.MQTTv311,
               transport="tcp")