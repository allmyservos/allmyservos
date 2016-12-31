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
import __bootstrap, time, logging, Notifier, Specification, Scheduler, Motion, Camera, Timelapse, TrayIcon
from __bootstrap import AmsEnvironment
from Keyboard import *
from Setting import Setting
from SRPC import *

## The CLI object handles the entire sequence of setting up the command line interface
class CLI:
	def __init__(self):
		""" Initializes the Command Line Interface
		"""
		self.s = Setting()
		self.notifier = Notifier()
		self.printLicense()
		self.initScheduler()
		self.initTrayIcon()
		self.initSpec()
		self.initMotionScheduler()
		self.initKbThread()
		self.initRPC()
		self.initCamera()
		self.printFooter()
		try:
			while(True):
				time.sleep(100)
		except KeyboardInterrupt:
			self.shutDown()
	def initTrayIcon(self):
		""" Initializes the system tray icon
		"""
		if (AmsEnvironment.IsLxdeRunning()):
			self.trayIcon = TrayIcon.TrayIcon(self.scheduler)
			self.trayIcon.setExitCallback(self.shutDown)
	def initSpec(self):
		""" Initializes the specification
		"""
		self.spec = Specification()
	def initScheduler(self):
		""" Initializes the scheduler
		"""
		self.scheduler = Scheduler()
	def initMotionScheduler(self):
		""" Initializes the motion scheduler
		"""
		self.motionScheduler = MotionScheduler()
		if(self.s.get('motion_scheduler_autostart', True)):
			print('Motion scheduler service - started')
		else:
			print('Motion scheduler service - stopped')
	def initKbThread(self):
		""" Initializes the keyboard service
		"""
		if(self.s.get('kb_autostart',True)):
			self.kbthread = KeyboardThread(self.spec, self.motionScheduler, self.scheduler)
			print('Keyboard service - started')
		else:
			print('Keyboard service - stopped')
	def initRPC(self):
		""" Initializes the RPC service
		"""
		self.rpcserver = SRPCServer(motionScheduler = self.motionScheduler)
		if(self.s.get('rpc_autostart',True)):
			print('RPC service - started')
		else:
			print('RPC service - stopped')
	def initCamera(self):
		""" Initializes the camera
		"""
		self.camera = Camera.Camera(self.scheduler, self.kbthread if hasattr(self, 'kbthread') else None, self.notifier)
		self.timelapse = Timelapse.Timelapse(self.camera)
		if(self.s.get('cam_autostart',True)):
			print('Camera service - started')
		else:
			print('Camera service - stopped')
	def shutDown(self):
		""" Handles shutting down the application
		"""
		self.__stoptasks()
		self.printOutro()
		sys.exit()
	def printLicense(self):
		""" Outputs the license text
		"""
		print('''AllMyServos - Fun with PWM
Copyright (C) 2015  Donate BTC:14rVTppdYQzLrqay5fp2FwP3AXvn3VSZxQ

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.
		
''')
	def printFooter(self):
		""" Outputs the footer
		"""
		print('''
Use Ctrl+C to exit
Use GUI.py to change configuration''')
	def printOutro(self):
		""" Outputs the outro message
		"""
		print('''
Thanks for playing!''')
	def __stoptasks(self):
		""" Stops all tasks runnung through the scheduler
		"""
		for name in self.scheduler.listTasks():
			self.scheduler.stopTask(name)
if __name__ == "__main__":
	
	app = CLI()
	