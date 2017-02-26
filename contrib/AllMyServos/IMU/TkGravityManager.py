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
import Tkinter, os, Specification, cmath, math, copy
from __bootstrap import AmsEnvironment
from Tkinter import *
from TkBlock import *
from TkDependencyManager import *
from Setting import *
from IMU import IMU

## UI for gravity demo
class TkGravityManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes TkGravityManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkGravityManager,self).__init__(parent, gui, **options)
		self.initDependencyManager()
		if(hasattr(self.gui, 'scheduler')):
			self.scheduler = self.gui.scheduler
		else:
			self.scheduler = Scheduler.GetInstance()
		if(not self.pm.installRequired()):
			if(hasattr(self.gui, 'imu')):
				self.imu = self.gui.imu
			else:
				self.imu = self.gui.imu = IMU(self.scheduler, (not Setting.get('imu_autostart', False)))
			self.groundcoords = [[0, 237], [800, 237], [800, 800], [0, 800]]
			self.centre = complex(237,237)
			self.shapes = {}
			self.cache = {}
			self.basepath = AmsEnvironment.AppPath()
			self.pimg = self.gui.getModule('PIL.Image')
			self.tkimg = self.gui.getModule('PIL.ImageTk')
			self.initImages()
			self.scheduler.addTask('gravity_display', self.updateGravity, 0.2, True)
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
		self.pm = TkDependencyManager(self.widget, dependencies, 'Gravity Manager', self.gui)
	def initImages(self):
		""" setup required images
		"""
		self.oimages = {}
		self.oimages['reticle'] = self.pimg.Image.open(os.path.join(self.basepath, 'images/horizon/reticle.png')).convert('RGBA')
		self.oimages['mask'] = self.pimg.Image.open(os.path.join(self.basepath, 'images/horizon/mask.png')).convert('RGBA')
	def getImage(self, name, angle):
		""" gets an image from cache or caches it
		
		@param name
		@param angle
		"""
		try:
			self.cache[name]
		except:
			self.cache[name] = {}
		try:
			self.cache[name][angle]
		except:
			self.cache[name][angle] = self.tkimg.ImageTk.PhotoImage(self.oimages[name].rotate(angle))
		return self.cache[name][angle]
	def setup(self):
		""" setup gui menu
		"""
		try:
			self.gui.menus['imu']
		except:
			self.gui.menus['imu'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="IMU", menu=self.gui.menus['imu'])
		self.gui.menus['imu'].insert_command(2, label="Gravity", command=self.OnGravityClick)
	
	#=== VIEWS ===#
	def serviceManager(self):
		""" view - imu service manager
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
	def showGravity(self):
		""" view - displays graviry ui
		"""
		if (not IMU.isAvailable()):
			return self.unavailable()
		
		self.open()
		
		self.serviceManager()
		
		self.gridrow += 1
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='IMU / Gravity', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='W')
		
		self.gridrow += 1
		
		self.widgets['gframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['gframe'].grid(column=0,row=self.gridrow, columnspan = 3, sticky='EW')
		self.widgets['gframe'].columnconfigure(0, weight=1)
		self.widgets['tframe'].columnconfigure(0, weight=1)

		self.widgets['rollLabel'] = Tkinter.Label(self.widgets['gframe'],text='TBD', bg=self.colours['bg'], fg=self.colours['fg'], font=self.fonts['heading2'])
		self.widgets['rollLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['hCanvas'] = Tkinter.Canvas(self.widgets['gframe'], borderwidth=0, bg=self.colours['bg'], highlightthickness=0, width=474, height=474)
		self.widgets['hCanvas'].grid(column=0,row=self.gridrow, padx= 10,sticky='EW')
		self.shapes['skyplane'] = self.widgets['hCanvas'].create_polygon([(0, 0), (474, 0), (474, 474), (0, 474)], fill='#fff')
		self.shapes['groundplane'] = self.widgets['hCanvas'].create_polygon(self.groundcoords, fill='#828282')
		self.shapes['mask'] = self.widgets['hCanvas'].create_image(self.centre.real, self.centre.imag, image=self.getImage('mask',0))
		self.shapes['reticle'] = self.widgets['hCanvas'].create_image(self.centre.real, self.centre.imag, image=self.getImage('reticle',0))
		
		self.widgets['pitchLabel'] = Tkinter.Label(self.widgets['gframe'],text='TBD', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], font=self.fonts['heading2'])
		self.widgets['pitchLabel'].grid(column=1,row=self.gridrow,sticky='NS')
	def updateGravity(self):
		""" util - updates gravity ui
		"""
		try:
			self.last
		except:
			self.last = { 'roll': 0, 'pitch': 0, 'yaw': 0 }
		metric = self.imu.metrics['acc_ang'].value
		if(metric != None):
			p = int(metric['p'])
			r = int(metric['r'])
			if(self.last['pitch'] != p or self.last['roll'] != r):
				newcoords = [x[:] for x in self.groundcoords]
				if(self.last['pitch'] != p):
					self.last['pitch'] = p
					self.widgets['pitchLabel'].configure(text=str(p), fg=self.colours['valuefg'])
				for c in newcoords:
					c[1] += 4.444 * -p
				if(self.last['roll'] != r):
					self.last['roll'] = r
					self.widgets['rollLabel'].configure(text=str(r), fg=self.colours['valuefg'])
				cangle = cmath.exp(math.radians(r)*1j)
				newpoly = []
				for x, y in newcoords:
					new = cangle * (complex(x,y) - self.centre) + self.centre
					newpoly.append(int(new.real))
					newpoly.append(int(new.imag))
				self.widgets['hCanvas'].coords(self.shapes['groundplane'], *newpoly)
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
		Setting.set('imu_watch_norm', True)
		Setting.set('imu_watch_low', True)
		Setting.set('imu_watch_ang', True)
		self.imu.start()
		self.scheduler.startTask('gravity_display')
	def OnStopClick(self):
		""" action - stops the imu service
		"""
		self.widgets['start'].configure(state='normal')
		self.widgets['stop'].configure(state='disabled')
		self.variables['status'].set('Stopped')
		self.scheduler.stopTask('gravity_display')
		self.imu.stop()
	def OnToggleAutostartClick(self):
		""" action - toggles imu service autostart
		"""
		self.autostart = Setting.set('imu_autostart', self.variables['autostart'].get())
	def OnGravityClick(self):
		""" action - displays the gravity page
		"""
		if(not self.pm.installRequired()):
			self.showGravity()
		else:
			self.open()
			self.pm.addManager()