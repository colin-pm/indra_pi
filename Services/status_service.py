#!/usr/bin/env python3
# This script will be set up to run on 1 minute intervals by cron
import paho.mqtt.client as mqtt
import time
import json

STATUS_FILE = '/tmp/status.json'
MQTT_HOST = ''
MQTT_CA_CERTS = ''
MQTT_CERTFILE = ''
MQTT_KEYFILE = ''
MQTT_PORT = 8883
MQTT_KEEPALIVE = 60

status = False
mqttc = None


def init_mqtt():
    global mqttc
    # Init MQTT client
    mqttc = mqtt.Client()
    mqttc.tls_set(ca_certs=MQTT_CA_CERTS, certfile=MQTT_CERTFILE, keyfile=MQTT_KEYFILE)
    mqttc.connect(host=MQTT_HOST, port=MQTT_PORT, keepalive=MQTT_KEEPALIVE)

    # Register callback for messages when valve state has changed
    mqttc.message_callback_add('indra/device/status', received_status)
    mqttc.loop_start()


def create_status_file(data):
    with open(STATUS_FILE, 'w+') as f:
        f.write(json.dumps(data))


def received_status(client, userdata, message):
    global status
    response = json.loads(message.payload)
    response['timestamp'] = time.asctime(time.localtime(time.time()))
    status = True


def request_status():
    global mqttc
    mqttc.publish('indra/command/status',
                  json.dumps(['valve']),
                  qos=2)


if __name__ == "__main__":
    # Initialize the mqtt client
    count = 0
    init_mqtt()

    request_status()

    while not status or count < 5:
        time.sleep(12)

    if not status:
        response = {'timestamp': time.asctime(time.localtime(time.time())), 'status': 'offline'}
        create_status_file(response)
