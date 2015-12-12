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
import re, os, datetime, Specification
from Scheduler import *
from subprocess import Popen, PIPE
from Notifier import *
class Network(object):
	def __init__(self, scheduler = None):
		if(scheduler != None):
			self.scheduler = scheduler
		else:
			self.scheduler = Scheduler()
		self.patterns = {}
		self.nodes = {}
		self.__initPatterns()
		self.nmapcachepath = os.path.join(Specification.Specification.filebase, 'network')
		self.nmapcachefile = 'nmap_cache.txt'
		self.nmapcommand = ['nmap', '192.168.0.0/24']
		self.ifconfigcommand = ['ifconfig']
		self.nics = []
		self.myip = None
		self.ifconfigraw = None
		self.nmapraw = None
		self.mapping = False
		self.notifier = Notifier()
		self.scheduler.addTask('network_mapper', self.update, 30)
	def __initPatterns(self):
		self.patterns['ifconfig'] = {}
		self.patterns['ifconfig']['nic'] = re.compile(r'(?P<name>[^\s]+).?')
		self.patterns['ifconfig']['addr'] = re.compile(r'\s*inet\saddr:(?P<ip>[^\s]+).*')
		self.patterns['nmap'] = {}
		self.patterns['nmap']['start'] = re.compile(r'Starting\sNmap\s(?P<version>[^\s]+)\s\( http:\/\/nmap.org \)\sat\s(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)\s(?P<hour>\d+):(?P<minute>\d+)\s(?P<timezone>\w+)')
		self.patterns['nmap']['report'] = re.compile(r'Nmap\sscan\sreport\sfor\s(?P<ip>[^\s]+)')
		self.patterns['nmap']['service'] = re.compile(r'(?P<port>[^\/]+)\/(?P<protocol>\w+)\s+(?P<state>\w+)\s+(?P<service>.+)')
		self.patterns['nmap']['mac'] = re.compile(r'MAC\sAddress:\s+(?P<mac>[^\s]+)\s+\((?P<brand>[^\)]+)\)')
	def update(self):
		if(self.ifconfigraw == None and self.mapping == False):
			self.mapping = True
			self.__ifconfig()
			self.mapping = False
		if(not self.__loadNmapCache()):
			if(self.myip != None and self.nmapraw == None and self.mapping == False):
				self.mapping = True
				self.nmapcommand[1] = self.__getBroadcast()
				self.__scanNetwork()
				self.__cacheNmap()
				self.mapping = False
	def __scanNetwork(self):
		result = False
		p = Popen(self.nmapcommand, stdout=PIPE)
		o = p.communicate()[0]
		if(p.returncode == 0):
			result = True
			self.nmapraw = o
			res = self.__parseNmap()
			if(res):
				self.notifier.addNotice('Nmap command complete')
		return result
	def __parseNmap(self):
		res = False
		if(self.nmapraw != None):
			tmp = []
			for l in self.nmapraw.split('\n'):
				match = self.patterns['nmap']['report'].match(l)
				if(match):
					tmp.append({ 'ip': match.group('ip'), 'mac': '', 'brand': '', 'services': [] })
				match = self.patterns['nmap']['service'].match(l)
				if(match):
					tmp[len(tmp)-1]['services'].append({ 'port': match.group('port'), 'protocol': match.group('protocol'), 'state': match.group('state'), 'service': match.group('service') })
				match = self.patterns['nmap']['mac'].match(l)
				if(match):
					tmp[len(tmp)-1]['mac'] = match.group('mac')
					tmp[len(tmp)-1]['brand'] = match.group('brand')
			for t in tmp:
				self.nodes[t['ip']] = t
			res = True
		return res
	def __parseDate(self, raw):
		date = None
		if(raw != None and raw != ''):
			linecount = 0
			for l in raw.split('\n'):
				match = self.patterns['nmap']['start'].match(l)
				if(match):
					datestring = '{0}-{1}-{2} {3}:{4} {5}'.format(match.group('year'), match.group('month'), match.group('day'), match.group('hour'), match.group('minute'), match.group('timezone'))
					tmpdate = datetime.datetime.strptime(datestring,'%Y-%m-%d %H:%M %Z')
					now = datetime.datetime.now()
					if(tmpdate > now - datetime.timedelta(days=1)):
						date = tmpdate
					break
				linecount += 1
				if(linecount >= 10):
					break
		return date
	def __cacheNmap(self):
		filepath = os.path.join(self.nmapcachepath, self.nmapcachefile)
		f = open(filepath, 'w')
		f.write(self.nmapraw)
		f.close()
	def __loadNmapCache(self):
		if not os.path.exists(self.nmapcachepath):
			os.makedirs(self.nmapcachepath)
			return False
		filepath = os.path.join(self.nmapcachepath, self.nmapcachefile)
		if not os.path.exists(os.path.join(self.nmapcachepath, self.nmapcachefile)):
			return False
		if len(self.nodes) > 0:
			return False
		f = open(filepath, 'r')
		data = f.read()
		f.close()
		date = self.__parseDate(data)
		if(date):
			self.nmapraw = data
			parsed = self.__parseNmap()
			self.notifier.addNotice('Nmap cache loaded')
			return parsed
		return False
	def __ifconfig(self):
		result = False
		p = Popen(self.ifconfigcommand, stdout=PIPE)
		o = p.communicate()[0]
		if(p.returncode == 0):
			result = True
			self.ifconfigraw = o
			res = self.__parseIfconfig()
			if(res):
				self.notifier.addNotice('Ifconfig command complete')
		return result
	def __parseIfconfig(self):
		if(self.ifconfigraw != None):
			for l in self.ifconfigraw.split('\n'):
				match = self.patterns['ifconfig']['nic'].match(l)
				if(match):
					self.nics.append({'name': match.group('name'), 'ip': ''})
				match = self.patterns['ifconfig']['addr'].match(l)
				if(match):
					self.nics[-1]['ip'] = match.group('ip')
			for n in self.nics:
				if(n['name'] != 'lo' and n['ip'] != '127.0.0.1'):
					self.myip = n['ip']
					break
			return True
		return False
	def __getBroadcast(self):
		ip = None
		if(self.myip != None and self.myip != '127.0.0.1'):
			parts = self.myip.split('.')
			if(len(parts) == 4):
				ip = '{0}.{1}.{2}.{3}'.format(parts[0], parts[1], parts[2], '0/24')
		return ip