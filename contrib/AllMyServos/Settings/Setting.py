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
import os
from DB import *

class Setting(Table):
	def __init__(self, name = '', storedvalue = '', type = 'string'):
		'''
		the setting class provides a type of variable which can be fetched from the database with a default value. if the setting doesn't exist, it is created.
		accessing settings in a loop does not cause multiple queries. setting values are cached.
		'''
		try:
			Setting.cache
		except:
			Setting.cache = {}
		self.name = name
		self.type = type
		self.storedvalue = storedvalue
		super(Setting,self).__init__(dbpath=os.path.join(os.getcwd(), 'files', 'settings', 'settings.db'))
	@property
	def value(self):
		'''
		gets the values of the setting
		'''
		if(self.name != ''):
			try:
				return self.cachedvalue
			except:
				if(self.type == 'bool'):
					if(self.storedvalue.lower() == 'true'):
						self.cachedvalue = True
					else:
						self.cachedvalue = False
				elif(self.type == 'int'):
					self.cachedvalue = int(self.storedvalue)
				elif(self.type == 'long'):
					self.cachedvalue = long(self.storedvalue)
				elif(self.type == 'float'):
					self.cachedvalue = float(self.storedvalue)
				elif(self.type == 'complex'):
					self.cachedvalue = complex(self.storedvalue)
				else:
					self.cachedvalue = self.storedvalue
				return self.cachedvalue
	@value.setter
	def value(self, value):
		'''
		saves the value of a setting
		'''
		if(self.name != ''):
			self.storedvalue = str(value)
			if(isinstance(value, bool)):
				self.type = 'bool'
			elif(isinstance(value, int)):
				self.type = 'int'
			elif(isinstance(value, long)):
				self.type = 'long'
			elif(isinstance(value, float)):
				self.type = 'float'
			elif(isinstance(value, complex)):
				self.type = 'complex'
			else:
				self.type = 'string'
			self.cachedvalue = value
			Setting.cache[self.name] = self
			self.save()
	def parseAttributes(self):
		'''
		overrides the parseAttributes function of the Table class to exclude 'value' and 'get'
		'''
		super(Setting,self).parseAttributes(['value', 'get'])
	@staticmethod
	def get(name, default = None):
		'''
		convenience function which retrieves a setting from cache, database or saves the default
		'''
		try:
			Setting.cache
		except:
			Setting.cache = {}
		try:
			return Setting.cache[name].value
		except:
			s = Setting()
			res = s.loadBy({'name':name})
			if(res != None):
				Setting.cache[res.name] = res
				return res.value
			elif(default != None):
				s = Setting(name)
				s.value = default
				Setting.cache[s.name] = s
				return s.value
	@staticmethod
	def set(name, value):
		'''
		sets the value of a setting in the cache, database or create it
		'''
		try:
			Setting.cache[name].value = value
		except:
			s = Setting()
			res = s.loadBy({'name':name})
			if(res != None):
				Setting.cache[res.name] = res
			else:
				Setting.cache[name] = Setting(name=name)
			Setting.cache[name].value = value
		return value
	def query(self, expr = '', order = '', keyindex = True):
		'''
		overrides the query function and adds any results to the cache
		'''
		res = super(Setting,self).query(expr, order, keyindex)
		for r in res:
			Setting.cache[res[r].name] = res[r]
			Setting.cache[res[r].name].value
		return res