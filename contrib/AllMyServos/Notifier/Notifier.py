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
import time, Setting
from Metric import Metric
from Setting import Setting
class Notifier(object):
	def __init__(self, log = False, display = True):
		try:
			Notifier.display
		except:
			Notifier.display = display
			Notifier.type = 'notice'
			Notifier.text = ''
			Notifier.time = 0
			Notifier.callback = self.printNotice
		self.now = lambda: int(round(time.time() * 1000))
		if(Setting.get('notifier_archive', False)):
			self.metric = NotifierMetric()
	def setCallback(self, cb):
		Notifier.callback = cb
	def addNotice(self, text, type='notice'):
		Notifier.text = text
		Notifier.type = type
		Notifier.time = self.now()
		self.push()
	def getNotice(self):
		return { 'time': Notifier.time, 'text': Notifier.text, 'type': Notifier.type }
	def push(self):
		if(Setting.get('notifier_archive', False)):
			self.metric.value = { 'type': Notifier.type, 'text': Notifier.text }
		if(Notifier.display):
			Notifier.callback()
	def printNotice(self):
		print('{0}: {1}'.format(Notifier.type, Notifier.text))
class NotifierMetric(Metric):
	def __init__(self, history = 0, archive = True, batch = 1):
		super(NotifierMetric,self).__init__('notifications', history, archive, batch)