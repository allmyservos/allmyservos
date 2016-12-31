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
import Tkinter, Keyboard, Motion
from Tkinter import *
from TkBlock import *

## UI for keyboard
class TkKeyboardManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes TkKeyboardManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkKeyboardManager,self).__init__(parent, gui, **options)
		self.scheduler = gui.scheduler
		self.specification = gui.specification
		self.asciimap = Keyboard.AsciiMap()
		try:
			self.gui.kbthread
		except:
			self.gui.kbthread = Keyboard.KeyboardThread(self.specification, self.gui.motionScheduler, self.gui.scheduler, not Setting.get('kb_use_tk_callback', True))
		self.kbthread = self.gui.kbthread
		self.stopped = not Setting.get('kb_autostart', False)
		if(Setting.get('kb_autostart', False)):
			self.OnStartClick()
	def setup(self):
		""" setup gui menu
		"""
		self.gui.menus['kb'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		self.gui.menus['kb'].add_command(label="New Map", command=self.OnAddMapClick)
		self.gui.menus['kb'].add_separator()
		self.gui.menus['kb'].add_command(label="Manage", command=self.OnListMapsClick)
		self.addMenu(label="Keyboard", menu=self.gui.menus['kb'])
	
	#=== VIEWS ===#
	def serviceManager(self):
		""" view - service manager
		"""
		self.widgets['servicelabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyboard / Service', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['servicelabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['statusLabel'] = Tkinter.Label(self.widgets['tframe'],text='Status', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['statusLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.variables['status'] = Tkinter.StringVar()
		self.widgets['statusdata'] = Tkinter.Label(self.widgets['tframe'],textvariable=self.variables['status'], bg=self.colours['bg'], fg=self.colours['fg'], font=self.fonts['heading2'])
		self.widgets['statusdata'].grid(column=0,row=self.gridrow,sticky='EW')
		
		if(self.stopped == False):
			self.variables['status'].set('Running')
		else:
			self.variables['status'].set('Stopped')
		
		self.widgets['start'] = Tkinter.Button(self.widgets['tframe'],text=u"Start", image=self.images['play'], command=self.OnStartClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['start'].grid(column=1,row=self.gridrow)
		
		self.widgets['stop'] = Tkinter.Button(self.widgets['tframe'],text=u"Stop", image=self.images['stop'], command=self.OnStopClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['stop'].grid(column=2,row=self.gridrow)
		
		if(self.stopped == False):
			self.widgets['start'].configure(state='disabled')
		else:
			self.widgets['stop'].configure(state='disabled')
		
		self.variables['autostart'] = Tkinter.BooleanVar()
		self.variables['autostart'].set(Setting.get('kb_autostart', False))
		self.widgets['autostartentry'] = Tkinter.Checkbutton(self.widgets['tframe'], text="Autostart", variable=self.variables['autostart'], command=self.OnToggleAutostartClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['autostartentry'].grid(column=3,row=self.gridrow)
	
	def listMaps(self):
		""" view - list maps
		"""
		self.open()

		self.serviceManager()
		
		self.gridrow += 1
		
		self.widgets['kblabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyboard / Key Maps', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['kblabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['addmap'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Map", image=self.images['add'], command=self.OnAddMapClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addmap'].grid(column=4,row=self.gridrow)
		
		self.gridrow += 1

		rowcolour = self.colours['rowbg']
		if(len(self.maps) > 0):
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['tframe'],text='Edit', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['editLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['mappingLabel'] = Tkinter.Label(self.widgets['tframe'],text='Mapping', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['mappingLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['activeLabel'] = Tkinter.Label(self.widgets['tframe'],text='Activate', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['activeLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['tframe'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['deleteLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			rowcount = 1
			for k, v in self.maps.items():
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['nameData'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=v['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['nameData'+str(self.gridrow)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['editButton'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnEditMapClick(x))
				self.widgets['editButton'+str(self.gridrow)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['mappingButton'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Mappings", image=self.images['key'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnListMappingsClick(x))
				self.widgets['mappingButton'+str(self.gridrow)].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['activeButton'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Activate", image=self.images['play'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnActivateMapClick(x))
				self.widgets['activeButton'+str(self.gridrow)].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['deleteButton'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Delete", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnDeleteMapClick(x))
				self.widgets['deleteButton'+str(self.gridrow)].grid(column=4,row=self.gridrow,sticky='EW')
				if(v['active'] == True):
					self.widgets['activeButton'+str(self.gridrow)].configure(state='disabled')
				else:
					self.widgets['activeButton'+str(self.gridrow)].configure(state='normal')
				self.gridrow += 1
		else:
			self.widgets['nomapslabel'] = Tkinter.Label(self.widgets['tframe'],text="There are currently no key maps", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nomapslabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.gridrow += 1

	def editMap(self):
		""" view - edit maps
		"""
		self.open()
		self.widgets['kblabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyboard / Key Maps / Edit', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['kblabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.variables['name'] = Tkinter.StringVar()
		if(self.map['name'] != ''):
			self.variables['name'].set(self.map['name'])
		self.widgets['nameentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['name'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['nameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.gridrow = 0
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.map['name'] != ''):
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['deleteLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnListMapsClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['savemap'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Map", image=self.images['save'], command=self.OnSaveMapClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['savemap'].grid(column=1,row=self.gridrow)
		if(self.map['name'] != ''):
			self.widgets['deletemap'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete Map", image=self.images['delete'], command=self.OnDeleteMapClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['deletemap'].grid(column=2,row=self.gridrow)
	def deleteMap(self):
		""" view - delete map
		"""
		self.open()
		
		self.widgets['kblabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyboard / Key Maps / Delete', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['kblabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['infolabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this map?', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['infolabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['nameData'] = Tkinter.Label(self.widgets['tframe'],text=self.map['name'], bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['nameData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['mappingsLabel'] = Tkinter.Label(self.widgets['tframe'],text='Mappings', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['mappingsLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['mappingsData'] = Tkinter.Label(self.widgets['tframe'],text=len(self.map['mappings']), bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['mappingsData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['infolabel'] = Tkinter.Label(self.widgets['tframe'],text='This map and all associated mappings will be deleted.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['infolabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.gridrow = 0
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['confirmLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['confirmLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnMapBackClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['confirm'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Confirm", image=self.images['accept'], command=self.OnConfirmDeleteMapClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['confirm'].grid(column=1,row=self.gridrow)
	def listMappings(self):
		""" view - list mappings
		"""
		self.open()
		self.gridrow = 0
		self.widgets['kblabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyboard / Key Map / Edit / Key Mapping', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['kblabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['addmapping'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Mapping", image=self.images['add'], command=self.OnAddMappingClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addmapping'].grid(column=5,row=self.gridrow)
		self.gridrow += 1
		if(any(self.map['mappings'])):
			self.widgets['asciiLabel'] = Tkinter.Label(self.widgets['tframe'],text='Ascii', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['asciiLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['hexLabel'] = Tkinter.Label(self.widgets['tframe'],text='Hex', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['hexLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['actionLabel'] = Tkinter.Label(self.widgets['tframe'],text='Action', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['actionLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['commandLabel'] = Tkinter.Label(self.widgets['tframe'],text='Command', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['commandLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['tframe'],text='Edit', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['editLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['tframe'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['deleteLabel'].grid(column=5,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			rowcount = 1
			for m in self.map['mappings'].values():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['asciiData'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=m['ascii'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['asciiData'+str(self.gridrow)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['hexData'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=m['hex'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['hexData'+str(self.gridrow)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['actionData'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=m['action'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['actionData'+str(self.gridrow)].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['commandData'+str(self.gridrow)] = Tkinter.Label(self.widgets['tframe'],text=m['command'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['commandData'+str(self.gridrow)].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['editButton'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = m['hex']:self.OnEditMappingClick(x))
				self.widgets['editButton'+str(self.gridrow)].grid(column=4,row=self.gridrow,sticky='EW')
				self.widgets['deleteButton'+str(self.gridrow)] = Tkinter.Button(self.widgets['tframe'],text=u"Delete", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = m['hex']:self.OnDeleteMappingClick(x))
				self.widgets['deleteButton'+str(self.gridrow)].grid(column=5,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['nomappingslabel'] = Tkinter.Label(self.widgets['tframe'],text="This map currently has no key mappings", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nomappingslabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.gridrow = 0
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnListMapsClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
	def editMapping(self):
		""" view - edit mapping
		"""
		self.open()
		
		self.widgets['kblabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyboard / Key Map / Edit / Key Mapping / Edit', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['kblabel'].grid(column=0,row=self.gridrow, columnspan=4, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['keyLabel'] = Tkinter.Label(self.widgets['tframe'],text='Key', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['keyLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.variables['hex'] = Tkinter.StringVar()
		if(self.mapping['hex'] != ''):
			self.variables['hex'].set(self.mapping['hex'])
		self.widgets['hexentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['hex'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['hexentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['ascii'] = Tkinter.StringVar()
		if(self.mapping['ascii'] != ''):
			self.variables['ascii'].set(self.mapping['ascii'])
		self.widgets['asciiData'] = Tkinter.Label(self.widgets['tframe'],textvariable=self.variables['ascii'], bg=self.colours['bg'], height=2, fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['asciiData'].grid(column=2,row=self.gridrow,sticky='EW', padx = 10)
		self.widgets['captureButton'] = Tkinter.Button(self.widgets['tframe'],text=u"Capture", image=self.images['process'], command=self.OnKeyCaptureClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['captureButton'].grid(column=3,row=self.gridrow)
		self.gridrow += 1
		
		self.widgets['actionLabel'] = Tkinter.Label(self.widgets['tframe'],text='Action', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['actionLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.variables['action'] = Tkinter.StringVar()
		if(self.mapping['action'] != ''):
			self.variables['action'].set(self.mapping['action'])

		self.widgets['actionentry'] = Tkinter.OptionMenu(self.widgets['tframe'],self.variables['action'], 'motion', 'chain', 'relax', 'default')
		self.widgets['actionentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
		self.widgets['actionentry'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['commandLabel'] = Tkinter.Label(self.widgets['tframe'],text='Command', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['commandLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.variables['command'] = Tkinter.StringVar()
		if(self.mapping['command'] != ''):
			self.variables['command'].set(self.mapping['command'])
		self.widgets['commandentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['command'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['commandentry'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=4, sticky='EW')
		self.gridrow = 0
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.mapping['hex'] != ''):
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['deleteLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=lambda x = self.map['name']:self.OnListMappingsClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['savemap'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Mapping", image=self.images['save'], command=self.OnSaveMappingClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['savemap'].grid(column=1,row=self.gridrow)
		if(self.mapping['hex'] != ''):
			self.widgets['deletemap'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete Mapping", image=self.images['delete'], command=lambda x = self.mapping['hex']:self.OnDeleteMappingClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['deletemap'].grid(column=2,row=self.gridrow)
	def deleteMapping(self):
		""" view - delete mapping
		"""
		self.open()
		
		self.widgets['kblabel'] = Tkinter.Label(self.widgets['tframe'],text='Keyboard / Key Map / Edit / Key Mapping / Delete', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['kblabel'].grid(column=0,row=self.gridrow, columnspan=4,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['infolabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this key mapping?', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['infolabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['asciiLabel'] = Tkinter.Label(self.widgets['tframe'],text='Ascii', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['asciiLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['asciiData'] = Tkinter.Label(self.widgets['tframe'],text=self.mapping['ascii'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['asciiData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['hexLabel'] = Tkinter.Label(self.widgets['tframe'],text='Hex', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['hexLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['hexData'] = Tkinter.Label(self.widgets['tframe'],text=self.mapping['hex'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['hexData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['actionLabel'] = Tkinter.Label(self.widgets['tframe'],text='Action', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['actionLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['actionData'] = Tkinter.Label(self.widgets['tframe'],text=self.mapping['action'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['actionData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['commandLabel'] = Tkinter.Label(self.widgets['tframe'],text='Command', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['commandLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['commandData'] = Tkinter.Label(self.widgets['tframe'],text=self.mapping['command'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['commandData'].grid(column=1,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.gridrow = 0
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['confirmLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['confirmLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnMappingBackClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['confirm'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Confirm", image=self.images['accept'], command=self.OnConfirmDeleteMappingClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['confirm'].grid(column=1,row=self.gridrow)
	
	#=== ACTIONS ===#
	def OnStartClick(self):
		""" action - start kb service
		"""
		self.stopped = False
		try:
			self.widgets['start'].configure(state='disabled')
			self.widgets['stop'].configure(state='normal')
			self.variables['status'].set('Running')
		except:
			pass
		self.kbthread.start()
		if(Setting.get('kb_use_tk_callback', True)):
			self.widget.bind_all('<Key>',self.inputTkCapture)
		else:
			self.widget.unbind_all('<Key>')
	def OnStopClick(self):
		""" action - stop kb service
		"""
		self.stopped = True
		try:
			self.widgets['start'].configure(state='normal')
			self.widgets['stop'].configure(state='disabled')
			self.variables['status'].set('Stopped')
		except:
			pass
		if(Setting.get('kb_use_tk_callback', True)):
			self.widget.unbind_all('<Key>')
		self.kbthread.stop()
	def OnToggleAutostartClick(self):
		""" action - toggle kb autostart
		"""
		self.autostart = Setting.set('kb_autostart',self.variables['autostart'].get())
	
	def OnListMapsClick(self):
		""" action - displays the list of maps
		"""
		self.maps = self.specification.keyboard
		self.listMaps()
	def OnAddMapClick(self):
		""" action - displays add map page
		"""
		self.map = {
			'name': '',
			'active': False,
			'mappings': {}
		}
		self.editMap()
	def OnEditMapClick(self, index):
		""" action - displays edit map page
		
		@param index
		"""
		self.map = self.specification.keyboard[index]
		self.editMap()
	def OnSaveMapClick(self):
		""" action - saves map
		"""
		name = self.variables['name'].get()
		if (name == ''):
			self.notifier.addNotice('Please specify a name', 'warning')
			return
		if (self.map['name'] == '' and name in self.specification.keyboard.keys()):
			self.notifier.addNotice('A map with that name already exists', 'warning')
			return
		if (self.map['name'] != '' and name != self.map['name']):
			del(self.specification.keyboard[self.map['name']]) #remove from original index
		self.map['name'] = name
		self.map['active'] = False if any([x for x in self.specification.keyboard.values() if  x['active'] == True]) else True
		self.specification.keyboard[name] = self.map
		self.specification.save()
		self.notifier.addNotice('Map "{0}" has been saved'.format(name))
		self.listMaps()
	def OnDeleteMapClick(self, index):
		""" action - display delete map page
		
		@param index
		"""
		if (index in self.specification.keyboard.keys()):
			self.map = self.specification.keyboard[index]
			self.deleteMap()
	def OnConfirmDeleteMapClick(self):
		""" action - delete map
		"""
		if (hasattr(self, 'map')):
			del(self.specification.keyboard[self.map['name']])
			self.specification.save()
			self.notifier.addNotice('Map deleted')
			self.listMaps()
	def OnMapBackClick(self):
		""" action - back from map page
		"""
		self.listMaps()
	def OnActivateMapClick(self, index):
		""" action - activate key map
		
		@param index
		"""
		for k, v in self.specification.keyboard.items():	
			if (v['active'] == True):
				v['active'] = False
			if (k == index):
				v['active'] = True
		self.specification.save()
		self.listMaps()
	
	def OnListMappingsClick(self, index):
		""" action - displays the mappings list page
		
		@param index
		"""
		self.map = self.specification.keyboard[index]
		self.listMappings()
	def OnAddMappingClick(self):
		""" action - displays add mapping page
		"""
		self.mapping = {
			'hex': '',
			'ascii': '',
			'action': '',
			'command': ''
		}
		self.editMapping()
	def OnEditMappingClick(self, index):
		""" action - displays edit mapping page
		
		@param index
		"""
		self.mapping = self.map['mappings'][index]
		self.editMapping()
	def OnSaveMappingClick(self):
		""" action - saves mapping
		"""
		self.mapping['hex'] = self.variables['hex'].get()
		self.mapping['ascii'] = self.variables['ascii'].get()
		self.mapping['action'] = self.variables['action'].get()
		self.mapping['command'] = self.variables['command'].get()
		self.specification.keyboard[self.map['name']]['mappings'][self.mapping['hex']] = self.mapping
		self.specification.save()
		self.notifier.addNotice('Mapping for key "{0}" has been saved'.format(self.mapping['ascii']))
		self.listMappings()
	def OnDeleteMappingClick(self, index):
		""" action - display delete mapping page
		
		@param index
		"""
		self.mapping = self.map['mappings'][index]
		self.deleteMapping()
	def OnConfirmDeleteMappingClick(self):
		""" action - deletes mapping
		"""
		tmpascii = self.mapping['ascii']
		del(self.map['mappings'][self.mapping['hex']])
		self.specification.save()
		self.notifier.addNotice('Mapping for key "{0}" has been deleted'.format(tmpascii))
		self.listMappings()
	def OnMappingBackClick(self):
		""" action - back from mapping
		"""
		self.editMap()
	def OnKeyCaptureClick(self):
		""" action - triggers key capture
		"""
		self.widgets['captureButton'].configure(state='disabled')
		self.widget.bind_all('<Key>',self.keyCapture)
		self.keycaptured = False
		self.notifier.addNotice('Press any key', 'warning')
	
	#=== UTILS ===#
	def inputTkCapture(self, event):
		""" util - captures kb events from TkInter
		
		@param event
		"""
		ec = '0x{0}'.format('%02x' % ord(event.char)) if any(event.char) else None
		if (ec != None):
			for h, a in self.asciimap.keyindex.items():
				if(h == ec):
					self.kbthread.doCallback(h, a)
					break
	def keyCapture(self, event):
		""" util - captures pressed key
		
		@param event
		"""
		if(not self.keycaptured):
			for h, a in self.asciimap.keyindex.items():
				if(a == event.char):
					self.keycaptured = True
					self.variables['hex'].set(h)
					self.variables['ascii'].set(a)
					self.widget.unbind_all('<Key>')
					self.widgets['captureButton'].configure(state='normal')
					self.notifier.addNotice('Key Captured')
					break