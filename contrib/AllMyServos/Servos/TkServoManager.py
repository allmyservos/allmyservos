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
import Tkinter
from Tkinter import *
from TkBlock import *
import ttk
from DB import *
from Motion import *
from xml.dom import minidom
from xml.dom.minidom import Document

## UI for servos
class TkServoManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes TkServoManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkServoManager,self).__init__(parent, gui, **options)
		if(gui.specification != None):
			self.specification = gui.specification
		else:
			self.specification = Specification()
		self.servos = gui.specification.servos
	def setup(self):
		""" setup gui menu
		"""
		self.gui.menus['servo'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		self.gui.menus['servo'].add_command(label="New", command=self.OnAddServoClick)
		self.gui.menus['servo'].add_separator()
		self.gui.menus['servo'].add_command(label="Test", command=self.OnTestServosClick)
		self.gui.menus['servo'].add_command(label="Configure", command=self.OnListServosClick)
		self.addMenu(label="Servos", menu=self.gui.menus['servo'])
	
	#=== VIEWS ===#
	def listServos(self):
		""" view - list servos
		"""
		self.open()
		self.gridrow = 0
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Servos / Configuration', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['addservo'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Servo", image=self.images['add'], command=self.OnAddServoClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addservo'].grid(column=1,row=self.gridrow)
		self.widgets['testservos'] = Tkinter.Button(self.widgets['tframe'],text=u"Test Servos", image=self.images['test'], command=self.OnTestServosClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['testservos'].grid(column=2,row=self.gridrow)
		self.gridrow += 1

		self.widgets['listFrame'] = Tkinter.Frame(self.widgets['tframe'], borderwidth=0, highlightthickness=0, bg=self.colours['bg'])
		self.widgets['listFrame'].grid(column=0,row=self.gridrow,columnspan=3,sticky='EW')
		
		self.gridrow = 0
		
		if(any(self.servos)):
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['listFrame'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['channelLabel'] = Tkinter.Label(self.widgets['listFrame'],text='Channel', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['channelLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['angleLabel'] = Tkinter.Label(self.widgets['listFrame'],text='Default Angle', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['angleLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['trimLabel'] = Tkinter.Label(self.widgets['listFrame'],text='Trim', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['trimLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['disabledLabel'] = Tkinter.Label(self.widgets['listFrame'],text='Disabled', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['disabledLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.widgets['optionsLabel'] = Tkinter.Label(self.widgets['listFrame'],text='Edit', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['optionsLabel'].grid(column=5,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			rowcount = 0
			for s in self.channelindex:
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['name'+str(self.gridrow)] = Tkinter.Label(self.widgets['listFrame'],text=s.jsonData['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['name'+str(self.gridrow)].grid(column=0,row=self.gridrow,sticky='EW')
				
				self.widgets['channel'+str(self.gridrow)] = Tkinter.Label(self.widgets['listFrame'],text=s.jsonData['channel'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['channel'+str(self.gridrow)].grid(column=1,row=self.gridrow,sticky='EW')
				
				self.widgets['angle'+str(self.gridrow)] = Tkinter.Label(self.widgets['listFrame'],text=s.jsonData['angle'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['angle'+str(self.gridrow)].grid(column=2,row=self.gridrow,sticky='EW')
				
				self.widgets['trim'+str(self.gridrow)] = Tkinter.Label(self.widgets['listFrame'],text=s.jsonData['trim'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['trim'+str(self.gridrow)].grid(column=3,row=self.gridrow,sticky='EW')
				
				self.variables['disabled'+str(self.gridrow)] = Tkinter.IntVar()
				self.widgets['disabledentry'+str(self.gridrow)] = Tkinter.Checkbutton(self.widgets['listFrame'], text="Disabled", highlightthickness=0, state=DISABLED, variable=self.variables['disabled'+str(self.gridrow)], bg=rowcolour, fg=self.colours['fg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], height=2)
				self.widgets['disabledentry'+str(self.gridrow)].grid(column=4,row=self.gridrow)
				self.variables['disabled'+str(self.gridrow)].set(s.jsonData['disabled'])
				
				self.widgets['edit'+str(self.gridrow)] = Tkinter.Button(self.widgets['listFrame'],text=u"Edit Servo", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = s.jbIndex:self.OnEditServoClick(x))
				self.widgets['edit'+str(self.gridrow)].grid(column=5,row=self.gridrow,sticky='EW')
				
				self.gridrow += 1
		else:
			self.widgets['emptylabel'] = Tkinter.Label(self.widgets['listFrame'], text="There are currently no servos", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['emptylabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.gridrow += 1
	def editServo(self):
		""" view - edit servo
		"""
		self.open()
		self.gridrow = 0
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Servos / Servo / Edit', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['name'] = Tkinter.StringVar()
		self.widgets['nameentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['name'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['nameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.servo.blobExists()):
			self.variables['name'].set(self.servo.jsonData['name'])
		
		self.gridrow += 1
		
		self.widgets['channelLabel'] = Tkinter.Label(self.widgets['tframe'],text='Channel', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['channelLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['channel'] = Tkinter.IntVar()
		self.widgets['channelentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['channel'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['channelentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.servo.blobExists()):
			self.variables['channel'].set(int(self.servo.jsonData['channel']))
		
		self.gridrow += 1
		
		self.widgets['minLabel'] = Tkinter.Label(self.widgets['tframe'],text='PWM Min', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['minLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['min'] = Tkinter.IntVar()
		self.variables['min'].set(int(self.servo.jsonData['servoMin']))
		self.widgets['minentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['min'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['minentry'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['maxLabel'] = Tkinter.Label(self.widgets['tframe'],text='PWM Max', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['maxLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['max'] = Tkinter.IntVar()
		self.variables['max'].set(int(self.servo.jsonData['servoMax']))
		self.widgets['maxentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['max'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['maxentry'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['angleLabel'] = Tkinter.Label(self.widgets['tframe'],text='Angle', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['angleLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['angle'] = Tkinter.IntVar()
		self.variables['angle'].set(int(self.servo.jsonData['angle']))
		self.widgets['angleentry'] = Tkinter.Scale(self.widgets['tframe'], from_=0, to=180, variable=self.variables['angle'], command=self.OnAngleChange, resolution=1, orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
		self.widgets['angleentry'].grid(column=1,row=self.gridrow)
		
		if(self.servo.blobExists()):
			self.variables['pulse'] = Tkinter.IntVar()
			self.variables['pulse'].set(self.servo.pulsetable[self.servo.jsonData['angle']])
			self.widgets['pulseLabel'] = Tkinter.Label(self.widgets['tframe'],text='PWM Value', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['pulseLabel'].grid(column=2,row=self.gridrow, padx=10, sticky='EW')
			self.widgets['pulse'] = Tkinter.Label(self.widgets['tframe'],textvariable=self.variables['pulse'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
			self.widgets['pulse'].grid(column=3,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['trimLabel'] = Tkinter.Label(self.widgets['tframe'],text='Trim', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['trimLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['trim'] = Tkinter.IntVar()
		self.widgets['trimentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['trim'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['trimentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.servo.blobExists()):
			self.variables['trim'].set(int(self.servo.jsonData['trim']))
		
		self.gridrow += 1
		
		self.widgets['disabledLabel'] = Tkinter.Label(self.widgets['tframe'],text='Disabled', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['disabledLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['disabled'] = Tkinter.BooleanVar()
		self.widgets['disabledentry'] = Tkinter.Checkbutton(self.widgets['tframe'], text="Disabled", variable=self.variables['disabled'], bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['disabledentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.servo.blobExists()):
			self.variables['disabled'].set(bool(self.servo.jsonData['disabled']))
		
		self.gridrow += 1
		
		self.widgets['invertedLabel'] = Tkinter.Label(self.widgets['tframe'],text='Inverted', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['invertedLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['inverted'] = Tkinter.BooleanVar()
		self.widgets['invertedentry'] = Tkinter.Checkbutton(self.widgets['tframe'], text="Inverted", variable=self.variables['inverted'], bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['invertedentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.servo.blobExists()):
			self.variables['inverted'].set(bool(self.servo.jsonData['inverted']))
		
		self.gridrow += 1
		
		self.widgets['partNoLabel'] = Tkinter.Label(self.widgets['tframe'],text='Part No.', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['partNoLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['partNo'] = Tkinter.StringVar()
		self.widgets['partNoentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['partNo'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['partNoentry'].grid(column=1,row=self.gridrow,sticky='EW')

		if(self.servo.blobExists()):
			self.variables['partNo'].set(self.servo.jsonData['partNo'])
		
		self.gridrow += 1
		
		self.widgets['blenderLabel'] = Tkinter.Label(self.widgets['tframe'],text='Blender Attributes', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['blenderLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['boneNameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Bone Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['boneNameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['boneName'] = Tkinter.StringVar()
		self.widgets['boneNameentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['boneName'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['boneNameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.servo.blobExists()):
			self.variables['boneName'].set(self.servo.jsonData['boneName'])
			
		self.gridrow += 1
		
		self.widgets['boneArmatureLabel'] = Tkinter.Label(self.widgets['tframe'],text='Bone Armature', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['boneArmatureLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['boneArmature'] = Tkinter.StringVar()
		self.widgets['boneArmatureentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['boneArmature'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['boneArmatureentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.servo.blobExists()):
			self.variables['boneArmature'].set(self.servo.jsonData['boneArmature'])
		
		self.gridrow += 1
		
		self.widgets['boneAxisLabel'] = Tkinter.Label(self.widgets['tframe'],text='Bone Axis', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['boneAxisLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['boneAxis'] = Tkinter.StringVar()
		self.widgets['boneAxisentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['boneAxis'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['boneAxisentry'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.widgets['boneAxisentry'] = Tkinter.OptionMenu(self.widgets['tframe'],self.variables['boneAxis'], 'x', 'y', 'z')
		self.widgets['boneAxisentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
		self.widgets['boneAxisentry'].grid(column=1,row=self.gridrow,sticky='EW')
		
		if(self.servo.blobExists()):
			self.variables['boneAxis'].set(self.servo.jsonData['boneAxis'])
			
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.servo.blobExists()):
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['deleteLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Motion", image=self.images['back'], command=self.listServos, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['saveservo'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Servo", image=self.images['save'], command=self.OnSaveServoClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['saveservo'].grid(column=1,row=self.gridrow)
		if(self.servo.blobExists()):
			self.widgets['deleteservo'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete Servo", image=self.images['delete'], command=self.OnDeleteServoClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['deleteservo'].grid(column=2,row=self.gridrow)
	def deleteServo(self):
		""" view - delete servo
		"""
		self.open()
		self.gridrow = 0
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Delete Servo', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		self.widgets['confirmlabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this servo?', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['confirmlabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['namelabel'] = Tkinter.Label(self.widgets['tframe'],text="Name", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['namelabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['namedata'] = Tkinter.Label(self.widgets['tframe'],text=self.servo.jsonData['name'], bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['namedata'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['channellabel'] = Tkinter.Label(self.widgets['tframe'],text="Channel", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['channellabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['channeldata'] = Tkinter.Label(self.widgets['tframe'],text=self.servo.jsonData['channel'], bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['channeldata'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['acceptlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Accept", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['acceptlabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['cancelbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Cancel", image=self.images['back'], command=self.OnCancelDeleteClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['cancelbutton'].grid(column=0,row=self.gridrow)
		self.widgets['confirmbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['accept'], command=self.OnDeleteServoConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['confirmbutton'].grid(column=1,row=self.gridrow)
	def testServos(self):
		""" view - test servos
		"""
		self.open()
		self.gridrow = 0
		self.widgets['testheading'] = Tkinter.Label(self.widgets['tframe'],text='Servos / Default Pose', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['testheading'].grid(column=0,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		
		if(any(self.servos)):
			self.widgets['nameheading'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['nameheading'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['channelheading'] = Tkinter.Label(self.widgets['tframe'],text='Channel', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['channelheading'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['angleheading'] = Tkinter.Label(self.widgets['tframe'],text='Angle', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['angleheading'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['trimheading'] = Tkinter.Label(self.widgets['tframe'],text='Trim', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['trimheading'].grid(column=3,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			rowcount = 0
			for s in self.channelindex:
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['namelabel'+str(s.jbIndex)] = Tkinter.Label(self.widgets['tframe'],text=s.jsonData['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['namelabel'+str(s.jbIndex)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['channellabel'+str(s.jbIndex)] = Tkinter.Label(self.widgets['tframe'],text=s.jsonData['channel'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['channellabel'+str(s.jbIndex)].grid(column=1,row=self.gridrow,sticky='EW')
				
				self.variables['angle'+str(s.jbIndex)] = Tkinter.IntVar()
				self.variables['angle'+str(s.jbIndex)].set(int(s.angle))
				self.widgets['angleentry'+str(s.jbIndex)] = Tkinter.Scale(self.widgets['tframe'], from_=0, to=180, borderwidth=0, variable=self.variables['angle'+str(s.jbIndex)], command=self.OnUpdateAngles, resolution=1, orient=Tkinter.HORIZONTAL, length = 180, bg=rowcolour, fg=self.colours['fg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
				self.widgets['angleentry'+str(s.jbIndex)].grid(column=2,row=self.gridrow)

				self.variables['servotrim'+str(s.jbIndex)] = Tkinter.IntVar()
				self.widgets['trimentry'+str(s.jbIndex)] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['servotrim'+str(s.jbIndex)], bg=self.colours['inputbg'], fg=self.colours['inputfg'], width=5)
				self.widgets['trimentry'+str(s.jbIndex)].grid(column=3,row=self.gridrow,sticky='EW', padx=5)
				self.variables['servotrim'+str(s.jbIndex)].set(int(s.trim))
				self.gridrow += 1
			self.gridrow += 1
		
			self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
			self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
			
			self.gridrow = 0
			
			self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['acceptlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Save", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['acceptlabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['resetlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Reset", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['resetlabel'].grid(column=2,row=self.gridrow,sticky='EW')
			
			self.gridrow += 1
			
			self.widgets['cancelbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Cancel", image=self.images['back'], command=self.OnCancelDeleteClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['cancelbutton'].grid(column=0,row=self.gridrow)
			self.widgets['confirmbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['accept'], command=self.OnSaveServosClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['confirmbutton'].grid(column=1,row=self.gridrow)
			self.widgets['resetbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Reset", image=self.images['reset'], command=self.OnResetServosClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['resetbutton'].grid(column=2,row=self.gridrow)
		else:
			self.widgets['infoLabel1'] = Tkinter.Label(self.widgets['tframe'],text='There are currently no servos.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['infoLabel1'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
			self.gridrow += 1
		
			self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
			self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
			
			self.gridrow = 0
			
			self.widgets['addlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Add", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['addlabel'].grid(column=0,row=self.gridrow,sticky='EW')
			
			self.gridrow += 1
			
			self.widgets['addbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Add", image=self.images['add'], command=self.OnAddServoClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['addbutton'].grid(column=0,row=self.gridrow)
	
	#=== ACTIONS ===#
	def OnListServosClick(self):
		""" action - display servo list page
		"""
		self.refreshServos()
		self.listServos()
	def OnAddServoClick(self):
		""" action - display add servo page
		"""
		self.servo = Servo()
		self.editServo()
	def OnEditServoClick(self, index = None):
		""" action - display edit servo page
		"""
		self.servo = self.servos[index]
		self.editServo()
	def OnSaveServoClick(self):
		""" action - save servo
		"""
		channels = [ x.channel for x in self.servos.values() ]
		if(not self.servo.blobExists() and self.variables['channel'].get() in channels):
			self.notifier.addNotice('A servo is already configured for this channel. Please choose another.','warning')
			return
		if(self.variables['name'].get() == ''):
			self.notifier.addNotice('Please enter a name','warning')
			return
		if(int(self.variables['channel'].get()) < 0):
			self.notifier.addNotice('Channel must be zero or above','warning')
			return
		if(int(self.variables['trim'].get()) < 0):
			self.notifier.addNotice('Trim must be zero or above','warning')
			return
		if(int(self.variables['min'].get()) < 0 or int(self.variables['min'].get()) > 4096):
			self.notifier.addNotice('Please enter a valid PWM minimum value (0 - 4096)','warning')
			return
		if(int(self.variables['max'].get()) < 0 or int(self.variables['max'].get()) > 4096):
			self.notifier.addNotice('Please enter a valid PWM maximum value (0 - 4096)','warning')
			return
		if(int(self.variables['max'].get()) <= int(self.variables['min'].get())):
			self.notifier.addNotice('PWM min must be less than PWM max','warning')
			return
		
		self.servo.jsonData['name'] = self.variables['name'].get()
		self.servo.jsonData['channel'] = self.variables['channel'].get()
		self.servo.jsonData['angle'] = self.variables['angle'].get()
		self.servo.jsonData['trim'] = self.variables['trim'].get()
		self.servo.jsonData['disabled'] = self.variables['disabled'].get()
		self.servo.jsonData['inverted'] = self.variables['inverted'].get()
		self.servo.jsonData['partNo'] = self.variables['partNo'].get()
		self.servo.jsonData['boneName'] = self.variables['boneName'].get()
		self.servo.jsonData['boneArmature'] = self.variables['boneArmature'].get()
		self.servo.jsonData['boneAxis'] = self.variables['boneAxis'].get()
		self.servo.save()
		self.specification.servos[self.servo.jbIndex] = self.servo
		self.specification.save()
		self.notifier.addNotice('Servo saved')
		self.refreshServos()
		self.gui.widgets['left']['TkServoGrid'].OnShowGridClick()
		self.listServos()
	def OnDeleteServoClick(self):
		""" action - display delete servo page
		"""
		self.deleteServo()
	def OnCancelDeleteClick(self):
		""" action - cancel delete servo
		"""
		self.OnListServosClick()
	def OnDeleteServoConfirmClick(self):
		""" action - delete servo
		"""
		if hasattr(self, 'servo'):
			del(self.specification.servos[self.servo.jbIndex])
			self.specification.save()
			self.servo.delete()
			self.servo = None
			self.refreshServos()
			self.listServos()
	def OnTestServosClick(self):
		""" action - display servo test page
		"""
		self.refreshServos()
		self.testServos()
	def OnSaveServosClick(self):
		""" action - display save servos page
		"""
		for s in self.servos:
			self.servos[s].save()
		self.listServos()
	def OnResetServosClick(self):
		""" action - reset servos
		"""
		for s in self.servos.values():
			s.reload()
			s.setServoAngle()
		self.testServos()
	def OnAngleChange(self, newangle):
		""" action - angle change
		
		@param newangle
		"""
		self.servo.angle = int(newangle)
		if(self.servo.blobExists()):
			self.servo.setServoAngle()
			self.variables['pulse'].set(self.servo.pulsetable[self.servo.angle])
	def OnUpdateAngles(self, event):
		""" action - update angles
		
		@param event
		"""
		for s in self.servos.values():
			if ('angle'+str(s.jbIndex) in self.variables.keys()):
				s.angle = self.variables['angle'+str(s.jbIndex)].get()
				s.setServoAngle()
	
	#=== UTILS ===#
	def refreshServos(self):
		""" util - refresh servos
		"""
		if (any(self.servos)):
			for s in self.servos.values():
				s.reload()
		else:
			self.servos = self.gui.specification.servos
		self.channelindex = sorted(self.servos.values(), key=lambda x: x.jsonData['channel'])