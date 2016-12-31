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

import time, json, os, copy, Specification
from Adafruit_PWM_Servo_Driver import PWM
from DB import *
from Setting import *
from Scheduler import *
from Metric import *
from JsonBlob import *

## Motions are animations for a set of servos
class Motion(JsonBlob):
	def __init__(self, index = None):
		""" Initializes the Motion object
		
		@param index
		"""
		super(Motion,self).__init__(index)
		if (not self.blobExists()):
			self.jsonData = {
				'name': '',
				'fps': 10,
				'keyframes': []
			}
## Servo abstraction
class Servo(JsonBlob):
	def __init__(self, index = None):
		""" Initializes the Servo object
		
		@param index
		"""
		super(Servo,self).__init__(index)
		if (not self.blobExists()):
			self.jsonData = {
				'name': '',
				'channel': 0,
				'ident': '',
				'angle': 0,
				'trim': 0,
				'disabled': False,
				'inverted': False,
				'displayOrder': 0,
				'servoMin': 150,
				'servoMax': 600,
				'boneName': '',
				'boneArmature': '',
				'boneAxis': '',
				'partNo': ''
			}
		self.now = lambda: int(round(time.time() * 1000))
		self.resetData()
		try:
			Servo.pwm
		except:
			debug = False
			if(Setting.get('servo_debug', False)):
				print("Setting Up PWM")
				debug = True
			Servo.pwm = PWM(0x40, debug=debug)
			Servo.pwm.setPWMFreq(60)
	def resetData(self):
		""" sync servo with saved data
		"""
		self.modifier = 0
		self.channel = self.jsonData['channel']
		self.angle = self.jsonData['angle']
		self.trim = self.jsonData['trim']
		self.disabled = self.jsonData['disabled']
		self.inverted = self.jsonData['inverted']
		self.buildPulseTable()
	def buildPulseTable(self):
		""" pre-calculate pwm values and index by angle 
		"""
		self.pulsetable = {}
		pulseunit = (float(self.jsonData['servoMax']) - float(self.jsonData['servoMin']))/180
		base = self.jsonData['servoMin'] + (pulseunit * self.jsonData['trim'])
		for i in range(181):
				self.pulsetable[i] = int((pulseunit*float(i))+base)
	def setCallback(self, func):
		""" sets the function to use for callbacks
		
		@param func
		"""
		self._callback = func
	def setServoAngle(self, time=None, modifier = 0):
		""" sync the physical servo angle with in-memoty value
		
		@param time int
		@param modifier int
		"""
		if(time != None):
			self.time = time
		else:
			self.time = self.now()
		if(isinstance(modifier, int)):
			self.modifier = modifier
		if(self.disabled):
			Servo.pwm.setPWM(int(self.channel),0,4096)
			self.doCallback()
			return True
		newAngle = self.angle + self.trim + self.modifier
		if(newAngle < 0):
			newAngle = 0
		if(newAngle > 180):
			newAngle = 180
		if(self.inverted):
			newAngle = 180 - newAngle
		Servo.pwm.setPWM(int(self.channel), 0, self.pulsetable[int(newAngle)])
		self.doCallback()
	def doCallback(self):
		""" perform callback
		"""
		try:
			self._callback()
		except:
			pass
	def relax(self):
		""" relax servo
		"""
		Servo.pwm.setPWM(int(self.channel),0,4096)
	def reload(self):
		""" sync object with saved data
		"""
		super(Servo,self).reload()
		self.resetData()
	def save(self):
		""" override JsonBlob.save() to allow specification ID to be inserted
		"""
		self.jsonData['ident'] = Specification.Specification.currentIdent()
		super(Servo,self).save()
## Motion scheduler maintains a list of motions and chains and runs them when triggered
class MotionScheduler(object):
	def __init__(self, specification = None, scheduler = None):
		""" Initializes the MotionScheduler object
		
		@param specification
		@param scheduler
		"""
		self.now = lambda: int(round(time.time() * 1000))
		self.queuedmotions = 0
		self.currentpos = 0
		
		if(specification == None):
			self.specification = Specification.Specification()
		else:
			self.specification = specification
		self.channelindex = { v.channel : v for k, v in self.specification.servos.items()}
		if(scheduler == None):
			self.scheduler = Scheduler()
		else:
			self.scheduler = scheduler
		self.cache = {}
		self.chaincache = {}
		self.queuemeta = []
		self.chainmeta = []
		self.queue = []
		self.queuecount = 0
		self.chaincount = 0
		self.scheduler.addTask('motion_scheduler', self.checkQueue, interval = 0.005, stopped=(not Setting.get('motion_scheduler_autostart', True)))
	def triggerMotion(self, id, slow = False):
		""" queue up a motion
		
		@param id str
		@param slow bool
		"""
		if(any(self.queuemeta)):
			if(self.queue[:1][0].jbIndex == id):
				return
		self.queuedmotions += 1
		self.queue.append(self.specification.motions[id])
		self.queuemeta.append({ 'queuepos' : self.queuedmotions, 'frameindex' : 0, 'slow' : slow })
		self.queuecount += 1
	def triggerChain(self, id):
		""" queue up a chain
		
		@param id str
		"""
		if(any(self.chainmeta)):
			self.chainmeta[0]['continue'] = True
			return
		self.chainmeta.append({ 'cid': id, 'type' : 'start', 'triggered' : [], 'looptriggered' : [], 'continue' : False})
		self.chaincount += 1
	def stopChain(self, id):
		""" advance a chain to stop motion
		
		@param id str
		"""
		if(len(self.chainmeta) == 0):
			return
		self.chainmeta[0]['type'] = 'stop'
	def checkQueue(self):
		""" process motion and chain queues
		applies a 'frame' of instructions from a motion.
		the 'frame' is chosen from the queued motion or motion related to the current chain position
		this function can be run multiple times per frame and will advance based on the motion FPS
		"""
		if(self.queuecount > 0):
			stamp = self.now()
			qmlen = len(self.queuemeta)
			qm = self.queuemeta[:1][0]
			qd = self.queue[:1][0]
			if(qm['frameindex'] < len(qd.jsonData['keyframes'])):
				if(self.currentpos != qm['queuepos']):
					self.currentpos = qm['queuepos']
					qm['starttime'] = stamp
				mtime = stamp - qm['starttime']
				kf = qd.jsonData['keyframes'][qm['frameindex']]
				if(qm['slow']):
					target = kf['time'] * float(Setting.get('motion_slow_factor', default=5))
				else:
					target = kf['time']
				if(target <= mtime):
					qm['frameindex'] += 1
					for i in kf['instructions']:
						self.channelindex[i['channel']].angle = i['angle']
						self.channelindex[i['channel']].disabled = i['disabled']
						self.channelindex[i['channel']].setServoAngle(time=stamp)
			else:
				self.queuecount -= 1
				if(qmlen > 1):
					self.queue = self.queue[1:]
					self.queuemeta = self.queuemeta[1:]
				else:
					self.queue[:] = []
					self.queuemeta[:] = []	
		elif(self.chaincount > 0):
			cm = self.chainmeta[0]
			chain = self.specification.chains[cm['cid']]
			if(cm['type'] == 'start'):
				#print('start motion')
				if(not self.findMotion(chain, cm)):
					cm['type'] = 'loop'
			elif(cm['type'] == 'loop'):
				#print('loop motion')
				if(not self.findMotion(chain, cm) and not cm['continue']):
					cm['type'] = 'stop'
			elif(cm['type'] == 'stop'):
				#print('stop motion')
				if(not self.findMotion(chain, cm)):
					cm['type'] = 'stopped'
			elif(cm['type'] == 'stopped'):
				if(self.chaincount > 1):
					self.chainmeta[1:]
				else:
					self.chainmeta = []
				self.chaincount -= 1
	def findMotion(self, chain, meta):
		""" given a chain (dict) and queue meta data (dict), locate and trigger the motion
		
		@param chain dict
		@param meta dict
		
		@return bool
		"""
		found = False
		for k, v in chain['motions'].items():
			if(not k in meta['triggered'] and meta['type'] == v['type'] and v['type'] != 'loop'):
				self.chainmeta[0]['triggered'].append(k)
				self.triggerMotion(self.specification.getMotionId(v['motion']))
				found = True
			elif(not k in meta['looptriggered'] and v['type'] == 'loop'):
				self.chainmeta[0]['looptriggered'].append(k)
				self.triggerMotion(self.specification.getMotionId(v['motion']))
				found = True
		if(not found and meta['type'] == 'loop' and meta['continue']):
			self.chainmeta[0]['looptriggered'] = []
			self.chainmeta[0]['continue'] = False
			found = True
		return found
	def relax(self):
		""" stock motion to relax all servos
		"""
		for s in self.channelindex.values():
			s.disabled = True
			s.setServoAngle()
	def default(self):
		""" stock motion to default all servos
		"""
		for s in self.channelindex.values():
			s.reload()
			s.setServoAngle()