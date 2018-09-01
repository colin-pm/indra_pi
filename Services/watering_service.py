#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import sqlite3
import time
import os.path
import logging
import json
import configparser
from os import path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import date

CONFIG_PATH = '/home/pi/other_files/config'
LOG_PATH = '/tmp/watering_service.log'
DEBUG_LVL = logging.DEBUG
LAST_UPDATE = time.time()
MQTTC = None


class DatabaseWatcher(FileSystemEventHandler):
    """
    Class for /tmp directory watchdog
    """
    def on_created(self, event):
        """
        Called when a file in /tmp is created (non-recursive)
        :param event:
        :return:
        """
        global LAST_UPDATE
        if event.src_path == config['DATABASE']:
            LAST_UPDATE = time.time()
            send_schedule()

    def on_modified(self, event):
        """
        Called when a file in /tmp is modified (non-recursive)
        :param event:
        :return:
        """
        global LAST_UPDATE
        if event.src_path == config['DATABASE']:
            LAST_UPDATE = time.time()
            send_schedule()


def initialize_client():
    """
    Creates and connects MQTT client
    :return: MQTT client object
    """
    log.info('Initializing MQTT client')
    # Init MQTT client
    MQTTC = mqtt.Client()
    MQTTC.on_connect = on_connect
    MQTTC.tls_set(ca_certs=config['MQTT_CA_CERT'],
                  certfile=config['MQTT_CERTFILE'],
                  keyfile=config['MQTT_KEYFILE'])
    MQTTC.connect(host=config['MQTT_HOST'],
                  port=int(config['MQTT_PORT']),
                  keepalive=int(config['MQTT_KEEPALIVE']))
    MQTTC.loop_start()

    # Subscribe to topic for schedule requests
    MQTTC.subscribe('indra/schedule_request', 0)
    MQTTC.message_callback_add('indra/schedule_request', on_schedule_request)
    return MQTTC


def on_schedule_request(client, userdata, message):
    """
    Callback for messages received on schedule request topic.  Sends schedule as response.
    """
    print(float(json.loads(message.payload.decode('UTF-8'))['timestamp']))
    if LAST_UPDATE > float(json.loads(message.payload.decode('UTF-8'))['timestamp']):
        send_schedule()


def on_connect(client, userdata, flags, rc):
    """
    Callback for MQTT client connects and reconnects.  Sends schedule.
    """
    log.info('Connected to AWS')
    # Send schedule in case a request was missed
    send_schedule()


def send_schedule():
    """
    Create and send MQTT message with waterings and timestamp
    """
    MQTTC.publish('indra/schedule',
                  payload=json.dumps({'waterings': get_waterings(), 'timestamp': LAST_UPDATE}),
                  qos=1)
 

def get_waterings():
    """
    Gets waterings from sqlite database
    :return: 2D list object containing waterings
    """
    command = 'SELECT day, hour, minute, duration FROM waterings ORDER BY day, hour, minute'
    db = sqlite3.connect(config['DATABASE'])
    schedule = [[] for _ in range(7)]
    for row in db.execute(command):
        schedule[row[0]].append(row[1:])
    for day in schedule:
        day.sort()
    return schedule


def get_day_num():
    """
    Modifies date.isoweekday() to conform with list ordering
    :return:
    """
    return date.isoweekday(date.today()) if date.isoweekday(date.today()) != 7 else 0


if __name__ == "__main__":
    # Create logging object
    log = logging.Logger(LOG_PATH, DEBUG_LVL)

    # Parse config file
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    config = config['DEFAULT']

    # Create watchdog to send schedule whenever altered
    observer = Observer()
    observer.schedule(DatabaseWatcher(), path.split(config['DATABASE'])[0], recursive=False)
    observer.start()

    # Initialize the mqtt client
    MQTTC = initialize_client()

    while True:
        time.sleep(1)
