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
import sys, os, shutil, distutils.core, traceback, uuid, tarfile, time, copy, errno, JsonBlob, Motion, Keyboard
from xml.dom import minidom
from xml.dom.minidom import Document
from Setting import *

class Specification(JsonBlob.JsonBlob):
	cwd = os.getcwd()
	basepath = os.path.join(cwd, 'specifications')
	installpath = os.path.join(basepath, 'installed')
	packagepath = os.path.join(basepath, 'packages')
	filebase = os.path.join(cwd, 'files')
	@staticmethod
	def currentIdent(new = False):
		specs = JsonBlob.JsonBlob.all('Specification','Specification')
		currentident = specs.keys()[0] if not new and any(specs) else Specification.newIdent() #first in index or new
		savedident = Setting.get('spec_active_ident', currentident) #get the active ident setting or default to first or new
		if not new and os.path.exists(os.path.join(Specification.installpath, savedident)):
			currentident = savedident #the saved ident refers to an existing specification so use it 
		elif not new:
			Setting.set('spec_active_ident', currentident) #update the saved active ident
		return currentident
	@staticmethod
	def newIdent():
		return str(uuid.uuid4())
	@staticmethod
	def listPackages():
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
		'''
		collects the spec data inside a package
		'''
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
		newspec.save()
		return newspec
	@staticmethod
	def deployPackage(tarfilename):
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
			elif ((pinfo['blendfile'] != '' and t.name == pinfo['blendfile']) or (pinfo['thumbfile'] != '' and t.name == pinfo['thumbfile'])):
				#supporting file
				ipath = os.path.join(Specification.installpath, pinfo['ident'])
				if (not os.path.exists(ipath)):
					os.makedirs(ipath) #create install path
				tar.extract(t, ipath)
		tar.close()
		return 'unpacked'
	def __init__(self, index = None):
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
				'keyboard': {},
				'locked': False
			}
			self.init()
			self.save()
		else:
			self.init()
	def init(self):
		self.servos = JsonBlob.JsonBlob.hydrate('Motion', 'Servo', self.jsonData['servos'].keys())
		self.motions = JsonBlob.JsonBlob.hydrate('Motion', 'Motion', self.jsonData['motions'].keys())
		self.chains = self.jsonData['chains']
		self.keyboard = self.jsonData['keyboard']
		self.imu = self.jsonData['imu']
	def save(self):
		self.jsonData['servos'] = { k : v.jsonData for k, v in self.servos.items() }
		self.jsonData['motions'] = { k : v.jsonData for k, v in self.motions.items() }
		super(Specification,self).save()
		if (not self.isInstalled()):
			os.makedirs(self.getInstallPath())
	def delete(self):
		if (self.isInstalled()):
			shutil.rmtree(self.getInstallPath())
		for s in self.servos.values():
			s.delete()
		for m in self.motions.values():
			m.delete()
		super(Specification,self).delete()
	def change(self, newident):
		if (self.isInstalled(newident)):
			self.jbIndex = newident
			self.reload()
			self.init()
			Setting.set('spec_active_ident', newident)
	def getInstallPath(self):
		return os.path.join(Specification.installpath, self.jbIndex)
	def isInstalled(self, ident = None):
		if (ident != None):
			return os.path.exists(os.path.join(Specification.installpath, ident))
		return os.path.exists(self.getInstallPath())
	def getPackagePath(self):
		return os.path.join(Specification.packagepath, '{}.tar.gz'.format(self.jbIndex))
	def isPackaged(self):
		return os.path.exists(self.getPackagePath())
	def getPackageTimestamp(self):
		return os.path.getmtime(self.getPackagePath())
	def refreshServos(self):
		if (any(self.servos)):
			for k, v in self.servos.items():
				v.reload()
	def getMotionId(self, name):
		for k, v in self.motions.items():
			if (v.jsonData['name'] == name):
				return k
		return None
	def getActiveKeyMap(self):
		try:
			self.activemap
		except:
			amap = [x for x in self.keyboard.values() if x['active']]
			if (any(amap)):
				self.activemap = amap[0]
		return self.activemap
	def getKeyMapping(self, hex):
		map = self.getActiveKeyMap()
		if ('mappings' in map.keys()):
			if (any(map['mappings'])):
				return [ x for x in map['mappings'].values() if x['hex'] == hex ]
		return []
	def generatePackage(self):
		tar = tarfile.open(self.getPackagePath(), "w:gz")
		if (self.jsonData['blendfile'] != '' and os.path.exists(os.path.join(self.getInstallPath(), self.jsonData['blendfile']))):
			tar.add(os.path.join(self.getInstallPath(), self.jsonData['blendfile']), self.jsonData['blendfile']) #add blend file
		if (self.jsonData['thumbfile'] != '' and os.path.exists(os.path.join(self.getInstallPath(), self.jsonData['thumbfile']))):
			tar.add(os.path.join(self.getInstallPath(), self.jsonData['thumbfile']), self.jsonData['thumbfile']) #add thumb file
		for s in self.servos.values():
			tar.add(s.getRowPath(), os.path.join('servos', s.getRowFileName())) #add servo blob
		for m in self.motions.values():
			tar.add(m.getRowPath(), os.path.join('motions', m.getRowFileName())) #add motion blob
		tar.add(self.getRowPath(), self.getRowFileName()) #spec blob
		tar.close()