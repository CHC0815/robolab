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
        self.distance_per_tick = (55 * math.pi) / 360
        self.wheelbase = 15 # min(12.3) max(17.4)

        self.dataList = []
        self.oldEl = [0, 0]

        self.position = [0, 0]
        self.rot = 0


    def addData(self, left, right):
        data = [left, right]
        self.dataList.append(data)
    

    def calc(self):
        pos = self.position

        for el in self.dataList:
            
            dist_left = self.motorPosToDist(self.oldEl[0], el[0])
            dist_right = self.motorPosToDist(self.oldEl[1], el[1])

            alpha = (dist_right / (dist_left + self.wheelbase))

            s = ((dist_right + dist_left) / alpha) * math.sin((alpha / 2 ))

            delta_x = -math.sin(self.rot + (alpha / 2)) * s
            delta_y = math.cos(self.rot + (alpha / 2)) * s

            self.rot += alpha
            pos[0] += delta_x
            pos[1] += delta_y

            self.oldEl = el

        self.position = pos
        self.dataList.clear()
        logger.debug('Odometry: Position: ' + str(self.position[0]) + '/' + str(self.position[1]))


    def motorPosToDist(self, start, end):
        return self.distance_per_tick * (end - start)



