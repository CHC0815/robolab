import json
import config
import ssl
import logging
from time import sleep
from controlls.Robot import Robot


#                           Communication                        #


logger = logging.getLogger('communication')


class Communication():
    """
        Communication interact with the mothership
        Runs on thread
    """

    def __init__(self, mqtt_client, robo: Robot, test=None):
        """
        Init Comm
        :param mqtt_client: paho.mqtt.client.Client
        :param test: name of testplanet
        :param robo: give a roboter
        """

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

        self.client.loop_start()

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
        if topic == "explorer/" + str(config.general.group_id):

            #testplanet message
            if self.payload['from'] == "debug" and self.payload['type'] == "notice":
                self._planetName = self.payload['payload']['planetName']

            #ready message
            elif self.payload['from'] == "server" and self.payload['type'] == "planet":
                self.client.subscribe('planet/' + self._planet + '/' +config.general.group_id, 1)
                # set odometry 
                _startX = int(self.payload['payload']['startX'])
                _startY = int(self.payload['payload']['startY'])
                _startDir = int(self.payload['payload']['startOrientation'])
                self.robo.odometry.updateRobo(_startX, _startY, _startDir)

        #planet messages
        elif topic == "planet/" + self._planet + "/" + str(config.general.group_id):

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
                _startX = self.payload['payload']['startX']
                _startY = self.payload['payload']['startY']
                _startDirection = self.payload['payload']['startDirection']
                _endX = self.payload['payload']['endX']
                _endY = self.payload['payload']['endY']
                _endDirection = self.payload['payload']['endDirection']
                _pathStatus = self.payload['payload']['pathStatus']
                _pathWeight = self.payload['payload']['pathWeight']
                # TODO 
            #target message
            elif self.payload['from'] == "server" and self.payload['type'] == "target":
                target = [self.payload['payload']['targetX'], self.payload['payload']['targetY']]
                self.robo.planet.set_target(target)

            #complete message
            elif self.payload['from'] == "server" and self.payload['type'] == "done":
                _complete_message = self.payload['payload']['message']

                # TODO ende

        #valid_message
        elif topic == "comtest/" + config.general.group_id + " (Invalid)":
            if self.payload['from'] == "debug" and self.payload['type'] == "syntax":
                _debug_message = self.payload['payload']['message']
                _errors = self.payload['payload']['error']
                logger.debug(_errors)

        #invalid_message
        elif topic == "comtest/" + config.general.group_id + " (Valid)":
           if  self.payload['from'] == "debug" and self.payload['type'] == "syntax":
             _message = self.payload['payload']['message']



    def send_ready(self):
        """Send the ready message to the mothership
            return: the start coords
        """

        ready_msg = {}
        ready_msg['from'] = "client"
        ready_msg['type'] = "ready"

        self.send_message('explorer/' + config.general.group_id, ready_msg)



    def sendPath(self, start, end, status):
        if status == "blocked":
            end = start

        startX = start[0]
        startY = start[1]
        endX = end[0]
        endY = end[1]
        startDirection = start[2]
        endDirection = end[2]

        path_message={}
        path_message['from'] = "client"
        path_message['type'] = "path"
        path_message['payload']['startX'] = startX
        path_message['payload']['startY'] = startY
        path_message['payload']['startDirection'] = startDirection
        path_message['payload']['endX'] = endX
        path_message['payload']['endY'] = endY
        path_message['payload']['endDirection'] = endDirection
        path_message['payload']['pathStatus'] = status

        self.send_message("planet" + self._planetName + '/', path_message)



    def sendPathSelect(self, start):

        startX = start[0]
        startY = start[1]
        startDirection = start[2]

        pathSel_message = {}
        pathSel_message['from'] = "client"
        pathSel_message['type'] = "pathSelect"
        pathSel_message['payload']['startX'] = startX
        pathSel_message['payload']['startY'] = startY
        pathSel_message['payload']['startDirection'] = startDirection

        self.send_message("planet" + self._planetName + '/', pathSel_message)



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


    def send_exploration_completed(self, message=None):
        """
        :param message: additional message to send to the server
        """

        _message = None

        if message is None:
            _message = "..."
        else:
            _message = message

        exp_message = {}
        exp_message['from'] = "client"
        exp_message['type'] = "explorationCompleted"
        exp_message['payload']['message'] = _message

        self.send_message('explorer/' + str(config.general.group_id), exp_message)


    def send_target_completed(self, message=None):
        """
        :param message: additional message to send to the server
        """

        _message = None

        if message is None:
            _message = "..."
        else:
            _message = message

        target_message = {}
        target_message['from'] = "client"
        target_message['type'] = "targetReached"
        target_message['payload']['message'] = _message

        self.send_message('explorer/' + str(config.general.group_id), target_message)



    def stopp_comm(self):
        self.client.loop_stop()



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

