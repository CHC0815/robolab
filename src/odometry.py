# !/usr/bin/env python3
import math
import logging
import csv

from planet import Direction

logger = logging.getLogger('Odometry')

class Odometry:
    def __init__(self, robo):
        """
        Initializes odometry module
        """
        self.robot = robo
        self.distance_per_tick = (5.5 * math.pi) / self.robot.m_left.count_per_rot
        self.wheelbase = 15 # min(12.3) max(17.4)

        self.dataList = []

        self.rot = 0
        self.pos = [0,0]
        self.direction = Direction.NORTH


        self.firstNode = True
        self.oldNode = [1, 1]
        self.currentNode = [1, 1]
        self.fromDirection = Direction.NORTH
        self.toDirection = Direction.NORTH

    def addData(self, left, right):
        """
        adds left and right motor position to dataList
        :param int: left motor position
        :param int: right motor position
        """
        d = [left, right]
        self.dataList.append(d)

    def calc(self, color):

        # first node was set by mothership
        if self.firstNode:
            self.firstNode = False
            self.robot.comm.set_testplanet("Examinator-A-1337r")
            self.robot.comm.send_ready()
            return


        prev = self.dataList[0]
        gamma = self.rot

        delta_x = 0
        delta_y = 0

        for el in self.dataList:
            dist_left = self.motorPosToDist(prev[0], el[0])
            dist_right = self.motorPosToDist(prev[1], el[1])

            alpha = (dist_right - dist_left) / self.wheelbase
            beta = alpha / 2

            if alpha != 0:
                s = ((dist_right + dist_left) / alpha) * math.sin(beta)
            else:
                s = dist_left

            dx = math.sin(gamma + beta) * s
            dy = math.cos(gamma + beta) * s
            
            gamma -= alpha
            delta_x += dx
            delta_y += dy

            prev = el

        self.pos[0] += delta_x
        self.pos[1] += delta_y
        self.dataList.clear()
        self.rot += gamma
        self.rot = self.normAngleRad(self.rot)
        self.rot = self.roundRotation()

        self.direction = self.angleToDirection(self.rot)
        self.pos[0], self.pos[1] = self.roundPos()

        x, y = self.getNodeCoord()
        self.currentNode = [x, y]

        # send path to mothership
        e = self.currentNode.copy()
        self.toDirection = self.oppositeDirection(self.direction)
        endNode = [e[0], e[1], self.toDirection]
        
        s = self.oldNode.copy()
        startNode = [s[0], s[1], self.fromDirection]

        logger.debug('Start Node: ')
        logger.debug(startNode)

        logger.debug('End Node: ')
        logger.debug(endNode)

        self.robot.comm.sendPath(startNode, endNode, "free")
        self.oldNode = self.currentNode


    def radToDeg(self, rad):
        """
        converts an angle from radians to degrees
        :param float: angle (rad)
        :return float: angle (deg)
        """
        deg = math.degrees(rad)
        return deg

    def degToRad(self, deg):
        """
        converts an angle from degrees to radians
        :param float: angle (deg)
        :return float: angle(rad)
        """
        rad = math.radians(deg)
        return rad

    def addOffset(self, offset):
        """
        adds an offset to the current view
        :param float: angle in degrees
        """
        self.rot += self.degToRad(offset)
        self.rot = self.normAngleRad(self.rot)
        print(self.direction)
        self.direction = self.angleToDirection(self.rot)
        print(self.direction)

    def normAngleRad(self, angle):
        """
        normalizes an angle (-pi/pi)
        :param float: angle
        :return void
        """
        #while(angle <= -math.pi):
        #    angle += 2 * math.pi
        #while(angle > math.pi):
        #    angle -= 2 * math.pi
        angle = angle % (2*math.pi)
        return angle

    def normAngleDeg(self, angle):
        """
        normalizes an angle(-180/180)
        :param float: angle
        :return void
        """
        #while(angle <= -180):
        #    angle += 360
        #while(angle > 180):
        #    angle -= 360
        angle = angle % 360
        return angle

    def currentDirection(self):
        """
        returns the current direction
        :return Direction
        """
        return self.angleToDirection(self.rot)

    def angleToDirection(self, angle):
        """
        returns a directions from an angle
        :param float: angle
        :return Direction
        """
        # angle = self.normAngleRad(angle)
        angle += (2*math.pi) # positive
        angle = angle % (2*math.pi)

        if angle <= (math.pi * 1/4) or angle > (math.pi * 7/4):
            return Direction.NORTH
        elif angle >= (math.pi * 1/4) and angle < (math.pi * 3/4):
            return Direction.EAST
        elif angle >= (math.pi * 3/4) and angle < (math.pi * 5/4):
            return Direction.SOUTH
        elif angle >= (math.pi * 5/4) and angle < (math.pi * 7/4):
            return Direction.WEST 

    def directionToAngle(self, dir: Direction):
        if dir == Direction.NORTH:
            return 0
        elif dir == Direction.EAST:
            return 90
        elif dir == Direction.SOUTH:
            return 180
        elif dir == Direction.WEST:
            return 270

    def motorPosToDist(self, start, end):
        """
        converts two motor positions to a distance
        :param int: start
        :param int: end
        :return float: distance
        """
        dist = (end-start) * self.distance_per_tick
        return dist

    def roundPos(self):
        """
        rounds the current position to n*50
        :return int, int
        """
        return (round(self.pos[0]/50) * 50), (round(self.pos[1]/50) * 50)
    
    def getNodeCoord(self):
        """
        returns the current position in node coordinates
        return int, int
        """
        posX, posY = self.roundPos()
        return (posX//50), (posY//50)

    def roundRotation(self):
        """
        rounds the current rotation
        :return float
        """
        deg = self.radToDeg(self.rot)
        deg = round(deg / 90) * 90
        return self.degToRad(deg)

    def updateRobo(self, posX, posY, direction):
        self.pos[0] = posX * 50
        self.pos[1] = posY * 50
        self.direction = Direction(direction)
        if self.firstNode:
            self.oldNode = [posX, posY]
        else:
            self.direction = self.oppositeDirection(self.direction)
            self.toDirection = self.direction
            self.currentNode = [posX, posY]

        self.rot = self.degToRad(self.directionToAngle(self.direction))
        logger.debug('Updated Robo: ' + str(self.pos[0]) + '/' + str(self.pos[1]) + ' ' + str(self.direction))

    def oppositeDirection(self, dir: Direction):
        if dir == Direction.NORTH:
            return Direction.SOUTH
        elif dir == Direction.SOUTH:
            return Direction.NORTH
        elif dir == Direction.WEST:
            return Direction.EAST
        elif dir == Direction.EAST:
            return Direction.WEST