import json
import config
import ssl
import logging
from time import sleep
from threading import Thread





#                           Communication                        #



logger = logging.getLogger('communication')


class Communication(Thread):
    """
        Communication interact with the mothership
        Runs on thread
    """



    def __init__(self, mqtt_client, test=None, robo):
        """
        Init Comm
        :param mqtt_client: paho.mqtt.client.Client
        :param test: name of testplanet
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

        self._planetName = None
        self.robo = robo


        #only when par test in comm defined
        if test is not None:
            self.set_testplanet(test)
        sleep(3)
        logger.info("Connected to server")



    # Listener
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """

        topic = message.topic
        self.payload = json.loads(message.payload.decode('utf-8'))
        print('Got message with topic "{}":'.format(message.topic))

        #explorer messages
        if topic == "explorer" + config.general.group_id:


            #testplanet message
            if self.payload['from'] == "debug" and self.payload['type'] == "notice":
                self._planetName = self.payload['payload']['planetName']


            #ready message
            elif self.payload['from'] == "server" and self.payload['type'] == "planet":
                self.client.subscribe('planet/' + self._planet + '/' +config.general.group_id, 1)

        #planet messages
        elif topic == "planet/" + self._planet + "/" + config.general.group_id:

            #path message
            if self.payload['from'] == "server" and self.payload['type'] == "path":

                _pathStatus = self.payload['payload']['pathStatus']
                if self._pathStatus == "blocked":
                    self._pathStatus = -1

                _startDirection = self.payload['payload']['startDirection']
                _endDirection = self.payload['payload']['endDirection']
                _startX = self.payload['payload']['startX']
                _startY = self.payload['payload']['startY']
                _endX = self.payload['payload']['endX']
                _endY = self.payload['payload']['endY']
                _pathWeight = self.payload['payload']['pathWeight']

                start = [[_startX, _startY], _startDirection]
                target = [[_endX, _endY], _endDirection]

                #add new path
                self.robo.planet.add_path(start, target, _pathWeight)

            #path select message
            elif self.payload['from'] == "server" and self.payload['type'] == "pathSelect":
                #set new direction
                self.robot.planet.go_direction(self.payload['payload']['startDirection'])

            #path unveiled message
            elif self.payload['from'] == "server" and self.payload['type'] == "pathUnveiled":
                self._startX = self.payload['payload']['startX']
                self._startY = self.payload['payload']['startY']
                self._startDirection = self.payload['payload']['startDirection']
                self._endX = self.payload['payload']['endX']
                self._endY = self.payload['payload']['endY']
                self._endDirection = self.payload['payload']['endDirection']
                self._pathStatus = self.payload['payload']['pathStatus']
                self._pathWeight = self.payload['payload']['pathWeight']


            #target message
            elif self.payload['from'] == "server" and self.payload['type'] == "target":
                target = [self.payload['payload']['targetX'], self.payload['payload']['targetY']]
                self.robo.planet.set_target(target)


            #complete message
            elif self.payload['from'] == "server" and self.payload['type'] == "done":
                _complete_message = self.payload['payload']['message']

                _complete_message

        elif topic == "comtest/" + config.general.group_id
            if self.payload['from'] == "debug" and self.payload['type'] == "syntax":
                _debug_message = self.payload['payload']['message']
                _errors = self.payload['payload']['error']

                logger.debug(_errors)




    def send_ready(self):
        """Send the ready message to the mothership
            return: the start coords
        """

        ready_msg = {}
        ready_msg['from'] = "client"
        ready_msg['type'] = "ready"

        self.send_message('explorer/' + config.general.group_id, ready_msg)



    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: mqtt topic String
        :param message: Object (to payload)
        :return: void
        """
        logger.debug('Send to: ' + topic)
        logger.debug(json.dumps(message, 2))

        self.client.subscribe(topic, qos=1)

        self.client.publish(topic, message, 1)

        self.client.loop_start()

        # TODO abort statement
        # while not mission_complete:


        self.client.loop_stop()



    def path(self, start, destination, blocked=False): #TODO: I need
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


    def set_testplanet(self, testplanet):
        """
        Only use for test

        :param testplanet: Test planet name
        """

        if testplanet == None:
            return

        testplanet_msg={}
        testplanet_msg['from'] = "client"
        testplanet_msg['from'] = "client"
        testplanet_msg['type'] = "testplanet"
        testplanet_msg['payload']['planetName'] = testplanet

        self.send_message('explorer/' + config.general.group_id, testplanet_msg)









