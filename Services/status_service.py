#!/usr/bin/env python3
# This script will be set up to run on 1 minute intervals by cron
import paho.mqtt.client as mqtt
import time
import json

STATUS_FILE = '/tmp/status.json'
MQTT_HOST = '' # Add your own AWS address here
MQTT_CA_CERTS = '' # Add your own certs here and below
MQTT_CERTFILE = ''
MQTT_KEYFILE = ''
MQTT_PORT = 8883
MQTT_KEEPALIVE = 60

DEBUG = False

status = False
mqttc = None
response = {}


def init_mqtt():
    global mqttc, DEBUG
    # Init MQTT client
    mqttc = mqtt.Client()
    mqttc.tls_set(ca_certs=MQTT_CA_CERTS, certfile=MQTT_CERTFILE, keyfile=MQTT_KEYFILE)
    mqttc.connect(host=MQTT_HOST, port=MQTT_PORT, keepalive=MQTT_KEEPALIVE)

    # Register callback for messages when valve state has changed
    mqttc.loop_start()
    mqttc.subscribe('indra/device/status', 0)
    mqttc.message_callback_add('indra/device/status', received_status)
    if DEBUG:
        print('Initialized mqtt client')


def create_status_file(data):
    global DEBUG
    with open(STATUS_FILE, 'w+') as f:
        f.write(json.dumps(data))
    if DEBUG:
        print('Wrote JSON payload to {}'.format(STATUS_FILE))


def received_status(client, userdata, message):
    global status, DEBUG, response
    if DEBUG:
        print('Received message from endpoint device...')
        print('"{}"'.format(message.payload.decode('UTF-8')))
    response = json.loads(message.payload.decode('UTF-8'))
    response['timestamp'] = time.asctime(time.localtime(time.time()))
    response['status'] = 'online'
    status = True


def request_status():
    global mqttc, DEBUG
    mqttc.publish('indra/command/status',
                  json.dumps(['valve']),
                  qos=1)
    if DEBUG:
        print('Sent status request message')


if __name__ == "__main__":
    # Initialize the mqtt client
    count = 0
    init_mqtt()

    request_status()

    while not status and count < 5:
        if DEBUG:
            print('Waited {} seconds for message'.format(count * 12))
        time.sleep(12)
        count += 1

    if not status:
        if DEBUG:
            print('Never heard from endpoint device, assuming device is offline')
        response = {'timestamp': time.asctime(time.localtime(time.time())), 'status': 'offline'}
    create_status_file(response)
