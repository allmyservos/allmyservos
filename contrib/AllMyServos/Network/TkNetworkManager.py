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
import Tkinter, ttk
from Tkinter import *
from TkBlock import *
from TkDependencyManager import *
from Scheduler import *
from Setting import *
from Network import *

class TkNetworkManager(TkPage):
	def __init__(self, parent, gui, **options):
		super(TkNetworkManager,self).__init__(parent, gui, **options)
		self.pm = TkDependencyManager(self.widget, {'package':'nmap', 'installer': 'apt-get'}, 'Network Manager', self.gui)
		if(hasattr(self.gui, 'scheduler')):
			self.scheduler = self.gui.scheduler
		else:
			self.scheduler = Scheduler()
	def setup(self):
		self.gui.menus['network'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		self.gui.menus['network'].add_command(label="Neighbourhood", command=self.OnManageNetworkClick)
		self.addMenu(label="Network", menu=self.gui.menus['network'])
	
	#=== VIEWS ===#
	def listNodes(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Network / Neighbourhood', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		
		self.widgets['nframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['nframe'].grid(column=0,row=self.gridrow, sticky='EW')
		
		self.widgets['scanLabel'] = Tkinter.Label(self.widgets['nframe'],text='Scanning network... please wait.', bg=self.colours['bg'], fg=self.colours['fg'], font=self.fonts['heading2'])
		self.widgets['scanLabel'].grid(column=0,row=0,sticky='EW')
	def updateNodes(self):
		try:
			self.widgets['nodes']
		except:
			self.widgets['nodes'] = {}
		if(len(self.network.nodes) > 0):
			try:
				self.widgets['scanLabel'].grid_forget()
				del(self.widgets['scanLabel'])
			except:
				pass
			row = 0
			keys = self.network.nodes.keys()
			keys.sort()
			for k, v in self.network.nodes.iteritems():
				try:
					self.widgets['nodes'][k]
				except:
					self.widgets['nodes'][k] = Tkinter.Frame(self.widgets['nframe'], bg=self.colours['bg'])
					self.widgets['nodes'][k].grid(column=0,row=row, sticky='EW')
					
					text = v['ip']
					if(self.network.myip == v['ip']):
						text = '{0} (Me)'.format(v['ip'])
						
					self.widgets['ip'.format(k)] = Tkinter.Label(self.widgets['nodes'][k],text=text, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
					self.widgets['ip'.format(k)].grid(column=0,row=0,sticky='EW')
					
					self.widgets['macLabel'.format(k)] = Tkinter.Label(self.widgets['nodes'][k],text='Mac Address', bg=self.colours['bg'], fg=self.colours['headingfg'])
					self.widgets['macLabel'.format(k)].grid(column=0,row=1,sticky='EW')
					
					self.widgets['macData'.format(k)] = Tkinter.Label(self.widgets['nodes'][k],text=v['mac'], bg=self.colours['bg'], fg=self.colours['fg'])
					self.widgets['macData'.format(k)].grid(column=1,row=1,sticky='EW')
					
					self.widgets['brandLabel'.format(k)] = Tkinter.Label(self.widgets['nodes'][k],text='Brand', bg=self.colours['bg'], fg=self.colours['headingfg'])
					self.widgets['brandLabel'.format(k)].grid(column=0,row=2,sticky='EW')
					
					self.widgets['brandData'.format(k)] = Tkinter.Label(self.widgets['nodes'][k],text=v['brand'], bg=self.colours['bg'], fg=self.colours['fg'])
					self.widgets['brandData'.format(k)].grid(column=1,row=2,sticky='EW')
					
					self.widgets['servicesLabel'.format(k)] = Tkinter.Label(self.widgets['nodes'][k],text='Services', bg=self.colours['bg'], fg=self.colours['headingfg'])
					self.widgets['servicesLabel'.format(k)].grid(column=0,row=3,sticky='EW')
					
					self.widgets['servicesData'.format(k)] = Tkinter.Frame(self.widgets['nodes'][k], bg=self.colours['bg'])
					self.widgets['servicesData'.format(k)].grid(column=1,row=3,sticky='EW')
					srow = 0
					
					self.widgets['portLabel'.format(srow)] = Tkinter.Label(self.widgets['servicesData'.format(k)],text='Port', bg=self.colours['bg'], fg=self.colours['headingfg'])
					self.widgets['portLabel'.format(srow)].grid(column=0,row=srow,sticky='EW')
					
					self.widgets['protocolLabel'.format(srow)] = Tkinter.Label(self.widgets['servicesData'.format(k)],text='Protocol', bg=self.colours['bg'], fg=self.colours['headingfg'])
					self.widgets['protocolLabel'.format(srow)].grid(column=1,row=srow,sticky='EW')
					
					self.widgets['stateLabel'.format(srow)] = Tkinter.Label(self.widgets['servicesData'.format(k)],text='State', bg=self.colours['bg'], fg=self.colours['headingfg'])
					self.widgets['stateLabel'.format(srow)].grid(column=2,row=srow,sticky='EW')
					
					self.widgets['serviceLabel'.format(srow)] = Tkinter.Label(self.widgets['servicesData'.format(k)],text='Service', bg=self.colours['bg'], fg=self.colours['headingfg'])
					self.widgets['serviceLabel'.format(srow)].grid(column=3,row=srow,sticky='EW')
					
					srow += 1
					
					for s in v['services']:
						self.widgets['port'.format(srow)] = Tkinter.Label(self.widgets['servicesData'.format(k)],text=s['port'], bg=self.colours['bg'], fg=self.colours['fg'])
						self.widgets['port'.format(srow)].grid(column=0,row=srow,sticky='EW')
						self.widgets['protocol'.format(srow)] = Tkinter.Label(self.widgets['servicesData'.format(k)],text=s['protocol'], bg=self.colours['bg'], fg=self.colours['fg'])
						self.widgets['protocol'.format(srow)].grid(column=1,row=srow,sticky='EW')
						self.widgets['state'.format(srow)] = Tkinter.Label(self.widgets['servicesData'.format(k)],text=s['state'], bg=self.colours['bg'], fg=self.colours['fg'])
						self.widgets['state'.format(srow)].grid(column=2,row=srow,sticky='EW')
						self.widgets['service'.format(srow)] = Tkinter.Label(self.widgets['servicesData'.format(k)],text=s['service'], bg=self.colours['bg'], fg=self.colours['fg'])
						self.widgets['service'.format(srow)].grid(column=3,row=srow,sticky='EW')
						srow += 1
				row += 1
	
	#=== ACTIONS ===#
	def OnManageNetworkClick(self):
		if(not self.pm.installRequired()):
			try:
				self.network
			except:
				self.network = Network()
			try:
				self.widgets['nodes']
			except:
				self.widgets['nodes'] = {}
			for v in self.widgets['nodes'].values():
				v.grid_forget()
			self.widgets['nodes'] = {}
			self.listNodes()
			self.scheduler.addTask('network_nodes', self.updateNodes, 5)
		else:
			self.open()
			self.pm.addManager()