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
import Tkinter, ttk, threading, platform, time, string
from Tkinter import *
from TkBlock import *
from TkDependencyManager import *
from TkGraphs import *
from Setting import *
from Scheduler import *

## UI for resources
class TkResourceManager(TkBlock):
	def __init__(self, parent, gui, **options):
		""" Initializes TkNetworkManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkResourceManager,self).__init__(parent, gui, **options)
		self.dm = TkDependencyManager(self.widget, {'package':'psutil', 'installer': 'pip', 'version': '3.3.0'}, 'Resource Manager', self.gui)
		if(not self.dm.installRequired()):
			self.gridrows = {}
			if(self.gui.scheduler != None):
				self.scheduler = self.gui.scheduler
			else:
				self.scheduler = Scheduler()
			self.resources = self.gui.getClass('Resource.Resources')(self.scheduler)
			self.tasksheight = 200 # sets the height of the tasks notebook
			self.last = { 'memory':0, 'disks':0, 'threads':0, 'processes':0, 'network':0 }
			if(Setting.get('resman_show_cpu',True)):
				self.addCpuManager()
			if(Setting.get('resman_show_tasks',True)):
				self.addTaskManager()
			if(Setting.get('resman_show_memory',True)):
				self.addMemoryManager()
			if(Setting.get('resman_show_temperature',True)):
				self.addTemperatureManager()
			if(Setting.get('resman_show_disk',True)):
				self.addDiskManager()
			self.addOptionManager()
		else:
			self.open()
			self.dm.addManager()
	
	#=== VIEWS ===#
	def addCpuManager(self):
		""" view - cpu ui
		"""
		row = 0
		self.cpuwidgets = {}
		self.gridrows['cpu'] = 0
		self.widgets['cpuframe'] = Frame(self.widget,bg=self.colours['bg'])
		self.widgets['cpuframe'].grid(column=0,row=row,sticky='EW')
		self.variables['cpupercentage'] = StringVar()
		self.variables['cpupercentage'].set(self.resources.metrics['cpu_percent'].value)
		self.cpuwidgets['cpulabel'] = Tkinter.Label(self.widgets['cpuframe'],text='CPU Usage', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.cpuwidgets['cpulabel'].grid(column=0,row=self.gridrows['cpu'],sticky='EW')
		self.gridrows['cpu'] += 1
		self.cpuwidgets['graph'] = TkLineGraph(self.widgets['cpuframe'], { }, {'bg': self.colours['bg'], 'fg': self.colours['fg'], 'line': self.colours['consolefg']}, height = 50, width = 150, yrange = { 'min': 0, 'max': 100}, pointlimit=20)
		self.cpuwidgets['graph'].widget.grid(column=0,row=self.gridrows['cpu'], sticky='EW')
		self.cpuwidgets['cpudata'] = Tkinter.Label(self.widgets['cpuframe'],textvariable=self.variables['cpupercentage'], bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], width=4)
		self.cpuwidgets['cpudata'].grid(column=1,row=self.gridrows['cpu'],sticky='EW')
		self.cpuwidgets['cpupercent'] = Tkinter.Label(self.widgets['cpuframe'],text='%', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.cpuwidgets['cpupercent'].grid(column=2,row=self.gridrows['cpu'],sticky='EW')
		self.scheduler.addTask('resman_cpu_pc', self.updateCpuPc, interval = 1)
		self.scheduler.addTask('resman_cpu_graph', self.updateCpuGraph, interval = 1)
	def updateCpuPc(self):
		""" util - update cpu percentage
		"""
		try:
			history = self.resources.metrics['cpu_percent'].hotValues()
			if(len(history) > 1):
				if(history[-1].datavalue != history[-2].datavalue):
					self.variables['cpupercentage'].set(self.resources.metrics['cpu_percent'].value)
			else:
				self.variables['cpupercentage'].set(self.resources.metrics['cpu_percent'].value)
		except:
			pass
	def updateCpuGraph(self):
		""" util - update cpu graph
		"""
		try:
			self.cpuwidgets['graph'].data = { x.timestamp : x.datavalue for x in self.resources.metrics['cpu_percent'].hotValues() }
			self.cpuwidgets['graph'].update()
		except:
			pass
	def addMemoryManager(self):
		""" view - memory ui
		"""
		row = 0
		self.gridrows['mem'] = 0
		self.widgets['memoryframe'] = Frame(self.widget,bg=self.colours['bg'])
		self.widgets['memoryframe'].grid(column=1,row=row,sticky='EW')
		self.widgets['memlabel'] = Tkinter.Label(self.widgets['memoryframe'],text='Memory', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['memlabel'].grid(column=0,row=self.gridrows['mem'],sticky='EW')
		self.gridrows['mem'] += 1
		self.widgets['vmemlabel'] = Tkinter.Label(self.widgets['memoryframe'],text="VMem", bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['vmemlabel'].grid(column=0,row=self.gridrows['mem'],sticky='EW')
		self.widgets['vmemdata'] = Tkinter.Label(self.widgets['memoryframe'],text=0, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['vmemdata'].grid(column=1,row=self.gridrows['mem'],sticky='EW')
		self.widgets['vmemgraph'] = TkBarGraph(self.widgets['memoryframe'], self.colours)
		self.widgets['vmemgraph'].widget.grid(column=2,row=self.gridrows['mem'],sticky='EW')
		self.gridrows['mem'] += 1
		self.widgets['swaplabel'] = Tkinter.Label(self.widgets['memoryframe'],text="Swap", bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['swaplabel'].grid(column=0,row=self.gridrows['mem'],sticky='EW')
		self.widgets['swapdata'] = Tkinter.Label(self.widgets['memoryframe'],text=0, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['swapdata'].grid(column=1,row=self.gridrows['mem'],sticky='EW')
		self.widgets['swapgraph'] = TkBarGraph(self.widgets['memoryframe'], self.colours)
		self.widgets['swapgraph'].widget.grid(column=2,row=self.gridrows['mem'],sticky='EW')
		self.scheduler.addTask('resman_memory', self.updateMemory, interval = 10)
	def updateMemory(self):
		""" util - update memory
		"""
		try:
			history = self.resources.metrics['memory'].hotValues()
			mem = self.resources.metrics['memory'].value
			if(len(history) > 1):
				if(history[-1].timestamp != self.last['memory']):
					self.last['memory'] = history[-1].timestamp
					self.widgets['vmemdata'].configure(text=mem['vmem'])
					self.widgets['vmemgraph'].update(mem['vmem'])
					self.widgets['swapdata'].configure(text=mem['smem'])
					self.widgets['swapgraph'].update(mem['smem'])
			else:
				self.widgets['vmemdata'].configure(text=mem['vmem'])
				self.widgets['vmemgraph'].update(mem['vmem'])
				self.widgets['swapdata'].configure(text=mem['smem'])
				self.widgets['swapgraph'].update(mem['smem'])
		except:
			pass
	def addTemperatureManager(self):
		""" view - temperature ui
		"""
		row = 1
		self.gridrows['temp'] = 0
		self.widgets['tempframe'] = Frame(self.widget,bg=self.colours['bg'])
		self.widgets['tempframe'].grid(column=0,row=row, columnspan=2, sticky='EW')
		self.widgets['cpuTemplabel'] = Tkinter.Label(self.widgets['tempframe'],text='CPU Temp', anchor=E, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['cpuTemplabel'].grid(column=0,row=self.gridrows['temp'], ipadx=30,sticky='EW')
		self.widgets['cpuTempData'] = Tkinter.Label(self.widgets['tempframe'],text='TBD', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['cpuTempData'].grid(column=1,row=self.gridrows['temp'], ipadx=10, padx=10, sticky='EW')
		
		self.widgets['gpuTemplabel'] = Tkinter.Label(self.widgets['tempframe'],text='GPU Temp', anchor=E, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['gpuTemplabel'].grid(column=2,row=self.gridrows['temp'], ipadx=30,sticky='EW')
		self.widgets['gpuTempData'] = Tkinter.Label(self.widgets['tempframe'],text='TBD', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['gpuTempData'].grid(column=3,row=self.gridrows['temp'], ipadx=10, padx=10,sticky='EW')
		
		self.scheduler.addTask('resman_temp', self.updateTemps, interval = 30)
	def updateTemps(self):
		""" util - update temperature
		"""
		temps = self.resources.metrics['temperature'].value
		if(temps != None):
			try:
				self.widgets['cpuTempData'].configure(text=round(temps['cpu'], 1), fg=self.colours['valuefg'] )
				self.widgets['gpuTempData'].configure(text=round(temps['gpu'], 1), fg=self.colours['valuefg'] )
			except:
				pass
	def addDiskManager(self):
		""" view - disk ui
		"""
		row = 2	
		self.gridrows['disk'] = 0
		self.widgets['diskframe'] = Frame(self.widget,bg=self.colours['bg'])
		self.widgets['diskframe'].grid(column=0,row=row, columnspan=2, sticky='EW')
		self.widgets['disklabel'] = Tkinter.Label(self.widgets['diskframe'],text='Disk Usage', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['disklabel'].grid(column=0,row=self.gridrows['disk'],sticky='EW')
		
		self.gridrows['disk'] += 1
		
		self.widgets['diskCanvas'] = Tkinter.Canvas(self.widgets['diskframe'], borderwidth=0, highlightthickness=0, width=420, height=220)
		self.widgets['diskCanvas'].grid(column=0,row=self.gridrows['disk'], sticky='EW')
		self.widgets['diskdataframe'] = Frame(self.widgets['diskCanvas'],bg=self.colours['bg'])
		self.widgets['diskdataframe'].grid(column=0,row=0,sticky='EW')
		self.widgets['diskScroller'] = Tkinter.Scrollbar(self.widgets['diskframe'], orient=VERTICAL, command=self.widgets['diskCanvas'].yview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
		self.widgets['diskScroller'].grid(column=1, row=self.gridrows['disk'], sticky="NS")
		self.widgets['diskCanvas'].configure(yscrollcommand=self.widgets['diskScroller'].set, bg=self.colours['bg'])
		self.widgets['diskCanvas'].create_window((0,0),window=self.widgets['diskdataframe'],anchor='nw')
		self.widgets['diskdataframe'].bind("<Configure>", self.diskInfoScroll)
		
		self.scheduler.addTask('resman_disks', self.updateDisks, interval = 30)
	def diskInfoScroll(self, event):
		""" scroll event callback
		
		@param event
		"""
		self.widgets['diskCanvas'].configure(scrollregion=self.widgets['diskCanvas'].bbox(ALL), width=420, height=220)
	def updateDisks(self):
		""" util - update disks
		"""
		history = self.resources.metrics['disks'].hotValues()
		if(len(history) > 1):
				if(history[-1].timestamp != self.last['disks']):
					self.last['disks'] = history[-1].timestamp
					self.__applyDiskData(history[1].datavalue)
		else:
			if(self.resources.metrics['disks'].value != None):
				try:
					self.__applyDiskData(self.resources.metrics['disks'].value)
				except:
					pass
	def __applyDiskData(self, disks):
		""" util - apply disk data
		
		@param disks
		"""
		col = 0
		for k, v in disks.iteritems():
			try:
				self.widgets[k]['diskchart'].update({self.colours['unitblue1']: v['percent'], self.colours['unitblue2']: 100-v['percent']})
				self.widgets[k]['useddata'].configure(text=self.sizeof_fmt(v['used']))
				self.widgets[k]['freedata'].configure(text=self.sizeof_fmt(v['free']))
				self.widgets[k]['disktotaldata'].configure(text=self.sizeof_fmt(v['total']))
			except:
				self.widgets[k] = {}
				mp = v['mountpoint'].split('/')
				if(len(mp) > 2):
					mp = mp[-1]
				else:
					mp = v['mountpoint']
				self.widgets[k]['diskchart'] = TkPiChart(self.widgets['diskdataframe'], {self.colours['unitblue1']: v['percent'], self.colours['unitblue2']: 100-v['percent']}, colours=self.colours, label=mp)
				self.widgets[k]['diskchart'].widget.grid(column=col,row=self.gridrows['disk'],sticky='EW', padx=5, pady=5)
				col += 1
				self.widgets[k]['diskdata'] = Frame(self.widgets['diskdataframe'],bg=self.colours['bg'])
				self.widgets[k]['diskdata'].grid(column=col,row=self.gridrows['disk'], sticky='EW')
				
				dd = self.widgets[k]['diskdata']
				
				self.gridrows['diskdata'] = 1
				
				self.widgets[k]['devicelabel'] = Tkinter.Label(dd,text='Device', anchor=NE, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets[k]['devicelabel'].grid(column=0,row=self.gridrows['diskdata'],sticky='EW')
				self.widgets[k]['devicedata'] = Tkinter.Label(dd,text=k, anchor=NW, bg=self.colours['bg'], fg=self.colours['lightfg'])
				self.widgets[k]['devicedata'].grid(column=1,row=self.gridrows['diskdata'],sticky='EW')
				
				self.gridrows['diskdata'] += 1
				
				self.widgets[k]['fslabel'] = Tkinter.Label(dd,text='File System', anchor=NE, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets[k]['fslabel'].grid(column=0,row=self.gridrows['diskdata'],sticky='EW')
				self.widgets[k]['fsdata'] = Tkinter.Label(dd,text=v['fstype'], anchor=NW, bg=self.colours['bg'], fg=self.colours['lightfg'])
				self.widgets[k]['fsdata'].grid(column=1,row=self.gridrows['diskdata'],sticky='EW')
				
				self.gridrows['diskdata'] += 1
				
				self.widgets[k]['usedlabel'] = Tkinter.Label(dd,text='Used', anchor=NE, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets[k]['usedlabel'].grid(column=0,row=self.gridrows['diskdata'],sticky='EW')
				self.widgets[k]['useddata'] = Tkinter.Label(dd,text=self.sizeof_fmt(v['used']), anchor=NW, bg=self.colours['bg'], fg=self.colours['lightfg'])
				self.widgets[k]['useddata'].grid(column=1,row=self.gridrows['diskdata'],sticky='EW')
				
				self.gridrows['diskdata'] += 1
				
				self.widgets[k]['freelabel'] = Tkinter.Label(dd,text='Free', anchor=NE, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets[k]['freelabel'].grid(column=0,row=self.gridrows['diskdata'],sticky='EW')
				self.widgets[k]['freedata'] = Tkinter.Label(dd,text=self.sizeof_fmt(v['free']), anchor=NW, bg=self.colours['bg'], fg=self.colours['lightfg'])
				self.widgets[k]['freedata'].grid(column=1,row=self.gridrows['diskdata'],sticky='EW')
				
				self.gridrows['diskdata'] += 1
				
				self.widgets[k]['disktotallabel'] = Tkinter.Label(dd,text='Total', anchor=NE, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets[k]['disktotallabel'].grid(column=0,row=self.gridrows['diskdata'],sticky='EW')
				self.widgets[k]['disktotaldata'] = Tkinter.Label(dd,text=self.sizeof_fmt(v['total']), anchor=NW, bg=self.colours['bg'], fg=self.colours['lightfg'])
				self.widgets[k]['disktotaldata'].grid(column=1,row=self.gridrows['diskdata'],sticky='EW')
				
				col = 0
				self.gridrows['disk'] += 1
	def addTaskManager(self):
		""" view - tasks ui
		"""
		row = 4
		self.widgets['taskframe'] = Frame(self.widget,bg=self.colours['bg'])
		self.widgets['taskframe'].grid(column=0,row=row,columnspan=2, sticky='EW')
		self.taskwidgets = {}
		self.notestyle = ttk.Style()
		self.notestyle.configure("TNotebook", background=self.colours['bg'], borderwidth=0)
		self.notestyle.configure("TNotebook.Tab", background=self.colours['buttonbg'], foreground='#000000', borderwidth=0)
		self.gridrows['tasks'] = 0
		self.taskwidgets['frameLabel'] = Tkinter.Label(self.widgets['taskframe'],text='Tasks / Network', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.taskwidgets['frameLabel'].grid(column=0,row=self.gridrows['tasks'], columnspan=1,sticky='EW')
		self.gridrows['tasks'] += 1
		self.taskwidgets['tasksnotebook'] = ttk.Notebook(self.widgets['taskframe'], style="TNotebook")
		self.taskwidgets['tasksnotebook'].grid(column=0,row=self.gridrows['tasks'],sticky='EW')
		self.addThreadManager()
		self.addProcessManager()
		self.addTrafficManager()
		self.addConnectionManager()
		self.taskwidgets['tasksnotebook'].add(self.widgets['processframe'], text="Processes")
		self.taskwidgets['tasksnotebook'].add(self.widgets['threadframe'], text="Threads")
		self.taskwidgets['tasksnotebook'].add(self.netwidgets['trafficwrap'], text="Traffic")
		self.taskwidgets['tasksnotebook'].add(self.netwidgets['connectionwrap'], text="Connections")
	def addThreadManager(self):
		""" view - thread ui
		"""
		row = 0
		self.threadwidgets = {}
		self.gridrows['thread'] = 0
		self.widgets['threadframe'] = Frame(self.taskwidgets['tasksnotebook'],bg=self.colours['bg'])
		self.widgets['threadframe'].grid(column=0,row=row,sticky='EW')

		self.threadwidgets['infoCanvas'] = Tkinter.Canvas(self.widgets['threadframe'], borderwidth=0, highlightthickness=0, width=420, height=self.tasksheight)
		self.threadwidgets['infoCanvas'].grid(column=0,row=self.gridrows['thread'], sticky='EW')
		self.threadwidgets['dataframe'] = Frame(self.threadwidgets['infoCanvas'],bg=self.colours['bg'])
		self.threadwidgets['dataframe'].grid(column=0,row=0,sticky='EW')
		self.threadwidgets['infoScroller'] = Tkinter.Scrollbar(self.widgets['threadframe'], orient=VERTICAL, command=self.threadwidgets['infoCanvas'].yview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
		self.threadwidgets['infoScroller'].grid(column=1, row=self.gridrows['thread'], sticky="NS")
		self.threadwidgets['infoCanvas'].configure(yscrollcommand=self.threadwidgets['infoScroller'].set, bg=self.colours['bg'])
		self.threadwidgets['infoCanvas'].create_window((0,0),window=self.threadwidgets['dataframe'],anchor='nw')
		self.threadwidgets['dataframe'].bind("<Configure>", self.threadInfoScroll)
		
		self.threadwidgets['subframe'] = Frame(self.threadwidgets['dataframe'],bg=self.colours['bg'])
		self.threadwidgets['subframe'].grid(column=0,row=0,columnspan=2, sticky='EW')
		
		self.threadwidgets['stretchframe'] = Frame(self.threadwidgets['subframe'],bg=self.colours['bg'], borderwidth=0, width=420)
		self.threadwidgets['stretchframe'].grid(column=0,row=0, columnspan=4, sticky='EW')
		self.threadwidgets['stretchframe'].columnconfigure(0, weight=1)
		
		self.threadwidgets['namelabel'] = Tkinter.Label(self.threadwidgets['subframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
		self.threadwidgets['namelabel'].grid(column=0,row=1,sticky='EW')
		self.threadwidgets['identlabel'] = Tkinter.Label(self.threadwidgets['subframe'],text='Ident', bg=self.colours['bg'], fg=self.colours['fg'])
		self.threadwidgets['identlabel'].grid(column=1,row=1,sticky='EW')
		self.threadwidgets['daemonlabel'] = Tkinter.Label(self.threadwidgets['subframe'],text='Daemon', bg=self.colours['bg'], fg=self.colours['fg'])
		self.threadwidgets['daemonlabel'].grid(column=2,row=1,sticky='EW')
		self.threadwidgets['alivelabel'] = Tkinter.Label(self.threadwidgets['subframe'],text='Alive', bg=self.colours['bg'], fg=self.colours['fg'])
		self.threadwidgets['alivelabel'].grid(column=3,row=1,sticky='EW')

		self.threadwidgets['activelabel'] = Tkinter.Label(self.threadwidgets['dataframe'],text='Total', bg=self.colours['bg'], fg=self.colours['fg'])
		self.threadwidgets['activelabel'].grid(column=0,row=1,sticky='EW')
		self.threadwidgets['activedata'] = Tkinter.Label(self.threadwidgets['dataframe'],text='TBD', bg=self.colours['bg'], fg=self.colours['fg'])
		self.threadwidgets['activedata'].grid(column=1,row=1,sticky='EW')

		self.scheduler.addTask('resman_threads', self.updateThreads, interval = 20)
	def threadInfoScroll(self, event):
		""" handle thread scroll event
		
		@param event
		"""
		self.threadwidgets['infoCanvas'].configure(scrollregion=self.threadwidgets['infoCanvas'].bbox(ALL), width=420, height=self.tasksheight)
	def updateThreads(self):
		""" util - update threads ui
		"""
		history = self.resources.metrics['threads'].hotValues()
		if(len(history) > 0):
			if(history[-1].timestamp != self.last['threads']):
				try:
					self.__applyThreadData(history[-1].datavalue)
					self.last['threads'] = history[-1].timestamp
				except:
					pass
		else:
			try:
				self.__applyThreadData(self.resources.metrics['threads'].value)
			except:
				pass
	def __applyThreadData(self, threads):
		""" apply thread data
		"""
		if(threads != None):
			self.gridrows['thread'] = 2
			for k, v in threads.iteritems():
				rowcolour = self.colours['rowbg']
				if(self.gridrows['thread'] % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				try:
					self.threadwidgets[k]['talive'].configure(text=v['isalive'])
				except:
					self.threadwidgets[k] = {}
					self.threadwidgets[k]['name'] = Tkinter.Label(self.threadwidgets['subframe'],text=v['name'], bg=rowcolour, fg=self.colours['fg'])
					self.threadwidgets[k]['name'].grid(column=0,row=self.gridrows['thread'],sticky='EW')
					self.threadwidgets[k]['ident'] = Tkinter.Label(self.threadwidgets['subframe'],text=string.replace(k,'i',''), bg=rowcolour, fg=self.colours['fg'])
					self.threadwidgets[k]['ident'].grid(column=1,row=self.gridrows['thread'],sticky='EW')
					self.threadwidgets[k]['daemon'] = Tkinter.Label(self.threadwidgets['subframe'],text=v['isdaemon'], bg=rowcolour, fg=self.colours['fg'])
					self.threadwidgets[k]['daemon'].grid(column=2,row=self.gridrows['thread'],sticky='EW')
					self.threadwidgets[k]['talive'] = Tkinter.Label(self.threadwidgets['subframe'],text=v['isalive'], bg=rowcolour, fg=self.colours['fg'])
					self.threadwidgets[k]['talive'].grid(column=3,row=self.gridrows['thread'],sticky='EW')
				self.gridrows['thread'] += 1
			self.threadwidgets['activedata'].configure(text = str(self.resources.metrics['threadcount'].value))
	def addProcessManager(self):
		""" view - process ui
		"""
		row = 1
		self.processwidgets = {}
		self.gridrows['process'] = 0
		self.widgets['processframe'] = Frame(self.taskwidgets['tasksnotebook'],bg=self.colours['bg'])
		self.widgets['processframe'].grid(column=0,row=row,sticky='EW')
		self.processwidgets['infoCanvas'] = Tkinter.Canvas(self.widgets['processframe'], borderwidth=0, highlightthickness=0, width=420, height=self.tasksheight)
		self.processwidgets['infoCanvas'].grid(column=0,row=self.gridrows['process'],sticky='EW')
		self.processwidgets['dataframe'] = Frame(self.processwidgets['infoCanvas'],bg=self.colours['bg'])
		self.processwidgets['dataframe'].grid(column=0,row=0,sticky='EW')
		self.processwidgets['infoScroller'] = Tkinter.Scrollbar(self.widgets['processframe'], orient=VERTICAL, command=self.processwidgets['infoCanvas'].yview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
		self.processwidgets['infoScroller'].grid(column=1, row=self.gridrows['process'], sticky="NS")
		self.processwidgets['infoCanvas'].configure(yscrollcommand=self.processwidgets['infoScroller'].set, bg=self.colours['bg'])
		self.processwidgets['infoCanvas'].create_window((0,0),window=self.processwidgets['dataframe'],anchor='nw')
		self.processwidgets['dataframe'].bind("<Configure>", self.processInfoScroll)
		
		self.processwidgets['stretchframe'] = Frame(self.processwidgets['dataframe'],bg=self.colours['bg'], borderwidth=0, width=420)
		self.processwidgets['stretchframe'].grid(column=0,row=0, columnspan=2, sticky='EW')
		self.processwidgets['stretchframe'].columnconfigure(0, weight=1)
		
		self.processwidgets['namelabel'] = Tkinter.Label(self.processwidgets['dataframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
		self.processwidgets['namelabel'].grid(column=0,row=1,sticky='EW')
		self.processwidgets['userlabel'] = Tkinter.Label(self.processwidgets['dataframe'],text='User', bg=self.colours['bg'], fg=self.colours['fg'])
		self.processwidgets['userlabel'].grid(column=1,row=1,sticky='EW')
		self.widgets['processframe'].grid_columnconfigure(0, weight=1)
		self.processwidgets['infoCanvas'].grid_columnconfigure(0, weight=1)
		self.processwidgets['dataframe'].grid_columnconfigure(0, weight=4)
		
		self.scheduler.addTask('resman_processes', self.updateProcesses, interval = 30)
	def processInfoScroll(self, event):
		""" util - handle process scroll event
		"""
		self.processwidgets['infoCanvas'].configure(scrollregion=self.processwidgets['infoCanvas'].bbox(ALL), width=420, height=self.tasksheight)
	def updateProcesses(self):
		""" util - update threads ui
		"""
		history = self.resources.metrics['processes'].hotValues()
		if(history):
				if(history[-1].timestamp != self.last['processes']):
					self.last['processes'] = history[-1].timestamp
					self.__applyProcessData(history[-1].datavalue)
		else:
			try:
				self.__applyProcessData(self.resources.metrics['processes'].value)
			except:
				pass
	def __applyProcessData(self, processes):
		""" util - apply process data
		"""
		if(processes != None):
			self.gridrows['process'] = 2
			for k, v in processes.iteritems():
				rowcolour = self.colours['rowbg']
				if(self.gridrows['process'] % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				try:
						self.processwidgets[k]
				except:
					self.processwidgets[k] = {}
					self.processwidgets[k]['name'] = Tkinter.Label(self.processwidgets['dataframe'],text=v['name'], bg=rowcolour, fg=self.colours['fg'])
					self.processwidgets[k]['name'].grid(column=0,row=self.gridrows['process'],sticky='EW')
					self.processwidgets[k]['user'] = Tkinter.Label(self.processwidgets['dataframe'],text=v['username'], bg=rowcolour, fg=self.colours['fg'])
					self.processwidgets[k]['user'].grid(column=1,row=self.gridrows['process'],sticky='EW')
				self.gridrows['process'] += 1
	def addTrafficManager(self):
		""" view - traffic ui
		"""
		self.netwidgets = {}
		self.gridrows['traffic'] = 0
		
		self.netwidgets['trafficwrap'] = Frame(self.taskwidgets['tasksnotebook'],bg=self.colours['bg'])
		self.netwidgets['trafficwrap'].grid(column=0,row=2,sticky='EW')
		
		self.netwidgets['trafficCanvas'] = Tkinter.Canvas(self.netwidgets['trafficwrap'], borderwidth=0, highlightthickness=0, width=420, height=self.tasksheight)
		self.netwidgets['trafficCanvas'].grid(column=0,row=self.gridrows['traffic'],sticky='EW')
		self.netwidgets['trafficdata'] = Frame(self.netwidgets['trafficCanvas'],bg=self.colours['bg'])
		self.netwidgets['trafficdata'].grid(column=0,row=0,sticky='EW')
		self.netwidgets['trafficScroller'] = Tkinter.Scrollbar(self.netwidgets['trafficwrap'], orient=VERTICAL, command=self.netwidgets['trafficCanvas'].yview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
		self.netwidgets['trafficScroller'].grid(column=1, row=self.gridrows['traffic'], sticky="NS")
		self.netwidgets['trafficCanvas'].configure(yscrollcommand=self.netwidgets['trafficScroller'].set, bg=self.colours['bg'])
		self.netwidgets['trafficCanvas'].create_window((0,0),window=self.netwidgets['trafficdata'],anchor='nw')
		self.netwidgets['trafficdata'].bind("<Configure>", self.trafficInfoScroll)
		
		self.netwidgets['tstretchframe'] = Frame(self.netwidgets['trafficdata'],bg=self.colours['bg'], borderwidth=0, width=420)
		self.netwidgets['tstretchframe'].grid(column=0,row=self.gridrows['traffic'], columnspan=3, sticky='EW')
		self.netwidgets['tstretchframe'].columnconfigure(0, weight=1)
		
		self.gridrows['traffic'] += 1
		
		self.netwidgets['namelabel'] = Tkinter.Label(self.netwidgets['trafficdata'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
		self.netwidgets['namelabel'].grid(column=0,row=self.gridrows['traffic'],sticky='EW')
		self.netwidgets['bsentlabel'] = Tkinter.Label(self.netwidgets['trafficdata'],text='Sent', bg=self.colours['bg'], fg=self.colours['fg'])
		self.netwidgets['bsentlabel'].grid(column=1,row=self.gridrows['traffic'],sticky='EW')
		self.netwidgets['breceivedlabel'] = Tkinter.Label(self.netwidgets['trafficdata'],text='Received', bg=self.colours['bg'], fg=self.colours['fg'])
		self.netwidgets['breceivedlabel'].grid(column=2,row=self.gridrows['traffic'],sticky='EW')
		self.gridrows['traffic'] += 1
		
		self.netwidgets['trafficdata'].grid_columnconfigure(0, weight=1)
	def addConnectionManager(self):
		""" view - connection ui
		"""
		self.connwidgets = {}
		self.gridrows['connections'] = 0
		
		self.netwidgets['connectionwrap'] = Frame(self.taskwidgets['tasksnotebook'],bg=self.colours['bg'])
		self.netwidgets['connectionwrap'].grid(column=0,row=3,sticky='EW')
		
		self.netwidgets['connectionCanvas'] = Tkinter.Canvas(self.netwidgets['connectionwrap'], borderwidth=0, highlightthickness=0, width=420, height=self.tasksheight)
		self.netwidgets['connectionCanvas'].grid(column=0,row=self.gridrows['process'],sticky='EW')
		self.netwidgets['connectiondata'] = Frame(self.netwidgets['connectionCanvas'],bg=self.colours['bg'])
		self.netwidgets['connectiondata'].grid(column=0,row=0,sticky='EW')
		self.netwidgets['connectionScroller'] = Tkinter.Scrollbar(self.netwidgets['connectionwrap'], orient=VERTICAL, command=self.netwidgets['connectionCanvas'].yview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
		self.netwidgets['connectionScroller'].grid(column=1, row=self.gridrows['process'], sticky="NS")
		self.netwidgets['connectionCanvas'].configure(yscrollcommand=self.netwidgets['connectionScroller'].set, bg=self.colours['bg'])
		self.netwidgets['connectionCanvas'].create_window((0,0),window=self.netwidgets['connectiondata'],anchor='nw')
		self.netwidgets['connectiondata'].bind("<Configure>", self.connectionInfoScroll)
		
		self.netwidgets['cstretchframe'] = Frame(self.netwidgets['connectiondata'],bg=self.colours['bg'], borderwidth=0, width=400)
		self.netwidgets['cstretchframe'].grid(column=0,row=self.gridrows['connections'], columnspan=5, sticky='EW')
		self.netwidgets['cstretchframe'].columnconfigure(0, weight=1)
		
		self.gridrows['connections'] += 1
		
		self.netwidgets['laddlabel'] = Tkinter.Label(self.netwidgets['connectiondata'],text='Local Address', bg=self.colours['bg'], fg=self.colours['fg'])
		self.netwidgets['laddlabel'].grid(column=0,row=self.gridrows['connections'],sticky='EW')
		self.netwidgets['lportlabel'] = Tkinter.Label(self.netwidgets['connectiondata'],text='Local Port', bg=self.colours['bg'], fg=self.colours['fg'])
		self.netwidgets['lportlabel'].grid(column=1,row=self.gridrows['connections'],sticky='EW')
		self.netwidgets['raddlabel'] = Tkinter.Label(self.netwidgets['connectiondata'],text='Remote Address', bg=self.colours['bg'], fg=self.colours['fg'])
		self.netwidgets['raddlabel'].grid(column=2,row=self.gridrows['connections'],sticky='EW')
		self.netwidgets['rportlabel'] = Tkinter.Label(self.netwidgets['connectiondata'],text='Remote Port', bg=self.colours['bg'], fg=self.colours['fg'])
		self.netwidgets['rportlabel'].grid(column=3,row=self.gridrows['connections'],sticky='EW')
		self.netwidgets['statuslabel'] = Tkinter.Label(self.netwidgets['connectiondata'],text='Status', bg=self.colours['bg'], fg=self.colours['fg'])
		self.netwidgets['statuslabel'].grid(column=4,row=self.gridrows['connections'],sticky='EW')

		self.netwidgets['connectiondata'].grid_columnconfigure(0, weight=1)
		
		self.scheduler.addTask('resman_network', self.updateNetwork, interval = 30)
	def addOptionManager(self):
		""" view - options ui
		"""
		self.gridrows['option'] = 0
		self.widgets['oframe'] = Frame(self.widget,bg=self.colours['bg'])
		self.widgets['oframe'].grid(column=0,row=5,columnspan=2, padx=10, pady=5, sticky='EW')
		self.netwidgets['olabel'] = Tkinter.Label(self.widgets['oframe'],text='Archive', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.netwidgets['olabel'].grid(column=0,row=self.gridrows['option'], pady=5,sticky='EW')
		self.gridrows['option'] += 1
		self.variables['archiveCpu'] = Tkinter.BooleanVar()
		self.variables['archiveCpu'].set(Setting.get('resource_archive_cpu',False))
		self.netwidgets['aCpuEntry'] = Tkinter.Checkbutton(self.widgets['oframe'], variable=self.variables['archiveCpu'], text='CPU Usage', command=self.OnToggleCpuClick, anchor=W, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.netwidgets['aCpuEntry'].grid(column=0,row=self.gridrows['option'], padx=0, pady=0, ipadx=10, sticky='EW')
		
		self.variables['archiveMem'] = Tkinter.BooleanVar()
		self.variables['archiveMem'].set(Setting.get('resource_archive_mem',False))
		self.netwidgets['aMemEntry'] = Tkinter.Checkbutton(self.widgets['oframe'], variable=self.variables['archiveMem'], text='Memory', command=self.OnToggleMemoryClick, anchor=W, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.netwidgets['aMemEntry'].grid(column=1,row=self.gridrows['option'], padx=0, pady=0, ipadx=10, sticky='EW')
		
		self.variables['archiveTemp'] = Tkinter.BooleanVar()
		self.variables['archiveTemp'].set(Setting.get('resource_archive_temp',False))
		self.netwidgets['aTempEntry'] = Tkinter.Checkbutton(self.widgets['oframe'], variable=self.variables['archiveTemp'], text='Temperature', command=self.OnToggleTempClick, anchor=W, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.netwidgets['aTempEntry'].grid(column=2,row=self.gridrows['option'], padx=0, pady=0, ipadx=10, sticky='EW')
		
		self.variables['archiveDisks'] = Tkinter.BooleanVar()
		self.variables['archiveDisks'].set(Setting.get('resource_archive_disks',False))
		self.netwidgets['aDisksEntry'] = Tkinter.Checkbutton(self.widgets['oframe'], variable=self.variables['archiveDisks'], text='Disks', command=self.OnToggleDisksClick, anchor=W, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.netwidgets['aDisksEntry'].grid(column=3,row=self.gridrows['option'],padx=0, pady=0, ipadx=10, sticky='EW')
		
		self.gridrows['option'] += 1
		self.variables['archiveProcess'] = Tkinter.BooleanVar()
		self.variables['archiveProcess'].set(Setting.get('resource_archive_processes',False))
		self.netwidgets['aProcessEntry'] = Tkinter.Checkbutton(self.widgets['oframe'], variable=self.variables['archiveProcess'], text='Processes', command=self.OnToggleProcessesClick, anchor=W, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.netwidgets['aProcessEntry'].grid(column=0,row=self.gridrows['option'],padx=0, pady=0, ipadx=10, sticky='EW')
		
		self.variables['archiveThread'] = Tkinter.BooleanVar()
		self.variables['archiveThread'].set(Setting.get('resource_archive_threads',False))
		self.netwidgets['aThreadEntry'] = Tkinter.Checkbutton(self.widgets['oframe'], variable=self.variables['archiveThread'], text='Threads', command=self.OnToggleThreadsClick, anchor=W, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.netwidgets['aThreadEntry'].grid(column=1,row=self.gridrows['option'],padx=0, pady=0, ipadx=10, sticky='EW')
		
		self.variables['archiveNet'] = Tkinter.BooleanVar()
		self.variables['archiveNet'].set(Setting.get('resource_archive_net',False))
		self.netwidgets['aNetEntry'] = Tkinter.Checkbutton(self.widgets['oframe'], variable=self.variables['archiveNet'], text='Network', command=self.OnToggleNetworkClick, anchor=W, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.netwidgets['aNetEntry'].grid(column=2,row=self.gridrows['option'],padx=0, pady=0, ipadx=10, sticky='EW')
	
	def trafficInfoScroll(self, event):
		""" util - handle traffic scroll event
		
		@param event
		"""
		self.netwidgets['trafficCanvas'].configure(scrollregion=self.netwidgets['trafficCanvas'].bbox(ALL), width=420, height=self.tasksheight)
	def connectionInfoScroll(self, event):
		""" util - handle connection scroll event
		
		@param event
		"""
		self.netwidgets['connectionCanvas'].configure(scrollregion=self.netwidgets['connectionCanvas'].bbox(ALL), width=420, height=self.tasksheight)
	def updateNetwork(self):
		""" util - update network ui
		
		@param event
		"""
		history = self.resources.metrics['network'].hotValues()
		if(len(history) > 1):
				if(history[-1].timestamp != self.last['network']):
					self.last['network'] = history[-1].timestamp
					self.__applyNetworkData(history[-1].datavalue)
		else:
			try:
				self.__applyNetworkData(self.resources.metrics['network'].value)
			except:
				pass
	def __applyNetworkData(self, network):
		""" util - apply network data
		
		@param network
		"""
		self.gridrows['traffic'] = 2
		rowcount = 0
		for k,v in network['nics'].iteritems():
			rowcolour = self.colours['rowbg']
			if(rowcount % 2 == 0):
				rowcolour = self.colours['rowaltbg']
			rowcount += 1
			try:

				self.netwidgets[k]['bsent'].configure(text = self.sizeof_fmt(v['bytes_sent']))
				self.netwidgets[k]['breceived'].configure(text = self.sizeof_fmt(v['bytes_recv']))
			except:
				self.netwidgets[k] = {}
				self.netwidgets[k]['name'] = Tkinter.Label(self.netwidgets['trafficdata'],text=k, bg=rowcolour, fg=self.colours['fg'])
				self.netwidgets[k]['name'].grid(column=0,row=self.gridrows['traffic'],sticky='EW')
				self.netwidgets[k]['bsent'] = Tkinter.Label(self.netwidgets['trafficdata'],text=self.sizeof_fmt(v['bytes_sent']), bg=rowcolour, fg=self.colours['fg'])
				self.netwidgets[k]['bsent'].grid(column=1,row=self.gridrows['traffic'],sticky='EW')
				self.netwidgets[k]['breceived'] = Tkinter.Label(self.netwidgets['trafficdata'],text=self.sizeof_fmt(v['bytes_recv']), bg=rowcolour, fg=self.colours['fg'])
				self.netwidgets[k]['breceived'].grid(column=2,row=self.gridrows['traffic'],sticky='EW')
			self.gridrows['traffic'] += 1
		self.gridrows['connections'] = 2
		for k,v in network['conns'].iteritems():
			rowcolour = self.colours['rowbg']
			if(rowcount % 2 == 0):
				rowcolour = self.colours['rowaltbg']
			rowcount += 1
			try:
				self.connwidgets[k]['bstatus'].configure(text = v['status'])
				self.connwidgets[k]['status'] = v['status']
			except:
				self.connwidgets[k] = {}
				self.connwidgets[k]['ladd'] = Tkinter.Label(self.netwidgets['connectiondata'],text=v['laddr'][0] if len(v['laddr']) > 0 else '', bg=rowcolour, fg=self.colours['fg'])
				self.connwidgets[k]['ladd'].grid(column=0,row=self.gridrows['connections'],sticky='EW')
				self.connwidgets[k]['lport'] = Tkinter.Label(self.netwidgets['connectiondata'],text=v['laddr'][1] if len(v['laddr']) > 0 else '', bg=rowcolour, fg=self.colours['fg'])
				self.connwidgets[k]['lport'].grid(column=1,row=self.gridrows['connections'],sticky='EW')
				self.connwidgets[k]['radd'] = Tkinter.Label(self.netwidgets['connectiondata'],text=v['raddr'][0] if len(v['raddr']) > 0 else '', bg=rowcolour, fg=self.colours['fg'])
				self.connwidgets[k]['radd'].grid(column=2,row=self.gridrows['connections'],sticky='EW')
				self.connwidgets[k]['rport'] = Tkinter.Label(self.netwidgets['connectiondata'],text=v['laddr'][1] if len(v['raddr']) > 0 else '', bg=rowcolour, fg=self.colours['fg'])
				self.connwidgets[k]['rport'].grid(column=3,row=self.gridrows['connections'],sticky='EW')
				self.connwidgets[k]['bstatus'] = Tkinter.Label(self.netwidgets['connectiondata'],text=v['status'], bg=rowcolour, fg=self.colours['fg'])
				self.connwidgets[k]['bstatus'].grid(column=4,row=self.gridrows['connections'],sticky='EW')
			self.gridrows['connections'] += 1
	
	#=== ACTIONS ===#
	def OnToggleCpuClick(self):
		""" action - toggle cpu archive
		"""
		Setting.set('resource_archive_cpu', self.variables['archiveCpu'].get())
	def OnToggleMemoryClick(self):
		""" action - toggle memory archive
		"""
		Setting.set('resource_archive_mem', self.variables['archiveMem'].get())
	def OnToggleTempClick(self):
		""" action - toggle temperature archive
		"""
		Setting.set('resource_archive_temp', self.variables['archiveTemp'].get())
	def OnToggleDisksClick(self):
		""" action - toggle disks archive
		"""
		Setting.set('resource_archive_disks', self.variables['archiveDisks'].get())
	def OnToggleProcessesClick(self):
		""" action - toggle processes archive
		"""
		Setting.set('resource_archive_processes', self.variables['archiveProcess'].get())
	def OnToggleThreadsClick(self):
		""" action - toggle threads archive
		"""
		Setting.set('resource_archive_threads', self.variables['archiveThread'].get())
	def OnToggleNetworkClick(self):
		""" action - toggle network archive
		"""
		Setting.set('resource_archive_net', self.variables['archiveNet'].get())
	
	#=== UTILS ===#
	def sizeof_fmt(self, num):
		""" util - format file size for display
		"""
		for x in ['bytes','KB','MB','GB','TB']:
			if num < 1024.0:
				return "%3.1f %s" % (num, x)
			num /= 1024.0