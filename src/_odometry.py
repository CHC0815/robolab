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
        # distance per one degree
        self.distance_per_tick = (5.5 * math.pi) / 360
        self.wheelbase = 15 # min(12.3) max(17.4)
        # 15
        # 12.4
        # 13

        self.dataList = []
        self.oldEl = [0, 0, 0]

        self.position = [0, 0]
        self.rot = 0


    def addData(self, left, right, angle):
        data = [left, right, angle]
        self.dataList.append(data)
    

    def calc(self, color):
        with open('/home/robot/src/odometry.csv', mode='a') as odo_file:
            odo_writer = csv.writer(odo_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            odo_writer.writerow(['Alpha Rad', 'delta_x', 'delta_y', 'posX', 'posY'])

            for el in self.dataList:

                dist_left = self.motorPosToDist(self.oldEl[0], el[0])
                dist_right = self.motorPosToDist(self.oldEl[1], el[1])


                # _alpha = (dist_right - dist_left) / self.wheelbase

                alpha = self.oldEl[2] - el[2]
                alpha = self.degToRad(alpha)
                alpha = self.normAngleRad(alpha)

                if alpha != 0:
                    s = ((dist_right + dist_left) / alpha) * math.sin((alpha / 2 ))
                else:
                    s = dist_left # alpha == 0 --> dist_left == dist_right


                delta_x = math.sin(self.rot + (alpha / 2)) * s
                delta_y = math.cos(self.rot + (alpha / 2)) * s

                self.rot -= alpha
                self.rot = self.normAngleRad(self.rot)
                self.position[0] += delta_x
                self.position[1] += delta_y

                self.oldEl = el

                odo_writer.writerow([alpha, delta_x, delta_y, self.position[0], self.position[1]])

        self.oldEl = [0,0,0]
        self.dataList.clear()

        logger.debug('Position: ' + str(self.position[0]) + '/' + str(self.position[1]))
        self.position[0], self.position[1] = self.roundPos()
        logger.debug('RndPos: ' + str(self.position[0]) + '/' + str(self.position[1]))
        self.rot = self.roundRotation()
        self.rot = self.normAngleRad(self.rot)


    def roundRotation(self):
        rot = self.radToDeg(self.rot)
        rot = self.robot.gyro.value()
        return self.degToRad(round(rot / 90) * 90)

    def roundPos(self):
        return (round(self.position[0]/50) * 50), (round(self.position[1]/50) * 50)
    
    def getNodeCoord(self):
        posX, posY = self.roundPos()
        return (posX//50), (posY//50)


    def motorPosToDist(self, start, end):
        return self.distance_per_tick * (end - start)


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

