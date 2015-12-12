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
from Setting import *
from Notifier import *
class TkBlock(object):
	def __init__(self, parent, gui, **options):
		'''
		TkBlock is a base class. Any class containing Tkinter objects should extend it.
		- initializes common attributes
		- creates a wrapped widget which applies the settings from the theme profile
		- provides generic views for data
		- provides open and close functions
		'''
		self.gui = gui
		self.parent = parent
		self.column, self.row, self.columnspan, self.rowspan, self.padx, self.pady, self.sticky, self.scrollable, self.rowweight, self.columnweight, self.menuindex, self.width, self.height = options['column'], options['row'], options['columnspan'], options['rowspan'], options['padx'], options['pady'], options['sticky'], options['scrollable'], options['rowweight'], options['columnweight'], options['menuindex'], options['width'], options['height']
		self.widgets, self.variables = {}, {}
		self.notifier = Notifier()
		# collect theme information from the gui
		self.colours = self.gui.colours
		self.fonts = self.gui.fonts
		self.images = self.gui.images
		self.initWidget()
		self.setup()
	def setup(self):
		'''
		override this for menu setup
		'''
		pass
	def initWidget(self):
		'''
		initializes the common Tkinter objects required to be displayed
		'''
		self.wrap = Tkinter.Frame(self.parent, bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.wrap.grid(row=self.row, column=self.column, padx=self.padx, pady=self.pady, columnspan=self.columnspan, rowspan=self.rowspan, sticky=self.sticky)
		self.wrap.columnconfigure(0, weight=1)
		self.wrap.rowconfigure(0, weight=1)
		self.parent.columnconfigure(self.column, weight=self.columnweight)
		self.parent.rowconfigure(self.row, weight=self.rowweight)
		self.canvas = Tkinter.Canvas(self.wrap, borderwidth=0, bg=self.colours['bg'], highlightthickness=0)
		self.canvas.grid(column=0,row=0,sticky='WENS')
		
		self.widget = Tkinter.Frame(self.canvas, bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widget.grid(column=0,row=0,sticky='WENS')
		self.widget.columnconfigure(0, weight=1)
		self.widget.rowconfigure(0, weight=1)
		if(self.width != None):
			if(self.width > 0):
				self.canvas.configure(width=self.width)
				self.wrap.configure(width=self.width)
		if(self.height != None):
			if(self.height > 0):
				self.canvas.configure(height=self.height)
				self.wrap.configure(height=self.height)
		if(self.scrollable):
			self.yScroller = Tkinter.Scrollbar(self.wrap, orient=VERTICAL, command=self.canvas.yview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
			self.yScroller.grid(column=1, row=0, sticky="NS")
			self.xScroller = Tkinter.Scrollbar(self.wrap, orient=HORIZONTAL, command=self.canvas.xview, bg=self.colours['bg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
			self.xScroller.grid(column=0, row=1, sticky="EW")
			self.canvas.configure(yscrollcommand=self.yScroller.set, xscrollcommand=self.xScroller.set, bg=self.colours['bg'])
			self.canvas.create_window((0,0),window=self.widget, anchor=NW)
			self.widget.bind("<Configure>", self.gui.scroll)
	def addMenu(self, menu, label="-"):
		'''
		convenience function to make use of a menu index if one is supplied by the profile
		'''
		if(isinstance(self.menuindex, int)):
			self.gui.menubar.insert_cascade(index=self.menuindex, label=label, menu=menu)
		else:
			self.gui.menubar.add_cascade(label=label, menu=menu)
	def open(self):
		'''
		calling open causes this block to be displayed within Tkinter
		normally called at the top of a view method 
		'''
		try:
			self.widgets
		except:
			self.widgets = {}
		else:
			for k, v in self.widgets.iteritems():
				try:
					v.grid_forget()
				except:
					pass
				try:
					v.close()
				except:
					pass
			self.widgets = {}
		self.wrap.grid(row=self.row, column=self.column, padx=self.padx, pady=self.pady, columnspan=self.columnspan, rowspan=self.rowspan, sticky=self.sticky)
		self.gridrow = 0
		self.widgets['tframe'] = Frame(self.widget,bg=self.colours['bg'], borderwidth=5)
		self.widgets['tframe'].grid(column=0,row=0,sticky='NW')
		self.widgets['tframe'].grid_columnconfigure(0, weight=1)
	def close(self):
		'''
		calling close causes this block to be hidden within Tkinter
		'''
		self.wrap.grid_forget()
	def genericView(self, parent, value):
		'''
		within a view method, this can be used to display any variable
		
		supports: int, float, long, str, unicode, dict and list
		'''
		w = Tkinter.Frame(parent, borderwidth=0, highlightthickness=0, bg=self.colours['rowaltbg'])
		if(isinstance(value, (int, float, long))):
			view = self.numberView(w, value)
		elif(isinstance(value, (str, unicode))):
			view = self.stringView(w, value)
		elif(isinstance(value, dict)):
			view = self.dictView(w, value)
		elif(isinstance(value, (list, tuple))):
			view = self.iterView(w, value)
		else:
			view = Tkinter.Label(w,text='TBD', bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
		view.grid(column=0,row=0, sticky='EW')
		return w
	def numberView(self, parent, value):
		'''
		formats a number for display within Tkinter
		'''
		w = Tkinter.Label(parent,text=str(value), bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], anchor='nw', height=2)
		return w
	def stringView(self, parent, value):
		'''
		formats a string for display within Tkinter
		'''
		w = Tkinter.Label(parent,text=str(value), bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], anchor='nw')
		return w
	def dictView(self, parent, value):
		'''
		formats a dict for display within Tkinter
		'''
		w = Tkinter.Frame(parent, borderwidth=0, highlightthickness=0, bg=self.colours['rowaltbg'])
		if(len(value) > 0):
			row = 0
			for k,v in value.iteritems():
				heading = Tkinter.Label(w,text=k, bg=self.colours['rowbg'], fg=self.colours['headingfg'], anchor='nw', height=2)
				heading.grid(column=0,row=row, ipadx=10, sticky='NWSE')
				if(isinstance(v, (int, float, long))):
					view = self.numberView(w, v)
				elif(isinstance(v, (str, unicode))):
					view = self.stringView(w, v)
				elif(isinstance(v, dict)):
					view = self.dictView(w, v)
				elif(isinstance(v, (list, tuple))):
					view = self.iterView(w, v)
				elif(v == None):
					view = self.stringView(w, 'None')
				else:
					print(type(v))
					view = self.stringView(w, 'TBD')
				view.grid(column=1,row=row, sticky='EW')
				row += 1
		else:
			view = Tkinter.Label(w,text='TBD', bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
			view.grid(column=0,row=0, sticky='EW')
		return w
	def iterView(self, parent, value):
		'''
		formats a list for display within Tkinter
		'''
		w = Tkinter.Frame(parent, borderwidth=0, highlightthickness=0, bg=self.colours['rowaltbg'])
		if(len(value) > 0):
			row = 0
			for i in value:
				heading = Tkinter.Label(w,text=row, bg=self.colours['rowbg'], fg=self.colours['headingfg'], anchor='nw', height=2)
				heading.grid(column=0,row=row, ipadx=10,sticky='NWSE')
				if(isinstance(i, (int, float, long))):
					view = self.numberView(w, i)
				elif(isinstance(i, (str, unicode))):
					view = self.stringView(w, i)
				elif(isinstance(i, dict)):
					view = self.dictView(w, i)
				elif(isinstance(i, (list, tuple))):
					view = self.iterView(w, i)
				else:
					view = self.stringView(w, 'TBD')
				view.grid(column=1,row=row, sticky='EW')
				row += 1
		else:
			view = Tkinter.Label(w,text='TBD', bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
			view.grid(column=0,row=0, sticky='EW')
		return w
class TkPage(TkBlock):
	def __init__(self, parent, gui, **options):
		'''
		TkPage - extends TkBlock
		Before opening, TkPage will clear the main frame, so this object replaces any previous page
		'''
		super(TkPage,self).__init__(parent, gui, **options)
	def open(self):
		self.gui.clearMain()
		super(TkPage,self).open()