from pyb import I2C
import struct

class IMU:
#inertial measurment unit driver
#gives information about our orientation

    def __init__(self, I2C):
        self.addr = 0X28
        self.i2c = I2C
        self.calibcons = 0

    #set the operating mode to NDOF
    def NDOF_mode(self):
        opr_reg = 0X3D
        self.i2c.mem_write(0b00001100, self.addr, opr_reg) #set to NDOF mode

    #set the operating mode to NDOF
    def Config_mode(self):
        opr_reg = 0X3D #operation mode register 
        self.i2c.mem_write(0b00000000, self.addr, opr_reg) #set to configure mode

    #determine if the IMU is done calibrating
    def cal_stat(self) -> bool:
        stat_reg = 0X35
        cstat = self.i2c.mem_read(1, self.addr, stat_reg)[0]  # Read byte from register
        sys_cal = (cstat & 0b11000000) == 0b11000000  # System calibration (bits 7-6)
        gyro_cal = (cstat & 0b00110000) == 0b00110000  # Gyroscope calibration (bits 5-4)
        accel_cal = (cstat & 0b00001100) == 0b00001100  # Accelerometer calibration (bits 3-2)
        mag_cal = (cstat & 0b00000011) == 0b00000011  # Magnetometer calibration (bits 1-0)
        return sys_cal, gyro_cal, accel_cal, mag_cal  # Return tuple of booleans
    
    #read the calibration constants for the IMU
    def read_cc(self) -> tuple:
        #should return a tuple of length eleven where 
        #(x accelerometer offset, y accelerometer offset, z accelerometer offset, 
        # x magnetometer offset, y magnetometer offset, z magnetometer offset, x gyroscope offset, 
        # y gyroscope offset, z gyroscope offset, accelerometer radius, magnetometer radius)
        #read the calibration coefficients on the IMU
        #need 4 different metrics
        #data structure for offsets:
        #LSB then MSB for X then Y then Z 
        #acceleromter offset: 6 bytes
        #magnetometer offset: 6 bytes
        #gyroscope offset: 6 bytes
        #Lastly accelerometer and magnetometer radius
        #LSB then MSB for ACC then MAG: 4 bytes
        acc_addr = 0x55  # LSB of accelerometer offset
        data_buf = bytearray(22)  # Correct buffer size
        self.Config_mode() #set to configure mode
        self.i2c.mem_read(data_buf, self.addr, acc_addr)  # Read 22 bytes
        # Unpack 11 little-endian signed 16-bit integers
        (acco_x, acco_y, acco_z, mago_x, mago_y, mago_z, gyro_x, 
        gyro_y, gyro_z, acc_r, mag_r) = struct.unpack("<hhhhhhhhhhh", data_buf)
        self.NDOF_mode() #set back to NDOF mode
        # Return as a tuple
        return (acco_x, acco_y, acco_z, mago_x, mago_y, mago_z, gyro_x, gyro_y, gyro_z, acc_r, mag_r)
            
    #write the calibration constants for the IMU
    def write_cc(self, calibration_data):
        #should pass in a tuple of length eleven where 
        #(x accelerometer offset, y accelerometer offset, z accelerometer offset, 
        # x magnetometer offset, y magnetometer offset, z magnetometer offset, x gyroscope offset, 
        # y gyroscope offset, z gyroscope offset, accelerometer radius, magnetometer radius)
        #write these calibration coefficients to the IMU
        #need 4 different metrics
        #data structure for offsets:
        #LSB then MSB for X then Y then Z 
        #acceleromter offset: 6 bytes
        #magnetometer offset: 6 bytes
        #gyroscope offset: 6 bytes
        #Lastly accelerometer and magnetometer radius
        #LSB then MSB for ACC then MAG: 4 bytes
        self.Config_mode() #set to configure mode
        if len(calibration_data) != 11:
            raise ValueError("Expected 11 calibration values")
        acc_addr = 0X55  # first Memory address for calibration data
        # Pack data into a binary format
        data_buf = struct.pack("<hhhhhhhhhhh", *calibration_data)
        # Write data back to IMU
        self.i2c.mem_write(data_buf, self.addr, acc_addr)
        self.NDOF_mode() #set back to NDOF mode

    #get the euler angles from the IMU
    def get_euler(self):
        eul_addr = 0X1A
        data_buf = bytearray(6)
        self.i2c.mem_read(data_buf, self.addr, eul_addr)
        yaw, pitch, roll = struct.unpack("<hhh", data_buf)
        return (yaw/16, pitch/16, roll/16)
    
    #get the yaw angle from the IMU
    def get_yaw(self):
        eul_addr = 0X1A
        data_buf = bytearray(2)
        self.i2c.mem_read(data_buf, self.addr, eul_addr)
        yaw = struct.unpack("<h", data_buf)
        return (yaw[0])/16

    #get the anglur velocities from the IMU
    def get_angularvelo(self):
        ang_addr = 0X14
        data_buf = bytearray(6)
        self.i2c.mem_read(data_buf, self.addr, ang_addr)
        omx, omy, omz = struct.unpack("<hhh", data_buf)
        return (omx, omy, omz)
    
    def get_yawrate(self):
        eul_addr = 0X18
        data_buf = bytearray(2)
        self.i2c.mem_read(data_buf, self.addr, eul_addr)
        yaw_rate = struct.unpack("<h", data_buf)
        return (yaw_rate[0])/16