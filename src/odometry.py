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

    def addData(self, left, right, time):
        d = [left, right, time]
        self.dataList.append(d)


    def calc(self, color):

        # prev = [0, 0, self.rot]
        gamma = self.rot

        delta_x = 0
        delta_y = 0

        for el in self.dataList:
            # dist_left = self.motorPosToDist(prev[0], el[0])
            # dist_right = self.motorPosToDist(prev[1], el[1])

            cpr = self.robot.m_left.count_per_rot
            dist_left = (el[0] / cpr) * el[2] * self.distance_per_tick
            dist_right = (el[1] / cpr) * el[2] * self.distance_per_tick

            # dist_left = el[2] * el[0] * self.distance_per_tick
            # dist_right = el[2] * el[1] * self.distance_per_tick

            alpha = (dist_right - dist_left) / self.wheelbase

            
            #alpha = self.degToRad(prev[2] - el[2])
            
            beta = alpha / 2

            if alpha != 0:
                s = ((dist_right + dist_left) / alpha) + math.sin(beta)
            else:
                s = dist_left

            dx = -math.sin(gamma + beta) * s
            dy = math.cos(gamma + beta) * s
            
            gamma += alpha
            delta_x += dx
            delta_y += dy

            # prev = el

        self.pos[0] += delta_x
        self.pos[1] += delta_y
        self.dataList.clear()
        self.rot += gamma
        self.rot = self.normAngleRad(self.rot)
        self.rot = self.roundRotation()

        self.direction = self.angleToDirection(self.rot)

        self.pos[0], self.pos[1] = self.roundPos()


    def radToDeg(self, rad):
        deg = rad * 57.296
        return deg

    def degToRad(self, deg):
        return (deg / 57.296)

    def addOffset(self, offset):
        self.rot += self.degToRad(offset)

    def normAngleRad(self, angle):
        while(angle <= -math.pi):
            angle += 2 * math.pi
        while(angle > math.pi):
            angle -= 2 * math.pi
        return angle

    def angleToDirection(self, angle):
        angle = self.normAngleRad(angle)
        if angle <= math.pi * 1/4 or angle > math.pi * 7/4:
            return Direction.NORTH
        elif angle <= math.pi * 3/4 and angle > math.pi * 1/4:
            return Direction.WEST
        elif angle <= math.pi * 5/4 and angle > math.pi * 3/4:
            return Direction.SOUTH
        else:
            return Direction.EAST

    def motorPosToDist(self, start, end):
        dist = (end-start) * self.distance_per_tick
        return dist

    def roundPos(self):
        return (round(self.pos[0]/50) * 50), (round(self.pos[1]/50) * 50)
    
    def getNodeCoord(self):
        posX, posY = self.roundPos()
        return (posX//50), (posY//50)

    def roundRotation(self):
        return self.degToRad(round(self.rot / 90) * 90)

