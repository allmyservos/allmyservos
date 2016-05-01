#!/usr/bin/python
#######################################################################
# AllMyServos - Fun with PWM
# Copyright (C) 2015  Donate BTC:14rVTppdYQzLrqay5fp2FwP3AXvn3VSZxQ
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#######################################################################
import numpy, math, time, ctypes, os, Specification
from time import sleep,time
from lowpassfilter import lowpassfilter
from Metric import *
from Setting import *
from Scheduler import *
from MPU6050 import MPU6050, I2C
from subprocess import Popen, PIPE

class IMU(object):
	available = None
	@staticmethod
	def isAvailable():
		if (IMU.available == None):
			p = Popen(['i2cdetect', '-y', str(I2C.getPiI2CBusNumber())], stdout=PIPE)
			o = p.communicate()[0]
			available = False
			for line in o.split('\n'):
				if line.startswith('60:') and '68' in line:
					available = True
		return available
	def __init__(self, specification = None, scheduler = None, stopped = False):
		if (specification != None):
			self.specification = specification
		else:
			self.specification = Specification.Specification()
		if(scheduler != None):
			self.scheduler = scheduler
		else:
			self.scheduler = Scheduler()
		ipath = os.path.join(Specification.Specification.filebase, 'imu')
		if not os.path.exists(ipath):
			os.makedirs(ipath)
		self.filebase = os.path.join(ipath,'IMU_offset.txt')
		self.metrics = {}
		self.callbacks = {}
		self.mpi = 3.14159265359
		self.radian = 180 / self.mpi
		if (IMU.isAvailable()):
			self.device = MPU6050()
			self.__initOrientations()
			self.device.readOffsets(self.filebase)
			self.config = self.device.getConfig()
			self.initRaw()
			self.initNorm()
			self.initAngles()
			self.initLowpass()
			self.initHighpass()
			self.initComplement()
			self.inittime=time.time()
			self.tottime=0
			self.scheduler.addTask('imu_watcher', self.calculate, 0.02, stopped)
	def calibrate(self):
		self.device.updateOffsets(self.filebase)
	def initRaw(self):
		self.metrics['gyro_raw'] = IMUMetric('gyro_raw',0, Setting.get('imu_archive_gyro_raw',False))
		self.metrics['acc_raw'] = IMUMetric('acc_raw',0, Setting.get('imu_archive_acc_raw',False))
	def initNorm(self):
		self.metrics['gyro_norm'] = IMUMetric('gyro_norm',0, Setting.get('imu_archive_gyro_norm',False))
		self.metrics['acc_norm'] = IMUMetric('acc_norm',0, Setting.get('imu_archive_acc_norm',False))
	def initAngles(self):
		self.metrics['gyro_ang'] = IMUMetric('gyro_ang',0, Setting.get('imu_archive_gyro_ang',False))
		self.metrics['gyro_ang_inc'] = IMUMetric('gyro_ang_inc',0, Setting.get('imu_archive_gyro_ang_inc',False))
		self.metrics['acc_ang'] = IMUMetric('acc_ang',0, Setting.get('imu_archive_acc_ang',False))
	def initLowpass(self):
		self.lpf=lowpassfilter(0.5)
		self.metrics['lowpass'] = IMUMetric('lowpass',0, Setting.get('imu_archive_low',False))
	def initHighpass(self):
		self.metrics['highpass'] = IMUMetric('highpass',0, Setting.get('imu_archive_high',False))
	def initComplement(self):
		self.metrics['complement'] = IMUMetric('complement',0, Setting.get('imu_archive_com',False), 50)
	def addCallback(self, name, callback):
		self.callbacks[name] = callback
	def removeCallback(self, name):
		try:
			del(self.callbacks[name])
		except:
			pass
	def calculate(self):
		if(Setting.get('imu_watch_raw',True)):
			self.updateRaw()
			if(Setting.get('imu_watch_norm',True)):
				tottime_old=self.tottime
				self.tottime=time.time()-self.inittime
				self.steptime=self.tottime-tottime_old
				self.updateNorm()
				if(Setting.get('imu_watch_low',True)):
					self.updateLow()
					if(Setting.get('imu_watch_ang',True)):
						self.updateAng()
						if(Setting.get('imu_watch_com',True)):
							self.updateCom()
				if(Setting.get('imu_watch_high',False)):
					self.updateHigh()
		for v in self.callbacks.values():
			v()
	def updateRaw(self):
		try:
			data = self.device.readSensorsRaw()
			self.metrics['acc_raw'].value = { 'x':data[0], 'y':data[1], 'z':data[2] }
			self.metrics['gyro_raw'].value = { 'x':data[4], 'y':data[5], 'z':data[6] }
		except:
			pass
	def updateNorm(self):
		#data = self.device.readSensors()
		# self.metrics['acc_norm'].value = { 'x':data[0], 'y':data[1], 'z':data[2] }
		# self.metrics['gyro_norm'].value = { 'x':data[3], 'y':data[4], 'z':data[5] }
		
		self.metrics['acc_norm'].value = self.__getAccNormal()
		self.metrics['gyro_norm'].value = self.__getGyroNormal()

	def updateAng(self):
		self.metrics['acc_ang'].value = self.__getAngleAcc()
		self.metrics['gyro_ang_inc'].value = self.__getAngleGyroInc()
		self.metrics['gyro_ang'].value = self.__getAngleGyro()
	def updateCom(self):
		self.metrics['complement'].value = self.__getAngleCom()
	def updateLow(self):
		self.metrics['lowpass'].value = self.__getRawLow()
	def updateHigh(self):
		self.metrics['highpass'].value = self.__getRawHigh()
	def start(self):
		self.__initOrientations()
		self.device.readOffsets(self.filebase)
		self.config = self.device.getConfig()
		self.scheduler.startTask('imu_watcher')
	def stop(self):
		self.scheduler.stopTask('imu_watcher')
		self.__flushMetrics()
	def __flushMetrics(self):
		self.metrics['gyro_raw'].value = { 'x':0,'y':0,'z':0 }
		self.metrics['acc_raw'].value = { 'x':0,'y':0,'z':0 }
		self.metrics['gyro_ang'].value = { 'r':0,'p':0,'y':0 }
		self.metrics['acc_ang'].value = { 'r':0,'p':0,'y':0 }
		self.metrics['complement'].value = { 'r':0,'p':0,'y':0 }
		self.metrics['lowpass'].value = { 'x':0,'y':0,'z':0 }
		# del(self.tmpaang)
		# del(self.tmpgang)
		# del(self.tmpcang)
	def __getAccNormal(self):
		res = { 'x':0,'y':0,'z':0 }
		araw = self.metrics['acc_raw'].value
		if(araw != None):
			res = {
				'x': float(araw['x'] * self.config['calibrationIterations']) * self.config['accUnit'],
				'y': float(araw['y'] * self.config['calibrationIterations']) * self.config['accUnit'],
				'z': float(araw['z'] * self.config['calibrationIterations']) * self.config['accUnit']
			}
		return res
	def __getGyroNormal(self):
		res = { 'x':0,'y':0,'z':0 }
		graw = self.metrics['gyro_raw'].value
		if(graw != None):
			res = {
				'x': float(graw['x'] * self.config['calibrationIterations'] - self.config['offsets']['gx']) * self.config['gyroUnit'],
				'y': float(graw['y'] * self.config['calibrationIterations'] - self.config['offsets']['gy']) * self.config['gyroUnit'],
				'z': float(graw['z'] * self.config['calibrationIterations'] - self.config['offsets']['gz']) * self.config['gyroUnit']
			}
		return res
	def __getRawLow(self):
		x,y,z = 0,0,0
		araw = self.metrics['acc_norm'].value
		if(araw != None):
			x,y,z = self.lpf.filter(araw['x'],araw['y'],araw['z'],self.steptime)
		return { 'x' : x, 'y' : y, 'z' : z }
	def __getRawHigh(self):
		try:
			self.tmphigh
		except:
			self.tmphigh = { 'x' : 0, 'y' : 0, 'z' : 0 }
		low = self.metrics['lowpass'].value
		if(low != None):
			araw = self.metrics['acc_norm'].value
			self.tmphigh['x'] += araw['x'] - low['x']
			self.tmphigh['y'] += araw['y'] - low['y']
			self.tmphigh['z'] += araw['z'] - low['z']
		return self.tmphigh
	def __getAngleAcc(self):
		try:
			self.tmpaang
		except:
			self.tmpaang = {'r':0,'p':0,'y':0}
		low = self.__polarizeLow(self.metrics['lowpass'].value)
		if(low != None):
			o = self.orientation
			if(abs(low[o['pitchaxis']]) > 0.5): #pitch axis aligned with gravity
				self.tmpaang = {
					'r': math.atan2(low[o['yawaxis']], low[o['pitchaxis']]) * self.radian - 90,
					'p': 0, # take 0 as neither axis is aligned with gravity: math.atan2(low[o['rollaxis']], low[o['yawaxis']]) * self.radian,
					'y': math.atan2(low[o['pitchaxis']], low[o['rollaxis']]) * self.radian - 90
				}
			elif(abs(low[o['rollaxis']]) > 0.5): #roll axis aligned with gravity
				self.tmpaang = {
					'r': 0, # take 0 as neither axis is aligned with gravity: math.atan2(low[o['pitchaxis']], low[o['yawaxis']]) * self.radian,
					'p': math.atan2(-low[o['yawaxis']], low[o['rollaxis']]) * self.radian + 90,
					'y': math.atan2(low[o['pitchaxis']], abs(low[o['rollaxis']])) * self.radian
				}
			else: # yaw axis aligned with gravity or low gravity?
				self.tmpaang = {
					'r': math.atan2(-low[o['pitchaxis']], low[o['yawaxis']]) * self.radian,
					'p': math.atan2(low[o['rollaxis']], low[o['yawaxis']]) * self.radian,
					'y': 0 # take 0 as neither axis is aligned with gravity: math.atan2(low[o['pitchaxis']], low[o['rollaxis']]) * self.radian
				}
			aar, aap, arr, arp, ary = abs(self.tmpaang['r']), abs(self.tmpaang['p']), abs(low[o['rollaxis']]), abs(low[o['pitchaxis']]), abs(low[o['yawaxis']])
			if(aar + aap > 180):
				#if upside down prevent angle accumulation due to shared axis
				self.tmpaang['r'] = 180 - aar if(arp + ary < arr + ary and aar > 90) else self.tmpaang['r']
				self.tmpaang['p'] = 180 - aap if(arr + ary < arp + ary and aap > 90) else self.tmpaang['p']
		return self.__cleanAngles(self.tmpaang)
	def __getAngleGyroInc(self):
		res = {'r':0,'p':0,'y':0}
		graw = self.metrics['gyro_norm'].value
		if(graw != None):
			o = self.orientation
			res = {'r':graw[o['rollaxis']]*self.steptime,'p':graw[o['pitchaxis']]*self.steptime,'y':graw[o['yawaxis']]*self.steptime}
		return res
	def __getAngleGyro(self):
		try:
			self.tmpgang
		except:
			self.tmpgang = {'r':0,'p':0,'y':0}
		try:
			ginc = self.metrics['gyro_ang_inc'].value
			self.tmpgang['r'] = self.tmpgang['r'] + ginc['r']
			self.tmpgang['p'] = self.tmpgang['p'] + ginc['p']
			self.tmpgang['y'] = self.tmpgang['y'] + ginc['y']
		except:
			pass

		return self.__cleanAngles(self.__polarizeGyro(self.tmpgang))
	def __getAngleCom(self):
		aang = self.metrics['acc_ang'].value
		ginc = self.__polarizeGyro(self.metrics['gyro_ang_inc'].value)
		low = self.metrics['lowpass'].value
		try:
			self.tmpcang
		except:
			self.tmpcang = {'r':0,'p':0,'y':0}
			if(aang != None):
				self.tmpcang = aang #if an initial accelerometer angle is available, sync the complementary filter
		if(abs(low[self.orientation['rollaxis']]) <= 0.5):
			self.tmpcang['r'] = 0.98 * (self.tmpcang['r'] + ginc['r']) + 0.02 * aang['r'] if (self.tmpcang['r'] > 0 and aang['r'] > 0) or (self.tmpcang['r'] < 0 and aang['r'] < 0) else aang['r'] #take accelerometer roll if switching between positive/negative
		else:
			self.tmpcang['r'] += ginc['r'] #use the gyro roll if the roll axis is aligned with gravity
		if(abs(low[self.orientation['pitchaxis']]) <= 0.5):
			self.tmpcang['p'] = 0.98 * (self.tmpcang['p'] + ginc['p']) + 0.02 * aang['p'] if (self.tmpcang['p'] > 0 and aang['p'] > 0) or (self.tmpcang['p'] < 0 and aang['p'] < 0) else aang['p'] #take accelerometer pitch if switching between positive/negative
		else:
			self.tmpcang['p'] += ginc['p'] #use the gyro pitch if the pitch axis is aligned with gravity
		if(abs(low[self.orientation['yawaxis']]) <= 0.5):
			self.tmpcang['y'] = 0.98 * (self.tmpcang['y'] + ginc['y']) + 0.02 * aang['y'] if (self.tmpcang['y'] > 0 and aang['y'] > 0) or (self.tmpcang['y'] < 0 and aang['y'] < 0) else aang['y'] #take accelerometer yaw if switching between positive/negative
		else:
			self.tmpcang['y'] += ginc['y'] #use the gyro yaw if the yaw axis is aligned with gravity
		return self.__cleanAngles(self.tmpcang)
	def shutdown(self):
		for name in self.scheduler.listTasks():
			try:
				if(name.find('imu_') > -1):
					self.scheduler.stopTask(name)
			except:
				pass
	def __cleanAngles(self, rpy):
		return {
			'r': self.__cleanAngle(rpy['r']),
			'p': self.__cleanAngle(rpy['p']),
			'y': self.__cleanAngle(rpy['y'])
		}
	def __cleanAngle(self, angle):
		try:
			self.cleaned
		except:
			self.cleaned = {}
		try:
			angle = self.cleaned[angle] #free cleaning!
		except:
			old = angle
			if(angle > 180):
				angle -= 360
			if(angle < -180):
				angle += 360
			if(angle == -180):
				angle = 180
			self.cleaned[old] = angle
		return angle
	def __polarizeLow(self, xyz = { 'x':0,'y':0,'z':0 }):
		o = self.orientation
		return {
			'x': -xyz['x'] if o['polarity']['acc']['x'] else xyz['x'],
			'y': -xyz['y'] if o['polarity']['acc']['y'] else xyz['y'],
			'z': -xyz['z'] if o['polarity']['acc']['z'] else xyz['z']
		}
	def __polarizeGyro(self, rpy = {'r':0,'p':0,'y':0}):
		o = self.orientation
		return {
			'r': -rpy['r'] if o['polarity']['gyro'][o['rollaxis']] else rpy['r'],
			'p': -rpy['p'] if o['polarity']['gyro'][o['pitchaxis']] else rpy['p'],
			'y': -rpy['y'] if o['polarity']['gyro'][o['yawaxis']] else rpy['y']
		}
	def __initOrientations(self):
		try:
			self.orientations
		except:
			self.orientations = {
				'up': {
					0: { 
						'rollaxis': 'y',
						'pitchaxis': 'x',
						'yawaxis': 'z',
						'polarity': {
							'acc': {
								'x': False,
								'y': False,
								'z': False
							},
							'gyro': {
								'x': False,
								'y': False,
								'z': False
							}
						}
					},
					90: { 
						'rollaxis': 'x',
						'pitchaxis': 'y',
						'yawaxis': 'z',
						'polarity': {
							'acc': {
								'x': False,
								'y': True,
								'z': False
							},
							'gyro': {
								'x': False,
								'y': True,
								'z': False
							}
						}
					},
					180: { 
						'rollaxis': 'y',
						'pitchaxis': 'x',
						'yawaxis': 'z',
						'polarity': {
							'acc': {
								'x': True,
								'y': True,
								'z': False
							},
							'gyro': {
								'x': True,
								'y': True,
								'z': False
							}
						}
					},
					270: { 
						'rollaxis': 'x',
						'pitchaxis': 'y',
						'yawaxis': 'z',
						'polarity': {
							'acc': {
								'x': True,
								'y': False,
								'z': False
							},
							'gyro': {
								'x': True,
								'y': False,
								'z': False
							}
						}
					}
				},
				'down': {
					0: { 
						'rollaxis': 'y',
						'pitchaxis': 'x',
						'yawaxis': 'z',
						'polarity': {
							'acc': {
								'x': True,
								'y': False,
								'z': True
							},
							'gyro': {
								'x': True,
								'y': False,
								'z': True
							}
						}
					},
					90: { 
						'rollaxis': 'x',
						'pitchaxis': 'y',
						'yawaxis': 'z',
						'polarity': {
							'acc': {
								'x': True,
								'y': True,
								'z': True
							},
							'gyro': {
								'x': True,
								'y': True,
								'z': True
							}
						}
					},
					180: { 
						'rollaxis': 'y',
						'pitchaxis': 'x',
						'yawaxis': 'z',
						'polarity': {
							'acc': {
								'x': False,
								'y': True,
								'z': True
							},
							'gyro': {
								'x': False,
								'y': True,
								'z': True
							}
						}
					},
					270: { 
						'rollaxis': 'x',
						'pitchaxis': 'y',
						'yawaxis': 'z',
						'polarity': {
							'acc': {
								'x': False,
								'y': False,
								'z': True
							},
							'gyro': {
								'x': False,
								'y': False,
								'z': True
							}
						}
					}
				},
				'left': {
					0: { 
						'rollaxis': 'y',
						'pitchaxis': 'z',
						'yawaxis': 'x',
						'polarity': {
							'acc': {
								'x': True,
								'y': False,
								'z': False
							},
							'gyro': {
								'x': False,
								'y': False,
								'z': False
							}
						}
					},
					90: { 
						'rollaxis': 'x',
						'pitchaxis': 'z',
						'yawaxis': 'y',
						'polarity': {
							'acc': {
								'x': False,
								'y': False,
								'z': False
							},
							'gyro': {
								'x': False,
								'y': False,
								'z': False
							}
						}
					},
					180: { 
						'rollaxis': 'y',
						'pitchaxis': 'z',
						'yawaxis': 'x',
						'polarity': {
							'acc': {
								'x': False,
								'y': True,
								'z': False
							},
							'gyro': {
								'x': False,
								'y': True,
								'z': False
							}
						}
					},
					270: { 
						'rollaxis': 'x',
						'pitchaxis': 'z',
						'yawaxis': 'y',
						'polarity': {
							'acc': {
								'x': True,
								'y': True,
								'z': False
							},
							'gyro': {
								'x': True,
								'y': True,
								'z': False
							}
						}
					}
				},
				'right': {
					0: { 
						'rollaxis': 'y',
						'pitchaxis': 'z',
						'yawaxis': 'x',
						'polarity': {
							'acc': {
								'x': False,
								'y': False,
								'z': True
							},
							'gyro': {
								'x': False,
								'y': False,
								'z': True
							}
						}
					},
					90: { 
						'rollaxis': 'x',
						'pitchaxis': 'z',
						'yawaxis': 'y',
						'polarity': {
							'acc': {
								'x': True,
								'y': False,
								'z': True
							},
							'gyro': {
								'x': True,
								'y': False,
								'z': True
							}
						}
					},
					180: { 
						'rollaxis': 'y',
						'pitchaxis': 'z',
						'yawaxis': 'x',
						'polarity': {
							'acc': {
								'x': True,
								'y': True,
								'z': True
							},
							'gyro': {
								'x': True,
								'y': True,
								'z': True
							}
						}
					},
					270: { 
						'rollaxis': 'x',
						'pitchaxis': 'z',
						'yawaxis': 'y',
						'polarity': {
							'acc': {
								'x': False,
								'y': True,
								'z': True
							},
							'gyro': {
								'x': False,
								'y': True,
								'z': True
							}
						}
					}
				},
				'front': {
					0: { 
						'rollaxis': 'z',
						'pitchaxis': 'x',
						'yawaxis': 'y',
						'polarity': {
							'acc': {
								'x': False,
								'y': False,
								'z': True
							},
							'gyro': {
								'x': False,
								'y': False,
								'z': True
							}
						}
					},
					90: { 
						'rollaxis': 'z',
						'pitchaxis': 'y',
						'yawaxis': 'x',
						'polarity': {
							'acc': {
								'x': True,
								'y': False,
								'z': True
							},
							'gyro': {
								'x': True,
								'y': False,
								'z': False
							}
						}
					},
					180: { 
						'rollaxis': 'z',
						'pitchaxis': 'x',
						'yawaxis': 'y',
						'polarity': {
							'acc': {
								'x': True,
								'y': True,
								'z': True
							},
							'gyro': {
								'x': True,
								'y': True,
								'z': True
							}
						}
					},
					270: { 
						'rollaxis': 'z',
						'pitchaxis': 'y',
						'yawaxis': 'x',
						'polarity': {
							'acc': {
								'x': False,
								'y': True,
								'z': True
							},
							'gyro': {
								'x': False,
								'y': True,
								'z': True
							}
						}
					}
				},
				'back': {
					0: { 
						'rollaxis': 'z',
						'pitchaxis': 'x',
						'yawaxis': 'y',
						'polarity': {
							'acc': {
								'x': False,
								'y': True,
								'z': False
							},
							'gyro': {
								'x': False,
								'y': True,
								'z': False
							}
						}
					},
					90: { 
						'rollaxis': 'z',
						'pitchaxis': 'y',
						'yawaxis': 'x',
						'polarity': {
							'acc': {
								'x': True,
								'y': True,
								'z': False
							},
							'gyro': {
								'x': True,
								'y': True,
								'z': False
							}
						}
					},
					180: { 
						'rollaxis': 'z',
						'pitchaxis': 'x',
						'yawaxis': 'y',
						'polarity': {
							'acc': {
								'x': True,
								'y': False,
								'z': False
							},
							'gyro': {
								'x': True,
								'y': False,
								'z': False
							}
						}
					},
					270: { 
						'rollaxis': 'z',
						'pitchaxis': 'y',
						'yawaxis': 'x',
						'polarity': {
							'acc': {
								'x': False,
								'y': False,
								'z': False
							},
							'gyro': {
								'x': False,
								'y': False,
								'z': False
							}
						}
					}
				}
			}
		self.orientation = self.orientations[self.specification.imu['facing']][self.specification.imu['offset']]
class IMUMetric(Metric):
	def __init__(self, name, history = 0, archive = True, batch = 100):
		fullname = '{0}_{1}'.format('imu',name)
		super(IMUMetric,self).__init__(fullname, history, archive, batch)

if __name__ == '__main__':
	imu = IMU()
	time.sleep(10)
	imu.shutdown()
	time.sleep(0.5)