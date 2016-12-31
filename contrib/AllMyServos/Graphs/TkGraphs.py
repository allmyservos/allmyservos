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

## UI for line graphs
class TkLineGraph():
	def __init__(self, parent, data, colours={}, width=100, height=100, xrange = {'min':None, 'max':None}, yrange = { 'min':None, 'max':None}, pointlimit = 50):
		""" initializes the attributes for a line graph
		
		@param parent
		@param data
		@param colours
		@param width
		@param height
		@param xrange
		@param yrange
		@param pointlimit
		"""
		self.widget = Frame(parent)
		self.data = data
		self.width = float(width)
		self.height = float(height)
		self.gheight = self.height -1
		self.initColours(colours)
		self.xrange = xrange
		self.yrange = yrange
		self.pointlimit = pointlimit
		if(not isinstance(pointlimit, int)):
			self.pointlimit = 100
		self.shapes = {}
		self.setup()
	def initColours(self, colours):
		""" setup the colours
		
		@param colours
		"""
		try:
			TkLineGraph.colours
		except:
			TkLineGraph.colours = colours
		try:
			self.widget.configure(borderwidth=5, bg = TkLineGraph.colours['bg'])
		except:
			self.widget.configure(borderwidth=5)
	def setup(self):
		""" creates a canvas for the graph
		"""
		self.widgets = {}
		gridrow = 0
		self.widgets['canvas'] = Tkinter.Canvas(self.widget, width=self.width, height=self.height, bg=TkLineGraph.colours['bg'], highlightthickness=0)
		self.widgets['canvas'].grid(column=0,row=gridrow, sticky='EW')
		self.update()
	def addData(self, key=None, value=None):
		""" appends data to the graph
		
		@param key
		@param value
		"""
		if(key != None and value != None):
			self.data[key] = value
	def delData(self, index):
		""" removes data from the graph
		
		@param index
		"""
		try:
			self.widgets['canvas'].delete(self.shapes[index])
			del(self.shapes[index])
		except:
			pass
	def update(self):
		""" creates or arranges lines on the canvas
		"""
		fields = self.data.keys()
		fields.sort()
		if(self.pointlimit != None):
			overfill = len(self.data) - (self.pointlimit-1)
			while overfill > 0:
				#self.delData(overfill-1)
				self.data.pop(fields[overfill-1],None)
				del(fields[overfill-1])
				overfill -= 1
		values = self.data.values()
		count = len(fields)
		if(self.xrange['min'] != None):
			xmin = self.xrange['min']
		elif(count < 2):
			xmin = 0
		else:
			xmin = min(fields)
		if(self.xrange['max'] != None):
			xmax = self.xrange['max']
		elif(count < 2):
			xmax = 100
		else:
			xmax = max(fields)
		if(self.yrange['min'] != None):
			ymin = self.yrange['min']
		elif(count < 2):
			ymin = 0
		else:
			ymin = min(values)
		if(self.yrange['max'] != None):
			ymax = self.yrange['max']
		elif(count < 2):
			ymax = 100
		else:
			ymax = max(values)
		xunit = self.width / (xmax - xmin)
		xrange = xmax - xmin
		yunit = self.height / (ymax - ymin)
		yrange = ymax - ymin
		if(count > 2 and 'default' in self.shapes):
			try:
				self.widgets['canvas'].delete(self.shapes['default'])
				del(self.shapes['default'])
			except:
				pass
		if(count > 1):
			for i in range(count-1):
				try:
					self.widgets['canvas'].coords(self.shapes[i],(fields[i]-xmin)*xunit,self.gheight-((self.data[fields[i]]-ymin)*yunit),(fields[i+1]-xmin)*xunit,self.gheight-((self.data[fields[i+1]]-ymin)*yunit))
				except:
					self.shapes[i] = self.widgets['canvas'].create_line((fields[i]-xmin)*xunit,self.gheight-((self.data[fields[i]]-ymin)*yunit),(fields[i+1]-xmin)*xunit,self.gheight-((self.data[fields[i+1]]-ymin)*yunit), fill=TkLineGraph.colours['line'], activefill="white")
		else:
			try:
				self.shapes['default']
			except:
				self.shapes['default'] = self.widgets['canvas'].create_line(0,(yrange*0.5)*yunit,(xrange)*xunit,(yrange*0.5)*yunit, fill=TkLineGraph.colours['line'], activefill="white")
## UI for bar graphs
class TkBarGraph():
	def __init__(self, parent, colours={}, width=100, height=30, grange={'min': 0, 'max': 100}, horizontal=True):
		""" initializes the attributes for a bar graph
		
		@param parent
		@param colours
		@param width
		@param height
		@param grange
		@param horizontal
		"""
		self.colours = colours
		self.widget = Frame(parent, bg=self.colours['bg'])
		self.value = grange['min']
		self.grange = grange
		self.width = width
		self.height = height
		self.horizontal = horizontal
		self.setup()
	def setup(self):
		""" creates a canvas for the graph
		"""
		self.widgets = {}
		self.shapes = {}
		self.widgets['canvas'] = Tkinter.Canvas(self.widget, width=self.width, height=self.height-2, bg=self.colours['bg'], highlightthickness=2, highlightbackground=self.colours['greyborder'])
		self.widgets['canvas'].grid(column=0,row=0, sticky='EW', pady=2)
		if(self.horizontal):
			self.barunit = float(self.width)/(float(self.grange['max'])-float(self.grange['min']))
			self.shapes['bar'] = self.widgets['canvas'].create_rectangle((0,0,self.width, self.height), fill=self.colours['graphbar'])
		else:
			self.barunit = float(self.height)/(float(self.grange['max'])-float(self.grange['min']))
			self.shapes['bar'] = self.widgets['canvas'].create_rectangle((0,0, self.width, self.height), fill=self.colours['graphbar'])
	def update(self, value):
		""" updates the width or height of the bar in the graph
		
		@param value
		"""
		if(self.horizontal):
			self.widgets['canvas'].coords(self.shapes['bar'], 0,0,int(self.barunit*value), self.height)
		else:
			self.widgets['canvas'].coords(self.shapes['bar'], 0,self.barunit*value,self.width,self.height)
## UI for ii charts
class TkPiChart():
	def __init__(self, parent, data, colours={}, width=100, height=100, total = 100, label=None, rcolour=None):
		""" initializes the attributes for a pi chart
		
		@param parent
		@param data
		@param colours
		@param width
		@param height
		@param total
		@param label
		@param rcolour
		"""
		self.widget = Frame(parent)
		self.data = data
		self.colours = colours
		self.width = width
		self.height = height
		self.total = float(total)
		self.rcolour = rcolour
		self.unit = 360.0 / self.total
		self.label = label
		self.outercoords = 0,0,self.width,self.height
		self.setup()
	def setup(self):
		""" creates a canvas for the pi chart
		"""
		self.widgets = {}
		self.shapes = {}
		self.widgets['canvas'] = Tkinter.Canvas(self.widget, width=self.width, height=self.height, bg=self.colours['bg'], highlightthickness=0)
		self.widgets['canvas'].grid(column=0,row=0, sticky='EW')
		coords = self.width*0.25,self.height*0.25,self.width*0.75,self.height*0.75
		self.shapes['centre'] = self.widgets['canvas'].create_oval(coords, fill=self.colours['bg'], tags='centre')
		self.shapes['label'] = self.widgets['canvas'].create_text(self.width*0.5, self.height*0.5, text=self.label, fill=self.colours['consolefg'], tags='label')
		self.update()
	def update(self, data = None):
		""" converts the data into section of the pi chart
		
		@param data
		"""
		if(data != None):
			self.data = data
		initialangle = 0
		currentangle = initialangle
		for k in self.data.keys():
			if(self.data[k] >= 0 and self.data[k] <= 100):
				val = self.unit*self.data[k]
				try:
					self.widgets['canvas'].itemconfig(self.shapes[k], start=currentangle, extent=val)
				except:
					self.shapes[k] = self.widgets['canvas'].create_arc(self.outercoords, fill=k, start=currentangle, extent=val)
				currentangle += val
		if(isinstance(self.rcolour,str)):
			r = currentangle-initialangle
			if(r > 0):
				try:
					self.widgets['canvas'].itemconfig(self.shapes[self.rcolour], start=currentangle, extent=360-r)
				except:
					self.shapes[self.rcolour] = self.widgets['canvas'].create_arc(self.outercoords, fill=self.rcolour, start=currentangle, extent=r)
		self.widgets['canvas'].tag_raise('centre')
		self.widgets['canvas'].tag_raise('label')