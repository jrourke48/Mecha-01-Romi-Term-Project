import cotask
import task_share
import cqueue
from nb_input import NB_Input
from NBINhandler import Inputhandler
from pyb import Pin, USB_VCP, UART, I2C
from Motor_Driver import Motor
from Encoder_Driver import Encoder
from Line_Sensor import Line_Sensor
from Line_Array import Line_Array
from Bump_array import Bump_array
from Nav import Nav
from Grid import Grid
from IMU_Driver import IMU
# import tasks
from Nav_task import navtask_fun
from Sensortask import sensortask_fun
from Motor_task import motortask_fun
from Usertask import usertask_fun
from Controllertask import controllertask_fun

#initialize bt pins and uart1
uart1 = UART(1, baudrate=115200, bits=8, parity=None, stop=1)
#deconfigure default pins
Pin(Pin.cpu.B6, mode=Pin.ANALOG)
Pin(Pin.cpu.B7, mode=Pin.ANALOG)
#configure selected pins to alternate function
Pin(Pin.cpu.A9, mode=Pin.ALT, alt=7)
Pin(Pin.cpu.A10, mode=Pin.ALT, alt=7)
#set repl to uart
pyb.repl_uart(uart1)

calibration_constants = [-10, -76, -27, 355, -268, 750, -2, -1, -1, 1000, 558] 
#calibration constants above: 
#[offsets:acc_x, acc_y, acc_z, mag_x, mag_y, mag_z, gyr_x, gyr_y, gyr_z radius: acc, mag]
i2c = I2C(1) #intialize our i2c controller on bus 1
i2c.init(I2C.CONTROLLER)
imu = IMU(i2c)
#set up the left and right motor and encoder objects
L_motor = Motor((8, 3, Pin.cpu.C8), Pin.cpu.C6, Pin.cpu.C9)
R_motor = Motor((2, 1, Pin.cpu.A15), Pin.cpu.C12, Pin.cpu.C10)
L_encoder = Encoder((4, 2, 1), Pin.cpu.B7, Pin.cpu.B6)
R_encoder = Encoder((3, 2, 1), Pin.cpu.B5, Pin.cpu.B4)
L_eff = task_share.Share('i', thread_protect = False, name = "L_eff") #motor effort share
R_eff = task_share.Share('i', thread_protect = False, name = "R_eff") #motor effort share
V = task_share.Share('f', thread_protect = False, name = "V") #motor effort share
NB_in = NB_Input(uart1, echo = True)  #initialize the non-blocking user input object
prompt = Inputhandler(NB_in) #helper class for nonblocking input
run = task_share.Share('B', thread_protect = False, name = "run") #done collecting flag share
e = task_share.Share('f', thread_protect = False, name = "e") #done collecting flag share
mode = task_share.Share('B', thread_protect = False, name = "mode") #done collecting flag share
bmp = task_share.Share('B', thread_protect = False, name = "bmp") #done collecting flag share
centroid = task_share.Share('f', thread_protect = False, name = "centroid") #done collecting flag share
calibrateb = task_share.Share('B', thread_protect = False, name = "calibrateb") #done collecting flag share
calibratew = task_share.Share('B', thread_protect = False, name = "calibratew") #done collecting flag share
psat = task_share.Share("f", thread_protect = False, name = "psat") #average line sensor value
i = task_share.Share("i", thread_protect = False, name = "i") #average line sensor value
CP = cqueue.FloatQueue(10)
calw = [1977, 326, 373, 312, 316, 297, 300, 317, 308, 311, 324, 3147, 1444]

# setup sensor pins
P1 = Line_Sensor(Pin.cpu.C5, 1)
P2 = Line_Sensor(Pin.cpu.A6, 2)
P3 = Line_Sensor(Pin.cpu.A7, 3)
P4 = Line_Sensor(Pin.cpu.C4, 4)
P5 = Line_Sensor(Pin.cpu.A4, 5)
P6 = Line_Sensor(Pin.cpu.A0, 6)
P7 = Line_Sensor(Pin.cpu.A1, 7)
P8 = Line_Sensor(Pin.cpu.A4, 8)
P9 = Line_Sensor(Pin.cpu.B0, 9)
P10 = Line_Sensor(Pin.cpu.C2, 10)
P11 = Line_Sensor(Pin.cpu.C1, 11)
P12 = Line_Sensor(Pin.cpu.C3, 12)
P13 = Line_Sensor(Pin.cpu.C0, 13)
# setup line Sensor array
lin_sen_array = Line_Array(Pin.cpu.B2,Pin.cpu.B15,
                           [P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12,P13])
#create bump array
bmp0 = Pin(Pin.cpu.C11, Pin.IN, Pin.PULL_UP) #establish each bump pin 
bmp1 = Pin(Pin.cpu.H0, Pin.IN, Pin.PULL_UP) #establish each bump pin 
bmp2 = Pin(Pin.cpu.H1, Pin.IN, Pin.PULL_UP) #establish each bump pin 
bmp3 = Pin(Pin.cpu.B12, Pin.IN, Pin.PULL_UP) #establish each bump pin 
bmp4 = Pin(Pin.cpu.B11, Pin.IN, Pin.PULL_UP) #establish each bump pin 
bmp5 = Pin(Pin.cpu.B14, Pin.IN, Pin.PULL_UP) #establish each bump pin 
bmp_array = Bump_array([bmp0, bmp1, bmp2, bmp3, bmp4, bmp5]) #create the bump array
 # Create tasks

navtask = cotask.Task(navtask_fun, name='navtask', priority=1, period=5, profile=True, trace=False,
                         shares=[run, e, mode, bmp, imu, R_encoder, L_encoder, psat, i])
sensortask = cotask.Task(sensortask_fun, name='Sensortask', priority=1, period=5, profile=True, trace=False,
                         shares=[run, calibrateb, calibratew, lin_sen_array, centroid, bmp, bmp_array, psat])
controllertask = cotask.Task(controllertask_fun, name='Controllertask', priority=1, period=5, profile=True, trace=False,
                         shares=[mode, centroid, V, e, L_eff, R_eff])
Lmotortask = cotask.Task(motortask_fun, name='Lmotortask', priority=1, period=5, profile=True, trace=False,
                        shares=[run, L_encoder, L_motor, L_eff])
Rmotortask = cotask.Task(motortask_fun, name='Rmotortask', priority=1, period=5, profile=True, trace=False,
                        shares=[run, R_encoder, R_motor, R_eff])
usertask = cotask.Task(usertask_fun, name='usertask', priority= 0, period=0, profile=True, trace = False,
                        shares=[prompt, run, calibrateb, calibratew, L_eff, R_eff, V]) 


def main():
    #intialize all shares
    i.put(0)
    lin_sen_array.off()
    calibrateb.put(0)
    calibratew.put(0)
    imu.NDOF_mode() #Change modes
    imu.write_cc(calibration_constants)
    print(imu.cal_stat())
    print(imu.get_yaw())
    bmp.put(0)
    mode.put(0)
    psat.put(0)
    centroid.put(7) #set centriod to center
    run.put(0) 
    L_eff.put(0) #initialize the motor effort
    R_eff.put(0)
    L_motor.disable() #disable the motors
    R_motor.disable()
    L_motor.set_eff(0) #initialize the motor effort
    R_motor.set_eff(0)
    L_encoder.zero() #zero the encoders
    R_encoder.zero()
    # Add tasks to the task list
    cotask.task_list.append(controllertask)
    cotask.task_list.append(sensortask)
    cotask.task_list.append(usertask)
    cotask.task_list.append(Lmotortask)
    cotask.task_list.append(Rmotortask)
    cotask.task_list.append(navtask)

    while True: 
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            L_motor.disable()
            R_motor.disable()
            print(controllertask.__repr__())
            print(sensortask.__repr__())
            print(Lmotortask.__repr__())
            print(Rmotortask.__repr__())
            print(usertask.__repr__())
            print(navtask.__repr__())
            print('Program terminated')
            break
        except:
            L_motor.disable()
            R_motor.disable()
            print(controllertask.__repr__())
            print(sensortask.__repr__())
            print(Lmotortask.__repr__())
            print(Rmotortask.__repr__())
            print(usertask.__repr__())
            print(navtask.__repr__())
            print('Error Occured')
            raise

if __name__ == "__main__":
     main()