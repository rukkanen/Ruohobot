"""
IMU sensor class for Ruohobot (GY-521/MPU-6050)
Reads acceleration and gyro data via I2C.
"""
import time
try:
    from mpu6050 import mpu6050
except ImportError:
    mpu6050 = None

class IMU:
    def __init__(self, i2c_address=0x68):
        if mpu6050 is None:
            raise ImportError("mpu6050 library is required for IMU support.")
        self.sensor = mpu6050(i2c_address)

    def get_accel(self):
        return self.sensor.get_accel_data()

    def get_gyro(self):
        return self.sensor.get_gyro_data()

    def get_all(self):
        data = {}
        data.update(self.get_accel())
        data.update(self.get_gyro())
        return data

    def get_temperature(self):
        return self.sensor.get_temp()
