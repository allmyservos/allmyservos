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
import Tkinter, sys
from StringIO import StringIO
from TkBlock import *
from Tkinter import *
from Setting import *

## UI for console output
class TkConsole(TkBlock):
	def __init__(self, parent, gui, **options):
		""" Initializes the TkConsole object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkConsole,self).__init__(parent, gui, **options)
		if(Setting.get('console_enabled',True)): 
			self._old_stdout = sys.stdout #retain a reference to the original stdout callback
			self._old_stderr = sys.stderr #retain a reference to the original stderr callback
			self.logger = Logger(self._old_stdout, self._old_stderr, Setting.get('console_use_old',True)) #initialize the logger
			sys.stdout = self.logger #update stdout
			sys.stderr = self.logger #update stderr
			self.addConsole()
	def addConsole(self):
		""" view - console output
		"""
		self.gridrow = 0
		
		self.widgets['infoFrame'] = Tkinter.Frame(self.widget, bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['infoFrame'].grid(column=0,row=0,sticky='WE')
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['infoFrame'],text='Console', anchor=NW, borderwidth=1, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['frameLabel'].grid(column=0,row=0,sticky='WE')
		
		self.variables['enabled'] = Tkinter.BooleanVar()
		self.variables['enabled'].set(Setting.get('console_enabled', False))
		self.widgets['enabledentry'] = Tkinter.Checkbutton(self.widgets['infoFrame'], text="Enabled", variable=self.variables['enabled'], command=self.OnToggleConsoleClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['enabledentry'].grid(column=1,row=0,sticky='E')
		
		self.variables['terminal'] = Tkinter.BooleanVar()
		self.variables['terminal'].set(Setting.get('console_use_old', True))
		self.widgets['terminalentry'] = Tkinter.Checkbutton(self.widgets['infoFrame'], text="Copy to Terminal", variable=self.variables['terminal'], command=self.OnToggleTerminalClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['terminalentry'].grid(column=2,row=0,sticky='E')
		
		self.widgets['infoData'] = Tkinter.Label(self.widgets['infoFrame'], textvariable = self.logger.output, anchor=W, justify="left", bg=self.colours['bg'], fg=self.colours['consolefg'])
		self.widgets['infoData'].grid(column=0,row=1,columnspan=3,sticky='WE')
	def OnToggleConsoleClick(self):
		""" action - enable / disable console
		"""
		Setting.set('console_enabled', self.variables['enabled'].get())
	def OnToggleTerminalClick(self):
		""" action - enable / disable copying to the terminal
		"""
		Setting.set('console_use_old', self.variables['terminal'].get())
## Custom stdout handler
class Logger(StringIO):
	def __init__(self, old_stdout, old_stderr, useold):
		""" Initializes the Logger object
		Extends StringIO in order to capture stdout and stderr
		
		@param old_stdout
		@param old_stderr
		@param useold
		"""
		StringIO.__init__(self) #overriding object must implement StringIO
		self.output = Tkinter.StringVar()
		self.useold = useold
		self.old_stdout = old_stdout
		self.old_stderr = old_stderr
	def write(self, value):
		''' capture and reverse console output
		'''
		try:
			StringIO.write(self,value)
			self.output.set(value+self.output.get()) #reverse console output order (newest on top)
			if(self.useold):
				self.old_stdout.write(value) #repeat to command line
		except Exception as e:
			pass