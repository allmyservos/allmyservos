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

## Schedules threaded tasks
class Scheduler(object):
	@staticmethod
	def GetInstance():
		""" returns a shared instance of the Scheduler object
		"""
		try:
			Scheduler.__sharedInstance
		except:
			Scheduler.__sharedInstance = Scheduler()
		return Scheduler.__sharedInstance
	def __init__(self):
		""" Initializes the Scheduler object
		"""
		self.tasks = {}
		self.notifier = Notifier()
	def addTask(self, name, callback, interval = 0.1, stopped = False):
		""" add a new task
		
		@param name
		@param callback
		@param interval
		@param stopped
		"""
		self.tasks[name] = GenericThread(name, callback, stopped, interval)
	def removeTask(self, name):
		""" remove a task
		
		@param name
		"""
		try:
			self.tasks[name].stop()
			del(self.tasks[name])
		except:
			pass
	def startTask(self, name):
		""" start a task
		
		@param name
		"""
		try:
			self.tasks[name].start()
		except:
			pass
	def stopTask(self, name):
		""" stop a task
		
		@param name
		"""
		try:
			self.tasks[name].stop()
		except:
			pass
	def isRunning(self, name):
		""" checks if a task is running
		
		@param name
		
		@return bool
		"""
		try:
			return not self.tasks[name].stopped
		except:
			return False
	def listTasks(self):
		""" list tasks
		
		@return list
		"""
		t = []
		for i in self.tasks:
			t.append(self.tasks[i].name)
		return t
## Generic thread objec, used for all scheduled tasks
class GenericThread(threading.Thread):
	def __init__(self, name, callback, stopped = False, interval = 0.1):
		""" Initializes a GenericThread object
		"""
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
		""" run this task
		"""
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
		""" stop tasks
		"""
		self.stopped = True
	def start(self):
		""" start task
		"""
		self.stopped = False