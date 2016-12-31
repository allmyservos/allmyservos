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
import re, json, time, datetime, tarfile, os
from __bootstrap import AmsEnvironment
from copy import copy

## Metrics are variables which can archive 
class Metric(object):
	def __init__(self, name, history = 0, archive = True, batch = 10):
		""" Initializes a Metric object
		A metric is like a variable but it collects changes and saves them in batches to an archive in CSV format. Older archives are compressed and added to cold storage.
		This was designed to have as smaller footprint on CPU and RAM as possible while still recording every historic value
		
		@param name - should be unique to each instance of the Metric class - characters which cannot be used as directory names will be stripped or replaced
		@param history - the amount of time in milliseconds used to retain values in memory. 0 = no previous values, -1 = all previous values, 1000 = the last seconds worth
		@param archive - create an archive of historic values for later examination
		@param batch
		"""
		self.name = self.__cleanseName(name)
		self.history = history
		self.__archive = archive
		self.__batch = batch
		self.__coldstored = False
		self.now = lambda: int(round(time.time() * 1000))
		self.__values = []
		try:
			Metric.metrics
		except:
			Metric.metrics = {}
		try:
			Metric.__session
		except:
			Metric.__session = {}
			Metric.__session['date'] = datetime.date.today()
			Metric.filebase = AmsEnvironment.FilePath()
			Metric.__session['archivepath'] = os.path.join(Metric.filebase, 'archive')
			Metric.__session['archivepattern'] = re.compile(r'(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)-(?P<name>.+)\.csv')
			Metric.__session['coldpattern'] = re.compile(r'(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+).tar.gz')
			Metric.__session['datapattern'] = re.compile(r'(?P<t>\d+),(?P<dt>\w+),(?P<v>.*)')
			Metric.__session['coldfolder'] = 'coldstorage'
			Metric.__session['coldstored'] = False
			Metric.__session['coldpath'] = os.path.join(Metric.__session['archivepath'], Metric.__session['coldfolder'])
			if not os.path.exists(Metric.__session['coldpath']):
				os.makedirs(Metric.__session['coldpath'])
		try:
			Metric.metrics[self.name]
		except:
			Metric.metrics[name] = self
		Metric.index()
	@staticmethod
	def getIndex():
		""" gets the complete metrics index
		
		@return dict
		"""
		return Metric.__session['index']
	@staticmethod
	def index(force = False):
		"""internal use only
		indexes archive names and temperature (hot/cold) by date
		
		@param force
		"""
		firstrun = False
		try:
			Metric.__session['index']
		except:
			firstrun = True
		if(force or firstrun):
			Metric.__session['index'] = { 'sessions': {}, 'metrics': {} }
			for a in Metric.__listArchives():
				Metric.__indexArchive(a,False)
			for a in Metric.__listColdArchives():
				Metric.__indexArchive(a,True)
			for k, v in Metric.__session['index']['sessions'].iteritems():
				for a in v:
					try:
						Metric.__session['index']['metrics'][a[0]['name']]
					except:
						Metric.__session['index']['metrics'][a[0]['name']] = []
					Metric.__session['index']['metrics'][a[0]['name']].append([k, a[0], a[1]])
	@staticmethod
	def __indexArchive(archive, cold = False):
		""" creates index entry for an archive
		
		@param archive
		@param old
		"""
		datestring = '{0}-{1}-{2}'.format(archive['year'], archive['month'], archive['day'])
		try:
			Metric.__session['index']['sessions'][datestring]
		except:
			Metric.__session['index']['sessions'][datestring] = []
		Metric.__session['index']['sessions'][datestring].append([archive, cold])
	@staticmethod
	def __listArchives(name = None):
		""" returns a list of segmented archive names, found in the archives folder
		
		@param name
		
		@return list
		"""
		files = os.listdir(Metric.__session['archivepath'])
		files = [ x for x in files if Metric.__session['archivepattern'].match(x) ]
		if(name):
			files = [ x for x in files if x.find(name+'.csv') > -1 ]
		return map(Metric.__unpackArchiveName,files)
	@staticmethod
	def __listColdArchives(name = None):
		""" returns a list of archives found in any date-named tar.gz files in the coldstorage folder
		
		@param name
		
		@return list
		"""
		coldarchives = []
		files = os.listdir(Metric.__session['coldpath'])
		for f in files:
			coldarchives.extend(Metric.__warmArchives(f, name))
		return map(Metric.__unpackArchiveName,coldarchives)
	@staticmethod
	def __unpackArchiveName(name):
		""" splits an archive name (e.g. 2014-01-01-[name].csv) into a dict
		
		@param name
		
		@return dict or None
		"""
		groups = Metric.__session['archivepattern'].match(name)
		try:
			return { 'year': groups.group('year'), 'month': groups.group('month'), 'day': groups.group('day'), 'name': groups.group('name') }
		except:
			return None
	@staticmethod
	def __unpackColdArchiveName(name):
		""" splits a compressed archive name (e.g. 2014-01-01.tar.gz) into a dict
		
		@param name
		
		@return dict or None
		"""
		groups = Metric.__session['coldpattern'].match(name)
		try:
			return { 'year': groups.group('year'), 'month': groups.group('month'), 'day': groups.group('day') }
		except:
			return None
	@staticmethod
	def __warmArchives(coldfile, name = None):
		""" returns a complete list of archives within a given tar file
		
		@param coldfile
		@param name
		
		@return list
		"""
		tarpath = os.path.join(Metric.__session['coldpath'], coldfile)
		try:
			tar = tarfile.open(tarpath, "r:gz")
			names = [ x for x in tar.getnames() if Metric.__session['archivepattern'].match(x) ]
			tar.close()
			if(name):
				names = [ x for x in names if x.find(name) > 0 ]
		except:
			names = []
		return names
	
	def getInfo(self):
		""" get metric info
		
		@return dict
		"""
		return { 'name': self.name, 'history': self.history, 'archive': self.__archive, 'batch': self.__batch, 'type': self.__getType() }
	def __cleanseName(self, name):
		""" ensures metric name is suitable for directory use
		
		@return str
		"""
		badstring = r'\/:*?"<>|'
		if(badstring.find(name[0]) > -1):
			name = name[1:]
		name = re.sub(badstring, '', name)
		return name
	def __getType(self):
		""" gets the value type
		
		@return str
		"""
		mytype = 'TBD'
		try:
			mytype = self.__values[-1].datatype
		except:
			pass
		return mytype
	@property
	def value(self):
		""" gets the most up to date value of this metric
		usage: x = metric.value
		
		@return value
		"""
		v = None
		try:
			v = self.__values[-1]
		except:
			return None
		return v.datavalue
	@value.setter
	def value(self, value):
		""" sets the most up to date value and performs maintenance
		metric.value = x
		"""
		if(isinstance(value, dict)):
			datatype = 'dict'
			strvalue = json.dumps(value)
		elif(isinstance(value, list)):
			datatype = 'list'
			strvalue = json.dumps(value)
		elif(isinstance(value, tuple)):		
			datatype = 'tuple'
			strvalue = json.dumps(value)
		elif(isinstance(value, bool)):
			datatype = 'bool'
			strvalue = str(value)
		elif(isinstance(value, int)):
			datatype = 'int'
			strvalue = str(value)
		elif(isinstance(value, long)):
			datatype = 'long'
			strvalue = str(value)
		elif(isinstance(value, float)):
			datatype = 'float'
			strvalue = str(value)
		elif(isinstance(value, complex)):
			datatype = 'complex'
			strvalue = str(value)
		else:
			datatype = 'string'
			strvalue = str(value)
		now = self.now()
		self.__values.append(MetricValue(self.name, now, datatype, strvalue, value, self.__archive, self.__batch))
		self.__maintain(now)
	def hotValues(self):
		""" gets all values in memory
		x = metric.hotValues()
		
		@return list
		"""
		return copy(self.__values)
	def clearValues(self):
		""" empties the list of values
		metric.clearValues()
		"""
		self.__values = []
	def loadValues(self, start = None, end = None, resolution = 'hour'):
		""" load historic values for this metric between the given times
		metric.loadValues(time.time(),time.time())
		start - time.time() float - seconds since unix epoc (subtract seconds for earlier values)
		end - time.time() float - seconds since unix epoc (subtract seconds for earlier values)
		
		@param start
		@param end
		@param resolution
		"""
		resolutions = ['hour','minute','second','millisecond']
		if(resolution in resolutions):
			ikeys = Metric.__session['index']['sessions'].keys()
			ikeys.sort()
			if(start == None):
				start = time.time()
			startdate = datetime.datetime.fromtimestamp(start).date()
			if(end == None):
				end = time.time()
			enddate = datetime.datetime.fromtimestamp(end).date()
			for i in ikeys:
				d = datetime.datetime.strptime(i,'%Y-%m-%d').date()
				if(d >= startdate and d <= enddate):
					for a in Metric.__session['index']['sessions'][i]:
						if(a[0]['name'] == self.name):
							if(a[1] == False):
								self.__loadWarm(a[0], start, end, resolution)
							else:
								self.__loadCold(a[0], start, end, resolution)
	def hasValues(self, start, end):
		""" check for valies in time range
		
		@param start
		@param end
		
		@return bool
		"""
		ikeys = Metric.__session['index']['sessions'].keys()
		ikeys.sort()
		startdate = datetime.datetime.fromtimestamp(start).date()
		enddate = datetime.datetime.fromtimestamp(end).date()
		found = False
		for i in ikeys:
			d = datetime.datetime.strptime(i,'%Y-%m-%d').date()
			if(d >= startdate and d <= enddate):
				for a in Metric.__session['index']['sessions'][i]:
					if(a[0]['name'] == self.name):
						if(a[1] == False):
							if(self.__findWarm(a[0], start, end)):
								found = True
								break
								break
						else:
							if(self.__findCold(a[0], start, end)):
								found = True
								break
								break
		return found
	def __cast(self, val):
		""" casts a MetricValue to the relevant python data type
		
		@param val
		
		@return value
		"""
		if(val.datatype == 'dict'):
			return json.loads(val.strvalue)
		elif(val.datatype == 'list'):
			return json.loads(val.strvalue)
		elif(val.datatype == 'tuple'):
			return json.loads(val.strvalue)
		elif(val.datatype == 'bool'):
			if(val.strvalue.lower() == 'true'):
				return True
			else:
				return False
		elif(val.datatype == 'int'):
			return int(val.strvalue)
		elif(val.datatype == 'long'):
			return long(val.strvalue)
		elif(val.datatype == 'float'):
			return float(val.strvalue)
		elif(val.datatype == 'complex'):
			return complex(val.strvalue)
		else:
			return str(val.strvalue)
	def __recast(self, strvalue, datatype):
		""" casts a string to the supplied python data type
		
		@param strvalue
		@param datatype
		
		@return value
		"""
		if(datatype == 'dict'):
			return json.loads(strvalue)
		elif(datatype == 'list'):
			return json.loads(strvalue)
		elif(datatype == 'tuple'):
			return json.loads(strvalue)
		elif(datatype == 'bool'):
			if(strvalue.lower() == 'true'):
				return True
			else:
				return False
		elif(datatype == 'int'):
			return int(strvalue)
		elif(datatype == 'long'):
			return long(strvalue)
		elif(datatype == 'float'):
			return float(strvalue)
		elif(datatype == 'complex'):
			return complex(strvalue)
		else:
			return str(strvalue)
	def __loadWarm(self, archive, start, end, resolution):
		""" loads a warm archive from /archives
		
		@param archive
		@param start
		@param end
		@param resolution
		"""
		filename = '{0}/{1}-{2}-{3}-{4}.csv'.format(Metric.__session['archivepath'], archive['year'], archive['month'], archive['day'], archive['name'])
		self.__parseArchive(filename, start, end, resolution)
	def __loadCold(self, archive, start, end, resolution):
		""" loads a cold archive from /archives/coldstorage/[date].tar.gz
		
		@param archive
		@param start
		@param end
		@param resolution
		"""
		coldfile = '{0}/{1}-{2}-{3}.tar.gz'.format(Metric.__session['coldpath'], archive['year'], archive['month'], archive['day'])
		filename = '{0}-{1}-{2}-{3}.csv'.format(archive['year'], archive['month'], archive['day'], archive['name'])
		self.__warmArchive(coldfile, filename, start, end, resolution)
	def __findWarm(self, archive, start, end):
		""" determines whether warm values exist in timespan
		
		@param archive
		@param start
		@param end
		
		@return bool
		"""
		filename = '{0}/{1}-{2}-{3}-{4}.csv'.format(Metric.__session['archivepath'], archive['year'], archive['month'], archive['day'], archive['name'])
		f = open(filepath, 'r')
		for l in f:
			matches = Metric.__session['datapattern'].match(l)
			if(matches):
				ts = float(matches.group('t'))/1000
				if(ts >= start and ts <= end):
					f.close()
					return True
		f.close()
		return False
	def __findCold(self, archive, start, end):
		""" determines whether cold values exist in timespan
		
		@param archive
		@param start
		@param end
		
		@return bool
		"""
		coldfile = '{0}/{1}-{2}-{3}.tar.gz'.format(Metric.__session['coldpath'], archive['year'], archive['month'], archive['day'])
		filename = '{0}-{1}-{2}-{3}.csv'.format(archive['year'], archive['month'], archive['day'], archive['name'])
		tar = tarfile.open(coldfile, "r:gz")
		f=tar.extractfile(filename)
		found = False
		for l in f:
			matches = Metric.__session['datapattern'].match(l)
			if(matches):
				ts = float(matches.group('t'))/1000
				if(ts >= start and ts <= end):
					found = True
					break
				elif(ts > end):
					break
		return found
	def __parseArchive(self, filepath, start, end, resolution):
		""" collects data from an uncompressed archive
		
		@param filepath
		@param start
		@param end
		@param resolution
		"""
		increments = { 'hour': 3600.0, 'minute': 60.0, 'second': 1.0, 'millisecond': 0.001 }
		nextts = 0
		f = open(filepath, 'r')
		for l in f:
			matches = Metric.__session['datapattern'].match(l)
			if(matches):
				ts = float(matches.group('t'))/1000
				if(ts >= start and ts <= end and ts >= nextts): #if the timestamp for the value is between the start and end, and a value for this resolution hasn't been returned yet
					nextts = ts + increments[resolution]
					self.__values.append(self.__parseValue(matches))
		f.close()
	def __warmArchive(self, coldfile, archive, start, end, resolution):
		""" collects data from a compressed archive
		
		@param coldfile
		@param archive
		@param start
		@param end
		@param resolution
		"""
		increments = { 'hour': 3600.0, 'minute': 60.0, 'second': 1.0, 'millisecond': 0.001 }
		nextts = 0
		tar = tarfile.open(coldfile, "r:gz")
		f=tar.extractfile(archive)
		for l in f:
			matches = Metric.__session['datapattern'].match(l)
			if(matches):
				ts = float(matches.group('t'))/1000
				if(ts >= start and ts <= end and ts >= nextts):
					nextts = ts + increments[resolution]
					self.__values.append(self.__parseValue(matches))
		tar.close()
	def __parseValue(self, value):
		""" generic function for converting pattern matches into MetricValue objects
		
		@param value
		"""
		return MetricValue(self.name, long(value.group('t')), str(value.group('dt')), str(value.group('v')), self.__recast(str(value.group('v')), str(value.group('dt'))))
	def __maintain(self, now):
		""" archives values from memory and triggers cold storage (at the beginning of each session)
		
		@param now
		"""
		v = self.__values
		if(self.__archive and not hasattr(v[-1], 'saved')):
			v[-1].saved = True
			v[-1].archive()
		if(self.history > -1 and v[0].timestamp < now - self.history):
			del(self.__values[0])
		self.__coldstore()
	def __coldstore(self):
		""" finds older archives for compression
		"""
		if(not Metric.__session['coldstored']):
			Metric.__session['coldstored'] = True
			tochill = [ x for x in Metric.__listArchives(self.name) if self.__isChillable(x) ]
			self.__chillArchives(tochill)
	def __isChillable(self, archive):
		""" determines which archives are chillable (yesterday or older)
		
		@param archive
		
		@return bool
		"""
		if(archive != None):
			datestring = '{0}-{1}-{2}'.format(archive['year'], archive['month'], archive['day'])
			archivedate = datetime.datetime.strptime(datestring,'%Y-%m-%d').date()
			return True if archivedate < Metric.__session['date'] else False
		return False
	def __chillArchives(self, archives = []):
		""" indexes chillable archives by date so they can be compressed in a single transaction per date
		then performs compression
		
		@param archives list
		"""
		if(len(archives) > 0):
			dates = {}
			for a in archives:
				datestring = '{0}-{1}-{2}'.format(a['year'], a['month'], a['day'])
				try:
					dates[datestring]
				except:
					dates[datestring] = {}
				f = '{0}/{1}-{2}-{3}-{4}.csv'.format(Metric.__session['archivepath'],a['year'],a['month'],a['day'], a['name'])
				n = '{0}-{1}-{2}-{3}.csv'.format(a['year'],a['month'],a['day'], a['name'])
				dates[datestring].update({ n : f })
			for k, v in dates.iteritems():
				tarpath = '{0}/{1}.tar.gz'.format(Metric.__session['coldpath'], k)
				tar = tarfile.open(tarpath, "w:gz")
				if(len(v) > 0):
					for name, file in v.iteritems():
						try:
							tar.add(file,name)
							os.remove(file)
						except:
							pass
					Metric.index(True)
				tar.close()
## Metric values are self archiving with a timestamp
class MetricValue(object):
	def __init__(self, name = '', timestamp = 0, datatype = '', strvalue = '', datavalue = None, archive = True, batch = 10):
		""" Initializes MetricValue object
		In-memory objects which hold historic values of a metric
		they are also responsible for archiving themselves
		"""
		self.name = name
		self.timestamp = timestamp
		self.datatype = datatype
		self.strvalue = strvalue
		self.datavalue = datavalue
		self.__archive = archive
		self.__batch = batch
		try:
			MetricValue.queue
		except:
			MetricValue.queue = {}
			MetricValue.counters = {}
		try:
			MetricValue.__session
		except:
			MetricValue.__session = {}
			MetricValue.filebase = AmsEnvironment.FilePath()
			MetricValue.__session['date'] = datetime.date.today()
			MetricValue.__session['path'] = os.path.join(MetricValue.filebase, 'archive')
			MetricValue.__session['header'] = 't,dt,v\r\n'
			MetricValue.__session['template'] = '{0},{1},{2}\r\n'
			MetricValue.__session['writing'] = False
			if not os.path.exists(MetricValue.__session['path']):
				os.makedirs(MetricValue.__session['path'])
		self.__session['file'] = '{0}-{1}.csv'.format(MetricValue.__session['date'],self.name)
		self.__session['abs'] = os.path.join(MetricValue.__session['path'], self.__session['file'])
		try:
			MetricValue.queue[self.name]
		except:
			MetricValue.queue[self.name] = []
			MetricValue.counters[self.name] = 0
			if self.__archive and not os.path.exists(self.__session['abs']):
				f = open(self.__session['abs'], 'w')
				f.write(MetricValue.__session['header'])
				f.close()
	def archive(self):
		""" a metric triggers this function but it only writes to the file once 10 values have been collected
		metricvalue.archive()
		"""
		MetricValue.queue[self.name].append(MetricValue.__session['template'].format(self.timestamp,self.datatype,self.strvalue))
		MetricValue.counters[self.name] += 1
		if(self.__archive and MetricValue.counters[self.name] >= self.__batch and not MetricValue.__session['writing']):
			MetricValue.__session['writing'] = True
			f = open(self.__session['abs'], 'a')
			f.write(''.join(MetricValue.queue[self.name]))
			MetricValue.queue[self.name] = []
			MetricValue.counters[self.name] = 0
			f.close()
			MetricValue.__session['writing'] = False