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
import __bootstrap, time, Motion
from Keyboard import *
from Setting import Setting
from SRPC import *
class CLI:
	def __init__(self):
		self.s = Setting()
		self.printLicense()
		self.initMotionScheduler()
		self.initKbThread()
		self.initRPC()
		self.printFooter()
		try:
			while(True):
				time.sleep(100)
		except KeyboardInterrupt:
			print('''
Thanks for playing!''')
			sys.exit()
	def initMotionScheduler(self):
		self.motionScheduler = MotionScheduler()
		if(self.s.get('motion_scheduler_autostart', True)):
			print('Motion scheduler service - started')
		else:
			print('Motion scheduler service - stopped')
	def initKbThread(self):
		if(self.s.get('kb_autostart',True)):
			self.kbthread = KeyboardThread(motionScheduler = self.motionScheduler)
			print('Keyboard service - started')
		else:
			print('Keyboard service - stopped')
	def initRPC(self):
		if(self.s.get('rpc_autostart',True)):
			self.rpcserver = SRPCServer(motionScheduler = self.motionScheduler)
			print('RPC service - started')
		else:
			print('RPC service - stopped')
	def printLicense(self):
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
		print('''
Use Ctrl+C to exit
Use GUI.py to change configuration''')
if __name__ == "__main__":
	app = CLI()