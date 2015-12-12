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
import Tkinter, time
from Tkinter import *
from TkBlock import *
from Notifier import *
from Scheduler import *
from Setting import *
class TkNotifier(TkBlock):
	def __init__(self, parent, gui, **options):
		super(TkNotifier,self).__init__(parent, gui, **options)
		self.now = lambda: int(round(time.time() * 1000))
		self.displayed = []
		self.firstrun = True
		self.notifier = Notifier(log=Setting.get('notifier_log', False))
		self.notifier.setCallback(self.update)
		self.addNotifier()
		self.notifier.addNotice('Welcome to AllMyServos')
		self.gui.scheduler.addTask('notifier_cleanup', self.cleanup, 15)
	def addNotifier(self):
		self.open()
		self.widgets['main'] = Tkinter.Frame(self.widget, bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['main'].grid(column=0,row=0,sticky='EW')
		self.widgets['main'].grid_columnconfigure(0, weight=1)
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['main'],text='Notifications', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['archive'] = Tkinter.BooleanVar()
		self.variables['archive'].set(Setting.get('notifier_archive', False))
		self.widgets['archiveentry'] = Tkinter.Checkbutton(self.widgets['main'], text="Archive", variable=self.variables['archive'], command=self.OnToggleArchiveClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['archiveentry'].grid(column=1,row=self.gridrow,sticky='E')
		
		self.gridrow += 1
		self.widgets['notices'] = Tkinter.Frame(self.widgets['main'], bg=self.colours['bg'])
		self.widgets['notices'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.widgets['notices'].grid_columnconfigure(0, weight = 1)
		#self.widgets['notices'].grid_propagate(False)
	def update(self):
		if(len(self.displayed) <= 20):
			n = self.notifier.getNotice()
			self.displayed.append(TkNotice(self.widgets['notices'], self.gui, n['time'], n['text'], n['type'], self.width))
	def cleanup(self):
		dlen = len(self.displayed)
		if(dlen > 0 and self.firstrun == False):
			removed = None
			try:
				if(self.displayed[0].time <= (self.now() - 10000)):
					self.displayed[0].remove()
					if(dlen == 1):
						self.displayed = []
					else:
						self.displayed = self.displayed[1:]
			except:
				pass
		if(self.firstrun == True):
			self.firstrun = False
	def close(self):
		self.widget.grid_forget()
	def OnToggleArchiveClick(self):
		Setting.set('notifier_archive', self.variables['archive'].get())
class TkNotice(object):
	def __init__(self, parent, gui, time, text, type = 'notice', width=840):
		try:
			TkNotice.displayed
		except:
			TkNotice.displayed = 0
		nrow = TkNotice.displayed
		TkNotice.displayed += 1
		self.widgets = {}
		self.gui = gui
		self.colours = self.gui.colours
		self.fonts = self.gui.fonts
		self.images = self.gui.images
		self.text = text
		self.type = type
		self.time = time
		self.removed = False
		bg = self.colours['noticebg']
		image = self.images['notice']
		if(type == 'warning'):
			bg = self.colours['warningbg']
			image = self.images['warning']
		elif(type == 'error'):
			bg = self.colours['errorbg']
			image = self.images['error']
		self.widget = Frame(parent,bg=self.colours['bg'], borderwidth=1)
		self.widget.grid(column=0,row=nrow,  sticky='EW')
		self.widget.columnconfigure(0, weight=1)
		self.widgets['subframe'] = Frame(self.widget,bg=bg, borderwidth=1)
		self.widgets['subframe'].grid(column=0,row=nrow,  sticky='EW')
		self.widgets['subframe'].columnconfigure(0, weight=1)
		
		self.widgets['subframe2'] = Frame(self.widgets['subframe'],bg=self.colours['bg'], borderwidth=2, width=width)
		self.widgets['subframe2'].grid(column=0,row=nrow,  sticky='EW')
		self.widgets['subframe2'].columnconfigure(1, weight=1)
		
		nrow = TkNotice.displayed
		TkNotice.displayed += 1
		
		self.widgets['stretchframe'] = Frame(self.widget,bg=self.colours['bg'], borderwidth=0, width=width-20)
		self.widgets['stretchframe'].grid(column=0,row=nrow,  sticky='EW')
		self.widgets['stretchframe'].columnconfigure(0, weight=1)
		
		self.widgets['imageLabel'] = Tkinter.Label(self.widgets['subframe2'],text=self.type, anchor=W, image = image, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['imageLabel'].grid(column=0,row=0, padx= 10,sticky='EW')
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['subframe2'],text=self.text, anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['frameLabel'].grid(column=1,row=0, padx=10, pady=5,sticky='W')
	def remove(self):
		self.widget.grid_forget()
		