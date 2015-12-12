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
import datetime
from TkBlock import *

class Footer(TkBlock):
	def __init__(self, parent, gui, **options):
		'''
		a simple frame containing footer information
		'''
		super(Footer,self).__init__(parent, gui, **options)
		self.open() #automatically added to layout
		year = datetime.date.today().year
		grid = { 'copyright': [0,0], 'buttons': [1,0] }
		if(self.gui.theme.profile != None):
			if(self.gui.theme.profile['name'] == 'slim'):
				grid = { 'copyright': [0,0], 'buttons': [0,1] } #accounts for slim profile
		self.widgets['copyrightLabel'] = Tkinter.Label(self.widget,text='AllMyServos Copyright {0}  - Distributed under GNU GPL License - Want to help out? '.format(year), bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['copyrightLabel'].grid(column=grid['copyright'][0],row=grid['copyright'][1],sticky='EW')
		self.widgets['fframe'] = Frame(self.widget,bg=self.colours['bg'])
		self.widgets['fframe'].grid(column=grid['buttons'][0],row=grid['buttons'][1],sticky='EW')
		self.widgets['donateButton'] = Tkinter.Button(self.widgets['fframe'],text=u"Donate", bg=self.colours['buttonbg'], fg=self.colours['headingfg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.gui.widgets['main']['TkHelpManager'].OnDonateClick)
		self.widgets['donateButton'].grid(column=1,row=0,sticky='EW')
		self.widgets['watchButton'] = Tkinter.Button(self.widgets['fframe'],text=u"Subscribe", bg=self.colours['buttonbg'], fg=self.colours['headingfg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.gui.widgets['main']['TkHelpManager'].OnSubscribeClick)
		self.widgets['watchButton'].grid(column=2,row=0,sticky='EW')
		self.widgets['fframe'].columnconfigure(0, weight=1)
		self.widgets['fframe'].columnconfigure(4, weight=1)
		self.widgets['fframe'].rowconfigure(0, weight=1)