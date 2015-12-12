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
import Tkinter, ttk, sys, os, copy
from Tkinter import *
from tkFileDialog import askopenfilename
from TkBlock import *
from DB import *
from Motion import *
from xml.dom import minidom
from xml.dom.minidom import Document
from StringIO import StringIO

class TkMotionManager(TkPage):
	def __init__(self, parent, gui, **options):
		super(TkMotionManager,self).__init__(parent, gui, **options)
		self.specification = gui.specification
		self.servos = self.gui.specification.servos
		self.channelindex = sorted(self.servos.values(), key=lambda x: x.jsonData['channel'])
		self.refreshMotions()
	def setup(self):
		self.gui.menus['motion'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		self.gui.menus['motion'].add_command(label="New", command=self.OnAddMotionClick)
		self.gui.menus['motion'].add_separator()
		self.gui.menus['motion'].add_command(label="List Motions", command=self.OnListMotionsClick)
		self.gui.menus['motion'].add_command(label="List Chains", command=self.OnListChainsClick)
		self.addMenu(label="Motion", menu=self.gui.menus['motion'])
	
	#=== VIEWS ===#
	##== Services ==##
	def serviceManager(self):
		self.widgets['servicelabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Scheduler Service', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['servicelabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['statusLabel'] = Tkinter.Label(self.widgets['tframe'],text='Status', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['statusLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.variables['status'] = Tkinter.StringVar()
		self.widgets['statusdata'] = Tkinter.Label(self.widgets['tframe'],textvariable=self.variables['status'], bg=self.colours['bg'], fg=self.colours['fg'], font=self.fonts['heading2'])
		self.widgets['statusdata'].grid(column=0,row=self.gridrow,sticky='EW')
		
		if(self.gui.scheduler.tasks['motion_scheduler'].stopped == False):
			self.variables['status'].set('Running')
		else:
			self.variables['status'].set('Stopped')
		
		self.widgets['start'] = Tkinter.Button(self.widgets['tframe'],text=u"Start", image=self.images['play'], command=self.OnStartClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['start'].grid(column=1,row=self.gridrow)
		
		self.widgets['stop'] = Tkinter.Button(self.widgets['tframe'],text=u"Stop", image=self.images['stop'], command=self.OnStopClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['stop'].grid(column=2,row=self.gridrow)
		
		if(self.gui.scheduler.tasks['motion_scheduler'].stopped == False):
			self.widgets['start'].configure(state='disabled')
		else:
			self.widgets['stop'].configure(state='disabled')
		
		self.variables['autostart'] = Tkinter.BooleanVar()
		self.variables['autostart'].set(Setting.get('motion_scheduler_autostart', True))
		self.widgets['autostartentry'] = Tkinter.Checkbutton(self.widgets['tframe'], text="Autostart", variable=self.variables['autostart'], command=self.OnToggleAutostartClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['autostartentry'].grid(column=3,row=self.gridrow)
	
	##== Motions ==##
	def listMotions(self):
		self.open()
		
		self.serviceManager()
		
		self.gridrow += 1
		
		self.widgets['molabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / List Motions', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['molabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		self.widgets['reindex'] = Tkinter.Button(self.widgets['tframe'],text=u"Reindex", image=self.images['reset'], command=self.OnRefreshClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['reindex'].grid(column=4,row=self.gridrow)
		self.widgets['addmotion'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Motion", image=self.images['add'], command=self.OnAddMotionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addmotion'].grid(column=5,row=self.gridrow)
		self.gridrow += 1
		if(any(self.motions)):
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['fpsLabel'] = Tkinter.Label(self.widgets['tframe'],text='FPS', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['fpsLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['framesLabel'] = Tkinter.Label(self.widgets['tframe'],text='Frames', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['framesLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['tframe'],text='Edit', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['editLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['playLabel'] = Tkinter.Label(self.widgets['tframe'],text='Play', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['playLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.widgets['slomoLabel'] = Tkinter.Label(self.widgets['tframe'],text='Slow', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['slomoLabel'].grid(column=5,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			rowcount = 1
			for mo in self.motions.values():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				
				self.widgets['name'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=mo.jsonData['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['name'+str(self.gridrow)].grid(column=0,row=self.gridrow,sticky='EW')
				
				self.widgets['fps'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=mo.jsonData['fps'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['fps'+str(self.gridrow)].grid(column=1,row=self.gridrow,sticky='EW')
				
				self.widgets['frames'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=len(mo.jsonData['keyframes']), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['frames'+str(self.gridrow)].grid(column=2,row=self.gridrow,sticky='EW')
				
				self.widgets['edit'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = mo.jbIndex:self.OnEditMotionClick(x))
				self.widgets['edit'+str(self.gridrow)].grid(column=3,row=self.gridrow,sticky='EW')
				
				self.widgets['play'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Play", image=self.images['play'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = mo.jbIndex:self.OnPlayMotionClick(x))
				self.widgets['play'+str(self.gridrow)].grid(column=4,row=self.gridrow,sticky='EW')
				
				self.widgets['slomo'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Slow", image=self.images['slow'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = mo.jbIndex:self.OnPlaySlowMotionClick(x))
				self.widgets['slomo'+str(self.gridrow)].grid(column=5,row=self.gridrow,sticky='EW')
				
				self.gridrow += 1
		else:
			self.widgets['nomotionslabel'] = Tkinter.Label(self.widgets['tframe'],text="There are currently no motions", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nomotionslabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['relaxLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Relax', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['relaxLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['defaultLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Default', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['defaultLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['relax'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Relax", image=self.images['stop'], command=self.OnRelaxClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['relax'].grid(column=0,row=self.gridrow)
		self.widgets['default'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Default", image=self.images['ram'], command=self.OnDefaultClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['default'].grid(column=1,row=self.gridrow)
	def editMotion(self):
		self.open()
		self.gridrow = 0
		self.variables = {}
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Motion / Edit', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['name'] = Tkinter.StringVar()
		self.widgets['nameentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['name'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['nameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if self.motion.blobExists():
			self.variables['name'].set(self.motion.jsonData['name'])
		
		self.gridrow += 1
		
		self.widgets['fpsLabel'] = Tkinter.Label(self.widgets['tframe'],text='FPS', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['fpsLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['fps'] = Tkinter.IntVar()	
		self.widgets['fpsentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['fps'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['fpsentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if self.motion.blobExists():
			self.variables['fps'].set(self.motion.jsonData['fps'])
		else:
			self.variables['fps'].set(1)
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')

		if self.motion.blobExists():
			self.widgets['keyframeLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Key Frames', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['keyframeLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['deleteLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Motion", image=self.images['back'], command=self.listMotions, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['savemotion'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Motion", image=self.images['save'], command=self.OnSaveMotionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['savemotion'].grid(column=1,row=self.gridrow)
		if self.motion.blobExists():
			self.widgets['keyframes'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Key Frames", image=self.images['key'], command=self.OnEditKeyFramesClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['keyframes'].grid(column=2,row=self.gridrow)
			self.widgets['deletemotion'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete Motion", image=self.images['delete'], command=self.OnDeleteMotionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['deletemotion'].grid(column=3,row=self.gridrow)
	def deleteMotion(self):
		self.open()
		self.gridrow = 0
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Motion / Delete', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['confirmlabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this motion?', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['confirmlabel'].grid(column=0,row=self.gridrow, columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['namelabel'] = Tkinter.Label(self.widgets['tframe'],text="Name", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['namelabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['namedata'] = Tkinter.Label(self.widgets['tframe'],text=self.motion.jsonData['name'], bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['namedata'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['fpslabel'] = Tkinter.Label(self.widgets['tframe'],text="FPS", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['fpslabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['fpsdata'] = Tkinter.Label(self.widgets['tframe'],text=self.motion.jsonData['fps'], bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['fpsdata'].grid(column=1,row=self.gridrow,sticky='EW')
		
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
		self.widgets['confirmbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['accept'], command=self.OnDeleteMotionConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['confirmbutton'].grid(column=1,row=self.gridrow)
	def editKeyFrames(self):
		self.open()
		self.gridrow = 0
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Motion / Edit Keyframes', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		try:
			self.duration
		except:
			self.duration = 1000
			if(len(self.keyframes) > 0):
				self.duration = int(self.keyframes[sorted(self.keyframes)[-1]]['time'])
				if(self.duration < 1000):
					self.duration = 1000
		self.gridrow += 1
		self.widgets['timeLabel'] = Tkinter.Label(self.widgets['tframe'],text='Time', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['timeLabel'].grid(column=0,row=self.gridrow,sticky='EW', padx=10)
		try:
			self.time
		except:
			self.time = Tkinter.IntVar()
		if(not(hasattr(self, 'lastmotion')) or self.lastmotion != self.motion.jbIndex):
			self.time.set(0)
			self.lastmotion = self.motion.jbIndex
		self.widgets['timeline'] = Tkinter.Scale(self.widgets['tframe'], from_=0, to=self.duration, variable=self.time, command=self.activeKeyFrame, resolution=1000/int(self.motion.jsonData['fps']), orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['inputbg'], fg=self.colours['fg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
		self.widgets['timeline'].grid(column=1,row=self.gridrow)
		self.widgets['addbutton'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Second", command=self.OnAddTimeClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addbutton'].grid(column=2,row=self.gridrow)
		self.widgets['trimbutton'] = Tkinter.Button(self.widgets['tframe'],text=u"Trim Time", command=self.OnTrimTimeClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['trimbutton'].grid(column=3,row=self.gridrow)
		self.gridrow += 1
		self.widgets['framestatuslabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyframe Status', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], height=2)
		self.widgets['framestatuslabel'].grid(column=0,row=self.gridrow,padx=10,sticky='EW')
		self.widgets['framestatusdata'] = Tkinter.Label(self.widgets['tframe'],text='Unsaved', bg=self.colours['bg'], fg=self.colours['valuefg'], font=self.fonts['heading2'], height=2)
		self.widgets['framestatusdata'].grid(column=1,row=self.gridrow,padx=10,sticky='W')
		self.gridrow += 1
		self.widgets['servonameheading'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['servonameheading'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['servochannelheading'] = Tkinter.Label(self.widgets['tframe'],text='Channel', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['servochannelheading'].grid(column=1,row=self.gridrow,sticky='EW')
		self.widgets['servoangleheading'] = Tkinter.Label(self.widgets['tframe'],text='Angle', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['servoangleheading'].grid(column=2,row=self.gridrow,sticky='EW')
		self.widgets['servodisabledheading'] = Tkinter.Label(self.widgets['tframe'],text='Disabled', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['servodisabledheading'].grid(column=3,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		rowcount = 1
		for s in self.channelindex:
			rowcolour = self.colours['rowbg']
			if(rowcount % 2 == 0):
				rowcolour = self.colours['rowaltbg']
			rowcount += 1
			self.widgets['servoname'+s.jbIndex] = Tkinter.Label(self.widgets['tframe'],text=s.jsonData['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
			self.widgets['servoname'+s.jbIndex].grid(column=0,row=self.gridrow,sticky='EW')
			
			self.widgets['servochannel'+s.jbIndex] = Tkinter.Label(self.widgets['tframe'],text=s.jsonData['channel'], bg=rowcolour, fg=self.colours['fg'], height=2)
			self.widgets['servochannel'+s.jbIndex].grid(column=1,row=self.gridrow,sticky='EW')
			
			self.variables['servoangle'+s.jbIndex] = Tkinter.IntVar()
			self.widgets['angleentry'+s.jbIndex] = Tkinter.Scale(self.widgets['tframe'], from_=0, to=180, variable=self.variables['servoangle'+s.jbIndex], command=self.OnUpdateAngles, resolution=1, orient=Tkinter.HORIZONTAL, length = 180, bg=rowcolour, fg=self.colours['fg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
			self.widgets['angleentry'+s.jbIndex].grid(column=2,row=self.gridrow)
			self.variables['servoangle'+s.jbIndex].set(int(s.jsonData['angle']))
			
			self.variables['servodisabled'+s.jbIndex] = Tkinter.BooleanVar()
			self.widgets['disabledentry'+s.jbIndex] = Tkinter.Checkbutton(self.widgets['tframe'], text="Disabled", variable=self.variables['servodisabled'+s.jbIndex], bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
			self.widgets['disabledentry'+s.jbIndex].grid(column=3,row=self.gridrow)
			self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['updatelabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Update", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['updatelabel'].grid(column=1,row=self.gridrow,sticky='EW')
		self.widgets['movelabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Move", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['movelabel'].grid(column=2,row=self.gridrow,sticky='EW')
		self.widgets['clonelabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Clone", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['clonelabel'].grid(column=3,row=self.gridrow,sticky='EW')
		self.widgets['deletelabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Delete", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['deletelabel'].grid(column=4,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.listMotions, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['updatekeyframebutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Update", image=self.images['save'], command=self.OnUpdateKeyFrameClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['updatekeyframebutton'].grid(column=1,row=self.gridrow)
		self.widgets['movekeyframebutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Move", image=self.images['play'], command=self.OnMoveKeyFrameClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['movekeyframebutton'].grid(column=2,row=self.gridrow)
		self.widgets['clonekeyframebutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Clone", image=self.images['process'], command=self.OnCloneKeyFrameClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['clonekeyframebutton'].grid(column=3,row=self.gridrow)
		self.widgets['deletekeyframebutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['delete'], command=self.OnDeleteKeyFrameClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['deletekeyframebutton'].grid(column=4,row=self.gridrow)
	def getActiveKeyframe(self, time):
		for kf in self.keyframes:
			if(self.keyframes[kf]['time'] == time):
				return self.keyframes[kf]
		return None
	def activeKeyFrame(self, time):
		kf = self.getActiveKeyframe(self.time.get())
		if(kf != None):
			self.widgets['framestatusdata'].configure(text="Saved")
			self.widgets['movekeyframebutton'].configure(state='normal')
			self.widgets['clonekeyframebutton'].configure(state='normal')
			self.widgets['deletekeyframebutton'].configure(state='normal')
			instructions = kf['instructions']
			for s in self.channelindex:
				ins = [v for v in instructions if v['channel'] == s.channel]
				if(any(ins)):
					self.variables['servoangle'+s.jbIndex].set(int(ins[0]['angle']))
					self.variables['servodisabled'+s.jbIndex].set(bool(ins[0]['disabled']))
					s.angle = ins[0]['angle']
					s.disabled = ins[0]['disabled']
					s.setServoAngle()
		else:
			self.widgets['framestatusdata'].configure(text="Unsaved")
			self.widgets['movekeyframebutton'].configure(state='disabled')
			self.widgets['clonekeyframebutton'].configure(state='disabled')
			self.widgets['deletekeyframebutton'].configure(state='disabled')
	def moveKeyFrame(self):
		self.open()
		self.gridrow = 0
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Motion / Edit Keyframes / Move', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['currentlabel'] = Tkinter.Label(self.widgets['tframe'],text='Key frame at time: '+str(self.time.get()), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['currentlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['moveLabel'] = Tkinter.Label(self.widgets['tframe'],text='Move this frame to: ', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['moveLabel'].grid(column=0,row=self.gridrow,sticky='EW', padx=10)
		
		self.variables['newtime'] = Tkinter.IntVar()
		self.widgets['timeentry'] = Tkinter.Scale(self.widgets['tframe'], from_=0, to=self.duration, variable=self.variables['newtime'], resolution=1000/int(self.motion.jsonData['fps']), orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['inputbg'], fg=self.colours['fg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
		self.widgets['timeentry'].grid(column=1,row=self.gridrow)
		self.variables['newtime'].set(self.time.get())
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['movelabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Move", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['movelabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnCancelKeyFrameClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['move'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Move", image=self.images['process'], command=self.OnMoveKeyFrameConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['move'].grid(column=1,row=self.gridrow)
	def cloneKeyFrame(self):
		self.open()
		self.gridrow = 0
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Motion / Edit Keyframes / Clone', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['currentlabel'] = Tkinter.Label(self.widgets['tframe'],text='Key frame at time: '+str(self.time.get()), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['currentlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['cloneLabel'] = Tkinter.Label(self.widgets['tframe'],text='Clone this frame to: ', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['cloneLabel'].grid(column=0,row=self.gridrow,sticky='EW', padx=10)
		
		self.variables['newtime'] = Tkinter.IntVar()
		self.widgets['timeentry'] = Tkinter.Scale(self.widgets['tframe'], from_=0, to=self.duration, variable=self.variables['newtime'], resolution=1000/int(self.motion.jsonData['fps']), orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['inputbg'], fg=self.colours['fg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
		self.widgets['timeentry'].grid(column=1,row=self.gridrow)
		self.variables['newtime'].set(self.time.get())
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['clonelabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Clone", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['clonelabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnCancelKeyFrameClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['clone'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Clone", image=self.images['process'], command=self.OnCloneKeyFrameConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['clone'].grid(column=1,row=self.gridrow)
	def deleteKeyFrame(self):
		self.open()
		self.gridrow = 0
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Motion / Edit Keyframes / Delete', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['currentlabel'] = Tkinter.Label(self.widgets['tframe'],text='Key frame at time: '+str(self.time.get()), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['currentlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this keyframe?', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['deleteLabel'].grid(column=0,row=self.gridrow,sticky='EW', padx=10)
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['deletelabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Delete", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['deletelabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnCancelKeyFrameClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['delete'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['delete'], command=self.OnDeleteKeyFrameConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['delete'].grid(column=1,row=self.gridrow)
	
	##== Chains ==##
	def listChains(self):
		self.open()
		
		self.serviceManager()
		
		self.gridrow += 1

		self.widgets['clabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / List Chains', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['clabel'].grid(column=0,row=self.gridrow, columnspan=4, sticky='EW')
		self.widgets['addchain'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Chain", image=self.images['add'], command=self.OnAddChainClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addchain'].grid(column=5,row=self.gridrow)
		self.gridrow += 1
		if(len(self.chains) > 0):
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['tframe'],text='Edit', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['editLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['motionsLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['motionsLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['playLabel'] = Tkinter.Label(self.widgets['tframe'],text='Play', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['playLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['tframe'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['deleteLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			rowcount = 1
			for k, v in self.chains.items():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['name'+k] = Tkinter.Label(self.widgets['tframe'],text=v['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['name'+k].grid(column=0,row=self.gridrow,sticky='EW')
				
				self.widgets['edit'+k] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnEditChainClick(x))
				self.widgets['edit'+k].grid(column=1,row=self.gridrow,sticky='EW')
				
				self.widgets['motions'+k] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['add'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnListChainMotionsClick(x))
				self.widgets['motions'+k].grid(column=2,row=self.gridrow,sticky='EW')
				
				self.widgets['play'+k] = Tkinter.Button(self.widgets['tframe'],text=u"Play", image=self.images['play'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnPlayChainClick(x))
				self.widgets['play'+k].grid(column=3,row=self.gridrow,sticky='EW')
				
				self.widgets['delete'+k] = Tkinter.Button(self.widgets['tframe'],text=u"Delete", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnDeleteChainClick(x))
				self.widgets['delete'+k].grid(column=4,row=self.gridrow,sticky='EW')
				
				self.gridrow += 1
		else:
			self.widgets['nochainslabel'] = Tkinter.Label(self.widgets['tframe'],text="There are currently no chains", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nochainslabel'].grid(column=0,row=self.gridrow,sticky='EW')
	def editChain(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Chain / Edit', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['name'] = Tkinter.StringVar()
		self.widgets['nameentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['name'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['nameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if (len(self.chain['name']) > 0):
			self.variables['name'].set(self.chain['name'])
		self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		if (self.chain['name'] != ''):
			self.widgets['motionsLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Motions', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['motionsLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['deleteLabel'].grid(column=3,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.listChains, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['savechain'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Chain", image=self.images['save'], command=self.OnSaveChainClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['savechain'].grid(column=1,row=self.gridrow)
		if (self.chain['name'] != ''):
			self.widgets['chainmotions'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Chain Motions", image=self.images['add'], command=self.OnListChainMotionsClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['chainmotions'].grid(column=2,row=self.gridrow)
			self.widgets['deletechain'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete Chain", image=self.images['delete'], command=self.OnDeleteChainClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['deletechain'].grid(column=3,row=self.gridrow)
	def deleteChain(self):
		self.open()
		self.gridrow = 0
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Chain / Delete', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		self.widgets['confirmlabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this chain?', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['confirmlabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['namelabel'] = Tkinter.Label(self.widgets['tframe'],text="Name", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['namelabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['namedata'] = Tkinter.Label(self.widgets['tframe'],text=self.chain['name'], bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['namedata'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['acceptlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Accept", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['acceptlabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['cancelbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Cancel", image=self.images['back'], command=self.OnCancelDeleteChainClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['cancelbutton'].grid(column=0,row=self.gridrow)
		self.widgets['confirmbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['accept'], command=self.OnDeleteChainConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['confirmbutton'].grid(column=1,row=self.gridrow)
	def listChainMotions(self):
		self.open()
		self.widgets['clabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Chain / Chain Motions', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['clabel'].grid(column=0,row=self.gridrow, columnspan=4, sticky='EW')
		self.widgets['addchainmotion'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Chain Motion", image=self.images['add'], command=self.OnAddChainMotionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addchainmotion'].grid(column=5,row=self.gridrow)
		self.gridrow += 1
		if(any(self.chain['motions'])):
			self.widgets['chainLabel'] = Tkinter.Label(self.widgets['tframe'],text='Chain', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['chainLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['motionLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motion', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['motionLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['typeLabel'] = Tkinter.Label(self.widgets['tframe'],text='Type', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['typeLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['tframe'],text='Edit', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['editLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['tframe'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['deleteLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			rowcount = 1
			for k, v in self.chain['motions'].items():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['chain'+k] = Tkinter.Label(self.widgets['tframe'],text=self.chain['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['chain'+k].grid(column=0,row=self.gridrow,sticky='EW')
				
				if (any([ x for x in self.specification.motions.values() if x.jsonData['name'] == v['motion']])):
					self.widgets['motion'+k] = Tkinter.Label(self.widgets['tframe'],text=v['motion'], bg=rowcolour, fg=self.colours['fg'], height=2)
					self.widgets['motion'+k].grid(column=1,row=self.gridrow,sticky='EW')
				else:
					self.widgets['motion'+k] = Tkinter.Label(self.widgets['tframe'],text='missing', bg=rowcolour, fg=self.colours['fg'], height=2)
					self.widgets['motion'+k].grid(column=1,row=self.gridrow,sticky='EW')

				self.widgets['type'+k] = Tkinter.Label(self.widgets['tframe'],text=v['type'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['type'+k].grid(column=2,row=self.gridrow,sticky='EW')
				
				self.widgets['edit'+k] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnEditChainMotionClick(x))
				self.widgets['edit'+k].grid(column=3,row=self.gridrow,sticky='EW')
				
				self.widgets['delete'+k] = Tkinter.Button(self.widgets['tframe'],text=u"Delete", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnDeleteChainMotionClick(x))
				self.widgets['delete'+k].grid(column=4,row=self.gridrow,sticky='EW')
				
				self.gridrow += 1
		else:
			self.widgets['nochainslabel'] = Tkinter.Label(self.widgets['tframe'],text="This chain currently has no motions.", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nochainslabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		self.widgets['cancelbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Cancel", image=self.images['back'], command=self.OnEditChainClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['cancelbutton'].grid(column=0,row=self.gridrow)
	def editChainMotion(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Chain / Chain Motion / Edit', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['motionLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motion', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['motionLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['motion'] = Tkinter.StringVar()
		if(self.chainmotion['motion'] != ''):
			self.variables['motion'].set(self.chainmotion['motion'])

		self.widgets['motionentry'] = Tkinter.OptionMenu(self.widgets['tframe'],self.variables['motion'], *self.getMotionNames())
		self.widgets['motionentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
		self.widgets['motionentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		
		self.widgets['typeLabel'] = Tkinter.Label(self.widgets['tframe'],text='Type', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['typeLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['type'] = Tkinter.StringVar()
		if(self.chainmotion['type'] != ''):
			self.variables['type'].set(self.chainmotion['type'])
		self.widgets['typeentry'] = Tkinter.OptionMenu(self.widgets['tframe'],self.variables['type'], 'start', 'loop', 'stop')
		self.widgets['typeentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
		self.widgets['typeentry'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.chainmotion['type'] != ''):
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['deleteLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.listChainMotions, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['save'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Chain Motion", image=self.images['save'], command=self.OnSaveChainMotionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['save'].grid(column=1,row=self.gridrow)
		if(self.chainmotion['type'] != ''):
			self.widgets['delete'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete Chain Motion", image=self.images['delete'], command=self.OnDeleteChainMotionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['delete'].grid(column=2,row=self.gridrow)
		
	def deleteChainMotion(self):
		self.open()
		self.gridrow = 0
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Motions / Chain / Chain Motion / Delete', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		self.widgets['confirmlabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this chain motion?', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['confirmlabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['namelabel'] = Tkinter.Label(self.widgets['tframe'],text="Chain", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['namelabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['namedata'] = Tkinter.Label(self.widgets['tframe'],text=self.chain['name'], bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['namedata'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['motionlabel'] = Tkinter.Label(self.widgets['tframe'],text="Motion", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['motionlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['motiondata'] = Tkinter.Label(self.widgets['tframe'],text=self.chainmotion['motion'], bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['motiondata'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['typelabel'] = Tkinter.Label(self.widgets['tframe'],text="Type", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['typelabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['typedata'] = Tkinter.Label(self.widgets['tframe'],text=self.chainmotion['type'], bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['typedata'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['acceptlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Accept", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['acceptlabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['cancelbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Cancel", image=self.images['back'], command=self.OnCancelDeleteChainMotionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['cancelbutton'].grid(column=0,row=self.gridrow)
		self.widgets['confirmbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['accept'], command=self.OnDeleteChainMotionConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['confirmbutton'].grid(column=1,row=self.gridrow)
	
	#=== ACTIONS ===#
	##== Service ==##
	def OnStartClick(self):
		self.widgets['start'].configure(state='disabled')
		self.widgets['stop'].configure(state='normal')
		self.gui.scheduler.tasks['motion_scheduler'].start()
	def OnStopClick(self):
		self.widgets['start'].configure(state='normal')
		self.widgets['stop'].configure(state='disabled')
		self.gui.scheduler.tasks['motion_scheduler'].stop()
	def OnToggleAutostartClick(self):
		self.autostart = Setting.set('motion_scheduler_autostart', self.variables['autostart'].get())
	
	##== Motions ==##
	def OnRelaxClick(self):
		self.gui.motionScheduler.relax()
		self.notifier.addNotice('Servos relaxed.')
	def OnDefaultClick(self):
		self.gui.motionScheduler.default()
		self.notifier.addNotice('Default servo position activated.')
	def OnListMotionsClick(self):
		self.refreshMotions()
		self.listMotions()
	def OnAddMotionClick(self):
		self.motion = Motion()
		self.editMotion()
	def OnRefreshClick(self):
		self.refreshMotions()
		self.listMotions()
	def OnPlayMotionClick(self, index = None):
		self.gui.motionScheduler.triggerMotion(index)
	def OnPlaySlowMotionClick(self, index = None):
		self.gui.motionScheduler.triggerMotion(index, True)
	def OnSaveMotionClick(self):
		name = self.variables['name'].get()
		fps = self.variables['fps'].get()
		if (len(name) < 3):
			self.notifier.addNotice('Name must be at least 3 characters', 'warning')
			return
		if (fps < 1 or fps > 50):
			self.notifier.addNotice('FPS must be between 1 and 50', 'warning')
			return
		self.motion.jsonData['name'] = name
		self.motion.jsonData['fps'] = fps
		self.motion.save()
		self.specification.motions[self.motion.jbIndex] = self.motion
		self.specification.save()
		self.notifier.addNotice('Motion saved')
		self.refreshMotions()
		self.listMotions()
	def OnEditMotionClick(self, index):
		self.motion = Motion(index)
		self.editMotion()
	def OnEditKeyFramesClick(self):
		self.keyframes = { x['time']:x for x in self.motion.jsonData['keyframes'] }
		self.editKeyFrames()
	def OnDeleteMotionClick(self):
		self.deleteMotion()
	def OnCancelDeleteClick(self):
		self.listMotions()
	def OnDeleteMotionConfirmClick(self):
		if hasattr(self, 'motion'):
			del(self.specification.motions[self.motion.jbIndex])
			self.motion.delete()
			del(self.motion)
			self.specification.save()
			self.refreshMotions()
			self.notifier.addNotice('Motion deleted')
			self.listMotions()
	def OnAddTimeClick(self):
		self.duration += 1000
		self.widgets['timeline'].configure(to=self.duration)
		self.notifier.addNotice('1 Second added. Update to apply')
	def OnTrimTimeClick(self):
		self.duration = 1000
		if(any(self.keyframes)):
			self.duration = self.keyframes[sorted(self.keyframes)[-1]]['time']
		#self.editKeyFrames()
		self.notifier.addNotice('Motion time trimmed')
	def OnMoveKeyFrameClick(self):
		self.currentTime = self.time.get()
		self.moveKeyFrame()
	def OnMoveKeyFrameConfirmClick(self):
		newtime = self.variables['newtime'].get()
		if (self.currentTime == newtime):
			self.notifier.addNotice('Frame already at ' + str(newtime), 'warning')
			return
		if (newtime in self.keyframes.keys()):
			self.notifier.addNotice('A frame already exists at ' + str(newtime), 'warning')
			return
		self.keyframes[newtime] = copy(self.keyframes[self.currentTime])
		self.keyframes[newtime]['time'] = newtime
		del(self.keyframes[self.currentTime])
		self.notifier.addNotice('Keyframe moved. Update to apply.')
		self.editKeyFrames()
	def OnCloneKeyFrameClick(self):
		self.currentTime = self.time.get()
		self.cloneKeyFrame()
	def OnCloneKeyFrameConfirmClick(self):
		newtime = self.variables['newtime'].get()
		if (self.currentTime == newtime):
			self.notifier.addNotice('Cannot clone to same time', 'warning')
			return
		if (newtime in self.keyframes.keys()):
			self.notifier.addNotice('A frame already exists at ' + str(newtime), 'warning')
			return
		self.keyframes[newtime] = copy(self.keyframes[self.currentTime])
		self.keyframes[newtime]['time'] = newtime
		self.notifier.addNotice('Keyframe cloned. Update to apply.')
		self.editKeyFrames()
		self.notifier.addNotice('Keyframe Cloned')
	def OnUpdateKeyFrameClick(self):
		kf = {
			'time': self.time.get(),
			'instructions': []
		}
		for s in self.channelindex:
			kf['instructions'].append({
				'channel': s.channel,
				'angle': self.variables['servoangle'+s.jbIndex].get(),
				'disabled': self.variables['servodisabled'+s.jbIndex].get()
			})
			self.keyframes[kf['time']] = kf
		
		self.__implantKeyframes()
		self.motion.save()
		self.editKeyFrames()
		self.notifier.addNotice('Keyframe updated')
	def OnDeleteKeyFrameClick(self):
		self.currentTime = self.time.get()
		self.deleteKeyFrame()
	def OnDeleteKeyFrameConfirmClick(self):
		del(self.keyframes[self.currentTime])
		self.notifier.addNotice('Keyframe deleted. Update to apply')
		self.editKeyFrames()
	def OnCancelKeyFrameClick(self):
		self.editKeyFrames()
	def OnUpdateAngles(self, event):
		for s in self.channelindex:
			s.angle = self.variables['servoangle'+s.jbIndex].get()
			s.setServoAngle()

	##== Chains ==##
	def OnListChainsClick(self):
		self.chains = self.specification.chains
		self.listChains()
	def OnAddChainClick(self):
		self.chain = {
			'name': '',
			'motions': {}
		}
		self.editChain()
	def OnEditChainClick(self, index = None):
		if (index != None):
			self.chain = self.chains[index]
			self.editChain()
		elif (hasattr(self, 'chain')):
			self.editChain()
	def OnSaveChainClick(self):
		if (hasattr(self, 'chain')):
			name = self.variables['name'].get()
			if (name == ''):
				self.notifier.addNotice('Please specify a name','warning')
				return
			if (self.chain['name'] == '' and name in self.chains.keys()):
				self.notifier.addNotice('A chain with that name already exists','warning')
				return
			self.chain['name'] = name
			self.specification.chains[name] = self.chain
			self.specification.save()
			self.notifier.addNotice('Chain saved')
			self.listChains()
	def OnDeleteChainClick(self, index = None):
		if (index != None):
			self.chain = self.chains[index]
			self.deleteChain()
		elif hasattr(self, 'chain'):
			self.deleteChain()
	def OnDeleteChainConfirmClick(self):
		if hasattr(self, 'chain'):
			del(self.specification.chains[self.chain['name']])
			self.specification.save()
			self.chain = None
		self.listChains()
	def OnCancelDeleteChainClick(self):
		self.listChains()
	def OnPlayChainClick(self, index):
		self.gui.motionScheduler.triggerChain(index)
	def OnListChainMotionsClick(self, index = None):
		if (index != None):
			self.chain = self.specification.chains[index]
			self.listChainMotions()
		elif(hasattr(self, 'chain')):
			self.listChainMotions()
	def OnAddChainMotionClick(self):
		self.chainmotion = {
			'index': str(uuid.uuid4()),
			'motion': '',
			'type': '',
		}
		self.editChainMotion()
	def OnEditChainMotionClick(self, index = None):
		if (index != None):
			self.chainmotion = self.chain['motions'][index]
			self.editChainMotion()
		elif (hasattr(self, 'chainmotion')):
			self.editChainMotion()
	def OnSaveChainMotionClick(self):
		motion = self.variables['motion'].get()
		chaintype = self.variables['type'].get()
		if (not motion in [ x.jsonData['name'] for x in self.specification.motions.values() ]):
			self.notifier.addNotice('Invalid motion name','warning')
			return
		if (chaintype == ''):
			self.notifier.addNotice('Please select a type','warning')
			return
		self.chainmotion['motion'] = motion
		self.chainmotion['type'] = chaintype
		self.chain['motions'][self.chainmotion['index']] = self.chainmotion
		self.specification.save()
		self.notifier.addNotice('Chain motion saved')
		self.OnListChainMotionsClick()
	def OnDeleteChainMotionClick(self, index = None):
		if (index != None):
			self.chainmotion = self.chain['motions'][index]
			self.deleteChainMotion()
		elif (hasattr(self, 'chainmotion')):
			self.deleteChainMotion()
	def OnDeleteChainMotionConfirmClick(self):
		if hasattr(self, 'chainmotion'):
			del(self.chain['motions'][self.chainmotion['index']])
			self.specification.save()
			self.chainmotion = None
			self.notifier.addNotice('Chain motion deleted')
			self.listChainMotions()
	def OnCancelDeleteChainMotionClick(self):
		self.listChainMotions()
			
	#=== UTILS ===#
	def getMotionNames(self):
		motions = []
		for m in self.motions.values():
			motions.append(m.jsonData['name'])
		return tuple(motions)
	def getMotionFromName(self, name):
		motion = None
		m = {k:v for k,v in self.motions.items() if v.jsonData['name'] == name }
		if(len(m) == 1):
			motion = m[m.keys()[0]]
		return motion
	def getMotionFromId(self, id):
		return motion[id]
	def refreshMotions(self):
		self.motions = self.specification.motions
		
	def __implantKeyframes(self):
		self.motion.jsonData['keyframes'] = []
		if (len(self.keyframes) > 0):
			for key in sorted(self.keyframes):
				self.motion.jsonData['keyframes'].append(self.keyframes[key])	