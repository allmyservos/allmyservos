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
import threading, time, traceback
from Notifier import *

class Scheduler(object):
	def __init__(self):
		self.tasks = {}
		self.notifier = Notifier()
	def addTask(self, name, callback, interval = 0.1, stopped = False):
		self.tasks[name] = GenericThread(name, callback, stopped, interval)
	def removeTask(self, name):
		try:
			self.tasks[name].stop()
			del(self.tasks[name])
		except:
			pass
	def startTask(self, name):
		try:
			self.tasks[name].start()
		except:
			pass
	def stopTask(self, name):
		try:
			self.tasks[name].stop()
		except:
			pass
	def isRunning(self, name):
		try:
			return not self.tasks[name].stopped
		except:
			return False
	def listTasks(self):
		t = []
		for i in self.tasks:
			t.append(self.tasks[i].name)
		return t
class GenericThread(threading.Thread):
	def __init__(self, name, callback, stopped = False, interval = 0.1):
		threading.Thread.__init__(self)
		if(name != None):
			self.setName(name)
		self.callback = callback
		self.stopped = stopped
		if(isinstance(interval, (int, float, long)) and interval > 0.0):
			self.interval = interval
		else:
			self.interval = 0.1
		self.notifier = Notifier()
		self.daemon = True
		threading.Thread.start(self)
	def run(self):
		try:
			while True:
				try:
					d, start = 0, time.time()
				except:
					pass
				else:
					if(not self.stopped):
						try:
							self.callback()
						except Exception as e:
							self.notifier.addNotice('Error in {0}: {1}\nStack Trace: {2}'.format(self.name, e, traceback.format_exc()), 'warning')
					d = time.time() - start
					if (d > 0 and d < self.interval):
						time.sleep(self.interval - d)
					elif (d == self.interval):
						time.sleep(self.interval)
		except (KeyboardInterrupt, SystemExit, EOFError):
			cleanup_stop_thread()
			sys.exit()
	def stop(self):
		self.stopped = True
	def start(self):
		self.stopped = False