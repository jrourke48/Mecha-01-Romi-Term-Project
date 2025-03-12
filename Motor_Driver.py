from pyb import Pin, Timer

class Motor:
    # to properly define a motor object you need three inputs: PWM which is tuple with three elements: the timer number,
    # the channel number, and the pin number. Second DIR and nSLP are both the pins for those
    def __init__(self, PWM: tuple, DIR: Pin, nSLP: Pin):
        self.nSLP = Pin(nSLP, Pin.OUT_PP, value = 0) #establishes the sleep pin
        self.DIR = Pin(DIR, Pin.OUT_PP, value = 0)   #establishes the direction pin
        #establishes the timer and the pwm pin
        self.PWM = Timer(PWM[0], freq=20000).channel(PWM[1], pin=PWM[2], mode=Timer.PWM, pulse_width_percent=0)

    def set_eff(self, eff: int): # sets the effort based on an input -100 to 100
        try:    #ensure the input is a valid integer
            int(round(eff))
        except:
            TypeError("Effort must be an integer")
        if eff > 100:
            self.DIR.low()
            self.PWM.pulse_width_percent(100)
        elif eff < -100:
            self.DIR.high()
            self.PWM.pulse_width_percent(100)
        elif eff < 0:
            self.DIR.high()
            self.PWM.pulse_width_percent(-eff)
        else:
            self.DIR.low()
            self.PWM.pulse_width_percent(eff)

    def enable(self):
        #enables the motor to run or brake
        self.nSLP.high()
    def disable(self):
        #disables the motor, allows for coasting
        self.nSLP.low()
       