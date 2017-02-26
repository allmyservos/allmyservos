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

from Tkinter import *
from TkBlock import *
from TkGraphs import *
from TkDependencyManager import *

## UI for joystick configuration
class TkJoystickManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes the TkJoystickManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkJoystickManager,self).__init__(parent, gui, **options)
		self.initDependencyManager()
		if(not self.pm.installRequired()):
			if(hasattr(self.gui, 'scheduler')):
				self.scheduler = self.gui.scheduler
			else:
				self.scheduler = Scheduler.GetInstance()
				self.gui.scheduler = self.scheduler
			self.__joystickModule = self.gui.getModule('Joystick')
			self.jr = self.__joystickModule.JoystickRegistry.GetInstance(self.scheduler)
			self.gui.joystickRegistry = self.jr
	def initDependencyManager(self):
		""" setup dependency checks
		"""
		dependencies = [
			{'package':'joystick', 'installer': 'apt-get'}
		]
		self.pm = TkDependencyManager(self.widget, dependencies, 'Joystick Manager', self.gui)
	def setup(self):
		""" setup gui menu
		"""
		try:
			self.gui.menus['joystick']
		except:
			self.gui.menus['joystick'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="Joystick", menu=self.gui.menus['joystick'])
		self.gui.menus['joystick'].insert_command(2, label="Configure", command=self.OnConfigureClick)
		
	#=== VIEWS ===#
	def showConfig(self):
		""" view - show available joysticks with previews
		"""
		self.open()
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Joystick / Configure', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='W')
		
		self.gridrow += 1
		
		self.widgets['jframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['jframe'].grid(column=0,row=self.gridrow, sticky='EW')
		
		self.widgets['joysticks'] = {}
		
		self.scheduler.addTask('joystick_config_ui', self.updateConfig, 2)
	def updateConfig(self):
		""" util - manage config ui
		"""
		if (any(self.jr.joysticks)):
			# remove no joysticks message
			if ('nojoysticks' in self.widgets.keys()):
				self.widgets['nojoysticks'].grid_forget()
				del(self.widgets['nojoysticks'])
			# disconnected
			for k in self.widgets['joysticks'].keys():
				if (not k in self.jr.joysticks.keys()):
					self.widgets['joysticks'][k].widget.grid_forget()
					del(self.widgets['joysticks'][k])
			# connected
			for k, v in self.jr.joysticks.items():
				if (not k in self.widgets['joysticks'].keys()):
					self.widgets['joysticks'][k] = TkJoystick(self.widgets['jframe'], k, v, self.colours, self.images)
					self.widgets['joysticks'][k].widget.grid(column=0,row=self.gridrow, padx = 10, pady = 10, sticky='EW')
					self.gridrow += 1
		else:
			#remove all joysticks
			if (any(self.widgets['joysticks'])):
				for k in self.widgets['joysticks'].keys():
					self.widgets['joysticks'][k].widget.grid_forget()
					del(self.widgets['joysticks'][k])
			# add no joysticks message
			if (not 'nojoysticks' in self.widgets.keys()):
				self.widgets['nojoysticks'] = Tkinter.Label(self.widgets['jframe'],text='Connect a USB or Bluetooth Joystick or Gamepad.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'], font=self.fonts['heading2'])
				self.widgets['nojoysticks'].grid(column=0,row=0, padx = 10, pady = 10, sticky='EW')
	#=== ACTIONS ===#
	def OnConfigureClick(self):
		""" action - displays the configure page
		"""
		if(not self.pm.installRequired()):
			self.showConfig()
			self.jr.addCallback('TkJoystick', self.tkJoystickCallback)
		else:
			self.open()
			self.pm.addManager()
			
	def close(self):
		""" override of TkPage.close()
		hides the viewfinder
		"""
		if (hasattr(self, 'jr')):
			self.jr.removeCallback('TkJoystick')
		super(TkJoystickManager,self).close()
	def tkJoystickCallback(self,dev_num,signal,number,name,value,init):
		device = 'js%s' % dev_num
		if (device in self.widgets['joysticks'].keys()):
			self.widgets['joysticks'][device].update(signal,number,name,value,init)
class TkJoystick(TkBlock):
	def __init__(self, parent, device, joystick, colours={}, images={}):
		""" initializes the TkJoystick object
		
		@param parent
		@param device str
		@param joystick Joystick object
		@param colours dict
		@param images dict
		"""
		self.widget = Frame(parent)
		self.widgets = {}
		self.device = device
		self.joystick = joystick
		self.initColours(colours)
		self.initImages(images)
		self.dualAxis = self.joystick.dual_axis
		self.singleAxis = self.joystick.single_axis
		self.setup()
	def initColours(self, colours):
		""" setup colours
		"""
		try:
			TkJoystick.colours
		except:
			TkJoystick.colours = colours
		self.widget.configure(borderwidth=3, bg = TkJoystick.colours['bg'], highlightthickness=1, highlightbackground=TkJoystick.colours['activebg'])
	def initImages(self, images):
		""" setup images
		"""
		try:
			TkJoystick.images
		except:
			TkJoystick.images = images
	def setup(self):
		""" setup servo joystick ui
		"""
		gridrow = 0
		self.widgets['nameLabel'] = Tkinter.Label(self.widget,text='Name', anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['headingfg'], width=15)
		self.widgets['nameLabel'].grid(column=0,row=gridrow, sticky='EW')
		self.widgets['nameData'] = Tkinter.Label(self.widget,text=self.joystick.info['name'], anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['valuefg'])
		self.widgets['nameData'].grid(column=1,row=gridrow, sticky='EW')
		
		gridrow += 1
		
		self.widgets['devLabel'] = Tkinter.Label(self.widget,text='Device', anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['headingfg'], width=15)
		self.widgets['devLabel'].grid(column=0,row=gridrow, sticky='EW')
		self.widgets['devData'] = Tkinter.Label(self.widget,text=self.device, anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['valuefg'])
		self.widgets['devData'].grid(column=1,row=gridrow, sticky='EW')
		
		gridrow += 1
		
		self.widgets['axisLabel'] = Tkinter.Label(self.widget,text='Axis', anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['headingfg'], width=15)
		self.widgets['axisLabel'].grid(column=0,row=gridrow, sticky='NW')
		
		self.widgets['aframe'] = Tkinter.Frame(self.widget, bg=self.colours['bg'])
		self.widgets['aframe'].grid(column=1,row=gridrow, sticky='EW')
		
		self.widgets['anframe'] = Tkinter.Frame(self.widgets['aframe'], bg=self.colours['bg'])
		self.widgets['anframe'].grid(column=0,row=gridrow, sticky='EW')
		
		self.widgets['anumLabel'] = Tkinter.Label(self.widgets['anframe'],text='Total:', anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['headingfg'])
		self.widgets['anumLabel'].grid(column=0,row=0, sticky='EW')
		self.widgets['anumData'] = Tkinter.Label(self.widgets['anframe'],text=self.joystick.info['num_axis'], anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['valuefg'])
		self.widgets['anumData'].grid(column=1,row=0, sticky='EW')
		
		gridrow += 1
		col = 0
		if (any(self.joystick.info['axis_map'])):
			self.widgets['axis'] = {}
			for k,v in self.dualAxis.items():
				if (k in self.joystick.info['axis_map'] and v in self.joystick.info['axis_map']):
					self.widgets['axis'][k] = TkJoystickDualAxis(self.widgets['aframe'], k, v, self.colours, self.images)
					self.widgets['axis'][k].widget.grid(column=col,row=gridrow, sticky='NW')
					self.widgets['axis'][v] = self.widgets['axis'][k]
					col += 1
			for k,v in self.singleAxis.items():
				if (k in self.joystick.info['axis_map']):
					self.widgets['axis'][k] = TkJoystickAxis(self.widgets['aframe'], k, self.colours, self.images, v)
					self.widgets['axis'][k].widget.grid(column=col,row=gridrow, sticky='NW')
					col += 1
			
		gridrow += 1
		
		self.widgets['buttonLabel'] = Tkinter.Label(self.widget,text='Buttons', anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['headingfg'], width=15)
		self.widgets['buttonLabel'].grid(column=0,row=gridrow, sticky='NW')
		
		self.widgets['bframe'] = Tkinter.Frame(self.widget, bg=self.colours['bg'])
		self.widgets['bframe'].grid(column=1,row=gridrow, sticky='EW')
		
		self.widgets['bnframe'] = Tkinter.Frame(self.widgets['bframe'], bg=self.colours['bg'])
		self.widgets['bnframe'].grid(column=0,row=gridrow, sticky='EW')
		
		self.widgets['bnumLabel'] = Tkinter.Label(self.widgets['bnframe'],text='Total:', anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['headingfg'])
		self.widgets['bnumLabel'].grid(column=0,row=gridrow, sticky='EW')
		self.widgets['bnumData'] = Tkinter.Label(self.widgets['bnframe'],text=self.joystick.info['num_buttons'], anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['valuefg'])
		self.widgets['bnumData'].grid(column=1,row=gridrow, sticky='EW')
		
		gridrow += 1
		col = 0
		if (any(self.joystick.info['button_map'])):
			self.widgets['buttons'] = []
			for x in self.joystick.info['button_map']:
				self.widgets['buttons'].append(TkJoystickButton(self.widgets['bframe'], x, self.colours, self.images))
				self.widgets['buttons'][-1].widget.grid(column=col,row=gridrow, sticky='EW')
				col += 1
				if (col == 10):
					col = 0
					gridrow += 1
		gridrow += 1
		
		self.widgets['cbLabel'] = Tkinter.Label(self.widget,text='Callbacks', anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['headingfg'], width=15)
		self.widgets['cbLabel'].grid(column=0,row=gridrow, sticky='NW')
		
		self.widgets['cbframe'] = Tkinter.Frame(self.widget, bg=self.colours['bg'])
		self.widgets['cbframe'].grid(column=1,row=gridrow, sticky='EW')
		
		if any(self.joystick.callbacks):
			for x in self.joystick.callbacks.keys():
				self.widgets['nocbLabel'] = Tkinter.Label(self.widgets['cbframe'],text=x, anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['valuefg'])
				self.widgets['nocbLabel'].grid(column=0,row=gridrow, sticky='NW')
				gridrow += 1
		else:
			self.widgets['nocbLabel'] = Tkinter.Label(self.widgets['cbframe'],text='No callbacks', anchor=NW, bg=TkJoystick.colours['bg'], fg=TkJoystick.colours['fg'])
			self.widgets['nocbLabel'].grid(column=0,row=gridrow, sticky='NW')
	def update(self,signal,number,name,value,init):
		""" update preview widgets
		"""
		if (signal == 'axis'):
			if (name in self.singleAxis.keys()):
				self.widgets['axis'][name].update(value)
			elif (name in self.dualAxis.keys()):
				self.widgets['axis'][name].update('x',value)
			elif (name in self.dualAxis.values()):
				self.widgets['axis'][name].update('y',value)
		elif(signal == 'button'):
			try:
				self.widgets['buttons'][number].update(value)
			except:
				pass
class TkJoystickAxis(TkBlock):
	def __init__(self, parent, name, colours={}, images={}, horizontal = True):
		""" Initializes the TkJoystickAxis object
		
		@param parent
		@param colours
		@param images
		"""
		self.widget = Tkinter.Frame(parent)
		self.widgets = {}
		self.name = name
		self.horizontal = horizontal
		self._value = Tkinter.DoubleVar()
		self._value.set(0)
		self.initColours(colours)
		self.initImages(images)
		self.setup()
	def initColours(self, colours):
		""" setup colours
		"""
		try:
			TkJoystickAxis.colours
		except:
			TkJoystickAxis.colours = colours
		try:
			self.widget.configure(borderwidth=3, bg = TkJoystickAxis.colours['bg'])
		except:
			self.widget.configure(borderwidth=3)
	def initImages(self, images):
		""" setup images
		"""
		try:
			TkJoystickAxis.images
		except:
			TkJoystickAxis.images = images
	def setup(self):
		""" setup axis ui
		"""
		gridrow = 0
		
		self.widgets['label'] = Tkinter.Label(self.widget,text=self.name, anchor=S, bg=TkJoystickAxis.colours['bg'], fg=TkJoystickAxis.colours['headingfg'])
		self.widgets['label'].grid(column=0,row=gridrow, sticky='EW')
		
		gridrow += 1
		
		size = (20, 100) if self.horizontal else (100, 20)
		self.widgets['graph'] = TkBarGraph(self.widget, TkJoystickAxis.colours, height = size[0], width = size[1], grange = { 'min': -1, 'max': 1}, horizontal = self.horizontal)
		self.widgets['graph'].widget.grid(column=0,row=gridrow, sticky='N')
		self.widgets['graph'].update(0)
		
		gridrow += 1
		
		self.widgets['value'] = Tkinter.Label(self.widget,textvariable=self._value, anchor=N, bg=TkJoystickAxis.colours['bg'], fg=TkJoystickAxis.colours['valuefg'], width=5)
		self.widgets['value'].grid(column=0,row=gridrow, sticky='EW')
		
	def update(self, value):
		""" update preview widgets
		"""
		self.widgets['graph'].update(float(value))
		self._value.set(round(float(value),3))
class TkJoystickDualAxis(TkBlock):
	def __init__(self, parent, xname, yname, colours={}, images={}):
		""" Initializes the TkJoystickDualAxis object
		
		@param parent
		@param colours
		@param images
		"""
		self.widget = Tkinter.Frame(parent)
		self.widgets = {}
		self.shapes = {}
		self.axisNames = (xname, yname)
		self.size = (100, 100)
		self._x = Tkinter.DoubleVar()
		self._x.set(0)
		self._y = Tkinter.DoubleVar()
		self._y.set(0)
		self.initColours(colours)
		self.initImages(images)
		self.setup()
	def initColours(self, colours):
		""" setup colours
		"""
		try:
			TkJoystickDualAxis.colours
		except:
			TkJoystickDualAxis.colours = colours
		try:
			self.widget.configure(borderwidth=3, bg = TkJoystickDualAxis.colours['bg'])
		except:
			self.widget.configure(borderwidth=3)
	def initImages(self, images):
		""" setup images
		"""
		try:
			TkJoystickDualAxis.images
		except:
			TkJoystickDualAxis.images = images
	def setup(self):
		""" setup dual axis ui
		"""
		gridrow = 0
		
		self.widgets['plabel'] = Tkinter.Label(self.widget,text='{} / {}'.format(self.axisNames[0],self.axisNames[1]), anchor=S, bg=TkJoystickDualAxis.colours['bg'], fg=TkJoystickDualAxis.colours['headingfg'])
		self.widgets['plabel'].grid(column=1,row=gridrow, sticky='EW')
		
		gridrow += 1
		
		self.widgets['yframe'] = Tkinter.Frame(self.widget, bg=self.colours['bg'])
		self.widgets['yframe'].grid(column=0,row=gridrow, sticky='EW')
		
		self.widgets['ylabel'] = Tkinter.Label(self.widgets['yframe'],text=self.axisNames[1], anchor=S, bg=TkJoystickDualAxis.colours['bg'], fg=TkJoystickDualAxis.colours['headingfg'])
		self.widgets['ylabel'].grid(column=0,row=0, sticky='EW')
		
		self.widgets['yval'] = Tkinter.Label(self.widgets['yframe'],textvariable=self._y, anchor=S, bg=TkJoystickDualAxis.colours['bg'], fg=TkJoystickDualAxis.colours['valuefg'], width=5)
		self.widgets['yval'].grid(column=0,row=1, sticky='EW')
		
		self.widgets['canvas'] = Tkinter.Canvas(self.widget, width=self.size[0], height=self.size[1], bg=self.colours['bg'], highlightthickness=2, highlightbackground=self.colours['greyborder'])
		self.widgets['canvas'].grid(column=1,row=gridrow, sticky='EW')
		
		self.shapes['x'] = self.widgets['canvas'].create_line(*self.xLineCoords(), fill=self.colours['graphbar'], width=3)
		self.shapes['y'] = self.widgets['canvas'].create_line(*self.yLineCoords(), fill=self.colours['graphbar'], width=3)
		
		gridrow += 1
		
		self.widgets['xframe'] = Tkinter.Frame(self.widget, bg=self.colours['bg'])
		self.widgets['xframe'].grid(column=1,row=gridrow, sticky='EW')
		self.widgets['xframe'].columnconfigure(0, weight=2)
		self.widgets['xlabel'] = Tkinter.Label(self.widgets['xframe'],text=self.axisNames[0], anchor=N, bg=TkJoystickDualAxis.colours['bg'], fg=TkJoystickDualAxis.colours['headingfg'])
		self.widgets['xlabel'].grid(column=0,row=0, sticky='EW')
		
		self.widgets['xval'] = Tkinter.Label(self.widgets['xframe'],textvariable=self._x, anchor=N, bg=TkJoystickDualAxis.colours['bg'], fg=TkJoystickDualAxis.colours['valuefg'], width=5)
		self.widgets['xval'].grid(column=0,row=1, sticky='EW')
	def xLineCoords(self):
		""" get coordinates for x axis line
		"""
		lineLength = 20
		clippedx = self.size[0] / 2 - lineLength / 2
		clippedy = self.size[1] / 2 - lineLength / 2
		ax = (self.size[0] / 2 - lineLength / 2) + clippedx * self._x.get()
		ay = (self.size[1] / 2) + clippedy * self._y.get()
		bx = ax + lineLength
		by = ay
		return [ax, ay, bx, by]
	def yLineCoords(self):
		""" get coordinates for y axis line
		"""
		lineLength = 20
		clippedx = self.size[0] / 2 - lineLength / 2
		clippedy = self.size[1] / 2 - lineLength / 2
		ax = (self.size[0] / 2) + clippedx * self._x.get()
		ay = (self.size[1] / 2 - lineLength / 2) + clippedy * self._y.get()
		bx = ax
		by = ay + lineLength
		return [ax, ay, bx, by]
	def update(self, axis, value):
		""" update dual axis ui
		"""
		value = round(float(value), 3)
		if (axis == 'x'):
			self._x.set(value)
		else:
			self._y.set(value)
		self.widgets['canvas'].coords(self.shapes['x'], *self.xLineCoords())
		self.widgets['canvas'].coords(self.shapes['y'], *self.yLineCoords())
class TkJoystickButton(TkBlock):
	def __init__(self, parent, name, colours={}, images={}):
		""" Initializes the TkJoystickButton object
		
		@param parent
		@param colours
		@param images
		"""
		self.widget = Tkinter.Frame(parent)
		self.widgets = {}
		self.name = name
		self._value = Tkinter.BooleanVar()
		self._value.set(False)
		self.initColours(colours)
		self.initImages(images)
		self.setup()
	def initColours(self, colours):
		""" setup colours
		"""
		try:
			TkJoystickButton.colours
		except:
			TkJoystickButton.colours = colours
		try:
			self.widget.configure(borderwidth=3, bg = TkJoystickButton.colours['bg'])
		except:
			self.widget.configure(borderwidth=3)
	def initImages(self, images):
		""" setup images
		"""
		try:
			TkJoystickButton.images
		except:
			TkJoystickButton.images = images
	def setup(self):
		gridrow = 0
		
		self.widgets['label'] = Tkinter.Label(self.widget,text=self.name, anchor=S, bg=TkJoystickButton.colours['bg'], fg=TkJoystickButton.colours['headingfg'])
		self.widgets['label'].grid(column=0,row=gridrow, sticky='EW')
		
		gridrow += 1
		
		self.widgets['val'] = Tkinter.Label(self.widget,text='On' if self._value.get() == True else 'Off', anchor=S, bg=TkJoystickButton.colours['bg'], fg = self.colours['valuefg'] if self._value.get() == True else self.colours['fg'])
		self.widgets['val'].grid(column=0,row=gridrow, sticky='EW')
	def update(self, value):
		""" update button ui
		"""
		self._value.set(True if value == 1 else False)
		self.widgets['val'].configure(text='On' if self._value.get() == True else 'Off', fg = self.colours['valuefg'] if self._value.get() == True else self.colours['fg'])