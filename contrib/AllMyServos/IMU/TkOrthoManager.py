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
import Tkinter, os, Specification
from __bootstrap import AmsEnvironment
from Tkinter import *
from TkBlock import *
from TkDependencyManager import *
from Setting import *
from IMU import IMU

## UI for orthographic demo
class TkOrthoManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes TkOrthoManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkOrthoManager,self).__init__(parent, gui, **options)
		self.specification = gui.specification
		self.initDependencyManager()
		if(hasattr(self.gui, 'scheduler')):
			self.scheduler = self.gui.scheduler
		else:
			self.scheduler = Scheduler.GetInstance()
		if(not self.dm.installRequired()):
			self.pimg = self.gui.getModule('PIL.Image')
			self.tkimg = self.gui.getModule('PIL.ImageTk')
			if(hasattr(self.gui, 'imu')):
				self.imu = self.gui.imu
			else:
				self.imu = self.gui.imu = IMU(self.specification, self.scheduler, (not Setting.get('imu_autostart', False)))
			self.shapes = {}
			self.cache = { 'roll': {}, 'pitch': {}, 'yaw': {} }
			self.basepath = AmsEnvironment.AppPath()
			self.initImages()
			self.scheduler.addTask('ortho', self.updateOrtho, 0.2, True)
	def initDependencyManager(self):
		""" setup dependency checks
		"""
		dependencies = [
			{'package':'python-imaging', 'installer': 'apt-get'},
			{'package':'python-imaging-tk', 'installer': 'apt-get'},
			{'package':'tk8.5', 'installer': 'apt-get'},
			{'package':'tcl8.5', 'installer': 'apt-get'},
			{'package':'pillow', 'installer': 'pip', 'version': '2.6.1'}
		]
		self.dm = TkDependencyManager(self.widget, dependencies, 'Orthographic Manager', self.gui)
	def setup(self):
		""" setup gui menu
		"""
		try:
			self.gui.menus['imu']
		except:
			self.gui.menus['imu'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="IMU", menu=self.gui.menus['imu'])
		self.gui.menus['imu'].insert_command(3, label="Orthographic", command=self.OnShowOrthographicClick)
	def initImages(self):
		""" setup required images
		"""
		self.oimages = {}
		self.oimages['roll'] = self.pimg.Image.open(os.path.join(self.basepath, 'images/orthographic/front.png')).convert('RGBA')
		self.oimages['pitch'] = self.pimg.Image.open(os.path.join(self.basepath, 'images/orthographic/right.png')).convert('RGBA')
		self.oimages['yaw'] = self.pimg.Image.open(os.path.join(self.basepath, 'images/orthographic/top.png')).convert('RGBA')
	def buildCache(self):
		""" setup cache (first 60 degs)
		"""
		if(not any(self.cache['roll'])):
			for i in range(-30,30):
				self.cache['roll'][i] = self.tkimg.ImageTk.PhotoImage(self.oimages['roll'].rotate(i))
				self.cache['pitch'][i] = self.tkimg.ImageTk.PhotoImage(self.oimages['pitch'].rotate(i))
				self.cache['yaw'][i] = self.tkimg.ImageTk.PhotoImage(self.oimages['yaw'].rotate(i))
	def getImage(self, axis, angle):
		""" gets an image from cache or caches it
		
		@param axis
		@param angle
		"""
		try:
			self.cache[axis][angle]
		except:
			self.cache[axis][angle] = self.tkimg.ImageTk.PhotoImage(self.oimages[axis].rotate(angle))
		return self.cache[axis][angle]
	
	#=== VIEWS ===#
	def serviceManager(self):
		""" view - service manager
		"""
		self.widgets['servicelabel'] = Tkinter.Label(self.widgets['tframe'],text='IMU / IMU Service', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['servicelabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['sframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['sframe'].grid(column=0,row=self.gridrow, sticky='W')
		
		self.widgets['statusLabel'] = Tkinter.Label(self.widgets['sframe'],text='Status', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['statusLabel'].grid(column=0,row=0,sticky='EW')
		
		self.variables['status'] = Tkinter.StringVar()
		self.widgets['statusdata'] = Tkinter.Label(self.widgets['sframe'],textvariable=self.variables['status'], bg=self.colours['bg'], fg=self.colours['fg'], font=self.fonts['heading2'])
		self.widgets['statusdata'].grid(column=0,row=1,padx=50, sticky='EW')
		
		self.widgets['start'] = Tkinter.Button(self.widgets['sframe'],text=u"Start", image=self.images['play'], command=self.OnStartClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['start'].grid(column=1,row=1,sticky='W')
		
		self.widgets['stop'] = Tkinter.Button(self.widgets['sframe'],text=u"Stop", image=self.images['stop'], command=self.OnStopClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['stop'].grid(column=2,row=1,sticky='W')
		
		if(self.scheduler.tasks['imu_watcher'].stopped == False):
			self.variables['status'].set('Running')
			self.widgets['start'].configure(state='disabled')
		else:
			self.variables['status'].set('Stopped')
			self.widgets['stop'].configure(state='disabled')
			
		self.gridrow += 1
		
		self.widgets['orientframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['orientframe'].grid(column=0,row=self.gridrow, sticky='W')
		
		self.widgets['orientLabel'] = Tkinter.Label(self.widgets['orientframe'],text='Mounted', bg=self.colours['bg'], fg=self.colours['headingfg'], height=3)
		self.widgets['orientLabel'].grid(column=0,row=0, padx=10,sticky='EW')
		
		self.widgets['orientLabel'] = Tkinter.Label(self.widgets['orientframe'],text='Facing', bg=self.colours['bg'], fg=self.colours['headingfg'], height=3)
		self.widgets['orientLabel'].grid(column=1,row=0, padx=10,sticky='EW')
		
		self.widgets['orientLabel'] = Tkinter.Label(self.widgets['orientframe'],text=self.specification.imu['facing'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=3)
		self.widgets['orientLabel'].grid(column=2,row=0, padx=10,sticky='EW')
		
		self.widgets['orientLabel'] = Tkinter.Label(self.widgets['orientframe'],text='Offset', bg=self.colours['bg'], fg=self.colours['headingfg'], height=3)
		self.widgets['orientLabel'].grid(column=3,row=0, padx=10,sticky='EW')
		
		self.widgets['orientLabel'] = Tkinter.Label(self.widgets['orientframe'],text=self.specification.imu['offset'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=3)
		self.widgets['orientLabel'].grid(column=4,row=0, padx=10,sticky='EW')
	def showOrthographic(self):
		""" view - displays orthographic ui
		"""
		if (not IMU.isAvailable()):
			return self.unavailable()
		
		self.open()
		
		self.serviceManager()
		
		self.gridrow += 1
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='IMU / Orthographic', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='W')
		
		self.gridrow += 1
		
		self.widgets['oframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['oframe'].grid(column=0,row=self.gridrow, columnspan = 3, sticky='EW')
		
		self.widgets['rollLabel'] = Tkinter.Label(self.widgets['oframe'],text='Roll', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['rollLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['pitchLabel'] = Tkinter.Label(self.widgets['oframe'],text='Pitch', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['pitchLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.widgets['yawLabel'] = Tkinter.Label(self.widgets['oframe'],text='Yaw', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['yawLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['rollCanvas'] = Tkinter.Canvas(self.widgets['oframe'], borderwidth=0, bg=self.colours['bg'], highlightthickness=0, width=280, height=280)
		self.widgets['rollCanvas'].grid(column=0,row=self.gridrow, padx= 10,sticky='NE')
		self.shapes['rollImage'] = self.widgets['rollCanvas'].create_image(150,150, image=self.getImage('roll',0))
		
		self.widgets['pitchCanvas'] = Tkinter.Canvas(self.widgets['oframe'], borderwidth=0, bg=self.colours['bg'], highlightthickness=0, width=280, height=280)
		self.widgets['pitchCanvas'].grid(column=1,row=self.gridrow, padx= 10,sticky='NE')
		self.shapes['pitchImage'] = self.widgets['pitchCanvas'].create_image(150,150, image=self.getImage('pitch',0))
		
		self.widgets['yawCanvas'] = Tkinter.Canvas(self.widgets['oframe'], borderwidth=0, bg=self.colours['bg'], highlightthickness=0, width=280, height=280)
		self.widgets['yawCanvas'].grid(column=2,row=self.gridrow, padx= 10,sticky='NE')
		self.shapes['yawImage'] = self.widgets['yawCanvas'].create_image(150,150, image=self.getImage('yaw',0))
	def updateOrtho(self):
		""" util - updates ortho ui
		"""
		try:
			self.last
		except:
			self.last = { 'roll': 0, 'pitch': 0, 'yaw': 0 }
		try:
			metric = self.imu.metrics['complement'].value
			if(self.last['roll'] != metric['r']):
				self.last['roll'] = metric['r']
				self.widgets['rollCanvas'].itemconfigure(self.shapes['rollImage'], image=self.getImage('roll',int(-metric['r'])))
			if(self.last['pitch'] != metric['p']):
				self.last['pitch'] = metric['p']
				self.widgets['pitchCanvas'].itemconfigure(self.shapes['pitchImage'], image=self.getImage('pitch',int(-metric['p'])))
			if(self.last['yaw'] != metric['y']):
				self.last['yaw'] = metric['y']
				self.widgets['yawCanvas'].itemconfigure(self.shapes['yawImage'], image=self.getImage('yaw',int(metric['y'])))
		except:
			pass
	def unavailable(self):
		""" view - fallback for missing imu
		"""
		self.open()
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='IMU / Unavailable', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='The MPU6050 has not been detected.', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
	
	#=== ACTIONS ===#
	def OnStartClick(self):
		""" action - starts the imu service
		"""
		self.widgets['start'].configure(state='disabled')
		self.widgets['stop'].configure(state='normal')
		self.variables['status'].set('Running')
		Setting.set('imu_watch_raw', True)
		Setting.set('imu_watch_norm', True)
		Setting.set('imu_watch_low', True)
		Setting.set('imu_watch_com', True)
		self.imu.start()
		self.scheduler.startTask('ortho')
	def OnStopClick(self):
		""" action - stops the imu service
		"""
		self.widgets['start'].configure(state='normal')
		self.widgets['stop'].configure(state='disabled')
		self.variables['status'].set('Stopped')
		self.scheduler.stopTask('ortho')
		self.imu.stop()
	def OnShowOrthographicClick(self):
		""" action - dsplays the ortho page
		"""
		if(not self.dm.installRequired()):
			self.buildCache()
			self.showOrthographic()
		else:
			self.open()
			self.dm.addManager()