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

def watering_loop():
    global valve
    while True:
        # Get day of week
        day = get_day_num()
        # Get waterings for current day
        waterings = get_waterings(day)
        # Get current time for watering
        curr_time = time.strftime('%H:%M').spit(':')
        # Check watering schedule and open or close valve if appropriate
        for watering in waterings:
            stop_time = (watering[0] + int(watering[2] / 60), watering[1] + (watering[2] % 60))
            if (curr_time[0] == watering[0] and curr_time[1] > watering[1]) or (curr_time[0] > watering[0]):
                if (curr_time[0] == stop_time[0] and curr_time[1] < stop_time[1]) or (curr_time[0] < stop_time[0]):
                    if valve == "closed":
                        open_valve()
                else:
                    if valve == "open":
                        close_valve()
            else:
                if valve == "open":
                    close_valve()
        # Sleep for a minute before checking again
        time.sleep(60)



def open_valve():
    cmd_payload = {'valve': 'open'}
    mqttc.publish('indra/command/valve', json.dumps(cmd_payload), qos=2)


def close_valve():
    cmd_payload = {'valve': 'closed'}
    mqttc.publish('indra/command/valve', json.dumps(cmd_payload), qos=2)


def received_valve_msg(client, userdata, message):
    global valve
    valve = json.loads(message.payload)['valve']


def init_mqtt():
    global mqttc
    # Init MQTT client
    mqttc = mqtt.Client()
    mqttc.tls_set(ca_certs=MQTT_CA_CERTS, certfile=MQTT_CERTFILE, keyfile=MQTT_KEYFILE)
    mqttc.connect(host=MQTT_HOST, port=MQTT_PORT, keepalive=MQTT_KEEPALIVE)

    # Register callback for messages when valve state has changed
    mqttc.message_callback_add('indra/device/valve', received_valve_msg)
    mqttc.loop_start()


def get_waterings(day):
    command = 'Select hour, minute, duration FROM waterings WHERE day == ? ORDER BY hour, minute'
    db = sqlite3.connect(DATABASE)
    return [row for row in db.execute(command, day)]


def get_day_num():
    day_num = date.isoweekday(date.today())
    return day_num + 1 if day_num != 7 else 1


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
