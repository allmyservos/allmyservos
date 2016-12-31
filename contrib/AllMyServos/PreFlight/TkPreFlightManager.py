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
import os, Tkinter, PreFlight
from __bootstrap import AmsEnvironment
from Tkinter import *
from TkBlock import TkBlock, TkPage

## UI for pre flight checks
class TkPreFlightManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes TkPreFlightManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkPreFlightManager,self).__init__(parent, gui, **options)
		self.report = PreFlight.PreFlight.report()
	def setup(self):
		""" setup gui menu
		"""
		try:
			self.gui.menus['file']
		except:
			self.gui.menus['file'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="File", menu=self.gui.menus['file'])
		self.gui.menus['file'].insert_command(index=1, label="Exit", command=self.OnExitClick)
	
	#=== VIEWS ===#
	def checks(self):
		""" view - list checks
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Pre Flight Checks', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='I2C Communication Requirements', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		#i2c interface
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='1. Interfaces', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='The following interfaces must be enabled in /boot/config.txt:', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['iframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['iframe'].grid(column=0,row=self.gridrow, pady=20, sticky='EW')
		
		self.widgets['statusLabel'] = Tkinter.Label(self.widgets['iframe'],text='Status', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['statusLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['iframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['nameLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		self.widgets['entryLabel'] = Tkinter.Label(self.widgets['iframe'],text='Entry', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['entryLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		
		for k, v in self.report['interfaces'].items():
			self.widgets['status'+k] = Tkinter.Label(self.widgets['iframe'],image=self.gui.images['notice'] if v['enabled'] else self.gui.images['error'], bg=self.colours['rowbg'], fg=self.colours['valuefg'], height=30)
			self.widgets['status'+k].grid(column=0,row=self.gridrow, ipadx=20, sticky='EW')
			self.widgets['name'+k] = Tkinter.Label(self.widgets['iframe'],text=k, bg=self.colours['rowbg'], fg=self.colours['valuefg'], height=2)
			self.widgets['name'+k].grid(column=1,row=self.gridrow, ipadx=20, sticky='EW')
			self.widgets['entry'+k] = Tkinter.Label(self.widgets['iframe'],text='dtparam={0}=on'.format(v['interface']), bg=self.colours['rowbg'], fg=self.colours['valuefg'], height=2)
			self.widgets['entry'+k].grid(column=2,row=self.gridrow, ipadx=20, sticky='EW')
			self.gridrow += 1
			
		#modules
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='2. Modules', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='The following entries must appear in "/etc/modules":', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['mframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['mframe'].grid(column=0,row=self.gridrow, pady=20, sticky='EW')
		
		self.widgets['statusLabel'] = Tkinter.Label(self.widgets['mframe'],text='Status', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['statusLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['mframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['nameLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['mframe'],text='Info', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['infoLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		rowcount = 1
		for k, v in self.report['modules'].iteritems():
			rowcolour = self.colours['rowbg']
			if(rowcount % 2 == 0):
				rowcolour = self.colours['rowaltbg']
			rowcount += 1
			self.widgets['status'+k] = Tkinter.Label(self.widgets['mframe'],image=self.gui.images['notice'] if v else self.gui.images['error'], bg=rowcolour, fg=self.colours['valuefg'], height=30)
			self.widgets['status'+k].grid(column=0,row=self.gridrow, ipadx=20, sticky='EW')
			self.widgets['name'+k] = Tkinter.Label(self.widgets['mframe'],text=k, bg=rowcolour, fg=self.colours['valuefg'], height=2)
			self.widgets['name'+k].grid(column=1,row=self.gridrow, ipadx=20, sticky='EW')
			self.widgets['info'+k] = Tkinter.Label(self.widgets['mframe'],text='present' if v else 'missing', bg=rowcolour, fg=self.colours['valuefg'], height=2)
			self.widgets['info'+k].grid(column=2,row=self.gridrow, ipadx=20, sticky='EW')
			self.gridrow += 1
		
		self.gridrow += 1
		#blacklist
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='3. Blacklist', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='The following entries must only appear as a comment in "/etc/modprobe.d/raspi-blacklist.conf":', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		self.widgets['bframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['bframe'].grid(column=0,row=self.gridrow, pady=20, sticky='EW')
		
		self.widgets['statusLabel'] = Tkinter.Label(self.widgets['bframe'],text='Status', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['statusLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['bframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['nameLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['bframe'],text='Info', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['infoLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		rowcount = 1
		for k, v in self.report['blacklist'].iteritems():
			rowcolour = self.colours['rowbg']
			if(rowcount % 2 == 0):
				rowcolour = self.colours['rowaltbg']
			rowcount += 1
			self.widgets['status'+k] = Tkinter.Label(self.widgets['bframe'],image=self.gui.images['notice'] if v else self.gui.images['error'], bg=rowcolour, fg=self.colours['valuefg'], height=30)
			self.widgets['status'+k].grid(column=0,row=self.gridrow, ipadx=20, sticky='EW')
			self.widgets['name'+k] = Tkinter.Label(self.widgets['bframe'],text=k, bg=rowcolour, fg=self.colours['valuefg'], height=2)
			self.widgets['name'+k].grid(column=1,row=self.gridrow, ipadx=20, sticky='EW')
			self.widgets['info'+k] = Tkinter.Label(self.widgets['bframe'],text='missing / commented' if v else 'present', bg=rowcolour, fg=self.colours['valuefg'], height=2)
			self.widgets['info'+k].grid(column=2,row=self.gridrow, ipadx=20, sticky='EW')
			self.gridrow += 1
		
		self.gridrow += 1
		#update / upgrade
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='4. Update / Upgrade', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='The following commands will be run before installing dependencies:', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		self.widgets['uframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['uframe'].grid(column=0,row=self.gridrow, pady=20, sticky='EW')
		
		self.widgets['statusLabel'] = Tkinter.Label(self.widgets['uframe'],text='Status', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['statusLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['commandLabel'] = Tkinter.Label(self.widgets['uframe'],text='Command', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['commandLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		rowcount = 1
		for p in self.report['prep']:
			rowcolour = self.colours['rowbg']
			if(rowcount % 2 == 0):
				rowcolour = self.colours['rowaltbg']
			rowcount += 1
			self.widgets['status'+k] = Tkinter.Label(self.widgets['uframe'],image=self.gui.images['warning'], bg=rowcolour, fg=self.colours['valuefg'], height=30)
			self.widgets['status'+k].grid(column=0,row=self.gridrow, ipadx=20, sticky='EW')
			self.widgets['command'+k] = Tkinter.Label(self.widgets['uframe'],text=' '.join(p['command']), bg=rowcolour, fg=self.colours['valuefg'], height=2)
			self.widgets['command'+k].grid(column=1,row=self.gridrow, ipadx=20, sticky='EW')
		
			self.gridrow += 1
		#dependencies
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='5. Dependencies', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='The following dependencies must be installed:', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		self.widgets['pframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['pframe'].grid(column=0,row=self.gridrow, pady=20, sticky='EW')
		
		self.widgets['statusLabel'] = Tkinter.Label(self.widgets['pframe'],text='Status', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['statusLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['pframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['nameLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		self.widgets['installerLabel'] = Tkinter.Label(self.widgets['pframe'],text='Installer', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['installerLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['pframe'],text='Info', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['infoLabel'].grid(column=3,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		rowcount = 1
		for d in self.report['dependencies']:
			rowcolour = self.colours['rowbg']
			if(rowcount % 2 == 0):
				rowcolour = self.colours['rowaltbg']
			rowcount += 1
			self.widgets['status'+k] = Tkinter.Label(self.widgets['pframe'],image=self.gui.images['notice'] if d['installed'] else self.gui.images['error'], bg=rowcolour, fg=self.colours['valuefg'], height=30)
			self.widgets['status'+k].grid(column=0,row=self.gridrow, ipadx=20, sticky='EW')
			self.widgets['name'+k] = Tkinter.Label(self.widgets['pframe'],text=d['package'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
			self.widgets['name'+k].grid(column=1,row=self.gridrow, ipadx=20, sticky='EW')
			self.widgets['installer'+k] = Tkinter.Label(self.widgets['pframe'],text=d['installer'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
			self.widgets['installer'+k].grid(column=2,row=self.gridrow, ipadx=20, sticky='EW')
			self.widgets['info'+k] = Tkinter.Label(self.widgets['pframe'],text='installed' if d['installed'] else 'not installed', bg=rowcolour, fg=self.colours['valuefg'], height=2)
			self.widgets['info'+k].grid(column=3,row=self.gridrow, ipadx=20, sticky='EW')
			self.gridrow += 1
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='Click accept to make these configuration changes automatically and the Pi will reboot.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='Reopen AllMyServos and this message should not appear.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='This may take a while. Please wait for processing to complete.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		self.widgets['optionframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionframe'],text='Exit', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['acceptlabel'] = Tkinter.Label(self.widgets['optionframe'],text="Accept", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['acceptlabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['back'] = Tkinter.Button(self.widgets['optionframe'],text=u"Back", image=self.images['back'], command=self.OnExitClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['confirmbutton'] = Tkinter.Button(self.widgets['optionframe'],text=u"Accept", image=self.images['accept'], command=self.OnCorrectClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['confirmbutton'].grid(column=1,row=self.gridrow)
	
	#=== ACTIONS ===#
	def OnChecksClick(self):
		""" action - display checks
		"""
		self.checks()
	def OnCorrectClick(self):
		""" action - perform corrections
		"""
		PreFlight.PreFlight.configure()
	def OnExitClick(self):
		""" action - exit the gui
		"""
		self.gui.quit()
## UI for pre flight logo
class TkPreFlightLogo(TkBlock):
	def __init__(self, parent, gui, **options):
		""" Initializes TkPreFlightLogo object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkPreFlightLogo,self).__init__(parent, gui, **options)
		self.view()
	def view(self):
		""" view - display logo
		"""
		self.open()
		self.logo = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'pre-flight','vwave.gif'))
		self.widgets['frameLabel'] = Tkinter.Label(self.widget, text="logo", image = self.logo, anchor=S, bg=self.colours['bg'], fg=self.colours['headingfg'], highlightthickness=0)
		self.widgets['frameLabel'].grid(column=0,row=0,sticky='S')
		self.widgets['frameLabel'].logo = self.logo
## UI for pre flight screens
class TkPreFlightScreens(TkBlock):
	def __init__(self, parent, gui, **options):
		""" Initializes TkPreFlightScreens object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkPreFlightScreens,self).__init__(parent, gui, **options)
		self.view()
	def view(self):
		""" view - display flight screens
		"""
		self.open()
		self.logo = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'pre-flight','ui-screens.gif'))
		self.widgets['frameLabel'] = Tkinter.Label(self.widget, text="logo", image = self.logo, anchor=S, bg=self.colours['bg'], fg=self.colours['headingfg'], highlightthickness=0)
		self.widgets['frameLabel'].grid(column=0,row=0,sticky='S')
		self.widgets['frameLabel'].logo = self.logo