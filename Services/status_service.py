#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import sqlite3
import time
import os.path
import json
from datetime import date

DATABASE = '/tmp/waterings.db'
MQTT_HOST = ''
MQTT_CA_CERTS = ''
MQTT_CERTFILE = ''
MQTT_KEYFILE = ''
MQTT_PORT = 8883
MQTT_KEEPALIVE = 60


valve = ''
mqttc = None



def init_mqtt():
    global mqttc
    # Init MQTT client
    mqttc = mqtt.Client()
    mqttc.tls_set(ca_certs=MQTT_CA_CERTS, certfile=MQTT_CERTFILE, keyfile=MQTT_KEYFILE)
    mqttc.connect(host=MQTT_HOST, port=MQTT_PORT, keepalive=MQTT_KEEPALIVE)

    # Register callback for messages when valve state has changed
    mqttc.message_callback_add('indra/device/valve', received_valve_msg)
    mqttc.loop_start()


if __name__ == "__main__":
    # Wait for database file to be created if it does not exist yet
    while not os.path.isfile(DATABASE):
        time.sleep(1)

    # Initialize the mqtt client
    init_mqtt()

    # Ensure that the valve is closed before entering loop
    close_valve()

    # Start the loop to check for waterings
    watering_loop()
