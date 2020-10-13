import json
import config
import ssl
import logging
from time import sleep
from threading import Thread


#                           Communication                        #



logger = logging.getLogger('communication')

#TODO : comm init, Client, connect2broker, loop for network traffic, sub, publish, disc, test, messages



class Communication(Thread):
    """
        Communication interact with the mothership
        Runs on thread
    """



    def __init__(self, mqtt_client):
        """
        Init Comm
        :param mqtt_client: paho.mqtt.client.Client
        """

        # Init Threading
        Thread.__init__(self)

        if mqtt_client is None:
            raise ValueError('Invalid mqtt client')

        # MQTT setup
        self.client = mqtt_client
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(str(config.general.group_id), password=config.mqtt.pw)

        self.client.on_message = self.safe_on_message_handler
        self.client.on_message = self.on_message

        self.client.connect(config.mqtt.domain, config.mqtt.pw)
        self.client.subscribe('explorer/212', config.mqtt.qos_level)

        sleep(3)







    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """

        payload = json.loads(message.payload.decode('utf-8'))
        self.logger.debug(json.dumps(payload, indent=2))

        json.dumps(self.payload, separators=(',', ':'))









    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.
    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))

        self.client.subscribe(topic, qos=1)
        self.client.on_message = on_message or self._pass









    def set_testplanet(self, testplanet):
        """
        Indicate the name of the current testplanet to the MQTT server.
        (Should only be used during testruns).

        :param testplanet: Test planet name
        """
        self.send_message('explorer/' + Communication.GROUP_ID,
                          'testplanet ' + testplanet)









    #Some Super Cool Famous Beutiful Helper Stuff

    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"

    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise
