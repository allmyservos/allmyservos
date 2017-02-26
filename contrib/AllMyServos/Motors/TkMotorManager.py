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
import Tkinter, Keyboard, TkJoystickManager, copy
from TkBlock import *
from Motors import *

## UI for motors
class TkMotorManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes TkMotorManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkMotorManager,self).__init__(parent, gui, **options)
		self.gpioInfo = [
			{ 'number': 1, 'name': '3V3 1', 'default_usage': '3v' },
			{ 'number': 2, 'name': '5V 1', 'default_usage': '5v' },
			{ 'number': 3, 'name': 'SDA', 'default_usage': 'i2c' },
			{ 'number': 4, 'name': '5V 2', 'default_usage': '5v', },
			{ 'number': 5, 'name': 'SCL', 'default_usage': 'i2c' },
			{ 'number': 6, 'name': 'GND 1', 'default_usage': 'gnd' },
			{ 'number': 7, 'name': 'GPIO 4', 'default_usage': 'gpio' },
			{ 'number': 8, 'name': 'TXD', 'default_usage': 'uart' },
			{ 'number': 9, 'name': 'GND 2', 'default_usage': 'gnd' },
			{ 'number': 10, 'name': 'RXD', 'default_usage': 'uart' },
			{ 'number': 11, 'name': 'GPIO 17', 'default_usage': 'gpio' },
			{ 'number': 12, 'name': 'GPIO 18', 'default_usage': 'gpio' },
			{ 'number': 13, 'name': 'GPIO 27', 'default_usage': 'gpio' },
			{ 'number': 14, 'name': 'GND 3', 'default_usage': 'gnd' },
			{ 'number': 15, 'name': 'GPIO 22', 'default_usage': 'gpio' },
			{ 'number': 16, 'name': 'GPIO 23', 'default_usage': 'gpio' },
			{ 'number': 17, 'name': '3V3 2', 'default_usage': '3v' },
			{ 'number': 18, 'name': 'GPIO 24', 'default_usage': 'gpio' },
			{ 'number': 19, 'name': 'MOSI', 'default_usage': 'spi' },
			{ 'number': 20, 'name': 'GND 4', 'default_usage': 'gnd' },
			{ 'number': 21, 'name': 'MISO', 'default_usage': 'spi' },
			{ 'number': 22, 'name': 'GPIO 25', 'default_usage': 'gpio' },
			{ 'number': 23, 'name': 'CLK', 'default_usage': 'spi' },
			{ 'number': 24, 'name': 'CE0', 'default_usage': 'spi' },
			{ 'number': 25, 'name': 'GND 5', 'default_usage': 'gnd' },
			{ 'number': 26, 'name': 'CE1', 'default_usage': 'spi' },
			{ 'number': 27, 'name': 'ID_SD', 'default_usage': 'i2c' },
			{ 'number': 28, 'name': 'ID_SC', 'default_usage': 'i2c' },
			{ 'number': 29, 'name': 'GPIO 5', 'default_usage': 'gpio' },
			{ 'number': 30, 'name': 'GND 6', 'default_usage': 'gnd' },
			{ 'number': 31, 'name': 'GPIO 6', 'default_usage': 'gpio' },
			{ 'number': 32, 'name': 'GPIO 12', 'default_usage': 'gpio' },
			{ 'number': 33, 'name': 'GPIO 13', 'default_usage': 'gpio' },
			{ 'number': 34, 'name': 'GND 7', 'default_usage': 'gnd' },
			{ 'number': 35, 'name': 'GPIO 19', 'default_usage': 'gpio' },
			{ 'number': 36, 'name': 'GPIO 16', 'default_usage': 'gpio' },
			{ 'number': 37, 'name': 'GPIO 26', 'default_usage': 'gpio' },
			{ 'number': 38, 'name': 'GPIO 20', 'default_usage': 'gpio' },
			{ 'number': 39, 'name': 'GND 8', 'default_usage': 'gnd' },
			{ 'number': 40, 'name': 'GPIO 21', 'default_usage': 'gpio' },
		]
		self.specification = gui.specification
		self.shapes = {}
		self.kbthread = Keyboard.KeyboardThread.GetInstance()
	def setup(self):
		""" setup gui menu
		"""
		self.gui.menus['motors'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		self.gui.menus['motors'].add_command(label="New DC Motor", command=self.OnAddDCMotorClick)
		self.gui.menus['motors'].add_command(label="New Stepper Motor", command=self.OnAddStepperMotorClick)
		self.gui.menus['motors'].add_separator()
		self.gui.menus['motors'].add_command(label="DC Motors", command=self.OnListDCMotorsClick)
		self.gui.menus['motors'].add_command(label="Stepper Motors", command=self.OnListStepperMotorsClick)
		self.addMenu(label="Motors", menu=self.gui.menus['motors'])
	
	#=== VIEWS ===#
	def listDCMotors(self):
		""" view - list dc motors
		"""
		self.open()
		
		self.widgets['molabel'] = Tkinter.Label(self.widgets['tframe'],text='Motors / DC Motors', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['molabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		self.widgets['addmotor'] = Tkinter.Button(self.widgets['tframe'],text=u"Add DC Motor", image=self.images['add'], command=self.OnAddDCMotorClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addmotor'].grid(column=5,row=self.gridrow)
		
		self.gridrow += 1
		
		if (any(self.specification.motors)):
			self.widgets['cLabel'] = Tkinter.Label(self.widgets['tframe'],text='Controllers', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['cLabel'].grid(column=3,row=self.gridrow,columnspan=2,sticky='EW')
			self.gridrow += 1
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['dtLabel'] = Tkinter.Label(self.widgets['tframe'],text='Drive Type', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['dtLabel'].grid(column=1,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['pinsLabel'] = Tkinter.Label(self.widgets['tframe'],text='Pins', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['pinsLabel'].grid(column=2,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['jsLabel'] = Tkinter.Label(self.widgets['tframe'],text='Joystick', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['jsLabel'].grid(column=3,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['kbLabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyboard', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['kbLabel'].grid(column=4,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['tframe'],text='Edit', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['editLabel'].grid(column=5,row=self.gridrow,sticky='EW')
			self.widgets['controllersLabel'] = Tkinter.Label(self.widgets['tframe'],text='Controllers', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['controllersLabel'].grid(column=6,row=self.gridrow,sticky='EW')
			self.widgets['delLabel'] = Tkinter.Label(self.widgets['tframe'],text='Delete', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['delLabel'].grid(column=7,row=self.gridrow,sticky='EW')
			
			self.gridrow += 1
			rowcount = 1
			for k,v in self.specification.motors.items():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				
				self.widgets['name'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=v.jsonData['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['name'+str(self.gridrow)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['dt'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=v.driveTypes[v.driveType]['label'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['dt'+str(self.gridrow)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['pins'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=len(v.pins), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['pins'+str(self.gridrow)].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['js'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=len(v.controllers['joystick']), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['js'+str(self.gridrow)].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['kb'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=len(v.controllers['keyboard']), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['kb'+str(self.gridrow)].grid(column=4,row=self.gridrow,sticky='EW')
				self.widgets['edit'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnEditDCMotorClick(x))
				self.widgets['edit'+str(self.gridrow)].grid(column=5,row=self.gridrow,sticky='EW')
				self.widgets['controllers'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Controllers", image=self.images['joystick'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnEditDCMotorControllersClick(x))
				self.widgets['controllers'+str(self.gridrow)].grid(column=6,row=self.gridrow,sticky='EW')
				self.widgets['del'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Delete", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnDeleteDCMotorClick(x))
				self.widgets['del'+str(self.gridrow)].grid(column=7,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['nomotorslabel'] = Tkinter.Label(self.widgets['tframe'],text="There are currently no motors", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nomotorslabel'].grid(column=0,row=self.gridrow,sticky='EW')
	def listStepperMotors(self):
		""" view - list stepper motors
		"""
		self.open()
		
		self.widgets['molabel'] = Tkinter.Label(self.widgets['tframe'],text='Motors / Stepper Motors', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['molabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		self.widgets['addmotor'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Stepper Motor", image=self.images['add'], command=self.OnAddStepperMotorClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addmotor'].grid(column=5,row=self.gridrow)
		
		self.gridrow += 1
		
		if (any(self.specification.steppers)):
			self.widgets['cLabel'] = Tkinter.Label(self.widgets['tframe'],text='Controllers', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['cLabel'].grid(column=3,row=self.gridrow,columnspan=2,sticky='EW')
			self.gridrow += 1
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['rpmLabel'] = Tkinter.Label(self.widgets['tframe'],text='RPM', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['rpmLabel'].grid(column=1,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['pinsLabel'] = Tkinter.Label(self.widgets['tframe'],text='Pins', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['pinsLabel'].grid(column=2,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['jsLabel'] = Tkinter.Label(self.widgets['tframe'],text='Joystick', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['jsLabel'].grid(column=3,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['kbLabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyboard', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['kbLabel'].grid(column=4,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['tframe'],text='Edit', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['editLabel'].grid(column=5,row=self.gridrow,sticky='EW')
			self.widgets['controllersLabel'] = Tkinter.Label(self.widgets['tframe'],text='Controllers', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['controllersLabel'].grid(column=6,row=self.gridrow,sticky='EW')
			self.widgets['delLabel'] = Tkinter.Label(self.widgets['tframe'],text='Delete', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['delLabel'].grid(column=7,row=self.gridrow,sticky='EW')
			
			self.gridrow += 1
			rowcount = 1
			for k,v in self.specification.steppers.items():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				
				self.widgets['name'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=v.jsonData['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['name'+str(self.gridrow)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['rpm'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=v.jsonData['rpm'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['rpm'+str(self.gridrow)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['pins'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=len(v.pins), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['pins'+str(self.gridrow)].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['js'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=len(v.controllers['joystick']), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['js'+str(self.gridrow)].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['kb'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=len(v.controllers['keyboard']), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['kb'+str(self.gridrow)].grid(column=4,row=self.gridrow,sticky='EW')
				self.widgets['edit'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnEditStepperMotorClick(x))
				self.widgets['edit'+str(self.gridrow)].grid(column=5,row=self.gridrow,sticky='EW')
				self.widgets['controllers'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Controllers", image=self.images['joystick'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnEditStepperMotorControllersClick(x))
				self.widgets['controllers'+str(self.gridrow)].grid(column=6,row=self.gridrow,sticky='EW')
				self.widgets['del'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Delete", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnDeleteStepperMotorClick(x))
				self.widgets['del'+str(self.gridrow)].grid(column=7,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['nomotorslabel'] = Tkinter.Label(self.widgets['tframe'],text="There are currently no motors", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nomotorslabel'].grid(column=0,row=self.gridrow,sticky='EW')
	def editMotor(self):
		""" view - edit dc or stepper motor
		"""
		self.open()
		
		self.widgets['molabel'] = Tkinter.Label(self.widgets['tframe'],text='Motors / %s %s Motor' % (('Add' if not self.motor.blobExists() else 'Edit'), 'DC' if self.motor.jbType == 'DcMotor' else 'Stepper'), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['molabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['gpio'] = self.displayGpio(self.widgets['tframe'])
		self.widgets['gpio'].grid(column=4,row=self.gridrow, rowspan=10, sticky='NW')
		
		self.widgets['nlabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['nlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.variables['name'] = Tkinter.StringVar()
		self.widgets['nameentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['name'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['nameentry'].grid(column=1,row=self.gridrow, padx=10, pady=5,sticky='EW')
		if self.motor.blobExists():
			self.variables['name'].set(self.motor.jsonData['name'])
		
		self.gridrow += 1
		
		if (self.motor.jbType == 'DcMotor'):
			self.widgets['tlabel'] = Tkinter.Label(self.widgets['tframe'],text='Drive Type', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['tlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
			self.variables['drivetype'] = Tkinter.StringVar()
			self.variables['drivetype'].set(self.motor.driveType)
			self.widgets['dtentry'] = Tkinter.OptionMenu(self.widgets['tframe'],self.variables['drivetype'], *self.motor.driveTypes.keys())
			self.widgets['dtentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
			self.widgets['dtentry'].grid(column=1,row=self.gridrow,padx=10,sticky='EW')
			
			self.widgets['rfrefreshbutton'] = Tkinter.Button(self.widgets['tframe'],text=u"Refresh", image=self.images['accept'], command=self.OnDriveTypeChangeClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['rfrefreshbutton'].grid(column=2,row=self.gridrow,sticky='W')
		
			self.gridrow += 1
			
			self.widgets['tlabel'] = Tkinter.Label(self.widgets['tframe'],text='Compatible with', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['tlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.widgets['compatible'] = { 'frame': Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg']), 'boards': {}}
			self.widgets['compatible']['frame'].grid(column=1,row=self.gridrow, sticky='EW')
			
			self.gridrow += 1
		self.widgets['plabel'] = Tkinter.Label(self.widgets['tframe'],text='Pins', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['plabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.widgets['pframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['pframe'].grid(column=1,row=self.gridrow, sticky='EW')
		
		self.updatePins()
		
		self.gridrow += 1
		
		if (self.motor.jbType == 'StepperMotor'):
			self.widgets['rpmlabel'] = Tkinter.Label(self.widgets['tframe'],text='Max. RPM', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['rpmlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.variables['rpm'] = Tkinter.IntVar()
			self.widgets['rpmentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['rpm'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
			self.widgets['rpmentry'].grid(column=1,row=self.gridrow, padx=10, pady=5,sticky='EW')
			self.variables['rpm'].set(self.motor.jsonData['rpm'])
			
			self.gridrow += 1
			
			self.widgets['stepslabel'] = Tkinter.Label(self.widgets['tframe'],text='Steps Per Rev', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['stepslabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.variables['steps'] = Tkinter.IntVar()
			self.widgets['stepsentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['steps'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
			self.widgets['stepsentry'].grid(column=1,row=self.gridrow, padx=10, pady=5,sticky='EW')
			self.variables['steps'].set(self.motor.jsonData['steps_per_rev'])
			
			self.gridrow += 1
			
			self.widgets['orderlabel'] = Tkinter.Label(self.widgets['tframe'],text='Output Order', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['orderlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.variables['order'] = Tkinter.StringVar()
			self.variables['order'].set(self.motor.getOutputOrder())
			self.widgets['orderentry'] = Tkinter.OptionMenu(self.widgets['tframe'],self.variables['order'], *self.motor.outputOrders.keys())
			self.widgets['orderentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
			self.widgets['orderentry'].grid(column=1,row=self.gridrow,padx=10,sticky='EW')
			
			self.widgets['rfrefreshbutton'] = Tkinter.Button(self.widgets['tframe'],text=u"Refresh", image=self.images['accept'], command=self.OnOutputOrderRefreshClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['rfrefreshbutton'].grid(column=2,row=self.gridrow,sticky='W')
			
			self.gridrow += 1
			
			self.widgets['seqlabel'] = Tkinter.Label(self.widgets['tframe'],text='Sequence', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['seqlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.widgets['seqframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
			self.widgets['seqframe'].grid(column=1,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.variables['sequence'] = Tkinter.StringVar()
			self.variables['sequence'].set(self.motor.jsonData['sequence_key'] if 'sequence_key' in self.motor.jsonData.keys() else 'half_step')
			self.widgets['halfstep'] = Radiobutton(self.widgets['seqframe'], text='Half Step', variable=self.variables['sequence'], value='half_step', command=self.OnChangeSequence, selectcolor=self.colours['bg'], bg=self.colours['bg'], activebackground=self.colours['activebg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'])
			self.widgets['halfstep'].grid(column=0,row=0,padx=10,sticky='W')
			
			self.widgets['fullstep'] = Radiobutton(self.widgets['seqframe'], text='Full Step', variable=self.variables['sequence'], value='full_step', command=self.OnChangeSequence, selectcolor=self.colours['bg'], bg=self.colours['bg'], activebackground=self.colours['activebg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'])
			self.widgets['fullstep'].grid(column=1,row=0,padx=10,sticky='W')
			
			self.gridrow += 1
			
			self.widgets['normlabel'] = Tkinter.Label(self.widgets['tframe'],text='Normalize Angle', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['normlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.variables['normalize'] = Tkinter.BooleanVar()
			self.variables['normalize'].set(self.motor.normalizeAngle)
			self.widgets['normentry'] = Tkinter.Checkbutton(self.widgets['tframe'], variable=self.variables['normalize'], text='', anchor=W, command=self.OnToggleNormalize, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
			self.widgets['normentry'].grid(column=1,row=self.gridrow, padx=10, pady=5, sticky="W")
			
			self.gridrow += 1
			
		self.widgets['acclabel'] = Tkinter.Label(self.widgets['tframe'],text='Acceleration Time', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['acclabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.variables['acc_time'] = Tkinter.DoubleVar()
		self.variables['acc_time'].set(float(self.motor.acceleration['acc_time']))
		self.widgets['accentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['acc_time'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['accentry'].grid(column=1,row=self.gridrow, padx=10, pady=5,sticky='EW')
		
		self.widgets['accinfo'] = Tkinter.Label(self.widgets['tframe'],text='seconds to full speed', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['accinfo'].grid(column=2,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['declabel'] = Tkinter.Label(self.widgets['tframe'],text='Deceleration Time', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['declabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.variables['dec_time'] = Tkinter.DoubleVar()
		self.variables['dec_time'].set(float(self.motor.acceleration['dec_time']))
		self.widgets['decentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['dec_time'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['decentry'].grid(column=1,row=self.gridrow, padx=10, pady=5,sticky='EW')
		
		self.widgets['decinfo'] = Tkinter.Label(self.widgets['tframe'],text='seconds to stop', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['decinfo'].grid(column=2,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['elabel'] = Tkinter.Label(self.widgets['tframe'],text='Enabled', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['elabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.variables['enabled'] = Tkinter.BooleanVar()
		self.variables['enabled'].set(self.motor.jsonData['enabled'] if self.motor.blobExists() else False)
		self.widgets['enabledentry'] = Tkinter.Checkbutton(self.widgets['tframe'], variable=self.variables['enabled'], text='', anchor=W, command=self.OnToggleEnabled, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['enabledentry'].grid(column=1,row=self.gridrow, padx=10, pady=5, sticky="W")
		
		self.gridrow += 1
		
		self.widgets['slabel'] = Tkinter.Label(self.widgets['tframe'],text='State', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['slabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.variables['state'] = Tkinter.DoubleVar()
		self.variables['state'].set(float(self.motor.driveState))
		self.widgets['stateentry'] = Tkinter.Scale(self.widgets['tframe'], from_=-1, to=1, variable=self.variables['state'], command=self.OnDriveStateChange, resolution=0.01, orient=Tkinter.HORIZONTAL, length = 500, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
		self.widgets['stateentry'].grid(column=1,row=self.gridrow, columnspan=2, padx=10, pady=5)
		
		self.gridrow += 1
		
		if (self.motor.jbType == 'StepperMotor'):
			self.widgets['anglabel'] = Tkinter.Label(self.widgets['tframe'],text='Angle', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['anglabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.widgets['angdata'] = Tkinter.Label(self.widgets['tframe'],text=round(self.motor.angle,3), anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=5)
			self.widgets['angdata'].grid(column=1,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.motor.addCallback('angle_display', self.updateAngle)
			
			self.gridrow += 1
			
			self.widgets['gotolabel'] = Tkinter.Label(self.widgets['tframe'],text='Go To Angle', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['gotolabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.variables['goto'] = Tkinter.IntVar()
			self.widgets['gotoentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['goto'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
			self.widgets['gotoentry'].grid(column=1,row=self.gridrow, padx=10, pady=5,sticky='EW')
			self.variables['goto'].set(0)
			
			self.widgets['grefreshbutton'] = Tkinter.Button(self.widgets['tframe'],text=u"Refresh", image=self.images['accept'], command=self.OnGoToAngleClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['grefreshbutton'].grid(column=2,row=self.gridrow,sticky='W')
			
			self.gridrow += 1
			
			self.widgets['zerolabel'] = Tkinter.Label(self.widgets['tframe'],text='Set Zero Angle', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['zerolabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.widgets['grefreshbutton'] = Tkinter.Button(self.widgets['tframe'],text=u"Refresh", image=self.images['accept'], command=self.OnZeroAngleClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['grefreshbutton'].grid(column=1,row=self.gridrow,sticky='W')
			
			self.gridrow += 1
			
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')

		if self.motor.blobExists():
			self.widgets['controllerLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Controllers', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['controllerLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['deleteLabel'].grid(column=3,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnListDCMotorsClick if self.motor.jbType == 'DcMotor' else self.OnListStepperMotorsClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['savemotor'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Motor", image=self.images['save'], command=self.OnSaveMotorClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['savemotor'].grid(column=1,row=self.gridrow)
		if self.motor.blobExists():
			controllerFunc = self.OnEditDCMotorControllersClick if self.motor.jbType == 'DcMotor' else self.OnEditStepperMotorControllersClick
			self.widgets['controllers'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Controllers", image=self.images['joystick'], command=lambda x = self.motor.jbIndex:controllerFunc(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['controllers'].grid(column=2,row=self.gridrow)
			self.widgets['deletemotor'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete Motor", image=self.images['delete'], command=self.OnDeleteDCMotorClick if self.motor.jbType == 'DcMotor' else self.OnDeleteStepperMotorClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['deletemotor'].grid(column=3,row=self.gridrow)
	def displayGpio(self, parent):
		""" partial view - display gpio canvas
		
		@param parent Frame
		
		@return Frame
		"""
		width=50
		height=410
		startpos = (20,40)
		frame = Tkinter.Frame(parent, bg=self.colours['bg'])
		self.widgets['gpiolabel'] = Tkinter.Label(frame,text='GPIO Configuration', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['gpiolabel'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['gpiocanvas'] = Tkinter.Canvas(frame, width=width + 200, height=height + 60, bg=self.colours['bg'], highlightthickness=2, highlightbackground=self.colours['greyborder'])
		self.widgets['gpiocanvas'].grid(column=0,row=1, sticky='EW')
		self.shapes['board'] = self.widgets['gpiocanvas'].create_rectangle((0,20,width+40, height+60), fill=self.colours['pcb'])
		self.shapes['base'] = self.widgets['gpiocanvas'].create_rectangle(
			(
				startpos[0],
				startpos[1],
				startpos[0]+width,
				startpos[1]+height
			),
			fill=self.colours['gpiobg'],
			tags='base'
		)
		pinsize = (10,10)
		pingap = (20,10)
		pincol = 1
		usedPins = self.getUsedPins()
		x = startpos[0]
		y = startpos[1] + pingap[1]
		for pindex in range(1,41):
			pincol = 2 if pindex % 2 == 0 else 1
			x = startpos[0] + pingap[1] + pingap[0] * (pincol-1)
			if (pincol == 1):
				y = startpos[1] + pingap[1] * pindex
			self.shapes['pin%s' % pindex] = self.widgets['gpiocanvas'].create_rectangle(
				(
					x,
					y,
					x+pinsize[0],
					y+pinsize[1]
				),
				fill=self.colours['gpiopin'],
				width=3,
				tags='pins'
			)
			colour = self.colours['gpiopin']
			border = self.colours['gpiounavail']
			pinfo = self.getPinInfo(pindex)
			if (pinfo['default_usage'] == 'i2c'):
				colour = self.colours['gpioi2c']
			elif (pinfo['default_usage'] == 'uart'):
				colour = self.colours['gpiouart']
			elif (pinfo['default_usage'] == 'spi'):
				colour = self.colours['gpiospi']
			elif (pinfo['default_usage'] == '5v'):
				colour = self.colours['gpio5v']
			elif (pinfo['default_usage'] == '3v'):
				colour = self.colours['gpio3v3']
			elif (pinfo['default_usage'] == 'gnd'):
				colour = self.colours['gpiognd']
			
			if (self.isPinAvailable(pindex)):
				border = self.colours['gpioavail']
			if (pindex in usedPins):
				border = self.colours['gpioused']
			self.widgets['gpiocanvas'].itemconfig(self.shapes['pin%s' % pindex], fill=colour, activefill=self.colours['valuefg'], outline=border)
		self.shapes['pinfo'] = {}
		self.widgets['gpiocanvas'].tag_raise('base')
		self.widgets['gpiocanvas'].tag_raise('pins')
		self.widgets['gpiocanvas'].tag_bind('pins', '<Enter>', self.showPinData, '+')
		self.widgets['gpiocanvas'].tag_bind('pins', '<Leave>', self.hidePinData, '+')
		return frame
	def deleteMotor(self):
		""" view - delete dc or stepper motor
		"""
		self.open()
		
		self.widgets['molabel'] = Tkinter.Label(self.widgets['tframe'],text='Motors / Delete %s Motor' % ('DC' if self.motor.jbType == 'DcMotor' else 'Stepper'), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['molabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['nlabel'] = Tkinter.Label(self.widgets['tframe'],text='Motor Name', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['nlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.widgets['nlabel'] = Tkinter.Label(self.widgets['tframe'],text=self.motor.jsonData['name'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['nlabel'].grid(column=1,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['ilabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this motor?', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['ilabel'].grid(column=0,row=self.gridrow, columnspan=2, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['delLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['delLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnListDCMotorsClick if self.motor.jbType == 'DcMotor' else self.OnListStepperMotorsClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['del'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['accept'], command=self.OnDeleteMotorConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['del'].grid(column=1,row=self.gridrow)
	def editControllers(self):
		""" view - list motor controllers
		"""
		self.open()
		
		self.widgets['mainlabel'] = Tkinter.Label(self.widgets['tframe'],text='Motors / Motor / Edit Controllers', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['mainlabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['mnframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['mnframe'].grid(column=0,row=self.gridrow, columnspan=2, sticky='EW')
		
		self.widgets['nlabel'] = Tkinter.Label(self.widgets['mnframe'],text='Motor Name', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['nlabel'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['ndata'] = Tkinter.Label(self.widgets['mnframe'],text=self.motor.jsonData['name'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['ndata'].grid(column=1,row=0, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['jlabel'] = Tkinter.Label(self.widgets['tframe'],text='Joystick', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['jlabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		self.widgets['addjs'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Joystick Action", image=self.images['add'], command=self.OnAddJoystickActionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addjs'].grid(column=1,row=self.gridrow,sticky='E')
		
		self.gridrow += 1
		
		self.widgets['jframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['jframe'].grid(column=0,row=self.gridrow, columnspan=2, sticky='EW')
		
		if (any(self.motor.controllers) and any(self.motor.controllers['joystick'])):
			self.widgets['deviceLabel'] = Tkinter.Label(self.widgets['jframe'],text='Device', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['deviceLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['signalLabel'] = Tkinter.Label(self.widgets['jframe'],text='Signal', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['signalLabel'].grid(column=1,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['jframe'],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['nameLabel'].grid(column=2,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['numberLabel'] = Tkinter.Label(self.widgets['jframe'],text='Number', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['numberLabel'].grid(column=3,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['jframe'],text='Edit', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['editLabel'].grid(column=4,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['delLabel'] = Tkinter.Label(self.widgets['jframe'],text='Delete', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['delLabel'].grid(column=5,row=self.gridrow,padx=10,sticky='EW')
			
			self.gridrow += 1
			rowcount = 1
			keys = self.motor.controllers['joystick'].keys()
			keys.sort() #ensure controllers are listed in order
			for k in keys:
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				v = self.motor.controllers['joystick'][k]
				self.widgets['device'+str(self.gridrow)] = Tkinter.Label(self.widgets['jframe'],text=v['device'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['device'+str(self.gridrow)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['signal'+str(self.gridrow)] = Tkinter.Label(self.widgets['jframe'],text=v['signal'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['signal'+str(self.gridrow)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['name'+str(self.gridrow)] = Tkinter.Label(self.widgets['jframe'],text=v['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['name'+str(self.gridrow)].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['number'+str(self.gridrow)] = Tkinter.Label(self.widgets['jframe'],text=v['number'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['number'+str(self.gridrow)].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['edit'+str(self.gridrow)] = Tkinter.Button(self.widgets['jframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnEditJoystickActionClick(x))
				self.widgets['edit'+str(self.gridrow)].grid(column=4,row=self.gridrow,sticky='EW')
				self.widgets['del'+str(self.gridrow)] = Tkinter.Button(self.widgets['jframe'],text=u"Delete", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnDeleteJoystickActionClick(x))
				self.widgets['del'+str(self.gridrow)].grid(column=5,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['nojclabel'] = Tkinter.Label(self.widgets['jframe'],text="There are currently no joystick motor controllers", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nojclabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			
		self.widgets['spacer'] = Tkinter.Label(self.widgets['tframe'],text='', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], height=1)
		self.widgets['spacer'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['klabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyboard', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['klabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		self.widgets['addkb'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Keyboard Action", image=self.images['add'], command=self.OnAddKeyboardActionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addkb'].grid(column=1,row=self.gridrow,sticky='E')
		
		self.gridrow += 1
		
		self.widgets['kframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['kframe'].grid(column=0,row=self.gridrow, columnspan=2, sticky='EW')
		
		if (any(self.motor.controllers) and any(self.motor.controllers['keyboard'])):
			self.widgets['asciiLabel'] = Tkinter.Label(self.widgets['kframe'],text='ASCII', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['asciiLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['hexLabel'] = Tkinter.Label(self.widgets['kframe'],text='Hex', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['hexLabel'].grid(column=1,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['dmLabel'] = Tkinter.Label(self.widgets['kframe'],text='Drive Mode', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['dmLabel'].grid(column=2,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['kframe'],text='Edit', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['editLabel'].grid(column=3,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['delLabel'] = Tkinter.Label(self.widgets['kframe'],text='Delete', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['delLabel'].grid(column=4,row=self.gridrow,padx=10,sticky='EW')
			
			self.gridrow += 1
			rowcount = 1
			driveModes = {
				'drive_state': 'Drive State',
				'move_to': 'Move To Angle',
				'move_by': 'Move By Angle',
				'zero_angle': 'Zero Angle'
			}
			keys = self.motor.controllers['keyboard'].keys()
			keys.sort() #ensure controllers are listed in order
			for k in keys:
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				v = self.motor.controllers['keyboard'][k]
				self.widgets['ascii'+str(self.gridrow)] = Tkinter.Label(self.widgets['kframe'],text=v['ascii'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['ascii'+str(self.gridrow)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['hex'+str(self.gridrow)] = Tkinter.Label(self.widgets['kframe'],text=v['hex'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['hex'+str(self.gridrow)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['dm'+str(self.gridrow)] = Tkinter.Label(self.widgets['kframe'],text=driveModes[v['drive_mode']], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['dm'+str(self.gridrow)].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['edit'+str(self.gridrow)] = Tkinter.Button(self.widgets['kframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnEditKeyboardActionClick(x))
				self.widgets['edit'+str(self.gridrow)].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['del'+str(self.gridrow)] = Tkinter.Button(self.widgets['kframe'],text=u"Delete", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnDeleteKeyboardActionClick(x))
				self.widgets['del'+str(self.gridrow)].grid(column=4,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['nokclabel'] = Tkinter.Label(self.widgets['kframe'],text="There are currently no keyboard motor controllers", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nokclabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		if (self.motor.jbType == 'DcMotor'):
			self.widgets['back'].configure(command=lambda x = self.motor.jbIndex: self.OnEditDCMotorClick(x))
		else:
			self.widgets['back'].configure(command=lambda x = self.motor.jbIndex: self.OnEditStepperMotorClick(x))
		self.widgets['back'].grid(column=0,row=self.gridrow)
	def editJoystickAction(self):
		""" view - edit joystick action
		"""
		self.open()
		
		self.widgets['mainlabel'] = Tkinter.Label(self.widgets['tframe'],text='Motors / Motor / Controllers / Joystick', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['mainlabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['mnframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['mnframe'].grid(column=0,row=self.gridrow, columnspan=2, sticky='EW')
		
		self.widgets['nlabel'] = Tkinter.Label(self.widgets['mnframe'],text='Motor Name', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['nlabel'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['ndata'] = Tkinter.Label(self.widgets['mnframe'],text=self.motor.jsonData['name'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['ndata'].grid(column=1,row=0, padx=10, pady=5, sticky='EW')
		
		if (self.motor.jbType == 'StepperMotor'):
			self.widgets['anglelabel'] = Tkinter.Label(self.widgets['mnframe'],text='Angle', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['anglelabel'].grid(column=0,row=1, padx=10, pady=5, sticky='EW')
			self.widgets['angle'] = Tkinter.Label(self.widgets['mnframe'],text=round(self.motor.angle,3), anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
			self.widgets['angle'].grid(column=1,row=1, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['alabel'] = Tkinter.Label(self.widgets['tframe'],text='Action', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['alabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.widgets['aframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['aframe'].grid(column=1,row=self.gridrow, sticky='EW')
		
		self.widgets['devicelabel'] = Tkinter.Label(self.widgets['aframe'],text='Device', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['devicelabel'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['devicedata'] = Tkinter.Label(self.widgets['aframe'],text=self.controller['device'] if any(self.controller['device']) else '-', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['devicedata'].grid(column=1,row=0, padx=10, pady=5, sticky='EW')
		
		self.widgets['featurelabel'] = Tkinter.Label(self.widgets['aframe'],text='Feature', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['featurelabel'].grid(column=2,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['featuredata'] = Tkinter.Label(self.widgets['aframe'],text=self.controller['signal'] if any(self.controller['signal']) else '-', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['featuredata'].grid(column=3,row=0, padx=10, pady=5, sticky='EW')
		
		self.widgets['fidlabel'] = Tkinter.Label(self.widgets['aframe'],text='Ident', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['fidlabel'].grid(column=4,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['fiddata'] = Tkinter.Label(self.widgets['aframe'],text=self.controller['name'] if any(self.controller['name']) else '-', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['fiddata'].grid(column=5,row=0, padx=10, pady=5, sticky='EW')
		
		self.widgets['capture'] = Tkinter.Button(self.widgets['aframe'],text=u"Capture", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.OnCaptureJoystickActionClick)
		self.widgets['capture'].grid(column=6,row=0,sticky='EW')
		
		self.widgets['infolabel'] = Tkinter.Label(self.widgets['aframe'],text='Click the button to capture a joystick action.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['infolabel'].grid(column=0,row=1, columnspan=6,padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['ilabel'] = Tkinter.Label(self.widgets['tframe'],text='Inverted', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['ilabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		self.variables['invert'] = Tkinter.BooleanVar()
		self.widgets['invertentry'] = Tkinter.Checkbutton(self.widgets['tframe'], highlightthickness=0, state='normal' if any(self.controller['device']) else 'disabled', variable=self.variables['invert'], command=self.OnInvertControllerClick, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], height=2)
		self.widgets['invertentry'].grid(column=1,row=self.gridrow, sticky='W')
		self.variables['invert'].set(self.controller['invert'])
		
		self.gridrow += 1
		
		self.widgets['dlabel'] = Tkinter.Label(self.widgets['tframe'],text='Drive Mode', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['dlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.widgets['drive_mode'] = { 'frame': Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg']), 'options': {} }
		self.widgets['drive_mode']['frame'].grid(column=1,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.updateDriveMode()
		
		self.gridrow += 1
		
		self.widgets['dzlabel'] = Tkinter.Label(self.widgets['tframe'],text='Dead Zone', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['dzlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.widgets['dzframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['dzframe'].grid(column=1,row=self.gridrow, sticky='EW')
		
		self.updateDeadZone()
		
		self.gridrow += 1
		
		self.widgets['plabel'] = Tkinter.Label(self.widgets['tframe'],text='Preview', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['plabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.widgets['pframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['pframe'].grid(column=1,row=self.gridrow, sticky='EW')
		
		self.updateJoystickActionPreview()
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		backFunc = self.OnEditDCMotorControllersClick if self.motor.jbType == 'DcMotor' else self.OnEditStepperMotorControllersClick
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=lambda x = self.motor.jbIndex: backFunc(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['savemotor'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Motor", image=self.images['save'], command=self.OnSaveJoystickActionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['savemotor'].grid(column=1,row=self.gridrow)
	def updateDriveMode(self):
		""" partial view - update drive mode options
		"""
		# clear any existing options
		for v in self.widgets['drive_mode']['options'].values():
			v.grid_forget()
			del(v)
		row = 0
		#drive mode
		dmOptions = {'drive_state':'Drive State'}
		if (self.motor.jbType == 'StepperMotor'):
			# stepper options
			dmOptions.update({
				'move_to': 'Move To Angle',
				'move_by': 'Move By Angle'
			})
			if (('signal' in self.controller.keys() and self.controller['signal'] == 'button') or self.controller['type'] == 'keyboard'):
				# button only stepper options
				dmOptions.update({
					'zero_angle': 'Zero Angle'
				})
		self.widgets['drive_mode']['options']['dmlabel'] = Tkinter.Label(self.widgets['drive_mode']['frame'],text='Change', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['drive_mode']['options']['dmlabel'].grid(column=0,row=row, padx=10, pady=5, sticky='EW')
		
		if (not 'drive_mode' in self.variables.keys()):
			self.variables['drive_mode'] = Tkinter.StringVar()
			self.variables['drive_mode'].set(self.controller['drive_mode'] if 'drive_mode' in self.controller.keys() else 'drive_state')
		col = 1
		for k,v in dmOptions.items():
			self.widgets['drive_mode']['options'][k] = Radiobutton(self.widgets['drive_mode']['frame'], text=v, variable=self.variables['drive_mode'], value=k, command=self.OnJoystickActionDriveModeChange, selectcolor=self.colours['bg'], bg=self.colours['bg'], activebackground=self.colours['activebg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'])
			self.widgets['drive_mode']['options'][k].grid(column=col,row=row,padx=10,sticky='W')
			col += 1
		row += 1
		
		if (self.variables['drive_mode'].get() == 'drive_state'):
			#drive state options
			self.widgets['drive_mode']['options']['mlabel'] = Tkinter.Label(self.widgets['drive_mode']['frame'],text='Mix Mode', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['drive_mode']['options']['mlabel'].grid(column=0,row=row, padx=10, pady=5, sticky='EW')
			
			self.variables['mix'] = Tkinter.StringVar()
			self.variables['mix'].set(self.controller['mix_mode'] if 'mix_mode' in self.controller.keys() else 'override')
			self.widgets['drive_mode']['options']['override'] = Radiobutton(self.widgets['drive_mode']['frame'], text='Override', variable=self.variables['mix'], value='override', command=self.OnChangeMixMode, selectcolor=self.colours['bg'], bg=self.colours['bg'], activebackground=self.colours['activebg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'])
			self.widgets['drive_mode']['options']['override'].grid(column=1,row=row,padx=10,sticky='W')
			self.widgets['drive_mode']['options']['additive'] = Radiobutton(self.widgets['drive_mode']['frame'], text='Additive', variable=self.variables['mix'], value='additive', command=self.OnChangeMixMode, selectcolor=self.colours['bg'], bg=self.colours['bg'], activebackground=self.colours['activebg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'])
			self.widgets['drive_mode']['options']['additive'].grid(column=2,row=row,padx=10,sticky='W')
		elif (self.variables['drive_mode'].get() in ['move_to', 'move_by']):
			#move to options
			if ('signal' in self.controller.keys() and self.controller['signal'] == 'axis'):
				self.widgets['drive_mode']['options']['poslabel'] = Tkinter.Label(self.widgets['drive_mode']['frame'],text='Positive Angle', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['drive_mode']['options']['poslabel'].grid(column=0,row=row, padx=10, pady=5, sticky='EW')
				self.variables['positive'] = Tkinter.IntVar()
				self.variables['positive'].set(self.controller['pos_angle'] if 'pos_angle' in self.controller.keys() else 0)
				self.widgets['drive_mode']['options']['posentry'] = Tkinter.Entry(self.widgets['drive_mode']['frame'], textvariable=self.variables['positive'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
				self.widgets['drive_mode']['options']['posentry'].grid(column=1,row=row,sticky='EW')
				
				self.widgets['drive_mode']['options']['neglabel'] = Tkinter.Label(self.widgets['drive_mode']['frame'],text='Negative Angle', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['drive_mode']['options']['neglabel'].grid(column=2,row=row, padx=10, pady=5, sticky='EW')
				self.variables['negative'] = Tkinter.IntVar()
				self.variables['negative'].set(self.controller['neg_angle'] if 'neg_angle' in self.controller.keys() else 0)
				self.widgets['drive_mode']['options']['negentry'] = Tkinter.Entry(self.widgets['drive_mode']['frame'], textvariable=self.variables['negative'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
				self.widgets['drive_mode']['options']['negentry'].grid(column=3,row=row,sticky='EW')
			else:
				self.widgets['drive_mode']['options']['anglabel'] = Tkinter.Label(self.widgets['drive_mode']['frame'],text='Angle', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['drive_mode']['options']['anglabel'].grid(column=0,row=row, padx=10, pady=5, sticky='EW')
				self.variables['angle'] = Tkinter.IntVar()
				self.variables['angle'].set(self.controller['angle'] if 'angle' in self.controller.keys() else 0)
				self.widgets['drive_mode']['options']['angentry'] = Tkinter.Entry(self.widgets['drive_mode']['frame'], textvariable=self.variables['angle'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
				self.widgets['drive_mode']['options']['angentry'].grid(column=1,row=row,sticky='EW')
	def updateJoystickActionPreview(self):
		""" partial view - update joystick preview display
		"""
		if ('preview' in self.widgets):
			if (self.widgets['preview']['state'] == 'previewing'):
				self.widgets['preview']['widget'].widget.grid_forget()
				del(self.widgets['preview'])
			else:
				self.widgets['preview']['widget'].grid_forget()
				del(self.widgets['preview'])
		if(hasattr(self.gui,'joystickRegistry')):
			if (any(self.controller['device'])):
				#controller data available
				if (self.controller['device'] in self.gui.joystickRegistry.joysticks):
					#new
					if (self.controller['signal'] == 'axis'):
						if (self.controller['name'] in self.gui.joystickRegistry.joysticks[self.controller['device']].dual_axis.keys()):
							#key axis
							k = self.controller['name']
							v = self.gui.joystickRegistry.joysticks[self.controller['device']].dual_axis[k]
							self.widgets['preview'] = {
								'state': 'previewing',
								'type': 'dual',
								'dev_num': self.controller['dev_num'],
								'device': self.controller['device'],
								'signal': self.controller['signal'],
								'name': self.controller['name'],
								'xaxis': k,
								'yaxis': v,
								'current_axis': k,
								'number': self.controller['number'],
								'widget': TkJoystickManager.TkJoystickDualAxis(self.widgets['pframe'], k, v, self.colours, self.images)
							}
							self.widgets['preview']['widget'].widget.grid(column=0,row=0, padx=10, pady=5, sticky='EW')
						elif (self.controller['name'] in self.gui.joystickRegistry.joysticks[self.controller['device']].dual_axis.values()):
							#value axis
							k =  [k for k,v in self.gui.joystickRegistry.joysticks[self.controller['device']].dual_axis.items() if v == self.controller['name']]
							k = k[0]
							v = self.controller['name']
							self.widgets['preview'] = {
								'state': 'previewing',
								'type': 'dual',
								'dev_num': self.controller['dev_num'],
								'device': self.controller['device'],
								'signal': self.controller['signal'],
								'name': self.controller['name'],
								'xaxis': k,
								'yaxis': v,
								'current_axis': v,
								'number': self.controller['number'],
								'widget': TkJoystickManager.TkJoystickDualAxis(self.widgets['pframe'], k, v, self.colours, self.images)
							}
							self.widgets['preview']['widget'].widget.grid(column=0,row=0, padx=10, pady=5, sticky='EW')
						elif (self.controller['name'] in self.gui.joystickRegistry.joysticks[self.controller['device']].single_axis.keys()):
							horizontal = self.gui.joystickRegistry.joysticks[self.controller['device']].single_axis[self.controller['name']]
							#single axis
							self.widgets['preview'] = {
								'state': 'previewing',
								'type': 'single',
								'dev_num': self.controller['dev_num'],
								'device': self.controller['device'],
								'name': self.controller['name'],
								'signal': self.controller['signal'],
								'number': self.controller['number'],
								'widget': TkJoystickManager.TkJoystickAxis(self.widgets['pframe'], self.controller['name'], self.colours, self.images, horizontal)
							}
							self.widgets['preview']['widget'].widget.grid(column=0,row=0, padx=10, pady=5, sticky='EW')
					else:
						self.widgets['preview'] = {
							'state': 'previewing',
							'type': 'button',
							'dev_num': self.controller['dev_num'],
							'device': self.controller['device'],
							'name': self.controller['name'],
							'signal': self.controller['signal'],
							'number': self.controller['number'],
							'widget': TkJoystickManager.TkJoystickButton(self.widgets['pframe'], self.controller['name'], self.colours, self.images)
						}
						self.widgets['preview']['widget'].widget.grid(column=0,row=0, padx=10, pady=5, sticky='EW')
					self.motor.controllersEnabled = False #disable other controllers while previewing
					self.gui.joystickRegistry.addCallback('JoystickActionPreview', self.joystickActionPreviewCallback)
				else:
					self.widgets['preview'] = {
						'state': 'unavailable',
						'widget': Tkinter.Label(self.widgets['pframe'],text='Controller unavailable', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
					}
					self.widgets['preview']['widget'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
			else:
				#no action
				self.widgets['preview'] = {
					'state': '',
					'widget': Tkinter.Label(self.widgets['pframe'],text='No controller action', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
				}
				self.widgets['preview']['widget'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
		else:
			#joysticks unavailable
			self.widgets['preview'] = {
				'state': '',
				'widget': Tkinter.Label(self.widgets['pframe'],text='Joysticks are unavailable. Check the joystick module', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			}
			self.widgets['preview']['widget'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
	def deleteJoystickAction(self):
		""" view - delete joystick action
		"""
		self.open()
		
		self.widgets['mainlabel'] = Tkinter.Label(self.widgets['tframe'],text='Motors / Motor / Controllers / Joystick / Delete', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['mainlabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['nlabel'] = Tkinter.Label(self.widgets['tframe'],text='Motor Name', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['nlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		self.widgets['ndata'] = Tkinter.Label(self.widgets['tframe'],text=self.motor.jsonData['name'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['ndata'].grid(column=1,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['alabel'] = Tkinter.Label(self.widgets['tframe'],text='Action', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['alabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.widgets['aframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['aframe'].grid(column=1,row=self.gridrow, sticky='EW')
		
		self.widgets['devicelabel'] = Tkinter.Label(self.widgets['aframe'],text='Device', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['devicelabel'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['devicedata'] = Tkinter.Label(self.widgets['aframe'],text=self.controller['device'] if any(self.controller['device']) else '-', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['devicedata'].grid(column=1,row=0, padx=10, pady=5, sticky='EW')
		
		self.widgets['featurelabel'] = Tkinter.Label(self.widgets['aframe'],text='Feature', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['featurelabel'].grid(column=2,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['featuredata'] = Tkinter.Label(self.widgets['aframe'],text=self.controller['signal'] if any(self.controller['signal']) else '-', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['featuredata'].grid(column=3,row=0, padx=10, pady=5, sticky='EW')
		
		self.widgets['fidlabel'] = Tkinter.Label(self.widgets['aframe'],text='Ident', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['fidlabel'].grid(column=4,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['fiddata'] = Tkinter.Label(self.widgets['aframe'],text=self.controller['name'] if any(self.controller['name']) else '-', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['fiddata'].grid(column=5,row=0, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['ilabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this controller?', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['ilabel'].grid(column=0,row=self.gridrow, columnspan=2, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['delLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['delLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		backFunc = self.OnEditDCMotorControllersClick if self.motor.jbType == 'DcMotor' else self.OnEditStepperMotorControllersClick
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=lambda x = self.motor.jbIndex: backFunc(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['del'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['accept'], command=lambda x = self.controller['ident']: self.OnDeleteJoystickActionConfirmClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['del'].grid(column=1,row=self.gridrow)
	def editKeyboardAction(self):
		""" view - edit keyboard action
		"""
		self.open()
		
		self.widgets['mainlabel'] = Tkinter.Label(self.widgets['tframe'],text='Motors / Motor / Controllers / Keyboard', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['mainlabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['mnframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['mnframe'].grid(column=0,row=self.gridrow, columnspan=2, sticky='EW')
		
		self.widgets['nlabel'] = Tkinter.Label(self.widgets['mnframe'],text='Motor Name', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['nlabel'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['ndata'] = Tkinter.Label(self.widgets['mnframe'],text=self.motor.jsonData['name'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['ndata'].grid(column=1,row=0, padx=10, pady=5, sticky='EW')
		
		if (self.motor.jbType == 'StepperMotor'):
			self.widgets['anglelabel'] = Tkinter.Label(self.widgets['mnframe'],text='Angle', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['anglelabel'].grid(column=0,row=1, padx=10, pady=5, sticky='EW')
			self.widgets['angdata'] = Tkinter.Label(self.widgets['mnframe'],text=round(self.motor.angle,3), anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
			self.widgets['angdata'].grid(column=1,row=1, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		if (not self.kbthread.isRunning()):
			self.widgets['ilabel'] = Tkinter.Label(self.widgets['tframe'],text='The keyboard service must be running to manage keyboard controllers', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['ilabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.gridrow += 1
			
			self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
			self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
			
			self.gridrow = 0
			
			self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['startLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Start', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['startLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
			self.gridrow += 1

			backFunc = self.OnEditDCMotorControllersClick if self.motor.jbType == 'DcMotor' else self.OnEditStepperMotorControllersClick
			self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=lambda x = self.motor.jbIndex: backFunc(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['back'].grid(column=0,row=self.gridrow)
			self.widgets['start'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Start KB Service", image=self.images['accept'], command=self.OnStartKeyboardServiceClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['start'].grid(column=1,row=self.gridrow)
		else:
			self.widgets['alabel'] = Tkinter.Label(self.widgets['tframe'],text='Action', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['alabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.widgets['aframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
			self.widgets['aframe'].grid(column=1,row=self.gridrow, sticky='EW')
			
			self.widgets['asciilabel'] = Tkinter.Label(self.widgets['aframe'],text='ASCII', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['asciilabel'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
			self.widgets['asciidata'] = Tkinter.Label(self.widgets['aframe'],text=self.controller['ascii'] if any(self.controller['ascii']) else '-', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
			self.widgets['asciidata'].grid(column=1,row=0, padx=10, pady=5, sticky='EW')
			
			self.widgets['hexlabel'] = Tkinter.Label(self.widgets['aframe'],text='Hex', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['hexlabel'].grid(column=2,row=0, padx=10, pady=5, sticky='EW')
			self.widgets['hexdata'] = Tkinter.Label(self.widgets['aframe'],text=self.controller['hex'] if any(self.controller['hex']) else '-', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
			self.widgets['hexdata'].grid(column=3,row=0, padx=10, pady=5, sticky='EW')
			
			self.widgets['capture'] = Tkinter.Button(self.widgets['aframe'],text=u"Capture", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.OnCaptureKeyboardActionClick)
			self.widgets['capture'].grid(column=4,row=0,sticky='EW')
			
			self.widgets['infolabel'] = Tkinter.Label(self.widgets['aframe'],text='Click the button to capture a keyboard action.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['infolabel'].grid(column=0,row=1, columnspan=4,padx=10, pady=5, sticky='EW')
		
			self.gridrow += 1
			
			self.widgets['ilabel'] = Tkinter.Label(self.widgets['tframe'],text='Inverted', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['ilabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			self.variables['invert'] = Tkinter.BooleanVar()
			self.widgets['invertentry'] = Tkinter.Checkbutton(self.widgets['tframe'], highlightthickness=0, state='normal' if any(self.controller['hex']) else 'disabled', variable=self.variables['invert'], command=self.OnInvertControllerClick, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], height=2)
			self.widgets['invertentry'].grid(column=1,row=self.gridrow, sticky='W')
			self.variables['invert'].set(self.controller['invert'])
			
			self.gridrow += 1
			
			self.widgets['dlabel'] = Tkinter.Label(self.widgets['tframe'],text='Drive Mode', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['dlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.widgets['drive_mode'] = { 'frame': Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg']), 'options': {} }
			self.widgets['drive_mode']['frame'].grid(column=1,row=self.gridrow, padx=10, pady=5, sticky='EW')
			
			self.updateDriveMode()
		
			self.gridrow += 1
			
			self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
			self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
			
			self.gridrow = 0
			
			self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
			self.gridrow += 1

			backFunc = self.OnEditDCMotorControllersClick if self.motor.jbType == 'DcMotor' else self.OnEditStepperMotorControllersClick
			self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=lambda x = self.motor.jbIndex: backFunc(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['back'].grid(column=0,row=self.gridrow)
			self.widgets['savemotor'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Motor", image=self.images['save'], command=self.OnSaveKeyboardActionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['savemotor'].grid(column=1,row=self.gridrow)
	def deleteKeyboardAction(self):
		""" view - delete joystick action
		"""
		self.open()
		
		self.widgets['mainlabel'] = Tkinter.Label(self.widgets['tframe'],text='Motors / Motor / Controllers / Keyboard / Delete', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['mainlabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['nlabel'] = Tkinter.Label(self.widgets['tframe'],text='Motor Name', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['nlabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		self.widgets['ndata'] = Tkinter.Label(self.widgets['tframe'],text=self.motor.jsonData['name'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['ndata'].grid(column=1,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['alabel'] = Tkinter.Label(self.widgets['tframe'],text='Action', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['alabel'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
		
		self.widgets['aframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['aframe'].grid(column=1,row=self.gridrow, sticky='EW')
		
		self.widgets['asciilabel'] = Tkinter.Label(self.widgets['aframe'],text='ASCII', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['asciilabel'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['asciidata'] = Tkinter.Label(self.widgets['aframe'],text=self.controller['ascii'] if any(self.controller['ascii']) else '-', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['asciidata'].grid(column=1,row=0, padx=10, pady=5, sticky='EW')
		
		self.widgets['hexlabel'] = Tkinter.Label(self.widgets['aframe'],text='Hex', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['hexlabel'].grid(column=2,row=0, padx=10, pady=5, sticky='EW')
		self.widgets['hexdata'] = Tkinter.Label(self.widgets['aframe'],text=self.controller['hex'] if any(self.controller['hex']) else '-', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['hexdata'].grid(column=3,row=0, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['ilabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this controller?', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['ilabel'].grid(column=0,row=self.gridrow, columnspan=2, padx=10, pady=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['delLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['delLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		backFunc = self.OnEditDCMotorControllersClick if self.motor.jbType == 'DcMotor' else self.OnEditStepperMotorControllersClick
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=lambda x = self.motor.jbIndex: backFunc(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['del'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['accept'], command=lambda x = self.controller['ident']: self.OnDeleteKeyboardActionConfirmClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['del'].grid(column=1,row=self.gridrow)
	
	#=== ACTIONS ===#
	def OnListDCMotorsClick(self):
		""" action - list dc motors
		"""
		self.listDCMotors()
	def OnListStepperMotorsClick(self):
		""" action - list stepper motors
		"""
		self.listStepperMotors()
	def OnAddDCMotorClick(self):
		""" action - add dc motor
		"""
		self.motor = DcMotor()
		self.editMotor()
	def OnEditDCMotorClick(self, index):
		""" action - edit dc motor
		"""
		if (index in self.specification.motors.keys()):
			self.motor = self.specification.motors[index]
			self.editMotor()
		else:
			self.notifier.addNotice('Unable to find motor in specification', 'error')
	def OnAddStepperMotorClick(self):
		""" action - add stepper motor
		"""
		self.motor = StepperMotor()
		self.editMotor()
	def OnEditStepperMotorClick(self, index):
		""" action - edit stepper motor
		"""
		if (index in self.specification.steppers.keys()):
			self.motor = self.specification.steppers[index]
			self.editMotor()
		else:
			self.notifier.addNotice('Unable to find stepper in specification', 'error')
	def OnDriveStateChange(self, newstate):
		""" action - change drive state of cuurent motor
		"""
		#try updating accleration
		acc, dec = 0, 0
		failed = False
		try:
			acc = self.variables['acc_time'].get()
		except:
			failed = True
		try:
			dec = self.variables['acc_time'].get()
		except:
			failed = True
		if (not failed and acc >= 0 and dec >= 0):
			self.motor.acceleration.update({
				'acc_time': acc,
				'dec_time': dec,
			})
		#set drive state
		self.motor.setDriveState(float(newstate))
	def OnDriveTypeChangeClick(self):
		""" action - change dc motor drive type
		"""
		dt = self.variables['drivetype'].get()
		self.motor.stop() #pins are changing so cleanup is required
		self.motor.driveType = dt
		self.motor.pins = copy.copy(self.motor.driveTypes[dt]['pins'])
		self.updatePins()
		self.notifier.addNotice('Drive type updated')
		
	def OnOutputOrderRefreshClick(self):
		""" action - refresh stepper motor output order
		"""
		if (self.motor.jbType == 'StepperMotor'):
			self.motor.outputOrder = self.motor.outputOrders[self.variables['order'].get()]
			self.notifier.addNotice('Output order updated')
	def OnToggleEnabled(self):
		""" action - enable / disable motor
		"""
		#update pins
		usedPins = self.getUsedPins([self.motor.jbIndex] if self.motor.blobExists() else [])
		index = 0
		for p in self.motor.pins:
			try:
				pinNum = self.variables['pnum%s' % index].get()
			except:
				return
			if (not self.isGpioPin(pinNum)):
				return
			if (pinNum in usedPins):
				return
			self.motor.pins[index]['number'] = pinNum
			index += 1
		self.motor.enabled = bool(self.variables['enabled'].get())
		if (self.motor.enabled == True and not self.motor.running):
			self.motor.start()
		elif (self.motor.running):
			self.motor.stop()
	def OnToggleNormalize(self):
		""" action - toggle normalize angle
		"""
		if (hasattr(self, 'motor')):
			self.motor.normalizeAngle = self.variables['normalize'].get()
	def OnChangeSequence(self):
		""" action - change stepper motor sequence
		"""
		self.motor.jsonData['sequence_key'] = self.variables['sequence'].get()
		self.motor.sequence = self.motor.sequences[self.motor.jsonData['sequence_key']]
		self.motor.sequenceLength  = len(self.motor.sequence)
	def OnGoToAngleClick(self):
		""" action - turn stepper motor to specified angle
		"""
		if (hasattr(self, 'motor')):
			toAng = 0
			try:
				toAng = self.variables['goto'].get()
			except:
				self.notifier.addNotice('Invalid angle', 'error')
				return
			self.notifier.addNotice('Moving to %s deg' % toAng)
			self.motor.moveToAngle(toAng)
	def OnZeroAngleClick(self):
		""" action - set zero angle
		"""
		if (hasattr(self, 'motor')):
			self.motor.setZeroAngle()
			self.updateAngle(self.motor.driveState)
			self.notifier.addNotice('0 angle has been set')
	def OnSaveMotorClick(self):
		""" action - save motor
		"""
		name = self.variables['name'].get()
		enabled = self.variables['enabled'].get()
		if (len(name) < 3):
			self.notifier.addNotice('Name must be at least 3 characters', 'warning')
			return
		#check pins
		index = 0
		usedPins = self.getUsedPins([self.motor.jbIndex])
		for p in self.motor.pins:
			try:
				pinNum = self.variables['pnum%s' % index].get()
			except:
				self.notifier.addNotice('That\'s not a number silly (%s)!' % p['name'], 'error')
				return
			if (not self.isGpioPin(pinNum)):
				self.notifier.addNotice('Invalid pin number: %d' % pinNum, 'error')
				return
			if (pinNum in usedPins):
				self.notifier.addNotice('Occupied pin number: %d (%s)' % (pinNum,p['name']), 'error')
				return
			self.motor.pins[index]['number'] = pinNum
			index += 1
		#try updating accleration
		acc, dec = -1, -1
		failed = False
		try:
			acc = self.variables['acc_time'].get()
		except:
			failed = True
		try:
			dec = self.variables['dec_time'].get()
		except:
			failed = True
		if (not failed and acc >= 0 and dec >= 0):
			self.motor.acceleration.update({
				'acc_time': acc,
				'dec_time': dec,
			})
		elif (acc < 0):
			self.notifier.addNotice('Invalid acceleration time', 'error')
			return
		elif (dec < 0):
			self.notifier.addNotice('Invalid deceleration time', 'error')
			return
		#update simple variables
		self.motor.jsonData['name'] = name
		self.motor.jsonData['enabled'] = enabled
		#steppers only
		if (self.motor.jbType == 'StepperMotor'):
			#rpm
			try:
				rpm = self.variables['rpm'].get()
			except:
				self.notifier.addNotice('Invalid RPM', 'error')
				return
			if (rpm < 1):
				self.notifier.addNotice('Invalid RPM', 'error')
				return
			self.motor.jsonData['rpm'] = rpm
			#steps
			try:
				steps = self.variables['steps'].get()
			except:
				self.notifier.addNotice('Invalid number of steps', 'error')
				return
			if (steps < 1):
				self.notifier.addNotice('Invalid number of steps', 'error')
				return
			self.motor.jsonData['steps_per_rev'] = steps
		self.motor.save()
		#update spec
		if (self.motor.jbType == 'DcMotor'):
			self.specification.motors[self.motor.jbIndex] = self.motor
		else:
			self.specification.steppers[self.motor.jbIndex] = self.motor
		self.specification.save()
		self.notifier.addNotice('%s Motor Saved: %s' % ('DC' if self.motor.jbType == 'DcMotor' else 'Stepper', name))
		self.OnListDCMotorsClick() if self.motor.jbType == 'DcMotor' else self.OnListStepperMotorsClick()
	def OnDeleteDCMotorClick(self, index = None):
		""" action - delete dc motor
		"""
		if (index != None):
			self.motor = DcMotor(index)
		if (hasattr(self, 'motor')):
			self.deleteMotor()
	def OnDeleteStepperMotorClick(self, index = None):
		""" action - delete stepper motor
		"""
		if (index != None):
			self.motor = StepperMotor(index)
		if (hasattr(self, 'motor')):
			self.deleteMotor()
	def OnDeleteMotorConfirmClick(self):
		""" action - delete current motor
		"""
		if (hasattr(self,'motor')):
			motorType = self.motor.jbType
			if (motorType == 'DcMotor'):
				del(self.specification.motors[self.motor.jbIndex])
			else:
				del(self.specification.steppers[self.motor.jbIndex])
			self.motor.delete()
			self.specification.save()
			del(self.motor)
			self.notifier.addNotice('%s Motor deleted' % 'DC' if motorType == 'DcMotor' else 'Stepper')
			self.OnListDCMotorsClick() if motorType == 'DcMotor' else self.OnListStepperMotorsClick()
		else:
			self.notifier.addNotice('Unable to locate motor','error')
	def OnEditDCMotorControllersClick(self, index):
		""" action - edit dc motor controllers
		"""
		if (index in self.specification.motors.keys()):
			self.motor = self.specification.motors[index]
			self.editControllers()
		else:
			self.notifier.addNotice('Unable to locate motor','error')
	def OnEditStepperMotorControllersClick(self, index):
		""" action - edit stepper motor controllers
		"""
		if (index in self.specification.steppers.keys()):
			self.motor = self.specification.steppers[index]
			self.editControllers()
		else:
			self.notifier.addNotice('Unable to locate stepper','error')
	def OnAddJoystickActionClick(self):
		""" action - setup joystick action
		"""
		if(hasattr(self,'motor')):
			self.controller = self.motor.newController()
			self.editJoystickAction()
	def OnEditJoystickActionClick(self, index):
		""" action - edit joystick action
		"""
		if(hasattr(self,'motor')):
			self.controller = self.motor.controllers['joystick'][index]
			self.editJoystickAction()
	def OnDeleteJoystickActionClick(self, index):
		""" action - delete joystick action dialogue
		"""
		if(hasattr(self,'motor')):
			self.controller = self.motor.controllers['joystick'][index]
			self.deleteJoystickAction()
	def OnDeleteJoystickActionConfirmClick(self, index):
		""" action - delete joystick action
		"""
		if(hasattr(self,'controller') and index in self.motor.controllers['joystick'].keys()):
			del(self.motor.controllers['joystick'][index])
			self.motor.save()
			self.notifier.addNotice('Controller deleted')
			self.editControllers()
	def OnCaptureJoystickActionClick(self):
		""" action - start joystick action capture
		"""
		if(hasattr(self,'motor')):
			if(hasattr(self,'controller')):
				if(hasattr(self.gui,'joystickRegistry')):
					self.gui.joystickRegistry.addCallback('JoystickActionCapture', self.captureJoystickAction)
					self.notifier.addNotice('Waiting for input. Press any buton / move axis')
					self.widgets['infolabel'].configure(text='Double tap a button or move all the way along an axis.')
				else:
					self.notifier.addNotice('Joystick registry unavailable, check the joystick module.', 'warning')
			else:
				self.notifier.addNotice('Unable to determine controller', 'error')
		else:
			self.notifier.addNotice('Unable to determine motor', 'error')
	def OnInvertControllerClick(self):
		""" action - toggle joystick action invert
		"""
		if (hasattr(self,'controller')):
			self.controller['invert'] = not self.controller['invert']
	def OnJoystickActionDriveModeChange(self):
		""" action - change drive mode
		"""
		self.controller['drive_mode'] = self.variables['drive_mode'].get()
		self.updateDriveMode()
	def OnChangeMixMode(self):
		""" action - change mix mode
		"""
		self.controller['mix_mode'] = self.variables['mix'].get()
	def OnSaveJoystickActionClick(self):
		""" action - setup joystick action
		"""
		if (hasattr(self,'controller')):
			if (any(self.controller['device']) and isinstance(self.controller['dev_num'], int)):
				self.controller['drive_mode'] = self.variables['drive_mode'].get() #update drive mode
				if (self.controller['drive_mode'] == 'drive_state'):
					self.controller['mix_mode'] = self.variables['mix'].get() # update mix mode
				elif(self.controller['drive_mode'] in ['move_to','move_by']):
					if (self.controller['signal'] == 'axis'):
						try:
							self.controller['pos_angle'] = self.variables['positive'].get() #update positive angle
						except:
							self.notifier.addNotice('Invalid positive angle', 'warning')
							return
						try:
							self.controller['neg_angle'] = self.variables['negative'].get() #update negative angle
						except:
							self.notifier.addNotice('Invalid negative angle', 'warning')
							return
					else:
						try:
							self.controller['angle'] = self.variables['angle'].get() #update angle
						except:
							self.notifier.addNotice('Invalid angle', 'warning')
							return
				
				if ('dead_zone' in self.variables):
					dz = self.variables['dead_zone'].get()
					if (dz >= 0):
						if (dz < 1):
							self.controller['dead_zone'] = dz # update dead zone
						else:
							self.notifier.addNotice('Invalid dead zone (too high)', 'error')
							return
					else:
						self.notifier.addNotice('Invalid dead zone (too low)', 'error')
						return
				res = self.motor.updateController(self.controller)
				if (res == 'updated'):
					self.motor.save()
					self.notifier.addNotice('Motor controller saved')
					self.motor.controllersEnabled = True
					self.OnEditDCMotorControllersClick(self.motor.jbIndex) if self.motor.jbType == 'DcMotor' else self.OnEditStepperMotorControllersClick(self.motor.jbIndex)
				else:
					self.notifier.addNotice('Unable to register controller. (%s)' % res, 'warning')
			else:
				self.notifier.addNotice('Capture an action before saving', 'warning')
		else:
			self.notifier.addNotice('Unable to find controller', 'error')
	def OnAddKeyboardActionClick(self):
		""" action - setup keyboard action
		"""
		if(hasattr(self,'motor')):
			self.controller = self.motor.newController('keyboard')
			self.editKeyboardAction()
			self.motor.addCallback('angle_display', self.updateAngle)
	def OnEditKeyboardActionClick(self, index):
		""" action - edit existing keyboard action
		"""
		if(hasattr(self,'motor')):
			self.controller = self.motor.controllers['keyboard'][index]
			self.editKeyboardAction()
			self.motor.addCallback('angle_display', self.updateAngle)
	def OnCaptureKeyboardActionClick(self):
		""" action - triggers key capture
		"""
		self.widgets['capture'].configure(state='disabled')
		self.kbthread.addCallback('kb_action_capture', self.keyCapture)
		self.keycaptured = False
		self.notifier.addNotice('Press any key', 'warning')
	def OnSaveKeyboardActionClick(self):
		""" action - saves a keyboard action
		"""
		if (hasattr(self,'controller')):
			if (any(self.controller['ascii']) and any(self.controller['hex'])):
				if (self.controller['drive_mode'] == 'drive_state'):
					self.controller['mix_mode'] = self.variables['mix'].get() # update mix mode
				elif(self.controller['drive_mode'] in ['move_to','move_by']):
					try:
						self.controller['angle'] = self.variables['angle'].get() #update angle
					except:
						self.notifier.addNotice('Invalid angle', 'warning')
						return
				res = self.motor.updateController(self.controller, 'keyboard')
				if (res == 'updated'):
					self.motor.save()
					self.notifier.addNotice('Motor controller saved')
					self.motor.controllersEnabled = True
					self.OnEditDCMotorControllersClick(self.motor.jbIndex) if self.motor.jbType == 'DcMotor' else self.OnEditStepperMotorControllersClick(self.motor.jbIndex)
				else:
					self.notifier.addNotice('Controller update failed', 'error')
			else:
				self.notifier.addNotice('Capture a keyboard action before saving', 'warning')
	def OnDeleteKeyboardActionClick(self, index):
		""" action - display delete keyboard action
		"""
		if(hasattr(self,'motor')):
			self.controller = self.motor.controllers['keyboard'][index]
			self.deleteKeyboardAction()
	def OnDeleteKeyboardActionConfirmClick(self, index):
		""" action - delete keyboard action
		"""
		if(hasattr(self,'controller') and index in self.motor.controllers['keyboard'].keys()):
			del(self.motor.controllers['keyboard'][index])
			self.motor.save()
			self.notifier.addNotice('Controller deleted')
			self.editControllers()
	def OnStartKeyboardServiceClick(self):
		""" action - start Keyboard service
		"""
		kbm = self.gui.widgets['main']['TkKeyboardManager']
		if (not self.kbthread.isRunning()):
			kbm.OnStartClick()
			self.editKeyboardAction()
	
	#=== UTILS ===#
	def updateAngle(self, driveState):
		""" util - update angle display
		"""
		self.widgets['angdata'].configure(text=round(self.motor.angle,3))
	def updatePins(self):
		""" util - update pins display
		"""
		if ('pframe' in self.widgets.keys()):
			#update compatible
			if ('compatible' in self.widgets.keys()):
				if (any(self.widgets['compatible']['boards'])):
					for k,v in self.widgets['compatible']['boards'].items():
						v.grid_forget()
						del(v)
				row = 0
				if (self.motor.driveType in self.motor.driveTypes.keys()):
					dt = self.motor.driveTypes[self.motor.driveType]
					if (any(dt['compatible'])):
						for board in dt['compatible']:
							self.widgets['compatible']['boards'][board] = Tkinter.Label(self.widgets['compatible']['frame'],text=board, anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
							self.widgets['compatible']['boards'][board].grid(column=1,row=row, padx=10, pady=5, sticky='EW')
							row += 1
			#update pins
			if ('pins' not in self.widgets.keys()):
				self.widgets['pins'] = []
			else:
				for p in self.widgets['pins']:
					p.grid_forget()
					del(p)
				self.widgets['pins'] = []
			if (any(self.motor.pins)):
				frame = Tkinter.Frame(self.widgets['pframe'], bg=self.colours['bg'])
				frame.grid(column=0,row=0, sticky='EW')
				
				index = 0
				for p in self.motor.pins:
					self.widgets['pframe%s' % index] = Tkinter.Frame(frame, bg=self.colours['bg'], highlightthickness=1)
					self.widgets['pframe%s' % index].grid(column=0,row=index, padx=10, pady=5, sticky='EW')
					self.widgets['pnamelabel'] = Tkinter.Label(self.widgets['pframe%s' % index],text='Name', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
					self.widgets['pnamelabel'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
					self.widgets['pnamedata'] = Tkinter.Label(self.widgets['pframe%s' % index],text=p['name'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
					self.widgets['pnamedata'].grid(column=1,row=0, padx=10, pady=5, sticky='EW')
					self.widgets['ptypelabel'] = Tkinter.Label(self.widgets['pframe%s' % index],text='GPIO Type', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
					self.widgets['ptypelabel'].grid(column=0,row=1, padx=10, pady=5, sticky='EW')
					self.widgets['ptypedata'] = Tkinter.Label(self.widgets['pframe%s' % index],text=p['gpio_type'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
					self.widgets['ptypedata'].grid(column=1,row=1, padx=10, pady=5, sticky='EW')
					self.widgets['pnumlabel'] = Tkinter.Label(self.widgets['pframe%s' % index],text='Number', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
					self.widgets['pnumlabel'].grid(column=0,row=2, padx=10, pady=5, sticky='EW')
					self.variables['pnum%s' % index] = Tkinter.IntVar()
					self.widgets['pinentry%s' % index] = Tkinter.Entry(self.widgets['pframe%s' % index], textvariable=self.variables['pnum%s' % index], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
					self.widgets['pinentry%s' % index].grid(column=1,row=2, padx=10, pady=5,sticky='EW')
					self.variables['pnum%s' % index].set(p['number'])
					self.widgets['pins'].append(self.widgets['pframe%s' % index])
					index += 1
			else:
				frame = Tkinter.Frame(self.widgets['pframe'], bg=self.colours['bg'])
				frame.grid(column=0,row=0, sticky='EW')
				self.widgets['nopinlabel'] = Tkinter.Label(frame,text='No pin scheme available', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['nopinlabel'].grid(column=0,row=0, padx=10, pady=5, sticky='EW')
				self.widgets['pins'].append(frame)
	def showPinData(self, event):
		""" util - display pin data modal
		
		@param event
		"""
		canvas = event.widget
		pin = self.__findPin(event)
		if (pin != None):
			if (any(self.shapes['pinfo'])):
				for x in self.shapes['pinfo'].values():
					self.widgets['gpiocanvas'].delete(x)
				self.shapes['pinfo'] = {}
			pinfo = self.getPinInfo(pin)
			x = canvas.canvasx(event.x)
			y = canvas.canvasy(event.y)
			bbox = canvas.bbox(ALL)
			pos = [x+20, y]
			if (y > bbox[3] * 0.5):
				pos[1] -= 100
			self.shapes['pinfo']['bg'] = self.widgets['gpiocanvas'].create_rectangle(
				(
					pos[0],
					pos[1],
					pos[0]+140,
					pos[1]+100
				),
				fill=self.colours['bg'],
				tags='pindata'
			)
			#pin number
			self.shapes['pinfo']['pinLabel'] = self.widgets['gpiocanvas'].create_text(
				(
					pos[0]+10,
					pos[1]+10,
				),
				text='Pin',
				anchor='w',
				fill=self.colours['headingfg'],
				tags='pindata'
			)
			self.shapes['pinfo']['pinData'] = self.widgets['gpiocanvas'].create_text(
				(
					pos[0]+80,
					pos[1]+10,
				),
				text=str(pin),
				anchor='w',
				fill=self.colours['valuefg'],
				tags='pindata'
			)
			#pin name
			self.shapes['pinfo']['nameLabel'] = self.widgets['gpiocanvas'].create_text(
				(
					pos[0]+10,
					pos[1]+30,
				),
				text='Name',
				anchor='w',
				fill=self.colours['headingfg'],
				tags='pindata'
			)
			self.shapes['pinfo']['nameData'] = self.widgets['gpiocanvas'].create_text(
				(
					pos[0]+80,
					pos[1]+30,
				),
				text=pinfo['name'],
				anchor='w',
				fill=self.colours['valuefg'],
				tags='pindata'
			)
			#pin usage
			self.shapes['pinfo']['usageLabel'] = self.widgets['gpiocanvas'].create_text(
				(
					pos[0]+10,
					pos[1]+50,
				),
				text='Usage',
				anchor='w',
				fill=self.colours['headingfg'],
				tags='pindata'
			)
			self.shapes['pinfo']['usageData'] = self.widgets['gpiocanvas'].create_text(
				(
					pos[0]+80,
					pos[1]+50,
				),
				text=pinfo['default_usage'].upper(),
				anchor='w',
				fill=self.colours['valuefg'],
				tags='pindata'
			)
			#pin available
			self.shapes['pinfo']['availLabel'] = self.widgets['gpiocanvas'].create_text(
				(
					pos[0]+10,
					pos[1]+70,
				),
				text='Available',
				anchor='w',
				fill=self.colours['headingfg'],
				tags='pindata'
			)
			self.shapes['pinfo']['availData'] = self.widgets['gpiocanvas'].create_text(
				(
					pos[0]+80,
					pos[1]+70,
				),
				text='Yes' if self.isPinAvailable(pin) else 'No',
				anchor='w',
				fill=self.colours['valuefg'],
				tags='pindata'
			)
	def hidePinData(self, event):
		""" util - hide pin data modal
		
		@param event
		"""
		pin = self.__findPin(event)
		if (pin != None):
			if (any(self.shapes['pinfo'])):
				for x in self.shapes['pinfo'].values():
					self.widgets['gpiocanvas'].delete(x)
	def __findPin(self, event):
		""" util - locate active pin in canvas
		
		@param event
		
		@return int
		"""
		canvas = event.widget
		x = canvas.canvasx(event.x)
		y = canvas.canvasy(event.y)
		shape = canvas.find_closest(x, y, halo=6)
		pin = None
		if (any(shape)):
			pin = [k for k,v in self.shapes.items() if 'pin' in k and v in shape]
		if (any(pin)):
			pin = int(pin[0].replace('pin',''))
		else:
			pin = None
		return pin
	def updateDeadZone(self):
		""" util - update dead zone ui
		"""
		if (self.controller['signal'] == 'axis' and not 'dead_zone' in self.variables.keys()):
			if('dzinfo' in self.widgets.keys()):
				self.widgets['dzinfo'].grid_forget()
				del(self.widgets['dzinfo'])
			self.variables['dead_zone'] = Tkinter.DoubleVar()
			self.variables['dead_zone'].set(self.controller['dead_zone'] if 'dead_zone' in self.controller.keys() else 0.05)
			self.widgets['dzentry'] = Tkinter.Entry(self.widgets['dzframe'], textvariable=self.variables['dead_zone'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
			self.widgets['dzentry'].grid(column=0,row=0,sticky='EW')
		elif(self.controller['signal'] != 'axis'):
			if ('dead_zone' in self.variables.keys()):
				del(self.variables['dead_zone'])
			if ('dzentry' in self.widgets.keys()):
				self.widgets['dzentry'].grid_forget()
				del(self.widgets['dzentry'])
			if(not 'dzinfo' in self.widgets.keys()):
				self.widgets['dzinfo'] = Tkinter.Label(self.widgets['dzframe'],text='Axis only', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['dzinfo'].grid(column=0,row=self.gridrow, padx=10, pady=5, sticky='EW')
	def captureJoystickAction(self,dev_num,signal,number,name,value,init):
		""" util - capture a joystick action
		double tap a button or move axis over 0.5
		
		@param dev_num
		@param signal
		@param number
		@param name
		@param value
		@param init
		"""
		try:
			self.capture
		except:
			self.capture = {
				'captured': False,
				'args': {},
				'presses': {},
			}
		if (init == 0 and not self.capture['captured']):
			device = 'js%s' % dev_num
			if (signal == 'axis'):
				if (abs(value) > 0.5):
					#capture axis
					self.capture['captured'] = True
					self.capture['args'] = {
						'dev_num': dev_num,
						'signal': signal,
						'number': number,
						'name': name,
						'value': value,
						'init': init
					}
					self.__finishCaptureJoystickAction()
			elif (value == 1):
				if (not device in self.capture['presses'].keys()):
					self.capture['presses'][device] = {}
				if (not signal in self.capture['presses'][device].keys()):
					self.capture['presses'][device][signal] = {}
				index = 'b%s' % number
				if (not index in self.capture['presses'][device][signal].keys()):
					self.capture['presses'][device][signal][index] = {
						'number': number,
						'name': name,
					}
				else:
					#capture button
					self.capture['captured'] = True
					self.capture['args'] = {
						'dev_num': dev_num,
						'signal': signal,
						'number': number,
						'name': name,
						'value': value,
						'init': init
					}
					self.__finishCaptureJoystickAction()
		elif (init == 0 and self.gui.joystickRegistry.hasCallback('JoystickActionCapture')):
			self.__finishCaptureJoystickAction()
	def __finishCaptureJoystickAction(self):
		""" util - finish capture joystick action
		remove capture callback, update controller, update widgets, toast it!
		"""
		self.gui.joystickRegistry.removeCallback('JoystickActionCapture')
		if (any(self.capture['args'])):
			self.controller.update({
				'device': 'js%s' % self.capture['args']['dev_num'],
				'dev_num': self.capture['args']['dev_num'],
				'signal': self.capture['args']['signal'],
				'name': self.capture['args']['name'],
				'number': self.capture['args']['number']
			})
			self.widgets['devicedata'].configure(text=self.controller['device'])
			self.widgets['featuredata'].configure(text=self.controller['signal'])
			self.widgets['fiddata'].configure(text=self.controller['name'])
			self.widgets['infolabel'].configure(text='Captured')
			self.widgets['invertentry'].configure(state='normal')
			self.notifier.addNotice('Got it!')
			self.updateDriveMode()
			self.updateDeadZone()
			self.updateJoystickActionPreview()
		del(self.capture) #clear capture data
	def joystickActionPreviewCallback(self,dev_num,signal,number,name,value,init):
		""" util - joystick action preview callback
		update the ui for the joystick action
		
		@param dev_num
		@param signal
		@param number
		@param name
		@param value
		@param init
		"""
		if ('preview' in self.widgets):
			if (self.widgets['preview']['state'] == 'previewing'):
				if (self.widgets['preview']['dev_num'] == dev_num and self.widgets['preview']['signal'] == signal):
					updateDrive = False
					if (self.widgets['preview']['type'] == 'dual'):
						if (name == self.widgets['preview']['xaxis']):
							self.widgets['preview']['widget'].update('x', value)
						elif (name == self.widgets['preview']['yaxis']):
							self.widgets['preview']['widget'].update('y', value)
						if (name == self.widgets['preview']['current_axis']):
							if(self.controller['invert']):
								value = 0 - value
							updateDrive = True
					elif(self.widgets['preview']['number'] == number):
						self.widgets['preview']['widget'].update(value)
						if(self.controller['invert']):
							value = 0 - value
						updateDrive = True
					if (self.controller['drive_mode'] == 'zero_angle'):
						self.motor.setZeroAngle()
					if (updateDrive):
						if ('dead_zone' in self.variables.keys()):
							dz = self.variables['dead_zone'].get()
							if (dz > 0 and dz < 1):
								self.controller['dead_zone'] = dz # update dead zone
							if (self.controller['dead_zone'] > abs(value)):
								value = 0 # override under dead zone
						self.controller['drive_mode'] = self.variables['drive_mode'].get()
						if (self.controller['drive_mode'] == 'drive_state'):
								self.motor.setDriveState(value)
						elif (self.controller['drive_mode'] in ['move_to','move_by'] and abs(value) > 0.5):
							angleFunc = self.motor.moveToAngle if self.controller['drive_mode'] == 'move_to' else self.motor.moveByAngle
							if (self.controller['signal'] == 'axis'):
								try:
									self.controller['pos_angle'] = self.variables['positive'].get() #try updating the pos angle
								except:
									return
								try:
									self.controller['neg_angle'] = self.variables['negative'].get() #try updating the neg angle
								except:
									return
								angleFunc(self.controller['pos_angle'] if value > 0 else self.controller['neg_angle'])
							else:
								try:
									self.controller['angle'] = self.variables['angle'].get() #try updating the angle
								except:
									return
								angleFunc(self.controller['angle'])
						try:
							self.widgets['angle'].configure(text=round(self.motor.angle,3)) # try to update the angle widget
						except:
							pass
	def keyCapture(self, hex, ascii):
		""" util - captures pressed key
		
		@param event
		"""
		if(not self.keycaptured):
			self.keycaptured = True
			self.controller.update({
				'hex': hex,
				'ascii': ascii
			})
			self.widgets['asciidata'].configure(text=ascii)
			self.widgets['hexdata'].configure(text=hex)
			self.kbthread.removeCallback('kb_action_capture') # no longer required
			self.widgets['capture'].configure(state='normal') # allow another capture
			self.widgets['invertentry'].configure(state='normal') # allow invert to be set
			self.notifier.addNotice('Got it!')
			self.updateDriveMode()
	def getUsedPins(self, ignore = []):
		""" util - get used pins
		find used pins except those in ignore
		
		@param ignore list
		"""
		up = []
		for x in self.specification.motors.values():
			if (not x.jbIndex in ignore):
				for p in x.pins:
					up.append(p['number'])
		for x in self.specification.steppers.values():
			if (not x.jbIndex in ignore):
				for p in x.pins:
					up.append(p['number'])
		return up
	def isGpioPin(self, number):
		""" util - check if default pin usage is gpio
		avoids reassigning pins used for other peripherals
		
		@param number int
		"""
		pin = [x for x in self.gpioInfo if x['number'] == number and x['default_usage'] == 'gpio']
		if (any(pin)):
			return True
		return False
	def isPinAvailable(self, number):
		""" util - check if a pin is available for gpio usage
		returns False if not a gpio pin or it is already occupied
		
		@param number int
		"""
		pin = [x for x in self.gpioInfo if x['number'] == number and x['default_usage'] == 'gpio']
		if (any(pin) and not pin[0]['number'] in self.getUsedPins()):
			return True
		return False
	def getPinInfo(self, number):
		""" util - gets data about a given pin
		
		@param number int
		
		@return dict
		"""
		pin = [x for x in self.gpioInfo if x['number'] == number]
		if (any(pin)):
			return pin[0]
		return None
		
	def close(self):
		""" override - remove callbacks if required
		"""
		if (hasattr(self, 'motor')):
			if (self.motor.hasCallback('angle_display')):
				self.motor.removeCallback('angle_display')
			self.motor.stop()
			if (self.motor.blobExists()):
				self.motor.reload() #remove unsaved changes
			self.kbthread.removeCallback('kb_action_capture') #in case kb capture was not completed
		super(TkMotorManager,self).close()