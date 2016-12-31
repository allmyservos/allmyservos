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
import ttk, Tkinter, Egg
from Tkinter import *
from TkBlock import *
from Setting import *

## UI for settings
class TkSettingManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes TkSettingManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkSettingManager,self).__init__(parent, gui, **options)
		self.s = Setting()
	def setup(self):
		""" setup gui menu
		"""
		try:
			self.gui.menus['settings']
		except:
			self.gui.menus['settings'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="Settings", menu=self.gui.menus['settings'])
		self.gui.menus['settings'].insert_separator(1)
		self.gui.menus['settings'].insert_command(label="All Settings", index=2, command=self.OnListSettingsClick)
	
	#=== VIEWS ===#
	def listSettings(self):
		""" view - list settings
		"""
		self.open()
		self.gridrow = 0
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Setting Manager / Settings', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['addsetting'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Setting", image=self.images['add'], command=self.OnAddSettingClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addsetting'].grid(column=1,row=self.gridrow)
		self.gridrow += 1
		self.settings = self.s.query(order = 'name', keyindex= False)

		self.widgets['settingFrame'] = Tkinter.Frame(self.widgets['tframe'], borderwidth=0, highlightthickness=0, bg=self.colours['bg'])
		self.widgets['settingFrame'].grid(column=0,row=self.gridrow, columnspan=2,sticky='E')
		
		if(len(self.settings) > 0):
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['settingFrame'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['typeLabel'] = Tkinter.Label(self.widgets['settingFrame'],text='Type', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['typeLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['valueLabel'] = Tkinter.Label(self.widgets['settingFrame'],text='Value', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['valueLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['settingFrame'],text='Edit', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['editLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['settingFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['deleteLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			rowcount = 0
			for s in self.settings:
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['name'+str(self.gridrow)] = Tkinter.Label(self.widgets['settingFrame'],text=self.settings[s].name, bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['name'+str(self.gridrow)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['type'+str(self.gridrow)] = Tkinter.Label(self.widgets['settingFrame'],text=self.settings[s].type, bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['type'+str(self.gridrow)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['value'+str(self.gridrow)] = Tkinter.Label(self.widgets['settingFrame'],text=self.settings[s].value, bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['value'+str(self.gridrow)].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['edit'+str(self.gridrow)] = Tkinter.Button(self.widgets['settingFrame'],text=u"Edit Setting", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = self.settings[s].name:self.OnEditSettingClick(x))
				self.widgets['edit'+str(self.gridrow)].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['delete'+str(self.gridrow)] = Tkinter.Button(self.widgets['settingFrame'],text=u"Delete Setting", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = self.settings[s].name:self.OnDeleteSettingClick(x))
				self.widgets['delete'+str(self.gridrow)].grid(column=4,row=self.gridrow,sticky='EW')
				self.gridrow += 1
			
			self.widgets['egg'] = Tkinter.Button(self.widgets['settingFrame'], bg=self.colours['bg'], activebackground='#000000', highlightbackground=self.colours['bg'], highlightthickness=0, borderwidth=0, command=self.OnEggClick, height=1, width=1)
			self.widgets['egg'].grid(column=4,row=self.gridrow,sticky='EW')
		else:
			self.widgets['emptylabel'] = Tkinter.Label(self.widgets['settingFrame'], text="There are currently no settings", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['emptylabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.gridrow += 1
	def editSetting(self):
		""" view - edit setting
		"""
		self.open()
		self.gridrow = 0
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Edit Setting', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['name'] = Tkinter.StringVar()
		self.widgets['nameentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['name'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['nameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if hasattr(self.setting, 'rowid'):
			self.variables['name'].set(self.setting.name)
		
		self.gridrow += 1
		
		self.widgets['typeLabel'] = Tkinter.Label(self.widgets['tframe'],text='Type', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['typeLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['type'] = Tkinter.StringVar()
		self.widgets['typeentry'] = Tkinter.OptionMenu(self.widgets['tframe'],self.variables['type'], 'string', 'int', 'long', 'float', 'complex', 'bool', command=self.OnChangeType)
		self.widgets['typeentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
		self.widgets['typeentry'].grid(column=1,row=self.gridrow,sticky='EW')
		if hasattr(self.setting, 'rowid'):
			self.variables['type'].set(self.setting.type)
		
		self.gridrow += 1
		
		self.widgets['valueLabel'] = Tkinter.Label(self.widgets['tframe'],text='Value', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['valueLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.valueframerow = self.gridrow
		
		self.OnChangeType()
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		if hasattr(self.setting, 'rowid'):
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['deleteLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.listSettings, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['savesetting'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Setting", image=self.images['save'], command=self.OnSaveSettingClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['savesetting'].grid(column=1,row=self.gridrow)
		if hasattr(self.setting, 'rowid'):
			self.widgets['deletesetting'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete Setting", image=self.images['delete'], command=self.OnDeleteSettingClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['deletesetting'].grid(column=2,row=self.gridrow)
	def egg(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Congratulations, you found an eggy wegg!', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.e = Egg.EggyWegg.open()
		self.widgets['typeLabel'] = Tkinter.Label(self.widgets['tframe'],image=self.e['yolk'], bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['typeLabel'].grid(column=0,row=self.gridrow,sticky='EW')
	def deleteSetting(self):
		""" view - delete setting
		"""
		self.open()
		self.gridrow = 0
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Delete Setting', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		self.widgets['confirmLabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this setting?', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['confirmLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['nameData'] = Tkinter.Label(self.widgets['tframe'],text=self.setting.name, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['typeLabel'] = Tkinter.Label(self.widgets['tframe'],text='Type', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['typeLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['typeData'] = Tkinter.Label(self.widgets['tframe'],text=self.setting.type, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['typeData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['valueLabel'] = Tkinter.Label(self.widgets['tframe'],text='Value', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['valueLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['valueData'] = Tkinter.Label(self.widgets['tframe'],text=self.setting.value, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['valueData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['acceptlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Accept", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['acceptlabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['cancelbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Cancel", image=self.images['back'], command=self.OnCancelDeleteClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['cancelbutton'].grid(column=0,row=self.gridrow)
		self.widgets['confirmbutton'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['accept'], command=self.OnDeleteSettingConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['confirmbutton'].grid(column=1,row=self.gridrow)
	
	#=== ACTIONS ===#
	def OnChangeType(self, value = None):
		""" action - change setting type
		
		@param value
		"""
		try:
			self.widgets['valueframe'].grid_forget()
		except:
			pass
		self.widgets['valueframe'] = Frame(self.widgets['tframe'],bg=self.colours['bg'])
		self.widgets['valueframe'].grid(column=1,row=self.valueframerow,sticky='EW')
		if(self.variables['type'].get() == 'bool'):
			self.variables['value'] = Tkinter.BooleanVar()
			self.widgets['valueentry'] = Tkinter.Checkbutton(self.widgets['valueframe'], text="Value", variable=self.variables['value'], bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
			self.widgets['valueentry'].grid(column=1,row=0,sticky='EW')
			if hasattr(self.setting, 'rowid'):
				self.variables['value'].set(bool(self.setting.value))
		else:
			self.variables['value'] = Tkinter.StringVar()
			self.widgets['valueentry'] = Tkinter.Entry(self.widgets['valueframe'], textvariable=self.variables['value'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
			self.widgets['valueentry'].grid(column=1,row=0,sticky='EW')
			if hasattr(self.setting, 'rowid'):
				self.variables['value'].set(self.setting.value)
	def OnListSettingsClick(self):
		""" action - display settings list page
		"""
		self.listSettings()
	def OnEditSettingClick(self, name):
		""" action - display edit setting page
		"""
		self.setting = self.s.loadBy({'name': name})
		self.editSetting()
	def OnAddSettingClick(self):
		""" action - display add setting page
		"""
		self.setting = Setting()
		self.editSetting()
	def OnSaveSettingClick(self):
		""" action - save setting
		"""
		if(len(self.variables['name'].get()) == 0):
			self.editSetting()
			return False
		self.setting.name = self.variables['name'].get()
		val = self.variables['value'].get()
		try:
			if(self.variables['type'].get() == 'bool'):
				val = bool(self.variables['value'].get())
			elif(self.variables['type'].get() == 'int'):
				val = int(self.variables['value'].get())
			elif(self.variables['type'].get() == 'long'):
				val = long(self.variables['value'].get())
			elif(self.variables['type'].get() == 'float'):
				val = float(self.variables['value'].get())
			elif(self.variables['type'].get() == 'complex'):
				val = complex(self.variables['value'].get())
		except:
			self.editSetting()
			return False
		self.setting.value = val #auto saves
		self.notifier.addNotice('Setting saved')
		self.listSettings()
	def OnDeleteSettingClick(self, name = None):
		""" action - display delete setting page
		
		@param name
		"""
		if(name != None):
			self.setting = self.s.loadBy({'name': name})
		self.deleteSetting()
	def OnDeleteSettingConfirmClick(self):
		""" action - delete setting
		"""
		self.setting.delete()
		self.setting = None
		self.notifier.addNotice('Setting deleted')
		self.listSettings()
	def OnCancelDeleteClick(self):
		""" action - cancel delete setting
		"""
		self.listSettings()
	def OnEggClick(self):
		self.egg()