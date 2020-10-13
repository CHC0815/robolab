# !/usr/bin/env python3
import math
import logging

logger = logging.getLogger('Odometry')

class Odometry:
    def __init__(self):
        """
        Initializes odometry module
        """

        # distance per one degree
        self.distance_per_tick = (5.5 * math.pi) / 360
        self.wheelbase = 15.9 # min(12.3) max(17.4)
        # 15
        # 12.4
        # 13

        self.dataList = []
        self.oldEl = [0, 0]

        self.position = [0, 0]
        self.rot = 0


    def addData(self, left, right, angle):
        data = [left, right, angle]
        #if self.oldEl[0] == 0 and self.oldEl[1] == 0:
        #    self.oldEl = data
        #else:
        self.dataList.append(data)
    

    def calc(self):
        pos = self.position

        for el in self.dataList:
            
            dist_left = self.motorPosToDist(self.oldEl[0], el[0])
            dist_right = self.motorPosToDist(self.oldEl[1], el[1])

            # alpha = (dist_right / (dist_left + self.wheelbase))
            alpha = (dist_right - dist_left) / self.wheelbase
            alpha = alpha % 2 * math.pi
            # alpha = self.degToRad(self.oldEl[2] - el[2])

            if alpha != 0:
                s = ((dist_right + dist_left) / alpha) * math.sin((alpha / 2 ))
            else:
                s = dist_left # alpha == 0 --> dist_left == dist_right


            delta_x = -math.sin(self.rot + (alpha / 2)) * s
            delta_y = math.cos(self.rot + (alpha / 2)) * s

            self.rot -= alpha
            self.rot = self.rot % 2 * math.pi
            pos[0] += delta_x
            pos[1] += delta_y

            self.oldEl = el

        self.position = pos
        self.dataList.clear()


    def motorPosToDist(self, start, end):
        return self.distance_per_tick * (end - start)


    def radToDeg(self, rad):
        deg = (rad / math.pi) * 180
        return deg

    def degToRad(self, deg):
        return ((math.pi / 180) * deg)

    def addOffset(self, offset):
        self.rot += offset