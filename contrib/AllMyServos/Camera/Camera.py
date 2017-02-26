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
import os, re, time, datetime, socket, errno, Notifier, Keyboard
from __bootstrap import AmsEnvironment
from picamera import PiCamera
from subprocess import Popen, PIPE
from Scheduler import *
from Setting import *
from JsonBlob import *

## Manages interfacing with the pi camera hardware
class Camera(object):
	def __init__(self, scheduler=None, kbthread=None, notifier=None):
		""" Initializes the camera object
		
		@param scheduler
		@param kbthread
		@param notifier
		"""
		self.now = lambda: int(round(time.time() * 1000))
		if(scheduler != None):
			self.scheduler = scheduler
		else:
			self.scheduler = Scheduler.GetInstance()
		self.kbthread = Keyboard.KeyboardThread.GetInstance()
		if(notifier != None):
			self.notifier = notifier
		else:
			self.notifier = Notifier()
		self.viewfinder = {
			'enabled': False,
			'visible': False,
			'window': (0,0,320,240),
			'fullscreen': False,
			'element': None
		}
		self.patterns = {
			'nic': re.compile(r'(?P<name>[^\s]+).?'),
			'addr': re.compile(r'\s*inet\saddr:(?P<ip>[^\s]+).*'),
			'overscan': re.compile(r'[^#]?disable_overscan=(?P<overscan>\d+).*'),
			'overscan_left': re.compile(r'[^#]?overscan_left=(?P<left>\d+)'),
			'overscan_right': re.compile(r'[^#]?overscan_right=(?P<right>\d+)'),
			'overscan_top': re.compile(r'[^#]?overscan_top=(?P<top>\d+)'),
			'overscan_bottom': re.compile(r'[^#]?overscan_bottom=(?P<bottom>\d+)'),
			'start_x': re.compile(r'[^#]?start_x=(?P<start_x>\d+)'),
			'gpu_mem': re.compile(r'[^#]?gpu_mem=(?P<gpu_mem>\d+)'),
		}
		self.initProfile()
		self.initInfo()
		self.initKb()
		self.callbacks = {}
		self.scheduler.addTask('cam_watcher', self.check, interval = 0.5, stopped=not Setting.get('cam_autostart', False))
	def initProfile(self):
		""" Loads the current profile or sets up a default
		"""
		default_profile = Setting.get('cam_default_profile', '')
		if (default_profile == ''):
			self.cam_profile = CameraProfile()
			self.cam_profile.save()
			Setting.set('cam_default_profile', self.cam_profile.jbIndex)
			default_profile = self.cam_profile.jbIndex
		else:
			self.cam_profile = CameraProfile(default_profile)
			if (not self.cam_profile.blobExists()):
				self.cam_profile.save()
	def initInfo(self):
		""" Establishes information for the camera
		"""
		self.info = {
			'cam_start': 0,
			'streaming': {
				'enabled': False,
				'running': False,
				'connected': False
			},
			'revision': 0,
			'max_res': (0,0),
			'max_framerate': 0,
			'still_res_modes': {
				'320x240': (320, 240),
				'640x480': (640, 480),
				'1024x768': (1024, 768),
				'1280x720': (1280, 720),
				'1440x900': (1440, 900),
				'1600x1200': (1600, 1200),
				'1920x1080': (1920, 1080),
				'2048x1536': (2048, 1536),
				'2560x1600': (2560, 1600),
			},
			'video_res_modes': {
				'320x240': (320, 240),
				'640x480': (640, 480),
				'1024x768': (1024, 768),
				'1280x720': (1280, 720),
				'1920x1080': (1920, 1080)
			},
			'fps_options': {
				'320x240': [
					15,
					24,
					30,
					60,
					90,
					120
				],
				'640x480': [
					15,
					24,
					30,
					60,
					90
				],
				'1024x768': [
					15,
					24,
					30,
					60
				],
				'1280x720': [
					15,
					24,
					30
				],
				'1920x1080': [
					15,
					24,
					30
				],
			},
			'exposure_modes': [
				'auto',
				'night',
				'nightpreview',
				'backlight',
				'spotlight',
				'sports',
				'snow',
				'beach',
				'verylong',
				'fixedfps',
				'antishake',
				'fireworks',
			],
			'awb_modes': [
				'off',
				'auto',
				'sunlight',
				'cloudy',
				'shade',
				'tungsten',
				'fluorescent',
				'incandescent',
				'flash',
				'horizon'
			],
			'effects': {},
			'sharpness_range': (-100, 100),
			'contrast_range': (-100, 100),
			'brightness_range': (0, 100),
			'saturation_range': (-100, 100),
			'zoom_range': (0,1),
			'awb_range': (0.0,8.0),
			'iso_range': [
				'Auto',
				'100',
				'200',
				'300',
				'400',
				'500',
				'600',
				'700',
				'800',
			],
			'rotations': [
				0,
				90,
				180,
				270
			],
			'formats': {
				'video': {
					'h264' : 'h264',
					'mjpeg' : 'mjpg'
				},
				'still': {
					'jpeg': 'jpg',
					'png':'png',
					'gif': 'gif',
					'bmp': 'bmp'
				}
			},
			'file_path': os.path.join(AmsEnvironment.FilePath(), 'camera'),
			'overscan': {
				'enabled': False,
				'size': [48,48,48,48]
			},
			'cam_config': {
				'start_x': False,
				'gpu_mem': 0,
				'hardware': False
			}
		}
		camConfig = self.__getCamConfig()
		if ('overscan' in camConfig.keys()):
			self.info['overscan'] = camConfig['overscan']
		if ('cam_config' in camConfig.keys()):
			self.info['cam_config'] = camConfig['cam_config']
		if (self.info['cam_config']['start_x']):
			try:
				if (not hasattr(self,'cam')):
					self.cam = PiCamera()
					self.info['cam_config']['hardware'] = True
			except:
				self.info['cam_config']['hardware'] = False
			if (self.info['cam_config']['hardware']):
				self.info['max_res'] = self.cam.MAX_RESOLUTION if (hasattr(self.cam,'MAX_RESOLUTION')) else (0,0)
				if (self.info['max_res'][0] == 2592):
					self.info['revision'] = 1
				elif(self.info['max_res'][0] == 3280):
					self.info['revision'] = 2
				self.info['max_framerate'] = self.cam.MAX_FRAMERATE if (hasattr(self.cam,'MAX_FRAMERATE')) else 0
				self.info['exposure_modes'] = self.cam.EXPOSURE_MODES if (hasattr(self.cam,'EXPOSURE_MODES')) else {}
				self.info['effects'] = self.cam.IMAGE_EFFECTS if (hasattr(self.cam,'IMAGE_EFFECTS')) else {}
				self.cam.close()
	def initKb(self):
		""" Initializes hex for keyboard events
		"""
		self.kbmap = {
			'0x43': self.toggleService,
			'0x3c': self.setStillMode,
			'0x3e': self.setVideoMode,
			'0x53': self.toggleStream,
			'0x20': self.toggleCapture
		}
		self.kbthread.addCallback('camera', self.camKb)
	def isAvailable(self):
		""" Confirms camera is enabled in raspi-config and the hardware was detected
		"""
		return (self.info['cam_config']['start_x'] and self.info['cam_config']['gpu_mem'] >= 128 and self.info['cam_config']['hardware'])
	def isRunning(self):
		""" True if either prviewing or recording
		
		@return bool
		"""
		return hasattr(self,'cam') and (self.cam.previewing or self.cam.recording)
	def isPreviewing(self):
		""" True if previewing
		
		@return bool
		"""
		return hasattr(self,'cam') and self.cam.previewing
	def isRecording(self):
		""" True if recording
		
		@return bool
		"""
		return hasattr(self,'cam') and self.cam.recording
	def isStreaming(self):
		""" True if streaming
		
		@return bool
		"""
		return self.info['streaming']['running']
	def isServiceRunning(self):
		""" True if camera service is running
		
		@return bool
		"""
		return self.scheduler.isRunning('cam_watcher')
	def start(self):
		""" Starts the camera service
		"""
		if (not self.isServiceRunning()):
			self.scheduler.startTask('cam_watcher')
			self.notifier.addNotice('Camera service started')
	def stop(self):
		""" Stops the camera service
		"""
		if (self.isServiceRunning()):
			self.scheduler.stopTask('cam_watcher')
			self.stopStream()
			self.check()
			self.notifier.addNotice('Camera service stopped')
	def toggleService(self):
		""" Toggle service
		Used for the keyboard so one key can start and stop service
		"""
		if (self.isServiceRunning()):
			self.stop()
		else:
			self.start()
	def setStillMode(self):
		""" Activates still capture mode
		"""
		self.cam_profile.jsonData['rec_mode'] = 'still'
		self.check()
	def setVideoMode(self):
		""" Activates video capture mode
		"""
		self.cam_profile.jsonData['rec_mode'] = 'video'
		self.check()
	def startCam(self, profile = None):
		""" Starts the camera hardware
		"""
		if (profile == None):
			if (hasattr(self, 'timelapse')):
				profile = self.timelapse.getCamProfile() #take timelapse profile
			if (profile == None):
				profile = self.cam_profile #take default profile
		if (hasattr(self,'cam_profile')):
			self.cam = PiCamera(resolution=profile.getResolution(), framerate=profile.jsonData['fps'])
		else:
			self.cam = PiCamera()
		self.updateProfile(profile)
		self.info['cam_start'] = self.now()
	def stopCam(self):
		""" Stops the camera hardware
		"""
		if (not self.cam.closed):
			self.cam.close()
			self.info['cam_start'] = 0
	def stopPreview(self):
		""" Stops the camera preview
		"""
		if (self.isPreviewing()):
			self.cam.stop_preview()
	def updateProfile(self, profile = None):
		""" Applies camera profile settings
		"""
		if (profile == None):
			profile = self.cam_profile.jsonData
		else:
			profile = profile.jsonData
		if (hasattr(self, 'cam') and profile != None):
			self.cam.led = profile['led']
			self.cam.hflip = profile['fliph']
			self.cam.vflip = profile['flipv']
			self.cam.sharpness = int(profile['sharpness'])
			self.cam.contrast = int(profile['contrast'])
			self.cam.brightness = int(profile['brightness'])
			self.cam.saturation = int(profile['saturation'])
			self.cam.iso = int(profile['iso'])
			self.cam.rotation = int(profile['rotation'])
			self.cam.image_effect = profile['image_effect']
			self.cam.exposure_mode = profile['exposure_mode']
			self.cam.awb_mode = profile['awb_mode']
			self.cam.awb_gains = (float(profile['awb_gains'][0]),float(profile['awb_gains'][1]))
			self.cam.video_stabilization = profile['video_stabilization']
			self.cam.zoom = profile['zoom']
	def toggleCapture(self):
		""" Captures a still or starts / stops video recording
		"""
		if (self.isServiceRunning()):
			if (self.cam_profile.getRecMode() == 'video'):
				if (not self.isRecording()):
					self.capture()
				else:
					self.stopCapture()
			else:
				self.capture()
	def capture(self, profile = None):
		""" Captures still / video based on the provided profile (or camera default)
		
		@param profile
		
		@return dict
		"""
		res = {
			'captured': False,
			'rec_mode': 'still',
			'path': '',
			'filename': ''
		}
		if(not self.cam.closed):
			if(profile == None):
				profile = self.cam_profile
			recmode = profile.getRecMode()
			currentPath = os.path.join(self.info['file_path'], recmode)
			currentPath = '{}/{}'.format(currentPath, datetime.date.today())
			if (not os.path.exists(currentPath)):
				os.makedirs(currentPath) #setup directories
			res['rec_mode'] = recmode
			res['path'] = currentPath
			res['filename'] = filename = '{}-{}.{}'.format('Image' if recmode == 'still' else 'Clip', self.now(), self.info['formats'][recmode][profile.getFormat()])
			if (recmode == 'still'):
				self.cam.capture(os.path.join(currentPath,filename))
				res['captured'] = True
			else:
				self.cam.start_recording(os.path.join(currentPath,filename))
				res['captured'] = True
		return res
	def stopCapture(self, profile = None):
		""" Stops video capture
		"""
		if(profile == None):
			profile = self.cam_profile
		if (profile.getRecMode() == 'video' and self.isRecording()):
			self.cam.stop_recording()
			return True
		return False
	def enableStream(self):
		""" Enables streaming
		"""
		self.info['streaming']['enabled'] = True
		self.notifier.addNotice('Stream enabled')
	def disableStream(self):
		""" Disables streaming
		"""
		self.info['streaming']['enabled'] = False
		self.notifier.addNotice('Stream disabled')
	def toggleStream(self):
		""" Enables / disables streaming
		"""
		if (not self.isRecording()):
			if(not self.isStreaming()):
				self.enableStream()
			else:
				self.disableStream()
	def startStream(self):
		""" Starts the stream
		"""
		self.info['streaming']['running'] = True
		self.server_socket = socket.socket()
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.settimeout(0.8)
		self.server_socket.bind(('0.0.0.0', 8000))
		self.server_socket.listen(0)
	def openStream(self):
		""" Attempts to open stream connection
		"""
		try:
			attempt = self.server_socket.accept()
			self.connection = attempt[0].makefile('wb')
			self.cam.start_recording(self.connection, format='h264')
			self.info['streaming']['connected'] = True
			self.notifier.addNotice('Stream connection established')
		except:
			self.info['streaming']['connected'] = False
	def stopStream(self):
		""" Stops the stream
		"""
		if (self.isStreaming()):
			try:
				self.cam.stop_recording() #stop recording trows an error if stream is stopped remotely
			except:
				pass
			try:
				if (hasattr(self, 'connection')):
					self.connection.close()
			except socket.error, e:
				if isinstance(e.args, tuple):
					if e[0] == errno.EPIPE:
						#could use notifier here to state connection was remotely closed
						pass
			self.server_socket.close()
			self.info['streaming']['enabled'] = False
			self.info['streaming']['running'] = False
			self.info['streaming']['connected'] = False
	def enableViewfinder(self, window=(0,0,320,240), fullscreen=False, element=None):
		""" Enables preview viewfinder (GUI only)
		"""
		self.viewfinder = {
			'enabled': True,
			'visible': True,
			'window': window,
			'fullscreen': fullscreen,
			'element': element
		}
	def disableViewfinder(self):
		""" Disables the viewfinder
		"""
		self.viewfinder['enabled'] = False
		self.viewfinder['visible'] = False
	def getStreamUrls(self):
		""" Lists available URLs
		
		@return list
		"""
		urls = []
		for n in self.__getNics():
			if (len(n['ip']) > 2):
				urls.append('tcp/h264://{}:{}/'.format(n['ip'],8000))
		return urls
	def camKb(self, hex = None, ascii = None):
		""" Callback for KbThread
		"""
		if (hasattr(self, 'kbmap') and any(self.kbmap)):
			for k, v in self.kbmap.items():
				if (k == hex):
					v()
					break
	def __ifconfig(self):
		""" Gets the result of ifconfig
		
		@return string
		"""
		p = Popen('ifconfig', stdout=PIPE)
		o = p.communicate()[0]
		if(p.returncode == 0):
			return o
		return ''
	def __getNics(self):
		""" Gets a list of network interfaces
		
		@return list
		"""
		nics = []
		for l in self.__ifconfig().split('\n'):
			match = self.patterns['nic'].match(l)
			if(match):
				nics.append({'name': match.group('name'), 'ip': ''})
			match = self.patterns['addr'].match(l)
			if(match):
				nics[-1]['ip'] = match.group('ip')
		return nics
	def __getCamConfig(self):
		""" Queries raspi-config
		
		@return dict
		"""
		res = {
			'overscan': {
				'enabled': False,
				'size': [48,48,48,48]
			},
			'cam_config': {
				'start_x': False,
				'gpu_mem': 0,
				'hardware': False
			}
		}
		f = open('/boot/config.txt', 'r')
		for l in f:
			match = self.patterns['overscan'].match(l)
			if (match):
				try:
					res['overscan']['enabled'] = True if match.group('overscan') == '0' else False
				except:
					pass
			match = self.patterns['overscan_left'].match(l)
			if (match):
				try:
					res['overscan']['size'][0] = int(match.group('left'))
				except:
					pass
			match = self.patterns['overscan_right'].match(l)
			if (match):
				try:
					res['overscan']['size'][1] = int(match.group('right'))
				except:
					pass
			match = self.patterns['overscan_top'].match(l)
			if (match):
				try:
					res['overscan']['size'][2] = int(match.group('top'))
				except:
					pass
			match = self.patterns['overscan_bottom'].match(l)
			if (match):
				try:
					res['overscan']['size'][3] = int(match.group('bottom'))
				except:
					pass
			match = self.patterns['start_x'].match(l)
			if (match):
				if (int(match.group('start_x')) == 1):
					res['cam_config']['start_x'] = True
			match = self.patterns['gpu_mem'].match(l)
			if (match):
				res['cam_config']['gpu_mem'] = int(match.group('gpu_mem'))
		f.close()
		return res
	def check(self):
		""" Updates the camera state
			cam_watcher task can run without starting the camera hardware.
			allows the task to start and stop the camera as needed to save power during long running tasks like timelapse.
		"""
		if (self.isServiceRunning() and ((self.viewfinder['enabled'] and self.viewfinder['visible']) or self.info['streaming']['enabled']) and (not hasattr(self, 'cam') or self.cam.closed)):
			self.startCam() #preview needed so start it

		if (self.isServiceRunning() and self.viewfinder['enabled'] and self.viewfinder['visible'] and not self.cam.previewing):
			vfwindow = self.viewfinder['window'] #default window
			if (self.viewfinder['element'] != None):
				#update window
				winx = self.viewfinder['element'].winfo_rootx()
				winy = self.viewfinder['element'].winfo_rooty()
				if (self.info['overscan']['enabled']):
					winx += self.info['overscan']['size'][0]
					winy += self.info['overscan']['size'][2]
				vfwindow = (winx,winy,self.viewfinder['element'].winfo_reqwidth(),self.viewfinder['element'].winfo_reqheight())
			self.cam.start_preview(window=vfwindow, fullscreen=self.viewfinder['fullscreen']) #start preview
		elif(hasattr(self, 'cam') and self.cam.previewing and (not self.viewfinder['visible'] or not self.isServiceRunning())):
			self.stopPreview() #stop preview
		
		if (self.isServiceRunning() and self.info['streaming']['enabled'] and not self.info['streaming']['running']):
			self.startStream()
		elif (self.isServiceRunning() and self.info['streaming']['enabled'] and self.info['streaming']['running'] and not self.info['streaming']['connected']):
			self.openStream()
		elif (self.info['streaming']['enabled'] == False and self.info['streaming']['running'] == True):
			self.stopStream()
		
		if (not self.isServiceRunning() and not self.isPreviewing() and not self.cam.closed):
			self.stopCam() #stop the camera
		
		self.doCallbacks()
	def addCallback(self, name, callback):
		""" Allows other modules to plug-in the camera schedule
		"""
		self.callbacks[name] = callback
	def removeCallback(self, name):
		""" Removes a plug-in from the camera schedule
		"""
		try:
			del(self.callbacks[name])
		except:
			pass
	def doCallbacks(self):
		""" Performs callbacks
		"""
		if(any(self.callbacks)):
			for x in self.callbacks.values():
				x()
	def listDir(self, path = None):
		""" Lists camera media directory info
		
		@param path list of sub directories
		
		@return dict
		"""
		res = {
			'base': self.info['file_path'],
			'path': path,
			'exists': False,
			'items': []
		}
		currentDir = os.path.join(self.info['file_path'], *path) if (path != None and any(path)) else self.info['file_path']
		res['exists'] = os.path.exists(currentDir)
		if (res['exists']):
			files = os.listdir(currentDir)
			for item in files:
				itemPath = os.path.join(currentDir, item)
				isDir = os.path.isdir(itemPath)
				filetype = 'dir'
				ext = None
				if (not isDir):
					filetype = 'file'
					ext = os.path.splitext(item)[1][1:]
					if (any([x for x in self.info['formats']['video'].values() if x == ext])):
						filetype = 'video'
					elif (any([x for x in self.info['formats']['still'].values() if x == ext])):
						filetype = 'still'
				res['items'].append({
					'filename': item,
					'is_dir': isDir,
					'modified': datetime.datetime.fromtimestamp(os.path.getmtime(itemPath)),
					'extension': ext,
					'file_type': filetype
				})
		return res
## Camera settings are grouped into camera profiles which can be saved and reused
class CameraProfile(JsonBlob):
	@staticmethod
	def GetAll():
		""" Gets all CameraProfile blobs
		
		@return dict of CameraProfile objects
		"""
		return JsonBlob.all('Camera', 'CameraProfile')
	@staticmethod
	def GetAllNames():
		""" Gets a list of all used names
		
		@return list of CameraProfile names
		"""
		return [x.jsonData['profile_name'] for x in CameraProfile.GetAll().values()]
	def __init__(self, index = None):
		""" Initializes the CameraProfile object
		
		@param index jbIndex / a new index or None
		"""
		super(CameraProfile,self).__init__(index)
		if (not self.blobExists()):
			self.jsonData = {
				'profile_name': 'Default',
				'viewfinder': (320, 240),
				'rec_modes': ('still','video'),
				'rec_mode': 'still',
				'still_res': (320, 240),
				'video_res': (320, 240),
				'fps': 30,
				'still_format': 'jpeg',
				'video_format': 'h264',
				'led': True,
				'sharpness': 0,
				'contrast': 0,
				'brightness': 50,
				'saturation': 0,
				'iso': 0,
				'video_stabilization': False,
				'exposure_compensation': 0,
				'exposure_mode': 'auto',
				'meter_mode': 'average',
				'awb_mode': 'auto',
				'awb_gains': (0.0,0.0),
				'image_effect': 'none',
				'color_effects': None,
				'rotation': 0,
				'zoom': (0.0, 0.0, 1.0, 1.0),
				'fliph': False,
				'flipv': False
			}
	def getResolution(self):
		""" Gets the current camera resolution based on the current mode
		"""
		return self.jsonData['still_res'] if (self.jsonData['rec_mode'] == 'still') else self.jsonData['video_res']
	def getFormat(self):
		""" Gets the current file format for capture
		"""
		return self.jsonData['still_format'] if (self.jsonData['rec_mode'] == 'still') else self.jsonData['video_format']
	def getRecMode(self):
		""" Gets the current capture mode
		"""
		return self.jsonData['rec_mode']