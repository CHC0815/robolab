#!/usr/bin/env python3

import unittest.mock
import time
import paho.mqtt.client as mqtt
import uuid
import Communication
import config


class TestRoboLabCommunication(unittest.TestCase):
    @unittest.mock.patch('logging.Logger')
    def setUp(self, mock_logger):
        """
        Instantiates the communication class
        """
        client_id = str(config.general.group_id) + '-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
        client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                             clean_session=False,  # We want to be remembered
                             protocol=mqtt.MQTTv311  # Define MQTT protocol version
                             )

        # Initialize your data structure here
        self.communication = Communication(client, mock_logger)

        self.start = [5,8,0]
        self.end = [2,1,90]
        self.blocked = 'false'

    def test_message_ready(self):
        """
        This test should check the syntax of the message type "ready"
        """
        print("start ready message test")

        self.communication.send_ready()

        time.sleep(2)

        self.assertEqual(self.communication._debug_message, "Correct")
        self.communication._debug_message = "Incorrect"
        

    def test_message_path(self):
        """
        This test should check the syntax of the message type "path"
        """
        print("start path message test")

        self.communication.send_ready()

        self.communication.sendPath(self.start, self.end, self.blocked)

        time.sleep(2)

        self.assertEqual(self.communication._debug_message, "Correct")
        self.communication._debug_message = "Incorrect"


    def test_message_path_invalid(self):
        """
        This test should check the syntax of the message type "path" with errors/invalid data
        """
        print("start path invalid test")

        self.communication.send_ready()

        time.sleep(2)

        self.assertEqual(self.communication._is_input_invalid, True)

    def test_message_select(self):
        """
        This test should check the syntax of the message type "pathSelect"
        """
        print("start message path select test")

        start = [6,7,270]
        self.communication.send_ready()

        self.communication.sendPathSelect(start)

        time.sleep(2)

        self.assertEqual(self.communication._debug_message, "Correct")
        self.communication._debug_message = "Incorrect"


    def test_message_complete(self):
        """
        This test should check the syntax of the message type "explorationCompleted" or "targetReached"
        """
        print("start exploration and target reached message test")

        self.communication.send_ready()

        self.communication.send_exploration_completed()

        time.sleep(2)

        self.assertEqual(self.communication._debug_message, "Correct")
        self.communication._debug_message = "Incorrect"

        self.communication.send_target_completed()

        time.sleep(2)

        self.assertEqual(self.communication._debug_message, "Correct")


if __name__ == "__main__":
    unittest.main()
