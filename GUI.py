#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
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

import __bootstrap, TrayIcon, Tkinter, tkFont, webbrowser, datetime, sys, os
from Tkinter import *
from TkBlock import TkBlock, TkPage
from PreFlight import PreFlight
from Theme import *
from Setting import *
from Scheduler import *


## The GUI object handles the entire sequence of setting up the TkInter window
class GUI(Tkinter.Tk):
	def __init__(self,parent=None):
		""" Initializes the GUI Object
		
		@param parent
		"""
		Tkinter.Tk.__init__(self,parent)
		self.screen = { 'width': self.winfo_screenwidth(), 'height': self.winfo_screenheight() }
		self.widgets, self.menus = {}, {}
		self.title('AllMyServos')
		self.parent = parent
		self.setting = Setting()
		if(PreFlight.status()):
			self.specification = self.getClass('Specification.Specification')() #avoids importing before preflight checks
			self.scheduler = Scheduler()
			self.motionScheduler = self.getClass('Motion.MotionScheduler')(self.specification, self.scheduler)
			self.initTheme()
			self.initFrames()
			self.trayIcon = TrayIcon.TrayIcon(self.scheduler)
			self.setup()
		else:
			self.initTheme()
			self.initFrames()
			self.setupPreFlight()
	def setupPreFlight(self):
		"""	Initializes the interface for pre flight checks
		"""
		self.menubar = Tkinter.Menu(self, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		#logo
		c = self.getClass('TkPreFlightManager.TkPreFlightLogo')
		w = {
			'name': 'TkPreFlightManager.TkPreFlightLogo',
			'row': 0,
			'column': 0,
			'width': None,
			'height': None,
			'rowspan': None, 
			'columnspan': None, 
			'padx': 0, 
			'pady': 0, 
			'sticky': 'NS', 
			'scrollable': False,
			'rowweight': 1, 
			'columnweight': 1,
			'menuindex': 1
		}
		self.widgets['main'] = { c.__name__ : c(parent=self.frames['left'], gui=self, **w) }
		#checks
		c = self.getClass('TkPreFlightManager.TkPreFlightManager')
		w = {
			'name': 'TkPreFlightManager.TkPreFlightManager',
			'row': 0,
			'column': 0,
			'width': None,
			'height': None,
			'rowspan': None, 
			'columnspan': None, 
			'padx': 10, 
			'pady': 10, 
			'sticky': 'WENS', 
			'scrollable': False,
			'rowweight': 1, 
			'columnweight': 1,
			'menuindex': 1
		}
		self.widgets['main'] = { c.__name__ : c(parent=self.frames['main'], gui=self, **w) }
		self.config(menu=self.menubar)
		self.widgets['main']['TkPreFlightManager'].OnChecksClick()
		#screens
		c = self.getClass('TkPreFlightManager.TkPreFlightScreens')
		w = {
			'name': 'TkPreFlightManager.TkPreFlightScreens',
			'row': 0,
			'column': 0,
			'width': None,
			'height': None,
			'rowspan': None, 
			'columnspan': None, 
			'padx': 0, 
			'pady': 0, 
			'sticky': 'NS', 
			'scrollable': False,
			'rowweight': 1, 
			'columnweight': 1,
			'menuindex': 1
		}
		self.widgets['main'] = { c.__name__ : c(parent=self.frames['right'], gui=self, **w) }
	def setup(self):
		""" Initializes the menubar and adds frames and widgets from the theme profile
		"""
		self.menubar = Tkinter.Menu(self, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])

		for f in self.theme.profile['frames']: # each frame in the profile
			self.widgets[f['name']] = {} # make a slot for this frame
			for w in f['widgets']: # each widget in the frame
				c = self.getClass(w['name']) # get a reference to the class
				self.widgets[f['name']][c.__name__] = c(parent=self.frames[f['name']], gui=self, **w) # initialize the class with attributes from the profile
		self.config(menu=self.menubar)
		if(len(self.specification.servos) > 0):
			self.widgets['main']['TkMotionManager'].OnListMotionsClick() # if servos exist in this specification open the motion manager
		else:
			self.widgets['main']['TkServoManager'].OnListServosClick() # otherwise open the servo manager
	def initTheme(self):
		""" Loads the current theme
		"""
		self.theme = Theme(self.setting.get('gui_theme_name','DarkBlue'), self.screen)
		self.theme.load()
		self.images, self.colours, self.fonts = {}, {}, {}
		for k, v in self.theme.images.iteritems():
			self.images[k] = Tkinter.PhotoImage(file = os.path.join(self.theme.basepath, v))
		self.colours = self.theme.colours
		for k, v in self.theme.fonts.iteritems():
			self.fonts[k] = tkFont.Font(family=v['family'], size=v['size'])
	def initFrames(self):
		""" Creates frames according to the profile
		"""
		self.frames = {}
		if(self.theme.profile != None):
			profile = self.theme.profile
			self.frames['appWrap'] = Tkinter.Frame(self, bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
			self.frames['appWrap'].pack(fill=BOTH, expand=1)
			self.frames['appWrap'].columnconfigure(0, weight=1)
			self.frames['appWrap'].rowconfigure(0, weight=1)
			self.frames['appCanvas'] = Tkinter.Canvas(self.frames['appWrap'], borderwidth=0, bg=self.colours['bg'], highlightthickness=0)
			self.frames['appCanvas'].grid(column=0,row=0, padx= 10,sticky='WENS')
			self.frames['app'] = Tkinter.Frame(self.frames['appCanvas'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
			self.frames['app'].pack(fill=BOTH, expand=1)
			if(profile['scrollable']): #makes the whole window scrollable for accessibility
				self.frames['appyScroller'] = Tkinter.Scrollbar(self.frames['appWrap'], orient=VERTICAL, command=self.frames['appCanvas'].yview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
				self.frames['appyScroller'].grid(column=1, row=0, sticky="NS")
				self.frames['appxScroller'] = Tkinter.Scrollbar(self.frames['appWrap'], orient=HORIZONTAL, command=self.frames['appCanvas'].xview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
				self.frames['appxScroller'].grid(column=0, row=1, sticky="EW")
				self.frames['appCanvas'].configure(yscrollcommand=self.frames['appyScroller'].set, xscrollcommand=self.frames['appxScroller'].set, bg=self.colours['bg'])
				self.frames['appCanvas'].create_window((0,0),window=self.frames['app'], anchor=NW)
				self.frames['app'].bind("<Configure>", self.scroll)
				self.frames['appCanvas'].bind("<Button-4>", self.mouseScroll)
				self.frames['appCanvas'].bind("<Button-5>", self.mouseScroll)
				
			for f in profile['frames']:
				self.frames['{0}{1}'.format(f['name'], 'Wrap')] = Tkinter.Frame(self.frames['app'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
				self.frames['{0}{1}'.format(f['name'], 'Wrap')].grid(column=f['column'],row=f['row'],columnspan=f['columnspan'],rowspan=f['rowspan'],sticky=f['sticky'])
				if (f['columnweight'] > 0):
					self.frames['app'].columnconfigure(f['column'], weight=f['columnweight'])
				if (f['rowweight'] > 0):
					self.frames['app'].rowconfigure(f['row'], weight=f['rowweight'])
				self.frames['{0}{1}'.format(f['name'], 'Wrap')].columnconfigure(0, weight=1)
				self.frames['{0}{1}'.format(f['name'], 'Wrap')].rowconfigure(0, weight=1)
				self.frames['{0}{1}'.format(f['name'], 'Canvas')] = Tkinter.Canvas(self.frames['{0}{1}'.format(f['name'], 'Wrap')], borderwidth=0, bg=self.colours['bg'], highlightthickness=0)
				self.frames['{0}{1}'.format(f['name'], 'Canvas')].grid(column=0,row=0,sticky='WENS')
				self.frames['{0}{1}'.format(f['name'], 'Canvas')].columnconfigure(0, weight=1)
				self.frames['{0}{1}'.format(f['name'], 'Canvas')].rowconfigure(0, weight=1)
				self.frames[f['name']] = Tkinter.Frame(self.frames['{0}{1}'.format(f['name'], 'Canvas')], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
				self.frames[f['name']].grid(column=0,row=0,sticky='WENS')
				self.frames[f['name']].columnconfigure(0, weight=1)
				self.frames[f['name']].rowconfigure(0, weight=1)
				if(f['scrollable']): # makes this frame scrollable
					self.frames['{0}{1}'.format(f['name'], 'yScroller')] = Tkinter.Scrollbar(self.frames['{0}{1}'.format(f['name'], 'Wrap')], orient=VERTICAL, command=self.frames['{0}{1}'.format(f['name'], 'Canvas')].yview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
					self.frames['{0}{1}'.format(f['name'], 'yScroller')].grid(column=1, row=0, sticky="NS")
					self.frames['{0}{1}'.format(f['name'], 'xScroller')] = Tkinter.Scrollbar(self.frames['{0}{1}'.format(f['name'], 'Wrap')], orient=HORIZONTAL, command=self.frames['{0}{1}'.format(f['name'], 'Canvas')].xview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
					self.frames['{0}{1}'.format(f['name'], 'xScroller')].grid(column=0, row=1, sticky="EW")
					self.frames['{0}{1}'.format(f['name'], 'Canvas')].configure(yscrollcommand=self.frames['{0}{1}'.format(f['name'], 'yScroller')].set, xscrollcommand=self.frames['{0}{1}'.format(f['name'], 'xScroller')].set)
					self.frames['{0}{1}'.format(f['name'], 'Canvas')].create_window((0,0),window=self.frames[f['name']], anchor=NW)
					self.frames[f['name']].bind("<Configure>", self.scroll)
					self.frames['{0}{1}'.format(f['name'], 'Canvas')].bind("<Button-4>", self.mouseScroll)
					self.frames['{0}{1}'.format(f['name'], 'Canvas')].bind("<Button-5>", self.mouseScroll)
		else:
			# fallback layout
			self.frames['header'] = Tkinter.Frame(self, borderwidth=0, bg = self.colours['bg'])
			self.frames['header'].grid(row = 0, column = 0, rowspan = 1, columnspan = 3, padx= 10, sticky = "WENS")
			self.frames['left'] = Tkinter.Frame(self, borderwidth=0, bg = self.colours['bg'])
			self.frames['left'].grid(row = 1, column = 0, sticky = "WENS")
			
			self.frames['mainWrap'] = Tkinter.Frame(self, bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
			self.frames['mainWrap'].grid(column=1,row=1,sticky='NW')
			
			self.frames['mainCanvas'] = Tkinter.Canvas(self.frames['mainWrap'], borderwidth=0, bg=self.colours['bg'], highlightthickness=0, width=920, height=710)
			self.frames['mainCanvas'].grid(column=0,row=0, padx= 10,sticky='NE')
			
			self.frames['main'] = Tkinter.Frame(self.frames['mainCanvas'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
			self.frames['main'].grid(column=0,row=0,sticky='NW')
			
			self.frames['yScroller'] = Tkinter.Scrollbar(self.frames['mainWrap'], orient=VERTICAL, command=self.frames['mainCanvas'].yview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
			self.frames['yScroller'].grid(column=1, row=0, sticky="NS")
			self.frames['xScroller'] = Tkinter.Scrollbar(self.frames['mainWrap'], orient=HORIZONTAL, command=self.frames['mainCanvas'].xview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
			self.frames['xScroller'].grid(column=0, row=1, sticky="EW")
			
			self.frames['mainCanvas'].configure(yscrollcommand=self.frames['yScroller'].set, xscrollcommand=self.frames['xScroller'].set, bg=self.colours['bg'])
			self.frames['mainCanvas'].create_window((0,0),window=self.frames['main'], anchor=NW)
			self.frames['main'].bind("<Configure>", self.scroll)
			
			self.frames['mainCanvas'].bind("<Button-4>", self.mouseScroll)
			self.frames['mainCanvas'].bind("<Button-5>", self.mouseScroll)

			self.frames['right'] = Tkinter.Frame(self, borderwidth=0, bg = self.colours['bg'])
			self.frames['right'].grid(row = 1, column = 2, sticky = "WENS")
			
			self.frames['footerwrap'] = Tkinter.Frame(self, borderwidth=0, bg = self.colours['bg'])
			self.frames['footerwrap'].grid(row = 2, column = 0, columnspan= 3, sticky = "WENS")
			
			self.frames['footer'] = Tkinter.Frame(self.frames['footerwrap'], borderwidth=0, bg = self.colours['bg'])
			self.frames['footer'].grid(row = 0, column = 0, sticky = "WENS")
		
		self.configure(bg=self.colours['bg'], borderwidth=0)
		self.geometry('{}x{}'.format(self.screen['width'], self.screen['height']))
	def scroll(self, event):
		""" Generic function to handle resizing
		
		@param event TkInter event object
		"""
		event.widget.master.configure(scrollregion=event.widget.master.bbox(ALL))
	def mouseScroll(self, event):
		""" Generic function to handle scroll wheel events
		"""
		event.widget.yview('scroll', -1 if event.num == 4 else 1,'units')
	def reset(self):
		""" Resets the scrollbar to the top when changing widget in the main frame
		"""
		self.frames['mainCanvas'].yview('moveto', 0)
	def clearMain(self):
		""" Convenience function which closes all widgets in the 'main' frame
		"""
		if('main' in self.widgets.keys()):
			for k, v in self.widgets['main'].iteritems():
				v.close()
		self.reset()
	def getClass(self, name):
		""" Returns an uninstantiated class object from a string. 
		
		@param name String containing [MODULE].[CLASS] e.g. 'Logo.Logo'
		"""
		ns = name.split(".")
		modname = ns[0]
		classname = ns[1]
		if(len(ns) > 2):
			modname = '.'.join(ns[0:-2])
			classname = ns[-1]
		mod = __import__(modname)
		return getattr(mod, classname)
	def getModule(self, name):
		""" Returns a reference to the specified module
		
		@param name Module name e.g. Logo
		
		@return Module
		"""
		return __import__(name)
if __name__ == "__main__":
	app = GUI()
	app.mainloop() # fire this puppy up!