##from pyb import Pin, Timer
from time import ticks_diff, ticks_us, ticks_add
from array import array


class Collector:
    def __init__(self, encoder):
        # Initialize the motor, encoder, and timer
        self.encoder = encoder
        # Initialize index for data array
        self.idx = 0
        # Initialize time variable
        self.interval = 5_000 #interval in microseconds
        self.time = 0
        # Initialize data array to store (time, position, velocity)
        self.tdata = array("f", 100*[0])
        self.pdata = array("f", 100*[0])
        self.vdata = array("f", 100*[0])

    def collect_data(self):
        # Get the current time in microseconds
        start = ticks_us()
        self.encoder.update()
        self.tdata[self.idx] = self.time # set time in array
        self.pdata[self.idx] = self.encoder.get_position() #set new position and velocity
        self.vdata[self.idx] = self.encoder.get_velocity()
        # Calculate the new time
        nextrun = ticks_add(start, self.interval)
        # Update position and velocity from the encoder
        while self.idx < 100:
            now = ticks_us() #get current time
            if ticks_diff(nextrun, now) <= 0:
                self.encoder.update()
                self.time += self.interval #inc time 
                self.tdata[self.idx] = self.time # set time in array
                self.pdata[self.idx] = self.encoder.get_position() #set new position and velocity
                self.vdata[self.idx] = self.encoder.get_velocity()
                nextrun = ticks_add(nextrun, self.interval)
                self.idx += 1
            
            
    
        
    def print_data(self):
        #Prints collected data and writes each row to a CSV file
        print("Time, Position, Velocity")
            # Write each row to CSV as we print it
        for idx in range(len(self.tdata)):
            row = f"{self.tdata[idx]/1_000_000},{self.pdata[idx]/229},{self.vdata[idx]*4363}"
            print(row)
              # Save each row right after printing