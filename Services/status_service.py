#!/usr/bin/env python3
from paho import mqtt
import os
import os.path
import time

# This service checks the current status of the valve and writes the data to a file