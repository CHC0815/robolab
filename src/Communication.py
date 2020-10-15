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



    def __init__(self, mqtt_client, test=None):
        """
        Init Comm
        :param mqtt_client: paho.mqtt.client.Client
        :param test: name of the testplanet
        """

        # Init Threading
        Thread.__init__(self)

        if mqtt_client is None:
            raise ValueError('Invalid mqtt client')

        # MQTT setup
        self._planet = test
        self.client = mqtt_client
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(str(config.general.group_id), password=config.mqtt.pw)

        self.client.on_message = self.safe_on_message_handler
        self.client.on_message = self.on_message

        self.client.connect(config.mqtt.domain, config.mqtt.pw)
        self.client.subscribe('explorer/212', config.mqtt.qos_level)

        sleep(3)



    # DO NOT EDIT THE METHOD SIGNATURE
    # Listener
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """

        print('Got message with topic "{}":'.format(message.topic))
        self.payload = json.loads(message.payload.decode('utf-8'))


        # DO NOT EDIT THE METHOD SIGNATURE
        #
        # In order to keep the logging working you must provide a topic string and
        # an already encoded JSON-Object as message.

    def send_ready(self):
        if not self._planet == "test":
            return

        self.client.subscribe('explorer/' + config.general.group_id, 1)

        ready_msg = {"from": "client", "type": "ready"}

        self.client.publish("explorer/" + config.general.group_id, ready_msg, 1)



    def on_ready(self):
        if not self.payload['type'] == 'planet':
            print("Falsche Nachricht")
            return

        #für Orientierung
        self._startX = self.payload['payload']['startX']
        self._startY = self.payload['payload']['startY']
        self._startOrientation = self.payload['payload']['startOrientation']
        self._planet = self.payload['payload']['planetName']

        self.client.subscribe('planet/' + self._planet + '/' +
                              config.general.group_id, 1)



    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: mqtt topic String
        :param message: Object (to payload)
        :return: void
        """
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))

        self.client.publish(topic, payload=message, qos=1)

        self.client.loop_start()

        while True:


        self.client.loop_stop()



    def set_testplanet(self, testplanet):
        """
        Indicate the name of the current testplanet to the MQTT server.
        (Should only be used during testruns).

        :param testplanet: Test planet name
        """

        if self._planet == None:
            return


        self.send_message('explorer/' + config.general.group_id,
                          'type ' + "testplanet",
                            'payload', 'planetName' + testplanet)
        self.client.subscribe('planet/' + self._planet, qos=1)



    def path(self, start, destination, blocked=False): #TODO
         #send next path and mothership will correct it

        path_msg = {
            {
                "from": "client",
                "type": "path",
                "payload": {
                    "startX": "sX",
                    "startY": "sY",
                    "startDirction": "sD",
                    "endX": "eX",
                    "endY": "eY",
                    "endDirection": "eD",
                    "pathStatus": "moin"
                }
            }
        }

        self.send_message('planet/' + self._planet + '/' +
                                 config.general.group_id, path_msg, 1)



    def send_target_reached(self, message=None):
        """
           :param message: additional message to send to the server
        """
        self.payload['payload'] = "target reached!"



        if message:
            self.payload['payload'] += " " + message

        self.send_message('planet/' + self._planet, message)



    def send_exploration_completed(self, message=None):
        """
        :param message: additional message to send to the server
        """
        payload = "exploration completed!"
        if message:
            self.payload['payload'] = " " + message



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






