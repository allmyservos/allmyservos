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
import Tkinter, ttk, re, os, json
from Tkinter import *
from Setting import *
from Notifier import *
from subprocess import Popen, PIPE
from copy import copy
from distutils.version import StrictVersion

class TkDependencyManager(object):
	def __init__(self, parent, dependencies, module, gui):
		'''
		parent: a tkinter frame
		dependencies: required packages - examples:
			single dependency: { 'package': 'nmap', 'installer': 'apt-get' }
			multi dependency: [{ 'package': 'tk8.5-dev', 'installer': 'apt-get' }, { 'package': 'pillow', 'installer': 'pip', 'version': 'latest' }]
		module: the name of the module which initialized the package manager
		gui: reference to the main tkinter app
		'''
		self.widgets = {}
		self.variables = {}
		if(isinstance(dependencies, dict)):
			self.dependencies = [dependencies]
		elif(isinstance(dependencies, list)):
			self.dependencies = dependencies
		else:
			self.dependencies = dependencies
		self.module = module
		self.gui = gui
		self.notifier = Notifier()
		self.aptGet = { 'install': ['sudo','apt-get','-q','-y','install'], 'remove': ['sudo','apt-get','-q','-y','remove'] }
		self.pip = { 'install': ['sudo', 'pip','-q', 'install'], 'remove': ['sudo', 'pip','-q', 'uninstall'] }
		self.loadCache()
		self.colours = self.gui.colours
		self.images = self.gui.images
		self.fonts = self.gui.fonts
		self.widget = Frame(parent,bg=self.colours['bg'], borderwidth=0, highlightthickness=0)
		self.widget.grid(column=0,row=0,sticky='EW')
	
	def addManager(self):
		'''
		called by requesting module if install / upgrade is required
		'''
		self.gridrow = 0
		self.checkDependencies()
	
	#=== VIEWS ===#
	def checkDependencies(self):
		'''
		view - displays the result of the dependency checks
		'''
		self.open()
		
		self.widgets['tlabel'] = Tkinter.Label(self.widgets['tframe'],text='Dependencies / Installation', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['tlabel'].grid(column=0,row=self.gridrow, columnspan=2,sticky='EW')
		self.gridrow += 1
			
		self.widgets['moduleLabel'] = Tkinter.Label(self.widgets['tframe'],text='Module', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['moduleLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['moduleData'] = Tkinter.Label(self.widgets['tframe'],text=self.module, anchor='w', bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['moduleData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['dependencyLabel'] = Tkinter.Label(self.widgets['tframe'],text='Dependencies', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['dependencyLabel'].grid(column=0,row=self.gridrow,sticky='N')
		
		i = 0
		for d in self.dependencies:
			self.widgets['pframe'+str(i)] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['rowaltbg'])
			self.widgets['pframe'+str(i)].grid(column=1,row=self.gridrow, pady=10, sticky='EW')
			
			self.widgets['name{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['package'], bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['name{0}'.format(i)].grid(column=0,row=0, ipadx=15,sticky='EW')
			
			self.widgets['installerLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Installer', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['installerLabel{0}'.format(i)].grid(column=1,row=0,ipadx=5,sticky='EW')
			self.widgets['installer{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['installer'], bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
			self.widgets['installer{0}'.format(i)].grid(column=2,row=0,ipadx=5,sticky='W')
			
			self.widgets['installLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Install Command', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['installLabel{0}'.format(i)].grid(column=1,row=1,ipadx=5,sticky='EW')
			self.widgets['i{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['icom'], bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=1)
			self.widgets['i{0}'.format(i)].grid(column=2,row=1,ipadx=5,sticky='W')
			
			self.widgets['removeLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Uninstall Command', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['removeLabel{0}'.format(i)].grid(column=1,row=2,ipadx=5,sticky='EW')
			self.widgets['r{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['rcom'], bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=1)
			self.widgets['r{0}'.format(i)].grid(column=2,row=2,ipadx=5,sticky='W')
			
			status = 'installed'
			if(d['status']==0): status = 'not installed'
			elif(d['status']==1): status = 'upgrade required'
			self.widgets['statusLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Status', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['statusLabel{0}'.format(i)].grid(column=1,row=3,ipadx=5,sticky='EW')
			self.widgets['installed{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=status, bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
			self.widgets['installed{0}'.format(i)].grid(column=2,row=3,ipadx=5,sticky='W')
			i+=1
			self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.gridrow = 0
		self.widgets['installLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Install', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['installLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['install'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Install", image=self.images['accept'], command=self.OnInstallClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['install'].grid(column=0,row=self.gridrow)
	def success(self):
		'''
		view - displays in the event of a successful installation
		'''
		self.open()
		self.widgets['tlabel'] = Tkinter.Label(self.widgets['tframe'],text='Dependencies / Installation / Success', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['tlabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['moduleLabel'] = Tkinter.Label(self.widgets['tframe'],text='Module', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['moduleLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['moduleData'] = Tkinter.Label(self.widgets['tframe'],text=self.module, anchor='w', bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['moduleData'].grid(column=1,row=self.gridrow, ipadx=15, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['dependencyLabel'] = Tkinter.Label(self.widgets['tframe'],text='Dependencies', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['dependencyLabel'].grid(column=0,row=self.gridrow,sticky='N')
		
		i = 0
		for d in self.dependencies:
			self.widgets['pframe'+str(i)] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['rowaltbg'])
			self.widgets['pframe'+str(i)].grid(column=1,row=self.gridrow, pady=10, sticky='EW')
			
			self.widgets['name{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['package'], bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['name{0}'.format(i)].grid(column=0,row=0, ipadx=15,sticky='EW')
			
			self.widgets['installerLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Installer', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['installerLabel{0}'.format(i)].grid(column=1,row=0,ipadx=5,sticky='EW')
			self.widgets['installer{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['installer'], bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
			self.widgets['installer{0}'.format(i)].grid(column=2,row=0,ipadx=5,sticky='W')
			
			self.widgets['installLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Install Command', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['installLabel{0}'.format(i)].grid(column=1,row=1,ipadx=5,sticky='EW')
			self.widgets['i{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['icom'], bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=1)
			self.widgets['i{0}'.format(i)].grid(column=2,row=1,ipadx=5,sticky='W')
			
			self.widgets['removeLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Uninstall Command', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['removeLabel{0}'.format(i)].grid(column=1,row=2,ipadx=5,sticky='EW')
			self.widgets['r{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['rcom'], bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=1)
			self.widgets['r{0}'.format(i)].grid(column=2,row=2,ipadx=5,sticky='W')
			
			status = 'installed'
			if(d['status']==0): status = 'not installed'
			elif(d['status']==1): status = 'upgrade required'
			self.widgets['statusLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Status', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['statusLabel{0}'.format(i)].grid(column=1,row=3,ipadx=5,sticky='EW')
			self.widgets['installed{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=status, bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
			self.widgets['installed{0}'.format(i)].grid(column=2,row=3,ipadx=5,sticky='W')
			i+=1
			self.gridrow += 1
		
		self.widgets['info'] = Tkinter.Label(self.widgets['tframe'],text='All dependencies were installed successfully.', bg=self.colours['bg'], fg=self.colours['fg'], height=3)
		self.widgets['info'].grid(column=0,row=self.gridrow, columnspan = 2, sticky='EW')
		self.gridrow += 1
		self.widgets['info'] = Tkinter.Label(self.widgets['tframe'],text='Restart the interface and reopen the {0} module.'.format(self.module), bg=self.colours['bg'], fg=self.colours['headingfg'], height=3)
		self.widgets['info'].grid(column=0,row=self.gridrow, columnspan = 2, sticky='EW')
	def failure(self):
		'''
		view - displays in the event of an unsuccessful installation
		'''
		self.open()
		self.widgets['tlabel'] = Tkinter.Label(self.widgets['tframe'],text='Dependencies / Installation / Failure', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['tlabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['moduleLabel'] = Tkinter.Label(self.widgets['tframe'],text='Module', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['moduleLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['moduleData'] = Tkinter.Label(self.widgets['tframe'],text=self.module, anchor='nw', bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['moduleData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['dependencyLabel'] = Tkinter.Label(self.widgets['tframe'],text='Dependencies', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['dependencyLabel'].grid(column=0,row=self.gridrow,sticky='N')
		
		i = 0
		for d in self.dependencies:
			self.widgets['pframe'+str(i)] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['rowaltbg'])
			self.widgets['pframe'+str(i)].grid(column=1,row=self.gridrow, pady=10, sticky='EW')
			
			self.widgets['name{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['package'], bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['name{0}'.format(i)].grid(column=0,row=0, ipadx=15,sticky='EW')
			
			self.widgets['installerLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Installer', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['installerLabel{0}'.format(i)].grid(column=1,row=0,ipadx=5,sticky='EW')
			self.widgets['installer{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['installer'], bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
			self.widgets['installer{0}'.format(i)].grid(column=2,row=0,ipadx=5,sticky='W')
			
			self.widgets['installLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Install Command', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['installLabel{0}'.format(i)].grid(column=1,row=1,ipadx=5,sticky='EW')
			self.widgets['i{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['icom'], bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=1)
			self.widgets['i{0}'.format(i)].grid(column=2,row=1,ipadx=5,sticky='W')
			
			self.widgets['removeLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Uninstall Command', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['removeLabel{0}'.format(i)].grid(column=1,row=2,ipadx=5,sticky='EW')
			self.widgets['r{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=d['rcom'], bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=1)
			self.widgets['r{0}'.format(i)].grid(column=2,row=2,ipadx=5,sticky='W')
			
			status = 'installed'
			if(d['status']==0): status = 'not installed'
			elif(d['status']==1): status = 'upgrade required'
			self.widgets['statusLabel{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text='Status', bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
			self.widgets['statusLabel{0}'.format(i)].grid(column=1,row=3,ipadx=5,sticky='EW')
			self.widgets['installed{0}'.format(i)] = Tkinter.Label(self.widgets['pframe'+str(i)],text=status, bg=self.colours['rowaltbg'], fg=self.colours['valuefg'], height=2)
			self.widgets['installed{0}'.format(i)].grid(column=2,row=3,ipadx=5,sticky='W')
			i+=1
			self.gridrow += 1
		
		self.widgets['info'] = Tkinter.Label(self.widgets['tframe'],text='One or more dependencies failed to install.', bg=self.colours['bg'], fg=self.colours['fg'], height=3)
		self.widgets['info'].grid(column=0,row=self.gridrow, columnspan = 2, sticky='EW')
		self.gridrow += 1
		self.widgets['info'] = Tkinter.Label(self.widgets['tframe'],text='Please restart the interface and try again.', bg=self.colours['bg'], fg=self.colours['headingfg'], height=3)
		self.widgets['info'].grid(column=0,row=self.gridrow, columnspan = 2, sticky='EW')
	
	#=== ACTIONS ===#
	def OnInstallClick(self):
		'''
		action - performs installation
		'''
		self.close()
		fails = []
		for k, v in enumerate(self.dependencies):
			if(not self.isInstalled(v)):
				if(self.__installDependency(v)):
					self.dependencies[k]['status'] = 2
					self.notifier.addNotice('{0} installation complete'.format(v['package']))
				else:
					self.dependencies[k]['status'] = 0
					self.notifier.addNotice('{0} installation failed'.format(v['package']), 'error')
					fails.append(v)
			else:
				self.dependencies[k]['status'] = 2
		if(any(fails)):
			self.failure()
		else:
			self.success()
	
	#=== UTILS ===#
	def loadCache(self):
		'''
		initialises the dependency cache either with stored data or an empty dict 
		'''
		self.cache = {}
		self.cachepath = os.path.join(os.getcwd(), 'files', 'Dependencies')
		self.cachefile = os.path.join(self.cachepath, '{}-cache.json'.format(self.__safeName()))
		if os.path.isfile(self.cachefile):
			try:
				f = open(self.cachefile, 'r')
				contents = f.read()
				f.close()
				self.cache = json.loads(contents)
			except:
				pass
	
	def installRequired(self):
		'''
		returns a bool indicating whether or not any dependencies require installation
		'''
		if('required' in self.cache.keys()):
			if(not self.cache['required']):
				return False #only use cached result if installation is not required
		required = False
		for d in self.dependencies:
			try:
				if(d['status'] != 2):
					required = True
			except:
				d['status'] = self.isInstalled(d)
				if(d['status'] != 2):
					required = True
		self.cache = {
			'dependencies': self.dependencies,
			'required': required
		}
		if not os.path.exists(self.cachepath):
			os.makedirs(self.cachepath)
		f = open(self.cachefile, 'w')
		f.write(json.dumps(self.cache))
		f.close()
		return required
	def isInstalled(self, dependency):
		'''
		returns status: 0 = not installed, 1 = upgrade required, 2 = installed
		'''
		status = 0
		if(dependency['installer'] == 'apt-get'):
			if(len(dependency['package']) > 0):
				dependency['icom'] = copy(self.aptGet['install']) #install command
				dependency['icom'].append(dependency['package'])
				dependency['rcom'] = copy(self.aptGet['remove']) #remove command
				dependency['rcom'].append(dependency['package'])
				p = Popen(['dpkg','-s',dependency['package']], stdout=PIPE, stderr=PIPE)
				o = p.communicate()[0]
				if(p.returncode == 0):
					o = o.split('\n')
					pattern = re.compile(r'Status\:\s?(?P<status>.+)')
					for l in o:
						if(pattern.match(l)):
							status = 2
							break
		elif(dependency['installer'] == 'pip'):
			if(len(dependency['package']) > 0):
				dependency['icom'] = copy(self.pip['install'])
				dependency['icom'].append(dependency['package'])
				dependency['rcom'] = copy(self.pip['remove'])
				dependency['rcom'].append(dependency['package'])
				p = Popen(['pip','search',dependency['package']], stdout=PIPE)
				o = p.communicate()[0]
				if(p.returncode == 0):
					o = o.split('\n')
					pattern = re.compile(r'(?P<package>[^\s]+)\s+-\s+(?P<description>.+)')
					installedpattern = re.compile(r'.*installed:\s+(?P<version>.*)',re.IGNORECASE)
					packagematch = -1
					line = 0
					for l in o:
						matches = pattern.match(l)
						if(matches):
							if(matches.group('package').lower() == dependency['package'].lower()):
								packagematch = line
						matches = installedpattern.match(l)
						if(matches and packagematch == line-1):
							v = matches.group('version')
							dv = str(dependency['version'])
							num = v.split(' ')[0]
							if(dv == 'latest' and 'latest' in v):
								status = 2
							elif(dv != 'latest' and StrictVersion(dv) <= StrictVersion(num)):
								status = 2
							else:
								status = 1
								dependency['icom'].append('--upgrade')
							break
						line += 1
		return status
	def __installDependency(self, dependency):
		if(dependency['installer'] == 'apt-get'):
			return self.__installAptGetDependency(dependency)
		elif(dependency['installer'] == 'pip'):
			return self.__installPipDependency(dependency)
	def __installAptGetDependency(self, dependency):
		installed = False
		try:
			if(len(dependency['package']) > 0):
				command = copy(self.aptGet['install'])
				command.append(dependency['package'])
				p = Popen(command, stdout=PIPE)
				o = p.communicate()[0]
				if(p.returncode == 0):
					installed = True
		except:
			pass
		return installed
	def __installPipDependency(self, dependency):
		installed = False
		try:
			if(len(dependency['package']) > 0):
				command = copy(self.pip['install'])
				command.append(dependency['package'])
				try:
					if(dependency['status'] == 1):
						command.append('--upgrade')
				except:
					pass
				p = Popen(command, stdout=PIPE)
				o = p.communicate()[0]
				if(p.returncode == 0):
					installed = True
		except:
			pass
		return installed
	def __safeName(self):
		return self.module.replace(' ', '')
	def open(self):
		for k, v in self.widgets.iteritems():
			v.grid_forget()
		self.widgets = {}
		self.widget.grid(column=0,row=0)
		self.gridrow = 0
		self.widgets['tframe'] = Frame(self.widget,bg=self.colours['bg'])
		self.widgets['tframe'].grid(column=0,row=0,sticky='EW')
	def close(self):
		self.widget.grid_forget()