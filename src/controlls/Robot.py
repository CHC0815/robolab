
# 360° = 17.2788 cm

import ev3dev.ev3 as ev3
import time

from controlls.PID import PID
import csv

class States():
    scanNode = 0
    followLine = 1

class Robot():
    def __init__(self):
        self.isCalibrated = True
        self.PID = PID()
        self.wheelbase = 152 # mm

        self.state = States.followLine # TODO implement some type of state machine

        # Ultraschallsensor
        self.us = ev3.UltrasonicSensor()
        self.us.mode = 'US-DIST-CM'
        # Motoren
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
        # Farbsensor
        self.cs = ev3.ColorSensor() 
        self.cs.mode = 'RGB-RAW'
        self.cs.bin_data("hhh")
        self.red = [144, 55, 17]
        self.blue = [30, 161, 115]
        self.white = [286, 494, 252]
        self.black = [0, 0, 0]

    def scanNode(self):
        print('Scanning node...')

    def readLight(self):
        #self.cs.mode = 'COL-REFLECT'
        #return self.cs.value()
        r = self.cs.value(0)
        g = self.cs.value(1)
        b = self.cs.value(2)

        whiteOffset = -40
        max = ((self.white[0] + self.white[1] + self.white[2]) / 3) + whiteOffset
        min = (self.black[0] + self.black[1] + self.black[2]) / 3
        diff = max - min

        val = (r + g + b) / 3
        # relative range
        return ((val - min) * 100) / (diff)

    def run(self):
        #if not self.isCalibrated:
        #    self.calibrate()
        #    self.isCalibrated = True
#
        #self.lineFolower()
        #self.cs.mode = 'COL-REFLECT'
        while True:
            print(self.readLight())


    # calibrates colors in following order: red, blue, white, black
    def calibrate(self):
        while(self.readDistance() > 5):
            pass 
        self.red = self.readColor()
        print(self.red)
        time.sleep(2)
        while(self.readDistance() > 5):
            pass
        self.blue = self.readColor()
        print(self.blue)
        time.sleep(2)
        while(self.readDistance() > 5):
            pass
        self.white = self.readColor()
        print(self.white)
        time.sleep(2)
        while(self.readDistance() > 5):
            pass
        self.black = self.readColor()
        print(self.black)



    def lineFolower(self):
        self.m_left.speed_sp = 0
        self.m_right.speed_sp = 0

        with open('/home/robot/src/robot_data.csv', mode='w') as robot_file:
            robot_writer = csv.writer(robot_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            robot_writer.writerow(['Action', 'LightValue', 'MotorSpeedLeft', 'MotorSpeedRight'])
            while True:
                lightValue = self.readLight()
                powerLeft, powerRight = self.PID.update(lightValue)

                if powerLeft > 1000:
                    powerLeft = 1000
                if powerRight > 1000:
                    powerRight = 1000
                if powerLeft < -1000:
                    powerLeft = -1000
                if powerRight < -1000:
                    powerRight = -1000

                action = ""
                if powerLeft > powerRight:
                    print("turn right")
                    action = "TurnRight"
                elif powerRight > powerLeft:
                    print("turn left")
                    action = "TurnLeft"
                else:
                    print("forward")
                    action = "Forward"
                
                robot_writer.writerow([action, lightValue, powerLeft, powerRight])

                self.m_left.speed_sp = powerLeft
                self.m_right.speed_sp = powerRight
                self.m_left.command = "run-forever"
                self.m_right.command = "run-forever"

    def test(self):
        self.move_forward(100)
        while(self.readDistance() > 10):
            pass
        self.m_right.stop()
        self.m_left.stop()
        print(self.readDistance())
        
    def readDistance(self):
        dist = self.us.distance_centimeters
        #time.sleep(0.25)
        return dist

    def readColor(self):
        return [self.cs.value(0), self.cs.value(1), self.cs.value(2)]

    def move_forward(self, speed):
        self.m_left.speed_sp = speed
        self.m_right.speed_sp = speed
        self.m_left.command = "run-forever"
        self.m_right.command = "run-forever"

