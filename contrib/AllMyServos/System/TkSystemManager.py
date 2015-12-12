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
from Tkinter import *
from TkBlock import *
from subprocess import Popen, PIPE

class TkSystemManager(TkPage):
	def __init__(self, parent, gui, **options):
		super(TkSystemManager,self).__init__(parent, gui, **options)
		self.patterns = {}
		self.patterns['ident'] = re.compile(r'(?P<ident>\w+)\s+Change\sLog')
		self.patterns['head'] = re.compile(r'(?P<date>Date)\s+(?P<amends>Amends)')
		self.patterns['version'] = re.compile(r'v(?P<version>(\d|\.)+)')
		self.patterns['amendstart'] = re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\s+(?P<comment>.*)')
		self.patterns['amendcont'] = re.compile(r'\s+(?P<comment>.+)')
	def setup(self):
		try:
			self.gui.menus['file']
		except:
			self.gui.menus['file'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="File", menu=self.gui.menus['file'])
		self.gui.menus['system'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		self.gui.menus['system'].add_command(label="Information", command=self.OnInformationClick)
		self.gui.menus['system'].add_separator()
		self.gui.menus['system'].add_command(label="Reboot", command=self.OnRebootClick)
		self.gui.menus['system'].add_command(label="Poweroff", command=self.OnPoweroffClick)
		self.gui.menus['file'].insert_cascade(index=1, label="System", menu=self.gui.menus['system'])
		self.gui.menus['file'].insert_command(index=10, label="Exit", command=self.OnExitClick)
	
	#=== VIEWS ===#
	def showInformation(self):
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
		
		self.widgets['pathLabel'] = Tkinter.Label(self.widgets['pysubframe'],text='System Paths', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
		self.widgets['pathLabel'].grid(column=0,row=row,sticky='EW')
		
		for p in sys.path:
			self.widgets['pathData'] = Tkinter.Label(self.widgets['pysubframe'],text=p, bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
			self.widgets['pathData'].grid(column=1,row=row,sticky='W')
			row += 1
	def amsInfo(self):
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
		
		self.widgets['achangeData'] = self.__changeLogView(self.widgets['asubframe'])
		self.widgets['achangeData'].grid(column=1,row=row,sticky='W')
	
	#=== ACTIONS ===#
	def OnInformationClick(self):
		self.showInformation()
	def OnRebootClick(self):
		self.reboot()
	def OnRebootConfirmClick(self):
		self.__stoptasks()
		time.sleep(5)
		p = Popen(['sudo','reboot'], stdout=PIPE)
		o = p.communicate()[0]
	def OnCancelRebootClick(self):
		self.showInformation()
	def OnPoweroffClick(self):
		self.poweroff()
	def OnPoweroffConfirmClick(self):
		self.__stoptasks()
		p = Popen(['sudo','poweroff'], stdout=PIPE)
		o = p.communicate()[0]
	def OnCancelPoweroffClick(self):
		self.showInformation()
	def OnExitClick(self):
		self.__stoptasks()
		self.gui.quit()
		
	#=== UTILS ===#
	def __parseChangeLog(self):
		self.currentversion = 0.01
		self.changelog = []
		self.ident = None
		self.headings = None
		filename = os.path.join(os.getcwd(), 'ChangeLog.txt')
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
	def __changeLogView(self, parent):
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
	def __stoptasks(self):
		for name in self.gui.scheduler.listTasks():
			self.gui.scheduler.stopTask(name)