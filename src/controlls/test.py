
# 360° = 17.2788 cm

import ev3dev.ev3 as ev3
import time

class RoboTest():
    def __init__(self):
        self.us = ev3.UltrasonicSensor()
        self.us.mode = 'US-DIST-CM'
        self.m_left = ev3.LargeMotor("outA")
        self.m_right = ev3.LargeMotor("outB")
        self.m_left.reset()
        self.m_right.reset()
        self.m_left.stop_action = "brake"
        self.m_right.stop_action = "brake"

    def test(self):
        self.move_forward(100)
        while(self.readDistance() > 10):
            pass
        self.m_right.stop()
        self.m_left.stop()
        print(self.readDistance())
        
    def readDistance(self):
        dist = self.us.distance_centimeters
        print(dist)
        #time.sleep(0.25)
        return dist

    def move_forward(self, speed):
        self.m_left.speed_sp = speed
        self.m_right.speed_sp = speed
        self.m_left.command = "run-forever"
        self.m_right.command = "run-forever"

