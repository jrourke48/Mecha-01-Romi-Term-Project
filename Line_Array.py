import pyb

class Line_Array:
    def __init__(self, ctrl_e, ctrl_o, line_array):
        #input parameters
        #ctrl_e: even control pin 
        #ctrl_o: odd control pin
        #LIne Array: list of line sensor objects 
        self.ctrl_o = ctrl_o
        self.ctrl_e = ctrl_e
        self.line_array = line_array
        
    #read each channel in the array
    def read_array(self):
        array_data = []
        for sensor in self.line_array:
            array_data.append(sensor.read())
        return array_data

    #determine line array centroid
    def centroid(self):
        self.on()
        light_data = self.read_array()
        sum_xA = 0
        for i in range(len(light_data)):
            sum_xA += (i+1)*light_data[i] #determine weighted area
        self.off()
        try:
            return sum_xA/sum(light_data)
        except ZeroDivisionError:
            return 7
    
    #return an average sensor value 
    def psat(self):
        self.on()
        light_data = self.read_array() 
        self.off()
        return sum(light_data)/13

    def calibrate_black(self):
        self.on()
        dark = []
        for sensor in self.line_array:
            dark.append(sensor.calibrate_black()) 
        print(dark)      
        self.off()

    def calibrate_white(self):
        self.on()
        light = []  
        for sensor in self.line_array:
            light.append(sensor.calibrate_white())
        print(light)
        self.off()
    
    def write_calb(self):
        for sensor in self.line_array:
            sensor.write_b(4095)     

    def write_calw(self, wcal_con):
        i = 0
        for sensor in self.line_array:
            sensor.write_w(wcal_con[i])
            i +=1

    def on(self):
        self.ctrl_o.high()
        self.ctrl_e.high()

    def off(self):
        self.ctrl_o.low()
        self.ctrl_e.low()