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

CONFIG_PATH = '/home/pi/indra_server/config'
LOG_PATH = '/tmp/watering_service.log'
DEBUG_LVL = logging.INFO


class DatabaseWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path == config['DATABASE']:
            send_schedule()

    def on_modified(self, event):
        if event.src_path == config['DATABASE']:
            send_schedule()


def initialize_client():
    global MQTTC
    log.info('Initializing MQTT client')
    # Init MQTT client
    MQTTC = mqtt.Client()
    MQTTC.on_connect = on_connect
    MQTTC.on_disconnect = on_disconnect
    MQTTC.tls_set(ca_certs=config['MQTT_CA_CERT'],
                  certfile=config['MQTT_CERTFILE'],
                  keyfile=config['MQTT_KEYFILE'])
    MQTTC.connect(host=config['MQTT_HOST'],
                  port=config['MQTT_PORT'],
                  keepalive=config['MQTT_KEEPALIVE'])
    MQTTC.loop_start()


def on_connect(client, userdata, flags, rc):
    log.info('Connected to AWS')


def on_disconnect(client, userdata, flags, rc):
    log.info('Disconnected from AWS')


def send_schedule():
    MQTTC.publish(config['SCHEDULE_TOPIC'],
                  payload=json.dumps({'waterings': get_waterings(), 'timestamp': time.time()}),
                  qos=2)
 

def get_waterings():
    global DEBUG
    command = 'Select day, hour, minute, duration FROM waterings ORDER BY day, hour, minute'
    db = sqlite3.connect(config['DATABASE'])
    schedule = [[] for _ in range(7)]
    for row in db.execute(command):
        schedule[row[0]].append(row[1:])
    return schedule


def get_day_num():
    return date.isoweekday(date.today()) if date.isoweekday(date.today()) != 7 else 0


if __name__ == "__main__":
    # Create logging object
    log = logging.Logger(LOG_PATH, DEBUG_LVL)

    # Parse config file
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    # Create watchdog to send schedule whenever altered
    observer = Observer()
    observer.schedule(DatabaseWatcher, path.split(config['DATABASE'])[0], recursive=False)

    # Wait for database file to be created if it does not exist yet
    while not os.path.isfile(config['DATABASE']):
        time.sleep(1)

    # Initialize the mqtt client
    initialize_client()

    while True:
        time.sleep(10)
