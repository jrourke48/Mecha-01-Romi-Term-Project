from pyb import Pin, Timer
from time import ticks_us, ticks_diff

class Encoder:
    #a quadrature encoder decoding interface in a python class
    # to properly define an encoder object you need three inputs: tim is tuple with three elements: the timer number,
    # the channel number for chan. A, and the channel number for CH B. 
    # ChA_pin and ChB_pin are both their respective pins
    def __init__(self, tim: tuple, chA_pin, chB_pin):
        # initializes an encoder object
        self.position =   0    # total accumulated position of the encoder
        self.prev_count = 0    # counter value from the most recent update
        self.delta =      0    # change in count btwn last two updates
        self.dt =         0    # amoutn of time btwn last two updates
        self.prev_time =  0
        self.pos_list = [0]*5
        self.t_list = [0]*5

        self.tim = Timer(tim[0], period = 0xFFFF, prescaler = 0)
        self.tim.channel(tim[1], pin=chA_pin, mode=Timer.ENC_AB)
        self.tim.channel(tim[2], pin=chB_pin, mode=Timer.ENC_AB)

    def update(self):
        # runs one update step on the encoder's timer counter to keep track of
        # the change in count and check for counter reload
        AR = 0xFFFF
        now = ticks_us()
        self.dt = ticks_diff(now, self.prev_time)
        self.prev_time = now
        cur_count = self.tim.counter()
        self.delta = cur_count - self.prev_count
        self.prev_count = cur_count
        if self.delta > (AR+1)/2:   # underflow
            self.delta = self.delta - (AR + 1)
        elif self.delta < -(AR+1)/2:
            self.delta = self.delta + (AR + 1)
        #append to the delta and t list to smooth out velocities
        self.pos_list.append(self.delta)
        self.t_list.append(self.dt)
        self.pos_list.pop(0)
        self.t_list.pop(0)
        self.position += self.delta
        
    def get_position(self):
        # returns the most recently updated value of positon as determined within
        # the update() method
        return self.position
    
    def get_velocity(self):
        # returns a measure of velocity using the most recently updated value
        # of delta as determined within the update() method
        return sum(self.pos_list)/sum(self.t_list)
   
    
    def zero(self):
        # sets the present encoder position to zero and causes future updates to
        # measure with respect to the new zero position
        self.position = 0