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
import Tkinter, ttk, time, uuid
from Tkinter import *
from TkBlock import *
from TkDependencyManager import *
from SSLManager import *
from Motion import *

## UI for RPC server
class TkRPCManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes TkRPCManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkRPCManager,self).__init__(parent, gui, **options)
		self.scheduler = self.gui.scheduler
		self.now = lambda: int(round(time.time() * 1000))
		self.urlshown = None
		dependencies = [
			{'package':'OpenSSL', 'installer': 'apt-get'},
			{'package':'python-openssl', 'installer': 'apt-get'}
		]
		self.dm = TkDependencyManager(self.widget, dependencies, 'RPC Manager', self.gui)
		if(not self.dm.installRequired()):
			self.ssl = SSLManager()
			self.scheduler.addTask('rpc_url_watcher', self.__hideUrl, 10)
			try:
				self.rpcserver = TkRPCManager.rpcserver
			except:
				TkRPCManager.rpcserver = self.rpcserver = self.gui.getClass('SRPC.SRPCServer')(motionScheduler = self.gui.motionScheduler, specification = self.gui.specification, scheduler = self.gui.scheduler)
	def setup(self):
		""" setup gui menu
		"""
		self.gui.menus['rpc'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		self.gui.menus['rpc'].add_command(label="Manage Server", command=self.OnManageRPCClick)
		self.addMenu(label="RPC", menu=self.gui.menus['rpc'])
	
	#=== VIEWS ===#
	def serverManager(self):
		""" view - RPC service manager
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='RPC Server', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['serviceLabel'] = Tkinter.Label(self.widgets['tframe'],text='Service', anchor='nw', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['serviceLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.variables['status'] = Tkinter.StringVar()
		self.widgets['statusdata'] = Tkinter.Label(self.widgets['tframe'],textvariable=self.variables['status'], bg=self.colours['bg'], fg=self.colours['fg'], font=self.fonts['heading2'])
		self.widgets['statusdata'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['controlframe'] = Tkinter.Frame(self.widgets['tframe'], borderwidth=0, bg = self.colours['bg'])
		self.widgets['controlframe'].grid(column = 1, row = self.gridrow, padx=20, columnspan=2, sticky = "WENS")
		
		self.widgets['startbutton'] = Tkinter.Button(self.widgets['controlframe'],text=u"Start RPC Server", image=self.images['play'], command=self.OnStartClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['startbutton'].grid(column=1,row=0, padx=10)
		
		self.widgets['stopbutton'] = Tkinter.Button(self.widgets['controlframe'],text=u"Stop RPC Server", image=self.images['stop'], command=self.OnStopClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['stopbutton'].grid(column=2,row=0, padx=10)
		
		self.variables['autostart'] = Tkinter.BooleanVar()
		self.variables['autostart'].set(Setting.get('rpc_autostart', False))
		self.widgets['autostartentry'] = Tkinter.Checkbutton(self.widgets['controlframe'], text="Autostart", variable=self.variables['autostart'], command=self.OnToggleAutostartClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['autostartentry'].grid(column=3,row=0, padx=10)
		
		if(self.rpcserver.isRunning() == False):
			self.variables['status'].set('Stopped')
			self.widgets['startbutton'].configure(state='normal')
			self.widgets['stopbutton'].configure(state='disabled')
		else:
			self.variables['status'].set('Running')
			self.widgets['startbutton'].configure(state='disabled')
			self.widgets['stopbutton'].configure(state='normal')
		
		self.gridrow += 1
		
		self.widgets['sslLabel'] = Tkinter.Label(self.widgets['tframe'],text='SSL Certificate', anchor='nw', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['sslLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['startdateLabel'] = Tkinter.Label(self.widgets['tframe'],text='Start Date', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['startdateLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['startdateData'] = Tkinter.Label(self.widgets['tframe'],text=str(self.ssl.start), bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['startdateData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.widgets['ccframe'] = Tkinter.Frame(self.widgets['tframe'], borderwidth=0, bg = self.colours['bg'])
		self.widgets['ccframe'].grid(column = 3, row = self.gridrow, padx=20, columnspan=4, rowspan=5, sticky = "WENS")
		
		self.widgets['ccLabel'] = Tkinter.Label(self.widgets['ccframe'],text='Valid Country Codes', anchor='nw', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['ccLabel'].grid(column=0,row=0, sticky='EW')
		
		self.widgets['ccSubframe'] = Tkinter.Frame(self.widgets['ccframe'], borderwidth=0, bg = self.colours['bg'])
		self.widgets['ccSubframe'].grid(column = 0, row = 1, sticky = "WENS")
		
		r,c = 0,0
		cols = 20
		
		for s in self.ssl.countryCodes():
			self.widgets['ccLabel'+s] = Tkinter.Label(self.widgets['ccSubframe'],text=s, anchor='nw', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['ccLabel'+s].grid(column=c,row=r,sticky='EW')
			#if (c == cols-1):
			#	r += 1
			if (c < cols):
				c = c+1 
			else:
				c = 0
				r+=1
		
		self.gridrow += 1
		
		self.widgets['enddateLabel'] = Tkinter.Label(self.widgets['tframe'],text='End Date', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['enddateLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['enddateData'] = Tkinter.Label(self.widgets['tframe'],text=str(self.ssl.end), bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['enddateData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['domainLabel'] = Tkinter.Label(self.widgets['tframe'],text='Domain', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['domainLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['domain'] = Tkinter.StringVar()
		self.widgets['domainentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['domain'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['domainentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['domain'].set(Setting.get('rpc_server_ssl_domain', 'localhost'))
		
		self.gridrow += 1
		
		self.widgets['companyLabel'] = Tkinter.Label(self.widgets['tframe'],text='Company', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['companyLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['company'] = Tkinter.StringVar()
		self.widgets['companyentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['company'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['companyentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['company'].set(Setting.get('rpc_server_ssl_company', 'TestCo'))
		
		self.gridrow += 1
		
		self.widgets['countryLabel'] = Tkinter.Label(self.widgets['tframe'],text='Country', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['countryLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['country'] = Tkinter.StringVar()
		self.widgets['countryentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['country'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['countryentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['country'].set(Setting.get('rpc_server_ssl_country', 'GB'))
		
		self.gridrow += 1
		
		self.widgets['settingsLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings', anchor='nw', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['settingsLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['hostnameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Hostname', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['hostnameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['hostname'] = Tkinter.StringVar()
		self.widgets['hostnameentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['hostname'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['hostnameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['hostname'].set(Setting.get('rpc_server_hostname', 'localhost'))
		
		self.widgets['efframe'] = Tkinter.Frame(self.widgets['tframe'], borderwidth=0, bg = self.colours['bg'])
		self.widgets['efframe'].grid(column = 3, row = self.gridrow, padx=20, columnspan=6, rowspan=4, sticky = "WENS")
		
		self.widgets['efLabel'] = Tkinter.Label(self.widgets['efframe'],text='Exposed Functions', anchor='nw', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['efLabel'].grid(column=0,row=0, sticky='EW')
		
		self.widgets['efSubframe'] = Tkinter.Frame(self.widgets['efframe'], borderwidth=0, bg = self.colours['bg'])
		self.widgets['efSubframe'].grid(column = 0, row = 1, sticky = "WENS")
		r,c = 0,0
		cols = 4
		for t in self.rpcserver.listMethods():
			self.widgets[t+'Label'] = Tkinter.Label(self.widgets['efSubframe'],text=t, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets[t+'Label'].grid(column=c,row=r, padx=10,sticky='EW')
			if (c < cols):
				c = c+1 
			else:
				c = 0
				r+=1
		
		self.gridrow += 1
		
		self.widgets['portLabel'] = Tkinter.Label(self.widgets['tframe'],text='Port', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['portLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['port'] = Tkinter.IntVar()
		self.widgets['portentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['port'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['portentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['port'].set(Setting.get('rpc_server_port', 9000))
		
		self.gridrow += 1
		
		self.widgets['usernameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Username', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['usernameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['username'] = Tkinter.StringVar()
		self.widgets['usernameentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['username'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['usernameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['username'].set(Setting.get('rpc_server_username', 'remoteuser'))
		
		self.gridrow += 1
		
		self.widgets['passwordLabel'] = Tkinter.Label(self.widgets['tframe'],text='Password', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['passwordLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['password'] = Tkinter.StringVar()
		self.widgets['passwordentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['password'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['passwordentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['password'].set(Setting.get('rpc_server_password', str(uuid.uuid4())))
		
		self.widgets['genbutton'] = Tkinter.Button(self.widgets['tframe'],text=u"Generate Key", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.OnGeneratePasswordClick)
		self.widgets['genbutton'].grid(column=2,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['urlLabel'] = Tkinter.Label(self.widgets['tframe'],text='URL', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['urlLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['url'] = Tkinter.Label(self.widgets['tframe'],text='Click show or copy', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['url'].grid(column=1,row=self.gridrow, columnspan=6, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=0,row=self.gridrow, padx=5, sticky='EW')
		self.widgets['regenLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Regenerate SSL', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['regenLabel'].grid(column=1,row=self.gridrow,padx=5, sticky='EW')
		self.widgets['showUrlLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Show URL', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['showUrlLabel'].grid(column=2,row=self.gridrow,padx=5, sticky='EW')
		self.widgets['copyUrlLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Copy URL', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['copyUrlLabel'].grid(column=3,row=self.gridrow,padx=5, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['saveserver'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveServerClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['saveserver'].grid(column=0,row=self.gridrow)
		self.widgets['regen'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Regen", image=self.images['process'], command=self.OnRegenSSLClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['regen'].grid(column=1,row=self.gridrow)
		self.widgets['show'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Show", image=self.images['find'], command=self.OnShowUrlClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['show'].grid(column=2,row=self.gridrow)
		self.widgets['copy'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Copy", image=self.images['ram'], command=self.OnCopyUrlClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['copy'].grid(column=3,row=self.gridrow)
	
	#=== ACTIONS ===#
	def OnStartClick(self):
		""" action - start the RPC service
		"""
		self.variables['status'].set('Running')
		self.rpcserver.start()
		self.widgets['startbutton'].configure(state='disabled')
		self.widgets['stopbutton'].configure(state='normal')
	def OnStopClick(self):
		""" action - stop the RPC service
		"""
		self.variables['status'].set('Stopped')
		self.rpcserver.stop()
		self.widgets['startbutton'].configure(state='normal')
		self.widgets['stopbutton'].configure(state='disabled')
	def OnToggleAutostartClick(self):
		""" action - toggle RPC service autostart
		"""
		self.autostart = Setting.set('rpc_autostart', self.variables['autostart'].get())
	
	def OnManageRPCClick(self):
		""" action - display RPC service management page
		"""
		if(not self.dm.installRequired()):
			self.serverManager()
		else:
			self.open()
			self.dm.addManager()
	def OnSaveServerClick(self):
		""" action - save server config
		"""
		if(self.variables['hostname'].get() != '' and self.variables['port'].get() > 1000 and len(self.variables['username'].get()) > 4 and len(self.variables['password'].get()) > 4):
			hostname = Setting.set('rpc_server_hostname', self.variables['hostname'].get())
			port = Setting.set('rpc_server_port', self.variables['port'].get())
			username = Setting.set('rpc_server_username', self.variables['username'].get())
			password = Setting.set('rpc_server_password', self.variables['password'].get())
			self.notifier.addNotice('RPC server settings saved')
		else:
			self.notifier.addNotice('Invalid RPC server settings.', 'warning')
	def OnGeneratePasswordClick(self):
		""" action - generates a new password
		"""
		self.variables['password'].set(str(uuid.uuid4()))
		self.notifier.addNotice('New password generated. Click Save to apply it', 'warning')
	def OnRegenSSLClick(self):
		""" action - regenerates SSL certificate
		"""
		if(self.__validSSLDomain(self.variables['domain'].get())):
			if(self.__validSSLCompany(self.variables['company'].get())):
				if(self.__validSSLCountry(self.variables['country'].get())):
					domain = Setting.set('rpc_server_ssl_domain', self.variables['domain'].get())
					company = Setting.set('rpc_server_ssl_company', self.variables['company'].get())
					country = Setting.set('rpc_server_ssl_country', self.variables['country'].get())
					self.ssl.generateCertificate()
					self.notifier.addNotice('SSL Certifice regenerated successfully')
				else:
					self.notifier.addNotice('Invalid country code','error')
			else:
				self.notifier.addNotice('Invalid company name','error')
		else:
			self.notifier.addNotice('Invalid domain','error')
		self.serverManager()
	def OnShowUrlClick(self):
		""" action - shows the url based on current configuration
		"""
		url = 'https://{0}:{1}@{2}:{3}'.format(Setting.get('rpc_server_username', 'remoteuser'), Setting.get('rpc_server_password', str(uuid.uuid4())), Setting.get('rpc_server_hostname', 'localhost'), Setting.get('rpc_server_port', 9000))
		self.widgets['url'].configure(text=url)
		self.urlshown = self.now()
	def OnCopyUrlClick(self):
		""" action - copies the url to clipboard
		"""
		url = 'https://{0}:{1}@{2}:{3}'.format(Setting.get('rpc_server_username', 'remoteuser'), Setting.get('rpc_server_password', str(uuid.uuid4())), Setting.get('rpc_server_hostname', 'localhost'), Setting.get('rpc_server_port', 9000))
		self.gui.clipboard_clear()
		self.gui.clipboard_append(url)
		self.notifier.addNotice('The RPC URL has been copied to clipboard')
	
	#=== UTILS ===#
	def __hideUrl(self):
		""" util - auto hides the url after 10 seconds
		"""
		if(self.urlshown != None):
			if(self.urlshown <= self.now()-10000):
				self.widgets['url'].configure(text='Click show or copy')
				self.urlshown = None
				self.notifier.addNotice('URL hidden for security purposes')
	def __validSSLDomain(self, domain):
		""" util - validate SSL domain
		
		@param domain str
		"""
		try:
			assert len(domain) > 4
			assert not r"/" in domain
			return True
		except:
			pass
		return False
	def __validSSLCompany(self, company):
		""" util - validate SSL company
		
		@param company str
		"""
		try:
			assert len(company) > 4
			assert not r"/" in company
			return True
		except:
			pass
		return False
	def __validSSLCountry(self, country):
		""" util - validate SSL company
		
		@param country str
		"""
		try:
			assert country != ''
			assert any(country in s for s in self.ssl.countryCodes())
			return True
		except:
			pass
		return False