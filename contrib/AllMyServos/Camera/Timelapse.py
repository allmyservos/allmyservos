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
import time, datetime, Camera
from JsonBlob import *

## Manages timelapse events, driven by the camera service
class Timelapse(object):
	def __init__(self, camera=None):
		""" Initializes the Timelapse object
		
		@param camera
		"""
		self.now = lambda: int(round(time.time() * 1000))
		if(camera != None):
			self.camera = camera
		else:
			self.camera = Camera.Camera()
		self.camera.timelapse = self
		self.camera.addCallback('update_timelapse', self.update)
	def update(self):
		""" Updates the camera based on the timelapse profile (if any)
		"""
		active = TimelapseProfile.GetAllActive()
		if (any(active)):
			for x in active:
				camProfile = x.getCamProfile()
				#is it due?
				if (self.camera.info['cam_start'] == 0 and x.jsonData['last_checked'] < self.now() - (2000 + x.getWait()*1000)):	
					#it's boot time
					self.camera.startCam(camProfile)
				elif (self.camera.info['cam_start'] > 0 and x.jsonData['last_checked'] < self.now() - x.getWait()*1000 and self.camera.info['cam_start'] <= self.now()-2000):
					#it's capture time
					x.jsonData['last_checked'] = self.now()
					if (self.camera.isRecording()):
						x.jsonData['fails'].append({
							'time': x.jsonData['last_checked'],
							'reason': 'occupied'
						})
					else:
						cap = self.camera.capture(camProfile)
						if (not cap['captured']):
							x.jsonData['fails'].append({
								'time': x.jsonData['last_checked'],
								'reason': 'capture'
							})
						else:
							if (x.jsonData['cap_mode'] == 'video'):
								x.jsonData['capturing'] = True
							x.jsonData['media'].append({
								'time': x.jsonData['last_checked'],
								'filename': cap['filename'],
								'path': cap['path']
							})
					if (len(x.jsonData['fails']) > 1000):
						x.jsonData['fails'] = x.jsonData['fails'][1:] #limit length of fails
					x.save()
				elif (self.camera.isRecording() and x.jsonData['cap_mode'] == 'video' and x.jsonData['capturing'] and x.jsonData['last_checked'] <= self.now() - x.jsonData['video_length']*1000):
					self.camera.stopCapture(camProfile)
					x.jsonData['capturing'] = False
					x.save()
	def getCamProfile(self):
		""" Gets the camera profile from the active timelapse profile
		
		@return CameraProfile or None
		"""
		active = TimelapseProfile.GetAllActive()
		if (any(active)):
			for x in active:
				return x.getCamProfile()
		return None
## Timelapse settings are collected into a timelapse profile which can be saved an recalled
class TimelapseProfile(JsonBlob):
	@staticmethod
	def GetAll():
		""" Gets all TimelapseProfile objects
		
		@return dict of TimelapseProfile objects
		"""
		return JsonBlob.all('Timelapse', 'TimelapseProfile')
	@staticmethod
	def GetAllNames():
		""" Gets all names
		
		@return list of str
		"""
		return [x.jsonData['name'] for x in TimelapseProfile.GetAll().values()]
	@staticmethod
	def GetAllActive():
		""" Gets all active TimelapseProfiles
		
		@return list
		"""
		try:
			TimelapseProfile.cache
		except:
			TimelapseProfile.cache = [x for x in TimelapseProfile.GetAll().values() if x.jsonData['active']]
		return TimelapseProfile.cache
	@staticmethod
	def ClearCache():
		""" Clears the cache - useful when timelapse profiles are changed or removed
		"""
		try:
			del(TimelapseProfile.cache)
		except:
			pass
	def __init__(self, index = None):
		""" Initializes the TimelapseProfile object
		"""
		super(TimelapseProfile,self).__init__(index)
		if (not self.blobExists()):
			self.jsonData = {
				'active': False,
				'capturing': False,
				'name': 'Default',
				'last_checked': 0,
				'last_capture': 0,
				'cap_mode': 'still',
				'still_wait': 60,
				'video_wait': 60,
				'video_length': 10,
				'cam_profile': None,
				'media_limit_meta': 1000,
				'media_limit_files': 1000,
				'media': [],
				'fails': [],
			}
	def getWait(self):
		""" Gets the specified wait for this timelapse
		
		@return int
		"""
		return self.jsonData['{}_wait'.format(self.jsonData['cap_mode'])]
	def getCamProfile(self):
		""" Gets the camera profile for this timelapse
		
		@return CameraProfile or None
		"""
		if (self.jsonData['cam_profile'] != None):
			camProfile = Camera.CameraProfile(self.jsonData['cam_profile'])
			camProfile.jsonData['rec_mode'] = self.jsonData['cap_mode']
			return camProfile
		return None