# 360° = 17.2788 cm

import ev3dev.ev3 as ev3
import time
import logging
from controlls.PID import PID
from odometry import Odometry
import Sound as snd
from planet import Planet, Direction
import csv
from Communication import Communication


logger = logging.getLogger('Robot')

class Robot():
    def __init__(self, comm: Communication):
        self.isCalibrated = True
        self.PID = PID()
        self.wheelbase = 152 # mm
        self.comm = comm
        self.planet = Planet(self)

        # ultra sonic sensor
        self.us = ev3.UltrasonicSensor()
        self.us.mode = 'US-DIST-CM'
        # Gyro Sensor
        self.gyro = ev3.GyroSensor()
        self.gyro.mode = 'GYRO-CAL'
        time.sleep(0.1)
        self.gyro.mode = 'GYRO-CAL'
        time.sleep(0.1)
        self.gyro.mode = 'GYRO-ANG'
        # motor
        self.m_left = ev3.LargeMotor("outA")
        self.m_right = ev3.LargeMotor("outB")
        self.m_left.reset()
        self.m_right.reset()
        self.m_left.stop_action = "brake"
        self.m_right.stop_action = "brake"
        self.m_left.command = "run-forever"
        self.m_right.command = "run-forever"
        self.m_left.speed_sp = 0
        self.m_right.speed_sp = 0
        # color sensor
        self.cs = ev3.ColorSensor() 
        self.cs.mode = 'RGB-RAW'
        self.cs.bin_data("hhh")
        self.red = [144, 55, 17]
        self.blue = [30, 161, 115] # [235, 415, 217]
        self.white = [286, 494, 252]
        self.black = [0, 0, 0]
        self.r_offset = 0
        self.g_offset = 0
        self.b_offset = 0

        self.odometry = Odometry(self)

        self.oldNodePathes = []
        self.startDirection = 0
        self.discoveredNodes = []


    def scanNode(self):
        """
        scans a node and returns an array of booleans
        :return [bool, bool, bool, bool]
        """
        logger.debug('Scanning node...')
        self.rotateByDegGyro(45)
        is_right = self.rotateByDegGyro(90)
        is_bottom = self.rotateByDegGyro(90) # path from where the robot came, should always be true
        is_left = self.rotateByDegGyro(90)
        is_top = self.rotateByDegGyro(90)
        self.rotateByDegGyro(45, False)
        logger.debug('End scanning node...')
        logger.debug('Right: ' + str(is_right) + ' bottom: ' + str(is_bottom) + ' left: ' + str(is_left) + ' top: ' + str(is_top))
        return [is_right, is_bottom, is_left, is_top]

    def readLight(self):
        """
        returns the sum of the single color channels
        :return int
        """
        r = self.cs.value(0)
        g = self.cs.value(1)
        b = self.cs.value(2)
        val = (r + g + b) / 3
        return int(val)

    def run(self):
        self.calcOffsets()
        if not self.isCalibrated:
            self.calibrate()
            self.isCalibrated = True

        while True:
            status = self.lineFolower()

            # found node
            if status == 3 or status == 4:
                # play sound
                snd.play_node()
                time.sleep(0.2)

                # calc current position and send path to mothership
                self.odometry.calc(status)
                time.sleep(4)
                x, y = self.odometry.getNodeCoord()

                self.moveCm(6)
                time.sleep(0.5)

                if not self.isNodeAlreadyScanned(x, y):
                    pathes  = self.scanNode()
                    self.discoveredNodes.append([x, y])
                    
                    # add node and its directions to the list
                    node_pathes = []
                    if pathes[0]:
                        node_pathes.append([self.translateRotation(Direction.EAST), -2])
                    if pathes[1]:
                        node_pathes.append([self.translateRotation(Direction.SOUTH), -2])
                    if pathes[2]:
                        node_pathes.append([self.translateRotation(Direction.WEST), -2])
                    if pathes[3]:
                        node_pathes.append([self.translateRotation(Direction.NORTH), -2])            
                    node = {
                        (x, y): node_pathes
                    }
                    self.planet.add_unknown_path(node)
                else:
                    time.sleep(2)

                dir = self.planet.go_direction(x, y)
                dir = self.translateRotationToLocal(dir)

                self.rotateByDegGyro(45)
                if dir == Direction.EAST:
                    #right
                    self.rotateToLine()
                    self.rotateByDegGyro(5, False)
                    self.odometry.addOffset(90)
                    logger.debug('Right')
                elif dir == Direction.WEST:
                    # left
                    self.rotateByDegGyro(180)
                    self.rotateToLine()
                    self.rotateByDegGyro(5, False)
                    self.odometry.addOffset(270)
                    logger.debug('Left')
                elif dir == Direction.NORTH:
                    # forward
                    self.rotateByDegGyro(50, False)
                    logger.debug('Forward')
                elif dir == Direction.SOUTH:
                    # dead end - return 
                    self.rotateByDegGyro(90)
                    self.rotateToLine()
                    self.rotateByDegGyro(5, False)
                    self.odometry.addOffset(180)
                    logger.debug('Back')
                else:
                    print('Something went wrong')
                    logger.debug('Something went wrong')

                self.odometry.fromDirection = self.odometry.direction

            # found obstacle 
            elif status == 2:
                snd.play_obstacle()
                time.sleep(1)
                self.rotateByDegGyro(10)
                self.rotateToLine()
                self.odometry.addOffset(180)
                node = [self.odometry.oldNode[0], self.odometry.oldNode[1], self.odometry.fromDirection]
                node2 = [node[0], node[1], self.odometry.oppositeDirection(node[2])]
                self.comm.sendPath(node, node2, "blocked")
                time.sleep(2)



    # calibrates colors in following order: red, blue, white, black
    def calibrate(self):
        while(self.readDistance() > 5):
            pass 
        self.red = self.readColor()
        logger.debug('Red' + str(self.red))
        time.sleep(2)
        while(self.readDistance() > 5):
            pass
        self.blue = self.readColor()
        logger.debug('Blue: ' + str(self.blue))
        time.sleep(2)
        while(self.readDistance() > 5):
            pass
        self.white = self.readColor()
        logger.debug('White: ' + str(self.white))
        time.sleep(2)
        while(self.readDistance() > 5):
            pass
        self.black = self.readColor()
        logger.debug('Black:' + str(self.black))

    def calcOffsets(self):
        """
        Findes an offset for the color channels
        """
        r = self.white[0]
        g = self.white[1]
        b = self.white[2]

        self.r_offset = r / b
        self.g_offset = g / b
        self.b_offset = 1 

    def checkForBlue(self):
        """
        Checks whether the current color is blue
        :return bool
        """
        color = self.readColor()
        color[0] *= self.r_offset
        color[1] *= self.g_offset
        color[2] *= self.b_offset

        sum = color[0] + color[1] + color[2]
        blueThreshold = 0.22

        if sum == 0:
            return False

        if color[2] / sum >= blueThreshold:
            return True
        return False

    def checkForRed(self):
        """
        Checks whether the current color is red
        :return bool
        """
        color = self.readColor()
        color[0] *= self.r_offset
        color[1] *= self.g_offset
        color[2] *= self.b_offset

        sum = color[0] + color[1] + color[2]
        redThreshold = 0.45

        if sum == 0:
            return False
        if color[0] / sum >= redThreshold:
            return True
        
        return False
   
    def lineFolower(self):
        """
        method to follow a line
        return if it found a node
        :return int: status
        """

        self.m_left.reset()
        self.m_right.reset()

        self.m_left.stop_action = 'brake'
        self.m_right.stop_action = 'brake'

        self.m_left.speed_sp = 0
        self.m_right.speed_sp = 0

        while True:
            if self.readDistance() < 10:
                self.m_left.stop()
                self.m_right.stop()
                return 2

            if self.checkForBlue():
                self.m_left.stop()
                self.m_right.stop()
                return 3
            
            elif self.checkForRed():
                self.m_left.stop()
                self.m_right.stop()
                return 4
            
            lightValue = self.readLight()
            powerLeft, powerRight = self.PID.update(lightValue)
            
            # limits the velocity
            if powerLeft > 1000:
                powerLeft = 1000
            if powerRight > 1000:
                powerRight = 1000
            if powerLeft < -1000:
                powerLeft = -1000
            if powerRight < -1000:
                powerRight = -1000
            
            # setzt Motorparameter
            self.m_left.speed_sp = powerLeft
            self.m_right.speed_sp = powerRight
            self.m_left.command = "run-forever"
            self.m_right.command = "run-forever"

            self.odometry.addData(self.m_left.position, self.m_right.position)
    
    def readDistance(self):
        """, self.gyro.value()
        returns the current distance
        :return float
        """
        return self.us.distance_centimeters

    def readColor(self):
        """
        returns the current color values
        :return [int, int, int]
        """
        return [self.cs.value(0), self.cs.value(1), self.cs.value(2)]

    def rotateByDeg(self, angle):
        """
        rotates the robot by an angle
        :param int
        :return void
        """
        diameter = 55 #mm
        pi = 3.14159265359
        wheel_dist_per_rot = diameter * pi
        robot_dist_per_rot = self.wheelbase * pi

        
        degrees = ((robot_dist_per_rot * (angle / 360)) / wheel_dist_per_rot) * 360

        self.m_left.reset()
        self.m_right.reset()

        self.m_left.stop_action = 'brake'
        self.m_right.stop_action = 'brake'

        self.m_left.position_sp += int(degrees)
        self.m_right.position_sp -= int(degrees)

        self.m_left.speed_sp = 100
        self.m_right.speed_sp = 100

        self.m_left.command = 'run-to-abs-pos'
        self.m_right.command = 'run-to-abs-pos'

    def moveCm(self, cm):
        """
        moves the robot by n cm
        :param int
        :return void
        """
        diameter = 55 # mm
        pi = 3.14159265359
        wheel_dist_per_rot = diameter * pi / 10

        degrees = (360 / wheel_dist_per_rot) * cm

        self.m_left.reset()
        self.m_right.reset()

        self.m_left.stop_action = 'brake'
        self.m_right.stop_action = 'brake'

        self.m_left.position_sp += int(degrees)
        self.m_right.position_sp += int(degrees)

        self.m_left.speed_sp = 100
        self.m_right.speed_sp = 100

        self.m_left.command = 'run-to-abs-pos'
        self.m_right.command = 'run-to-abs-pos'
        time.sleep(2)

    def rotateByDegGyro(self, angle, cw = True):
        """
        rotates the robot and checks for path
        :param int: angle in degrees
        :param bool: clockwise or ccw
        :return bool
        """
        startAngle = self.gyro.value()

        self.m_left.stop()
        self.m_right.stop()

        self.m_left.reset()
        self.m_right.reset()

        self.m_left.stop_action = 'brake'
        self.m_right.stop_action = 'brake'

        speed = 150

        self.m_left.speed_sp =  speed if cw else -speed
        self.m_right.speed_sp = -speed if cw else speed

        self.m_left.command = 'run-forever'
        self.m_right.command = 'run-forever'

        isPath = False
        if cw:
            while (self.gyro.value() < startAngle + angle):
                #schaut ob es einen Weg gibt
                if self.readLight() < 200:
                    isPath = True
        else:
            while (self.gyro.value() > startAngle - angle):
                #schaut ob es einen Weg gibt
                if self.readLight() < 200:
                    isPath = True

        # self.odometry.addOffset(angle) # add odemetry offset

        self.m_left.stop()
        self.m_right.stop()

        return isPath
    
    def rotateToLine(self, cw = True):
        startAngle = self.gyro.value()

        self.m_left.stop()
        self.m_right.stop()

        self.m_left.reset()
        self.m_right.reset()

        self.m_left.stop_action = 'brake'
        self.m_right.stop_action = 'brake'

        self.m_left.speed_sp =  100 if cw else -100
        self.m_right.speed_sp = -100 if cw else 100

        self.m_left.command = 'run-forever'
        self.m_right.command = 'run-forever'

        while self.readLight() > 200:
            pass
            
        # offset = startAngle - self.gyro.value()
        # self.odometry.addOffset(offset)
        
        self.m_left.stop()
        self.m_right.stop()

    def translateRotation(self, dir: Direction):
        direction = Direction(((dir + self.odometry.direction) % 360))
        return direction

    def finished(self):
        print('==========FERTIG==========')
        snd.play_victory()
        self.comm.stopp_comm()
        quit()

    def translateRotationToLocal(self, dir: Direction):
        direction = Direction(((dir - self.odometry.direction) % 360))
        return direction

    def isNodeAlreadyScanned(self, x, y):
        
        node = [x, y]

        inList = (node in self.discoveredNodes)
        logger.debug('Current node already scanned: ' + str(inList))
        return inList

