class PID:
    def __init__(self):
        self.Kp = 1000
        self.Ki = 100
        self.Kd = 10000
        self.offset = 45 # 35
        self.Tp = 50
        self.integral = 0
        self.lastError = 0
        self.derivative = 0

    """
    Nimmt einen Helligkeitswert und gibt die Motorgeschwindigkeiten zurück 

    param: lightValue: int
    return int, int
    """
    def update(self, lightValue):
        self.error = lightValue - self.offset
        self.integral = self.integral + self.error
        self.derivative = self.error - self.lastError
        self.Turn = self.Kp * self.error + self.Ki * self.integral + self.Kd * self.derivative
        self.Turn = self.Turn / 100
        powerLeft = self.Tp + self.Turn
        powerRight = self.Tp - self.Turn
        self.lastError = self.error

        return int(powerLeft), int(powerRight)
