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
from TkBlock import TkBlock

class Logo(TkBlock):
	def __init__(self, parent, gui, **options):
		super(Logo,self).__init__(parent, gui, **options)
		self.open()
		self.widgets['logoLabel'] = Tkinter.Label(self.widget,text='AllMyServos', image = self.gui.images['robot'], bg=self.gui.colours['bg'], fg=self.gui.colours['fg'])
		self.widgets['logoLabel'].grid(column=0,row=0,sticky='EW')
		if(self.gui.theme.profile != None):
			if(self.gui.theme.profile['name'] == 'slim'):
				self.widget.rowconfigure(0, weight=1)