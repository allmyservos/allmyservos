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
#
# Joystick class is an enhanced version of the 2009 class
# by Jezra Lickter
# http://www.jezra.net/blog/Python_Joystick_Class_using_Gobject
#
#######################################################################
import sys, os, gobject, struct, array, re, copy
from fcntl import ioctl
from Scheduler import *

class JoystickRegistry(object):
	joysticks = {}
	callbacks = {}
	@staticmethod
	def IsAvailable():
		""" statically check if a joystick is available
		
		@return bool
		"""
		available = False
		for x in os.listdir('/dev/input'):
			if ('js' in x):
				available = True
				break
		return available
	@staticmethod
	def GetInstance(scheduler = None):
		""" statically get a shared instance of this class
		
		@return JoystickRegistry
		"""
		try:
			JoystickRegistry.__jrInstance
		except:
			JoystickRegistry.__jrInstance = JoystickRegistry(scheduler)
		return JoystickRegistry.__jrInstance
	def __init__(self, scheduler = None): 
		""" initialize the JoystickRegistry object
		
		@param scheduler
		"""
		self.patterns = {
			'js_device': re.compile(r'js(?P<devnum>\d+)')
		}
		if (scheduler != None):
			self.scheduler = scheduler
		else:
			self.scheduler = Scheduler.GetInstance()
		self.scan()
		self.scheduler.addTask('joystick_watcher', self.scan, interval = 2, stopped=not Setting.get('joystick_autostart', True))
	def scan(self):
		""" check for joysticks, initialize Joystick class when found
		"""
		devices = []
		# check connected
		for x in os.listdir('/dev/input'):
			match = self.patterns['js_device'].match(x)
			if (match):
				devices.append(x) # add to devices list
				if (not x in self.joysticks.keys()):
					self.joysticks[x] = Joystick(int(match.group('devnum'))) # initialize
		# check disconnected
		disconnected = [ k for k in self.joysticks.keys() if not k in devices ]
		if (any(disconnected)):
			for d in disconnected:
				del(self.joysticks[d])
		self.__updateCallbacks()
	def addCallback(self, name, callback):
		""" add a callback to receive events from joysticks
		
		@param name str
		@param callback function
		
		@return bool
		"""
		if (not name in self.callbacks.keys()):
			self.callbacks[name] = callback
			return True
		return False
	def removeCallback(self, name):
		""" remove a callback if it exists
		
		@param name str
		
		@return bool
		"""
		if (name  in self.callbacks.keys()):
			del(self.callbacks[name])
			self.__updateCallbacks()
			return True
		return False
	def hasCallback(self, name):
		""" check if a callback exists
		"""
		return name in self.callbacks.keys()
	def __updateCallbacks(self):
		""" pass callback functions to joysticks
		accounts for late connection / disconnection
		"""
		if (any(self.joysticks)):
			for k,v in self.joysticks.items():
				#register callbacks
				new = [x for x in self.callbacks.keys() if not x in v.callbacks.keys()]
				if (any(new)):
					for x in new:
						v.callbacks[x] = self.callbacks[x]
				#unregister callbacks
				togo = [x for x in v.callbacks.keys() if not x in self.callbacks.keys()]
				if (any(togo)):
					for x in togo:
						del(v.callbacks[x]) #should be removed
class Joystick(gobject.GObject): 
	"""The Joystick class is a GObject that sends signals that represent 
	Joystick events"""
	EVENT_BUTTON = 0x01 #button pressed/released 
	EVENT_AXIS = 0x02  #axis moved  
	EVENT_INIT = 0x80  #button/axis initialized  
	#see http://docs.python.org/library/struct.html for the format determination 
	EVENT_FORMAT = "IhBB" 
	EVENT_SIZE = struct.calcsize(EVENT_FORMAT) 
	 
	# we need a few signals to send data to the main 
	# signals will return 5 variables as follows: 
	# 1. a string representing if the signal is from an axis or a button 
	# 2. an integer representation of a particular button/axis 
	# 3. a string name of the button / axis
	# 4. an integer representing axis direction or button press/release 
	# 5. an integer representing the "init" of the button/axis 
	
	__gsignals__ = { 
	'axis' : 
	(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
	(gobject.TYPE_INT,gobject.TYPE_STRING,gobject.TYPE_INT,gobject.TYPE_INT)), 
	'button' : 
	(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
	(gobject.TYPE_INT,gobject.TYPE_STRING,gobject.TYPE_INT,gobject.TYPE_INT)) 
	} 
	
	axis_names = {
		0x00 : 'x',
		0x01 : 'y',
		0x02 : 'z',
		0x03 : 'rx',
		0x04 : 'ry',
		0x05 : 'rz',
		0x06 : 'throttle',
		0x07 : 'rudder',
		0x08 : 'wheel',
		0x09 : 'gas',
		0x0a : 'brake',
		0x10 : 'hat0x',
		0x11 : 'hat0y',
		0x12 : 'hat1x',
		0x13 : 'hat1y',
		0x14 : 'hat2x',
		0x15 : 'hat2y',
		0x16 : 'hat3x',
		0x17 : 'hat3y',
		0x18 : 'pressure',
		0x19 : 'distance',
		0x1a : 'tilt_x',
		0x1b : 'tilt_y',
		0x1c : 'tool_width',
		0x20 : 'volume',
		0x28 : 'misc',
	}

	button_names = {
		0x120 : 'trigger',
		0x121 : 'thumb',
		0x122 : 'thumb2',
		0x123 : 'top',
		0x124 : 'top2',
		0x125 : 'pinkie',
		0x126 : 'base',
		0x127 : 'base2',
		0x128 : 'base3',
		0x129 : 'base4',
		0x12a : 'base5',
		0x12b : 'base6',
		0x12f : 'dead',
		0x130 : 'a',
		0x131 : 'b',
		0x132 : 'c',
		0x133 : 'x',
		0x134 : 'y',
		0x135 : 'z',
		0x136 : 'tl',
		0x137 : 'tr',
		0x138 : 'tl2',
		0x139 : 'tr2',
		0x13a : 'select',
		0x13b : 'start',
		0x13c : 'mode',
		0x13d : 'thumbl',
		0x13e : 'thumbr',

		0x220 : 'dpad_up',
		0x221 : 'dpad_down',
		0x222 : 'dpad_left',
		0x223 : 'dpad_right',

		# XBox 360 controller uses these codes.
		0x2c0 : 'dpad_left',
		0x2c1 : 'dpad_right',
		0x2c2 : 'dpad_up',
		0x2c3 : 'dpad_down',
	}
	dual_axis = {
		'x': 'y',
		'rx': 'ry',
		'hat0x': 'hat0y',
		'hat1x': 'hat1y',
		'hat2x': 'hat2y',
		'tilt_x': 'tilt_y',
	}
	single_axis = {
		'z': False,
		'rz': False,
		'throttle': False,
		'rudder': False,
		'wheel': True,
		'gas': False,
		'brake': False,
		'pressure': False,
		'distance': False,
		'tool_width': False,
		'volume': False,
		'misc': False
	}
	
	JSIOCGAXES = 0x80016a11
	JSIOCGBUTTONS = 0x80016a12
	JSIOCGAXMAP = 0x80406a32
	JSIOCGBTNMAP = 0x80406a34
	
	def __init__(self,dev_num): 
		""" initialize Joystick object
		"""
		gobject.GObject.__init__(self) 
		self.callbacks = {}
		self.dev_num = dev_num
		#define the device 
		device = '/dev/input/js%s' % dev_num
		#error check that this can be read 
		try: 
			#open the joystick device 
			self.device = open(device) 
			#keep an eye on the device, when there is data to read, execute the read function 
			gobject.io_add_watch(self.device,gobject.IO_IN,self.read_buttons) 
		except Exception,ex: 
			#raise an exception 
			raise Exception( ex ) 
		self.info = {
			'name': self.get_name(),
			'num_axis': self.get_num_axis(),
			'num_buttons': self.get_num_buttons(),
			'axis_map': self.get_axis_map(),
			'button_map': self.get_button_map()
		}
	def get_name(self):
		""" gets the joystick name
		reads from the file: /sys/class/input/js0/device/name
		
		@return str
		"""
		name = ''
		buf = array.array('c', ['\0'] * 64)
		ioctl(self.device, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
		name = buf.tostring()
		if (not any(name)):
			#fallback try to get name from file
			namepath = os.path.join('/sys/class/input', 'js%s' % self.dev_num, 'device', 'name')
			name = 'Unknown'
			if (os.path.exists(namepath)):
				with open(namepath) as f:
					content = f.readlines()
				content = [x.strip() for x in content]
				if (any(content)):
					name = content[0]
				f.close()
		if (not any(name)):
			name = 'Unknown'
		return name
		
	def get_num_axis(self):
		"""gets number of axis
		
		@return int
		"""
		buf = array.array('B', [0])
		ioctl(self.device, self.JSIOCGAXES, buf)
		return buf[0]
	def get_num_buttons(self):
		"""gets number of axis
		
		@return int
		"""
		buf = array.array('B', [0])
		ioctl(self.device, self.JSIOCGBUTTONS, buf)
		return buf[0]
	
	def get_axis_map(self):
		"""gets list of axis names
		
		@return list
		"""
		buf = array.array('B', [0] * 0x40)
		ioctl(self.device, self.JSIOCGAXMAP, buf)
		axis_map = []
		for axis in buf[:self.get_num_axis()]:
			axis_name = self.axis_names.get(axis, 'unknown(0x%02x)' % axis)
			if (not axis_name in axis_map):
				axis_map.append(axis_name)
		return axis_map
	def get_button_map(self):	
		"""gets list of button names
		
		@return list
		"""
		buf = array.array('H', [0] * 200)
		ioctl(self.device, self.JSIOCGBTNMAP, buf)
		button_map = []
		for btn in buf[:self.get_num_buttons()]:
			btn_name = self.button_names.get(btn, 'unknown(0x%03x)' % btn)
			if (not btn_name in button_map):
				button_map.append(btn_name)
		return button_map
	def read_buttons(self, arg0='', arg1=''): 
		""" read the button and axis press event from the joystick device 
		and emit a signal containing the event data 
		"""
		#read self.EVENT_SIZE bytes from the joystick 
		read_event = self.device.read(self.EVENT_SIZE)   
		#get the event structure values from  the read event 
		time, value, type, number = struct.unpack(self.EVENT_FORMAT, read_event) 
		#get just the button/axis press event from the event type  
		event = type & ~self.EVENT_INIT 
		#get just the INIT event from the event type 
		init = type & ~event 
		name = 'unknown'
		if event == self.EVENT_AXIS: 
			signal = "axis"
			name = self.info['axis_map'][number] #get name
			value = float(value)/32767 #scale axis value
		elif event == self.EVENT_BUTTON: 
			signal = "button"
			try:
				name = self.info['button_map'][number] #get name
			except:
				pass
		if signal: 
			self.emit(signal,number,name,value,init) 
			self.__doCallbacks(signal,number,name,value,init)
		return True
	def registerCallbacks(self, callbacks):
		""" sets up one or more callbacks
		accepts tuple: (name, func) or dict { 'name1': func1, 'name2': func2 }
		
		@param callbacks
		"""
		if (isinstance(callbacks, dict) and any(callbacks)):
			self.callbacks.update(callbacks)
		elif(isinstance(callbacks, tuple) and len(callbacks) == 2):
			self.callbacks[callbacks[0]] = callbacks[1]
	def __doCallbacks(self,signal,number,name,value,init):
		""" perform callback function calls
		
		@param signal
		@param number
		@param name
		@param value
		@param init
		"""
		if (any(self.callbacks)):
			for x in self.callbacks.values():
				x(self.dev_num,signal,number,name,value,init)