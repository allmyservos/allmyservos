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
import os, Tkinter
from __bootstrap import AmsEnvironment
from xml.dom import minidom
from Tkinter import *

## UI generator for help files
class TkHtml(object):
	def __init__(self, gui, base='help'):
		""" for parsing html
		
		@param gui
		@param base
		"""
		self.colours = gui.colours
		self.fonts = gui.fonts
		self.images = {}
		self.base = os.path.join(AmsEnvironment.AppPath(), base)
		self.buildIndex()
	def buildIndex(self):
		""" gets a list of available HTML files
		"""
		self.index = {}
		files = os.listdir(self.base)
		files = [ x for x in files if x.endswith('.html') ]
		for f in files:
			parts = os.path.splitext(f)
			self.index[parts[0]] = f
	def getHtml(self, parent, name):
		""" returns a Tkinter frame containing the parsed HTML
		
		@param parent
		@param name
		"""
		view = self.viewWrapper(parent)
		try:
			filepath = os.path.join(self.base, self.index[name])
		except:
			v = self.view404(view)
			v.grid(column=0, row=0, sticky='W')
			return view
		xmldoc = minidom.parse(filepath)
		base = xmldoc.getElementsByTagName('html')[0]
		body = base.getElementsByTagName('body')[0]
		row = 0
		for c in body.childNodes:
			if c.nodeType == c.ELEMENT_NODE:
				if(c.tagName.lower() == 'h1'):
					v = self.headingView(view, c.firstChild.nodeValue)
					v.grid(column=0, row=row, pady=5, sticky='W')
					row += 1
				elif(c.tagName.lower() == 'h2'):
					v = self.headingView(view, c.firstChild.nodeValue, 2)
					v.grid(column=0, row=row, pady=5, sticky='W')
					row += 1
				elif(c.tagName.lower() == 'p'):
					v = self.paragraphView(view, c.firstChild.nodeValue)
					v.grid(column=0, row=row, pady=5, sticky='W')
					row += 1
				elif(c.tagName.lower() == 'img'):
					v = self.imageView(view, os.path.join(self.base, c.getAttribute('src')))
					v.grid(column=0, row=row, padx=10, pady=10, sticky='EW')
					row += 1
		return view
	def viewWrapper(self, parent):
		""" partial view - just a frame
		
		@param parent
		"""
		w = Tkinter.Frame(parent, borderwidth=0, highlightthickness=0, bg=self.colours['bg'])
		return w
	def headingView(self, parent, text, type = 1):
		""" partial view - heading label
		
		@param parent
		@param text
		@param type
		"""
		w = Tkinter.Label(parent,text=str(text), bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'], anchor=NW)
		if(type == 2):
			w.configure(font = self.fonts['heading2'])
		return w
	def paragraphView(self, parent, text):
		""" partial view - paragraph label
		
		@param parent
		@param text
		"""
		w = Tkinter.Label(parent,text=str(text), bg=self.colours['bg'], fg=self.colours['valuefg'], anchor=NW)
		return w
	def imageView(self, parent, filepath):
		""" partial view - image label
		
		@param parent
		@param filepath
		"""
		self.images[filepath] = Tkinter.PhotoImage(file=filepath)
		w = Tkinter.Label(parent, bg=self.colours['bg'], fg=self.colours['valuefg'], text='image', image=self.images[filepath])
		return w
	def view404(self, parent):
		""" view - default for missing html
		
		@param parent
		"""
		w = Tkinter.Frame(parent, borderwidth=0, highlightthickness=0, bg=self.colours['bg'])
		row = 0
		v = self.headingView(w, 'Not Found')
		v.grid(column=0, row=row, sticky='W')
		row += 1
		v = self.paragraphView(w, '404 File Not Found')
		v.grid(column=0, row=row, sticky='W')
		return w