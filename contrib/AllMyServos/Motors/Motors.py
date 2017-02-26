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
import copy, Keyboard, Scheduler, Joystick
from __bootstrap import AmsEnvironment
import RPi.GPIO as GPIO
from JsonBlob import *
## DC Motor abstraction
class DcMotor(JsonBlob):
	@staticmethod
	def CleanupGpio():
		""" calls GPIO.cleanup()
		
		allows other modules to statically cleanup GPIO pins without importing RPi.GPIO
		"""
		GPIO.cleanup()
	def __init__(self, index = None):
		""" Initializes the DcMotor object
		
		@param index
		"""
		super(DcMotor,self).__init__(index)
		if (not self.blobExists()):
			self.jsonData = {
				'name': '',
				'enabled': False,
				'drive_type': 'dda',
				'pins': [{
					'name': 'PWM',
					'number': 13,
					'gpio_type': 'analogue'
				},
				{
					'name': 'IN1',
					'number': 15,
					'gpio_type': 'digital'
				},
				{
					'name': 'IN2',
					'number': 16,
					'gpio_type': 'digital'
				}],
				'controllers': {
					'joystick': {},
					'keyboard': {}
				},
				'acceleration': {
					'acc_time': 0,
					'dec_time': 0
				}
			}
		self.now = AmsEnvironment.Now
		self.driveState, self.shadowState = 0.0, 0.0
		self.driveTypes = {
			'dda': {
				'label': 'DDA',
				'compatible': ['L298N'],
				'pins': [{
					'name': 'PWM',
					'number': 13,
					'gpio_type': 'analogue'
				},
				{
					'name': 'IN1',
					'number': 15,
					'gpio_type': 'digital'
				},
				{
					'name': 'IN2',
					'number': 16,
					'gpio_type': 'digital'
				}]
			},
			'ddda': {
				'label': 'DDDA',
				'compatible': ['TB6612FNG'],
				'pins': [{
					'name': 'PWM',
					'number': 13,
					'gpio_type': 'analogue'
				},
				{
					'name': 'IN1',
					'number': 15,
					'gpio_type': 'digital'
				},
				{
					'name': 'IN2',
					'number': 16,
					'gpio_type': 'digital'
				},
				{
					'name': 'STBY',
					'number': 18,
					'gpio_type': 'digital'
				}]
			},
			'ddaa': {
				'label': 'DDAA',
				'compatible': ['BTS7960'],
				'pins': [{
					'name': 'L_EN',
					'number': 13,
					'gpio_type': 'digital'
				},
				{
					'name': 'R_EN',
					'number': 15,
					'gpio_type': 'digital'
				},
				{
					'name': 'LPWM',
					'number': 16,
					'gpio_type': 'analogue'
				},
				{
					'name': 'RPWM',
					'number': 18,
					'gpio_type': 'analogue'
				}]
			},
		}
		
		self.callbacks, self.pwm = {}, {}
		self.scheduler = Scheduler.Scheduler.GetInstance()
		self.kbthread = Keyboard.KeyboardThread.GetInstance()
		self.last = {
			'kb_signal': -1,
			'kb_start': -1,
			'shadow_start_time': -1,
			'shadow_start_state': 0,
			'shadow_start_drive_state': 0
		}
		self.running = False
		self.controllersEnabled = True
		self.resetData()
		self.scheduler.addTask('motor_%s' % self.jbIndex, self.updateDriveState, interval = 0.05, stopped=False)
	def resetData(self):
		""" sync motor with saved data
		"""
		self.driveType = self.jsonData['drive_type']
		self.pins = self.jsonData['pins']
		self.enabled = self.jsonData['enabled']
		self.acceleration = self.jsonData['acceleration'] if 'acceleration' in self.jsonData.keys() else { 'acc_time': 0, 'dec_time': 0 }
		self.controllers = self.jsonData['controllers']
		self.initControllers()
	def reload(self):
		""" override - sync object with saved data
		"""
		super(DcMotor,self).reload()
		self.resetData()
	def addCallback(self, name, func):
		""" add a callback to this motor
		"""
		if (not name in self.callbacks.keys()):
			self.callbacks[name] = func
			return True
		return False
	def removeCallback(self, name):
		""" remove a callback from this motor
		"""
		if (name in self.callbacks.keys()):
			del(self.callbacks[name])
			return True
		return False
	def hasCallback(self, name):
		""" check if a callback exists
		"""
		if (name in self.callbacks.keys()):
			return True
		return False
	def doCallbacks(self):
		""" perform callbacks
		"""
		if (any(self.callbacks)):
			for v in self.callbacks.values():
				v(self.driveState)
	def start(self):
		""" start motor
		setup gpio pins
		"""
		if (self.enabled and not self.running):
			GPIO.setmode(GPIO.BOARD)
			for p in self.pins:
				if (p['gpio_type'] == 'digital'):
					GPIO.setup(p['number'], GPIO.OUT)
					GPIO.output(p['number'], GPIO.LOW)
				else:
					GPIO.setup(p['number'], GPIO.OUT)
					self.pwm['p%s' % p['number']] = GPIO.PWM(p['number'], 50)
					self.pwm['p%s' % p['number']].ChangeDutyCycle(0 if self.driveType != 'ddaa' else 100)
					self.pwm['p%s' % p['number']].start(1)
			self.running = True
			return True
		return False
	def stop(self):
		""" stop motor
		shutdown gpio pins
		"""
		if (self.running):
			for p in self.pins:
				if (p['gpio_type'] == 'analogue'):
					self.pwm['p%s' % p['number']].stop()
				else:
					GPIO.output(p['number'], GPIO.LOW) # set digital pins low for safety
			self.running = False
			return True
		return False
	def save(self):
		""" add a callback to this motor
		"""
		self.jsonData['drive_type'] = self.driveType
		self.jsonData['pins'] = self.pins
		self.jsonData['controllers'] = self.controllers
		self.jsonData['acceleration'] = self.acceleration
		super(DcMotor, self).save()
	def setDriveState(self, driveState = 0):
		""" sets the drive state
		start if enabled, sanitize, clip and apply drive state
		"""
		if (self.enabled and not self.running):
			self.start()
		if (not self.running):
			return False #motor is disabled
		if (not isinstance(driveState, (int, float))):
			driveState = 0 #sanitize
		self.driveState = round(float(driveState),3)
		if (self.driveState > 1):
			self.driveState = 1.0 #clip top
		if (self.driveState < -1):
			self.driveState = -1.0 #clip bottom
		
	def updateDriveState(self):
		self.simulateKeyUp()
		# update shadow state
		self.updateShadowState()
		# apply shadow state
		if (self.enabled and self.running):
			if (self.shadowState > 1):
				self.shadowState = 1.0 #clip top
			if (self.shadowState < -1):
				self.shadowState = -1.0 #clip bottom
			if (self.driveType == 'dda'):
				#L298N style output
				if (self.shadowState > 0):
					GPIO.output(self.pins[1]['number'], GPIO.LOW)
					GPIO.output(self.pins[2]['number'], GPIO.HIGH)
				else:
					GPIO.output(self.pins[1]['number'], GPIO.HIGH)
					GPIO.output(self.pins[2]['number'], GPIO.LOW)
				self.pwm['p%s' % self.pins[0]['number']].ChangeDutyCycle(abs(self.shadowState) * 100)
				self.doCallbacks()
				return True
			elif(self.driveType == 'ddda'):
				#TB6612FNG style output
				GPIO.output(self.pins[3]['number'], GPIO.HIGH) # stby
				if (self.shadowState > 0):
					GPIO.output(self.pins[1]['number'], GPIO.LOW)
					GPIO.output(self.pins[2]['number'], GPIO.HIGH)
				else:
					GPIO.output(self.pins[1]['number'], GPIO.HIGH)
					GPIO.output(self.pins[2]['number'], GPIO.LOW)
				self.pwm['p%s' % self.pins[0]['number']].ChangeDutyCycle(abs(self.shadowState) * 100)
			elif(self.driveType == 'ddaa'):
				#BTS7960 style output
				GPIO.output(self.pins[0]['number'], GPIO.HIGH)
				GPIO.output(self.pins[1]['number'], GPIO.HIGH)
				if (self.shadowState > 0):
					self.pwm['p%s' % self.pins[2]['number']].ChangeDutyCycle(100-abs(self.shadowState) * 100)
					self.pwm['p%s' % self.pins[3]['number']].ChangeDutyCycle(100)
				else:
					self.pwm['p%s' % self.pins[2]['number']].ChangeDutyCycle(100)
					self.pwm['p%s' % self.pins[3]['number']].ChangeDutyCycle(100-abs(self.shadowState) * 100)
				self.doCallbacks()
				return True
		return False
	def simulateKeyUp(self):
		""" simulate keyup event
		the keyboard service provides repeated callbacks while a key is pressed.
		this simulates a keyup event to stop the motor.
		there is a gap between the first callback and subsequent callbacks so at a minimum the motor must run for 0.5 seconds.
		"""
		if (self.driveState != 0):
			if (self.last['kb_signal'] > -1 and self.now() - self.last['kb_start'] > 500 and self.now() - self.last['kb_signal'] >= 50):
				#simulate keyup
				self.setDriveState(0) # stop motor
				self.last['kb_start'],self.last['kb_signal'] = -1,-1 #reset last kb variables
	def updateShadowState(self):
		""" accelerate / decelerate shadow state
		this allows the shadow state to lag behind the drive state to produce acceleration / deceleration effect
		"""
		if (self.driveState != self.shadowState):
			now = self.now()
			accIndex = 'acc_time'
			if ((self.shadowState < 0 and self.driveState > 0) or (self.shadowState > 0 and self.driveState < 0) or abs(self.shadowState) > abs(self.driveState)):
				accIndex = 'dec_time'
			if (self.acceleration[accIndex] > 0):
				if (self.last['shadow_start_time'] == -1 or self.last['shadow_start_drive_state'] != self.driveState):
					self.last.update({'shadow_start_time': now, 'shadow_start_state': self.shadowState, 'shadow_start_drive_state': self.driveState}) # mark acc start
				timeDiff = now - self.last['shadow_start_time']
				accMs = self.acceleration[accIndex] * 1000
				if(timeDiff <= accMs):
					#first or inside acc / dec time
					self.shadowState = self.last['shadow_start_state'] - (self.last['shadow_start_state'] - self.last['shadow_start_drive_state']) * (timeDiff / accMs)
				else:
					self.shadowState = self.driveState # ensure final matching values
			else:
				self.shadowState = self.driveState # mirror drive state (no acceleration)
		elif(self.last['shadow_start_time'] != -1):
			self.last.update({'shadow_start_time': -1, 'shadow_start_state': 0}) # finished shadow update
	def initControllers(self):
		""" register controllers with joystick or keyboard services
		"""
		# joystick controllers
		if (any(self.controllers['joystick']) and Joystick.JoystickRegistry.IsAvailable()):
			self.joystickRegistry = Joystick.JoystickRegistry.GetInstance()
			if (not self.joystickRegistry.hasCallback('motor_%s' % self.jbIndex)):
				self.joystickRegistry.addCallback('motor_%s' % self.jbIndex, self.joystickCallback)
		# keyboard controllers
		if (any(self.controllers['keyboard']) and not self.kbthread.hasCallback('motor_%s' % self.jbIndex)):
			pass
			self.kbthread.addCallback('motor_%s' % self.jbIndex, self.keyboardCallback)
		elif (not any(self.controllers['keyboard']) and self.kbthread.hasCallback('motor_%s' % self.jbIndex)):
			self.kbthread.removeCallback('motor_%s' % self.jbIndex)
	def hasControllers(self):
		""" check if any controllers exist
		"""
		return True if any(self.controllers['joystick']) or any(self.controllers['keyboard']) else False
	def newController(self, controllerType = 'joystick'):
		""" get the default dict for a controller
		"""
		controller = {'type':controllerType}
		if (controllerType == 'joystick'):
			controller.update({
				'dev_num': 0,
				'device': '',
				'signal': '',
				'number': 0,
				'name': '',
				'invert': False,
				'drive_mode': 'drive_state',
				'mix_mode': 'override',
				'dead_zone': 0.05
			})
		elif (controllerType == 'keyboard'):
			controller.update({
				'hex': '',
				'ascii': '',
				'invert': False,
				'drive_mode': 'drive_state',
				'mix_mode': 'override',
			})
		return controller
	def updateController(self, controller, controllerType = 'joystick'):
		""" update motor controller
		"""
		if (not controllerType in self.controllers.keys()):
			return 'unsupported'
		if (controllerType == 'joystick'):
			newIdent = '%s-%s-%s' % (controller['dev_num'], controller['signal'], controller['number'])
			if ('ident' in controller and controller['ident'] != newIdent):
				#joystick action has been changed
				controller = copy.copy(self.controllers['joystick'][controller['ident']])
				del(self.controllers['joystick'][controller['ident']])
			controller['ident'] = newIdent
			self.controllers['joystick'][controller['ident']] = controller
			self.initControllers()
			return 'updated'
		elif (controllerType == 'keyboard'):
			if ('ident' in controller and controller['ident'] != controller['hex']):
				#keyboard action has been changed
				controller = copy.copy(self.controllers['keyboard'][controller['ident']])
				del(self.controllers['keyboard'][controller['ident']])
			controller['ident'] = controller['hex']
			self.controllers['keyboard'][controller['ident']] = controller
			self.initControllers()
			return 'updated'
		return 'failed'
	def hasController(self, controllerType, ident):
		""" check if a controller exists
		"""
		if (controllerType in self.controllers.keys() and ident in self.controllers[controllerType].keys()):
			return True
		return False
	def removeController(self, controllerType, ident):
		""" remove controller from motor
		"""
		if (controllerType in self.controllers.keys() and ident in self.controllers[controllerType].keys()):
			del(self.controllers[controllerType][ident])
			self.initControllers()
			return True
		return False
	def joystickCallback(self,dev_num,signal,number,name,value,init):
		""" perform joystick callback
		"""
		if (self.controllersEnabled and init == 0):
			ds, additive = 0, 0
			for c in self.controllers['joystick'].values():
				try:
					if (signal == 'axis' and c['dead_zone'] > abs(value)):
						value = 0 # override under dead zone
				except:
					pass # ignore if no dead zone
				if (c['dev_num'] == dev_num and c['signal'] == signal and c['number'] == number):
					#current controller
					c['value'] = value if not c['invert'] else 0 - value
				else:
					#other controllers
					if (not 'value' in c.keys()):
						c['value'] = 0 #default value
				if ('mix_mode' in c.keys() and c['mix_mode'] == 'additive'):
					additive += c['value'] #additive
				elif(c['value'] != 0):
					ds = c['value'] #override
			self.setDriveState(ds + (additive * (1-ds *0.5)))
	def keyboardCallback(self, hex, ascii):
		""" perform keyboard callback
		"""
		if (self.controllersEnabled and any(hex)):
			try:
				self.controllers['keyboard'][hex]
			except:
				pass
			else:
				# apply controller
				self.last['kb_signal'] = self.now()
				if (self.last['kb_start'] == -1):
					self.last['kb_start'] = self.now()
				self.setDriveState(-1 if self.controllers['keyboard'][hex]['invert'] else 1)
## Stepper Motor abstraction
class StepperMotor(DcMotor):
	def __init__(self, index = None):
		""" Initializes the StepperMotor object
		
		@param index
		"""
		super(StepperMotor,self).__init__(index)
		if (not self.blobExists()):
			
			del(self.jsonData['drive_type'])
			self.jsonData.update({
				'name': '',
				'enabled': False,
				'normalize_angle': True,
				'rpm': 60,
				'steps_per_rev': 200,
				'angle': 0,
				'output_order': [0,1,2,3],
				'sequence_key': 'half_step',
				'sequence': [[1,0,0,1],
					[1,0,0,0],
					[1,1,0,0],
					[0,1,0,0],
					[0,1,1,0],
					[0,0,1,0],
					[0,0,1,1],
					[0,0,0,1]],
				'pins': [{
					'name': 'AIN1',
					'number': 13,
					'gpio_type': 'digital'
				},
				{
					'name': 'AIN2',
					'number': 15,
					'gpio_type': 'digital'
				},
				{
					'name': 'BIN1',
					'number': 16,
					'gpio_type': 'digital'
				},
				{
					'name': 'BIN2',
					'number': 18,
					'gpio_type': 'digital'
				}],
			})
		self.stage = 0
		self.angle = float(self.jsonData['angle']) if 'angle' in self.jsonData.keys() else 0
		self.target = None
		self.last.update({
			'stage': -1,
			'step_time': 0
		})
		self.outputOrders = {
			'1234': [0,1,2,3],
			'1324': [0,2,1,3],
		}
		self.sequences = {
			'half_step': [[1,0,0,1],
				[1,0,0,0],
				[1,1,0,0],
				[0,1,0,0],
				[0,1,1,0],
				[0,0,1,0],
				[0,0,1,1],
				[0,0,0,1]],
			'full_step': [[1,0,0,0],
				[0,1,0,0],
				[0,0,1,0],
				[0,0,0,1]],
		}
		self.resetData()
	def resetData(self):
		if ('angle' in self.jsonData.keys()):
			#only perform if stepper data has been setup (avoid calls from base class)
			self.enabled = self.jsonData['enabled']
			self.normalizeAngle = self.jsonData['normalize_angle'] if 'normalize_angle' in self.jsonData else True
			self.minTime = ((60.0 / float(self.jsonData['rpm'])) / float(self.jsonData['steps_per_rev'])) * 1000
			self.outputOrder = self.jsonData['output_order']
			self.sequence = self.jsonData['sequence']
			self.sequenceLength  = len(self.sequence)
			self.pins = self.jsonData['pins']
			if(self.scheduler.isRunning('motor_%s' % self.jbIndex)):
				self.scheduler.tasks['motor_%s' % self.jbIndex].interval = self.minTime / 1000 # sync motor task interval with rpm / steps per rev
			self.acceleration = self.jsonData['acceleration'] if 'acceleration' in self.jsonData.keys() else { 'acc_time': 0, 'dec_time': 0 }
			self.controllers = self.jsonData['controllers']
			self.initControllers()
	def reload(self):
		""" override - sync object with saved data
		"""
		super(StepperMotor,self).reload()
		self.resetData()
	def getOutputOrder(self, asList = False):
		""" gets the current output order
		"""
		if (asList):
			return self.outputOrder
		else:
			o = [k for k,v in self.outputOrders.items() if v[0] == self.outputOrder[0] and v[1] == self.outputOrder[1] and v[2] == self.outputOrder[2] and v[3] == self.outputOrder[3]]
			if (any(o)):
				return o[0]
		return []
	def setZeroAngle(self):
		""" assigns 0 angle to the current motor position
		"""
		self.angle = 0
		self.save()
		self.doCallbacks() # perform callbacks
	def moveToAngle(self, newAngle = 0):
		""" move the motor to the specified angle
		"""
		if (not self.running):
			self.start()
		self.target = self.__normalizeAngle(newAngle) if self.normalizeAngle else newAngle
	def moveByAngle(self, newAngle = 0):
		""" move the motor by the specified angle
		"""
		if (not self.running):
			self.start()
		newAngle = self.angle + newAngle
		self.target = newAngle
	def updateDriveState(self):
		""" update drive state
		called from scheduled task (runs on it's own thread)
		stops stepper motor if no changes have been sent in the last 10 seconds
		delays steps based on rpm and steps per rev
		if a target is provided, move toward it
		otherwise use drive state to determine speed
		"""
		if (not hasattr(self, 'enabled') or not self.enabled):
			return # not setup or enabled?
		if(not self.running):
			return
		self.simulateKeyUp() #reset drive state if there was kb control but not for a while
		# update shadow state
		self.updateShadowState()
		now = self.now()
		if (self.shadowState == 0 and self.target == None and self.last['step_time'] != 0 and self.last['step_time'] < now - 10000):
			return self.stop() #stepper stopper timeout (prevents overheating / saves power)
		waitTime = self.minTime * (1+((1-abs(self.shadowState))*self.jsonData['rpm'])) if self.target == None else self.minTime # speed control
		if (now - self.last['step_time'] < waitTime):
			return #rpm / wait limit
		angleChange = 0
		nextStage = self.stage
		if (self.target != None):
			#move to target
			if (self.__angularDistance(self.target, self.angle) < 0.1):
				self.target = None #target reached
				return
			if(self.target > self.angle):
				#clockwise
				if (self.stage < self.sequenceLength - 1):	
					nextStage += 1
				else:
					nextStage = 0
				angleChange = 360.0 / self.jsonData['steps_per_rev']
			elif(self.target < self.angle):
				#anticlockwise
				if (self.stage > 0):
					nextStage -= 1
				else:
					nextStage = self.sequenceLength - 1
				angleChange = 0-(360.0 / self.jsonData['steps_per_rev'])
		else:
			#move with drive state
			if (self.shadowState > 0):
				#clockwise
				if (self.stage < self.sequenceLength - 1):	
					nextStage += 1
				else:
					nextStage = 0
				angleChange = 360.0 / self.jsonData['steps_per_rev']
			elif (self.shadowState < 0):
				#anticlockwise
				if (self.stage > 0):
					nextStage -= 1
				else:
					nextStage = self.sequenceLength - 1
				angleChange = 0-(360.0 / self.jsonData['steps_per_rev'])
			else:
				#still
				pass
		if (nextStage != self.last['stage']):
			#time to move
			if (self.jsonData['sequence_key'] == 'half_step'):
				angleChange *= 0.5
			newAngle = self.angle + angleChange
			self.angle = self.__normalizeAngle(newAngle) if self.normalizeAngle else newAngle #track angle change
			self.last['stage'] = self.stage = nextStage
			self.last['step_time'] = now
			stage = self.sequence[self.stage]
			index = 0
			for x in self.outputOrder:
				p = self.pins[x]
				if (p['gpio_type'] == 'digital'):
					if (self.enabled and self.running and angleChange != 0):
						GPIO.output(p['number'], GPIO.HIGH if stage[index] == 1 else GPIO.LOW)
					else:
						GPIO.output(p['number'], GPIO.LOW) # dead zone
					index += 1 # track list index
			self.doCallbacks() # perform callbacks
	def stop(self):
		""" override - also calls save for the current angle
		"""
		super(StepperMotor,self).stop()
		self.save() #stores the current angle
	def save(self):
		""" override - saves stepper specific attributes
		"""
		self.jsonData['enabled'] = self.enabled
		self.jsonData['normalize_angle'] = self.normalizeAngle
		self.jsonData['angle'] = self.angle
		self.jsonData['output_order'] = self.outputOrder
		self.jsonData['sequence'] = self.sequence
		self.jsonData['pins'] = self.pins
		self.jsonData['controllers'] = self.controllers
		super(DcMotor, self).save()
	def joystickCallback(self,dev_num,signal,number,name,value,init):
		""" move the motor to the specified angle
		"""
		if (self.controllersEnabled and init == 0):
			c = [x for x in self.controllers['joystick'].values() if x['drive_mode'] in ['zero_angle','move_to','move_by'] and x['dev_num'] == dev_num and x['signal'] == signal and x['number'] == number]
			if (any(c)):
				c = c[0] #just take the first (should only be one)
				try:
					if (signal == 'axis' and c['dead_zone'] > abs(value)):
						value = 0 # override under dead zone
				except:
					pass
				if (c['drive_mode'] == 'zero_angle'):
					self.setZeroAngle()
					return
				if (c['invert']):
						value = 0 - value # invert value
				angleFunc = self.moveToAngle if c['drive_mode'] == 'move_to' else self.moveByAngle
				if (c['signal'] == 'axis' and value != 0):
					angleFunc(c['pos_angle'] if value > 0 else c['neg_angle']) # move to axis angle
				elif (c['signal'] == 'button' and value != 0):
					angleFunc(c['angle']) # move to button angle
			else:
				super(StepperMotor, self).joystickCallback(dev_num,signal,number,name,value,init) # handle drive state normally
	def keyboardCallback(self, hex, ascii):
		""" perform keyboard callback
		"""
		if (self.controllersEnabled):
			c = [x for x in self.controllers['keyboard'].values() if x['drive_mode'] in ['zero_angle','move_to','move_by'] and x['hex'] == hex]
			if (any(c)):
				c = c[0] #just take the first (should only be one)
				if (c['drive_mode'] == 'zero_angle'):
					self.setZeroAngle()
					return
				if (c['invert']):
						value = 0 - value # invert value
				angleFunc = self.moveToAngle if c['drive_mode'] == 'move_to' else self.moveByAngle
				angleFunc(c['angle']) # move to button angle
			else:
				super(StepperMotor, self).keyboardCallback(hex, ascii)
	def __normalizeAngle(self, angle):
		""" convert given angle to one within the range -180 - 180
		
		@param angle float
		
		@return float
		"""
		if(angle > 180.0):
			while(angle > 180.0):
				angle -= 360.0 # reduce to normal range
		if(angle <= -180.0):
			while(angle <= -180.0):
				angle += 360.0 # increase to normal range
		return angle
	def __angularDistance(self, a, b):
		""" get the angular distance between two given angles
		
		@param a float
		@param b float
		
		@return float
		"""
		a = self.__normalizeAngle(a)
		b = self.__normalizeAngle(b)
		return abs(self.__normalizeAngle(a - b))