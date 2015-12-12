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
import Tkinter, ttk, sys
from Tkinter import *
from TkBlock import *

class TkScheduleManager(TkPage):
	def __init__(self, parent, gui, **options):
		super(TkScheduleManager,self).__init__(parent, gui, **options)
		self.scheduler = self.gui.scheduler
	def setup(self):
		self.gui.menus['schedule'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		self.gui.menus['schedule'].add_command(label="Scheduled Tasks", command=self.OnListTasksClick)
		self.addMenu(label="Schedule", menu=self.gui.menus['schedule'])
	
	#=== VIEWS ===#
	def listTasks(self):
		self.open()
		self.widgets['slabel'] = Tkinter.Label(self.widgets['tframe'],text='Schedule / Scheduled Tasks', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['slabel'].grid(column=0,row=self.gridrow, columnspan=3, sticky='EW')
		self.widgets['startall'] = Tkinter.Button(self.widgets['tframe'],text=u"Start All", image=self.images['play'], command=self.OnStartAllClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['startall'].grid(column=4,row=self.gridrow)
		self.widgets['stopall'] = Tkinter.Button(self.widgets['tframe'],text=u"Stop All", image=self.images['stop'], command=self.OnStopAllClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['stopall'].grid(column=5,row=self.gridrow)
		self.widgets['resetall'] = Tkinter.Button(self.widgets['tframe'],text=u"Reset All", image=self.images['reset'], command=self.OnResetAllClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['resetall'].grid(column=6,row=self.gridrow)
		
		self.gridrow += 1
		
		if(len(self.scheduler.tasks) > 0):
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['statusLabel'] = Tkinter.Label(self.widgets['tframe'],text='Status', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['statusLabel'].grid(column=1,row=self.gridrow, padx=15, sticky='EW')
			self.widgets['callbackLabel'] = Tkinter.Label(self.widgets['tframe'],text='Callback', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['callbackLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['intervalLabel'] = Tkinter.Label(self.widgets['tframe'],text='Interval', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['intervalLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['startLabel'] = Tkinter.Label(self.widgets['tframe'],text='Start', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['startLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.widgets['stopLabel'] = Tkinter.Label(self.widgets['tframe'],text='Stop', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['stopLabel'].grid(column=5,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			rowcount = 1
			for k, v in self.scheduler.tasks.iteritems():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['name'+k] = Tkinter.Label(self.widgets['tframe'],text=k, bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['name'+k].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['status'+k] = Tkinter.Label(self.widgets['tframe'],text='Stopped' if v.stopped else 'Running', bg=rowcolour, fg=self.colours['headingfg'], height=2)
				self.widgets['status'+k].grid(column=1,row=self.gridrow, sticky='EW')
				self.widgets['callback'+k] = Tkinter.Label(self.widgets['tframe'],text=v.callback.__name__, bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['callback'+k].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['interval'+k] = Tkinter.Label(self.widgets['tframe'],text=v.interval, bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['interval'+k].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['start'+k] = Tkinter.Button(self.widgets['tframe'],text=u"Start", image=self.images['play'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnStartTaskClick(x))
				self.widgets['start'+k].grid(column=4,row=self.gridrow,sticky='EW')
				self.widgets['stop'+k] = Tkinter.Button(self.widgets['tframe'],text=u"Stop", image=self.images['stop'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnStopTaskClick(x))
				self.widgets['stop'+k].grid(column=5,row=self.gridrow,sticky='EW')
				if(not v.stopped):
					self.widgets['start'+k].configure(state='disabled')
					self.widgets['stop'+k].configure(state='normal')
				else:
					self.widgets['start'+k].configure(state='normal')
					self.widgets['stop'+k].configure(state='disabled')
				self.gridrow += 1
		else:
			self.widgets['noschedulelabel'] = Tkinter.Label(self.widgets['tframe'],text="There are currently no scheduled tasks", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noschedulelabel'].grid(column=0,row=self.gridrow,sticky='EW')
	
	#=== ACTIONS ===#
	def OnListTasksClick(self):
		self.initialState = {}
		for t in self.scheduler.listTasks():
			self.initialState[t] = self.scheduler.isRunning(t)
		self.listTasks()
	def OnStartTaskClick(self, name):
		self.widgets['status'+name].configure(text='Running')
		self.widgets['start'+name].configure(state='disabled')
		self.widgets['stop'+name].configure(state='normal')
		self.scheduler.startTask(name)
	def OnStopTaskClick(self, name):
		self.widgets['status'+name].configure(text='Stopped')
		self.widgets['start'+name].configure(state='normal')
		self.widgets['stop'+name].configure(state='disabled')
		self.scheduler.stopTask(name)
	def OnStartAllClick(self):
		for t in self.scheduler.listTasks():
			self.OnStartTaskClick(t)
	def OnStopAllClick(self):
		for t in self.scheduler.listTasks():
			self.OnStopTaskClick(t)
	def OnResetAllClick(self):
		for k, v in self.initialState.iteritems():
			if(v):
				self.scheduler.startTask(k)
			else:
				self.scheduler.stopTask(k)
		self.listTasks()