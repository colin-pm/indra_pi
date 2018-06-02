#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import sqlite3
import time
import os.path
import json
from datetime import date

DATABASE = '/tmp/waterings.db'
MQTT_HOST = '' # Insert own AWS host address, cert, & key files here
MQTT_CA_CERTS = ''
MQTT_CERTFILE = ''
MQTT_KEYFILE = ''
MQTT_PORT = 8883
MQTT_KEEPALIVE = 60

DEBUG = True

valve = ''
mqttc = None

def watering_loop():
    global valve, DEBUG
    while True:
        # Get day of week
        day = get_day_num()
        # Get waterings for current day
        waterings = get_waterings(day)
        # Get current time for watering
        curr_time = [int(num) for num in time.strftime('%H:%M').split(':')]
        if DEBUG:
            print('Current time: {0}:{1}'.format(curr_time[0], curr_time[1]))
        # Check watering schedule and open or close valve if appropriate
        for watering in waterings:
            stop_time = (watering[0] + int(watering[2] / 60), watering[1] + (watering[2] % 60))
            if (curr_time[0] == watering[0] and curr_time[1] >= watering[1]) or (curr_time[0] > watering[0]):
                if (curr_time[0] == stop_time[0] and curr_time[1] < stop_time[1]):
                    if DEBUG:
                        print("In scheduled watering period")
                    if valve == 'closed':
                        duration = stop_time[1] - curr_time[1]
                        open_valve(duration)
                elif curr_time[0] < stop_time[0]:
                    if DEBUG:
                        print("In watering period")
                    if valve == 'closed':
                        duration = ((stop_time[0] - curr_time[0]) * 60) + (stop_time[1] - curr_time[1])
                        open_valve(duration)
                elif valve == "open":
                    if DEBUG:
                        print("Left watering period with open valve")
                    close_valve()
            elif valve == "open":
                close_valve()
        # Sleep for half a minute before checking again
        time.sleep(30)


def open_valve(duration):
    global DEBUG
    if DEBUG:
        print('Opening valve for {}'.format(duration))
    cmd_payload = {'valve': 'open', 'duration': duration}
    mqttc.publish('indra/command/valve', json.dumps(cmd_payload), qos=1)


def close_valve():
    global DEBUG
    if DEBUG:
        print('Closing valve')
    cmd_payload = {'valve': 'close'}
    mqttc.publish('indra/command/valve', json.dumps(cmd_payload), qos=1)


def received_valve_msg(client, userdata, message):
    global valve, DEBUG
    if DEBUG:
        print('Received message: "{}"'.format(message.payload.decode('UTF-8')))
    valve = json.loads(message.payload.decode('UTF-8'))['valve']


def init_mqtt():
    global mqttc, DEBUG
    # Init MQTT client
    mqttc = mqtt.Client()
    mqttc.tls_set(ca_certs=MQTT_CA_CERTS, certfile=MQTT_CERTFILE, keyfile=MQTT_KEYFILE)
    mqttc.connect(host=MQTT_HOST, port=MQTT_PORT, keepalive=MQTT_KEEPALIVE)

    # Register callback for messages when valve state has changed
    mqttc.loop_start()
    mqttc.subscribe('indra/device/valve', 0)
    mqttc.message_callback_add('indra/device/valve', received_valve_msg)
    if DEBUG:
        print('Initialized MQTT client')


def get_waterings(day):
    global DEBUG
    command = 'Select hour, minute, duration FROM waterings WHERE day == ? ORDER BY hour, minute'
    db = sqlite3.connect(DATABASE)
    if DEBUG:
        print("Today's waterings:")
        for row in db.execute(command,(day,)):
            print(row)
    return [row for row in db.execute(command, (day,))]


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
    if DEBUG:
        print('Initially ensuring that valve is closed')
    close_valve()

    # Safety measure to ensure valve is online before entering loop
    while valve == '':
        if DEBUG:
            print('wating to hear that valve is closed')
        time.sleep(10)

    # Start the loop to check for waterings
    if DEBUG:
        print('Entering main service loop')
    watering_loop()
