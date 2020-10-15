# !/usr/bin/env python3
import math
import logging
import csv

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


    def addData(self, left, right, angle):
        d = [left, right, angle]
        self.dataList.append(d)


    def calc(self, color):

        prev = [0, 0, self.rot]

        gamma = 0

        for el in self.dataList:
            logger.debug(el)
            dist_left = self.motorPosToDist(prev[0], el[0])
            dist_right = self.motorPosToDist(prev[1], el[1])

            alpha = (dist_right - dist_left) / self.wheelbase

            
            #alpha = self.degToRad(prev[2] - el[2])
            
            beta = alpha / 2

            if alpha != 0:
                s = ((dist_right + dist_left) / alpha) + math.sin(beta)
            else:
                s = dist_left

            delta_x = -math.sin(self.rot + beta) * s
            delta_y = math.cos(self.rot + beta) * s
            
            gamma += alpha
            self.pos[0] += delta_x
            self.pos[1] += delta_y

            prev = el

        self.dataList.clear()
        self.rot += gamma
        self.rot = self.normAngleRad(self.rot)
        self.rot = self.roundRotation()

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