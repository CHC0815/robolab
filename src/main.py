#!/usr/bin/env python3

import ev3dev.ev3 as ev3
import logging
import os
import paho.mqtt.client as mqtt
import uuid

from communication import Communication
from odometry import Odometry
from planet import Direction, Planet

from controlls.Robot import Robot

import Sound
import time

client = None  # DO NOT EDIT


def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client

    client_id = '212-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
    client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                         clean_session=True,  # We want a clean session after disconnect or abort/crash
                         protocol=mqtt.MQTTv311  # Define MQTT protocol version
                         )
    log_file = os.path.realpath(__file__) + '/../../logs/project.log'
    logging.basicConfig(filename=log_file,  # Define log file
                        level=logging.DEBUG,  # Define default mode
                        format='%(asctime)s: %(message)s'  # Define default logging format
                        )
    logger = logging.getLogger('RoboLab')

    # THE EXECUTION OF ALL CODE SHALL BE STARTED FROM WITHIN THIS FUNCTION.
    # ADD YOUR OWN IMPLEMENTATION HEREAFTER.

    print("Hello World!")

    logger.debug('-----------------------------------------------------')
    logger.debug("run motorcontrol in main")

    
    #ev3.Sound.set_volume(100)
    #Sound.play_startup()
    #time.sleep(4)
    r = Robot()
    r.run()


    while True:
        pass

# DO NOT EDIT
if __name__ == '__main__':
    run()
