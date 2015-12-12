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
import os, sys, uuid, json

class JsonBlob(object):
	cwd = os.getcwd()
	basepath = os.path.join(cwd,'files', 'jsonblob')
	indexpath = os.path.join(basepath, 'index.json')
	constructors = {}
	indexexists = False
	indexed = False
	index = {}
	@staticmethod
	def reindex(force = False):
		'''
		collects information about available blobs from the file system
		'''
		if (not os.path.exists(JsonBlob.basepath)):
			os.makedirs(JsonBlob.basepath)
		if (os.path.exists(JsonBlob.indexpath)):
			JsonBlob.indexexists = True
		
		if (force == False and JsonBlob.indexexists):
			f = open(JsonBlob.indexpath, 'r')
			JsonBlob.index = json.loads(f.read())
			f.close()
		else:
			mods =  [ x for x in os.listdir(JsonBlob.basepath) if not 'index' in x ]
			for m in mods:
				if (os.path.isdir(os.path.join(JsonBlob.basepath, m))):
					JsonBlob.index[m] = { 'module': m, 'classes': {} }
					classes = [ x for x in os.listdir(os.path.join(JsonBlob.basepath, m)) if not 'index' in x ]
					for c in classes:
						if (os.path.isdir(os.path.join(JsonBlob.basepath, m, c))):
							JsonBlob.index[m]['classes'][c] = { 'class': c, 'rows': [] }
							rows = [ x for x in os.listdir(os.path.join(JsonBlob.basepath, m, c)) if '.json' in x ]
							for row in rows:
								splitrow = os.path.splitext(row)
								if (len(splitrow) == 2 and splitrow[1] == '.json'):
									JsonBlob.index[m]['classes'][c]['rows'].append(splitrow[0])
			f = open(JsonBlob.indexpath, 'wb')
			f.write(json.dumps(JsonBlob.index))
			f.close()
		JsonBlob.indexed = True
	@staticmethod
	def find(jbModule, jbType, jbIndex):
		'''
		returns the saved data or an empty dict
		'''
		typepath = os.path.join(JsonBlob.basepath, jbModule, jbType)
		if (jbIndex != None and os.path.exists(typepath)):
			rowpath = os.path.join(typepath,jbIndex + '.json')
			if (os.path.exists(rowpath)):
				f = open(rowpath, 'r')
				data = json.loads(f.read())
				f.close()
				return data
		return {}
	@staticmethod
	def all(jbModule = None, jbType = None):
		'''
		returns a dict of saved objects (keyed by jbIndex) or empty dict
		'''
		JsonBlob.reindex(not JsonBlob.indexed)
		if (jbModule != None and jbType != None):
			if (jbModule in JsonBlob.index.keys() and jbType in JsonBlob.index[jbModule]['classes'].keys()):
				return JsonBlob.hydrate(jbModule, jbType, JsonBlob.index[jbModule]['classes'][jbType]['rows'])
		return {}
	@staticmethod
	def hydrate(jbModule = None, jbType = None, ids = []):
		'''
		builds a dict of instantiated objects
		'''
		res = {}
		if (jbModule in JsonBlob.index.keys()):
			if (jbType in JsonBlob.index[jbModule]['classes']):
				try:
					JsonBlob.constructors[jbModule]
				except:
					JsonBlob.constructors[jbModule] = {'object': __import__(jbModule), 'classes': {}}
				try:
					JsonBlob.constructors[jbModule]['classes'][jbType]
				except:
					JsonBlob.constructors[jbModule]['classes'][jbType] = getattr(JsonBlob.constructors[jbModule]['object'],jbType)
				if (any(JsonBlob.index[jbModule]['classes'][jbType]['rows']) and any(ids)):
					for id in ids:
						res[id] = JsonBlob.constructors[jbModule]['classes'][jbType](id)
		return res
	def __init__(self, index = None, autoload = True):
		'''
		configures JsonBlob settings and loads any saved data for this jbIndex
		'''
		self.jbModule = type(self).__module__
		self.jbType = type(self).__name__
		self.jbIndex = index if index != None else str(uuid.uuid4())
		if (autoload):
			self.jsonData = JsonBlob.find(self.jbModule, self.jbType, self.jbIndex)
	def reload(self):
		'''
		reinitializes the jsonData
		'''
		self.jsonData = JsonBlob.find(self.jbModule, self.jbType, self.jbIndex)
	def save(self):
		'''
		saves the current jsonData
		'''
		typepath = self.getTypePath()
		if (not os.path.exists(typepath)):
			os.makedirs(typepath)
		f = open(self.getRowPath(), 'wb')
		f.write(json.dumps(self.jsonData))
		f.close()
		JsonBlob.reindex(force=True)
	def delete(self):
		'''
		deletes any saved data
		'''
		os.remove(self.getRowPath())
		JsonBlob.reindex(force=True)
	def blobExists(self):
		'''
		checks whether saved data exists for this object
		'''
		return os.path.exists(self.getRowPath())
	def getModulePath(self):
		'''
		returns the full file path for the module directory
		'''
		return os.path.join(JsonBlob.basepath, self.jbModule)
	def getTypePath(self):
		'''
		returns the full file path for the type directory
		'''
		return os.path.join(JsonBlob.basepath, self.jbModule, self.jbType)
	def getRowPath(self):
		'''
		returns the full file path for the object data
		'''
		return os.path.join(JsonBlob.basepath, self.jbModule, self.jbType, self.jbIndex + '.json')
	def getRowFileName(self):
		'''
		returns the file name for the object
		'''
		return self.jbIndex + '.json'