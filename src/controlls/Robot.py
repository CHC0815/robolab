
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
        self.blue = [30, 161, 115] # [235, 415, 217]
        self.white = [286, 494, 252]
        self.black = [0, 0, 0]
        self.r_offset = 0
        self.g_offset = 0
        self.b_offset = 0

    def scanNode(self):
        print('Scanning node...')

    def readLight(self):
        r = self.cs.value(0)
        g = self.cs.value(1)
        b = self.cs.value(2)
        val = (r + g + b) / 3
        return val

    def run(self):
        self.calcOffsets()
        if not self.isCalibrated:
            self.calibrate()
            self.isCalibrated = True

        self.lineFolower()


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

    def calcOffsets(self):
        r = self.white[0]
        g = self.white[1]
        b = self.white[2]

        self.r_offset = r / b
        self.g_offset = g / b
        self.b_offset = 1 

    def checkForBlue(self):
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
        color = self.readColor()
        color[0] *= self.r_offset
        color[1] *= self.g_offset
        color[2] *= self.b_offset

        sum = color[0] + color[1] + color[2]
        redThreshold = 0.45

        if sum == 0:
            return False
        print(color[0] / sum)
        if color[0] / sum >= redThreshold:
            return True
        
        return False

    def lineFolower(self):
        self.m_left.speed_sp = 0
        self.m_right.speed_sp = 0

        with open('/home/robot/src/robot_data.csv', mode='w') as robot_file:
            robot_writer = csv.writer(robot_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            robot_writer.writerow(['Action', 'LightValue', 'MotorSpeedLeft', 'MotorSpeedRight'])
            while True:
                
                if self.checkForBlue() or self.checkForRed():
                    ev3.Sound.beep()
                    return

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

