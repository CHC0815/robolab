
# 360° = 17.2788 cm

import ev3dev.ev3 as ev3
import time
import logging
from controlls.PID import PID
import csv

logger = logging.getLogger('Robot')

class States():
    scanNode = 0
    followLine = 1

class Robot():
    def __init__(self):
        self.isCalibrated = True
        self.PID = PID()
        self.wheelbase = 152 # mm


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


    """
    scans a node and returns an array of booleans
    :return [bool, bool, bool, bool]
    """
    def scanNode(self):
        print('Scanning node...')
        self.rotateByDegGyro(45, False)
        is_right = self.rotateByDegGyro(90, True)
        time.sleep(0.5)
        is_bottom = self.rotateByDegGyro(90, True) # path from where the robot came, should always be true
        time.sleep(0.5)
        is_left = self.rotateByDegGyro(90, True)
        time.sleep(0.5)
        is_top = self.rotateByDegGyro(90, True)
        time.sleep(0.5)
        self.rotateByDegGyro(45, False, False)
        print('End scanning node...')
        print('Right: ' + is_right + ' bottom: ' + is_bottom + ' left: ' + is_left + ' top: ' + is_top)
        return [is_right, is_bottom, is_left, is_top]

    """
    returns the sum of the single color channels
    :return int
    """
    def readLight(self):
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
            self.lineFolower()
            self.moveCm(5)
            time.sleep(1)
            pathes  = self.scanNode()
            if(pathes[0]):
                self.rotateByDegGyro(85, False)
            elif pathes[2]:
                self.rotateByDegGyro(265, False)
            elif pathes[3]:
                self.rotateByDegGyro(5, False, False)
            else:
                # dead end - return 
                self.rotateByDegGyro(175, False)




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


    """
    Findes an offset for the color channels
    """
    def calcOffsets(self):
        r = self.white[0]
        g = self.white[1]
        b = self.white[2]

        self.r_offset = r / b
        self.g_offset = g / b
        self.b_offset = 1 

    """
    Checks whether the current color is blue
    :return bool
    """
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

    """
    Checks whether the current color is red
    :return bool
    """
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
    """
    method to follow a line
    return if it found a node
    """
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

                # limits the velocity
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
                    action = "TurnRight"
                elif powerRight > powerLeft:
                    action = "TurnLeft"
                else:
                    action = "Forward"
                
                # schreibt Werte in die Tabelle
                robot_writer.writerow([action, lightValue, powerLeft, powerRight])

                # setzt Motorparameter
                self.m_left.speed_sp = powerLeft
                self.m_right.speed_sp = powerRight
                self.m_left.command = "run-forever"
                self.m_right.command = "run-forever"


    """
    Gibt die aktuelle Entfernung des Roboters über den Ultraschallsensor zurück
    :return float
    """
    def readDistance(self):
        return self.us.distance_centimeters

    """
    Gibt die aktuellen Werte des Farbsensors zurück
    :return [int, int, int]
    """
    def readColor(self):
        return [self.cs.value(0), self.cs.value(1), self.cs.value(2)]

    """
    Eine Methode die den Roboter um einen bestimmten Winkel dreht
    :param int
    :return void
    """
    def rotateByDeg(self, angle):
        diameter = 55 #mm
        pi = 3.14159265359
        wheel_dist_per_rot = diameter * pi
        robot_dist_per_rot = self.wheelbase * pi

        
        degrees = ((robot_dist_per_rot * (angle / 360)) / wheel_dist_per_rot) * 360

        print(degrees)
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

    """
    Eine Methode die den Roboter um eine bestimmte Länge nach vorn bewegt
    :param int
    :return void
    """
    def moveCm(self, cm):
        diameter = 55 # mm
        pi = 3.14159265359
        wheel_dist_per_rot = diameter * pi / 10

        degrees = (360 / wheel_dist_per_rot) * cm

        print(degrees)
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



    def rotateByDegGyro(self, angle, check, cw = True):
        startAngle = self.gyro.value()

        self.m_left.reset()
        self.m_right.reset()

        self.m_left.stop_action = 'brake'
        self.m_right.stop_action = 'brake'

        self.m_left.speed_sp =  100 if cw else -100
        self.m_right.speed_sp = -100 if cw else 100

        self.m_left.command = 'run-forever'
        self.m_right.command = 'run-forever'

        isPath = False
        if cw:
            while (self.gyro.value() < startAngle + angle):
                #schaut ob es einen Weg gibt
                if check:
                    if self.readLight() > 200:
                        isPath = True
        else:
            while (self.gyro.value() > startAngle - angle):
                #schaut ob es einen Weg gibt
                if check:
                    if self.readLight() > 200:
                        isPath = True


        self.m_left.stop()
        self.m_right.stop()

        return isPath

