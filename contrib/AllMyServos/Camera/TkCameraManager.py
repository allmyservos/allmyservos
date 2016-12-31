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
import Tkinter, JsonBlob, Camera
from __bootstrap import AmsEnvironment
from Tkinter import *
from TkBlock import *
from TkDependencyManager import *

## UI for camera configuration
class TkCameraManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes the TkCameraManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkCameraManager,self).__init__(parent, gui, **options)
		try:
			self.gui.kbthread
		except:
			self.gui.kbthread = Keyboard.KeyboardThread(self.gui.specification, self.gui.motionScheduler, self.gui.scheduler, not Setting.get('kb_use_tk_callback', True))
		self.kbthread = self.gui.kbthread
		try:
			self.gui.camera
		except:
			self.gui.camera = Camera.Camera(self.gui.scheduler, self.kbthread, self.notifier)
		self.camera = self.gui.camera
		self.tips = {
			'mode': 'stopped',
			'synced': False,
			'text': {
				'stopped': [
					'Start the service to begin'
				],
				'started': [
					'The service is running',
					'Capture and stream available'
				],
				'stream_start': [
					'Starting stream'
				],
				'stream_connecting': [
					'Available URLs:'
				],
				'stream_connected': [
					'Streaming in progress'
				],
				'stream_stop': [
					'Stream stopped'
				],
				'recording': [
					'Recording in progress'
				]
			}
		}
	def setup(self):
		""" setup gui menu
		"""
		try:
			self.gui.menus['cam']
		except:
			self.gui.menus['cam'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="Camera", menu=self.gui.menus['cam'])
		self.gui.menus['cam'].add_command(label="Manage", command=self.OnManageClick)
		
	#=== VIEWS ===#
	def cameraRequirements(self):
		""" view - displays the camera requirements
		"""
		self.open()
		
		self.widgets['mainlabel'] = Tkinter.Label(self.widgets['tframe'],text='Camera / Requirements', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['mainlabel'].grid(column=0,row=self.gridrow,columnspan=3,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['ilabel1'] = Tkinter.Label(self.widgets['tframe'],text='Interface', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['ilabel1'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['vlabel1'] = Tkinter.Label(self.widgets['tframe'],text='Enabled' if self.camera.info['cam_config']['start_x'] else 'Disabled', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['vlabel1'].grid(column=1,row=self.gridrow,sticky='EW')
		
		if (not self.camera.info['cam_config']['start_x']):
			self.widgets['tlabel1'] = Tkinter.Label(self.widgets['tframe'],text='The camera is not enabled in raspi-config', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['tlabel1'].grid(column=2,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1
		
		self.widgets['ilabel2'] = Tkinter.Label(self.widgets['tframe'],text='GPU Memory', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['ilabel2'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['vlabel2'] = Tkinter.Label(self.widgets['tframe'],text='OK' if self.camera.info['cam_config']['gpu_mem'] >= 128 else 'Too low', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['vlabel2'].grid(column=1,row=self.gridrow,sticky='EW')
		
		if (self.camera.info['cam_config']['gpu_mem'] < 128):
			self.widgets['tlabel2'] = Tkinter.Label(self.widgets['tframe'],text='Allocate at least 128MB GPU memory in raspi-config', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['tlabel2'].grid(column=2,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1
		
		self.widgets['ilabel3'] = Tkinter.Label(self.widgets['tframe'],text='Hardware', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['ilabel3'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['vlabel3'] = Tkinter.Label(self.widgets['tframe'],text='OK' if self.camera.info['cam_config']['hardware'] else 'Missing', anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['vlabel3'].grid(column=1,row=self.gridrow,sticky='EW')
		
		if (not self.camera.info['cam_config']['hardware']):
			self.widgets['tlabel3'] = Tkinter.Label(self.widgets['tframe'],text='Check the camera cable connections', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['tlabel3'].grid(column=2,row=self.gridrow,sticky='EW')
	def cameraManager(self):
		""" view - displays the manage page
		"""
		self.open()
		
		self.widgets['servicelabel'] = Tkinter.Label(self.widgets['tframe'],text='Camera / Camera Manager', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['servicelabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		#left frame prevents rowspan stretching
		self.widgets['leftframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['leftframe'].grid(column=0,row=self.gridrow, sticky='NW')
		
		#service manager
		self.widgets['service'] = self.serviceManager(self.widgets['leftframe'])
		self.widgets['service'].grid(column=1,row=0, pady=10,sticky='NW')
		
		#viewfinder
		self.widgets['viewfinder'] = self.viewFinder(self.widgets['leftframe'])
		self.widgets['viewfinder'].grid(column=1,row=1, sticky='NW')
		
		#camera profile
		self.widgets['profile'] = self.cameraProfile(self.widgets['tframe'])
		self.widgets['profile'].grid(column=1,row=self.gridrow, padx=10, sticky='NW')
		
	def serviceManager(self, rootElem):
		""" view - displays the camera service manager
		
		@param rootElem
		
		@return Frame
		"""
		serviceWidget = Tkinter.Frame(rootElem, bg=self.colours['bg'])
		
		self.widgets['statusLabel'] = Tkinter.Label(serviceWidget,text='Status', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['statusLabel'].grid(column=0,row=0,sticky='EW')
		
		self.variables['status'] = Tkinter.StringVar()
		self.widgets['statusdata'] = Tkinter.Label(serviceWidget,textvariable=self.variables['status'], bg=self.colours['bg'], fg=self.colours['fg'], font=self.fonts['heading2'])
		self.widgets['statusdata'].grid(column=0,row=1,padx=50, sticky='EW')
			
		self.widgets['start'] = Tkinter.Button(serviceWidget,text=u"Start", image=self.images['play'], command=self.OnStartClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['start'].grid(column=1,row=1,sticky='W')
		
		self.widgets['stop'] = Tkinter.Button(serviceWidget,text=u"Stop", image=self.images['stop'], command=self.OnStopClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['stop'].grid(column=2,row=1,sticky='W')
		
		if(self.camera.isServiceRunning() == True):
			self.variables['status'].set('Running')
			self.widgets['start'].configure(state='disabled')
		else:
			self.variables['status'].set('Stopped')
			self.widgets['stop'].configure(state='disabled')
			
		self.variables['autostart'] = Tkinter.BooleanVar()
		self.variables['autostart'].set(Setting.get('cam_autostart', False))
		self.widgets['autostartentry'] = Tkinter.Checkbutton(serviceWidget, text="Autostart", variable=self.variables['autostart'], command=self.OnToggleAutostartClick, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['autostartentry'].grid(column=3,row=1)
		
		self.updateServiceManager()
		self.camera.addCallback('update_service_man', self.updateServiceManager)
		
		return serviceWidget
		
	def viewFinder(self, rootElem):
		""" partial view - displays view finder
		
		@param rootElem
		
		@return Frame
		"""
		#view finder
		viewFinderFrame = Tkinter.Frame(rootElem, bg=self.colours['bg'])
		viewFinderFrame.grid(column=0,row=self.gridrow,sticky='N')
		
		self.widgets['mrframe'] = Tkinter.Frame(viewFinderFrame, bg=self.colours['bg'])
		self.widgets['mrframe'].grid(column=0,row=0,sticky='N')
		
		self.widgets['maxResLabel'] = Tkinter.Label(self.widgets['mrframe'],text='Max Resolution', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['maxResLabel'].grid(column=0,row=0,sticky='W')
		
		self.widgets['maxResValue'] = Tkinter.Label(self.widgets['mrframe'],text='-', bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['maxResValue'].grid(column=1,row=0,sticky='W')
		
		if (hasattr(self, 'camera') and hasattr(self.camera, 'info') and self.camera.info['max_res'][0] > 0):
			self.widgets['maxResValue'].configure(text='{} x {}'.format(self.camera.info['max_res'][0],self.camera.info['max_res'][1]))
		
		self.widgets['revLabel'] = Tkinter.Label(self.widgets['mrframe'],text='H/W Revision', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['revLabel'].grid(column=0,row=1,sticky='W')
		
		self.widgets['revValue'] = Tkinter.Label(self.widgets['mrframe'],text='-' if self.camera.info['revision'] == 0 else self.camera.info['revision'], bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['revValue'].grid(column=1,row=1,sticky='W')
		
		self.widgets['camvf'] = Tkinter.Frame(viewFinderFrame, bg=self.colours['bg'], width=self.camera.cam_profile.jsonData['viewfinder'][0], height=self.camera.cam_profile.jsonData['viewfinder'][1])
		self.widgets['camvf'].grid(column=0,row=2,sticky='W')
		
		self.widgets['cambgimg'] = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'camera','cam-bg-{}.gif'.format(self.camera.cam_profile.jsonData['viewfinder'][0])))
		self.widgets['cambgLabel'] = Tkinter.Label(self.widgets['camvf'],image=self.widgets['cambgimg'], bg=self.colours['bg'])
		self.widgets['cambgLabel'].grid(column=0,row=0,sticky='EW')
		
		#controls
		self.widgets['ctrlframe'] = Tkinter.Frame(viewFinderFrame, bg=self.colours['bg'])
		self.widgets['ctrlframe'].grid(column=0,row=3,columnspan=2, sticky='NW')
		
		self.widgets['recimg'] = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'camera','record.gif'))
		self.widgets['rec'] = Tkinter.Button(self.widgets['ctrlframe'],text=u"Capture", image=self.widgets['recimg'], command=self.OnCaptureClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['rec'].grid(column=0,row=0,sticky='W')
		
		self.widgets['recLabel'] = Tkinter.Label(self.widgets['ctrlframe'],text='Capture Photo', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['recLabel'].grid(column=1,row=0,padx=10,sticky='EW')
		
		self.widgets['streamimg'] = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'camera','stream.gif'))
		self.widgets['stream'] = Tkinter.Button(self.widgets['ctrlframe'],text=u"Stream", image=self.widgets['streamimg'] if not self.camera.isStreaming() else self.images['stop'], command=self.OnStreamClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['stream'].grid(column=2,row=0,sticky='W')
		
		self.widgets['streamLabel'] = Tkinter.Label(self.widgets['ctrlframe'],text='Start stream' if not self.camera.isStreaming() else 'Stop stream', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['streamLabel'].grid(column=3,row=0,padx=10,sticky='EW')
		
		self.widgets['tipsframe'] = Tkinter.Frame(self.widgets['ctrlframe'], bg=self.colours['bg'])
		self.widgets['tipsframe'].grid(column=0,row=1,columnspan=4, sticky='NW')
		
		self.widgets['tipsLabel'] = Tkinter.Label(self.widgets['tipsframe'],text='Tips', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['tipsLabel'].grid(column=0,row=0,pady=10,sticky='EW')
		
		self.widgets['tips'] = Tkinter.Frame(self.widgets['tipsframe'], bg=self.colours['bg'])
		self.widgets['tips'].grid(column=0,row=1,columnspan=4, sticky='NW')
		
		self.updateCapture()
		self.camera.addCallback('update_capture_display', self.updateCapture)
		
		#camera profiles
		self.widgets['profiles'] = self.cameraProfiles(viewFinderFrame)
		self.widgets['profiles'].grid(column=0,row=4, sticky='W')
		
		return viewFinderFrame
	def cameraProfile(self, rootElem):
		""" partial view - displays the current profile
		
		@param rootElem
		
		@return Frame
		"""
		gridrow = 0
		profileWidget = Tkinter.Frame(rootElem, bg=self.colours['bg'])
		
		self.widgets['profileLabel'] = Tkinter.Label(profileWidget,text='Camera Profile', bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['profileLabel'].grid(column=0,row=gridrow,sticky='W')
		
		gridrow += 1
		
		self.widgets['vfresLabel'] = Tkinter.Label(profileWidget,text='Viewfinder Res', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['vfresLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		self.widgets['vfframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
		self.widgets['vfframe'].grid(column=1,row=gridrow, sticky='W')
		
		self.variables['vfres'] = Tkinter.StringVar()
		self.variables['vfres'].set('{}x{}'.format(self.camera.cam_profile.jsonData['viewfinder'][0],self.camera.cam_profile.jsonData['viewfinder'][1]))
		self.widgets['vfentry'] = Tkinter.OptionMenu(self.widgets['vfframe'],self.variables['vfres'], '320x240', '640x480')
		self.widgets['vfentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
		self.widgets['vfentry'].grid(column=1,row=gridrow,sticky='EW')
		
		self.widgets['vfrefreshbutton'] = Tkinter.Button(self.widgets['vfframe'],text=u"Refresh", image=self.images['accept'], command=self.OnVfRefreshClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['vfrefreshbutton'].grid(column=2,row=gridrow)
		
		gridrow += 1
		
		self.widgets['recmodeLabel'] = Tkinter.Label(profileWidget,text='Record Mode', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['recmodeLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		self.widgets['rmframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
		self.widgets['rmframe'].grid(column=1,row=gridrow, sticky='W')
		
		self.widgets['stillimg'] = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'camera','still.gif'))
		self.widgets['recstillbutton'] = Tkinter.Button(self.widgets['rmframe'],text=u"Still", image=self.widgets['stillimg'], command=self.OnStillModeClick, bg=self.colours['bg'], activebackground=self.colours['bg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['recstillbutton'].grid(column=0,row=gridrow)
		
		self.widgets['videoimg'] = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'camera','video.gif'))
		self.widgets['recvidbutton'] = Tkinter.Button(self.widgets['rmframe'],text=u"Video", image=self.widgets['videoimg'], command=self.OnVideoModeClick, bg=self.colours['bg'], activebackground=self.colours['bg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['recvidbutton'].grid(column=1,row=gridrow)
		
		recMode = self.camera.cam_profile.getRecMode()
		if (recMode == 'video'):
			self.widgets['recstillbutton'].configure(state='normal')
			self.widgets['recvidbutton'].configure(state='disabled')
		else:
			self.widgets['recstillbutton'].configure(state='disabled')
			self.widgets['recvidbutton'].configure(state='normal')
			
		self.widgets['recmodeLabel'] = Tkinter.Label(self.widgets['rmframe'],text='Video' if recMode == 'video' else 'Photo', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['recmodeLabel'].grid(column=2,row=gridrow,padx=10, sticky='EW')
			
		gridrow += 1
		
		self.widgets['recresLabel'] = Tkinter.Label(profileWidget,text='Record Res', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['recresLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		self.widgets['rrframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
		self.widgets['rrframe'].grid(column=1,row=gridrow, sticky='W')
		
		resolution = self.camera.cam_profile.getResolution()
		resOptions = self.camera.info['{}_res_modes'.format(self.camera.cam_profile.getRecMode())]
		
		self.variables['rrres'] = Tkinter.StringVar()
		self.variables['rrres'].set('{}x{}'.format(resolution[0],resolution[1]))
		self.widgets['rrentry'] = Tkinter.OptionMenu(self.widgets['rrframe'],self.variables['rrres'], *resOptions)
		self.widgets['rrentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
		self.widgets['rrentry'].grid(column=1,row=gridrow,sticky='EW')
		
		self.widgets['rrrefreshbutton'] = Tkinter.Button(self.widgets['rrframe'],text=u"Refresh", image=self.images['accept'], command=self.OnResRefreshClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['rrrefreshbutton'].grid(column=2,row=gridrow)
		
		gridrow += 1
		
		self.widgets['fpsLabel'] = Tkinter.Label(profileWidget,text='FPS', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['fpsLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		self.widgets['fpsframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
		self.widgets['fpsframe'].grid(column=1,row=gridrow, sticky='W')
		
		fpsOptions = self.camera.info['fps_options']['{}x{}'.format(resolution[0],resolution[1])]
		
		self.variables['fps'] = Tkinter.IntVar()
		self.variables['fps'].set(self.camera.cam_profile.jsonData['fps'])
		self.widgets['fpsentry'] = Tkinter.OptionMenu(self.widgets['fpsframe'],self.variables['fps'], *fpsOptions)
		self.widgets['fpsentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
		self.widgets['fpsentry'].grid(column=1,row=gridrow,sticky='EW')
		
		self.widgets['fpsrefreshbutton'] = Tkinter.Button(self.widgets['fpsframe'],text=u"Refresh", image=self.images['accept'], command=self.OnFpsRefreshClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['fpsrefreshbutton'].grid(column=2,row=gridrow)
		
		if (self.camera.cam_profile.getRecMode() == 'video'):
			self.widgets['fpsentry'].configure(state='normal')
			self.widgets['fpsrefreshbutton'].configure(state='normal')
		else:
			self.widgets['fpsentry'].configure(state='disabled')
			self.widgets['fpsrefreshbutton'].configure(state='disabled')
		gridrow += 1
		
		self.widgets['recforLabel'] = Tkinter.Label(profileWidget,text='Record Format', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['recforLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		self.widgets['rfframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
		self.widgets['rfframe'].grid(column=1,row=gridrow, sticky='W')
		
		formatOptions = self.camera.info['formats'][self.camera.cam_profile.getRecMode()]
		
		self.variables['format'] = Tkinter.StringVar()
		self.variables['format'].set(self.camera.cam_profile.getFormat())
		self.widgets['formatentry'] = Tkinter.OptionMenu(self.widgets['rfframe'],self.variables['format'], *formatOptions)
		self.widgets['formatentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
		self.widgets['formatentry'].grid(column=1,row=gridrow,sticky='EW')
		
		self.widgets['rfrefreshbutton'] = Tkinter.Button(self.widgets['rfframe'],text=u"Refresh", image=self.images['accept'], command=self.OnFormatRefreshClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['rfrefreshbutton'].grid(column=2,row=gridrow)
		
		gridrow += 1
		
		self.widgets['ledLabel'] = Tkinter.Label(profileWidget,text='Recording LED', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['ledLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		self.variables['camLed'] = Tkinter.BooleanVar()
		self.variables['camLed'].set(self.camera.cam_profile.jsonData['led'])
		self.widgets['camLedentry'] = Tkinter.Checkbutton(profileWidget, variable=self.variables['camLed'], text='', anchor=W, command=self.OnToggleCamLed, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['camLedentry'].grid(column=1,row=gridrow, padx=5, sticky="W")
		
		gridrow += 1
		
		self.widgets['fliphLabel'] = Tkinter.Label(profileWidget,text='Flip Horizontal', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['fliphLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		self.variables['camFlipH'] = Tkinter.BooleanVar()
		self.variables['camFlipH'].set(self.camera.cam_profile.jsonData['fliph'])
		self.widgets['camFlipHentry'] = Tkinter.Checkbutton(profileWidget, variable=self.variables['camFlipH'], text='', anchor=W, command=self.OnToggleFliph, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['camFlipHentry'].grid(column=1,row=gridrow, padx=5, sticky="W")
		
		gridrow += 1
		
		self.widgets['flipvLabel'] = Tkinter.Label(profileWidget,text='Flip Vertically', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['flipvLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		self.variables['camFlipV'] = Tkinter.BooleanVar()
		self.variables['camFlipV'].set(self.camera.cam_profile.jsonData['flipv'])
		self.widgets['camFlipVentry'] = Tkinter.Checkbutton(profileWidget, variable=self.variables['camFlipV'], text='', anchor=W, command=self.OnToggleFlipv, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['camFlipVentry'].grid(column=1,row=gridrow, padx=5, sticky="W")
		
		gridrow += 1
		
		self.widgets['vstabLabel'] = Tkinter.Label(profileWidget,text='Video Stabilization', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['vstabLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		self.variables['vstab'] = Tkinter.BooleanVar()
		self.variables['vstab'].set(self.camera.cam_profile.jsonData['video_stabilization'])
		self.widgets['vstabentry'] = Tkinter.Checkbutton(profileWidget, variable=self.variables['vstab'], text='', anchor=W, command=self.OnToggleVstab, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['vstabentry'].grid(column=1,row=gridrow, padx=5, sticky="W")
		
		gridrow += 1
		
		self.widgets['roLabel'] = Tkinter.Label(profileWidget,text='Rotation', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['roLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		self.widgets['roframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
		self.widgets['roframe'].grid(column=1,row=gridrow, sticky='W')
		
		self.variables['rotation'] = Tkinter.StringVar()
		self.variables['rotation'].set(self.camera.cam_profile.jsonData['rotation'])
		self.widgets['roentry'] = Tkinter.OptionMenu(self.widgets['roframe'],self.variables['rotation'], *self.camera.info['rotations'])
		self.widgets['roentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
		self.widgets['roentry'].grid(column=1,row=gridrow,sticky='EW')
		
		self.widgets['rorefreshbutton'] = Tkinter.Button(self.widgets['roframe'],text=u"Refresh", image=self.images['accept'], command=self.OnRotRefreshClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['rorefreshbutton'].grid(column=2,row=gridrow)
		
		gridrow += 1
		
		if (hasattr(self, 'camera') and hasattr(self.camera, 'info')):
			self.widgets['sharpLabel'] = Tkinter.Label(profileWidget,text='Sharpness', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['sharpLabel'].grid(column=0,row=gridrow,sticky='EW')
			
			self.variables['sharpness'] = Tkinter.IntVar()
			self.variables['sharpness'].set(int(self.camera.cam_profile.jsonData['sharpness']))
			self.widgets['sharpentry'] = Tkinter.Scale(profileWidget, from_=self.camera.info['sharpness_range'][0], to=self.camera.info['sharpness_range'][1], variable=self.variables['sharpness'], command=self.OnSharpnessChange, resolution=1, orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
			self.widgets['sharpentry'].grid(column=1,row=gridrow)
		
			gridrow += 1
			
			self.widgets['conLabel'] = Tkinter.Label(profileWidget,text='Contrast', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['conLabel'].grid(column=0,row=gridrow,sticky='EW')
			
			self.variables['contrast'] = Tkinter.IntVar()
			self.variables['contrast'].set(int(self.camera.cam_profile.jsonData['contrast']))
			self.widgets['conentry'] = Tkinter.Scale(profileWidget, from_=self.camera.info['contrast_range'][0], to=self.camera.info['contrast_range'][1], variable=self.variables['contrast'], command=self.OnContrastChange, resolution=1, orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
			self.widgets['conentry'].grid(column=1,row=gridrow)
			
			gridrow += 1
			
			self.widgets['briLabel'] = Tkinter.Label(profileWidget,text='Brightness', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['briLabel'].grid(column=0,row=gridrow,sticky='EW')
			
			self.variables['brightness'] = Tkinter.IntVar()
			self.variables['brightness'].set(int(self.camera.cam_profile.jsonData['brightness']))
			self.widgets['brientry'] = Tkinter.Scale(profileWidget, from_=self.camera.info['brightness_range'][0], to=self.camera.info['brightness_range'][1], variable=self.variables['brightness'], command=self.OnBrightnessChange, resolution=1, orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
			self.widgets['brientry'].grid(column=1,row=gridrow)
		
			gridrow += 1
			
			self.widgets['satLabel'] = Tkinter.Label(profileWidget,text='Saturation', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['satLabel'].grid(column=0,row=gridrow,sticky='EW')
			
			self.variables['saturation'] = Tkinter.IntVar()
			self.variables['saturation'].set(int(self.camera.cam_profile.jsonData['saturation']))
			self.widgets['satentry'] = Tkinter.Scale(profileWidget, from_=self.camera.info['saturation_range'][0], to=self.camera.info['saturation_range'][1], variable=self.variables['saturation'], command=self.OnSaturationChange, resolution=1, orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
			self.widgets['satentry'].grid(column=1,row=gridrow)
		
			gridrow += 1
			
			self.widgets['zoomLabel'] = Tkinter.Label(profileWidget,text='Zoom', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['zoomLabel'].grid(column=0,row=gridrow,sticky='EW')
			
			self.widgets['zoomframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
			self.widgets['zoomframe'].grid(column=1,row=gridrow, sticky='W')
			
			self.widgets['zoomxLabel'] = Tkinter.Label(self.widgets['zoomframe'],text='X', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['zoomxLabel'].grid(column=0,row=0,padx=10,sticky='EW')
			
			self.variables['zoomx'] = Tkinter.DoubleVar()
			self.variables['zoomx'].set(float(self.camera.cam_profile.jsonData['zoom'][0]))
			self.widgets['zoomxentry'] = Tkinter.Scale(self.widgets['zoomframe'], from_=self.camera.info['zoom_range'][0], to=self.camera.info['zoom_range'][1], variable=self.variables['zoomx'], command=self.OnZoomChange, resolution=0.1, orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
			self.widgets['zoomxentry'].grid(column=1,row=0)
			
			self.widgets['zoomyLabel'] = Tkinter.Label(self.widgets['zoomframe'],text='Y', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['zoomyLabel'].grid(column=0,row=1,padx=10,sticky='EW')
			
			self.variables['zoomy'] = Tkinter.DoubleVar()
			self.variables['zoomy'].set(float(self.camera.cam_profile.jsonData['zoom'][1]))
			self.widgets['zoomyentry'] = Tkinter.Scale(self.widgets['zoomframe'], from_=self.camera.info['zoom_range'][0], to=self.camera.info['zoom_range'][1], variable=self.variables['zoomy'], command=self.OnZoomChange, resolution=0.1, orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
			self.widgets['zoomyentry'].grid(column=1,row=1)
			
			self.widgets['zoomwLabel'] = Tkinter.Label(self.widgets['zoomframe'],text='W', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['zoomwLabel'].grid(column=0,row=2,padx=10,sticky='EW')
			
			self.variables['zoomw'] = Tkinter.DoubleVar()
			self.variables['zoomw'].set(float(self.camera.cam_profile.jsonData['zoom'][2]))
			self.widgets['zoomwentry'] = Tkinter.Scale(self.widgets['zoomframe'], from_=self.camera.info['zoom_range'][0], to=self.camera.info['zoom_range'][1], variable=self.variables['zoomw'], command=self.OnZoomChange, resolution=0.1, orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
			self.widgets['zoomwentry'].grid(column=1,row=2)
			
			self.widgets['zoomhLabel'] = Tkinter.Label(self.widgets['zoomframe'],text='H', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['zoomhLabel'].grid(column=0,row=3,padx=10,sticky='EW')
			
			self.variables['zoomh'] = Tkinter.DoubleVar()
			self.variables['zoomh'].set(float(self.camera.cam_profile.jsonData['zoom'][3]))
			self.widgets['zoomhentry'] = Tkinter.Scale(self.widgets['zoomframe'], from_=self.camera.info['zoom_range'][0], to=self.camera.info['zoom_range'][1], variable=self.variables['zoomh'], command=self.OnZoomChange, resolution=0.1, orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
			self.widgets['zoomhentry'].grid(column=1,row=3)
			
			gridrow += 1
			
			self.widgets['isoLabel'] = Tkinter.Label(profileWidget,text='ISO', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['isoLabel'].grid(column=0,row=gridrow,sticky='EW')
			
			self.widgets['isoframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
			self.widgets['isoframe'].grid(column=1,row=gridrow, sticky='W')
			
			self.variables['iso'] = Tkinter.StringVar()
			self.variables['iso'].set('Auto' if int(self.camera.cam_profile.jsonData['iso']) == 0 else self.camera.cam_profile.jsonData['iso'])
			self.widgets['isoentry'] = Tkinter.OptionMenu(self.widgets['isoframe'],self.variables['iso'], *self.camera.info['iso_range'])
			self.widgets['isoentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
			self.widgets['isoentry'].grid(column=0,row=gridrow,sticky='EW')
			
			self.widgets['rrrefreshbutton'] = Tkinter.Button(self.widgets['isoframe'],text=u"Refresh", image=self.images['accept'], command=self.OnIsoRefreshClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['rrrefreshbutton'].grid(column=1,row=gridrow)
		
			gridrow += 1
			
			if (any(self.camera.info['effects'])):
				self.widgets['effectLabel'] = Tkinter.Label(profileWidget,text='Image Effect', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['effectLabel'].grid(column=0,row=gridrow,sticky='EW')
				
				self.widgets['eframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
				self.widgets['eframe'].grid(column=1,row=gridrow, sticky='W')
				
				self.variables['effect'] = Tkinter.StringVar()
				self.variables['effect'].set(self.camera.cam_profile.jsonData['image_effect'])
				self.widgets['effectentry'] = Tkinter.OptionMenu(self.widgets['eframe'],self.variables['effect'], *self.camera.info['effects'])
				self.widgets['effectentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
				self.widgets['effectentry'].grid(column=1,row=gridrow,sticky='EW')
				
				self.widgets['erefreshbutton'] = Tkinter.Button(self.widgets['eframe'],text=u"Refresh", image=self.images['accept'], command=self.OnEffectRefreshClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
				self.widgets['erefreshbutton'].grid(column=2,row=gridrow)
				
				gridrow += 1
				
			if (any(self.camera.info['exposure_modes'])):
				self.widgets['expLabel'] = Tkinter.Label(profileWidget,text='Exposure Mode', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['expLabel'].grid(column=0,row=gridrow,sticky='EW')
				
				self.widgets['exframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
				self.widgets['exframe'].grid(column=1,row=gridrow, sticky='W')
				
				self.variables['expmode'] = Tkinter.StringVar()
				self.variables['expmode'].set(self.camera.cam_profile.jsonData['exposure_mode'])
				self.widgets['expentry'] = Tkinter.OptionMenu(self.widgets['exframe'],self.variables['expmode'], *self.camera.info['exposure_modes'])
				self.widgets['expentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
				self.widgets['expentry'].grid(column=1,row=gridrow,sticky='EW')
				
				self.widgets['erefreshbutton'] = Tkinter.Button(self.widgets['exframe'],text=u"Refresh", image=self.images['accept'], command=self.OnExpModeRefreshClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
				self.widgets['erefreshbutton'].grid(column=2,row=gridrow)
				
				gridrow += 1
			if (any(self.camera.info['awb_modes'])):
				self.widgets['awbLabel'] = Tkinter.Label(profileWidget,text='Auto White Balance', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['awbLabel'].grid(column=0,row=gridrow,sticky='EW')
				
				self.widgets['aframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
				self.widgets['aframe'].grid(column=1,row=gridrow, sticky='W')
				
				self.variables['awb'] = Tkinter.StringVar()
				self.variables['awb'].set(self.camera.cam_profile.jsonData['awb_mode'])
				self.widgets['awbentry'] = Tkinter.OptionMenu(self.widgets['aframe'],self.variables['awb'], *self.camera.info['awb_modes'])
				self.widgets['awbentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
				self.widgets['awbentry'].grid(column=1,row=gridrow,sticky='EW')
				
				self.widgets['arefreshbutton'] = Tkinter.Button(self.widgets['aframe'],text=u"Refresh", image=self.images['accept'], command=self.OnAwbModeRefreshClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
				self.widgets['arefreshbutton'].grid(column=2,row=gridrow)
				
				gridrow += 1
				
				self.widgets['awbLabel'] = Tkinter.Label(profileWidget,text='AWB Gains', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['awbLabel'].grid(column=0,row=gridrow,sticky='EW')
				
				self.widgets['againsframe'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
				self.widgets['againsframe'].grid(column=1,row=gridrow, sticky='W')
				
				self.widgets['awbredLabel'] = Tkinter.Label(self.widgets['againsframe'],text='Red', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['awbredLabel'].grid(column=0,row=gridrow,padx=5,sticky='EW')
				
				self.variables['awbred'] = Tkinter.DoubleVar()
				self.variables['awbred'].set(self.camera.cam_profile.jsonData['awb_gains'][0])
				self.widgets['awbredentry'] = Tkinter.Scale(self.widgets['againsframe'], from_=self.camera.info['awb_range'][0], to=self.camera.info['awb_range'][1], variable=self.variables['awbred'], command=self.OnAwbRedChange, resolution=0.1, orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
				self.widgets['awbredentry'].grid(column=1,row=gridrow)
				
				gridrow += 1
				
				self.widgets['awbblueLabel'] = Tkinter.Label(self.widgets['againsframe'],text='Blue', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'])
				self.widgets['awbblueLabel'].grid(column=0,row=gridrow,padx=5,sticky='EW')
				
				self.variables['awbblue'] = Tkinter.DoubleVar()
				self.variables['awbblue'].set(self.camera.cam_profile.jsonData['awb_gains'][1])
				self.widgets['awbblueentry'] = Tkinter.Scale(self.widgets['againsframe'], from_=self.camera.info['awb_range'][0], to=self.camera.info['awb_range'][1], variable=self.variables['awbblue'], command=self.OnAwbBlueChange, resolution=0.1, orient=Tkinter.HORIZONTAL, length = 200, bg=self.colours['bg'], fg=self.colours['fg'], activebackground=self.colours['inputfg'], troughcolor=self.colours['inputbg'])
				self.widgets['awbblueentry'].grid(column=1,row=gridrow)
				
				self.updateAwbGains()
				
				gridrow += 1
				
			
		gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(profileWidget, bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=gridrow,columnspan=2, sticky='EW')
		
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=0,row=gridrow,sticky='EW')

		gridrow += 1

		self.widgets['save'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveProfileClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['save'].grid(column=0,row=gridrow)
		
		return profileWidget
	def cameraProfiles(self, rootElem):
		""" partial view - list camera profiles
		
		@param rootElem
		
		@return Frame
		"""
		gridrow = 0
		profileWidget = Tkinter.Frame(rootElem, bg=self.colours['bg'])
		
		gridrow += 1
		
		self.widgets['cpLabel'] = Tkinter.Label(profileWidget,text='Camera Profiles', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], font=self.fonts['heading2'])
		self.widgets['cpLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		gridrow += 1
		
		profiles = JsonBlob.JsonBlob.all('Camera', 'CameraProfile')
		
		if (any(profiles)):
			self.widgets['nameLabel'] = Tkinter.Label(profileWidget,text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['nameLabel'].grid(column=0,row=gridrow,sticky='EW')
			self.widgets['rmLabel'] = Tkinter.Label(profileWidget,text='Rec Mode', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['rmLabel'].grid(column=1,row=gridrow,sticky='EW')
			self.widgets['resLabel'] = Tkinter.Label(profileWidget,text='Resolution', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['resLabel'].grid(column=2,row=gridrow,sticky='EW')
			self.widgets['actLabel'] = Tkinter.Label(profileWidget,text='Activate', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['actLabel'].grid(column=3,row=gridrow,sticky='EW')
			self.widgets['actLabel'] = Tkinter.Label(profileWidget,text='Delete', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['actLabel'].grid(column=4,row=gridrow,sticky='EW')
			
			gridrow += 1
			rowcount = 1
			for k,v in profiles.items():
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				
				self.widgets['{}name'.format(k)] = Tkinter.Label(profileWidget,text=v.jsonData['profile_name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['{}name'.format(k)].grid(column=0,row=gridrow,sticky='EW')
				
				self.widgets['{}rm'.format(k)] = Tkinter.Label(profileWidget,text=v.jsonData['rec_mode'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['{}rm'.format(k)].grid(column=1,row=gridrow,sticky='EW')
				
				resolution = v.getResolution()
				self.widgets['{}res'.format(k)] = Tkinter.Label(profileWidget,text='{} x {}'.format(resolution[0],resolution[1]), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['{}res'.format(k)].grid(column=2,row=gridrow,sticky='EW')
				
				self.widgets['{}actbutton'.format(k)] = Tkinter.Button(profileWidget,text=u"Activate", image=self.images['play'], command=lambda x = v.jbIndex:self.OnActivateProfileClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
				self.widgets['{}actbutton'.format(k)].grid(column=3,row=gridrow,sticky='EW')
				
				self.widgets['{}delbutton'.format(k)] = Tkinter.Button(profileWidget,text=u"Delete", image=self.images['delete'], command=lambda x = v.jbIndex:self.OnDeleteProfileClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
				self.widgets['{}delbutton'.format(k)].grid(column=4,row=gridrow,sticky='EW')
				
				gridrow += 1
			self.updateProfiles()
		else:
			self.widgets['noLabel'] = Tkinter.Label(profileWidget,text='There are currently no profiles.', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noLabel'].grid(column=0,row=gridrow,sticky='EW')
		
		return profileWidget
	
	def saveProfile(self):
		""" view - save profile
		"""
		self.open()
		
		self.widgets['saveplabel'] = Tkinter.Label(self.widgets['tframe'],text='Camera / Camera Manager / Save Profile', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['saveplabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['sframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['sframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Profile Name', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['name'] = Tkinter.StringVar()
		self.widgets['nameentry'] = Tkinter.Entry(self.widgets['sframe'], textvariable=self.variables['name'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['nameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['name'].set(self.camera.cam_profile.jsonData['profile_name'])
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Viewfinder Resolution', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		res = '{} x {}'.format(self.camera.cam_profile.jsonData['viewfinder'][0], self.camera.cam_profile.jsonData['viewfinder'][1])
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=res, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Recording mode', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=self.camera.cam_profile.getRecMode(), anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Still Resolution', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		res = '{} x {}'.format(self.camera.cam_profile.jsonData['still_res'][0], self.camera.cam_profile.jsonData['still_res'][1])
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=res, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Video Resolution', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		res = '{} x {}'.format(self.camera.cam_profile.jsonData['video_res'][0], self.camera.cam_profile.jsonData['video_res'][1])
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=res, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Recording LED', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text='Enabled' if self.camera.cam_profile.jsonData['led'] else 'Disabled', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Flip Horizontal', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text='Enabled' if self.camera.cam_profile.jsonData['fliph'] else 'Disabled', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')

		self.gridrow += 1

		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Flip Vertical', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text='Enabled' if self.camera.cam_profile.jsonData['flipv'] else 'Disabled', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Video Stabilization', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text='Enabled' if self.camera.cam_profile.jsonData['video_stabilization'] else 'Disabled', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Rotation', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=self.camera.cam_profile.jsonData['rotation'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Sharpness', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=self.camera.cam_profile.jsonData['sharpness'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Contrast', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=self.camera.cam_profile.jsonData['contrast'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Brightness', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=self.camera.cam_profile.jsonData['brightness'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Saturation', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=self.camera.cam_profile.jsonData['saturation'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='ISO', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=self.camera.cam_profile.jsonData['iso'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Image Effect', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=self.camera.cam_profile.jsonData['image_effect'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Exposure Mode', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=self.camera.cam_profile.jsonData['exposure_mode'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Auto White Balance', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=self.camera.cam_profile.jsonData['awb_mode'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['sframe'],text='Save the current profile with a new name.', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['sframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnManageClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['save'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Profile", image=self.images['save'], command=self.OnSaveProfileConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['save'].grid(column=1,row=self.gridrow)
	def deleteProfile(self, profile):
		""" view - delete profile
		
		@param profile
		"""
		self.open()
		
		self.widgets['dellabel'] = Tkinter.Label(self.widgets['tframe'],text='Camera / Camera Manager / Delete Profile', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['dellabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['sframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['sframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Profile Name', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jsonData['profile_name'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='ID', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jbIndex, anchor=W, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Viewfinder Resolution', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jsonData['viewfinder'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Recording mode', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.getRecMode(), anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Still Resolution', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		res = '{} x {}'.format(profile.jsonData['still_res'][0], profile.jsonData['still_res'][1])
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=res, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Video Resolution', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		res = '{} x {}'.format(profile.jsonData['video_res'][0], profile.jsonData['video_res'][1])
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=res, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Recording LED', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text='Enabled' if profile.jsonData['led'] else 'Disabled', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Flip Horizontal', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text='Enabled' if profile.jsonData['fliph'] else 'Disabled', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')

		self.gridrow += 1

		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Flip Vertical', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text='Enabled' if profile.jsonData['flipv'] else 'Disabled', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Video Stabilization', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text='Enabled' if profile.jsonData['video_stabilization'] else 'Disabled', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Rotation', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jsonData['rotation'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Sharpness', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jsonData['sharpness'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Contrast', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jsonData['contrast'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Brightness', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jsonData['brightness'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Saturation', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jsonData['saturation'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='ISO', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jsonData['iso'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Image Effect', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jsonData['image_effect'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Exposure Mode', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jsonData['exposure_mode'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['label'] = Tkinter.Label(self.widgets['sframe'],text='Auto White Balance', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['label'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['value'] = Tkinter.Label(self.widgets['sframe'],text=profile.jsonData['awb_mode'], anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['value'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['sframe'],text='Are you sure you want to delete this profile?', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['sframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['delLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['delLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnManageClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['del'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['accept'], command=lambda x = profile.jbIndex: self.OnDeleteProfileConfirmClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['del'].grid(column=1,row=self.gridrow)
	#=== ACTIONS ===#
	def OnStartClick(self):
		""" action - starts the camera service
		"""
		self.camera.start()
		self.updateServiceManager()
	def OnStopClick(self):
		""" action - stops the camera service
		"""
		self.camera.stop()
		self.updateServiceManager()
	def OnToggleAutostartClick(self):
		""" action - toggle service auto start
		"""
		self.autostart = Setting.set('cam_autostart', self.variables['autostart'].get())
	
	def OnManageClick(self):
		""" action - opens the camera manager if dependencies have been installed and camera requirements are met
		"""
		if (self.camera.isAvailable()):
			self.cameraManager()
			self.camera.enableViewfinder(element=self.widgets['camvf'])
		else:
			self.cameraRequirements()

	def OnStillModeClick(self):
		""" action - Sets profile to still mode
		"""
		self.camera.cam_profile.jsonData['rec_mode'] = 'still'
		self.widgets['recstillbutton'].configure(state='disabled')
		self.widgets['recvidbutton'].configure(state='normal')
		if (any(self.camera.info['still_res_modes'])):
			self.widgets['rrentry']['menu'].delete(0, 'end')
			for v in self.camera.info['still_res_modes'].keys():
				self.widgets['rrentry']['menu'].add_command(label=v, command=Tkinter._setit(self.variables['rrres'], v))
		if (any(self.camera.info['formats']['still'])):
			self.widgets['formatentry']['menu'].delete(0, 'end')
			for v in self.camera.info['formats']['still'].keys():
				self.widgets['formatentry']['menu'].add_command(label=v, command=Tkinter._setit(self.variables['format'], v))
		self.updateCapture() #update capture button
		self.updateCurrentProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
		self.notifier.addNotice('Camera mode: Photo')
	def OnVideoModeClick(self):
		""" action - Sets profile to video mode
		"""
		self.camera.cam_profile.jsonData['rec_mode'] = 'video'
		self.widgets['recstillbutton'].configure(state='normal')
		self.widgets['recvidbutton'].configure(state='disabled')
		if (any(self.camera.info['video_res_modes'])):
			self.widgets['rrentry']['menu'].delete(0, 'end')
			for v in self.camera.info['video_res_modes'].keys():
				self.widgets['rrentry']['menu'].add_command(label=v, command=Tkinter._setit(self.variables['rrres'], v))
		if (any(self.camera.info['formats']['video'])):
			self.widgets['formatentry']['menu'].delete(0, 'end')
			for v in self.camera.info['formats']['video'].keys():
				self.widgets['formatentry']['menu'].add_command(label=v, command=Tkinter._setit(self.variables['format'], v))
		self.updateCapture() #update capture button
		self.updateCurrentProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
		self.notifier.addNotice('Camera mode: Video')
	def OnVfRefreshClick(self):
		""" action - Applies viewfinder resolution option
		"""
		if (not self.camera.isPreviewing()):
			res = self.variables['vfres'].get().split('x')
			if (len(res) == 2):
				self.camera.cam_profile.jsonData['viewfinder'] = (int(res[0]), int(res[1]))
				self.widgets['camvf'].configure(width=self.camera.cam_profile.jsonData['viewfinder'][0], height=self.camera.cam_profile.jsonData['viewfinder'][1])
				self.updateCamBg()
			self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
			self.notifier.addNotice('Viewfinder Resolution: {} x {}'.format(self.camera.cam_profile.jsonData['viewfinder'][0], self.camera.cam_profile.jsonData['viewfinder'][1]))
		else:
			self.notifier.addNotice('Viewfinder cannot be updated while previewing','warning')
	def OnResRefreshClick(self):
		""" action - Applies resolution option
		"""
		if (not self.camera.isPreviewing() and not self.camera.isRecording()):
			res = self.variables['rrres'].get().split('x')
			if (len(res) == 2):
				self.camera.cam_profile.jsonData['{}_res'.format(self.camera.cam_profile.getRecMode())] = (int(res[0]), int(res[1]))
			self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
			self.notifier.addNotice('{} Resolution: {} x {}'.format('Photo' if self.camera.cam_profile.getRecMode() == 'still' else 'Video', int(res[0]), int(res[1])))
		else:
			self.notifier.addNotice('Resolution cannot be updated while running','warning')
		self.updateCurrentProfile()
	def OnFpsRefreshClick(self):
		""" action - Applies fps option
		"""
		fps = int(self.variables['fps'].get())
		self.camera.cam_profile.jsonData['fps'] = fps
		if (not self.camera.isPreviewing() and not self.camera.isRecording()):
			self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
			self.notifier.addNotice('FPS set to: {}'.format(fps))
		else:
			self.notifier.addNotice('FPS cannot be updated while running','warning')
	def OnFormatRefreshClick(self):
		""" action - Applies file format option
		"""
		res = self.variables['format'].get()
		if (len(res) > 2):
			self.camera.cam_profile.jsonData['{}_format'.format(self.camera.cam_profile.getRecMode())] = res
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
		self.notifier.addNotice('Capture Format: {}'.format(self.camera.cam_profile.jsonData['{}_format'.format(self.camera.cam_profile.getRecMode())]))
	def OnRotRefreshClick(self):
		""" action - Applies rotation option
		"""
		self.camera.cam_profile.jsonData['rotation'] = int(self.variables['rotation'].get())
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
		self.notifier.addNotice('Capture Rotation: {}'.format(self.camera.cam_profile.jsonData['rotation']))
	def OnIsoRefreshClick(self):
		""" action - Applies ISO option
		"""
		iso = self.variables['iso'].get()
		if (iso == 'Auto'):
			self.camera.cam_profile.jsonData['iso'] = 0
		else:
			self.camera.cam_profile.jsonData['iso'] = int(iso)
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
		self.notifier.addNotice('ISO: {}'.format(iso))
	def OnEffectRefreshClick(self):
		""" action - Applies effect option
		"""
		self.camera.cam_profile.jsonData['image_effect'] = self.variables['effect'].get()
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
		self.notifier.addNotice('Image Effect: {}'.format(self.camera.cam_profile.jsonData['image_effect']))
	def OnExpModeRefreshClick(self):
		""" action - Applies exposure option
		"""
		self.camera.cam_profile.jsonData['exposure_mode'] = self.variables['expmode'].get()
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
		self.notifier.addNotice('Exposure Mode: {}'.format(self.camera.cam_profile.jsonData['exposure_mode']))
	def OnAwbModeRefreshClick(self):
		""" action - Applies AWB option
		"""
		self.camera.cam_profile.jsonData['awb_mode'] = self.variables['awb'].get()
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.updateCurrentProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
		self.notifier.addNotice('Auto White Balance Mode: {}'.format(self.camera.cam_profile.jsonData['awb_mode']))
	def OnToggleCamLed(self):
		""" action - Toggles camera LED (camera v1 only)
		"""
		if (self.camera.cam_profile.jsonData['led']):
			self.camera.cam_profile.jsonData['led'] = False
		else:
			self.camera.cam_profile.jsonData['led'] = True
		self.variables['camLed'].set(self.camera.cam_profile.jsonData['led'])
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
	def OnToggleFliph(self):
		""" action - Toggles flip horizontal
		"""
		if (self.camera.cam_profile.jsonData['fliph']):
			self.camera.cam_profile.jsonData['fliph'] = False
		else:
			self.camera.cam_profile.jsonData['fliph'] = True
		self.variables['camFlipH'].set(self.camera.cam_profile.jsonData['fliph'])
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
	def OnToggleFlipv(self):
		""" action - Toggles flip vertical
		"""
		if (self.camera.cam_profile.jsonData['flipv']):
			self.camera.cam_profile.jsonData['flipv'] = False
		else:
			self.camera.cam_profile.jsonData['flipv'] = True
		self.variables['camFlipV'].set(self.camera.cam_profile.jsonData['flipv'])
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
	def OnToggleVstab(self):
		""" action - Toggles video stabilization
		"""
		if (self.camera.cam_profile.jsonData['video_stabilization']):
			self.camera.cam_profile.jsonData['video_stabilization'] = False
		else:
			self.camera.cam_profile.jsonData['video_stabilization'] = True
		self.variables['vstab'].set(self.camera.cam_profile.jsonData['video_stabilization'])
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
	def OnSharpnessChange(self, newSharpness):
		""" action - Handles changes with the sharpness slider
		"""
		self.camera.cam_profile.jsonData['sharpness'] = int(newSharpness)
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
	def OnContrastChange(self, newContrast):
		""" action - Handles changes with the contrast slider
		"""
		self.camera.cam_profile.jsonData['contrast'] = int(newContrast)
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
	def OnBrightnessChange(self, newBrightness):
		""" action - Handles changes with the brightness slider
		"""
		self.camera.cam_profile.jsonData['brightness'] = int(newBrightness)
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
	def OnSaturationChange(self, newSaturation):
		""" action - Handles changes with the saturation slider
		"""
		self.camera.cam_profile.jsonData['saturation'] = int(newSaturation)
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
	def OnZoomChange(self, newZoom):
		""" action - Handles changes with the zoom sliders
		"""
		self.camera.cam_profile.jsonData['zoom'] = (float(self.variables['zoomx'].get()), float(self.variables['zoomy'].get()), float(self.variables['zoomw'].get()), float(self.variables['zoomh'].get()))
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
		self.widgets['{}actbutton'.format(Setting.get('cam_default_profile'))].configure(state='normal') #allow original settings to be restored
	def OnAwbRedChange(self, newRed):
		""" action - Handles changes with the awb red slider
		"""
		self.camera.cam_profile.jsonData['awb_gains'] = (float(newRed), self.camera.cam_profile.jsonData['awb_gains'][1])
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()
	def OnAwbBlueChange(self, newBlue):
		""" action - Handles changes with the awb blue slider
		"""
		self.camera.cam_profile.jsonData['awb_gains'] = (self.camera.cam_profile.jsonData['awb_gains'][0], float(newBlue))
		if (self.camera.isPreviewing() and not self.camera.isRecording()):
			self.camera.updateProfile()	
	
	def OnActivateProfileClick(self, index):
		""" action - Loads the settings from a profile
		"""
		cp = Camera.CameraProfile(index)
		if (cp.blobExists()):
			Setting.set('cam_default_profile', index)
			self.camera.initProfile()
		if (self.camera.isPreviewing()):
			self.camera.updateProfile()
		self.updateCurrentProfile()
	def OnSaveProfileClick(self):
		""" action - Displays the save profile view
		"""
		self.saveProfile()
	def OnSaveProfileConfirmClick(self):
		""" action - Saves a profile
		"""
		name = self.variables['name'].get()
		nl = len(name)
		if (nl > 1):
			if (nl < 256):
				profiles = JsonBlob.JsonBlob.all('Camera','CameraProfile')
				exists = False
				for k,v in profiles.items():
					if (v.jsonData['profile_name'] == name):
						exists = True
				if (not exists):
					cp = Camera.CameraProfile()
					cp.jsonData = self.camera.cam_profile.jsonData
					cp.jsonData['profile_name'] = name
					cp.save()
					self.notifier.addNotice('Profile saved (name: {})'.format(name))
					self.OnManageClick()
				else:
					self.notifier.addNotice('A profile with that name already exists','warning')
			else:
				self.notifier.addNotice('Name must be less than 256 characters','warning')
		else:
			self.notifier.addNotice('Name must be 2 characters or longer','warning')
	def OnDeleteProfileClick(self, index):
		""" action - Displays the delete profile view
		"""
		self.deleteProfile(Camera.CameraProfile(index))
	def OnDeleteProfileConfirmClick(self, index):
		""" action - Deletes a camera profile
		"""
		cp = Camera.CameraProfile(index)
		if (cp.blobExists()):
			if (index != Setting.get('cam_default_profile', '')):
				cp.delete()
				self.notifier.addNotice('Profile deleted')
				self.OnManageClick()
			else:
				self.notifier.addNotice('You shouldn\'t delete the active profile','error')
		else:
			self.notifier.addNotice('Profile not found','error')
	def OnCaptureClick(self):
		""" action - Triggers still / video capture
		"""
		if (not self.camera.isRecording()):
			self.camera.capture()
		else:
			self.camera.stopCapture()
		self.updateCapture()
	def OnStreamClick(self):
		""" action - Toggles stream
		"""
		if (not self.camera.isStreaming()):
			self.camera.enableStream()
		else:
			self.camera.disableStream()
		self.updateCapture()
	def updateProfiles(self):
		""" util - Updates the profiles UI
		"""
		self.profiles = JsonBlob.JsonBlob.all('Camera', 'CameraProfile')
		for k,v in self.profiles.items():
			try:
				self.widgets['{}actbutton'.format(k)].configure(state='normal' if k != Setting.get('cam_default_profile', '') else 'disabled')
				self.widgets['{}delbutton'.format(k)].configure(state='normal' if k != Setting.get('cam_default_profile', '') else 'disabled')
			except:
				pass
	def updateCurrentProfile(self):
		""" util - Updates the current profile UI
		"""
		#update viewfinder
		self.widgets['camvf'].configure(width=self.camera.cam_profile.jsonData['viewfinder'][0], height=self.camera.cam_profile.jsonData['viewfinder'][1])
		self.updateCamBg()
		#update vf res
		self.variables['vfres'].set('{}x{}'.format(self.camera.cam_profile.jsonData['viewfinder'][0],self.camera.cam_profile.jsonData['viewfinder'][1]))
		#update rec mode
		recMode = self.camera.cam_profile.getRecMode()
		if (recMode == 'video'):
			self.widgets['recstillbutton'].configure(state='normal')
			self.widgets['recvidbutton'].configure(state='disabled')
		else:
			self.widgets['recstillbutton'].configure(state='disabled')
			self.widgets['recvidbutton'].configure(state='normal')
		self.widgets['recmodeLabel'].configure(text='Video' if recMode == 'video' else 'Photo')
		#update rec res
		resolution = self.camera.cam_profile.getResolution()
		self.variables['rrres'].set('{}x{}'.format(resolution[0],resolution[1]))
		#update rec format
		format = self.camera.cam_profile.getFormat()
		self.variables['format'].set(self.camera.cam_profile.getFormat())
		#update fps
		if (recMode == 'still'):
			self.widgets['fpsentry'].configure(state='disabled')
			self.widgets['fpsrefreshbutton'].configure(state='disabled')
		else:
			self.widgets['fpsentry']['menu'].delete(0, 'end')
			options = self.camera.info['fps_options']['{}x{}'.format(resolution[0],resolution[1])]
			for v in options:
				self.widgets['fpsentry']['menu'].add_command(label=v, command=Tkinter._setit(self.variables['fps'], v))
			if not self.camera.cam_profile.jsonData['fps'] in options:
				self.camera.cam_profile.jsonData['fps'] = options[0]
				self.variables['fps'].set(options[0])
			self.widgets['fpsentry'].configure(state='normal')
			self.widgets['fpsrefreshbutton'].configure(state='normal')
		#update rec led
		self.variables['camLed'].set(self.camera.cam_profile.jsonData['led'])
		#update flip h
		self.variables['camFlipH'].set(self.camera.cam_profile.jsonData['fliph'])
		#update flip v
		self.variables['camFlipV'].set(self.camera.cam_profile.jsonData['flipv'])
		#update video stabilization
		self.variables['vstab'].set(self.camera.cam_profile.jsonData['video_stabilization'])
		#update rotation
		self.variables['rotation'].set(self.camera.cam_profile.jsonData['rotation'])
		#update sharpness
		self.variables['sharpness'].set(self.camera.cam_profile.jsonData['sharpness'])
		#update contrast
		self.variables['contrast'].set(self.camera.cam_profile.jsonData['contrast'])
		#update brightness
		self.variables['brightness'].set(self.camera.cam_profile.jsonData['brightness'])
		#update saturation
		self.variables['saturation'].set(self.camera.cam_profile.jsonData['saturation'])
		#update iso
		if (int(self.camera.cam_profile.jsonData['iso']) == 0):
			self.variables['iso'].set('Auto')
		else:
			self.variables['iso'].set(int(self.camera.cam_profile.jsonData['iso']))
		#update image effect
		self.variables['effect'].set(self.camera.cam_profile.jsonData['image_effect'])
		#update exposure mode
		self.variables['expmode'].set(self.camera.cam_profile.jsonData['exposure_mode'])
		#update awb
		self.variables['awb'].set(self.camera.cam_profile.jsonData['awb_mode'])
		#update awb gains
		self.updateAwbGains()
		#update profiles
		self.updateProfiles()
	def updateAwbGains(self):
		""" util - Updates the Auto White Balance sliders
		"""
		self.variables['awbred'].set(self.camera.cam_profile.jsonData['awb_gains'][0])
		self.variables['awbblue'].set(self.camera.cam_profile.jsonData['awb_gains'][1])
		if (self.camera.cam_profile.jsonData['awb_mode'] == 'off'):
			self.widgets['awbredentry'].configure(state='normal', fg=self.colours['fg'], troughcolor=self.colours['inputbg'])
			self.widgets['awbblueentry'].configure(state='normal', fg=self.colours['fg'], troughcolor=self.colours['inputbg'])
		else:
			self.widgets['awbredentry'].configure(state='disabled', fg=self.colours['bg'], troughcolor=self.colours['bg'])
			self.widgets['awbblueentry'].configure(state='disabled', fg=self.colours['bg'], troughcolor=self.colours['bg'])
	def updateCamBg(self):
		""" util - Updates the viewfinder background
		"""
		self.widgets['cambgimg'] = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'camera','cam-bg-{}.gif'.format(self.camera.cam_profile.jsonData['viewfinder'][0])))
		self.widgets['cambgLabel'].configure(image=self.widgets['cambgimg'])
	def updateCapture(self):
		""" util - Updates the capture UI
		"""
		if ('rec' in self.widgets.keys()):	
			#update capture label
			cap = 'Capture Photo'
			if (self.camera.cam_profile.getRecMode() == 'video'):
				cap = 'Capture Video'
			if (not self.camera.isStreaming() and self.camera.isRecording()):
				cap = 'Capturing'
			self.widgets['recLabel'].configure(text=cap)
			#update capture button
			if (not self.camera.isStreaming() and self.camera.isRecording()):
				if(self.camera.cam_profile.getRecMode() == 'video'):
					self.widgets['rec'].configure(image=self.images['stop'])
					self.widgets['recLabel'].configure(text='Recording ...')
			else:
				self.widgets['rec'].configure(image=self.widgets['recimg'])
				self.widgets['recLabel'].configure(text='Capture {}'.format('Photo' if (self.camera.cam_profile.getRecMode() == 'still') else 'Video'))
			if (not self.camera.isServiceRunning() or self.camera.info['streaming']['enabled']):
				self.widgets['rec'].configure(state='disabled')
			elif (not self.camera.info['streaming']['enabled']):
				self.widgets['rec'].configure(state='normal')
			#update stream button
			if (self.camera.isStreaming()):
				self.widgets['stream'].configure(image=self.images['stop'])
			else:
				self.widgets['stream'].configure(image=self.widgets['streamimg'])
			if (not self.camera.isServiceRunning() or (self.camera.isRecording() and not self.camera.isStreaming())):
				self.widgets['stream'].configure(state='disabled')
			elif (not self.camera.isStreaming() and not self.camera.isRecording()):
				self.widgets['stream'].configure(state='normal')
			#update stream label
			if (not self.camera.info['streaming']['enabled']):
				self.widgets['streamLabel'].configure(text='Start stream')
			elif (self.camera.info['streaming']['enabled'] and not self.camera.info['streaming']['running']):
				self.widgets['streamLabel'].configure(text='Starting stream ...')
			elif (self.camera.info['streaming']['enabled'] and self.camera.info['streaming']['running'] and not self.camera.info['streaming']['connected']):
				self.widgets['streamLabel'].configure(text='Looking for client ...')
			elif (self.camera.info['streaming']['enabled'] and self.camera.info['streaming']['running'] and self.camera.info['streaming']['connected']):
				self.widgets['streamLabel'].configure(text='Stop stream')
			#update tips mode
			if (not self.camera.isServiceRunning() and self.tips['mode'] != 'stopped'):
				self.tips['mode'] = 'stopped'
				self.tips['synced'] = False
			elif (self.camera.isServiceRunning() and self.tips['mode'] == 'stopped'):
				self.tips['mode'] = 'started'
				self.tips['synced'] = False
			if (self.camera.info['streaming']['enabled'] and not self.camera.info['streaming']['running'] and self.tips['mode'] != 'stream_start'):
				self.tips['mode'] = 'stream_start'
				self.tips['synced'] = False
			elif (self.camera.info['streaming']['enabled'] and self.camera.info['streaming']['running'] and not self.camera.info['streaming']['connected'] and self.tips['mode'] != 'stream_connecting'):
				self.tips['mode'] = 'stream_connecting'
				self.tips['synced'] = False
			elif (self.camera.info['streaming']['enabled'] and self.camera.info['streaming']['running'] and self.camera.info['streaming']['connected'] and self.tips['mode'] != 'stream_connected'):
				self.tips['mode'] = 'stream_connected'
				self.tips['synced'] = False
			elif (not self.camera.info['streaming']['enabled'] and not self.camera.info['streaming']['running'] and not self.camera.info['streaming']['connected'] and (self.tips['mode'] == 'stream_connected' or self.tips['mode'] == 'stream_connecting')):
				self.tips['mode'] = 'stream_stop'
				self.tips['synced'] = False
			elif (not self.camera.info['streaming']['enabled'] and not self.camera.info['streaming']['running'] and self.camera.isRecording() and self.tips['mode'] != 'recording'):
				self.tips['mode'] = 'recording'
				self.tips['synced'] = False
			#update tips
			if (not self.tips['synced']):
				self.widgets['tips'].grid_forget()
				del(self.widgets['tips'])
				self.widgets['tips'] = Tkinter.Frame(self.widgets['tipsframe'], bg=self.colours['bg'])
				self.widgets['tips'].grid(column=0,row=1,columnspan=4, sticky='NW')
				if (self.tips['mode'] in self.tips['text'].keys() and any(self.tips['text'][self.tips['mode']])):
					tiprow = 0
					for x in self.tips['text'][self.tips['mode']]:
						tip = Tkinter.Label(self.widgets['tips'],text='- {}'.format(x), anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
						tip.grid(column=0,row=tiprow,sticky='EW')
						tiprow += 1
					if (self.tips['mode'] == 'stream_connecting'):
						urls = self.camera.getStreamUrls()
						if (any(urls)):
							for u in urls:
								tip = Tkinter.Label(self.widgets['tips'],text=u, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
								tip.grid(column=0,row=tiprow,sticky='EW')
								tiprow += 1
					elif (self.tips['mode'] == 'stopped'):
						if (self.camera.kbthread.scheduler.isRunning('kb_watcher')):
							tip = Tkinter.Label(self.widgets['tips'],text='- Shortcut: C = Start / stop camera service', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
							tip.grid(column=0,row=tiprow,sticky='EW')
							tiprow += 1
							tip = Tkinter.Label(self.widgets['tips'],text='- Shortcut: S = Start streaming', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
							tip.grid(column=0,row=tiprow,sticky='EW')
							tiprow += 1
							tip = Tkinter.Label(self.widgets['tips'],text='- Shortcut: Space = Start / stop capture', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
							tip.grid(column=0,row=tiprow,sticky='EW')
							tiprow += 1
						else:
							tip = Tkinter.Label(self.widgets['tips'],text='- Start keyboard service for shortcuts', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
							tip.grid(column=0,row=tiprow,sticky='EW')
							tiprow += 1
				else:
					print('no tips for mode: {}'.format(self.tips['mode']))
				self.tips['synced'] = True
	def updateServiceManager(self):
		""" util - updates the service manager UI
		"""
		if ('status' in self.variables.keys()):
			if ((self.variables['status'].get() == 'Running' and not self.camera.isServiceRunning()) or (self.variables['status'].get() != 'Running' and self.camera.isServiceRunning())):
				#only update when variable doesn't match service state
				if (self.camera.isServiceRunning()):
					self.variables['status'].set('Running')
					self.widgets['start'].configure(state='disabled')
					self.widgets['stop'].configure(state='normal')
				else:
					self.variables['status'].set('Stopped')
					self.widgets['start'].configure(state='normal')
					self.widgets['stop'].configure(state='disabled')
	def close(self):
		""" Override of TkPage.close()
		Hides the viewfinder
		"""
		if (hasattr(self, 'camera') and self.camera.isPreviewing()):
			self.camera.viewfinder['visible'] = False
		super(TkCameraManager,self).close()