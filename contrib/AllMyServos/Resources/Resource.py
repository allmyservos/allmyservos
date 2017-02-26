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
import psutil, threading, time, commands
from Scheduler import *
from Metric import *
from Setting import *

## Track system resources
class Resources(object):
	def __init__(self, scheduler = None):
		""" Initialize the Resources object
		
		@param scheduler
		"""
		if(scheduler != None):
			self.scheduler = scheduler
		else:
			self.scheduler = Scheduler.GetInstance()
		self.s = Setting()
		self.metrics = {}
		self.initCpu()
		self.initMemory()
		self.initTemps()
		self.initDisks()
		self.initProcesses()
		self.initThreads()
		self.initNetwork()
	def initCpu(self):
		""" init cpu tracking
		"""
		self.metrics['cpu_percent'] = Resource('cpu_percent', 4000, Setting.get('resource_archive_cpu',False), 50)
		self.scheduler.addTask('cpu_watcher', self.cpu, interval = 0.4)
	def initMemory(self):
		""" init memory tracking
		"""
		self.metrics['memory'] = Resource('memory', 20000, Setting.get('resource_archive_mem',False))
		self.scheduler.addTask('memory_watcher', self.memory, interval = 10)
	def initTemps(self):
		""" init temperature tracking
		"""
		self.metrics['temperature'] = Resource('temperature', 0, Setting.get('resource_archive_temp',False))
		self.scheduler.addTask('temperature_watcher', self.temperature, interval = 10)
	def initDisks(self):
		""" init disk tracking
		"""
		self.metrics['disks'] = Resource('disks', 10000, Setting.get('resource_archive_disks',False))
		self.scheduler.addTask('disk_watcher', self.disks, interval = 5)
	def initProcesses(self):
		""" init process tracking
		"""
		self.metrics['processes'] = Resource('processes', 2000, Setting.get('resource_archive_processes',False))
		self.metrics['processcount'] = Resource('processcount', 20000, Setting.get('resource_archive_processes',False))
		self.scheduler.addTask('process_watcher', self.processes, interval = 10)
	def initThreads(self):
		""" init thread tracking
		"""
		self.metrics['threads'] = Resource('threads', 2000, Setting.get('resource_archive_threads',False))
		self.metrics['threadcount'] = Resource('threadcount', 20000, Setting.get('resource_archive_threads',False))
		self.scheduler.addTask('thread_watcher', self.threads, interval = 10)
	def initNetwork(self):
		""" init network tracking
		"""
		self.metrics['networksyswide'] = Resource('network_system_wide', 10000, Setting.get('resource_archive_net',False))
		self.metrics['network'] = Resource('network', 10000, Setting.get('resource_archive_net',False))
		self.scheduler.addTask('network_watcher', self.network, interval = 10)
	def cpu(self):
		""" track cpu
		"""
		try:
			self.metrics['cpu_percent'].value = float(psutil.cpu_percent(interval=0.4))
		except:
			pass
	def memory(self):
		""" track memory
		"""
		try:
			vmem = psutil.virtual_memory()
			smem = psutil.swap_memory()
			mem = { 'vmem': vmem.percent, 'smem': smem.percent}
			history = self.metrics['memory'].hotValues()
			if(any(history)):
				if(cmp(history[-1].datavalue,mem) != 0):
					self.metrics['memory'].value = mem
			else:
				self.metrics['memory'].value = mem
		except Exception,e:
			print(e)
	def temperature(self):
		""" track temp
		"""
		self.metrics['temperature'].value = {
			'cpu': self.__get_cpu_temp(),
			'gpu': self.__get_gpu_temp()
		}
	def disks(self):
		""" track disks
		"""
		try:
			diskdata = {}
			for p in psutil.disk_partitions():
				usage = psutil.disk_usage(p.mountpoint)
				diskdata[p.device] = { 'mountpoint': p.mountpoint, 'fstype': p.fstype, 'opts': p.opts, 'total': usage.total, 'used': usage.used, 'free': usage.free, 'percent': usage.percent}
			history = self.metrics['disks'].hotValues()
			if(any(history)):
				if(cmp(history[-1].datavalue,diskdata) != 0):
					self.metrics['disks'].value = diskdata
			else:
				self.metrics['disks'].value = diskdata
		except:
			pass
	def processes(self):
		""" track processes
		"""
		try:
			pids = psutil.pids()
			self.metrics['processcount'].value = len(pids)
			history = self.metrics['processcount'].hotValues()
			if(len(history) > 1):
				if(history[-1].datavalue != self.metrics['processcount'].value):
					self.metrics['processes'].value = self.__formatProcessData(pids)
			else:
				self.metrics['processes'].value = self.__formatProcessData(pids)
		except:
			pass
	def __formatProcessData(self, pids):
		""" format process data
		
		@param pids
		
		@return dict
		"""
		processdata = {}
		for pid in pids:
			p = psutil.Process(pid)
			tmp = p.as_dict(attrs=['pid', 'name', 'username'])
			processdata[tmp['name']] = tmp
		return processdata
	def threads(self):
		""" track threads
		"""
		try:
			self.metrics['threadcount'].value = threading.activeCount()
			history = self.metrics['threadcount'].hotValues()
			if(len(history) > 1):
				if(history[-1].datavalue != self.metrics['threadcount'].value):
					self.metrics['threads'].value = self.__formatThreadData(threading.enumerate())
			else:
				self.metrics['threads'].value = self.__formatThreadData(threading.enumerate())
		except:
			pass
	def __formatThreadData(self, threads):
		""" format thread data
		
		@return dict
		"""
		threaddata = {}
		for t in threads:
			threaddata['i{0}'.format(t.ident)] = { 'name': t.getName(), 'isdaemon': t.isDaemon(), 'isalive': t.isAlive() }
		return threaddata
	def network(self):
		""" track network
		"""
		syswide = psutil.net_io_counters()
		self.metrics['networksyswide'].value = { 'bytes_sent': syswide.bytes_sent, 'bytes_recv': syswide.bytes_recv, 'packets_sent': syswide.packets_sent, 'packets_recv' : syswide.packets_recv}
		history = self.metrics['networksyswide'].hotValues()
		if(len(history) > 1):
			old = history[-1].datavalue
			if(old['bytes_sent'] < syswide.bytes_sent or old['bytes_recv'] < syswide.bytes_recv):
				self.metrics['network'].value = self.__formatNetworkData(psutil.net_io_counters(pernic=True), psutil.net_connections())
		else:
			self.metrics['network'].value = self.__formatNetworkData(psutil.net_io_counters(pernic=True), psutil.net_connections())
	def __formatNetworkData(self, nics, conns):
		""" format network data
		
		@param nics
		@param conns
		
		@return dict
		"""
		networkdata = { 'nics': {}, 'conns': {}}
		for k,v in nics.iteritems():
			networkdata['nics'][k] = { 'bytes_sent': v.bytes_sent, 'bytes_recv': v.bytes_recv, 'packets_sent': v.packets_sent, 'packets_recv' : v.packets_recv, 'errin' : v.errin, 'errout' : v.errout, 'dropin' : v.dropin, 'dropout' : v.dropout }
		for i,c in enumerate(conns):
			networkdata['conns'][i] = { 'fd': c.fd, 'family': c.family, 'type': c.type, 'laddr': c.laddr, 'raddr': c.raddr, 'status': c.status, 'pid': c.pid }
		return networkdata
	def __get_cpu_temp(self):
		""" gets cpu temperature
		
		@return float
		"""
		tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
		cpu_temp = tempFile.read()
		tempFile.close()
		return float(cpu_temp)/1000
	def __get_gpu_temp(self):
		""" gets gpu temperature
		
		@return float
		"""
		gpu_temp = commands.getoutput( '/opt/vc/bin/vcgencmd measure_temp' ).replace( 'temp=', '' ).replace( '\'C', '' )
		return  float(gpu_temp)
## Sets up metric object for use with the resources class
class Resource(Metric):
	def __init__(self, name, history = 0, archive = True, batch = 10):
		""" Initialize the Resource object
		
		@param name
		@param history
		@param archive
		@param batch
		"""
		fullname = '{0}_{1}'.format('resource',name)
		super(Resource,self).__init__(fullname, history, archive, batch)
if __name__ == '__main__':
	resources = Resources()
	time.sleep(20)