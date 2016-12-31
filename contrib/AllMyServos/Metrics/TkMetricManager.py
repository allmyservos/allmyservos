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
import Tkinter, math
from Tkinter import *
from TkBlock import *
from Setting import *
from Metric import *
import ttk
import datetime

## UI for metrics
class TkMetricManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes TkMetricManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkMetricManager,self).__init__(parent, gui, **options)
		self.m = Metric('placeholder', archive = False)
		self.index = self.m.getIndex()
		self.sessions = self.index['sessions']
		self.metrics = self.index['metrics']
		self.scales = {
			'hour': (23, 240),
			'minute': (59, 600),
			'second': (59, 600),
			'millisecond': (999, 1000)
		}
		self.shapes = {}
		self.resolutions = { 'day': 86400.0, 'hour': 3600.0, 'minute': 60.0, 'second': 1.0, 'millisecond': 0.001}
	def setup(self):
		""" setup gui menu
		"""
		self.gui.menus['metrics'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
		self.gui.menus['metrics'].add_command(label="Snapshot", command=self.OnSnapshotClick)
		self.gui.menus['metrics'].add_command(label="History", command=self.OnListMetricsClick)
		self.addMenu(label="Metrics", menu=self.gui.menus['metrics'])
	
	#=== VIEWS ===#
	def listMetrics(self):
		""" view - display a list of metrics
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Metrics / History', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['hotvalues'] = Tkinter.Button(self.widgets['tframe'],text=u"Snapshot", image=self.images['ram'], command=self.OnSnapshotClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['hotvalues'].grid(column=1,row=self.gridrow)
		
		self.gridrow += 1
		
		if(len(self.metrics) > 0):
			keys = self.metrics.keys()
			keys.sort()
			
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Metric', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['sessionsLabel'] = Tkinter.Label(self.widgets['tframe'],text='Sessions', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['sessionsLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['viewLabel'] = Tkinter.Label(self.widgets['tframe'],text='View', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['viewLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			
			for k in keys:
				self.widgets['{0}MetricLabel'.format(k)] = Tkinter.Label(self.widgets['tframe'],text=k, anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
				self.widgets['{0}MetricLabel'.format(k)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['{0}SessionLabel'.format(k)] = Tkinter.Label(self.widgets['tframe'],text=len(self.metrics[k]), anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
				self.widgets['{0}SessionLabel'.format(k)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['{0}View'.format(k)] = Tkinter.Button(self.widgets['tframe'],text=u"View", image=self.images['find'], command=lambda x = k:self.OnViewMetricClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
				self.widgets['{0}View'.format(k)].grid(column=2,row=self.gridrow)
				self.gridrow += 1
	def viewMetric(self):
		""" view - browse metric archives
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Metrics / View Metric', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow, columnspan=2, sticky='EW')
		self.gridrow += 1
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Metric Name', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['nameData'] = Tkinter.Label(self.widgets['tframe'],text=self.metric.name, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['nameData'].grid(column=1,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		sessions = self.metrics[self.metric.name]
		if(any(sessions)):
			self.widgets['dayLabel'] = Tkinter.Label(self.widgets['tframe'],text='Day', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['dayLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['monthLabel'] = Tkinter.Label(self.widgets['tframe'],text='Month', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['monthLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['yearLabel'] = Tkinter.Label(self.widgets['tframe'],text='Year', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['yearLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['yearLabel'] = Tkinter.Label(self.widgets['tframe'],text='Archive', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['yearLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['viewLabel'] = Tkinter.Label(self.widgets['tframe'],text='View', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
			self.widgets['viewLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			for s in sessions:
				self.widgets['dLabel'] = Tkinter.Label(self.widgets['tframe'],text=s[1]['day'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
				self.widgets['dLabel'].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['mLabel'] = Tkinter.Label(self.widgets['tframe'],text=s[1]['month'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
				self.widgets['mLabel'].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['yLabel'] = Tkinter.Label(self.widgets['tframe'],text=s[1]['year'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
				self.widgets['yLabel'].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['yLabel'] = Tkinter.Label(self.widgets['tframe'],text='warm' if not s[2] else 'cold', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
				self.widgets['yLabel'].grid(column=3,row=self.gridrow,sticky='EW')
				self.widgets['view'] = Tkinter.Button(self.widgets['tframe'],text=u"View", image=self.images['find'], command=lambda x = s[0]:self.OnViewMetricSessionClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
				self.widgets['view'].grid(column=4,row=self.gridrow)
				self.gridrow += 1
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['tframe'],text='This metric currently has no sessions.', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['noLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Cancel", image=self.images['back'], command=self.OnListMetricsClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
	def viewMetricSession(self):
		""" view - browse metric sessions
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Metrics / View Metric', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow, columnspan=2, sticky='EW')
		self.gridrow += 1
		
		self.widgets['iframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['iframe'].grid(column=0,row=self.gridrow, sticky='W')
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['iframe'],text='Metric Name', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=0,sticky='EW')
		self.widgets['nameData'] = Tkinter.Label(self.widgets['iframe'],text=self.metric.name, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['nameData'].grid(column=1,row=0,sticky='EW')
		
		self.widgets['startLabel'] = Tkinter.Label(self.widgets['iframe'],text='Session Start', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['startLabel'].grid(column=0,row=1,sticky='EW')
		self.widgets['startData'] = Tkinter.Label(self.widgets['iframe'],text=str(self.sessionstart), bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['startData'].grid(column=1,row=1,sticky='EW')
		
		self.widgets['endLabel'] = Tkinter.Label(self.widgets['iframe'],text='Session End', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['endLabel'].grid(column=2,row=1,sticky='EW')
		self.widgets['endData'] = Tkinter.Label(self.widgets['iframe'],text=str(self.sessionend), bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['endData'].grid(column=3,row=1,sticky='EW')
		
		self.widgets['rangeStartLabel'] = Tkinter.Label(self.widgets['iframe'],text='Range Start', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['rangeStartLabel'].grid(column=0,row=2,sticky='EW')
		self.widgets['rangeStartData'] = Tkinter.Label(self.widgets['iframe'],text=str(datetime.datetime.fromtimestamp(self.times['rangestart'])), bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['rangeStartData'].grid(column=1,row=2,sticky='EW')
		
		self.widgets['rangeEndLabel'] = Tkinter.Label(self.widgets['iframe'],text='Range End', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['rangeEndLabel'].grid(column=2,row=2,sticky='EW')
		self.widgets['rangeEndData'] = Tkinter.Label(self.widgets['iframe'],text=str(datetime.datetime.fromtimestamp(self.times['rangeend'])), bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['rangeEndData'].grid(column=3,row=2,sticky='EW')
		
		self.widgets['resolutionLabel'] = Tkinter.Label(self.widgets['iframe'],text='Resolution', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['resolutionLabel'].grid(column=0,row=3,sticky='EW')
		self.widgets['resolutionData'] = Tkinter.Label(self.widgets['iframe'],text=self.resolution, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['resolutionData'].grid(column=1,row=3,sticky='EW')
		
		self.widgets['resolutionLabel'] = Tkinter.Label(self.widgets['iframe'],text='Values in Range', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['resolutionLabel'].grid(column=2,row=3,sticky='EW')
		self.widgets['resolutionData'] = Tkinter.Label(self.widgets['iframe'],text=len(self.vals), bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['resolutionData'].grid(column=3,row=3,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['tlframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['tlframe'].grid(column=0,row=self.gridrow, sticky='W')
		
		self.widgets['valuemap'] = Tkinter.Canvas(self.widgets['tlframe'], borderwidth=0, bg=self.colours['trough'], highlightthickness=0, width=self.scales[self.resolution][1], height=20)
		self.widgets['valuemap'].grid(column=1,row=0, padx=2, sticky='W')
		
		self.variables['time'] = Tkinter.IntVar()
		self.widgets['timeline'] = Tkinter.Scale(self.widgets['tlframe'], from_=0, to=self.scales[self.resolution][0], variable=self.variables['time'], command=self.updateMetricValues, resolution=1, orient=Tkinter.HORIZONTAL, length = self.scales[self.resolution][1], bg=self.colours['inputbg'], fg=self.colours['fg'], activebackground=self.colours['handle'], troughcolor=self.colours['trough'])
		self.widgets['timeline'].grid(column=1,row=1, sticky='W')
		if(self.resolution != 'millisecond'):
			self.widgets['change'] = Tkinter.Button(self.widgets['tlframe'],text=u"Change", image=self.images['find'], command=self.OnRaiseResolutionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['change'].grid(column=2,row=1, sticky='W')
		
		self.updateValueMap()
		
		self.gridrow += 1
		
		self.widgets['vframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['vframe'].grid(column=0,row=self.gridrow, sticky='W')
		self.widgets['showingLabel'] = Tkinter.Label(self.widgets['vframe'],text='Now showing', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['showingLabel'].grid(column=0,row=0,sticky='EW')
		self.widgets['currentData'] = Tkinter.Label(self.widgets['vframe'],text=str(self.start), bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['currentData'].grid(column=1,row=0,sticky='EW')
		self.widgets['dashLabel'] = Tkinter.Label(self.widgets['vframe'],text='-', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['dashLabel'].grid(column=2,row=0, padx=10, sticky='EW')
		self.widgets['recordData'] = Tkinter.Label(self.widgets['vframe'],text='No Record', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['recordData'].grid(column=3,row=0,sticky='EW')
		self.widgets['dataLabel'] = Tkinter.Label(self.widgets['vframe'],text='Value(s)',anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['dataLabel'].grid(column=0,row=1, ipady=10, ipadx=10, sticky='NW')
		self.widgets['dframe'] = Tkinter.Frame(self.widgets['vframe'], bg=self.colours['bg'])
		self.widgets['dframe'].grid(column=1,row=1, sticky='W')
		self.gridrow += 1
	
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backlabel'] = Tkinter.Label(self.widgets['optionsFrame'],text="Back", bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Cancel", image=self.images['back'], command=self.OnLowerResolutionClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
	def updateMetricValues(self, time):
		""" adds / updates the value of a metric given the time and resolution of the view
		"""
		time = int(time)
		self.times['currentstart'] = self.times['rangestart'] + time * self.resolutions[self.resolution]
		self.times['currentend'] = self.times['currentstart'] + self.resolutions[self.resolution]
		try:
			self.widgets['currentData'].configure(text=str(datetime.datetime.fromtimestamp(self.times['currentstart'])))
		except:
			return #first time round this has not been defined and the initial value is correct
		if(any(self.vals)):
			v = [x for x in self.vals if float(x.timestamp)/1000 >= self.times['currentstart'] and float(x.timestamp)/1000 <= self.times['currentend'] ]
			if(any(v)):
				self.wipeDataView()
				self.widgets['recordData'].configure(text='Recorded at: {}'.format(str(datetime.datetime.fromtimestamp(v[0].timestamp/1000))), fg=self.colours['valuefg'])
				self.widgets['dataview'] = self.genericView(self.widgets['dframe'], v[0].datavalue)
				self.widgets['dataview'].grid(column=0,row=0,sticky='EW')
			else:
				self.widgets['recordData'].configure(text='No Record', fg=self.colours['fg'])
				try:
					self.widgets['dataview']
				except:
					self.widgets['dataview'] = self.genericView(self.widgets['dframe'], 'TBD')
					self.widgets['dataview'].grid(column=0,row=0,sticky='EW')
		else:
			self.widgets['recordData'].configure(text='No Record', fg=self.colours['fg'])
			self.wipeDataView()
			self.widgets['dataview'] = self.genericView(self.widgets['dframe'], 'TBD')
			self.widgets['dataview'].grid(column=0,row=0,sticky='EW')
		self.updateValueMapMarker()
	def updateValueMap(self):
		"""adds shapes on the value map based on the time of each loaded MetricValue
		happens when the view is refreshed (change of resolution or first load
		"""
		unit = self.scales[self.resolution][1] / self.scales[self.resolution][0]
		for v in self.vals:
			indent = (v.timestamp / 1000.0 - self.times['rangestart'])
			if(self.resolution != 'millisecond'):
				indent /= self.resolutions[self.resolution]
			else:
				indent *= 1000
			units = 0
			while(units < indent):
				units += 1
			units -= 1
			if(self.resolution != 'millisecond'):
				indent = units * unit
			self.shapes['v{}'.format(indent)] = self.widgets['valuemap'].create_rectangle((indent,0,indent+10, 20), fill=self.colours['valuefg'], tags='value')
	def updateValueMapMarker(self):
		""" updates value map marker
		"""
		offset = float(self.variables['time'].get())
		if(self.resolution != 'millisecond'):
			unit = self.scales[self.resolution][1] / self.scales[self.resolution][0]
			offset *= unit
		else:
			unit = 10
		try:
			self.widgets['valuemap'].coords(self.shapes['marker'],offset,0,offset+unit,10)
		except:
			self.shapes['marker'] = self.widgets['valuemap'].create_rectangle((offset,0,offset+unit, 10), outline=self.colours['unitblue1'], tags='marker')
		self.widgets['valuemap'].tag_raise('marker')
		self.widgets['valuemap'].tag_lower('value')
	def wipeDataView(self):
		""" clears dataview ui
		"""
		try:
			self.widgets['dataview'].grid_forget()
			del(self.widgets['dataview'])
		except:
			pass
	def showSnapshot(self):
		""" view - displays in memory values for all metrics
		"""
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Metrics / Snapshot', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		if(len(Metric.metrics) > 0):
			for k,v in Metric.metrics.iteritems():
				self.widgets['mframe'+k] = Tkinter.Frame(self.widgets['tframe'], borderwidth=0, highlightthickness=0, bg=self.colours['bg'])
				self.widgets['mframe'+k].grid(column=0,row=self.gridrow,sticky='EW')
				row = 0
				
				self.widgets['hframe'+k] = Tkinter.Frame(self.widgets['mframe'+k], borderwidth=0, highlightthickness=0, bg=self.colours['bg'])
				self.widgets['hframe'+k].grid(column=0,row=0, columnspan=2,sticky='EW')
				
				self.widgets['valuesLabel'+k] = Tkinter.Label(self.widgets['mframe'+k],text='Values', anchor='nw', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
				self.widgets['valuesLabel'+k].grid(column=0,row=1,padx=10, sticky='NWSE')
				
				self.widgets['vframe'+k] = Tkinter.Frame(self.widgets['mframe'+k], borderwidth=0, highlightthickness=0, bg=self.colours['bg'])
				self.widgets['vframe'+k].grid(column=1,row=1,sticky='EW')
				
				info = v.getInfo()
				self.widgets['nameLabel'+k] = Tkinter.Label(self.widgets['hframe'+k],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
				self.widgets['nameLabel'+k].grid(column=0,row=row, padx=10, sticky='EW')
				self.widgets['nameData'+k] = Tkinter.Label(self.widgets['hframe'+k],text=info['name'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
				self.widgets['nameData'+k].grid(column=1,row=row,sticky='EW')
				
				self.widgets['typeLabel'+k] = Tkinter.Label(self.widgets['hframe'+k],text='Type', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
				self.widgets['typeLabel'+k].grid(column=2,row=row,padx=10, sticky='EW')
				self.widgets['typeData'+k] = Tkinter.Label(self.widgets['hframe'+k],text=info['type'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
				self.widgets['typeData'+k].grid(column=3,row=row,sticky='EW')
				
				self.widgets['historyLabel'+k] = Tkinter.Label(self.widgets['hframe'+k],text='History', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
				self.widgets['historyLabel'+k].grid(column=4,row=row,padx=10, sticky='EW')
				self.widgets['historyData'+k] = Tkinter.Label(self.widgets['hframe'+k],text=info['history'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
				self.widgets['historyData'+k].grid(column=5,row=row,sticky='EW')
				
				self.widgets['archiveLabel'+k] = Tkinter.Label(self.widgets['hframe'+k],text='Archive', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
				self.widgets['archiveLabel'+k].grid(column=6,row=row,padx=10, sticky='EW')
				self.widgets['archiveData'+k] = Tkinter.Label(self.widgets['hframe'+k],text=info['archive'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
				self.widgets['archiveData'+k].grid(column=7,row=row,sticky='EW')
				
				self.widgets['batchLabel'+k] = Tkinter.Label(self.widgets['hframe'+k],text='Batch', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
				self.widgets['batchLabel'+k].grid(column=8,row=row,padx=10, sticky='EW')
				self.widgets['batchData'+k] = Tkinter.Label(self.widgets['hframe'+k],text=info['batch'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
				self.widgets['batchData'+k].grid(column=9,row=row,sticky='EW')
				row += 1
				
				self.widgets['noLabel'+k] = Tkinter.Label(self.widgets['vframe'+k],text='TBD', bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
				self.widgets['noLabel'+k].grid(column=0,row=0,padx=10, sticky='EW')
				
				self.gridrow += 1
			self.updateValues()
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['tframe'],text='There are currently no metrics being monitored', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noLabel'].grid(column=0,row=self.gridrow,sticky='EW')
	def updateValues(self):
		""" updates values ui
		"""
		for k,v in Metric.metrics.iteritems():
			vals = v.hotValues()
			if(len(vals) > 0):
				try:
					self.widgets['noLabel'+k].grid_forget()
					del(self.widgets['noLabel'+k])
				except:
					pass
				vcol = 0
				for i in vals:
					vindex = 'v{0}{1}'.format(k,vcol)
					self.widgets['time'+vindex] = Tkinter.Label(self.widgets['vframe'+k],text=datetime.datetime.fromtimestamp(i.timestamp/1000).strftime('%Y-%m-%d %H:%M:%S'), bg=self.colours['rowbg'], fg=self.colours['headingfg'], height=2)
					self.widgets['time'+vindex].grid(column=vcol,row=0, padx=10,sticky='EW')
					self.widgets['val'+vindex] = self.genericView(self.widgets['vframe'+k], i.datavalue)
					self.widgets['val'+vindex].grid(column=vcol,row=1, padx=10, sticky='EW')
					vcol += 1
	
	#=== ACTIONS ===#
	def OnListMetricsClick(self):
		""" action - displays the list metrics page
		"""
		self.listMetrics()
	def OnViewMetricClick(self, name):
		""" action - displays the view metric page
		"""
		self.metric = Metric(name)
		self.viewMetric()
	def OnViewMetricSessionClick(self, datestring):
		""" action - displays the metric session page
		"""
		self.session = [x for x in self.metrics[self.metric.name] if x[0] == datestring]
		self.sessionstart = self.start = datetime.datetime.strptime(datestring,'%Y-%m-%d')
		self.sessionend = self.end = self.start + datetime.timedelta(seconds=86399)
		self.resolution = 'hour'
		self.times = {
			'rangestart': self.__mktime(self.start),
			'rangeend': self.__mktime(self.end),
		}
		self.times['currentstart'] = self.times['rangestart']
		self.times['currentend'] = self.times['currentstart'] + self.resolutions[self.resolution]
		self.metric.clearValues()
		self.metric.loadValues(start=self.times['rangestart'], end=self.times['rangeend'], resolution=self.resolution)
		self.vals = self.metric.hotValues()
		self.viewMetricSession()
	def OnRaiseResolutionClick(self):
		""" action - changes to a higher res
		"""
		self.times[self.resolution] = {
			'rangestart': self.times['rangestart'],
			'rangeend': self.times['rangeend'],
			'offset': float(self.variables['time'].get())
		}
		if(self.resolution == 'hour'):
			self.resolution = 'minute'
			self.times['rangestart'] = self.__mktime(self.sessionstart) + float(self.variables['time'].get()) * self.resolutions['hour']
			self.times['rangeend'] = self.times['rangestart'] + self.resolutions['hour']
		elif(self.resolution == 'minute'):
			self.resolution = 'second'
			self.times['rangestart'] += float(self.variables['time'].get()) * self.resolutions['minute']
			self.times['rangeend'] = self.times['rangestart'] + self.resolutions['minute']
		elif(self.resolution == 'second'):
			self.resolution = 'millisecond'
			self.times['rangestart'] += float(self.variables['time'].get()) * self.resolutions['second']
			self.times['rangeend'] = self.times['rangestart'] + self.resolutions['second']
		self.metric.clearValues()
		self.metric.loadValues(start=self.times['rangestart'], end=self.times['rangeend'], resolution=self.resolution)
		self.vals = self.metric.hotValues()
		del(self.shapes['marker']) #prevents canvas shape confusion
		self.viewMetricSession()
	def OnLowerResolutionClick(self):
		""" action - changes to a lower res
		"""
		if(self.resolution == 'millisecond'):
			self.resolution = 'second'
		elif(self.resolution == 'second'):
			self.resolution = 'minute'
		elif(self.resolution == 'minute'):
			self.resolution = 'hour'
		elif(self.resolution == 'hour'):
			self.viewMetric() #go back to the list of sessions for this metric
			return
		self.times['rangestart'] = self.times[self.resolution]['rangestart']
		self.times['rangeend'] = self.times[self.resolution]['rangeend']
		self.metric.clearValues()
		self.metric.loadValues(start=self.times['rangestart'], end=self.times['rangeend'], resolution=self.resolution)
		self.vals = self.metric.hotValues()
		del(self.shapes['marker']) #prevents canvas shape confusion
		self.viewMetricSession()
		self.variables['time'].set(self.times[self.resolution]['offset'])
		self.updateMetricValues(self.times[self.resolution]['offset'])
	def OnViewSessionClick(self, datestring):
		""" action - displays a session
		"""
		self.start = datetime.datetime.strptime(datestring,'%Y-%m-%d')
		self.end = self.start + datetime.timedelta(seconds=86399)
		self.session = self.sessions[datestring]
		self.metrics = {}
		for s in self.session:
			self.metrics[s[0]['name']] = Metric(s[0]['name'], -1, False)
		self.viewSession()
	def OnViewHourClick(self, data):
		""" action - displays an hour
		"""
		self.hour = data[0]
		self.metric = self.metrics[data[1]]
		datestring = '{0}-{1}-{2} {3}'.format(self.session[0][0]['year'], self.session[0][0]['month'], self.session[0][0]['day'], self.__formatMinute(self.hour,0))
		self.start = datetime.datetime.strptime(datestring,'%Y-%m-%d %H:%M')
		self.end = self.start + datetime.timedelta(seconds=3600)
		self.viewHour()
	def OnViewMinuteClick(self, data):
		""" action - displays a minute
		"""
		self.hour = data[0]
		self.minute = data[1]
		self.metric = data[2]
		datestring = '{0}-{1}-{2} {3}'.format(self.session[0][0]['year'], self.session[0][0]['month'], self.session[0][0]['day'], self.__formatSecond(self.hour,self.minute,0))
		self.start = datetime.datetime.strptime(datestring,'%Y-%m-%d %H:%M:%S')
		self.end = self.start + datetime.timedelta(seconds=60)
		self.viewMinute()
	def OnViewSecondClick(self, data):
		""" action - displays a second
		"""
		self.hour = data[0]
		self.minute = data[1]
		self.second = data[2]
		self.metric = data[3]
		datestring = '{0}-{1}-{2} {3}'.format(self.session[0][0]['year'], self.session[0][0]['month'], self.session[0][0]['day'], self.__formatSecond(self.hour,self.minute,self.second))
		self.start = datetime.datetime.strptime(datestring,'%Y-%m-%d %H:%M:%S')
		self.end = self.start + datetime.timedelta(seconds=1)
		self.viewSecond()
	def OnSnapshotClick(self):
		""" action - displays snapshot page
		"""
		self.showSnapshot()
	
	#=== UTILS ===#
	def __mktime(self, dt):
		""" util - time from datetime
		"""
		return time.mktime(dt.timetuple())
	def __formatHour(self, hour):
		""" util - hour display format
		"""
		strtime = '{0}:00'
		if hour < 10:
			strtime = strtime.format('0{0}'.format(hour))
		else:
			strtime = strtime.format(hour)
		return strtime
	def __formatMinute(self, hour, minute):
		""" util - minute display format
		"""
		strtime = '{0}:{1}'
		strhour = str(hour) if hour >= 10 else '0{0}'.format(hour)
		strmin = str(minute) if minute >= 10 else '0{0}'.format(minute)
		return strtime.format(strhour, strmin)
	def __formatSecond(self, hour, minute, second):
		""" util - second display format
		"""
		strtime = '{0}:{1}:{2}'
		strhour = str(hour) if hour >= 10 else '0{0}'.format(hour)
		strmin = str(minute) if minute >= 10 else '0{0}'.format(minute)
		strsec = str(second) if second >= 10 else '0{0}'.format(second)
		return strtime.format(strhour, strmin, strsec)
	def __formatMillisecond(self, hour, minute, second, ms):
		""" util - millisecond display format
		"""
		strtime = '{0}:{1}:{2}.{3}'
		strhour = str(hour) if hour >= 10 else '0{0}'.format(hour)
		strmin = str(minute) if minute >= 10 else '0{0}'.format(minute)
		strsec = str(second) if second >= 10 else '0{0}'.format(second)
		if(ms < 10):
			strms = '000{0}'.format(ms)
		elif(ms < 100):
			strms = '00{0}'.format(ms)
		else:
			strms = str(ms)
		return strtime.format(strhour, strmin, strsec, strms)