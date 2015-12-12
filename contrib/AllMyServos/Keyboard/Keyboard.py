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
import sys, termios, contextlib, Specification, Motion
from Scheduler import *
from Setting import *

@contextlib.contextmanager
def raw_mode(file):
	old_attrs = termios.tcgetattr(file.fileno())
	new_attrs = old_attrs[:]
	new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
	try:
		termios.tcsetattr(file.fileno(), termios.TCSADRAIN, new_attrs)
		yield
	finally:
		termios.tcsetattr(file.fileno(), termios.TCSADRAIN, old_attrs)
class KeyboardThread(object):
	def __init__(self, specification=None, map=None, motionScheduler=None, scheduler=None):
		'''
		used exclusively on the command line. Tkinter events drive the GUI.
		'''
		if(scheduler != None):
			self.scheduler = scheduler
		else:
			self.scheduler = Scheduler()
		if (specification != None):
			self.specification = specification
		else:
			self.specification = Specification.Specification()
		if(motionScheduler == None):
			self.motionScheduler = Motion.MotionScheduler()
		else:
			self.motionScheduler = motionScheduler
		self.callbacks = {}
		self.asciimap = AsciiMap()
		self.addCallback('motion', self.standardCallback)
		self.scheduler.addTask('kb_watcher', self.check, interval = 0.05, stopped=(not Setting.get('kb_autostart', False)))
	def check(self):
		with raw_mode(sys.stdin):
			ch = sys.stdin.read(1)
			if not ch or ch == chr(4):
				pass
			else:
				hex = '0x{0}'.format('%02x' % ord(ch))
				try:
					self.doCallback(hex=hex, ascii=self.asciimap.keyindex[hex])
				except:
					self.doCallback(hex=hex)
	def start(self):
		self.scheduler.startTask('kb_watcher')
	def stop(self):
		self.scheduler.stopTask('kb_watcher')
	def standardCallback(self, hex, ascii):
		mappings = []
		for h, a in self.asciimap.keyindex.items():
			if(h == hex):
				mappings = self.specification.getKeyMapping(h)
				break
		if(len(mappings) > 0):
			for m in mappings:
				if(m['action'] == 'motion' and m['command'] != None):
					for k, v in self.specification.motions.items():
						if (v['name'] == m['command']):
							self.motionScheduler.triggerMotion(k)
							break
				elif(m['action'] == 'chain' and m['command'] != None):
					for k, v in self.specification.chains.items():
						if (v['name'] == m['command']):
							self.motionScheduler.triggerChain(k)
							break
				elif(m['action'] == 'relax'):
					self.motionScheduler.relax()
				elif(m['action'] == 'default'):
					self.motionScheduler.default()
	def printCallback(self, hex, ascii):
		if(ascii != None):
			print({hex : ascii})
	def addCallback(self, index, func):
		self.callbacks.update({index:func})
	def removeCallback(self, index):
		del(self.callbacks[index])
	def doCallback(self, hex = None, ascii = None):
		for f in self.callbacks:
			self.callbacks[f](hex, ascii)

class AsciiMap(object):
	def __init__(self):
		AsciiMap.keyindex = {
		'0x20': '(sp)', 
		'0x21': '!', 
		'0x22': '"', 
		'0x23': '#', 
		'0x24': '$', 
		'0x25': '%', 
		'0x26': '&', 
		'0x27': '\'', 
		'0x28': '(', 
		'0x29': ')', 
		'0x2a': '*', 
		'0x2b': '+', 
		'0x2c': ',', 
		'0x2d': '-', 
		'0x2e': '.', 
		'0x2f': '/', 
		'0x30': '0', 
		'0x31': '1', 
		'0x32': '2', 
		'0x33': '3', 
		'0x34': '4', 
		'0x35': '5', 
		'0x36': '6', 
		'0x37': '7', 
		'0x38': '8', 
		'0x39': '9', 
		'0x3a': ':', 
		'0x3b': ';', 
		'0x3c': '<', 
		'0x3d': '=', 
		'0x3e': '>', 
		'0x3f': '?', 
		'0x40': '@', 
		'0x41': 'A', 
		'0x42': 'B', 
		'0x43': 'C', 
		'0x44': 'D', 
		'0x45': 'E', 
		'0x46': 'F', 
		'0x47': 'G', 
		'0x48': 'H', 
		'0x49': 'I', 
		'0x4a': 'J', 
		'0x4b': 'K', 
		'0x4c': 'L', 
		'0x4d': 'M', 
		'0x4e': 'N', 
		'0x4f': 'O', 
		'0x50': 'P', 
		'0x51': 'Q', 
		'0x52': 'R', 
		'0x53': 'S', 
		'0x54': 'T', 
		'0x55': 'U', 
		'0x56': 'V', 
		'0x57': 'W', 
		'0x58': 'X', 
		'0x59': 'Y', 
		'0x5a': 'Z', 
		'0x5b': '[', 
		'0x5c': '\\', 
		'0x5d': ']', 
		'0x5e': '^', 
		'0x5f': '_', 
		'0x60': '`', 
		'0x61': 'a', 
		'0x62': 'b', 
		'0x63': 'c', 
		'0x64': 'd', 
		'0x65': 'e', 
		'0x66': 'f', 
		'0x67': 'g', 
		'0x68': 'h', 
		'0x69': 'i', 
		'0x6a': 'j', 
		'0x6b': 'k', 
		'0x6c': 'l', 
		'0x6d': 'm', 
		'0x6e': 'n', 
		'0x6f': 'o', 
		'0x70': 'p', 
		'0x71': 'q', 
		'0x72': 'r', 
		'0x73': 's', 
		'0x74': 't', 
		'0x75': 'u', 
		'0x76': 'v', 
		'0x77': 'w', 
		'0x78': 'x', 
		'0x79': 'y', 
		'0x7a': 'z', 
		'0x7b': '{', 
		'0x7c': '|', 
		'0x7d': '}', 
		'0x7e': '~', 
		'0x7f': '(del)',
		'0x09': '(tab)'}

if __name__ == '__main__':
	t = KeyboardThread()
	t.addCallback('print', t.printCallback)
	t.start()
	