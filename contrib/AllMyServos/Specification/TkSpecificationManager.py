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
import Tkinter, tkColorChooser, os, shutil, datetime
from __bootstrap import AmsEnvironment
from Tkinter import *
from tkFileDialog import askopenfilename
from TkBlock import TkPage
from Specification import Specification
from subprocess import Popen, PIPE
from Motion import Servo, Motion

## UI for specifications
class TkSpecificationManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes TkSpecificationManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkSpecificationManager,self).__init__(parent, gui, **options)
		if(hasattr(self.gui, 'specification')):
			self.current = self.gui.specification
		else:
			self.current = Specification.GetInstance()
	def setup(self):
		""" setup gui menu
		"""
		try:
			self.gui.menus['file']
		except:
			self.gui.menus['file'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="File", menu=self.gui.menus['file'])
		try:
			self.gui.menus['spec']
		except:
			self.gui.menus['spec'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.gui.menus['file'].insert_cascade(index=0, label="Specification", menu=self.gui.menus['spec'])
		self.gui.menus['spec'].add_command(label="Current Specification", command=self.OnCurrentSpecificationClick)
		self.gui.menus['spec'].add_command(label="List Specifications", command=self.OnListSpecificationsClick)
		self.gui.menus['spec'].add_command(label="Install Specification", command=self.OnInstallSpecificationClick)
	
	#=== VIEWS ===#
	def listSpecifications(self):
		""" view - list specifications
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Specifications', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.widgets['new'] = Tkinter.Button(self.widgets['tframe'],text=u"New", image=self.images['add'], command=self.OnNewClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['new'].grid(column=6,row=self.gridrow)
		self.gridrow += 1
		rowcount = 1
		if(any(self.specs)):
			self.widgets['codenameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Codename', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['codenameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['identLabel'] = Tkinter.Label(self.widgets['tframe'],text='Ident', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['identLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['packageLabel'] = Tkinter.Label(self.widgets['tframe'],text='Packaged', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['packageLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['activateLabel'] = Tkinter.Label(self.widgets['tframe'],text='Activate', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['activateLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['viewLabel'] = Tkinter.Label(self.widgets['tframe'],text='View', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['viewLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.widgets['cloneLabel'] = Tkinter.Label(self.widgets['tframe'],text='Clone', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['cloneLabel'].grid(column=5,row=self.gridrow,sticky='EW')
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['tframe'],text='Uninstall', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['deleteLabel'].grid(column=6,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			for s in self.specs.values():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['codename'+s.jbIndex] = Tkinter.Label(self.widgets['tframe'],text=s.jsonData['codename'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['codename'+s.jbIndex].grid(column=0,row=self.gridrow, ipadx=20, sticky='EW')
				self.widgets['ident'+s.jbIndex] = Tkinter.Label(self.widgets['tframe'],text=s.jbIndex, bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['ident'+s.jbIndex].grid(column=1,row=self.gridrow, ipadx=10,sticky='EW')
				self.widgets['package'+s.jbIndex] = Tkinter.Label(self.widgets['tframe'],text='Exists' if s.isPackaged() > 0 else 'TBD', bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['package'+s.jbIndex].grid(column=2,row=self.gridrow, ipadx=10,sticky='EW')
				self.widgets['activate'+s.jbIndex] = Tkinter.Button(self.widgets['tframe'],text=u"Activate", image=self.images['play'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = s.jbIndex:self.OnActivateClick(x))
				self.widgets['activate'+s.jbIndex].grid(column=3,row=self.gridrow, sticky='EW')
				self.widgets['view'+s.jbIndex] = Tkinter.Button(self.widgets['tframe'],text=u"View", image=self.images['find'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = s.jbIndex:self.OnViewSpecificationClick(x))
				self.widgets['view'+s.jbIndex].grid(column=4,row=self.gridrow, sticky='EW')
				self.widgets['clone'+s.jbIndex] = Tkinter.Button(self.widgets['tframe'],text=u"Clone", image=self.images['ram'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = s.jbIndex:self.OnCloneSpecificationClick(x))
				self.widgets['clone'+s.jbIndex].grid(column=5,row=self.gridrow, sticky='EW')
				self.widgets['delete'+s.jbIndex] = Tkinter.Button(self.widgets['tframe'],text=u"Uninstall", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = s.jbIndex:self.OnDeleteSpecificationClick(x))
				self.widgets['delete'+s.jbIndex].grid(column=6,row=self.gridrow, sticky='EW')
				if(self.gui.specification.jbIndex == s.jbIndex):
					self.widgets['activate'+s.jbIndex].configure(state='disabled')
					self.widgets['delete'+s.jbIndex].configure(state='disabled')
				self.gridrow += 1
		else:
			self.widgets['noSpecsLabel'] = Tkinter.Label(self.widgets['tframe'],text='There are currently no specifications.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noSpecsLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
	def viewSpecification(self):
		""" view - view specification
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Specifications / View Specification', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['infoframe'].grid(column=0,row=self.gridrow, pady=20, sticky='EW')
		self.widgets['infoframe'].rowconfigure(3, weight=1)
		
		#codename
		self.widgets['codenameLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Codename:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], height=3)
		self.widgets['codenameLabel'].grid(column=0,row=0,padx=20,sticky='NW')
		self.widgets['codenameData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jsonData['codename'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], font=self.fonts['heading2'], height=3)
		self.widgets['codenameData'].grid(column=1,row=0,padx=10,sticky='NW')
		if(not self.spec.jsonData['locked']):
			self.widgets['codenameChange'] = Tkinter.Button(self.widgets['infoframe'],text=u"Change", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.OnChangeCodenameClick)
			self.widgets['codenameChange'].grid(column=2,row=0, sticky='SE')
		
		#ident
		self.widgets['identLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Ident:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['identLabel'].grid(column=0,row=1,padx=20,sticky='NW')
		self.widgets['identData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jbIndex, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['identData'].grid(column=1,row=1,padx=10,columnspan=3, sticky='NW')
		
		#blendfile
		self.widgets['blendfileLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Blendfile:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['blendfileLabel'].grid(column=0,row=2,padx=20,sticky='NW')
		self.widgets['blendfileData'] = Tkinter.Label(self.widgets['infoframe'],text='Not Available', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['blendfileData'].grid(column=1,row=2,padx=10,sticky='NW')
		if(self.spec.jsonData['blendfile'] != ''):
			self.widgets['blendfileData'].configure(text=self.spec.jsonData['blendfile'], fg=self.colours['valuefg'])
			self.widgets['blendfileView'] = Tkinter.Button(self.widgets['infoframe'],text=u"View", image=self.images['find'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.OnViewBlendClick)
			self.widgets['blendfileView'].grid(column=2,row=2, sticky='SE')
		if(not self.spec.jsonData['locked']):
			self.widgets['blendfileChange'] = Tkinter.Button(self.widgets['infoframe'],text=u"Change", image=self.images['blender'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.OnChangeBlendClick)
			self.widgets['blendfileChange'].grid(column=3,row=2, sticky='SE')
		
		#status
		self.widgets['statusLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Status:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['statusLabel'].grid(column=0,row=3,padx=20,sticky='NW')
		self.widgets['statusData'] = Tkinter.Label(self.widgets['infoframe'],text='Inactive', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['statusData'].grid(column=1,row=3,padx=10,sticky='NW')
		if(self.spec.jbIndex == self.current.jbIndex):
			self.widgets['statusData'].configure(text='Active', fg=self.colours['valuefg'])
			
		#package
		self.widgets['packageLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Package Created', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['packageLabel'].grid(column=0,row=4,padx=20,sticky='NW')
		self.widgets['packageData'] = Tkinter.Label(self.widgets['infoframe'],text='TBD', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['packageData'].grid(column=1,row=4,padx=10, sticky='NW')
		if(self.spec.isPackaged()):
			self.widgets['packageData'].configure(text=datetime.datetime.fromtimestamp(self.spec.getPackageTimestamp()),fg=self.colours['valuefg'])
			self.widgets['viewPackage'] = Tkinter.Button(self.widgets['infoframe'],text=u"View Package", image=self.images['find'], command=self.OnViewPackageClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['viewPackage'].grid(column=2,row=4)
		self.widgets['package'] = Tkinter.Button(self.widgets['infoframe'],text=u"Package", image=self.images['process'], command=self.OnPackageClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['package'].grid(column=3,row=4)
		
		#thumbnail
		self.widgets['thumbframe'] = Tkinter.Frame(self.widgets['infoframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['thumbframe'].grid(column=4,row=0,rowspan=5, padx=20,sticky='EW')
		self.widgets['thumbLabel'] = Tkinter.Label(self.widgets['thumbframe'],text='Thumbnail', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['thumbLabel'].grid(column=0,row=0,columnspan=2,sticky='EW')
		self.widgets['thumbData'] = Tkinter.Label(self.widgets['thumbframe'],text='Not Available', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['thumbData'].grid(column=0,row=1,sticky='EW')
		if(not self.spec.jsonData['locked']):
			self.widgets['thumbChange'] = Tkinter.Button(self.widgets['thumbframe'],text=u"Change", image=self.images['image'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.OnChangeThumbClick)
			self.widgets['thumbChange'].grid(column=1,row=1, sticky='SE')
		
		if(self.spec.jsonData['thumbfile'] != ''):
			self.thumbimage = Tkinter.PhotoImage(file = os.path.join(self.spec.getInstallPath(), self.spec.jsonData['thumbfile']))
			self.widgets['thumbData'].configure(image=self.thumbimage)
		
		self.gridrow += 1
		
		#servos
		self.widgets['servosLabel'] = Tkinter.Label(self.widgets['tframe'],text='Servos', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['servosLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		if(not self.spec.jsonData['locked'] and self.current.jbIndex == self.spec.jbIndex):
			self.widgets['addservo'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Servo", image=self.images['add'], command=self.OnAddServoClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['addservo'].grid(column=2,row=self.gridrow)
		self.gridrow += 1
		self.widgets['sframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['sframe'].grid(column=0,row=self.gridrow,pady=15, columnspan=3, sticky='EW')
		if(any(self.spec.servos)):
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['sframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['channelLabel'] = Tkinter.Label(self.widgets['sframe'],text='Channel', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['channelLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['angleLabel'] = Tkinter.Label(self.widgets['sframe'],text='Default Angle', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['angleLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['trimLabel'] = Tkinter.Label(self.widgets['sframe'],text='Trim', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['trimLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['disabledLabel'] = Tkinter.Label(self.widgets['sframe'],text='Disabled', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['disabledLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.widgets['displayLabel'] = Tkinter.Label(self.widgets['sframe'],text='Display Order', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['displayLabel'].grid(column=5,row=self.gridrow,sticky='EW')
			self.widgets['minLabel'] = Tkinter.Label(self.widgets['sframe'],text='PWM Min', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['minLabel'].grid(column=6,row=self.gridrow,sticky='EW')
			self.widgets['maxLabel'] = Tkinter.Label(self.widgets['sframe'],text='PWM Max', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['maxLabel'].grid(column=7,row=self.gridrow,sticky='EW')
			self.widgets['boneNameLabel'] = Tkinter.Label(self.widgets['sframe'],text='Bone Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['boneNameLabel'].grid(column=8,row=self.gridrow,sticky='EW')
			self.widgets['boneArmatureLabel'] = Tkinter.Label(self.widgets['sframe'],text='Armature', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['boneArmatureLabel'].grid(column=9,row=self.gridrow,sticky='EW')
			self.widgets['boneAxisLabel'] = Tkinter.Label(self.widgets['sframe'],text='Bone Axis', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['boneAxisLabel'].grid(column=10,row=self.gridrow,sticky='EW')
			self.widgets['partNoLabel'] = Tkinter.Label(self.widgets['sframe'],text='Part No.', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['partNoLabel'].grid(column=11,row=self.gridrow,sticky='EW')
			rowcount = 1
			self.gridrow += 1
			for v in self.spec.servos.values():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['nameLabel'] = Tkinter.Label(self.widgets['sframe'],text=v.jsonData['name'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['channelLabel'] = Tkinter.Label(self.widgets['sframe'],text=v.jsonData['channel'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['channelLabel'].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['angleLabel'] = Tkinter.Label(self.widgets['sframe'],text=v.jsonData['angle'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['angleLabel'].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['trimLabel'] = Tkinter.Label(self.widgets['sframe'],text=v.jsonData['trim'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['trimLabel'].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['disabledLabel'] = Tkinter.Label(self.widgets['sframe'],text=str(v.jsonData['disabled']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['disabledLabel'].grid(column=4,row=self.gridrow,sticky='EW')
				self.widgets['displayLabel'] = Tkinter.Label(self.widgets['sframe'],text=str(v.jsonData['displayOrder']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['displayLabel'].grid(column=5,row=self.gridrow,sticky='EW')
				self.widgets['minLabel'] = Tkinter.Label(self.widgets['sframe'],text=str(v.jsonData['servoMin']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['minLabel'].grid(column=6,row=self.gridrow,sticky='EW')
				self.widgets['maxLabel'] = Tkinter.Label(self.widgets['sframe'],text=str(v.jsonData['servoMax']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['maxLabel'].grid(column=7,row=self.gridrow,sticky='EW')
				self.widgets['boneNameLabel'] = Tkinter.Label(self.widgets['sframe'],text=str(v.jsonData['boneName']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['boneNameLabel'].grid(column=8,row=self.gridrow,sticky='EW')
				self.widgets['boneArmatureLabel'] = Tkinter.Label(self.widgets['sframe'],text=str(v.jsonData['boneArmature']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['boneArmatureLabel'].grid(column=9,row=self.gridrow,sticky='EW')
				self.widgets['boneAxisLabel'] = Tkinter.Label(self.widgets['sframe'],text=str(v.jsonData['boneAxis']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['boneAxisLabel'].grid(column=10,row=self.gridrow,sticky='EW')
				self.widgets['partNoLabel'] = Tkinter.Label(self.widgets['sframe'],text=str(v.jsonData['partNo']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['partNoLabel'].grid(column=11,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['noServosLabel'] = Tkinter.Label(self.widgets['sframe'],text='There are currently no servos in this specification.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noServosLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
			self.gridrow += 1
		
		#motions
		self.widgets['motionsLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['motionsLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		if(not self.spec.jsonData['locked'] and self.current.jbIndex == self.spec.jbIndex):
			self.widgets['addmotion'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Motion", image=self.images['add'], command=self.OnAddMotionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['addmotion'].grid(column=2,row=self.gridrow)
		self.gridrow += 1
		self.widgets['mframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['mframe'].grid(column=0,row=self.gridrow,pady=15,columnspan=3, sticky='EW')
		if(any(self.spec.motions)):
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['mframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['fpsLabel'] = Tkinter.Label(self.widgets['mframe'],text='FPS', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['fpsLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['framesLabel'] = Tkinter.Label(self.widgets['mframe'],text='Frames', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['framesLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			rowcount = 1
			self.gridrow += 1
			for v in self.spec.motions.values():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['nameLabel'] = Tkinter.Label(self.widgets['mframe'],text=v.jsonData['name'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['fpsLabel'] = Tkinter.Label(self.widgets['mframe'],text=v.jsonData['fps'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['fpsLabel'].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['framesLabel'] = Tkinter.Label(self.widgets['mframe'],text=len(v.jsonData['keyframes']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['framesLabel'].grid(column=2,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['mframe'],text='There are currently no motions in this specification.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		#chains
		self.widgets['chainsLabel'] = Tkinter.Label(self.widgets['tframe'],text='Chains', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['chainsLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		if(not self.spec.jsonData['locked'] and self.current.jbIndex == self.spec.jbIndex):
			self.widgets['addchain'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Chain", image=self.images['add'], command=self.OnAddChainClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['addchain'].grid(column=2,row=self.gridrow)
		self.gridrow += 1
		self.widgets['cframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['cframe'].grid(column=0,row=self.gridrow,pady=15,columnspan=3, sticky='EW')
		if(any(self.spec.chains)):
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['cframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['motionsLabel'] = Tkinter.Label(self.widgets['cframe'],text='Motions', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['motionsLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			rowcount = 1
			self.gridrow += 1
			for v in self.spec.chains.values():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['nameLabel'] = Tkinter.Label(self.widgets['cframe'],text=v['name'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['motionsLabel'] = Tkinter.Label(self.widgets['cframe'],text=len(v['motions']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['motionsLabel'].grid(column=1,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['cframe'],text='There are currently no chains in this specification.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		#motors
		self.widgets['motorsLabel'] = Tkinter.Label(self.widgets['tframe'],text='DC Motors', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['motorsLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		if(not self.spec.jsonData['locked'] and self.current.jbIndex == self.spec.jbIndex):
			self.widgets['addmotor'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Motor", image=self.images['add'], command=self.OnAddDCMotorClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['addmotor'].grid(column=2,row=self.gridrow)
		
		self.gridrow += 1
		
		self.widgets['moframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['moframe'].grid(column=0,row=self.gridrow,pady=15,columnspan=3, sticky='EW')
		
		if(hasattr(self.spec, 'motors') and any(self.spec.motors)):
			self.widgets['cLabel'] = Tkinter.Label(self.widgets['moframe'],text='Controllers', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['cLabel'].grid(column=3,columnspan=2,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['moframe'],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['dtLabel'] = Tkinter.Label(self.widgets['moframe'],text='Drive Type', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['dtLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['pinsLabel'] = Tkinter.Label(self.widgets['moframe'],text='Pins', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['pinsLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['jsLabel'] = Tkinter.Label(self.widgets['moframe'],text='Joystick', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['jsLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['kbLabel'] = Tkinter.Label(self.widgets['moframe'],text='Keyboard', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['kbLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			rowcount = 1
			for k,v in self.spec.motors.items():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				
				self.widgets['name'+str(self.gridrow)] = Tkinter.Label(self.widgets['moframe'],text=v.jsonData['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['name'+str(self.gridrow)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['dt'+str(self.gridrow)] = Tkinter.Label(self.widgets['moframe'],text=v.jsonData['drive_type'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['dt'+str(self.gridrow)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['pins'+str(self.gridrow)] = Tkinter.Label(self.widgets['moframe'],text=len(v.pins), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['pins'+str(self.gridrow)].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['js'+str(self.gridrow)] = Tkinter.Label(self.widgets['moframe'],text=len(v.controllers['joystick']), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['js'+str(self.gridrow)].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['kb'+str(self.gridrow)] = Tkinter.Label(self.widgets['moframe'],text=len(v.controllers['keyboard']), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['kb'+str(self.gridrow)].grid(column=4,row=self.gridrow,sticky='EW')
				self.gridrow += 1
				
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['moframe'],text='There are currently no DC motors in this specification.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		#steppers
		self.widgets['stepperLabel'] = Tkinter.Label(self.widgets['tframe'],text='Stepper Motors', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['stepperLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		if(not self.spec.jsonData['locked'] and self.current.jbIndex == self.spec.jbIndex):
			self.widgets['addmotor'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Motor", image=self.images['add'], command=self.OnAddStepperMotorClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['addmotor'].grid(column=2,row=self.gridrow)
		
		self.gridrow += 1
		
		self.widgets['stepframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['stepframe'].grid(column=0,row=self.gridrow,pady=15,columnspan=3, sticky='EW')
		
		if(hasattr(self.spec, 'steppers') and any(self.spec.steppers)):
			self.widgets['cLabel'] = Tkinter.Label(self.widgets['stepframe'],text='Controllers', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['cLabel'].grid(column=3,columnspan=2,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['stepframe'],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['rpmLabel'] = Tkinter.Label(self.widgets['stepframe'],text='RPM', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['rpmLabel'].grid(column=1,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['pinsLabel'] = Tkinter.Label(self.widgets['stepframe'],text='Pins', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['pinsLabel'].grid(column=2,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['jsLabel'] = Tkinter.Label(self.widgets['stepframe'],text='Joystick', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['jsLabel'].grid(column=3,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['kbLabel'] = Tkinter.Label(self.widgets['stepframe'],text='Keyboard', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['kbLabel'].grid(column=4,row=self.gridrow,padx=10,sticky='EW')
			self.gridrow += 1
			rowcount = 1
			for k,v in self.spec.steppers.items():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				
				self.widgets['name'+str(self.gridrow)] = Tkinter.Label(self.widgets['stepframe'],text=v.jsonData['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['name'+str(self.gridrow)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['rpm'+str(self.gridrow)] = Tkinter.Label(self.widgets['stepframe'],text=v.jsonData['rpm'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['rpm'+str(self.gridrow)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['pins'+str(self.gridrow)] = Tkinter.Label(self.widgets['stepframe'],text=len(v.pins), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['pins'+str(self.gridrow)].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['js'+str(self.gridrow)] = Tkinter.Label(self.widgets['stepframe'],text=len(v.controllers['joystick']), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['js'+str(self.gridrow)].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['kb'+str(self.gridrow)] = Tkinter.Label(self.widgets['stepframe'],text=len(v.controllers['keyboard']), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['kb'+str(self.gridrow)].grid(column=4,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['stepframe'],text='There are currently no stepper motors in this specification.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		#keyboard
		self.widgets['keyboardLabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyboard', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['keyboardLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		if(not self.spec.jsonData['locked'] and self.current.jbIndex == self.spec.jbIndex):
			self.widgets['addmap'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Map", image=self.images['add'], command=self.OnAddMapClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['addmap'].grid(column=2,row=self.gridrow)
		self.gridrow += 1
		self.widgets['kframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['kframe'].grid(column=0,row=self.gridrow,pady=15,columnspan=3, sticky='EW')
		if(any(self.spec.jsonData['keyboard'])):
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['kframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['activeLabel'] = Tkinter.Label(self.widgets['kframe'],text='Active', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['activeLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['mappingsLabel'] = Tkinter.Label(self.widgets['kframe'],text='Mappings', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['mappingsLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			rowcount = 1
			self.gridrow += 1
			for v in self.spec.jsonData['keyboard'].values():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['nameData'] = Tkinter.Label(self.widgets['kframe'],text=v['name'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['nameData'].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['activeData'] = Tkinter.Label(self.widgets['kframe'],text='Yes' if v['active'] else 'No', bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['activeData'].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['mappingsData'] = Tkinter.Label(self.widgets['kframe'],text=len(v['mappings']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['mappingsData'].grid(column=2,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['kframe'],text='There are currently no key maps in this specification.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		#imu
		self.widgets['imuLabel'] = Tkinter.Label(self.widgets['tframe'],text='IMU Orientation', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['imuLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		if(any(self.spec.jsonData['imu'])):
			self.widgets['mapframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
			self.widgets['mapframe'].grid(column=0,row=self.gridrow, sticky='W')
			
			self.oimage = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'orientation','{}{}.gif'.format(self.spec.jsonData['imu']['facing'],self.spec.jsonData['imu']['offset'])))
			self.widgets['oimage'] = Tkinter.Label(self.widgets['mapframe'],text='Preview', image=self.oimage, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['oimage'].grid(column=0,row=0, padx=10, columnspan=4,sticky='EW')
			
			self.widgets['mapLabel'] = Tkinter.Label(self.widgets['mapframe'],text='The direction and offset of the IMU in relation to the robot:', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['mapLabel'].grid(column=0,row=1, padx=10, columnspan=4, sticky='W')
			
			self.widgets['facingLabel'] = Tkinter.Label(self.widgets['mapframe'],text='Facing', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['facingLabel'].grid(column=0,row=2, padx=10,sticky='EW')
			self.widgets['facingData'] = Tkinter.Label(self.widgets['mapframe'],text=self.spec.jsonData['imu']['facing'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
			self.widgets['facingData'].grid(column=1,row=2, padx=10,sticky='EW')
			
			self.widgets['offsetLabel'] = Tkinter.Label(self.widgets['mapframe'],text='Offset', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['offsetLabel'].grid(column=2,row=2, padx=10,sticky='EW')
			self.widgets['offsetData'] = Tkinter.Label(self.widgets['mapframe'],text=self.spec.jsonData['imu']['offset'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
			self.widgets['offsetData'].grid(column=3,row=2, padx=10,sticky='EW')

			self.gridrow += 1
			
			if('adjustments' in self.spec.jsonData['imu'].keys()):
				self.widgets['bframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
				self.widgets['bframe'].grid(column=0,row=self.gridrow, sticky='W')
				
				row = 0
				
				self.widgets['bLabel'] = Tkinter.Label(self.widgets['bframe'],text='Balance Rules:', bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['bLabel'].grid(column=0,row=row, padx=10,sticky='W')
				
				row += 1
			
				if(any(self.spec.jsonData['imu']['adjustments'])):
					self.widgets['axisLabel'] = Tkinter.Label(self.widgets['bframe'],text='Axis', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
					self.widgets['axisLabel'].grid(column=0,row=row,sticky='EW')
					self.widgets['directionLabel'] = Tkinter.Label(self.widgets['bframe'],text='Direction', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
					self.widgets['directionLabel'].grid(column=1,row=row,sticky='EW')
					self.widgets['instructionsLabel'] = Tkinter.Label(self.widgets['bframe'],text='Instructions', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
					self.widgets['instructionsLabel'].grid(column=2,row=row,sticky='EW')
					row += 1
					for a in self.spec.jsonData['imu']['adjustments']:
						rowcolour = self.colours['rowbg']
						if(row % 2 == 0):
							rowcolour = self.colours['rowaltbg']
						rowcount += 1
						self.widgets['axisData'] = Tkinter.Label(self.widgets['bframe'],text=a['axis'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
						self.widgets['axisData'].grid(column=0,row=row,sticky='EW')
						self.widgets['directionData'] = Tkinter.Label(self.widgets['bframe'],text=a['direction'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
						self.widgets['directionData'].grid(column=1,row=row,sticky='EW')
						self.widgets['instructionsData'] = Tkinter.Label(self.widgets['bframe'],text=len(a['instructions']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
						self.widgets['instructionsData'].grid(column=2,row=row,sticky='EW')
						row += 1
				else:
					self.widgets['noLabel'] = Tkinter.Label(self.widgets['bframe'],text='There are currently no balance adjustments in this specification.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
					self.widgets['noLabel'].grid(column=0,row=row, ipadx=20,sticky='EW')
		self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		self.widgets['lockLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Lock', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['lockLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		self.widgets['unlockLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Unlock', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['unlockLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnListSpecificationsClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['save'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveSpecificationClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['save'].grid(column=1,row=self.gridrow)
		if(self.spec.jsonData['locked']):
			self.widgets['save'].configure(state='disabled')
		self.widgets['lock'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Lock", image=self.images['stop'], command=self.OnLockSpecificationClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['lock'].grid(column=2,row=self.gridrow)
		self.widgets['unlock'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Unlock", image=self.images['play'], command=self.OnUnlockSpecificationClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['unlock'].grid(column=3,row=self.gridrow)
		
		if(self.spec.jsonData['locked']):
			self.widgets['lock'].configure(state='disabled')
			self.widgets['unlock'].configure(state='normal')
		else:
			self.widgets['lock'].configure(state='normal')
			self.widgets['unlock'].configure(state='disabled')
	def editCodename(self):
		""" view - edit codename
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Specifications / Edit Codename', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['infoframe'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		self.widgets['infoframe'].rowconfigure(3, weight=1)
		
		self.widgets['identLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Ident:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['identLabel'].grid(column=0,row=1,padx=20,sticky='NW')
		self.widgets['identData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jbIndex, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['identData'].grid(column=1,row=1,padx=10,columnspan=3, sticky='NW')
		self.gridrow += 1
		self.widgets['codenameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Codename:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['codenameLabel'].grid(column=0,row=self.gridrow,padx=20, pady=20, sticky='NW')
		self.variables['codename'] = Tkinter.StringVar()
		self.variables['codename'].set(self.spec.jsonData['codename'])
		self.widgets['codenameData'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['codename'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['codenameData'].grid(column=1,row=self.gridrow,padx=10, pady=20, sticky='NW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.viewSpecification, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['save'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveCodenameClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['save'].grid(column=1,row=self.gridrow)
	def newSpec(self):
		""" view - new specification
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Specifications / New Specification', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['infoframe'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		self.widgets['infoframe'].rowconfigure(3, weight=1)
		
		self.widgets['identLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Ident:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['identLabel'].grid(column=0,row=1,padx=20,sticky='NW')
		self.widgets['identData'] = Tkinter.Label(self.widgets['infoframe'],text='TBD', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['identData'].grid(column=1,row=1,padx=10,columnspan=3, sticky='NW')
		self.gridrow += 1
		self.widgets['codenameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Codename:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['codenameLabel'].grid(column=0,row=self.gridrow,padx=20, pady=20, sticky='NW')
		self.variables['codename'] = Tkinter.StringVar()
		self.widgets['codenameData'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['codename'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['codenameData'].grid(column=1,row=self.gridrow,padx=10, pady=20, sticky='NW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.viewSpecification, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['save'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveNewClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['save'].grid(column=1,row=self.gridrow)
	def changeThumb(self):
		""" view - change thumb
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Specifications / Change Thumbnail', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['infoframe'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		self.widgets['infoframe'].rowconfigure(3, weight=1)
		
		self.widgets['codenameLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Codename:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], height=3)
		self.widgets['codenameLabel'].grid(column=0,row=0,padx=20,sticky='NW')
		self.widgets['codenameData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jsonData['codename'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], font=self.fonts['heading2'], height=3)
		self.widgets['codenameData'].grid(column=1,row=0,padx=10,sticky='NW')
		
		self.widgets['identLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Ident:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['identLabel'].grid(column=0,row=1,padx=20,sticky='NW')
		self.widgets['identData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jbIndex, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['identData'].grid(column=1,row=1,padx=10,columnspan=3, sticky='NW')
		self.gridrow += 1
		self.widgets['fileLabel'] = Tkinter.Label(self.widgets['tframe'],text='File', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['fileLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.variables['file'] = Tkinter.StringVar()
		self.widgets['fileData'] = Tkinter.Label(self.widgets['tframe'],textvariable=self.variables['file'], bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['fileData'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['file'].set(self.spec.jsonData['thumbfile'])
		self.widgets['fileEdit'] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.OnPickThumbnailClick)
		self.widgets['fileEdit'].grid(column=2,row=self.gridrow,sticky='EW')

		self.gridrow += 1
		self.widgets['previewLabel'] = Tkinter.Label(self.widgets['tframe'],text='Preview', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['previewLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['previewData'] = Tkinter.Label(self.widgets['tframe'],text="TBD", bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['previewData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		if(self.spec.jsonData['thumbfile'] != ''):
			self.thumbimage = Tkinter.PhotoImage(file = os.path.join(self.spec.getInstallPath(), self.spec.jsonData['thumbfile']))
			self.widgets['previewData'].configure(image=self.thumbimage)
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.viewSpecification, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['saveimage'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveThumbnailClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['saveimage'].grid(column=1,row=self.gridrow)
	def changeBlend(self):
		""" view - change blend file
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Specifications / Change Blend File', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['infoframe'].grid(column=0,row=self.gridrow,columnspan=3, sticky='EW')
		self.widgets['infoframe'].rowconfigure(3, weight=1)
		
		self.widgets['codenameLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Codename:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], height=3)
		self.widgets['codenameLabel'].grid(column=0,row=0,padx=20,sticky='NW')
		self.widgets['codenameData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jsonData['codename'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], font=self.fonts['heading2'], height=3)
		self.widgets['codenameData'].grid(column=1,row=0,padx=10,sticky='NW')
		
		self.widgets['identLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Ident:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['identLabel'].grid(column=0,row=1,padx=20,sticky='NW')
		self.widgets['identData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jbIndex, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['identData'].grid(column=1,row=1,padx=10,columnspan=3, sticky='NW')
		self.gridrow += 1
		self.widgets['fileLabel'] = Tkinter.Label(self.widgets['tframe'],text='File', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['fileLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.variables['file'] = Tkinter.StringVar()
		self.widgets['fileData'] = Tkinter.Label(self.widgets['tframe'],textvariable=self.variables['file'], bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['fileData'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['file'].set(self.spec.jsonData['blendfile'])
		self.widgets['fileEdit'] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.OnPickBlendClick)
		self.widgets['fileEdit'].grid(column=2,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.viewSpecification, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['saveimage'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveBlendClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['saveimage'].grid(column=1,row=self.gridrow)
	def generatePackage(self):
		""" view - generate package
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Specifications / Generate Package', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['infoframe'].grid(column=0,row=self.gridrow,columnspan=3, sticky='EW')
		self.widgets['infoframe'].rowconfigure(3, weight=1)
		
		self.widgets['codenameLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Codename:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], height=3)
		self.widgets['codenameLabel'].grid(column=0,row=0,padx=20,sticky='NW')
		self.widgets['codenameData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jsonData['codename'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], font=self.fonts['heading2'], height=3)
		self.widgets['codenameData'].grid(column=1,row=0,padx=10,sticky='NW')
		
		self.widgets['identLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Ident:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['identLabel'].grid(column=0,row=1,padx=20,sticky='NW')
		self.widgets['identData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jbIndex, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['identData'].grid(column=1,row=1,padx=10,columnspan=3, sticky='NW')
		self.gridrow += 1
		self.widgets['infoData'] = Tkinter.Label(self.widgets['tframe'],text='Create a package from this specification which can be used to recreate it. This may take some time.', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['infoData'].grid(column=1,row=self.gridrow,padx=10, pady=5, columnspan=3, sticky='NW')
		self.gridrow += 1
		self.widgets['infoData2'] = Tkinter.Label(self.widgets['tframe'],text='A gzip file will be created which can be distributed to other Raspberry Pi\'s running AllMyServos', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['infoData2'].grid(column=1,row=self.gridrow,padx=10, pady=5, columnspan=3, sticky='NW')
		self.gridrow += 1
		self.widgets['infoData3'] = Tkinter.Label(self.widgets['tframe'],text='Once installed, the exact servo configuration, motions, chains, key maps and IMU mapping will be recreated.', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['infoData3'].grid(column=1,row=self.gridrow,padx=10, pady=5, columnspan=3, sticky='NW')
		self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['acceptLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['acceptLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.viewSpecification, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['accept'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Accept", image=self.images['accept'], command=self.OnPackageConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['accept'].grid(column=1,row=self.gridrow)
	def listPackages(self):
		""" view - list packages
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Specifications / Packages', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		if(any(self.packages)):
			self.widgets['localLabel'] = Tkinter.Label(self.widgets['tframe'],text='Local packages', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], height=3)
			self.widgets['localLabel'].grid(column=0,row=self.gridrow,padx=20,sticky='NW')
			self.gridrow += 1
			self.widgets['codenameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Codename', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['codenameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['identLabel'] = Tkinter.Label(self.widgets['tframe'],text='Ident', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['identLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['installLabel'] = Tkinter.Label(self.widgets['tframe'],text='Install', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['installLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			
			self.gridrow += 1
		
			rowcount = 1
			for k, v in self.packages.iteritems():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['codenameLabel'+v['ident']] = Tkinter.Label(self.widgets['tframe'],text=v['codename'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['codenameLabel'+v['ident']].grid(column=0,row=self.gridrow, ipadx=10, sticky='EW')
				self.widgets['identLabel'+v['ident']] = Tkinter.Label(self.widgets['tframe'],text=v['ident'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['identLabel'+v['ident']].grid(column=1,row=self.gridrow,ipadx=10, sticky='EW')
				self.widgets['installedLabel'+v['ident']] = Tkinter.Label(self.widgets['tframe'],text='Yes' if v['installed'] else 'No', bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['installedLabel'+v['ident']].grid(column=2,row=self.gridrow, ipadx=20, sticky='EW')
				self.widgets['install'+v['ident']] = Tkinter.Button(self.widgets['tframe'],text=u"Install", image=self.images['play'], command=lambda x = v['file']:self.OnInstallPackageClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
				self.widgets['install'+v['ident']].grid(column=2,row=self.gridrow)
				if(v['installed']):
					self.widgets['install'+v['ident']].configure(state='disabled')
				self.gridrow += 1
			
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['tframe'],text='There are currently no locally stored packages.', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['noLabel'].grid(column=1,row=self.gridrow,ipadx=10, sticky='EW')
			self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['importLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Import', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['importLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		self.widgets['import'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Import", image=self.images['process'], command=self.OnImportSpecificationClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['import'].grid(column=0,row=self.gridrow)
	def activateSpecification(self):
		""" view - activate specification
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Specifications / Activate', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		if(hasattr(self,'newspec')):
			self.widgets['infoframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
			self.widgets['infoframe'].grid(column=0,row=self.gridrow,columnspan=3, sticky='EW')
			self.widgets['infoframe'].rowconfigure(3, weight=1)
			
			self.widgets['codenameLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Codename:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], height=3)
			self.widgets['codenameLabel'].grid(column=0,row=0,padx=20,sticky='NW')
			self.widgets['codenameData'] = Tkinter.Label(self.widgets['infoframe'],text=self.newspec.jsonData['codename'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], font=self.fonts['heading2'], height=3)
			self.widgets['codenameData'].grid(column=1,row=0,padx=10,sticky='NW')
			
			self.widgets['identLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Ident:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['identLabel'].grid(column=0,row=1,padx=20,sticky='NW')
			self.widgets['identData'] = Tkinter.Label(self.widgets['infoframe'],text=self.newspec.jbIndex, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
			self.widgets['identData'].grid(column=1,row=1,padx=10,columnspan=3, sticky='NW')
			self.gridrow += 1
			self.widgets['infoData'] = Tkinter.Label(self.widgets['tframe'],text='Activating this specification will configure the application to use the servos, motions, chains, keyboard and IMU mapping from the specification.', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['infoData'].grid(column=1,row=self.gridrow,padx=10, pady=5, columnspan=3, sticky='NW')
			self.gridrow += 1
			self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
			self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
			
			self.gridrow = 0
			
			self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['acceptLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['acceptLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.listSpecifications, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['back'].grid(column=0,row=self.gridrow)
			self.widgets['accept'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Accept", image=self.images['accept'], command=self.OnActivateConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['accept'].grid(column=1,row=self.gridrow)
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['tframe'],text='No new specification selected.', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['noLabel'].grid(column=1,row=self.gridrow,ipadx=10, sticky='EW')
	def deleteSpecification(self):
		""" view - delete specification
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Specifications / Uninstall', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		if(hasattr(self,'spec')):
			self.widgets['infoframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
			self.widgets['infoframe'].grid(column=0,row=self.gridrow,columnspan=3, sticky='EW')
			self.widgets['infoframe'].rowconfigure(3, weight=1)
			
			self.widgets['codenameLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Codename:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], height=3)
			self.widgets['codenameLabel'].grid(column=0,row=0,padx=20,sticky='NW')
			self.widgets['codenameData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jsonData['codename'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], font=self.fonts['heading2'], height=3)
			self.widgets['codenameData'].grid(column=1,row=0,padx=10,sticky='NW')
			
			self.widgets['identLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Ident:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['identLabel'].grid(column=0,row=1,padx=20,sticky='NW')
			self.widgets['identData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jbIndex, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
			self.widgets['identData'].grid(column=1,row=1,padx=10,columnspan=3, sticky='NW')
			self.gridrow += 1
			self.widgets['infoData'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to uninstall this specification?', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['infoData'].grid(column=1,row=self.gridrow,padx=10, pady=5, columnspan=3, sticky='NW')
			self.gridrow += 1
			self.widgets['infoData2'] = Tkinter.Label(self.widgets['tframe'],text='All locally stored records and files will be removed.', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['infoData2'].grid(column=1,row=self.gridrow,padx=10, pady=5, columnspan=3, sticky='NW')
			self.gridrow += 1
			self.widgets['infoData3'] = Tkinter.Label(self.widgets['tframe'],text='Packaging a specification before removal allows it to be restored or recreated on another copy of AllMyServos.', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['infoData3'].grid(column=1,row=self.gridrow,padx=10, pady=5, columnspan=3, sticky='NW')
			
			self.gridrow += 1
			self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
			self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
			self.gridrow = 0
			
			self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['acceptLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['acceptLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnListSpecificationsClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['back'].grid(column=0,row=self.gridrow)
			self.widgets['accept'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Accept", image=self.images['accept'], command=self.OnDeleteConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['accept'].grid(column=1,row=self.gridrow)
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['tframe'],text='No specification selected.', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['noLabel'].grid(column=1,row=self.gridrow,ipadx=10, sticky='EW')
	def cloneSpecification(self):
		""" view - clone specification
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Specifications / Clone', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		if(hasattr(self,'spec')):
			self.widgets['infoframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
			self.widgets['infoframe'].grid(column=0,row=self.gridrow,columnspan=3, sticky='EW')
			self.widgets['infoframe'].rowconfigure(3, weight=1)
			
			self.widgets['originalLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Original Codename:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], height=3)
			self.widgets['originalLabel'].grid(column=0,row=0,padx=20,sticky='NW')
			self.widgets['codenameData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jsonData['codename'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], font=self.fonts['heading2'], height=3)
			self.widgets['codenameData'].grid(column=1,row=0,padx=10,sticky='NW')
			
			self.widgets['codenameLabel'] = Tkinter.Label(self.widgets['infoframe'],text='New Codename:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], height=3)
			self.widgets['codenameLabel'].grid(column=0,row=1,padx=20,sticky='NW')
			self.variables['codename'] = Tkinter.StringVar()
			self.variables['codename'].set(self.spec.jsonData['codename'])
			self.widgets['codenameEntry'] = Tkinter.Entry(self.widgets['infoframe'], textvariable=self.variables['codename'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
			self.widgets['codenameEntry'].grid(column=1,row=1,padx=10, pady=20, sticky='NW')
			
			self.widgets['identLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Ident:', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['identLabel'].grid(column=0,row=2,padx=20,sticky='NW')
			self.widgets['identData'] = Tkinter.Label(self.widgets['infoframe'],text=self.spec.jbIndex, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
			self.widgets['identData'].grid(column=1,row=2,padx=10,columnspan=3, sticky='NW')
			self.gridrow += 1
			self.widgets['infoData'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to clone this specification?', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['infoData'].grid(column=1,row=self.gridrow,padx=10, pady=5, columnspan=3, sticky='NW')
			self.gridrow += 1
			self.widgets['infoData2'] = Tkinter.Label(self.widgets['tframe'],text='A duplicate specification with a new Ident will be created.', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['infoData2'].grid(column=1,row=self.gridrow,padx=10, pady=5, columnspan=3, sticky='NW')
			
			self.gridrow += 1
			self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
			self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
			self.gridrow = 0
			
			self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['acceptLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['acceptLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.listSpecifications, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['back'].grid(column=0,row=self.gridrow)
			self.widgets['accept'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Accept", image=self.images['accept'], command=self.OnCloneConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['accept'].grid(column=1,row=self.gridrow)
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['tframe'],text='No specification selected.', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['noLabel'].grid(column=1,row=self.gridrow,ipadx=10, sticky='EW')
	
	#=== ACTIONS ===#
	def OnListSpecificationsClick(self):
		""" action - display spec list page
		"""
		self.specs = Specification.all('Specification', 'Specification')
		self.listSpecifications()
	def OnCurrentSpecificationClick(self):
		""" action - display current spec page
		"""
		self.spec = self.current
		self.viewSpecification()
	def OnViewSpecificationClick(self, ident):
		""" action - display spec page
		
		@param ident
		"""
		self.spec = Specification(ident)
		self.viewSpecification()
	def OnCloneSpecificationClick(self, ident):
		""" action - display clone spec page
		
		@param ident
		"""
		self.spec = Specification(ident)
		self.cloneSpecification()
	def OnCloneConfirmClick(self):
		""" action - clone spec
		"""
		newcodename = self.variables['codename'].get()
		if(len(newcodename) >= 2): #use the new codename
			Specification.clone(self.spec.jbIndex, newcodename)
		else: #use original codename
			Specification.clone(self.spec.jbIndex)
		self.OnListSpecificationsClick()
		self.notifier.addNotice('Specification cloned.')
	def OnDeleteSpecificationClick(self, ident):
		""" action - display delete spec page
		
		@param ident
		"""
		self.spec = Specification(ident)
		self.deleteSpecification()
	def OnDeleteConfirmClick(self):
		""" action - delete spec
		"""
		self.spec.delete()
		del(self.spec)
		self.OnListSpecificationsClick()
		self.notifier.addNotice('Specification deleted.')
	def OnNewClick(self):
		""" action - display new spec page
		"""
		self.newSpec()
	def OnActivateClick(self, ident):
		""" action - display activate page
		
		@param ident
		"""
		self.newspec = Specification(ident)
		self.activateSpecification()
	def OnActivateConfirmClick(self):
		""" action - activate specification
		"""
		self.gui.specification.change(self.newspec.jbIndex)
		self.gui.widgets['left']['TkServoGrid'].OnShowGridClick()
		self.OnListSpecificationsClick()
		self.notifier.addNotice('Specification "{}" activated'.format(self.gui.specification.jsonData['codename']))
	def OnSaveSpecificationClick(self):
		""" action - save specification
		"""
		self.spec.save()
		self.notifier.addNotice('Specification saved')
	def OnSaveNewClick(self):
		""" action - save new specification
		"""
		name = self.variables['codename'].get()
		if(len(name) >= 4):
			self.spec = Specification(Specification.newIdent())
			self.spec.jsonData['codename'] = name
			self.spec.save()
			self.viewSpecification()
			self.notifier.addNotice('New specification created')
		else:
			self.notifier.addNotice('Codenames should be 4 characters or more.', 'warning')
	def OnLockSpecificationClick(self):
		""" action - lock specification
		"""
		self.widgets['lock'].configure(state='disabled')
		self.widgets['unlock'].configure(state='normal')
		self.spec.jsonData['locked'] = True
		self.spec.save()
		self.notifier.addNotice('Specification locked.')
		self.viewSpecification()
	def OnUnlockSpecificationClick(self):
		""" action - unlock specification
		"""
		self.widgets['lock'].configure(state='normal')
		self.widgets['unlock'].configure(state='disabled')
		self.spec.jsonData['locked'] = False
		self.spec.save()
		self.notifier.addNotice('Specification unlocked.')
		self.viewSpecification()
	def OnAddServoClick(self):
		""" action - display add servo page
		"""
		self.gui.widgets['main']['TkServoManager'].OnAddServoClick()
	def OnAddMotionClick(self):
		""" action - display add motion page
		"""
		self.gui.widgets['main']['TkMotionManager'].OnAddMotionClick()
	def OnAddChainClick(self):
		""" action - display add chain page
		"""
		self.gui.widgets['main']['TkMotionManager'].OnAddChainClick()
	def OnAddDCMotorClick(self):
		""" action - display add dc motor page
		"""
		self.gui.widgets['main']['TkMotorManager'].OnAddDCMotorClick()
	def OnAddStepperMotorClick(self):
		""" action - display add stepper page
		"""
		self.gui.widgets['main']['TkMotorManager'].OnAddStepperMotorClick()
	def OnAddMapClick(self):
		""" action - display add key map page
		"""
		self.gui.widgets['main']['TkKeyboardManager'].OnAddKeyMapClick()
		self.keymaps = KeyMap()
		self.keymaps = self.keymaps.query(keyindex=True)
		names = []
		for v in self.spec.meta['keyboard']:
			names.append(v['name'])
		self.keymaps = { k: v for k, v in self.keymaps.iteritems() if not v.name in names }
		self.addKeyMaps()
	
	def OnChangeBlendClick(self):
		""" action - display change blend page
		"""
		self.changeBlend()
	def OnPickBlendClick(self):
		""" action - change blend file
		"""
		filename = askopenfilename()
		if(len(filename) > 0):
			parts = os.path.splitext(filename)
			if('.blend' == parts[-1]):
				if(self.spec.getInstallPath() in filename):
					filename = filename.replace(self.spec.getInstallPath()+'/', '')
				else:
					filename = self.__copyBlend(filename)
				self.variables['file'].set(filename)
				self.spec.jsonData['blendfile'] = filename
				self.notifier.addNotice('Blend file updated. Save to apply.', 'warning')
			else:
				self.notifier.addNotice('Ensure the file is in .blend format', 'error')
		else:
			self.notifier.addNotice('Change cancelled', 'warning')
	def OnSaveBlendClick(self):
		""" action - save blend file
		"""
		self.spec.save()
		self.notifier.addNotice('Blend file saved')
		self.viewSpecification()
	def OnViewBlendClick(self):
		""" action - open file manager on blend directory
		"""
		result = False
		if(len(self.spec.jsonData['blendfile']) > 0):
			extras = os.path.dirname(self.spec.jsonData['blendfile'])
			dir = '{}/{}'.format(self.spec.getInstallPath(), extras)
			result = self.__openFileManager(dir)
		if(result):
			self.notifier.addNotice('Now showing: Blend file in file manager')
		else:
			self.notifier.addNotice('There was a problem opening the blend file location.', 'warning')
	
	def OnChangeThumbClick(self):
		""" action - display change thumb page
		"""
		self.changeThumb()
	def OnPickThumbnailClick(self):
		""" action - choose thumbnail
		"""
		filename = askopenfilename()
		if(len(filename) > 0):
			parts = os.path.splitext(filename)
			if('.gif' == parts[-1]):
				if(self.spec.getInstallPath() in filename):
					filename = filename.replace(self.spec.getInstallPath()+'/', '')
				else:
					filename = self.__copyThumb(filename)
				self.variables['file'].set(filename)
				self.spec.jsonData['thumbfile'] = filename
				self.thumbimage = Tkinter.PhotoImage(file = '{0}/{1}'.format(self.spec.getInstallPath(), self.spec.jsonData['thumbfile']))
				self.widgets['previewData'].configure(image=self.thumbimage)
				self.notifier.addNotice('Thumbnail preview updated. Save to apply', 'warning')
			else:
				self.notifier.addNotice('Thumbnail must be in gif format', 'error')
		else:
			self.notifier.addNotice('Change cancelled', 'warning')
	def OnSaveThumbnailClick(self):
		""" action - save thumbnail
		"""
		self.spec.save()
		self.notifier.addNotice('Thumbnail saved')
		self.viewSpecification()
	
	def OnChangeCodenameClick(self):
		""" action - display change codename page
		"""
		self.editCodename()
	def OnSaveCodenameClick(self):
		""" action - save codename
		"""
		newname = self.variables['codename'].get()
		if(newname != ''):
			self.spec.jsonData['codename'] = newname
			self.spec.save()
			self.notifier.addNotice('Codename saved')
			self.viewSpecification()
		else:
			self.notifier.addNotice('Please provide a codename', 'error')
	
	def OnPackageClick(self):
		""" action - display package generate page
		"""
		self.generatePackage()
	def OnPackageConfirmClick(self):
		""" action - generate package
		"""
		self.spec.generatePackage()
		self.notifier.addNotice('Package created')
		self.viewSpecification()
	def OnViewPackageClick(self):
		""" action - display package page
		"""
		result = False
		if(self.spec.packaged > 0):
			result = self.__openFileManager(self.spec.packagepath)
		if(result):
			self.notifier.addNotice('Now showing: Specification package in file manager')
		else:
			self.notifier.addNotice('There was a problem opening the package location.', 'warning')
	def OnInstallSpecificationClick(self):
		""" action - display package list page
		"""
		self.packages = Specification.listPackages()
		self.listPackages()
	def OnImportSpecificationClick(self):
		""" action - import package
		"""
		filename = askopenfilename()
		if(len(filename) > 0):
			parts = os.path.splitext(filename)
			if(filename.endswith('.tar.gz')):
				if(not os.path.split(filename)[1] in self.packages.keys()):
					self.__copyPackage(filename)
					self.notifier.addNotice('Package copied successfully')
					self.packages = Specification.listPackages()
					self.listPackages()
				else:
					self.notifier.addNotice('Package already listed', 'warning')
			else:
				self.notifier.addNotice('Ensure the package is in .tar.gz format', 'error')
		else:
			self.notifier.addNotice('Import cancelled', 'warning')
	def OnInstallPackageClick(self, filename):
		""" action - install package
		
		@param filename
		"""
		res = Specification.deployPackage(filename)
		if(res == 'unpacked'):
			self.widgets['install'+filename.replace('.tar.gz', '')].configure(state='disabled')
			self.notifier.addNotice('Package installed successfully')
		elif(res == 'exists'):
			self.notifier.addNotice('Package already exists', 'warning')
		else:
			self.notifier.addNotice('Package extraction failed', 'error')
	
	#=== UTILS ===#
	def __copyThumb(self, filepath):
		""" util - copy thumbnail into install path
		
		@param filepath
		
		@return str
		"""
		installpath = self.spec.getInstallPath()
		parts = filepath.split('/')
		filename = parts[-1]
		if not os.path.exists(installpath):
			os.makedirs(installpath)
		shutil.copyfile(filepath, os.path.join(installpath, filename))
		return filename
	def __copyBlend(self, filepath):
		""" util - copy blend file into install path
		
		@param filepath
		
		@return str
		"""
		installpath = self.spec.getInstallPath()
		parts = filepath.split('/')
		filename = parts[-1]
		if not os.path.exists(installpath):
			os.makedirs(installpath)
		shutil.copyfile(filepath, os.path.join(installpath, filename))
		return filename
	def __copyPackage(self, filename):
		""" util - copy package into package path
		
		@param filename
		
		@return str
		"""
		parts = filename.split('/')
		file = parts[-1]
		newfile = os.path.join(Specification.packagepath, file)
		if not os.path.exists(Specification.packagepath):
			os.makedirs(Specification.packagepath)
		shutil.copyfile(filename, newfile)
		return newfile
	def __openFileManager(self, dir=''):
		""" util - open file manager to given directory
		
		@param dir
		
		@return bool
		"""
		try:
			if(len(dir) > 0):
				command = ['pcmanfm', dir]
				p = Popen(command, stdout=PIPE)
				o = p.communicate()[0]
				if(p.returncode == 0):
					return True
		except:
			pass
		return False