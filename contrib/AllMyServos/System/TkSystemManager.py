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
import Tkinter, os, sys, commands, time, re
from __bootstrap import AmsEnvironment
from Tkinter import *
from TkBlock import *
from subprocess import Popen, PIPE

## UI for system info and options
class TkSystemManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes TkSystemManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkSystemManager,self).__init__(parent, gui, **options)
		self.patterns = {
			'ident': re.compile(r'(?P<ident>\w+)\s+Change\sLog'),
			'head': re.compile(r'(?P<date>Date)\s+(?P<amends>Amends)'),
			'version': re.compile(r'v(?P<version>(\d|\.)+)'),
			'amendstart': re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\s+(?P<comment>.*)'),
			'amendcont': re.compile(r'\s+(?P<comment>.+)'),
		}
		self.commands = {
			'auto_rc_cli': 'sleep 10;python {} &'.format(os.path.join(AmsEnvironment.AppPath(), 'CLI.py')),
			'auto_lxde_cli': '@sudo /usr/bin/python {}'.format(os.path.join(AmsEnvironment.AppPath(), 'CLI.py')),
			'auto_lxde_gui': '@sudo /usr/bin/python {}'.format(os.path.join(AmsEnvironment.AppPath(), 'GUI.py')),
		}
		self.gui.trayIcon.setExitCallback(self.OnExitClick) #enables the exit menu item of the tray icon
	def setup(self):
		""" setup gui menu
		"""
		try:
			self.gui.menus['file']
		except:
			self.gui.menus['file'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="File", menu=self.gui.menus['file'])
		self.gui.menus['system'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		self.gui.menus['system'].add_command(label="Information", command=self.OnInformationClick)
		self.gui.menus['system'].add_command(label="Startup", command=self.OnStartupClick)
		self.gui.menus['system'].add_separator()
		self.gui.menus['system'].add_command(label="Reboot", command=self.OnRebootClick)
		self.gui.menus['system'].add_command(label="Poweroff", command=self.OnPoweroffClick)
		self.gui.menus['file'].insert_cascade(index=1, label="System", menu=self.gui.menus['system'])
		self.gui.menus['file'].insert_command(index=10, label="Exit", command=self.OnExitClick)
		
	#=== VIEWS ===#
	def showInformation(self):
		""" view - show system information
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='System', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.amsInfo()
		
		self.gridrow += 1
		
		self.pythonInfo()
		
		self.gridrow += 1
		
		self.platformInfo()
	def platformInfo(self):
		""" view - show platform information
		"""
		row = 0
		self.widgets['pframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['pframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.widgets['pLabel'] = Tkinter.Label(self.widgets['pframe'],text='Platform', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['pLabel'].grid(column=0,row=row,sticky='EW')
		row += 1
		self.widgets['psubframe'] = Tkinter.Frame(self.widgets['pframe'], bg=self.colours['rowaltbg'])
		self.widgets['psubframe'].grid(column=0,row=row,columnspan=2, sticky='EW')
		row = 0
		
		self.widgets['platformLabel'] = Tkinter.Label(self.widgets['psubframe'],text='Platform', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
		self.widgets['platformLabel'].grid(column=0,row=row,sticky='EW')
		
		self.widgets['platformData'] = Tkinter.Label(self.widgets['psubframe'],text=str(sys.platform), bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
		self.widgets['platformData'].grid(column=1,row=row,sticky='W')
	def pythonInfo(self):
		""" view - show python information
		"""
		row = 0
		self.widgets['pyframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['pyframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.widgets['pyLabel'] = Tkinter.Label(self.widgets['pyframe'],text='Python', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['pyLabel'].grid(column=0,row=row,sticky='EW')
		row += 1
		self.widgets['pysubframe'] = Tkinter.Frame(self.widgets['pyframe'], bg=self.colours['rowaltbg'])
		self.widgets['pysubframe'].grid(column=0,row=row,columnspan=2, sticky='EW')
		row = 0
		self.widgets['pyversionLabel'] = Tkinter.Label(self.widgets['pysubframe'],text='Python Version', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
		self.widgets['pyversionLabel'].grid(column=0,row=row,sticky='EW')
		
		self.widgets['pyversionData'] = Tkinter.Label(self.widgets['pysubframe'],text=str(sys.version), bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
		self.widgets['pyversionData'].grid(column=1,row=row,sticky='W')
		
		row += 1
		
		self.widgets['wdLabel'] = Tkinter.Label(self.widgets['pysubframe'],text='Working Directory', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
		self.widgets['wdLabel'].grid(column=0,row=row,sticky='EW')
		
		self.widgets['wdData'] = Tkinter.Label(self.widgets['pysubframe'],text=os.getcwd(), bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
		self.widgets['wdData'].grid(column=1,row=row,sticky='W')
		
		row += 1
		
		self.widgets['adLabel'] = Tkinter.Label(self.widgets['pysubframe'],text='App Directory', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
		self.widgets['adLabel'].grid(column=0,row=row,sticky='EW')
		
		self.widgets['adData'] = Tkinter.Label(self.widgets['pysubframe'],text=AmsEnvironment.AppPath(), bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
		self.widgets['adData'].grid(column=1,row=row,sticky='W')
		
		row += 1
		
		self.widgets['fdLabel'] = Tkinter.Label(self.widgets['pysubframe'],text='Files Directory', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
		self.widgets['fdLabel'].grid(column=0,row=row,sticky='EW')
		
		self.widgets['fdData'] = Tkinter.Label(self.widgets['pysubframe'],text=AmsEnvironment.FilePath(), bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
		self.widgets['fdData'].grid(column=1,row=row,sticky='W')
		
		row += 1
		
		self.widgets['pathLabel'] = Tkinter.Label(self.widgets['pysubframe'],text='System Paths', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
		self.widgets['pathLabel'].grid(column=0,row=row,sticky='EW')
		
		for p in sys.path:
			self.widgets['pathData'] = Tkinter.Label(self.widgets['pysubframe'],text=p, bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
			self.widgets['pathData'].grid(column=1,row=row,sticky='W')
			row += 1
	def amsInfo(self):
		""" view - show All My Servos information
		"""
		self.__parseChangeLog()
		row = 0
		self.widgets['aframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['aframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.widgets['aLabel'] = Tkinter.Label(self.widgets['aframe'],text='AllMyServos', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['aLabel'].grid(column=0,row=row,sticky='EW')
		row += 1
		self.widgets['asubframe'] = Tkinter.Frame(self.widgets['aframe'], bg=self.colours['rowaltbg'])
		self.widgets['asubframe'].grid(column=0,row=row,columnspan=2, sticky='EW')
		row = 0
		self.widgets['aversionLabel'] = Tkinter.Label(self.widgets['asubframe'],text='Framework Version', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
		self.widgets['aversionLabel'].grid(column=0,row=row,sticky='NEW')
		
		self.widgets['aversionData'] = Tkinter.Label(self.widgets['asubframe'],text=self.currentversion, bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
		self.widgets['aversionData'].grid(column=1,row=row,sticky='W')
		
		row += 1
		
		self.widgets['achangeLabel'] = Tkinter.Label(self.widgets['asubframe'],text='Change Log', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
		self.widgets['achangeLabel'].grid(column=0,row=row,sticky='NEW')
		
		self.widgets['achangeData'] = self.changeLogView(self.widgets['asubframe'])
		self.widgets['achangeData'].grid(column=1,row=row,sticky='W')
	def changeLogView(self, parent):
		""" partial view - display change log data
		"""
		w = Tkinter.Frame(parent, borderwidth=0, highlightthickness=0, bg=self.colours['rowaltbg'])
		row = 0
		cindex = 'cl{0}'.format(row)
		for i in self.changelog:
			self.widgets[cindex+'version'] = Tkinter.Label(w,text=i['version'], bg=self.colours['rowaltbg'], fg=self.colours['headingfg'], height=2)
			self.widgets[cindex+'version'].grid(column=0,row=row,columnspan=2, sticky='NEW')
			row += 1
			for a in i['amends']:
				self.widgets[cindex+'date'] = Tkinter.Label(w,text='{0}-{1}-{2} : '.format(a['year'], a['month'], a['day']), bg=self.colours['rowaltbg'], fg=self.colours['headingfg'], height=2)
				self.widgets[cindex+'date'].grid(column=0,row=row, sticky='NEW')
				self.widgets[cindex+'comment'] = Tkinter.Label(w,text=a['comment'], bg=self.colours['rowaltbg'], fg=self.colours['valuefg'])
				self.widgets[cindex+'comment'].grid(column=1,row=row, sticky='NEW')
				row += 1
			row += 1
		return w
	def poweroff(self):
		""" view - poweroff page
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='System / Poweroff', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['confirmLabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to completely power down the Raspberry Pi?', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['confirmLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['commandLabel'] = Tkinter.Label(self.widgets['tframe'],text='Command', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['commandLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['commandData'] = Tkinter.Label(self.widgets['tframe'],text='sudo poweroff', bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['commandData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionpyframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionpyframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionpyframe'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['acceptlabel'] = Tkinter.Label(self.widgets['optionpyframe'],text="Accept", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['acceptlabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['cancelbutton'] = Tkinter.Button(self.widgets['optionpyframe'],text=u"Cancel", image=self.images['back'], command=self.OnCancelPoweroffClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['cancelbutton'].grid(column=0,row=self.gridrow)
		self.widgets['confirmbutton'] = Tkinter.Button(self.widgets['optionpyframe'],text=u"Delete", image=self.images['accept'], command=self.OnPoweroffConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['confirmbutton'].grid(column=1,row=self.gridrow)
	def reboot(self):
		""" view - reboot page
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='System / Reboot', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['confirmLabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to reboot the Raspberry Pi?', bg=self.colours['rowbg'], fg=self.colours['fg'], height=2)
		self.widgets['confirmLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['commandLabel'] = Tkinter.Label(self.widgets['tframe'],text='Command', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['commandLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['commandData'] = Tkinter.Label(self.widgets['tframe'],text='sudo reboot', bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['commandData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionpyframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionpyframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionpyframe'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['acceptlabel'] = Tkinter.Label(self.widgets['optionpyframe'],text="Accept", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['acceptlabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['cancelbutton'] = Tkinter.Button(self.widgets['optionpyframe'],text=u"Cancel", image=self.images['back'], command=self.OnCancelRebootClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['cancelbutton'].grid(column=0,row=self.gridrow)
		self.widgets['confirmbutton'] = Tkinter.Button(self.widgets['optionpyframe'],text=u"Delete", image=self.images['accept'], command=self.OnRebootConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['confirmbutton'].grid(column=1,row=self.gridrow)
	def startupConfig(self):
		""" view - show startup settings
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='System / Startup', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		
		
		self.widgets['spacer'] = Tkinter.Label(self.widgets['tframe'],text='', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['spacer'].grid(column=0,row=self.gridrow,pady=5,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['opLabel'] = Tkinter.Label(self.widgets['tframe'],text='Options', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['opLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['iLabel'] = Tkinter.Label(self.widgets['tframe'],text='Use this feature if you find this software useful enough to start with the Pi or you would like to run in headless mode (no monitor).', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['iLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['opframewrap'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['opframewrap'].grid(column=0,row=self.gridrow, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['iLabel'] = Tkinter.Label(self.widgets['tframe'],text='Only the CLI can be started with Linux. The application will be run in the background.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['iLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['iLabel'] = Tkinter.Label(self.widgets['tframe'],text='Starting with Linux is good for using the RPC service but cannot capture keyboard events.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['iLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['iLabel'] = Tkinter.Label(self.widgets['tframe'],text='Starting with LXDE requires the application to be installed locally on the Pi. When running from a network share, start with Linux instead.', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['iLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['iLabel'] = Tkinter.Label(self.widgets['tframe'],text='All services are available when using this method but the Pi must boot to the desktop, not the command line (setting in raspi-config).', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['iLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['confLabel'] = Tkinter.Label(self.widgets['tframe'],text='Configuration', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['confLabel'].grid(column=0,row=self.gridrow,pady=10,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['scframewrap'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['scframewrap'].grid(column=0,row=self.gridrow, sticky='EW')
		
		self.updateStartupConfig()
	def updateStartupConfig(self):
		self.startupInfo = self.__getStartupInfo()
		
		if ('opframe' in self.widgets.keys()):
			self.widgets['opframe'].grid_forget()
		
		self.widgets['opframe'] = Tkinter.Frame(self.widgets['opframewrap'], bg=self.colours['bg'])
		self.widgets['opframe'].grid(column=0,row=0, sticky='EW')
		
		self.widgets['asLabel'] = Tkinter.Label(self.widgets['opframe'],text='Enable autostart', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['asLabel'].grid(column=0,row=0,pady=10,sticky='EW')
		
		self.variables['autostart'] = Tkinter.BooleanVar()
		self.variables['autostart'].set(self.startupInfo['settings']['enabled'])
		self.widgets['autostartentry'] = Tkinter.Checkbutton(self.widgets['opframe'], text="Autostart", variable=self.variables['autostart'], command=self.OnToggleAutostartClick, bg=self.colours['bg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'], activebackground=self.colours['activebg'], selectcolor=self.colours['bg'])
		self.widgets['autostartentry'].grid(column=1,pady=10,row=0)
		
		self.widgets['swLabel'] = Tkinter.Label(self.widgets['opframe'],text='Start with ...', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['swLabel'].grid(column=0,row=1,pady=10,sticky='EW')
		
		self.variables['startwith'] = Tkinter.StringVar()
		self.variables['startwith'].set(self.startupInfo['settings']['start_with'])
		self.widgets['swlinux'] = Radiobutton(self.widgets['opframe'], text='Linux', variable=self.variables['startwith'], value='linux', command=self.OnChangeStartWith, selectcolor=self.colours['bg'], bg=self.colours['bg'], activebackground=self.colours['activebg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'])
		self.widgets['swlinux'].grid(column=1,row=1,padx=10,sticky='W')
		
		self.widgets['swlxde'] = Radiobutton(self.widgets['opframe'], text='LXDE', variable=self.variables['startwith'], value='lxde', command=self.OnChangeStartWith, selectcolor=self.colours['bg'], bg=self.colours['bg'], activebackground=self.colours['activebg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'])
		self.widgets['swlxde'].grid(column=1,row=2,padx=10,sticky='W')
		
		if (not self.startupInfo['settings']['enabled']):
			self.widgets['swlinux'].configure(state='disabled')
			self.widgets['swlxde'].configure(state='disabled')
		
		self.widgets['smLabel'] = Tkinter.Label(self.widgets['opframe'],text='Startup mode', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['smLabel'].grid(column=0,row=3,pady=10,sticky='EW')
		
		self.variables['startmode'] = Tkinter.StringVar()
		self.variables['startmode'].set(self.startupInfo['settings']['start_mode'])
		self.widgets['cli'] = Radiobutton(self.widgets['opframe'], text='CLI', variable=self.variables['startmode'], value='cli', command=self.OnChangeStartMode, selectcolor=self.colours['bg'], bg=self.colours['bg'], activebackground=self.colours['activebg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'])
		self.widgets['cli'].grid(column=1,row=3,padx=10,sticky='W')
		
		if (not self.startupInfo['settings']['enabled']):
			self.widgets['cli'].configure(state='disabled')
		
		self.widgets['gui'] = Radiobutton(self.widgets['opframe'], text='GUI', variable=self.variables['startmode'], value='gui', command=self.OnChangeStartMode, selectcolor=self.colours['bg'], bg=self.colours['bg'], activebackground=self.colours['activebg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'])
		self.widgets['gui'].grid(column=1,row=4,padx=10,sticky='W')
		
		if (not self.startupInfo['settings']['enabled'] or self.startupInfo['settings']['start_with'] == 'linux'):
			self.widgets['gui'].configure(state='disabled')
			
		self.widgets['smLabel'] = Tkinter.Label(self.widgets['opframe'],text='Startup user', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['smLabel'].grid(column=0,row=5,pady=10,sticky='EW')
		
		self.variables['startuser'] = Tkinter.StringVar()
		self.variables['startuser'].set('==global==' if self.startupInfo['settings']['start_user'] == '' else self.startupInfo['settings']['start_user'])
		self.widgets['rbGlobal'] = Radiobutton(self.widgets['opframe'], text='Global', variable=self.variables['startuser'], value='==global==', command=self.OnChangeStartUser, selectcolor=self.colours['bg'], bg=self.colours['bg'], activebackground=self.colours['activebg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'])
		self.widgets['rbGlobal'].grid(column=1,row=5,padx=10,sticky='W')
		if (not self.startupInfo['settings']['enabled'] or self.startupInfo['settings']['start_with'] == 'linux'):
			self.widgets['rbGlobal'].configure(state='disabled')
		
		row = 6
		for x in self.startupInfo['autostart']['users']:
			self.widgets['rb{}'.format(x['user'])] = Radiobutton(self.widgets['opframe'], text=x['user'], variable=self.variables['startuser'], value=x['user'], command=self.OnChangeStartUser, selectcolor=self.colours['bg'], bg=self.colours['bg'], activebackground=self.colours['activebg'], highlightbackground=self.colours['activebg'], fg=self.colours['valuefg'])
			self.widgets['rb{}'.format(x['user'])].grid(column=1,row=row,padx=10,sticky='W')
			if (not self.startupInfo['settings']['enabled'] or self.startupInfo['settings']['start_with'] == 'linux'):
				self.widgets['rb{}'.format(x['user'])].configure(state='disabled')
			row += 1
		
		if ('scframe' in self.widgets.keys()):
			self.widgets['scframe'].grid_forget()
		
		self.widgets['scframe'] = Tkinter.Frame(self.widgets['scframewrap'], bg=self.colours['bg'])
		self.widgets['scframe'].grid(column=0,row=0, sticky='EW')
		
		row = 0
		
		self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Status', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
		
		self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text='Syncronised' if self.startupInfo['synced'] else 'Not syncronised', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
		
		row += 1
		
		self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Startup Method', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
		
		startupMethod = 'None'
		if (self.startupInfo['settings']['enabled'] and self.startupInfo['settings']['start_with'] == 'linux'):
			startupMethod = 'rc.local'
		elif (self.startupInfo['settings']['enabled'] and self.startupInfo['settings']['start_with'] == 'lxde'):
			startupMethod = 'autostart'
		self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=startupMethod, anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
		
		row += 1
		
		if (not self.startupInfo['synced'] and startupMethod == 'None'):
			#should not be enabled
			#check rc.local
			if (self.startupInfo['rc_local']['file_exists'] and self.startupInfo['rc_local']['cmd_exists'] and not self.startupInfo['rc_local']['cmd_commented']):
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='File', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=self.startupInfo['rc_local']['path'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Command', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=self.commands['auto_rc_cli'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Issue', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text='Command exists when it should not', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1
			#check autostart
			if (self.startupInfo['autostart']['global']['file_exists']):
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='File', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=self.startupInfo['autostart']['global']['path'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1
				command = self.commands['auto_lxde_cli']
				if (self.startupInfo['autostart']['global']['cmd']['gui']['exists'] and not self.startupInfo['autostart']['global']['cmd']['gui']['commented']):
					command = self.commands['auto_lxde_gui']
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Command', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=command, anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Issue', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text='Command exists when it should not', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1
			for x in self.startupInfo['autostart']['users']:
				if (x['file_exists']):
					if (x['cmd']['cli']['exists'] and not x['cmd']['cli']['commented']):
						self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='File', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
						self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
						self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=x['path'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
						self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
						row += 1
						self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Command', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
						self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
						self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=self.commands['auto_lxde_cli'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
						self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
						row += 1
						self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Issue', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
						self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
						self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text='Command exists when it should not', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
						self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
						row += 1
					elif (x['cmd']['gui']['exists'] and not x['cmd']['gui']['commented']):
						self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='File', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
						self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
						self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=x['path'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
						self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
						row += 1
						self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Command', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
						self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
						self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=self.commands['auto_lxde_gui'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
						self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
						row += 1
						self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Issue', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
						self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
						self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text='Command exists when it should not', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
						self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
						row += 1
		elif (not self.startupInfo['synced']):
			if (self.startupInfo['settings']['start_with'] == 'linux'):
				#should start with linux
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='File', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=self.startupInfo['rc_local']['path'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Command', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=self.commands['auto_rc_cli'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1
				issue = 'File missing'
				if (not self.startupInfo['rc_local']['cmd_exists']):
					issue = 'Command missing'
				elif(self.startupInfo['rc_local']['cmd_commented']):
					issue = 'Command commented'
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Issue', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=issue, anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1
			else:
				#should start with lxde
				startupFile = self.startupInfo['autostart']['global']['path']
				issue = ''
				if (self.startupInfo['settings']['start_user'] == ''):
					#should be global
					if (self.startupInfo['settings']['start_mode'] == 'cli'):
						#should be cli mode
						if (not self.startupInfo['autostart']['global']['cmd']['cli']['exists']):
							issue = 'Command missing'
						elif (self.startupInfo['autostart']['global']['cmd']['cli']['commented']):
							issue = 'Command commented'
					else:
						#should be gui mode
						if (not self.startupInfo['autostart']['global']['cmd']['gui']['exists']):
							issue = 'Command missing'
						elif (self.startupInfo['autostart']['global']['cmd']['gui']['commented']):
							issue = 'Command commented'
				else:
					#should be user
					userFile = [x for x in self.startupInfo['autostart']['users'] if x['user'] == self.startupInfo['settings']['start_user']]
					if (not any(userFile)):
						issue = 'Missing user? {}'.format(self.startupInfo['settings']['start_user'])
					else:
						userFile = userFile[0]
						startupFile = userFile['path']
						if (not userFile['file_exists']):
							issue = 'File missing'
						else:
							if (self.startupInfo['settings']['start_mode'] == 'cli'):
								if (not userFile['cmd']['cli']['exists']):
									issue = 'Command missing'
								elif (userFile['cmd']['cli']['commented']):
									issue = 'Command commented'
							else:
								if (not userFile['cmd']['gui']['exists']):
									issue = 'Command missing'
								elif (userFile['cmd']['gui']['commented']):
									issue = 'Command commented'
					
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='File', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=startupFile, anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1
				startupCommand = self.commands['auto_lxde_cli'] if self.startupInfo['settings']['start_mode'] == 'cli' else self.commands['auto_lxde_gui']
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Command', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=startupCommand, anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1
				self.widgets['iLabel'] = Tkinter.Label(self.widgets['scframe'],text='Issue', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['iLabel'].grid(column=0,row=row,pady=5,sticky='EW')
				self.widgets['iValue'] = Tkinter.Label(self.widgets['scframe'],text=issue, anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
				self.widgets['iValue'].grid(column=1,row=row,pady=5,sticky='EW')
				row += 1

		if (not self.startupInfo['synced']):
			self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['scframe'], bg=self.colours['bg'])
			self.widgets['optionsFrame'].grid(column=0,row=row,columnspan=2, sticky='EW')
			
			self.widgets['syncLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Sync', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['syncLabel'].grid(column=0,row=row,sticky='EW')

			row += 1

			self.widgets['sync'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Sync", image=self.images['accept'], command=self.OnSyncConfigClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['sync'].grid(column=0,row=row)
			
	#=== ACTIONS ===#
	def OnInformationClick(self):
		""" action - display information page
		"""
		self.showInformation()
	def OnStartupClick(self):
		""" action - display startup page
		"""
		self.startupConfig()
	def OnRebootClick(self):
		""" action - display the reboot page
		"""
		self.reboot()
	def OnRebootConfirmClick(self):
		""" action - reboot the system
		"""
		self.__stoptasks()
		time.sleep(5)
		p = Popen(['sudo','reboot'], stdout=PIPE)
		o = p.communicate()[0]
	def OnCancelRebootClick(self):
		""" action - cancel reboot
		"""
		self.showInformation()
	def OnPoweroffClick(self):
		""" action - display poweroff page
		"""
		self.poweroff()
	def OnPoweroffConfirmClick(self):
		""" action - poweroff the system
		"""
		self.__stoptasks()
		p = Popen(['sudo','poweroff'], stdout=PIPE)
		o = p.communicate()[0]
	def OnCancelPoweroffClick(self):
		""" action - poweroff the system
		"""
		self.showInformation()
	def OnExitClick(self):
		self.__stoptasks()
		self.gui.quit()
	def OnToggleAutostartClick(self):
		Setting.set('startup_autostart', self.variables['autostart'].get())
		self.startupInfo = self.__getStartupInfo(useCache=False)
		self.updateStartupConfig()
	def OnChangeStartWith(self):
		Setting.set('startup_start_with', self.variables['startwith'].get())
		if (Setting.get('startup_start_with') == 'linux'):
			#ensure start_mode is cli and us
			Setting.set('startup_start_mode', 'cli')
		self.startupInfo = self.__getStartupInfo(useCache=False)
		self.updateStartupConfig()
	def OnChangeStartMode(self):
		Setting.set('startup_start_mode', self.variables['startmode'].get())
		self.startupInfo = self.__getStartupInfo(useCache=False)
		self.updateStartupConfig()
	def OnChangeStartUser(self):
		Setting.set('startup_start_user', '' if self.variables['startuser'].get() == '==global==' else self.variables['startuser'].get())
		self.startupInfo = self.__getStartupInfo(useCache=False)
		self.updateStartupConfig()
	def OnSyncConfigClick(self):
		res = self.__syncConfig()
		self.startupInfo = self.__getStartupInfo(useCache=False)
		self.updateStartupConfig()
		self.notifier.addNotice("Config Updated\n{}".format("\n".join(res['messages'])))
	#=== UTILS ===#
	def __parseChangeLog(self):
		""" util - parse change log data
		"""
		self.currentversion = 0.01
		self.changelog = []
		self.ident = None
		self.headings = None
		filename = os.path.join(AmsEnvironment.AppPath(), 'ChangeLog.txt')
		if os.path.exists(filename):
			f = open(filename, 'r')
			for l in f:
				matches = self.patterns['ident'].match(l)
				if(matches != None):
					self.ident = matches.group('ident')
				matches = self.patterns['head'].match(l)
				if(matches != None):
					self.headings = ['Date', 'Amends']
				matches = self.patterns['version'].match(l)
				if(matches != None):
					self.currentversion = matches.group('version')
					self.changelog.append({ 'version': self.currentversion, 'amends': []})
				matches = self.patterns['amendstart'].match(l)
				if(matches != None):
					self.changelog[-1]['amends'].append({'year': matches.group('year'), 'month': matches.group('month'), 'day': matches.group('day'), 'comment': matches.group('comment')})
				matches = self.patterns['amendcont'].match(l)
				if(matches != None):
					self.changelog[-1]['amends'][-1]['comment'] += '\n'+matches.group('comment')
			f.close()
	
	def __getStartupSettings(self):
		res = {
			'enabled': Setting.get('startup_autostart', False),
			'start_with': Setting.get('startup_start_with', 'lxde'),
			'start_mode': Setting.get('startup_start_mode', 'gui'),
			'start_user': Setting.get('startup_start_user', 'pi'),
		}
		return res
	def __getStartupInfo(self, useCache = True):
		""" util - collect startup information
		
		@return dict
		"""
		res = {
			'rc_local': self.__getRcLocal(useCache),
			'autostart': self.__getAutostart(useCache),
			'settings': self.__getStartupSettings(),
			'synced': False
		}
		if (res['settings']['enabled'] == True):
			if (res['settings']['start_with'] == 'linux'):
				#should start with linux (rc.local)
				if (res['rc_local']['file_exists'] and res['rc_local']['cmd_exists'] and not res['rc_local']['cmd_commented']):
					res['synced'] = True
			else:
				#should start with LXDE (autostart)
				if (res['settings']['start_user'] == ''):
					#should be using global
					if (res['settings']['start_mode'] == 'gui'):
						if (res['autostart']['global']['file_exists'] and res['autostart']['global']['cmd']['gui']['exists'] and not res['autostart']['global']['cmd']['gui']['commented']):
							res['synced'] = True
					else:
						if (res['autostart']['global']['file_exists'] and res['autostart']['global']['cmd']['cli']['exists'] and not res['autostart']['global']['cmd']['cli']['commented']):
							res['synced'] = True
				else:
					if (res['settings']['start_mode'] == 'gui'):
						#should start gui
						for x in res['autostart']['users']:
							if (x['user'] == res['settings']['start_user'] and x['file_exists'] and x['cmd']['gui']['exists'] and not x['cmd']['gui']['commented']):
								res['synced'] = True
					else:
						#should start the cli
						for x in res['autostart']['users']:
							if (x['file_exists'] and x['cmd']['cli']['exists'] and not x['cmd']['cli']['commented']):
								res['synced'] = True
		else:
			if (not res['rc_local']['cmd_exists'] or res['rc_local']['cmd_commented']):
				if (not res['autostart']['global']['cmd']['cli']['exists'] or res['autostart']['global']['cmd']['cli']['commented']):
					if (not res['autostart']['global']['cmd']['gui']['exists'] or res['autostart']['global']['cmd']['gui']['commented']):
						synced = True
						for x in res['autostart']['users']:
							if (x['cmd']['cli']['exists'] and not x['cmd']['cli']['commented']):
								synced = False
								break
							elif (x['cmd']['gui']['exists'] and not x['cmd']['gui']['commented']):
								synced = False
								break
						res['synced'] = synced
		return res
	def __getRcLocal(self, useCache = True):
		if (not hasattr(self, 'rc_local_cache') or not useCache):
			res = {
				'path': '/etc/rc.local',
				'file_exists': False,
				'cmd_exists': False,
				'cmd_commented': False,
				'cmd_line': -1,
				'data': None,
				'lines': []
			}
			res['file_exists'] = os.path.exists(res['path'])
			if (res['file_exists']):
				f = open(res['path'], 'r')
				res['data'] = f.read()
				f.close()
				res['lines'] = res['data'].split('\n')
				cmdLine = 0
				for l in res['lines']:
					if (self.commands['auto_rc_cli'] in l):
						if ('#' in l):
							res['cmd_commented'] = True
						res['cmd_exists'] = True
						res['cmd_line'] = cmdLine
						break;
					cmdLine += 1
			self.rc_local_cache = res
		return self.rc_local_cache
	def __getAutostart(self, useCache = True):
		if (not hasattr(self, 'autostart_cache') or not useCache):
			res = {
				'global': {
					'path': '/etc/xdg/lxsession/LXDE-pi/autostart',
					'file_exists': False,
					'cmd': {
						'cli': {
							'exists': False,
							'commented': False,
							'line': -1
						},
						'gui': {
							'exists': False,
							'commented': False,
							'line': -1
						},
					},
					'data': None,
					'lines': []
				},
				'users': []
			}
			#global
			res['global']['file_exists'] = os.path.exists(res['global']['path'])
			if (res['global']['file_exists']):
				f = open(res['global']['path'], 'r')
				res['global']['data'] = f.read()
				f.close()
				res['global']['lines'] = res['global']['data'].split('\n')
				cmdLine = 0
				for l in res['global']['lines']:
					if (self.commands['auto_lxde_cli'] in l):
						if ('#' in l):
							res['global']['cmd']['cli']['commented'] = True
						res['global']['cmd']['cli']['exists'] = True
						res['global']['cmd']['cli']['line'] = cmdLine
					if (self.commands['auto_lxde_gui'] in l):
						if ('#' in l):
							res['global']['cmd']['gui']['commented'] = True
						res['global']['cmd']['gui']['exists'] = True
						res['global']['cmd']['gui']['line'] = cmdLine
					cmdLine += 1
			#users
			for u in self.__getHomeUsers():
				asfile = {
					'user': u,
					'path': '/home/{}/.config/lxsession/LXDE-pi/autostart'.format(u),
					'file_exists': False,
					'cmd': {
						'cli': {
							'exists': False,
							'commented': False
						},
						'gui': {
							'exists': False,
							'commented': False
						},
					},
					'data': None,
					'lines': []
				}
				asfile['file_exists'] = os.path.exists(asfile['path'])
				if (asfile['file_exists']):
					f = open(asfile['path'], 'r')
					asfile['data'] = f.read()
					f.close()
					asfile['lines'] = asfile['data'].split('\n')
					cmdLine = 0
					for l in asfile['lines']:
						if (self.commands['auto_lxde_cli'] in l):
							if ('#' in l):
								asfile['cmd']['cli']['commented'] = True
							asfile['cmd']['cli']['exists'] = True
							asfile['cmd']['cli']['line'] = cmdLine
						if (self.commands['auto_lxde_gui'] in l):
							if ('#' in l):
								asfile['cmd']['gui']['commented'] = True
							asfile['cmd']['gui']['exists'] = True
							asfile['cmd']['gui']['line'] = cmdLine
						cmdLine += 1
				res['users'].append(asfile)
			self.autostart_cache = res
		return self.autostart_cache
	def __syncConfig(self):
		res = {
			'synced': False,
			'messages': []
		}
		self.startupInfo = self.__getStartupInfo(useCache=False)
		if (not self.startupInfo['synced']):
			#there's work to do
			if (self.startupInfo['settings']['enabled']):
				#should be enabled
				if (self.startupInfo['settings']['start_with'] == 'linux'):
					#should start with linux
					res['messages'].append(self.__enableRcLocal())
					res['messages'].extend(self.__disableAutostart())
					res['synced'] = True
				else:
					#should start with LXDE
					res['messages'].extend(self.__enableAutostart(self.startupInfo['settings']['start_mode'],self.startupInfo['settings']['start_user']))
					res['messages'].append(self.__disableRcLocal())
					res['synced'] = True
			else:
				#should be disabled
				res['messages'].append(self.__disableRcLocal())
				res['messages'].extend(self.__disableAutostart())
				res['synced'] = True
		else:
			res['synced'] = True
			res['messages'].append('No config changes required')
		return res
	def __enableRcLocal(self):
		res = 'Unchanged'
		if (self.startupInfo['rc_local']['file_exists']):
			if (self.startupInfo['rc_local']['cmd_exists']):
				if (not self.startupInfo['rc_local']['cmd_commented']):
					pass
				else:
					self.startupInfo['rc_local']['lines'][self.startupInfo['rc_local']['cmd_line']] = self.commands['auto_rc_cli']
					f = open(self.startupInfo['rc_local']['path'], 'w')
					f.write("\n".join(self.startupInfo['rc_local']['lines']))
					f.close()
					res = 'Uncommented'
			else:
				exitLine = -1
				el = 0
				for x in self.startupInfo['rc_local']['lines']:
					if ('exit 0' == x):
						exitLine = el
						break
					el += 1
				if (exitLine > -1):
					self.startupInfo['rc_local']['lines'].insert(exitLine,self.commands['auto_rc_cli'])
					f = open(self.startupInfo['rc_local']['path'], 'w')
					f.write("\n".join(self.startupInfo['rc_local']['lines']))
					f.close()
					res = 'Command inserted'
				else:
					res = 'Unable to locate exit line'
		else:
			res = 'File missing, highly unexpected!'
		return '/etc/rc.local: {}'.format(res)
	def __disableRcLocal(self):
		res = 'Unchanged'
		if (self.startupInfo['rc_local']['file_exists']):
			if (self.startupInfo['rc_local']['cmd_exists']):
				if (self.startupInfo['rc_local']['cmd_commented']):
					pass
				else:
					del(self.startupInfo['rc_local']['lines'][self.startupInfo['rc_local']['cmd_line']])
					f = open(self.startupInfo['rc_local']['path'], 'w')
					f.write("\n".join(self.startupInfo['rc_local']['lines']))
					f.close()
					res = 'Command removed'
		return '/etc/rc.local: {}'.format(res)
	def __enableAutostart(self, startMode = 'gui', startUser = 'pi'):
		res = self.__disableAutostart() #disable any existing autostart commands
		if (startUser == ''):
			#should be in global file
			if (not self.startupInfo['autostart']['global']['cmd'][startMode]['exists']):
				#command needs to be added
				xLine = -1
				xl = 0
				for x in self.startupInfo['autostart']['global']['lines']:
					if ('@xscreensaver' in x and not '#' in x):
						xLine = xl
					xl += 1
				if (xLine > -1):
					self.startupInfo['autostart']['global']['lines'].insert(xLine,self.commands['auto_lxde_{}'.format(startMode)])
				else:
					self.startupInfo['autostart']['global']['lines'].append(self.commands['auto_lxde_{}'.format(startMode)])
				f = open(self.startupInfo['autostart']['global']['path'], 'w')
				f.write("\n".join(self.startupInfo['autostart']['global']['lines']))
				f.close()	
				res.append('{}: Command added'.format(self.startupInfo['autostart']['global']['path']))
			elif (self.startupInfo['autostart']['global']['cmd'][startMode]['exists'] and self.startupInfo['autostart']['global']['cmd'][startMode]['commented']):
				#command needs to be uncommented
				self.startupInfo['autostart']['global']['lines'][self.startupInfo['autostart']['global']['cmd'][startMode]['line']] = self.commands['auto_lxde_{}'.format(startMode)]
				f = open(self.startupInfo['autostart']['global']['path'], 'w')
				f.write("\n".join(self.startupInfo['autostart']['global']['lines']))
				f.close()
				res.append('{}: Uncommented command'.format(self.startupInfo['autostart']['global']['path']))
		else:
			#should be in user file
			for uFile in self.startupInfo['autostart']['users']:
				if (uFile['user'] == startUser):
					#file identified
					if (not uFile['cmd'][startMode]['exists']):
						#command needs to be added
						xLine = -1
						xl = 0
						for x in uFile['lines']:
							if ('@xscreensaver' in x and not '#' in x):
								xLine = xl
							xl += 1
						if (xLine > -1):
							uFile['lines'].insert(xLine,self.commands['auto_lxde_{}'.format(startMode)])
						else:
							uFile['lines'].append(self.commands['auto_lxde_{}'.format(startMode)])
						f = open(uFile['path'], 'w')
						f.write("\n".join(uFile['lines']))
						f.close()	
						res.append('{}: Command added'.format(uFile['path']))
					elif (uFile['cmd'][startMode]['exists'] and uFile['cmd'][startMode]['commented']):
						#command needs to be uncommented
						uFile['lines'][uFile['cmd'][startMode]['line']] = self.commands['auto_lxde_{}'.format(startMode)]
						f = open(uFile['path'], 'w')
						f.write("\n".join(uFile['lines']))
						f.close()
						res.append('{}: Uncommented command'.format(uFile['path']))
					break
		return res
	def __disableAutostart(self):
		res = []
		if (self.startupInfo['autostart']['global']['cmd']['cli']['exists']):
			del(self.startupInfo['autostart']['global']['lines'][self.startupInfo['autostart']['global']['cmd']['cli']['line']])
			f = open(self.startupInfo['autostart']['global']['path'], 'w')
			f.write("\n".join(self.startupInfo['autostart']['global']['lines']))
			f.close()
			res.append('{}: CLI command removed'.format(self.startupInfo['autostart']['global']['path']))
		elif (self.startupInfo['autostart']['global']['cmd']['gui']['exists']):
			del(self.startupInfo['autostart']['global']['lines'][self.startupInfo['autostart']['global']['cmd']['gui']['line']])
			f = open(self.startupInfo['autostart']['global']['path'], 'w')
			f.write("\n".join(self.startupInfo['autostart']['global']['lines']))
			f.close()
			res.append('{}: GUI command removed'.format(self.startupInfo['autostart']['global']['path']))
		for uFile in self.startupInfo['autostart']['users']:
			if (uFile['cmd']['cli']['exists']):
				del(uFile['lines'][uFile['cmd']['cli']['line']])
				f = open(uFile['path'], 'w')
				f.write("\n".join(uFile['lines']))
				f.close()
				res.append('{}: CLI command removed'.format(uFile['path']))
			elif (uFile['cmd']['gui']['exists']):
				del(uFile['lines'][uFile['cmd']['gui']['line']])
				f = open(uFile['path'], 'w')
				f.write("\n".join(uFile['lines']))
				f.close()
				res.append('{}: GUI command removed'.format(uFile['path']))
		return res
	def __getHomeUsers(self):
		res = []
		base = '/home'
		if (os.path.exists(base)):
			dirs = os.listdir(base)
			if (any(dirs)):
				res = [ x for x in dirs if os.path.isdir(os.path.join(base,x)) ]
		return res
	def __stoptasks(self):
		""" util - stop all tasks
		"""
		for name in self.gui.scheduler.listTasks():
			self.gui.scheduler.stopTask(name)