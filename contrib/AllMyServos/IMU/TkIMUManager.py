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
import Tkinter, os, Specification
from Tkinter import *
from TkGraphs import *
from TkBlock import *
from Scheduler import *
from Setting import *
from Metric import *
from IMU import IMU
from math import pi

class TkIMUManager(TkPage):
	def __init__(self, parent, gui, **options):
		super(TkIMUManager,self).__init__(parent, gui, **options)
		self.specification = gui.specification
		if(hasattr(self.gui, 'scheduler')):
			self.scheduler = self.gui.scheduler
		else:
			self.scheduler = Scheduler()
		if(hasattr(self.gui, 'imu')):
			self.imu = self.gui.imu
		else:
			self.imu = self.gui.imu = IMU(self.specification, self.scheduler, (not Setting.get('imu_autostart', False)))
		self.poll = 0
		self.metrics = {}
	def initImages(self):
		self.facing = [ 'up', 'down', 'left','right', 'front', 'back' ]
		self.offset = [ 0, 90, 180, 270 ]
		if(not hasattr(self, 'oimages')):
			self.oimages = {}
			for f in self.facing:
				for o in self.offset:
					if(not f in self.oimages.keys()):
						self.oimages[f] = {}
					self.oimages[f][o] = Tkinter.PhotoImage(file = os.path.join(os.getcwd(), 'images', 'orientation','{}{}.gif'.format(f,o)))
	def setup(self):
		try:
			self.gui.menus['imu']
		except:
			self.gui.menus['imu'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="IMU", menu=self.gui.menus['imu'])
		self.gui.menus['imu'].insert_command(0, label="Orientation", command=self.OnOrientationClick)
		self.gui.menus['imu'].insert_command(1, label="Sensor Data", command=self.OnShowIMUDataClick)
	
	#=== VIEWS ===#
	def serviceManager(self):
		self.widgets['servicelabel'] = Tkinter.Label(self.widgets['tframe'],text='IMU / IMU Service', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['servicelabel'].grid(column=0,row=self.gridrow, columnspan=2, sticky='EW')
		
		self.gridrow += 1
		
		#archive frame
		self.widgets['aframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], highlightthickness=1, highlightbackground=self.colours['fg'])
		self.widgets['aframe'].grid(column=1,row=self.gridrow, rowspan=2, sticky='W')
		
		self.widgets['archiveLabel'] = Tkinter.Label(self.widgets['aframe'],text='Archive', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['archiveLabel'].grid(column=0,row=0,sticky='EW')
		
		self.variables['archivegyroraw'] = Tkinter.BooleanVar()
		self.variables['archivegyroraw'].set(Setting.get('imu_archive_gyro_raw',False))
		self.widgets['archivegyroentry'] = Tkinter.Checkbutton(self.widgets['aframe'], variable=self.variables['archivegyroraw'], text='Gyro Raw', anchor=W, command=self.OnToggleArchiveGyroRaw, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['archivegyroentry'].grid(column=0,row=1, padx=5, sticky="EW")
		
		self.variables['archiveaccraw'] = Tkinter.BooleanVar()
		self.variables['archiveaccraw'].set(Setting.get('imu_archive_acc_raw',False))
		self.widgets['archiveaccentry'] = Tkinter.Checkbutton(self.widgets['aframe'], variable=self.variables['archiveaccraw'], text='Acc Raw', anchor=W, command=self.OnToggleArchiveAccRaw, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['archiveaccentry'].grid(column=0,row=2, padx=5, sticky="EW")
		
		self.variables['archivegyronorm'] = Tkinter.BooleanVar()
		self.variables['archivegyronorm'].set(Setting.get('imu_archive_gyro_norm',False))
		self.widgets['archivegyronormentry'] = Tkinter.Checkbutton(self.widgets['aframe'], variable=self.variables['archivegyronorm'], text='Gyro Normal (+500/-500 deg)', anchor=W, command=self.OnToggleArchiveGyroNorm, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['archivegyronormentry'].grid(column=0,row=3, padx=5, sticky="EW")
		
		self.variables['archiveaccnorm'] = Tkinter.BooleanVar()
		self.variables['archiveaccnorm'].set(Setting.get('imu_archive_acc_norm',False))
		self.widgets['archiveaccnormentry'] = Tkinter.Checkbutton(self.widgets['aframe'], variable=self.variables['archiveaccnorm'], text='Acc Normal (+2/-2 g)', anchor=W, command=self.OnToggleArchiveAccNorm, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['archiveaccnormentry'].grid(column=0,row=4, padx=5, sticky="EW")
		
		self.variables['archivegyroang'] = Tkinter.BooleanVar()
		self.variables['archivegyroang'].set(Setting.get('imu_archive_gyro_ang',False))
		self.widgets['archivegyroangentry'] = Tkinter.Checkbutton(self.widgets['aframe'], variable=self.variables['archivegyroang'], text='Gyro Angle', anchor=W, command=self.OnToggleArchiveGyroAng, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['archivegyroangentry'].grid(column=0,row=5, padx=5, sticky="EW")
		
		self.variables['archivegyroanginc'] = Tkinter.BooleanVar()
		self.variables['archivegyroanginc'].set(Setting.get('imu_archive_gyro_ang_inc',False))
		self.widgets['archivegyroangincentry'] = Tkinter.Checkbutton(self.widgets['aframe'], variable=self.variables['archivegyroanginc'], text='Gyro Angle Increments', anchor=W, command=self.OnToggleArchiveGyroAngInc, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['archivegyroangincentry'].grid(column=0,row=6, padx=5, sticky="EW")
		
		self.variables['archiveaccang'] = Tkinter.BooleanVar()
		self.variables['archiveaccang'].set(Setting.get('imu_archive_acc_ang',False))
		self.widgets['archiveaccangentry'] = Tkinter.Checkbutton(self.widgets['aframe'], variable=self.variables['archiveaccang'], text='Acc Angle', anchor=W, command=self.OnToggleArchiveAccAng, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['archiveaccangentry'].grid(column=0,row=7, padx=5, sticky="EW")
		
		self.variables['archivelow'] = Tkinter.BooleanVar()
		self.variables['archivelow'].set(Setting.get('imu_archive_low',False))
		self.widgets['archivelowentry'] = Tkinter.Checkbutton(self.widgets['aframe'], variable=self.variables['archivelow'], text='Lowpass Filter', anchor=W, command=self.OnToggleArchiveLow, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['archivelowentry'].grid(column=0,row=8, padx=5, sticky="EW")
		
		self.variables['archivehigh'] = Tkinter.BooleanVar()
		self.variables['archivehigh'].set(Setting.get('imu_archive_high',False))
		self.widgets['archivehighentry'] = Tkinter.Checkbutton(self.widgets['aframe'], variable=self.variables['archivehigh'], text='Highpass Filter', anchor=W, command=self.OnToggleArchiveHigh, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['archivehighentry'].grid(column=0,row=9, padx=5, sticky="EW")
		
		self.variables['archivecom'] = Tkinter.BooleanVar()
		self.variables['archivecom'].set(Setting.get('imu_archive_com',False))
		self.widgets['archivecomentry'] = Tkinter.Checkbutton(self.widgets['aframe'], variable=self.variables['archivecom'], text='Complementary Filter', anchor=W, command=self.OnToggleArchiveCom, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['archivecomentry'].grid(column=0,row=10, padx=5, sticky="EW")
		
		#service frame
		self.widgets['sframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['sframe'].grid(column=0,row=self.gridrow, sticky='W')
		
		self.widgets['statusLabel'] = Tkinter.Label(self.widgets['sframe'],text='Status', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['statusLabel'].grid(column=0,row=0,sticky='EW')
		
		self.variables['status'] = Tkinter.StringVar()
		self.widgets['statusdata'] = Tkinter.Label(self.widgets['sframe'],textvariable=self.variables['status'], bg=self.colours['bg'], fg=self.colours['fg'], font=self.fonts['heading2'])
		self.widgets['statusdata'].grid(column=0,row=1,padx=50, sticky='EW')
		
		self.widgets['start'] = Tkinter.Button(self.widgets['sframe'],text=u"Start", image=self.images['play'], command=self.OnStartClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['start'].grid(column=1,row=1,sticky='W')
		
		self.widgets['stop'] = Tkinter.Button(self.widgets['sframe'],text=u"Stop", image=self.images['stop'], command=self.OnStopClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['stop'].grid(column=2,row=1,sticky='W')
		
		if(self.scheduler.tasks['imu_watcher'].stopped == False):
			self.variables['status'].set('Running')
			self.widgets['start'].configure(state='disabled')
		else:
			self.variables['status'].set('Stopped')
			self.widgets['stop'].configure(state='disabled')
		
		self.widgets['calibrateLabel'] = Tkinter.Label(self.widgets['sframe'],text='Calibrate', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['calibrateLabel'].grid(column=0,row=2,sticky='EW')
		
		self.widgets['calibrate'] = Tkinter.Button(self.widgets['sframe'],text=u"Calibrate", image=self.images['process'], command=self.OnCalibrateClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['calibrate'].grid(column=1,row=2,sticky='W')
		
		self.gridrow += 1
		
		self.widgets['dataframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['dataframe'].grid(column=0,row=self.gridrow, sticky='W')
		
		self.widgets['collectLabel'] = Tkinter.Label(self.widgets['dataframe'],text='Data Collection', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['collectLabel'].grid(column=0,row=0, padx=10,sticky='EW')
		
		#vertical labels
		self.widgets['collLabel'] = Tkinter.Label(self.widgets['dataframe'],text='Collect', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['collLabel'].grid(column=1,row=1, padx=10,sticky='EW')
		self.widgets['dispLabel'] = Tkinter.Label(self.widgets['dataframe'],text='Display', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['dispLabel'].grid(column=1,row=2, padx=10,sticky='EW')
		
		#horizontal labels
		self.widgets['rawLabel'] = Tkinter.Label(self.widgets['dataframe'],text='Raw', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['rawLabel'].grid(column=2,row=0, padx=10,sticky='EW')
		self.widgets['normLabel'] = Tkinter.Label(self.widgets['dataframe'],text='Normal', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['normLabel'].grid(column=3,row=0, padx=10,sticky='EW')
		self.widgets['lowLabel'] = Tkinter.Label(self.widgets['dataframe'],text='Lowpass', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['lowLabel'].grid(column=4,row=0, padx=10,sticky='EW')
		self.widgets['highLabel'] = Tkinter.Label(self.widgets['dataframe'],text='Highpass', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['highLabel'].grid(column=5,row=0, padx=10,sticky='EW')
		self.widgets['angLabel'] = Tkinter.Label(self.widgets['dataframe'],text='Angle', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['angLabel'].grid(column=6,row=0, padx=10,sticky='EW')
		self.widgets['comLabel'] = Tkinter.Label(self.widgets['dataframe'],text='Complement', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['comLabel'].grid(column=7,row=0, padx=10,sticky='EW')
		
		self.variables['watchraw'] = Tkinter.BooleanVar()
		self.variables['watchraw'].set(Setting.get('imu_watch_raw',True))
		self.widgets['watchrawentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['watchraw'], command=self.OnToggleWatchRawClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['watchrawentry'].grid(column=2,row=1, padx=5, pady=10)
		self.variables['displayraw'] = Tkinter.BooleanVar()
		self.variables['displayraw'].set(Setting.get('imu_display_raw',True))
		self.widgets['displayrawentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['displayraw'], command=self.OnToggleDisplayRawClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['displayrawentry'].grid(column=2,row=2, padx=5, pady=10)
		
		self.variables['watchnorm'] = Tkinter.BooleanVar()
		self.variables['watchnorm'].set(Setting.get('imu_watch_norm',True))
		self.widgets['watchnormentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['watchnorm'], command=self.OnToggleWatchNormClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['watchnormentry'].grid(column=3,row=1, padx=5, pady=10)
		self.variables['displaynorm'] = Tkinter.BooleanVar()
		self.variables['displaynorm'].set(Setting.get('imu_display_norm',True))
		self.widgets['displaynormentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['displaynorm'], command=self.OnToggleDisplayNormClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['displaynormentry'].grid(column=3,row=2, padx=5, pady=10)
		
		self.variables['watchlow'] = Tkinter.BooleanVar()
		self.variables['watchlow'].set(Setting.get('imu_watch_low',True))
		self.widgets['watchlowentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['watchlow'], command=self.OnToggleWatchLowClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['watchlowentry'].grid(column=4,row=1, padx=5, pady=10)
		self.variables['displaylow'] = Tkinter.BooleanVar()
		self.variables['displaylow'].set(Setting.get('imu_display_low',True))
		self.widgets['displaylowentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['displaylow'], command=self.OnToggleDisplayLowClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['displaylowentry'].grid(column=4,row=2, padx=5, pady=10)
		
		self.variables['watchhigh'] = Tkinter.BooleanVar()
		self.variables['watchhigh'].set(Setting.get('imu_watch_high',True))
		self.widgets['watchhighentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['watchhigh'], command=self.OnToggleWatchHighClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['watchhighentry'].grid(column=5,row=1, padx=5, pady=10)
		self.variables['displayhigh'] = Tkinter.BooleanVar()
		self.variables['displayhigh'].set(Setting.get('imu_display_high',True))
		self.widgets['displayhighentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['displayhigh'], command=self.OnToggleDisplayHighClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['displayhighentry'].grid(column=5,row=2, padx=5, pady=10)
		
		self.variables['watchang'] = Tkinter.BooleanVar()
		self.variables['watchang'].set(Setting.get('imu_watch_ang',True))
		self.widgets['watchangentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['watchang'], command=self.OnToggleWatchAngClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['watchangentry'].grid(column=6,row=1, padx=5, pady=10)
		self.variables['displayang'] = Tkinter.BooleanVar()
		self.variables['displayang'].set(Setting.get('imu_display_ang',True))
		self.widgets['displayangentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['displayang'], command=self.OnToggleDisplayAngClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['displayangentry'].grid(column=6,row=2, padx=5, pady=10)
		
		self.variables['watchcom'] = Tkinter.BooleanVar()
		self.variables['watchcom'].set(Setting.get('imu_watch_com',True))
		self.widgets['watchcomentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['watchcom'], command=self.OnToggleWatchComClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['watchcomentry'].grid(column=7,row=1, padx=5, pady=10)
		self.variables['displaycom'] = Tkinter.BooleanVar()
		self.variables['displaycom'].set(Setting.get('imu_display_com',True))
		self.widgets['displaycomentry'] = Tkinter.Checkbutton(self.widgets['dataframe'], variable=self.variables['displaycom'], command=self.OnToggleDisplayComClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['displaycomentry'].grid(column=7,row=2, padx=5, pady=10)
		
		self.gridrow += 1
		
		self.widgets['orientframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['orientframe'].grid(column=0,row=self.gridrow, sticky='W')
		
		self.widgets['orientLabel'] = Tkinter.Label(self.widgets['orientframe'],text='Mounted', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['orientLabel'].grid(column=0,row=0, padx=10,sticky='EW')
		
		self.widgets['orientLabel'] = Tkinter.Label(self.widgets['orientframe'],text='Facing', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['orientLabel'].grid(column=1,row=0, padx=10,sticky='EW')
		
		self.widgets['orientLabel'] = Tkinter.Label(self.widgets['orientframe'],text=self.specification.imu['facing'], bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['orientLabel'].grid(column=2,row=0, padx=10,sticky='EW')
		
		self.widgets['orientLabel'] = Tkinter.Label(self.widgets['orientframe'],text='Offset', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['orientLabel'].grid(column=3,row=0, padx=10,sticky='EW')
		
		self.widgets['orientLabel'] = Tkinter.Label(self.widgets['orientframe'],text=self.specification.imu['offset'], bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['orientLabel'].grid(column=4,row=0, padx=10,sticky='EW')
	def showData(self):
		self.open()
		
		self.serviceManager()
		
		self.gridrow += 1
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='IMU / Sensor Data', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['accframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], highlightthickness=1, highlightbackground=self.colours['fg'])
		self.widgets['accframe'].grid(column=0,row=self.gridrow, pady=5, columnspan=4, sticky='EW')
		
		row = 0
		
		self.widgets['accLabel'] = Tkinter.Label(self.widgets['accframe'],text='Accelerometer', bg=self.colours['bg'], fg=self.colours['headingfg'], width=20)
		self.widgets['accLabel'].grid(column=0,row=row, rowspan=3, sticky='EW')
		
		row += 1
		
		self.widgets['accRawLabel'] = Tkinter.Label(self.widgets['accframe'],text='Raw', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['accRawLabel'].grid(column=1,row=row, pady=10,sticky='EW')
		
		self.widgets['accRawXLabel'] = Tkinter.Label(self.widgets['accframe'],text='x', bg=self.colours['bg'], fg=self.colours['imux'])
		self.widgets['accRawXLabel'].grid(column=2,row=row, padx=10,sticky='EW')
		self.variables['accRawX'] = Tkinter.StringVar()
		self.variables['accRawX'].set('TBD')
		self.widgets['accRawX'] = Tkinter.Label(self.widgets['accframe'],textvariable=self.variables['accRawX'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['accRawX'].grid(column=3,row=row,sticky='EW')
		self.widgets['accRawYLabel'] = Tkinter.Label(self.widgets['accframe'],text='y', bg=self.colours['bg'], fg=self.colours['imuy'])
		self.widgets['accRawYLabel'].grid(column=4,row=row, padx=10,sticky='EW')
		self.variables['accRawY'] = Tkinter.StringVar()
		self.variables['accRawY'].set('TBD')
		self.widgets['accRawY'] = Tkinter.Label(self.widgets['accframe'],textvariable=self.variables['accRawY'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['accRawY'].grid(column=5,row=row,sticky='EW')
		self.widgets['accRawZLabel'] = Tkinter.Label(self.widgets['accframe'],text='z', bg=self.colours['bg'], fg=self.colours['imuz'])
		self.widgets['accRawZLabel'].grid(column=6,row=row, padx=10,sticky='EW')
		self.variables['accRawZ'] = Tkinter.StringVar()
		self.variables['accRawZ'].set('TBD')
		self.widgets['accRawZ'] = Tkinter.Label(self.widgets['accframe'],textvariable=self.variables['accRawZ'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['accRawZ'].grid(column=7,row=row,sticky='EW')
		
		row += 1
		
		self.widgets['accNormLabel'] = Tkinter.Label(self.widgets['accframe'],text='Norm', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['accNormLabel'].grid(column=1,row=row, pady=10,sticky='EW')
		
		self.widgets['accNormXLabel'] = Tkinter.Label(self.widgets['accframe'],text='x', bg=self.colours['bg'], fg=self.colours['imux'])
		self.widgets['accNormXLabel'].grid(column=2,row=row, padx=10,sticky='EW')
		self.variables['accNormX'] = Tkinter.StringVar()
		self.variables['accNormX'].set('TBD')
		self.widgets['accNormX'] = Tkinter.Label(self.widgets['accframe'],textvariable=self.variables['accNormX'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['accNormX'].grid(column=3,row=row,sticky='EW')
		self.widgets['accNormYLabel'] = Tkinter.Label(self.widgets['accframe'],text='y', bg=self.colours['bg'], fg=self.colours['imuy'])
		self.widgets['accNormYLabel'].grid(column=4,row=row, padx=10,sticky='EW')
		self.variables['accNormY'] = Tkinter.StringVar()
		self.variables['accNormY'].set('TBD')
		self.widgets['accNormY'] = Tkinter.Label(self.widgets['accframe'],textvariable=self.variables['accNormY'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['accNormY'].grid(column=5,row=row,sticky='EW')
		self.widgets['accNormZLabel'] = Tkinter.Label(self.widgets['accframe'],text='z', bg=self.colours['bg'], fg=self.colours['imuz'])
		self.widgets['accNormZLabel'].grid(column=6,row=row, padx=10,sticky='EW')
		self.variables['accNormZ'] = Tkinter.StringVar()
		self.variables['accNormZ'].set('TBD')
		self.widgets['accNormZ'] = Tkinter.Label(self.widgets['accframe'],textvariable=self.variables['accNormZ'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['accNormZ'].grid(column=7,row=row,sticky='EW')
		
		row += 1
		
		self.widgets['accAngLabel'] = Tkinter.Label(self.widgets['accframe'],text='Angle', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['accAngLabel'].grid(column=1,row=row, pady=10,sticky='EW')
		
		self.widgets['accAngYLabel'] = Tkinter.Label(self.widgets['accframe'],text='yaw', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['accAngYLabel'].grid(column=2,row=row, padx=10,sticky='EW')
		self.variables['accAngY'] = Tkinter.StringVar()
		self.variables['accAngY'].set('TBD')
		self.widgets['accAngY'] = Tkinter.Label(self.widgets['accframe'],textvariable=self.variables['accAngY'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['accAngY'].grid(column=3,row=row,sticky='EW')
		self.widgets['accAngPLabel'] = Tkinter.Label(self.widgets['accframe'],text='pitch', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['accAngPLabel'].grid(column=4,row=row, padx=10,sticky='EW')
		self.variables['accAngP'] = Tkinter.StringVar()
		self.variables['accAngP'].set('TBD')
		self.widgets['accAngP'] = Tkinter.Label(self.widgets['accframe'],textvariable=self.variables['accAngP'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['accAngP'].grid(column=5,row=row,sticky='EW')
		self.widgets['accAngRLabel'] = Tkinter.Label(self.widgets['accframe'],text='roll', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['accAngRLabel'].grid(column=6,row=row, padx=10,sticky='EW')
		self.variables['accAngR'] = Tkinter.StringVar()
		self.variables['accAngR'].set('TBD')
		self.widgets['accAngR'] = Tkinter.Label(self.widgets['accframe'],textvariable=self.variables['accAngR'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['accAngR'].grid(column=7,row=row,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['gyroframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], highlightthickness=1, highlightbackground=self.colours['fg'])
		self.widgets['gyroframe'].grid(column=0,row=self.gridrow, columnspan=4, pady=5, sticky='EW')
		
		row = 0
		
		self.widgets['gyroLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='Gyro', bg=self.colours['bg'], fg=self.colours['headingfg'], width=20)
		self.widgets['gyroLabel'].grid(column=0,row=row, rowspan=3, sticky='EW')
		
		row += 1
		
		self.widgets['gyroRawLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='Raw', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['gyroRawLabel'].grid(column=1,row=row, pady=10,sticky='EW')
		
		self.widgets['gyroRawXLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='x', bg=self.colours['bg'], fg=self.colours['imux'])
		self.widgets['gyroRawXLabel'].grid(column=2,row=row, padx=10,sticky='EW')
		self.variables['gyroRawX'] = Tkinter.StringVar()
		self.variables['gyroRawX'].set('TBD')
		self.widgets['gyroRawX'] = Tkinter.Label(self.widgets['gyroframe'],textvariable=self.variables['gyroRawX'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['gyroRawX'].grid(column=3,row=row,sticky='EW')
		self.widgets['gyroRawYLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='y', bg=self.colours['bg'], fg=self.colours['imuy'])
		self.widgets['gyroRawYLabel'].grid(column=4,row=row, padx=10,sticky='EW')
		self.variables['gyroRawY'] = Tkinter.StringVar()
		self.variables['gyroRawY'].set('TBD')
		self.widgets['gyroRawY'] = Tkinter.Label(self.widgets['gyroframe'],textvariable=self.variables['gyroRawY'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['gyroRawY'].grid(column=5,row=row,sticky='EW')
		self.widgets['gyroRawZLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='z', bg=self.colours['bg'], fg=self.colours['imuz'])
		self.widgets['gyroRawZLabel'].grid(column=6,row=row, padx=10,sticky='EW')
		self.variables['gyroRawZ'] = Tkinter.StringVar()
		self.variables['gyroRawZ'].set('TBD')
		self.widgets['gyroRawZ'] = Tkinter.Label(self.widgets['gyroframe'],textvariable=self.variables['gyroRawZ'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['gyroRawZ'].grid(column=7,row=row,sticky='EW')
		
		row += 1
		
		self.widgets['gyroNormLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='Norm', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['gyroNormLabel'].grid(column=1,row=row, pady=10,sticky='EW')
		
		self.widgets['gyroNormXLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='x', bg=self.colours['bg'], fg=self.colours['imux'])
		self.widgets['gyroNormXLabel'].grid(column=2,row=row, padx=10,sticky='EW')
		self.variables['gyroNormX'] = Tkinter.StringVar()
		self.variables['gyroNormX'].set('TBD')
		self.widgets['gyroNormX'] = Tkinter.Label(self.widgets['gyroframe'],textvariable=self.variables['gyroNormX'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['gyroNormX'].grid(column=3,row=row,sticky='EW')
		self.widgets['gyroNormYLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='y', bg=self.colours['bg'], fg=self.colours['imuy'])
		self.widgets['gyroNormYLabel'].grid(column=4,row=row, padx=10,sticky='EW')
		self.variables['gyroNormY'] = Tkinter.StringVar()
		self.variables['gyroNormY'].set('TBD')
		self.widgets['gyroNormY'] = Tkinter.Label(self.widgets['gyroframe'],textvariable=self.variables['gyroNormY'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['gyroNormY'].grid(column=5,row=row,sticky='EW')
		self.widgets['gyroNormZLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='z', bg=self.colours['bg'], fg=self.colours['imuz'])
		self.widgets['gyroNormZLabel'].grid(column=6,row=row, padx=10,sticky='EW')
		self.variables['gyroNormZ'] = Tkinter.StringVar()
		self.variables['gyroNormZ'].set('TBD')
		self.widgets['gyroNormZ'] = Tkinter.Label(self.widgets['gyroframe'],textvariable=self.variables['gyroNormZ'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['gyroNormZ'].grid(column=7,row=row,sticky='EW')
		
		row += 1
		
		self.widgets['gyroAngLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='Angle', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['gyroAngLabel'].grid(column=1,row=row, pady=10,sticky='EW')
		
		self.widgets['gyroAngYLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='yaw', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['gyroAngYLabel'].grid(column=2,row=row, padx=10,sticky='EW')
		self.variables['gyroAngY'] = Tkinter.StringVar()
		self.variables['gyroAngY'].set('TBD')
		self.widgets['gyroAngY'] = Tkinter.Label(self.widgets['gyroframe'],textvariable=self.variables['gyroAngY'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['gyroAngY'].grid(column=3,row=row,sticky='EW')
		self.widgets['gyroAngPLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='pitch', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['gyroAngPLabel'].grid(column=4,row=row, padx=10,sticky='EW')
		self.variables['gyroAngP'] = Tkinter.StringVar()
		self.variables['gyroAngP'].set('TBD')
		self.widgets['gyroAngP'] = Tkinter.Label(self.widgets['gyroframe'],textvariable=self.variables['gyroAngP'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['gyroAngP'].grid(column=5,row=row,sticky='EW')
		self.widgets['gyroAngRLabel'] = Tkinter.Label(self.widgets['gyroframe'],text='roll', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['gyroAngRLabel'].grid(column=6,row=row, padx=10,sticky='EW')
		self.variables['gyroAngR'] = Tkinter.StringVar()
		self.variables['gyroAngR'].set('TBD')
		self.widgets['gyroAngR'] = Tkinter.Label(self.widgets['gyroframe'],textvariable=self.variables['gyroAngR'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=10)
		self.widgets['gyroAngR'].grid(column=7,row=row,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['comframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], highlightthickness=1, highlightbackground=self.colours['fg'])
		self.widgets['comframe'].grid(column=0,row=self.gridrow, columnspan=4, pady=5, sticky='EW')
		
		self.widgets['comLabel'] = Tkinter.Label(self.widgets['comframe'],text='Complement', bg=self.colours['bg'], fg=self.colours['headingfg'], width=20)
		self.widgets['comLabel'].grid(column=0,row=0, rowspan=3, sticky='EW')
		
		self.widgets['comAngLabel'] = Tkinter.Label(self.widgets['comframe'],text='Angle', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['comAngLabel'].grid(column=1,row=0, pady=10,sticky='EW')
		
		self.widgets['comAngYLabel'] = Tkinter.Label(self.widgets['comframe'],text='yaw', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['comAngYLabel'].grid(column=2,row=0, padx=10,sticky='EW')
		self.variables['comAngY'] = Tkinter.StringVar()
		self.variables['comAngY'].set('TBD')
		self.widgets['comAngY'] = Tkinter.Label(self.widgets['comframe'],textvariable=self.variables['comAngY'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['comAngY'].grid(column=3,row=0,sticky='EW')
		self.widgets['comAngPLabel'] = Tkinter.Label(self.widgets['comframe'],text='pitch', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['comAngPLabel'].grid(column=4,row=0, padx=10,sticky='EW')
		self.variables['comAngP'] = Tkinter.StringVar()
		self.variables['comAngP'].set('TBD')
		self.widgets['comAngP'] = Tkinter.Label(self.widgets['comframe'],textvariable=self.variables['comAngP'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['comAngP'].grid(column=5,row=0,sticky='EW')
		self.widgets['comAngRLabel'] = Tkinter.Label(self.widgets['comframe'],text='roll', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['comAngRLabel'].grid(column=6,row=0, padx=10,sticky='EW')
		self.variables['comAngR'] = Tkinter.StringVar()
		self.variables['comAngR'].set('TBD')
		self.widgets['comAngR'] = Tkinter.Label(self.widgets['comframe'],textvariable=self.variables['comAngR'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['comAngR'].grid(column=7,row=0,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['lowframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], highlightthickness=1, highlightbackground=self.colours['fg'])
		self.widgets['lowframe'].grid(column=0,row=self.gridrow, columnspan=4, pady=5, sticky='EW')
		
		self.widgets['lowLabel'] = Tkinter.Label(self.widgets['lowframe'],text='Low Pass', bg=self.colours['bg'], fg=self.colours['headingfg'], width=20)
		self.widgets['lowLabel'].grid(column=0,row=0, rowspan=3, sticky='EW')
		
		self.widgets['lowRawLabel'] = Tkinter.Label(self.widgets['lowframe'],text='Raw', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['lowRawLabel'].grid(column=1,row=0, pady=10,sticky='EW')
		
		self.widgets['lowRawXLabel'] = Tkinter.Label(self.widgets['lowframe'],text='x', bg=self.colours['bg'], fg=self.colours['imux'])
		self.widgets['lowRawXLabel'].grid(column=2,row=0, padx=10,sticky='EW')
		self.variables['lowRawX'] = Tkinter.StringVar()
		self.variables['lowRawX'].set('TBD')
		self.widgets['lowRawX'] = Tkinter.Label(self.widgets['lowframe'],textvariable=self.variables['lowRawX'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['lowRawX'].grid(column=3,row=0,sticky='EW')
		self.widgets['lowRawYLabel'] = Tkinter.Label(self.widgets['lowframe'],text='y', bg=self.colours['bg'], fg=self.colours['imuy'])
		self.widgets['lowRawYLabel'].grid(column=4,row=0, padx=10,sticky='EW')
		self.variables['lowRawY'] = Tkinter.StringVar()
		self.variables['lowRawY'].set('TBD')
		self.widgets['lowRawY'] = Tkinter.Label(self.widgets['lowframe'],textvariable=self.variables['lowRawY'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['lowRawY'].grid(column=5,row=0,sticky='EW')
		self.widgets['lowRawZLabel'] = Tkinter.Label(self.widgets['lowframe'],text='z', bg=self.colours['bg'], fg=self.colours['imuz'])
		self.widgets['lowRawZLabel'].grid(column=6,row=0, padx=10,sticky='EW')
		self.variables['lowRawZ'] = Tkinter.StringVar()
		self.variables['lowRawZ'].set('TBD')
		self.widgets['lowRawZ'] = Tkinter.Label(self.widgets['lowframe'],textvariable=self.variables['lowRawZ'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['lowRawZ'].grid(column=7,row=0,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['highframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'], highlightthickness=1, highlightbackground=self.colours['fg'])
		self.widgets['highframe'].grid(column=0,row=self.gridrow, columnspan=4, pady=5, sticky='EW')
		
		self.widgets['highLabel'] = Tkinter.Label(self.widgets['highframe'],text='High Pass', bg=self.colours['bg'], fg=self.colours['headingfg'], width=20)
		self.widgets['highLabel'].grid(column=0,row=0, rowspan=3, sticky='EW')
		
		self.widgets['highRawLabel'] = Tkinter.Label(self.widgets['highframe'],text='Raw', bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['highRawLabel'].grid(column=1,row=0, pady=10,sticky='EW')
		
		self.widgets['highRawXLabel'] = Tkinter.Label(self.widgets['highframe'],text='x', bg=self.colours['bg'], fg=self.colours['imux'])
		self.widgets['highRawXLabel'].grid(column=2,row=0, padx=10,sticky='EW')
		self.variables['highRawX'] = Tkinter.StringVar()
		self.variables['highRawX'].set('TBD')
		self.widgets['highRawX'] = Tkinter.Label(self.widgets['highframe'],textvariable=self.variables['highRawX'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['highRawX'].grid(column=3,row=0,sticky='EW')
		self.widgets['highRawYLabel'] = Tkinter.Label(self.widgets['highframe'],text='y', bg=self.colours['bg'], fg=self.colours['imuy'])
		self.widgets['highRawYLabel'].grid(column=4,row=0, padx=10,sticky='EW')
		self.variables['highRawY'] = Tkinter.StringVar()
		self.variables['highRawY'].set('TBD')
		self.widgets['highRawY'] = Tkinter.Label(self.widgets['highframe'],textvariable=self.variables['highRawY'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['highRawY'].grid(column=5,row=0,sticky='EW')
		self.widgets['highRawZLabel'] = Tkinter.Label(self.widgets['highframe'],text='z', bg=self.colours['bg'], fg=self.colours['imuz'])
		self.widgets['highRawZLabel'].grid(column=6,row=0, padx=10,sticky='EW')
		self.variables['highRawZ'] = Tkinter.StringVar()
		self.variables['highRawZ'].set('TBD')
		self.widgets['highRawZ'] = Tkinter.Label(self.widgets['highframe'],textvariable=self.variables['highRawZ'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], width=20)
		self.widgets['highRawZ'].grid(column=7,row=0,sticky='EW')
		
		self.updateDataOptions()
	def showOrientation(self):
		self.open()
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='IMU / Orientation', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['previewLabel'] = Tkinter.Label(self.widgets['tframe'],text='Preview', image=self.oimages[self.specification.imu['facing']][self.specification.imu['offset']], bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['previewLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['oframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['oframe'].grid(column=0,row=self.gridrow, columnspan=4, pady=5, sticky='EW')
		
		row = 0
		
		self.widgets['facingLabel'] = Tkinter.Label(self.widgets['oframe'],text='Facing', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['facingLabel'].grid(column=0,row=row, ipady=10,sticky='EW')
		
		self.variables['facing'] = Tkinter.StringVar()
		self.variables['facing'].set(self.specification.imu['facing'])
		col = 1
		for f in self.facing:
			btn = Tkinter.Radiobutton(self.widgets['oframe'], text=f, variable=self.variables['facing'], command=self.updatePreview, value=f, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
			btn.grid(column=col, row=row, padx=10)
			col += 1
		row += 1
		self.widgets['offsetLabel'] = Tkinter.Label(self.widgets['oframe'],text='Offset', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['offsetLabel'].grid(column=0,row=row, ipady=10,sticky='EW')
		
		self.variables['offset'] = Tkinter.IntVar()
		self.variables['offset'].set(self.specification.imu['offset'])
		col = 1
		for o in self.offset:
			btn = Tkinter.Radiobutton(self.widgets['oframe'], text=o, variable=self.variables['offset'], command=self.updatePreview, value=o, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
			btn.grid(column=col, row=row, padx=10)
			col += 1
	def updateData(self):
		try:
			self.upoll
		except:
			self.upoll = 0
		if(Setting.get('imu_watch_raw',True) and Setting.get('imu_display_raw',True) and self.upoll == 0):
			dp = 8
			accRaw = self.imu.metrics['acc_raw'].value
			self.variables['accRawX'].set(round(accRaw['x'], dp))
			self.variables['accRawY'].set(round(accRaw['y'], dp))
			self.variables['accRawZ'].set(round(accRaw['z'], dp))
			gyroRaw = self.imu.metrics['gyro_raw'].value
			self.variables['gyroRawX'].set(round(gyroRaw['x'], dp))
			self.variables['gyroRawY'].set(round(gyroRaw['y'], dp))
			self.variables['gyroRawZ'].set(round(gyroRaw['z'], dp))
		if(Setting.get('imu_watch_norm',True) and Setting.get('imu_display_norm',True) and self.upoll == 0):
			dp = 4
			accNorm = self.imu.metrics['acc_norm'].value
			self.variables['accNormX'].set(round(accNorm['x'], dp))
			self.variables['accNormY'].set(round(accNorm['y'], dp))
			self.variables['accNormZ'].set(round(accNorm['z'], dp))
			gyroNorm = self.imu.metrics['gyro_norm'].value
			self.variables['gyroNormX'].set(round(gyroNorm['x'], dp))
			self.variables['gyroNormY'].set(round(gyroNorm['y'], dp))
			self.variables['gyroNormZ'].set(round(gyroNorm['z'], dp))
		if(Setting.get('imu_watch_ang',True) and Setting.get('imu_display_ang',True) and self.upoll == 0):
			accAng = self.imu.metrics['acc_ang'].value
			self.variables['accAngY'].set(round(accAng['y']))
			self.variables['accAngP'].set(round(accAng['p']))
			self.variables['accAngR'].set(round(accAng['r']))
			gyroAng = self.imu.metrics['gyro_ang'].value
			self.variables['gyroAngY'].set(round(gyroAng['y']))
			self.variables['gyroAngP'].set(round(gyroAng['p']))
			self.variables['gyroAngR'].set(round(gyroAng['r']))
		if(Setting.get('imu_watch_com',True) and Setting.get('imu_display_com',True) and self.upoll == 0):
			comAng = self.imu.metrics['complement'].value
			self.variables['comAngY'].set(round(comAng['y']))
			self.variables['comAngP'].set(round(comAng['p']))
			self.variables['comAngR'].set(round(comAng['r']))
		if(Setting.get('imu_watch_low',True) and Setting.get('imu_display_low',True) and self.upoll == 0):
			lowRaw = self.imu.metrics['lowpass'].value
			self.variables['lowRawX'].set(round(lowRaw['x'], dp))
			self.variables['lowRawY'].set(round(lowRaw['y'], dp))
			self.variables['lowRawZ'].set(round(lowRaw['z'], dp))
		if(Setting.get('imu_watch_high',True) and Setting.get('imu_display_high',True) and self.upoll == 0):
			highRaw = self.imu.metrics['highpass'].value
			self.variables['highRawX'].set(round(highRaw['x'], dp))
			self.variables['highRawY'].set(round(highRaw['y'], dp))
			self.variables['highRawZ'].set(round(highRaw['z'], dp))
		self.upoll += 1
		if(self.upoll == 10):
			self.upoll = 0
	def updateDataOptions(self):
		if(self.variables['watchraw'].get()):
			self.widgets['watchnormentry'].configure(state='normal')
			if(self.variables['watchnorm'].get()):
				self.widgets['watchlowentry'].configure(state='normal')
				if(self.variables['watchlow'].get()):
					self.widgets['watchangentry'].configure(state='normal')
					self.widgets['watchhighentry'].configure(state='normal')
					if(self.variables['watchang'].get()):
						self.widgets['watchcomentry'].configure(state='normal')
					else:
						self.disableDataOption('watchcomentry', 'watchcom', 'imu_watch_com')
				else:
					self.disableDataOption('watchhighentry', 'watchhigh', 'imu_watch_high')
					self.disableDataOption('watchangentry', 'watchang', 'imu_watch_ang')
					self.disableDataOption('watchcomentry', 'watchcom', 'imu_watch_com')
			else:
				self.disableDataOption('watchlowentry', 'watchlow', 'imu_watch_low')
				self.disableDataOption('watchhighentry', 'watchhigh', 'imu_watch_high')
				self.disableDataOption('watchangentry', 'watchang', 'imu_watch_ang')
				self.disableDataOption('watchcomentry', 'watchcom', 'imu_watch_com')
		else:
			self.disableDataOption('watchnormentry', 'watchnorm', 'imu_watch_norm')
			self.disableDataOption('watchlowentry', 'watchlow', 'imu_watch_low')
			self.disableDataOption('watchhighentry', 'watchhigh', 'imu_watch_high')
			self.disableDataOption('watchangentry', 'watchang', 'imu_watch_ang')
			self.disableDataOption('watchcomentry', 'watchcom', 'imu_watch_com')
	def disableDataOption(self, wname, vname, sname):
		self.widgets[wname].configure(state='disabled')
		if(self.variables[vname].get()):
			self.variables[vname].set(False)
			Setting.set(sname, False)
	def updatePreview(self):
		self.specification.imu['facing'] = self.variables['facing'].get()
		self.specification.imu['offset'] = self.variables['offset'].get()
		self.specification.save()
		self.widgets['previewLabel'].configure(image=self.oimages[self.specification.imu['facing']][self.specification.imu['offset']])
	
	#=== ACTIONS ===#
	def OnStartClick(self):
		self.variables['status'].set('Started')
		self.widgets['start'].configure(state='disabled')
		self.widgets['stop'].configure(state='normal')
		self.imu.start()
	def OnStopClick(self):
		self.variables['status'].set('Stopped')
		self.widgets['start'].configure(state='normal')
		self.widgets['stop'].configure(state='disabled')
		self.imu.stop()
	def OnToggleAutostartClick(self):
		self.autostart = Setting.set('imu_autostart', self.variables['autostart'].get())
	def OnCalibrateClick(self):
		self.imu.calibrate()
	def OnToggleArchiveGyroRaw(self):
		Setting.set('imu_archive_gyro_raw', self.variables['archivegyroraw'].get())
	def OnToggleArchiveAccRaw(self):
		Setting.set('imu_archive_acc_raw', self.variables['archiveaccraw'].get())
	def OnToggleArchiveGyroNorm(self):
		Setting.set('imu_archive_gyro_norm', self.variables['archivegyronorm'].get())
	def OnToggleArchiveAccNorm(self):
		Setting.set('imu_archive_acc_norm', self.variables['archiveaccnorm'].get())
	def OnToggleArchiveGyroAng(self):
		Setting.set('imu_archive_gyro_ang', self.variables['archivegyroang'].get())
	def OnToggleArchiveGyroAngInc(self):
		Setting.set('imu_archive_gyro_ang_inc', self.variables['archivegyroanginc'].get())
	def OnToggleArchiveAccAng(self):
		Setting.set('imu_archive_acc_ang', self.variables['archiveaccang'].get())
	def OnToggleArchiveLow(self):
		Setting.set('imu_archive_low', self.variables['archivelow'].get())
	def OnToggleArchiveHigh(self):
		Setting.set('imu_archive_high', self.variables['archivehigh'].get())
	def OnToggleArchiveCom(self):
		Setting.set('imu_archive_com', self.variables['archivecom'].get())
	def OnToggleWatchRawClick(self):
		Setting.set('imu_watch_raw', self.variables['watchraw'].get())
		self.updateDataOptions()
	def OnToggleDisplayRawClick(self):
		Setting.set('imu_display_raw', self.variables['displayraw'].get())
	def OnToggleWatchNormClick(self):
		Setting.set('imu_watch_norm', self.variables['watchnorm'].get())
		self.updateDataOptions()
	def OnToggleDisplayNormClick(self):
		Setting.set('imu_display_norm', self.variables['displaynorm'].get())
	def OnToggleWatchAngClick(self):
		Setting.set('imu_watch_ang', self.variables['watchang'].get())
		self.updateDataOptions()
	def OnToggleDisplayAngClick(self):
		Setting.set('imu_display_ang', self.variables['displayang'].get())
	def OnToggleWatchComClick(self):
		Setting.set('imu_watch_com', self.variables['watchcom'].get())
		self.updateDataOptions()
	def OnToggleDisplayComClick(self):
		Setting.set('imu_display_com', self.variables['displaycom'].get())
	def OnToggleWatchLowClick(self):
		Setting.set('imu_watch_low', self.variables['watchlow'].get())
		self.updateDataOptions()
	def OnToggleDisplayLowClick(self):
		Setting.set('imu_display_low', self.variables['displaylow'].get())
	def OnToggleWatchHighClick(self):
		Setting.set('imu_watch_high', self.variables['watchhigh'].get())
		self.updateDataOptions()
	def OnToggleDisplayHighClick(self):
		Setting.set('imu_display_high', self.variables['displayhigh'].get())
	def OnShowIMUDataClick(self):
		self.showData()
		self.imu.addCallback('display', self.updateData)
	def OnOrientationClick(self):
		self.initImages()
		self.showOrientation()