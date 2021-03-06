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
import sys, os, shutil, distutils.core, uuid, tarfile, time, copy, errno, JsonBlob, Motion, Motors
from __bootstrap import AmsEnvironment
from xml.dom import minidom
from xml.dom.minidom import Document
from Setting import *

## Robot specification
class Specification(JsonBlob.JsonBlob):
	cwd = AmsEnvironment.AppPath()
	basepath = os.path.join(cwd, 'specifications')
	installpath = os.path.join(basepath, 'installed')
	packagepath = os.path.join(basepath, 'packages')
	filebase = AmsEnvironment.FilePath()
	@staticmethod
	def GetInstance(index = None):
		try:
			Specification.__sharedInstance
		except:
			Specification.__sharedInstance = Specification(index)
		return Specification.__sharedInstance
	@staticmethod
	def currentIdent(new = False):
		""" gets the current specification id
		if a valid id is not found, a new one is created
		
		@param new bool
		"""
		JsonBlob.JsonBlob.reindex()
		if (not new and 
		'Specification' in JsonBlob.JsonBlob.index.keys() and 
		'Specification' in JsonBlob.JsonBlob.index['Specification']['classes'] and 
		any(JsonBlob.JsonBlob.index['Specification']['classes']['Specification']['rows'])):
			#take the first available id
			currentident = JsonBlob.JsonBlob.index['Specification']['classes']['Specification']['rows'][0]
		else:
			#generate a new id
			currentident = Specification.newIdent()
		savedident = Setting.get('spec_active_ident', currentident) #get the active ident setting
		if not new and os.path.exists(os.path.join(Specification.installpath, savedident)):
			currentident = savedident #the saved ident refers to an existing specification so use it 
		elif not new:
			Setting.set('spec_active_ident', currentident) #update the saved active ident
		return currentident
	@staticmethod
	def newIdent():
		""" generates a new id
		"""
		return str(uuid.uuid4())
	@staticmethod
	def listPackages():
		""" gets a list of specification packages
		"""
		res = {}
		if (not os.path.exists(Specification.packagepath)):
			os.makedirs(Specification.packagepath)
		tarpaths = [ x for x in os.listdir(Specification.packagepath) if '.tar.gz' in x ]
		for t in tarpaths:
			id = t.replace('.tar.gz', '')
			res[id] = Specification.getPackageInfo(t)
		return res
	@staticmethod
	def getPackageInfo(filename):
		""" collects the spec data inside a package
		
		@param filename
		"""
		extras = { 'file': filename, 'ident': filename.replace('.tar.gz', '') }
		extras['installed'] = os.path.exists(os.path.join(Specification.installpath, extras['ident']))
		tar = tarfile.open(os.path.join(Specification.packagepath, filename), "r:gz")
		for name in tar.getnames():
			parts = os.path.splitext(name)
			if(len(parts) == 2):
				if(extras['ident'] == parts[0] and parts[1] == '.json'):
					#spec json
					extras.update(json.loads(tar.extractfile(name).read()))
		tar.close()
		return extras
	@staticmethod
	def clone(ident, codename = None):
		""" clone a specification
		
		@param ident
		@param codename
		"""
		oldspec = Specification(ident)
		newspec = Specification(Specification.newIdent())
		newspec.jsonData = copy.deepcopy(oldspec.jsonData)
		if (codename != None):
			newspec.jsonData['codename'] = codename
		if (oldspec.isInstalled()):
			src = oldspec.getInstallPath()
			dst = newspec.getInstallPath()
			if (oldspec.jsonData['blendfile'] != '' and os.path.exists(os.path.join(src, oldspec.jsonData['blendfile']))):
				shutil.copy(os.path.join(src, oldspec.jsonData['blendfile']), os.path.join(dst, oldspec.jsonData['blendfile']))
			if (oldspec.jsonData['thumbfile'] != '' and os.path.exists(os.path.join(src, oldspec.jsonData['thumbfile']))):
				shutil.copy(os.path.join(src, oldspec.jsonData['thumbfile']), os.path.join(dst, oldspec.jsonData['thumbfile']))
		for k,v in oldspec.servos.items():
			s = Motion.Servo()
			s.jsonData = copy.copy(v.jsonData)
			s.jsonData['ident'] = newspec.jbIndex
			s.save()
			newspec.servos[s.jbIndex] = s
		for k,v in oldspec.motions.items():
			m = Motion.Motion()
			m.jsonData = copy.copy(v.jsonData)
			m.save()
			newspec.motions[m.jbIndex] = m
		for k,v in oldspec.motors.items():
			m = Motors.DcMotor()
			m.jsonData = copy.copy(v.jsonData)
			m.save()
			newspec.motors[m.jbIndex] = m
		for k,v in oldspec.steppers.items():
			s = Motors.StepperMotor()
			s.jsonData = copy.copy(v.jsonData)
			s.save()
			newspec.steppers[s.jbIndex] = s
		newspec.save()
		return newspec
	@staticmethod
	def deployPackage(tarfilename):
		""" unpack a specification package
		
		@param tarfilename
		"""
		fullpath = os.path.join(Specification.packagepath, tarfilename)
		if (not os.path.exists(fullpath)):
			return 'missing'
		pinfo = Specification.getPackageInfo(tarfilename)
		if (not 'codename' in pinfo.keys()):
			return 'failed'
		if (pinfo['installed']):
			return 'exists'
		tar = tarfile.open(fullpath, "r:gz")
		for t in tar.getmembers():
			parts = os.path.splitext(t.name)
			if (parts[0] == pinfo['ident'] and parts[1] == '.json'):
				#spec
				spec = Specification(pinfo['ident'])
				spec.jsonData = json.loads(tar.extractfile(t.name).read())
				super(Specification,spec).save() #save spec blob
				ipath = os.path.join(Specification.installpath, pinfo['ident'])
				if (not os.path.exists(ipath)):
					os.makedirs(ipath) #create install path
			elif ('servos/' in parts[0] and parts[1] == '.json'):
				#servo
				sid = parts[0].replace('servos/', '')
				if (sid in pinfo['servos'].keys()):
					servo = Motion.Servo(sid)
					servo.jsonData = json.loads(tar.extractfile(t.name).read())
					super(Motion.Servo, servo).save() #save servo blob
			elif ('motions/' in parts[0] and parts[1] == '.json'):
				#motion
				mid = parts[0].replace('motions/', '')
				if (mid in pinfo['motions'].keys()):
					motion = Motion.Motion(mid)
					motion.jsonData = json.loads(tar.extractfile(t.name).read())
					super(Motion.Motion, motion).save() #save motion blob
			elif ('motors/' in parts[0] and parts[1] == '.json'):
				#motors
				mid = parts[0].replace('motors/', '')
				if (mid in pinfo['motors'].keys()):
					motor = Motors.DcMotor(mid)
					motor.jsonData = json.loads(tar.extractfile(t.name).read())
					super(Motors.DcMotor, motor).save() #save motor blob
			elif ('steppers/' in parts[0] and parts[1] == '.json'):
				#steppers
				mid = parts[0].replace('steppers/', '')
				if (mid in pinfo['steppers'].keys()):
					stepper = Motors.StepperMotor(mid)
					stepper.jsonData = json.loads(tar.extractfile(t.name).read())
					super(Motors.StepperMotor, stepper).save() #save motor blob
			elif ((pinfo['blendfile'] != '' and t.name == pinfo['blendfile']) or (pinfo['thumbfile'] != '' and t.name == pinfo['thumbfile'])):
				#supporting file
				ipath = os.path.join(Specification.installpath, pinfo['ident'])
				if (not os.path.exists(ipath)):
					os.makedirs(ipath) #create install path
				tar.extract(t, ipath)
		tar.close()
		return 'unpacked'
	def __init__(self, index = None):
		""" Initializes the Specification object
		
		@param index
		"""
		super(Specification,self).__init__(index if index != None else Specification.currentIdent())
		if (not super(Specification,self).blobExists()):
			self.jsonData = {
				'codename': 'NewBot',
				'blendfile': '',
				'thumbfile': '',
				'imu': {
					'facing': 'up',
					'offset': 0
				},
				'servos': {},
				'motions': {},
				'chains': {},
				'motors': {},
				'steppers': {},
				'keyboard': {},
				'locked': False
			}
			self.init()
			self.save()
		else:
			self.init()
	def init(self):
		""" setup object attributes
		"""
		self.servos = JsonBlob.JsonBlob.hydrate('Motion', 'Servo', self.jsonData['servos'].keys())
		self.motions = JsonBlob.JsonBlob.hydrate('Motion', 'Motion', self.jsonData['motions'].keys())
		self.chains = self.jsonData['chains']
		self.motors = JsonBlob.JsonBlob.hydrate('Motors', 'DcMotor', self.jsonData['motors'].keys()) if 'motors' in self.jsonData.keys() else {}
		self.steppers = JsonBlob.JsonBlob.hydrate('Motors', 'StepperMotor', self.jsonData['steppers'].keys()) if 'steppers' in self.jsonData.keys() else {}
		self.keyboard = self.jsonData['keyboard']
		self.imu = self.jsonData['imu']
	def save(self):
		""" override of JsonBlob.save
		serializes servos, motions amd motors before saving
		"""
		self.jsonData['servos'] = { k : v.jsonData for k, v in self.servos.items() }
		self.jsonData['motions'] = { k : v.jsonData for k, v in self.motions.items() }
		self.jsonData['motors'] = { k : v.jsonData for k, v in self.motors.items() }
		self.jsonData['steppers'] = { k : v.jsonData for k, v in self.steppers.items() }
		super(Specification,self).save()
		if (not self.isInstalled()):
			os.makedirs(self.getInstallPath())
	def delete(self):
		""" delete specification
		"""
		if (self.isInstalled()):
			shutil.rmtree(self.getInstallPath())
		for s in self.servos.values():
			s.delete()
		for m in self.motions.values():
			m.delete()
		for m in self.motors.values():
			m.delete()
		for s in self.steppers.values():
			s.delete()
		super(Specification,self).delete()
	def change(self, newident):
		""" activates a specification
		
		@param newident
		"""
		if (self.isInstalled(newident)):
			self.jbIndex = newident
			self.reload()
			self.init()
			Setting.set('spec_active_ident', newident)
	def getInstallPath(self):
		""" gets the path for installed specifications
		"""
		return os.path.join(Specification.installpath, self.jbIndex)
	def isInstalled(self, ident = None):
		""" determine whether a spec exists
		
		@param ident
		"""
		if (ident != None):
			return os.path.exists(os.path.join(Specification.installpath, ident))
		return os.path.exists(self.getInstallPath())
	def getPackagePath(self):
		""" gets the path for spec packages
		"""
		return os.path.join(Specification.packagepath, '{}.tar.gz'.format(self.jbIndex))
	def isPackaged(self):
		""" checks for spec package
		"""
		return os.path.exists(self.getPackagePath())
	def getPackageTimestamp(self):
		""" gets the modified time for a package file
		"""
		return os.path.getmtime(self.getPackagePath())
	def refreshServos(self):
		""" refresh servos
		"""
		if (any(self.servos)):
			for k, v in self.servos.items():
				v.reload()
	def refreshMotors(self):
		if (any(self.motors)):
			for k, v in self.motors.items():
				v.reload()
		if (any(self.steppers)):
			for k, v in self.steppers.items():
				v.reload()
	def stopMotors(self):
		running = False
		if (any(self.motors)):
			for k, v in self.motors.items():
				if (v.running):
					running = True
					v.stop()
		if (any(self.steppers)):
			for k, v in self.steppers.items():
				if (v.running):
					running = True
					v.stop()
		if (running):
			Motors.DcMotor.CleanupGpio() #only cleanup if one or more motors were running
	def getMotionId(self, name):
		""" gets a motion id from name
		
		@param name
		"""
		for k, v in self.motions.items():
			if (v.jsonData['name'] == name):
				return k
		return None
	def getActiveKeyMap(self):
		""" gets the active keymap
		"""
		try:
			self.activemap
		except:
			amap = [x for x in self.keyboard.values() if x['active']]
			if (any(amap)):
				self.activemap = amap[0]
		return self.activemap if (hasattr(self,'activemap')) else None
	def getKeyMapping(self, hex):
		""" gets key mappings for given hex
		
		@param hex
		"""
		map = self.getActiveKeyMap()
		if (map != None and 'mappings' in map.keys()):
			if (any(map['mappings'])):
				return [ x for x in map['mappings'].values() if x['hex'] == hex ]
		return []
	def generatePackage(self):
		""" generate a package from a specification
		"""
		tar = tarfile.open(self.getPackagePath(), "w:gz")
		if (self.jsonData['blendfile'] != '' and os.path.exists(os.path.join(self.getInstallPath(), self.jsonData['blendfile']))):
			tar.add(os.path.join(self.getInstallPath(), self.jsonData['blendfile']), self.jsonData['blendfile']) #add blend file
		if (self.jsonData['thumbfile'] != '' and os.path.exists(os.path.join(self.getInstallPath(), self.jsonData['thumbfile']))):
			tar.add(os.path.join(self.getInstallPath(), self.jsonData['thumbfile']), self.jsonData['thumbfile']) #add thumb file
		for s in self.servos.values():
			tar.add(s.getRowPath(), os.path.join('servos', s.getRowFileName())) #add servo blob
		for m in self.motions.values():
			tar.add(m.getRowPath(), os.path.join('motions', m.getRowFileName())) #add motion blob
		for m in self.motors.values():
			tar.add(m.getRowPath(), os.path.join('motors', m.getRowFileName())) #add motor blob
		for s in self.steppers.values():
			tar.add(s.getRowPath(), os.path.join('steppers', s.getRowFileName())) #add stepper blob
		tar.add(self.getRowPath(), self.getRowFileName()) #spec blob
		tar.close()