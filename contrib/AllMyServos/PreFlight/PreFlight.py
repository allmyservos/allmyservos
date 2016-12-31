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
import os, re, json
from __bootstrap import AmsEnvironment
from subprocess import Popen, PIPE

## Pre flight checks - ensures the pi will work with servo features
class PreFlight:
	interfaces = { 'i2c': { 'interface': 'i2c_arm', 'enabled': False } }
	i2cModules = { 'i2c-bcm2708': False, 'i2c-dev': False}
	blacklist = { 'i2c-bcm2708': False }
	prep = [
		{'command': ['sudo', 'apt-get', '-q', '-y', 'update'], 'done': False },
		{'command': ['sudo', 'apt-get', '-q', '-y', 'upgrade'], 'done': False }
	]
	dependencies = [ 
		{'package': 'python-dev', 'installer': 'apt-get', 'installed': False },
		{'package': 'python-pip', 'installer': 'apt-get', 'installed': False },
		{'package': 'python-smbus', 'installer': 'apt-get', 'installed': False },
		{'package': 'i2c-tools', 'installer': 'apt-get', 'installed': False}
		]
	cache = {}
	cachepath = os.path.join(AmsEnvironment.FilePath(), 'PreFlight')
	cachefile = os.path.join(cachepath, 'cache.json')
	@staticmethod
	def status():
		""" gets the status of pre flight checks
		
		@return bool
		"""
		PreFlight.loadCache()
		try:
			if ('result' in PreFlight.cache.keys()):
				if(PreFlight.cache['result'] == True):
					#only use cache if all checks have passed
					PreFlight.interfaces = PreFlight.cache['interfaces']
					PreFlight.i2cModules = PreFlight.cache['modules']
					PreFlight.blacklist = PreFlight.cache['blacklist']
					PreFlight.prep = PreFlight.cache['prep']
					PreFlight.dependencies = PreFlight.cache['dependencies']
					return True
		except:
			pass
		return PreFlight.updateCache()
	@staticmethod
	def loadCache():
		""" load cached data if available
		"""
		if os.path.isfile(PreFlight.cachefile):
			try:
				f = open(PreFlight.cachefile, 'r')
				contents = f.read()
				f.close()
				PreFlight.cache = json.loads(contents)
			except:
				pass
	@staticmethod
	def updateCache():
		""" update cache data
		
		@return bool
		"""
		res = False
		if not os.path.exists(PreFlight.cachepath):
			os.makedirs(PreFlight.cachepath)
		interfaces = PreFlight.__checkInterfaces()
		mod = PreFlight.__checkModules()
		blk = PreFlight.__checkBlacklist()
		dep = PreFlight.__checkDependencies()
		if(interfaces and mod and blk and dep):
			res = True
		PreFlight.cache = { 'interfaces': PreFlight.interfaces, 'modules': PreFlight.i2cModules, 'blacklist': PreFlight.blacklist, 'prep': PreFlight.prep, 'dependencies': PreFlight.dependencies, 'result': res }
		f = open(PreFlight.cachefile, 'w')
		f.write(json.dumps(PreFlight.cache))
		f.close()
		return res
	@staticmethod
	def report():
		""" gets a full report of pre flight checks
		
		@return dict
		"""
		return { 'interfaces': PreFlight.interfaces, 'modules': PreFlight.i2cModules, 'blacklist': PreFlight.blacklist, 'prep': PreFlight.prep, 'dependencies': PreFlight.dependencies }
	@staticmethod
	def configure():
		""" performs configuration changes
		"""
		PreFlight.__configureInterfaces()
		PreFlight.__configureModules()
		PreFlight.__configureBlacklist()
		PreFlight.__performPrep()
		PreFlight.__configureDependencies()
		PreFlight.__reboot()
	@staticmethod
	def getPiI2CBusNumber():
		""" Gets the I2C bus number /dev/i2c#
		
		@return int
		"""
		return 1 if PreFlight.getPiRevision() > 1 else 0
	@staticmethod
	def getPiRevision():
		"""Gets the version number of the Raspberry Pi board
		Courtesy quick2wire-python-api
		https://github.com/quick2wire/quick2wire-python-api
		
		@return int
		"""
		try:
			with open('/proc/cpuinfo','r') as f:
				for line in f:
					if line.startswith('Revision'):
						return 1 if line.rstrip()[-1] in ['1','2'] else 2
		except:
			return 0
	@staticmethod
	def __checkInterfaces():
		""" check for interface line in config.txt
		
		@return bool
		"""
		f = open('/boot/config.txt', 'r')
		config = f.read()
		f.close()
		for k, v in PreFlight.interfaces.items():
			onPattern = re.compile(r'^dtparam={0}=on$'.format(v['interface']), re.MULTILINE)
			if (onPattern.search(config)):
				v['enabled'] = True #entry exists uncommented
		disabled = [ k for k, v in PreFlight.interfaces.items() if v['enabled'] == False ]
		if (not any(disabled)):
			return True
		return False
	@staticmethod
	def __checkModules():
		""" check modules for i2c lines
		
		@return bool
		"""
		names = PreFlight.i2cModules.keys()
		f = open('/etc/modules', 'r')
		for l in f:
			line = l.strip()
			if line in names:
				PreFlight.i2cModules[line] = True
		f.close()
		missing = [ k for k, v in PreFlight.i2cModules.iteritems() if v == False ]
		if(not any(missing)):
			return True
		return False
	@staticmethod
	def __checkBlacklist():
		""" check blacklist contents
		
		@return bool
		"""
		lines = []
		f = open('/etc/modprobe.d/raspi-blacklist.conf', 'r')
		for l in f:
			lines.append(l.strip())
		for k in PreFlight.blacklist.keys():
			if 'blacklist {}'.format(k) in lines:
				PreFlight.blacklist[k] = False
			else:
				PreFlight.blacklist[k] = True
		found = [ k for k, v in PreFlight.blacklist.iteritems() if v == False ]
		f.close()
		if(not any(found)):
			return True
		return False
	@staticmethod
	def __checkDependencies():
		""" check package dependencies
		
		@return bool
		"""
		for k, v in enumerate(PreFlight.dependencies):
			PreFlight.dependencies[k]['installed'] = True if PreFlight.__isInstalled(v) == 2 else False
		missing = [ d for d in PreFlight.dependencies if d['installed'] == False ]
		if(not any(missing)):
			return True
		return False
	
	@staticmethod
	def __configureInterfaces():
		""" append required lines to config.txt
		"""
		f = open('/boot/config.txt', 'r')
		config = f.read()
		f.close()
		writeRequired = False
		for k, v in PreFlight.interfaces.items():
			onPattern = re.compile(r'^dtparam={0}=on$'.format(v['interface']), re.MULTILINE)
			offPattern = re.compile(r'^dtparam={0}=off$'.format(v['interface']), re.MULTILINE)
			if (not onPattern.search(config)):
				#only perform configuration if it isn't already on
				if (offPattern.search(config)):
					#change entry
					config = config.replace('dtparam={0}=off'.format(v['interface']), 'dtparam={0}=on'.format(v['interface']))
					writeRequired = True
				else:
					#append entry
					if (config.endswith('\n')):
						config = config + 'dtparam={0}=on\n'.format(v['interface']) #append w/o newline prefix
					else:
						config = config + '\ndtparam={0}=on\n'.format(v['interface']) #append with newline prefix
					writeRequired = True
		if (writeRequired and len(config) > 10):
			f = open('/boot/config.txt', 'w')
			f.write(config)
			f.close()
	@staticmethod
	def __configureModules():
		""" append required line to modules
		"""
		names = PreFlight.i2cModules.keys()
		lines = []
		f = open('/etc/modules', 'r')
		for l in f:
			line = l.strip()
			lines.append(line)
			if line in names:
				PreFlight.i2cModules[line] = True
		f.close()
		missing = [ k for k, v in PreFlight.i2cModules.iteritems() if v == False ]
		if(any(missing)):
			for m in missing:
				lines.append(m)
			f = open('/etc/modules', 'w')
			f.write('\n'.join(lines))
			f.close()
	@staticmethod
	def __configureBlacklist():
		""" comment required lines from blacklist
		"""
		blnames = {'blacklist {}'.format(k): k for k in PreFlight.blacklist.keys()}
		lines = []
		saveneeded = False
		f = open('/etc/modprobe.d/raspi-blacklist.conf', 'r')
		for l in f:
			line = l.strip()
			lines.append(line)
			if line in blnames:
				lines[-1] = '#{}'.format(lines[-1])
				PreFlight.blacklist[blnames[line]] = True
				saveneeded = True
		f.close()
		if(saveneeded):
			f = open('/etc/modprobe.d/raspi-blacklist.conf', 'w')
			f.write('\n'.join(lines))
			f.close()
	@staticmethod
	def __configureDependencies():
		""" install required dependencies
		"""
		for k, v in enumerate(PreFlight.dependencies):
			if(not v['installed']):
				if(v['installer'] == 'apt-get'):
					PreFlight.dependencies[k]['installed'] = PreFlight.__installAptGetDependency(v)
				elif(v['installer'] == 'pip'):
					PreFlight.dependencies[k]['installed'] = PreFlight.__installPipDependency(v)
	@staticmethod
	def __performPrep():
		""" run preparation commands
		"""
		for k, v in enumerate(PreFlight.prep):
			p = Popen(v['command'], stdout=PIPE)
			o = p.communicate()[0]
			if(p.returncode == 0):
				PreFlight.prep[k]['done'] = True
	@staticmethod
	def __isInstalled(dependency):
		""" check if a dependency is installed or not
		status 0 = not installed
		status 1 = update required
		status 2 = installed
		
		@param dependency dict
		
		@return int
		"""
		status = 0
		if(dependency['installer'] == 'apt-get'):
			p = Popen(['dpkg','-s',dependency['package']], stdout=PIPE, stderr=PIPE)
			o = p.communicate()[0]
			if(p.returncode == 0):
				o = o.split('\n')
				pattern = re.compile(r'Status\:\s?(?P<status>.+)')
				for l in o:
					if(pattern.match(l)):
						status = 2
						break
		elif(dependency['installer'] == 'pip'):
			if(len(dependency['package']) > 0):
				try:
					p = Popen(['pip','search',dependency['package']], stdout=PIPE)
					o = p.communicate()[0]
					if(p.returncode == 0):
						o = o.split('\n')
						pattern = re.compile(r'(?P<package>[^\s]+)\s+-\s+(?P<description>.+)')
						installedpattern = re.compile(r'.*installed:\s+(?P<version>.*)',re.IGNORECASE)
						packagematch = -1
						line = 0
						for l in o:
							matches = pattern.match(l)
							if(matches):
								if(matches.group('package').lower() == dependency['package'].lower()):
									packagematch = line
							matches = installedpattern.match(l)
							if(matches and packagematch == line-1):
								v = matches.group('version')
								dv = str(dependency['version'])
								num = v.split(' ')[0]
								if(dv == 'latest' and 'latest' in v):
									status = 2
								elif(dv != 'latest' and StrictVersion(dv) <= StrictVersion(num)):
									status = 2
								else:
									status = 1
								break
							line += 1
				except:
					pass
		return status
	@staticmethod
	def __installAptGetDependency(dependency):
		""" install apt-get dependency
		
		@param dependency dict
		
		@return bool
		"""
		installed = False
		try:
			if(len(dependency['package']) > 0):
				command = ['sudo','apt-get','-q','-y','install', dependency['package'] ]
				p = Popen(command, stdout=PIPE)
				o = p.communicate()[0]
				if(p.returncode == 0):
					installed = True
		except:
			pass
		return installed
	@staticmethod
	def __installPipDependency(dependency):
		""" install pip dependency
		
		@return bool
		"""
		installed = False
		try:
			if(len(dependency['package']) > 0):
				command = ['sudo', 'pip', 'install', dependency['package'], '--upgrade']
				p = Popen(command, stdout=PIPE)
				o = p.communicate()[0]
				if(p.returncode == 0):
					installed = True
		except:
			pass
		return installed
	@staticmethod
	def __reboot():
		""" start rebooting
		"""
		p = Popen(['sudo','reboot'], stdout=PIPE)
		o = p.communicate()[0]