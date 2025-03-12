from pyb import Pin, ADC
import time

class Line_Sensor:
    
    def __init__(self, sensor:Pin, number):
        self.adc = ADC(sensor)
        self.number = number
        self.black = 0
        self.white = 0

    def read(self):
        try:
            val = (self.adc.read()-self.white)/(self.black-self.white)
            if val < 0.1:
                val = 0
            elif val > 1:
                val = 1
            return val
        except ZeroDivisionError:
            print("incorrect calibration")
    
    
    def calibrate_black(self):
        self.black = self.adc.read()
        return self.black

    def calibrate_white(self):
        self.white = self.adc.read()
        return self.white
    
    def write_b(self, cal):
        self.black = cal
        return self.black

    def write_w(self, cal):
        self.white = cal
        return self.white