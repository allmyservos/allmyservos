#!/usr/bin/env python
from __future__ import division
import signal, socket, time, string, sys, getopt, math, threading, smbus, select, os, struct, logging, subprocess
from __bootstrap import AmsEnvironment
from math import *
from numpy import array, dot
from array import *
from datetime import datetime

logpath = os.path.join(AmsEnvironment.FilePath(), 'imu')
if (not os.path.exists(logpath)):
	os.makedirs(logpath)

LOG_FILENAME = os.path.join(logpath,'logging.out')
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)
logging.disable(logging.CRITICAL)
############################################################################################
#
#  Adafruit i2c interface plus bug fix
#
############################################################################################
class I2C:
	@staticmethod
	def getPiRevision():
		"Gets the version number of the Raspberry Pi board"
		# Courtesy quick2wire-python-api
		# https://github.com/quick2wire/quick2wire-python-api
		try:
			with open('/proc/cpuinfo','r') as f:
				for line in f:
					if line.startswith('Revision'):
						if any(x in line for x in ['a01041', 'a21041', '900092', 'a02082', 'a22082']):
							return 2
						return 1 if line.rstrip()[-1] in ['1','2'] else 2
		except:
			return 0

	@staticmethod
	def getPiI2CBusNumber():
		# Gets the I2C bus number /dev/i2c#
		return 1 if I2C.getPiRevision() > 1 else 0
		
	def __init__(self, address, bus=None):
		self.address = address
		if(bus != None):
			self.bus = bus
		else:
			self.bus = smbus.SMBus(I2C.getPiI2CBusNumber())
	def reverseByteOrder(self, data):
		"Reverses the byte order of an int (16-bit) or long (32-bit) value"
		# Courtesy Vishal Sapre
		dstr = hex(data)[2:].replace('L','')
		byteCount = len(dstr[::2])
		val = 0
		for i, n in enumerate(range(byteCount)):
			d = data & 0xFF
			val |= (d << (8 * (byteCount - i - 1)))
			data >>= 8
		return val

	def write8(self, reg, value):
		"Writes an 8-bit value to the specified register/address"
		while True:
			try:
				self.bus.write_byte_data(self.address, reg, value)
				logging.debug('I2C: Wrote 0x%02X to register 0x%02X', value, reg)
				break
			except IOError, err:
				logging.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
				time.sleep(0.001)

	def writeList(self, reg, list):
		"Writes an array of bytes using I2C format"
		while True:
			try:
				self.bus.write_i2c_block_data(self.address, reg, list)
				break
			except IOError, err:
				logging.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
				time.sleep(0.001)

	def readU8(self, reg):
		"Read an unsigned byte from the I2C device"
		while True:
			try:
				result = self.bus.read_byte_data(self.address, reg)
				logging.debug('I2C: Device 0x%02X returned 0x%02X from reg 0x%02X', self.address, result & 0xFF, reg)
				return result
			except IOError, err:
				logging.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
				time.sleep(0.001)

	def readS8(self, reg):
		"Reads a signed byte from the I2C device"
		while True:
			try:
				result = self.bus.read_byte_data(self.address, reg)
				logging.debug('I2C: Device 0x%02X returned 0x%02X from reg 0x%02X', self.address, result & 0xFF, reg)
				if (result > 127):
					return result - 256
				else:
					return result
			except IOError, err:
				logging.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
				time.sleep(0.001)

	def readU16(self, reg):
		"Reads an unsigned 16-bit value from the I2C device"
		while True:
			try:
				hibyte = self.bus.read_byte_data(self.address, reg)
				result = (hibyte << 8) + self.bus.read_byte_data(self.address, reg+1)
				logging.debug('I2C: Device 0x%02X returned 0x%04X from reg 0x%02X', self.address, result & 0xFFFF, reg)
				if result == 0x7FFF or result == 0x8000:
					logging.critical('I2C read max value')
					time.sleep(0.001)
				else:
					return result
			except IOError, err:
				logging.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
				time.sleep(0.001)

	def readS16(self, reg):
		"Reads a signed 16-bit value from the I2C device"
		while True:
			try:
				hibyte = self.bus.read_byte_data(self.address, reg)
				if (hibyte > 127):
					hibyte -= 256
				result = (hibyte << 8) + self.bus.read_byte_data(self.address, reg+1)
				logging.debug('I2C: Device 0x%02X returned 0x%04X from reg 0x%02X', self.address, result & 0xFFFF, reg)
				if result == 0x7FFF or result == 0x8000:
					logging.critical('I2C read max value')
					time.sleep(0.001)
				else:
					return result
			except IOError, err:
				logging.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
				time.sleep(0.001)
				
	def readList(self, reg, length):
		"Reads a a byte array value from the I2C device"
		while True:
			try:
				result = self.bus.read_i2c_block_data(self.address, reg, length)
				logging.debug('I2C: Device 0x%02X from reg 0x%02X', self.address, reg)
				return result
			except IOError, err:
				logging.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
				time.sleep(0.001)



############################################################################################
#
#  Gyroscope / Accelerometer class for reading position / movement
#
############################################################################################
class MPU6050 :
	i2c = None

	# Registers/etc.
	__MPU6050_RA_XG_OFFS_TC= 0x00       # [7] PWR_MODE, [6:1] XG_OFFS_TC, [0] OTP_BNK_VLD
	__MPU6050_RA_YG_OFFS_TC= 0x01       # [7] PWR_MODE, [6:1] YG_OFFS_TC, [0] OTP_BNK_VLD
	__MPU6050_RA_ZG_OFFS_TC= 0x02       # [7] PWR_MODE, [6:1] ZG_OFFS_TC, [0] OTP_BNK_VLD
	__MPU6050_RA_X_FINE_GAIN= 0x03      # [7:0] X_FINE_GAIN
	__MPU6050_RA_Y_FINE_GAIN= 0x04      # [7:0] Y_FINE_GAIN
	__MPU6050_RA_Z_FINE_GAIN= 0x05      # [7:0] Z_FINE_GAIN
	__MPU6050_RA_XA_OFFS_H= 0x06	# [15:0] XA_OFFS
	__MPU6050_RA_XA_OFFS_L_TC= 0x07
	__MPU6050_RA_YA_OFFS_H= 0x08	# [15:0] YA_OFFS
	__MPU6050_RA_YA_OFFS_L_TC= 0x09
	__MPU6050_RA_ZA_OFFS_H= 0x0A	# [15:0] ZA_OFFS
	__MPU6050_RA_ZA_OFFS_L_TC= 0x0B
	__MPU6050_RA_XG_OFFS_USRH= 0x13     # [15:0] XG_OFFS_USR
	__MPU6050_RA_XG_OFFS_USRL= 0x14
	__MPU6050_RA_YG_OFFS_USRH= 0x15     # [15:0] YG_OFFS_USR
	__MPU6050_RA_YG_OFFS_USRL= 0x16
	__MPU6050_RA_ZG_OFFS_USRH= 0x17     # [15:0] ZG_OFFS_USR
	__MPU6050_RA_ZG_OFFS_USRL= 0x18
	__MPU6050_RA_SMPLRT_DIV= 0x19
	__MPU6050_RA_CONFIG= 0x1A
	__MPU6050_RA_GYRO_CONFIG= 0x1B
	__MPU6050_RA_ACCEL_CONFIG= 0x1C
	__MPU6050_RA_FF_THR= 0x1D
	__MPU6050_RA_FF_DUR= 0x1E
	__MPU6050_RA_MOT_THR= 0x1F
	__MPU6050_RA_MOT_DUR= 0x20
	__MPU6050_RA_ZRMOT_THR= 0x21
	__MPU6050_RA_ZRMOT_DUR= 0x22
	__MPU6050_RA_FIFO_EN= 0x23
	__MPU6050_RA_I2C_MST_CTRL= 0x24
	__MPU6050_RA_I2C_SLV0_ADDR= 0x25
	__MPU6050_RA_I2C_SLV0_REG= 0x26
	__MPU6050_RA_I2C_SLV0_CTRL= 0x27
	__MPU6050_RA_I2C_SLV1_ADDR= 0x28
	__MPU6050_RA_I2C_SLV1_REG= 0x29
	__MPU6050_RA_I2C_SLV1_CTRL= 0x2A
	__MPU6050_RA_I2C_SLV2_ADDR= 0x2B
	__MPU6050_RA_I2C_SLV2_REG= 0x2C
	__MPU6050_RA_I2C_SLV2_CTRL= 0x2D
	__MPU6050_RA_I2C_SLV3_ADDR= 0x2E
	__MPU6050_RA_I2C_SLV3_REG= 0x2F
	__MPU6050_RA_I2C_SLV3_CTRL= 0x30
	__MPU6050_RA_I2C_SLV4_ADDR= 0x31
	__MPU6050_RA_I2C_SLV4_REG= 0x32
	__MPU6050_RA_I2C_SLV4_DO= 0x33
	__MPU6050_RA_I2C_SLV4_CTRL= 0x34
	__MPU6050_RA_I2C_SLV4_DI= 0x35
	__MPU6050_RA_I2C_MST_STATUS= 0x36
	__MPU6050_RA_INT_PIN_CFG= 0x37
	__MPU6050_RA_INT_ENABLE= 0x38
	__MPU6050_RA_DMP_INT_STATUS= 0x39
	__MPU6050_RA_INT_STATUS= 0x3A
	__MPU6050_RA_ACCEL_XOUT_H= 0x3B
	__MPU6050_RA_ACCEL_XOUT_L= 0x3C
	__MPU6050_RA_ACCEL_YOUT_H= 0x3D
	__MPU6050_RA_ACCEL_YOUT_L= 0x3E
	__MPU6050_RA_ACCEL_ZOUT_H= 0x3F
	__MPU6050_RA_ACCEL_ZOUT_L= 0x40
	__MPU6050_RA_TEMP_OUT_H= 0x41
	__MPU6050_RA_TEMP_OUT_L= 0x42
	__MPU6050_RA_GYRO_XOUT_H= 0x43
	__MPU6050_RA_GYRO_XOUT_L= 0x44
	__MPU6050_RA_GYRO_YOUT_H= 0x45
	__MPU6050_RA_GYRO_YOUT_L= 0x46
	__MPU6050_RA_GYRO_ZOUT_H= 0x47
	__MPU6050_RA_GYRO_ZOUT_L= 0x48
	__MPU6050_RA_EXT_SENS_DATA_00= 0x49
	__MPU6050_RA_EXT_SENS_DATA_01= 0x4A
	__MPU6050_RA_EXT_SENS_DATA_02= 0x4B
	__MPU6050_RA_EXT_SENS_DATA_03= 0x4C
	__MPU6050_RA_EXT_SENS_DATA_04= 0x4D
	__MPU6050_RA_EXT_SENS_DATA_05= 0x4E
	__MPU6050_RA_EXT_SENS_DATA_06= 0x4F
	__MPU6050_RA_EXT_SENS_DATA_07= 0x50
	__MPU6050_RA_EXT_SENS_DATA_08= 0x51
	__MPU6050_RA_EXT_SENS_DATA_09= 0x52
	__MPU6050_RA_EXT_SENS_DATA_10= 0x53
	__MPU6050_RA_EXT_SENS_DATA_11= 0x54
	__MPU6050_RA_EXT_SENS_DATA_12= 0x55
	__MPU6050_RA_EXT_SENS_DATA_13= 0x56
	__MPU6050_RA_EXT_SENS_DATA_14= 0x57
	__MPU6050_RA_EXT_SENS_DATA_15= 0x58
	__MPU6050_RA_EXT_SENS_DATA_16= 0x59
	__MPU6050_RA_EXT_SENS_DATA_17= 0x5A
	__MPU6050_RA_EXT_SENS_DATA_18= 0x5B
	__MPU6050_RA_EXT_SENS_DATA_19= 0x5C
	__MPU6050_RA_EXT_SENS_DATA_20= 0x5D
	__MPU6050_RA_EXT_SENS_DATA_21= 0x5E
	__MPU6050_RA_EXT_SENS_DATA_22= 0x5F
	__MPU6050_RA_EXT_SENS_DATA_23= 0x60
	__MPU6050_RA_MOT_DETECT_STATUS= 0x61
	__MPU6050_RA_I2C_SLV0_DO= 0x63
	__MPU6050_RA_I2C_SLV1_DO= 0x64
	__MPU6050_RA_I2C_SLV2_DO= 0x65
	__MPU6050_RA_I2C_SLV3_DO= 0x66
	__MPU6050_RA_I2C_MST_DELAY_CTRL= 0x67
	__MPU6050_RA_SIGNAL_PATH_RESET= 0x68
	__MPU6050_RA_MOT_DETECT_CTRL= 0x69
	__MPU6050_RA_USER_CTRL= 0x6A
	__MPU6050_RA_PWR_MGMT_1= 0x6B
	__MPU6050_RA_PWR_MGMT_2= 0x6C
	__MPU6050_RA_BANK_SEL= 0x6D
	__MPU6050_RA_MEM_START_ADDR= 0x6E
	__MPU6050_RA_MEM_R_W= 0x6F
	__MPU6050_RA_DMP_CFG_1= 0x70
	__MPU6050_RA_DMP_CFG_2= 0x71
	__MPU6050_RA_FIFO_COUNTH= 0x72
	__MPU6050_RA_FIFO_COUNTL= 0x73
	__MPU6050_RA_FIFO_R_W= 0x74
	__MPU6050_RA_WHO_AM_I= 0x75

	__CALIBRATION_ITERATIONS = 100
	
	__ACC_UNIT = 4.0 / float(65536 * __CALIBRATION_ITERATIONS) #stores the accelerometer unit for scaling
	__GYRO_UNIT = 1000.0 / float(65536 * __CALIBRATION_ITERATIONS) #stores the gyro unit for scaling

	def __init__(self, address=0x68):
		self.i2c = I2C(address)
		self.address = address
		self.ax_offset = 0
		self.ay_offset = 0
		self.az_offset = 0
		self.gx_offset = 0
		self.gy_offset = 0
		self.gz_offset = 0
		self.sensor_data = array('B', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
		self.result_array = array('h', [0, 0, 0, 0, 0, 0, 0])

		logging.info('Reseting MPU-6050')

		#---------------------------------------------------------------------------
		# Reset all registers
		#---------------------------------------------------------------------------
		logging.debug('Reset all registers')
		self.i2c.write8(self.__MPU6050_RA_CONFIG, 0x80)
		time.sleep(0.5)
	
		#---------------------------------------------------------------------------
		# ********************************: Experimental :**************************
		# Sets sample rate to 1000/1+4 = 200Hz
		#---------------------------------------------------------------------------
		logging.debug('Sample rate 200Hz')
		self.i2c.write8(self.__MPU6050_RA_SMPLRT_DIV, 0x04)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Sets clock source to gyro reference w/ PLL
		#---------------------------------------------------------------------------
		logging.debug('Clock gyro PLL')
		self.i2c.write8(self.__MPU6050_RA_PWR_MGMT_1, 0x02)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Controls frequency of wakeups in accel low power mode plus the sensor standby modes
		#---------------------------------------------------------------------------
		logging.debug('Disable low-power')
		self.i2c.write8(self.__MPU6050_RA_PWR_MGMT_2, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# ********************************: Experimental :**************************
		# Disable gyro self tests, scale of +/- 500 degrees/s
		#---------------------------------------------------------------------------
		logging.debug('Gyro +/-500 degrees/s')
		self.i2c.write8(self.__MPU6050_RA_GYRO_CONFIG, 0x08)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# ********************************: Experimental :**************************
		# Disable accel self tests, scale of +/-2g
		#---------------------------------------------------------------------------
		logging.debug('Accel +/- 2g')
		self.i2c.write8(self.__MPU6050_RA_ACCEL_CONFIG, 0x00)
		time.sleep(0.005)

		#---------------------------------------------------------------------------
		# Setup INT pin to latch and AUX I2C pass through
		#---------------------------------------------------------------------------
		logging.debug('Enable interrupt')
		self.i2c.write8(self.__MPU6050_RA_INT_PIN_CFG, 0x20)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# ********************************: Experimental :**************************
		# Enable data ready interrupt
		#---------------------------------------------------------------------------
		logging.debug('Interrupt data ready')
		self.i2c.write8(self.__MPU6050_RA_INT_ENABLE, 0x01)
		time.sleep(0.005)

		#---------------------------------------------------------------------------
		# ********************************: Experimental :**************************
		# Disable FSync, 5Hz DLPF => 1kHz sample frequency used above divided by the
		# sample divide factor.
		#---------------------------------------------------------------------------
		logging.debug('5Hz DLPF')
		self.i2c.write8(self.__MPU6050_RA_CONFIG, 0x06)   # 0x05 => 10Hz DLPF
		time.sleep(0.005)
	
		logging.debug('Gumph hereafter...')
	
		#---------------------------------------------------------------------------
		# Freefall threshold of |0mg|
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_FF_THR, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Freefall duration limit of 0
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_FF_DUR, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Motion threshold of 0mg
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_MOT_THR, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Motion duration of 0s
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_MOT_DUR, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Zero motion threshold
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_ZRMOT_THR, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Zero motion duration threshold
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_ZRMOT_DUR, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Disable sensor output to FIFO buffer
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_FIFO_EN, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# AUX I2C setup
		# Sets AUX I2C to single master control, plus other config
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_I2C_MST_CTRL, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Setup AUX I2C slaves
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV0_ADDR, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV0_REG, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV0_CTRL, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV1_ADDR, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV1_REG, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV1_CTRL, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV2_ADDR, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV2_REG, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV2_CTRL, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV3_ADDR, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV3_REG, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV3_CTRL, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV4_ADDR, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV4_REG, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV4_DO, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV4_CTRL, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV4_DI, 0x00)
	
		#---------------------------------------------------------------------------
		# Slave out, dont care
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV0_DO, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV1_DO, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV2_DO, 0x00)
		self.i2c.write8(self.__MPU6050_RA_I2C_SLV3_DO, 0x00)
	
		#---------------------------------------------------------------------------
		# More slave config
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_I2C_MST_DELAY_CTRL, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Reset sensor signal paths
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_SIGNAL_PATH_RESET, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Motion detection control
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_MOT_DETECT_CTRL, 0x00)
		time.sleep(0.005)
	
		#--------------------------------------------------------------------------
		# Disables FIFO, AUX I2C, FIFO and I2C reset bits to 0
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_USER_CTRL, 0x00)
		time.sleep(0.005)
	
		#---------------------------------------------------------------------------
		# Data transfer to and from the FIFO buffer
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_FIFO_R_W, 0x00)
		time.sleep(0.005)


	def readSensorsRaw(self):
		#---------------------------------------------------------------------------
		# Clear the interrupt by reading the interrupt status register,
		#---------------------------------------------------------------------------
		self.i2c.readU8(self.__MPU6050_RA_INT_STATUS)

		#---------------------------------------------------------------------------
		# Hard loop on the data ready interrupt until it gets set high
		#---------------------------------------------------------------------------
		while not (self.i2c.readU8(self.__MPU6050_RA_INT_STATUS) == 0x01):
			time.sleep(0.001)
			continue

		#---------------------------------------------------------------------------
		# Disable the interrupt while we read the data
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_INT_ENABLE, 0x00)

		#---------------------------------------------------------------------------
		# For speed of reading, read all the sensors and parse to USHORTs after
		#---------------------------------------------------------------------------
		sensor_data = self.i2c.readList(self.__MPU6050_RA_ACCEL_XOUT_H, 14)

		for index in range(0, 14, 2):
			if (sensor_data[index] > 127):
				sensor_data[index] -= 256
			self.result_array[int(index / 2)] = (sensor_data[index] << 8) + sensor_data[index + 1]

		#---------------------------------------------------------------------------
		# Reenable the interrupt
		#---------------------------------------------------------------------------
		self.i2c.write8(self.__MPU6050_RA_INT_ENABLE, 0x01)

		return self.result_array


	def readSensors(self):
		#---------------------------------------------------------------------------
		# +/- 2g 2 * 16 bit range for the accelerometer
		# +/- 500 degrees * 16 bit range for the gyroscope
		#---------------------------------------------------------------------------
		[ax, ay, az, temp, gx, gy, gz] = self.readSensorsRaw()
		fax = float(ax * self.__CALIBRATION_ITERATIONS - self.ax_offset) * self.__ACC_UNIT
		fay = float(ay * self.__CALIBRATION_ITERATIONS - self.ay_offset) * self.__ACC_UNIT
		faz = float(az * self.__CALIBRATION_ITERATIONS - self.az_offset) * self.__ACC_UNIT
		fgx = float(gx * self.__CALIBRATION_ITERATIONS - self.gx_offset) * self.__GYRO_UNIT
		fgy = float(gy * self.__CALIBRATION_ITERATIONS - self.gy_offset) * self.__GYRO_UNIT
		fgz = float(gz * self.__CALIBRATION_ITERATIONS - self.gz_offset) * self.__GYRO_UNIT
		return fax, fay, faz, fgx, fgy, fgz
	
		
	def updateOffsets(self, file_name):
		ax_offset = 0
		ay_offset = 0
		az_offset = 0
		gx_offset = 0
		gy_offset = 0
		gz_offset = 0

		for loop_count in range(0, self.__CALIBRATION_ITERATIONS):
			[ax, ay, az, temp, gx, gy, gz] = self.readSensorsRaw()
			# ax_offset += ax
			# ay_offset += ay
			# az_offset += az
			gx_offset += gx
			gy_offset += gy
			gz_offset += gz

			time.sleep(0.05)

		self.ax_offset = ax_offset
		self.ay_offset = ay_offset
		self.az_offset = az_offset
		self.gx_offset = gx_offset
		self.gy_offset = gy_offset
		self.gz_offset = gz_offset

		#---------------------------------------------------------------------------
		# Open the offset config file
		#---------------------------------------------------------------------------
		cfg_rc = True
		try:
			with open(file_name, 'w+') as cfg_file:
				cfg_file.write('%d\n' % ax_offset)
				cfg_file.write('%d\n' % ay_offset)
				cfg_file.write('%d\n' % az_offset)
				cfg_file.write('%d\n' % gx_offset)
				cfg_file.write('%d\n' % gy_offset)
				cfg_file.write('%d\n' % gz_offset)
				cfg_file.flush()

		except IOError, err:
			logging.critical('Could not open offset config file: %s for writing', file_name)
			cfg_rc = False

		return cfg_rc


	def readOffsets(self, file_name):
		#---------------------------------------------------------------------------
		# Open the Offsets config file, and read the contents
		#---------------------------------------------------------------------------
		cfg_rc = True
		try:
			with open(file_name, 'r') as cfg_file:
				str_ax_offset = cfg_file.readline()
				str_ay_offset = cfg_file.readline()
				str_az_offset = cfg_file.readline()
				str_gx_offset = cfg_file.readline()
				str_gy_offset = cfg_file.readline()
				str_gz_offset = cfg_file.readline()

			self.ax_offset = int(str_ax_offset)
			self.ay_offset = int(str_ay_offset)
			self.az_offset = int(str_az_offset)
			self.gx_offset = int(str_gx_offset)
			self.gy_offset = int(str_gy_offset)
			self.gz_offset = int(str_gz_offset)

		except IOError, err:
			logging.critical('Could not open offset config file: %s for reading', file_name)
			cfg_rc = False

		return cfg_rc
	
	def getConfig(self):
		'''
		This method was created for AllMyServos.
		Extracts the current configuration for use outside of this object
		'''
		return { 
			'calibrationIterations': self.__CALIBRATION_ITERATIONS,
			'offsets': {
				'gx': self.gx_offset,
				'gy': self.gy_offset,
				'gz': self.gz_offset,
				},
			'gyroUnit': self.__GYRO_UNIT,
			'accUnit': self.__ACC_UNIT
			}
	def getEulerAngles(self, fax, fay, faz):
		#---------------------------------------------------------------------------
		# What's the angle in the x and y plane from horizonal?
		#---------------------------------------------------------------------------
		theta = math.atan2(fax, math.pow(math.pow(fay, 2) + math.pow(faz, 2), 0.5))
		psi = math.atan2(fay, math.pow(math.pow(fax, 2) + math.pow(faz, 2), 0.5))
		phi = math.atan2(math.pow(math.pow(fax, 2) + math.pow(fay, 2), 0.5), faz)

		theta *=  (180 / math.pi)
		psi *=  (180 / math.pi)
		phi *=  (180 / math.pi)

		return theta, psi, phi
	
	def readTemp(self):
		temp = self.i2c.readS16(self.__MPU6050_RA_TEMP_OUT_H)
		temp = (float(temp) / 340) + 36.53
		logging.debug('temp = %s oC', temp)
		return temp


#############################################################################################
# PID algorithm to take input accelerometer readings, and target accelermeter requirements, and
# as a result feedback new rotor speeds.
#############################################################################################
class PID:

	def __init__(self, p_gain, i_gain, d_gain):
		self.last_error = 0.0
		self.last_time = time.time()
		self.p_gain = p_gain
		self.i_gain = i_gain
		self.d_gain = d_gain

		self.i_error = 0.0
		self.i_err_min = 0.0
		self.i_err_max = 0.0
		if i_gain != 0.0:
			self.i_err_min = -250.0 / i_gain
			self.i_err_max = +250.0 / i_gain


	def Compute(self, input, target):

		now = time.time()
		dt = (now - self.last_time)

		#--------------------------------------------------------------------
		# Error is what the PID alogithm acts upon to derive the output
		#--------------------------------------------------------------------
		error = target - input

		#--------------------------------------------------------------------
		# The proportional term takes the distance between current input and target
		# and uses this proportially (based on Kp) to control the blade speeds
		#--------------------------------------------------------------------
		p_error = error

		#--------------------------------------------------------------------
		# The integral term sums the errors across many compute calls to allow for
		# external factors like wind speed and friction
		#--------------------------------------------------------------------
		self.i_error += (error + self.last_error) * dt
		if self.i_gain != 0.0 and self.i_error > self.i_err_max:
			self.i_error = self.i_err_max
			logging.warning('Cropped to max integral')
		elif self.i_gain != 0.0 and self.i_error < self.i_err_min:
			self.i_error = self.i_err_min
			logging.warning('Cropped to min integral')
		i_error = self.i_error

		#--------------------------------------------------------------------
		# The differential term accounts for the fact that as error approaches 0,
		# the output needs to be reduced proportionally to ensure factors such as
		# momentum do not cause overshoot.
		#--------------------------------------------------------------------
		d_error = (error - self.last_error) / dt

		#--------------------------------------------------------------------
		# The overall output is the sum of the (P)roportional, (I)ntegral and (D)iffertial terms
		#--------------------------------------------------------------------
		p_output = self.p_gain * p_error
		i_output = self.i_gain * i_error
		d_output = self.d_gain * d_error

		#--------------------------------------------------------------------
		# Store off last input (for the next differential calulation) and time for calculating the integral value
		#--------------------------------------------------------------------
		self.last_error = error
		self.last_time = now

		#--------------------------------------------------------------------
		# Return the output, which has been tuned to be the increment / decrement in blade PWM
		#--------------------------------------------------------------------
		return p_output, i_output, d_output
if __name__ == "__main__":
	try:
		g = MPU6050()
		print('gyro setup')
		while True:
			print(g.readSensors())
	except KeyboardInterrupt:
		quit()