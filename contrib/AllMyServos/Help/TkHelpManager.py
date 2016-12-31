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
import ttk, os, Tkinter
from __bootstrap import AmsEnvironment
from Tkinter import *
from TkBlock import *
from TkHtml import *
from Setting import *
from subprocess import Popen, PIPE

## UI for help
class TkHelpManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" uses TkHtml, a simple HTML to Tkinter class which only parses the first level of the body element. only created for use here
		"""
		super(TkHelpManager,self).__init__(parent, gui, **options)
		self.html = TkHtml(gui)
	def setup(self):
		""" setup the menu
		"""
		self.gui.menus['help'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		self.gui.menus['help'].add_command(label="Quick start guide", command=self.OnQuickStartGuideClick)
		self.gui.menus['help'].add_command(label="Hardware", command=self.OnHardwareClick)
		self.gui.menus['help'].add_command(label="Camera", command=self.OnCameraClick)
		self.gui.menus['help'].add_command(label="Blender", command=self.OnBlenderClick)
		self.gui.menus['help'].add_command(label="Development", command=self.OnDevelopmentClick)
		self.gui.menus['help'].add_command(label="Subscribe", command=self.OnSubscribeClick)
		self.gui.menus['help'].add_command(label="Donate", command=self.OnDonateClick)
		self.addMenu(label="Help", menu=self.gui.menus['help'])
	
	#=== VIEWS ===#
	def quickStartGuide(self):
		""" view - displaying the content for the quick start page
		"""
		self.open()
		
		self.widgets['frameText'] = self.html.getHtml(self.widgets['tframe'], 'QuickStart')
		self.widgets['frameText'].grid(column=0,row=self.gridrow,sticky='EW')
	def donate(self):
		""" view - displaying the content for the donate page
		"""
		self.open()
		
		self.widgets['frameText'] = self.html.getHtml(self.widgets['tframe'], 'Donate')
		self.widgets['frameText'].grid(column=0,row=self.gridrow,sticky='EW')
	def subscribe(self):
		""" view - displaying the content for the subscribe page
		"""
		self.open()
		
		self.widgets['frameText'] = self.html.getHtml(self.widgets['tframe'], 'Subscribe')
		self.widgets['frameText'].grid(column=0,row=self.gridrow,sticky='EW')
	def hardware(self):
		""" view - displaying the content for the hardware page
		"""
		self.open()
		
		self.widgets['frameText'] = self.html.getHtml(self.widgets['tframe'], 'Hardware')
		self.widgets['frameText'].grid(column=0,row=self.gridrow,sticky='EW')
	def camera(self):
		""" view - displaying the content for the camera page
		"""
		self.open()
		
		self.widgets['frameText'] = self.html.getHtml(self.widgets['tframe'], 'Camera')
		self.widgets['frameText'].grid(column=0,row=self.gridrow,sticky='EW')
	def blender(self):
		""" view - displaying the content for the blender page
		"""
		self.open()
		
		self.widgets['frameText'] = self.html.getHtml(self.widgets['tframe'], 'BlenderIntegration')
		self.widgets['frameText'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['infoframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widgets['infoframe'].grid(column=0,row=self.gridrow, pady=20, sticky='EW')
		
		self.widgets['pluginLabel'] = Tkinter.Label(self.widgets['infoframe'],text='AllMyServos Blender Addon', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['pluginLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['versionLabel'] = Tkinter.Label(self.widgets['infoframe'],text='Bundled Version', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['versionLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['versionData'] = Tkinter.Label(self.widgets['infoframe'],text='0.7', bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['versionData'].grid(column=1,row=self.gridrow, padx=15, sticky='EW')
		
		self.widgets['viewAddon'] = Tkinter.Button(self.widgets['infoframe'],text=u"View Addon", image=self.images['find'], command=self.OnViewAddonClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['viewAddon'].grid(column=3,row=self.gridrow)
	def development(self):
		""" view - displaying the content for the development page
		"""
		self.open()
		
		self.widgets['frameText'] = self.html.getHtml(self.widgets['tframe'], 'Development')
		self.widgets['frameText'].grid(column=0,row=self.gridrow,sticky='EW')
	
	#=== ACTIONS ===#
	def OnQuickStartGuideClick(self):
		""" action - open quick start guide
		"""
		self.quickStartGuide()
	def OnDonateClick(self):
		""" action - open donate page
		"""
		self.donate()
	def OnSubscribeClick(self):
		""" action - open subscribe page
		"""
		self.subscribe()
	def OnHardwareClick(self):
		""" action - open hardware page
		"""
		self.hardware()
	def OnCameraClick(self):
		""" action - open camera page
		"""
		self.camera()
	def OnBlenderClick(self):
		""" action - open blender page
		"""
		self.blender()
	def OnDevelopmentClick(self):
		""" action - open development page
		"""
		self.development()
	def OnViewAddonClick(self):
		""" action - open file manager to bundled blender addon location
		"""
		res = self.__openFileManager(os.path.join(AmsEnvironment.AppPath(), 'help/blender-addon'))
		if(res):
			self.notifier.addNotice('Now showing: Bundled Addon in file manager')
		else:
			self.notifier.addNotice('Unable to open: '+os.path.join(AmsEnvironment.AppPath(), 'help/blender-addon'), 'error')
	
	#=== UTILS ===#
	def __openFileManager(self, dir=''):
		""" opens the pi file manager
		
		@param dir str
		"""
		try:
			if(len(dir) > 0):
				command = ['pcmanfm', dir]
				p = Popen(command, stdout=PIPE)
				o = p.communicate()[0]
				if(p.returncode == 0):
					return True
		except:
			pass
		return False