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
import datetime, Tkinter, JsonBlob, Camera, Timelapse
from __bootstrap import AmsEnvironment
from Tkinter import *
from TkBlock import *

## UI for camera media
class TkTimelapseManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes the TkTimelapseManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkTimelapseManager,self).__init__(parent, gui, **options)
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
		self.timelapse = Timelapse.Timelapse(self.camera)
	def setup(self):
		""" setup gui menu
		"""
		try:
			self.gui.menus['cam']
		except:
			self.gui.menus['cam'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="Camera", menu=self.gui.menus['cam'])
		self.gui.menus['cam'].add_command(label="Timelapse", command=self.OnManageClick)
	#=== VIEWS ===#
	def listProfiles(self):
		""" view - list timelapse profiles
		"""
		self.open()
		
		self.widgets['mainlabel'] = Tkinter.Label(self.widgets['tframe'],text='Camera / Timelapse', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['mainlabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['addprofile'] = Tkinter.Button(self.widgets['tframe'],text=u"Add Profile", image=self.images['add'], command=self.OnAddProfileClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['addprofile'].grid(column=6,row=self.gridrow)
		
		self.gridrow += 1
		
		if (any(self.profiles)):
			
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['modeLabel'] = Tkinter.Label(self.widgets['tframe'],text='Mode', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['modeLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['waitLabel'] = Tkinter.Label(self.widgets['tframe'],text='Interval', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['waitLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['lengthLabel'] = Tkinter.Label(self.widgets['tframe'],text='Length', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['lengthLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.widgets['actLabel'] = Tkinter.Label(self.widgets['tframe'],text='Activate', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['actLabel'].grid(column=4,row=self.gridrow,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['tframe'],text='Edit', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['editLabel'].grid(column=5,row=self.gridrow,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['tframe'],text='Media', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['editLabel'].grid(column=6,row=self.gridrow,sticky='EW')
			
			self.gridrow += 1
			
			rowcolour = self.colours['rowbg']
			rowcount = 1
			for k, v in self.profiles.items():
				rowcolour = self.colours['rowaltbg'] if rowcount % 2 == 0 else self.colours['rowbg']
				rowcount += 1
				self.widgets['nameData{}'.format(k)] = Tkinter.Label(self.widgets['tframe'],text=v.jsonData['name'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['nameData{}'.format(k)].grid(column=0,row=self.gridrow,sticky='EW')
				
				self.widgets['modeData{}'.format(k)] = Tkinter.Label(self.widgets['tframe'],text=v.jsonData['cap_mode'], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['modeData{}'.format(k)].grid(column=1,row=self.gridrow,sticky='EW')
				
				self.widgets['waitData{}'.format(k)] = Tkinter.Label(self.widgets['tframe'],text=v.jsonData['{}_wait'.format(v.jsonData['cap_mode'])], bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['waitData{}'.format(k)].grid(column=2,row=self.gridrow,sticky='EW')
				
				self.widgets['lengthData{}'.format(k)] = Tkinter.Label(self.widgets['tframe'],text=v.jsonData['video_length'] if v.jsonData['cap_mode'] == 'video' else '-', bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['lengthData{}'.format(k)].grid(column=3,row=self.gridrow,sticky='EW')
				
				self.widgets['actButton{}'.format(k)] = Tkinter.Button(self.widgets['tframe'],text=u"Activate", image=self.images['stop'] if v.jsonData['active'] else self.images['play'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnActivateClick(x))
				self.widgets['actButton{}'.format(k)].grid(column=4,row=self.gridrow,sticky='EW')
				
				self.widgets['editButton{}'.format(k)] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnEditProfileClick(x))
				self.widgets['editButton{}'.format(k)].grid(column=5,row=self.gridrow,sticky='EW')
				
				self.widgets['mediaButton{}'.format(k)] = Tkinter.Button(self.widgets['tframe'],text=u"Media", image=self.images['image'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnMediaClick(x))
				self.widgets['mediaButton{}'.format(k)].grid(column=6,row=self.gridrow,sticky='EW')
				
				self.gridrow += 1
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['tframe'],text='There are currently no timelapse profiles', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noLabel'].grid(column=0,row=self.gridrow,sticky='EW')
	def editProfile(self):
		""" view - edit profile
		"""
		self.open()
		
		self.widgets['mainlabel'] = Tkinter.Label(self.widgets['tframe'],text='Camera / Timelapse / Edit', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['mainlabel'].grid(column=0,row=self.gridrow,columnspan=2,pady=10,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['activeLabel'] = Tkinter.Label(self.widgets['tframe'],text='Active', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['activeLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='W')
		
		self.variables['active'] = Tkinter.BooleanVar()
		self.variables['active'].set(self.profile.jsonData['active'])
		self.widgets['activeentry'] = Tkinter.Checkbutton(self.widgets['tframe'], variable=self.variables['active'], text='', anchor=W, command=self.OnToggleActive, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['activeentry'].grid(column=1,row=self.gridrow, padx=5, sticky="W")
		
		self.gridrow += 1
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='W')
		self.variables['name'] = Tkinter.StringVar()
		if(self.profile.jsonData['name'] != ''):
			self.variables['name'].set(self.profile.jsonData['name'])
		self.widgets['nameentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['name'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['nameentry'].grid(column=1,row=self.gridrow,pady=10,sticky='W')
		
		self.gridrow += 1
		
		self.widgets['capLabel'] = Tkinter.Label(self.widgets['tframe'],text='Capture Mode', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['capLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='W')
		
		self.widgets['rmframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['rmframe'].grid(column=1,row=self.gridrow, sticky='W')
		
		self.widgets['stillimg'] = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'camera','still.gif'))
		self.widgets['recstillbutton'] = Tkinter.Button(self.widgets['rmframe'],text=u"Still", image=self.widgets['stillimg'], command=self.OnStillModeClick, bg=self.colours['bg'], activebackground=self.colours['bg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['recstillbutton'].grid(column=0,row=self.gridrow)
		
		self.widgets['videoimg'] = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'camera','video.gif'))
		self.widgets['recvidbutton'] = Tkinter.Button(self.widgets['rmframe'],text=u"Video", image=self.widgets['videoimg'], command=self.OnVideoModeClick, bg=self.colours['bg'], activebackground=self.colours['bg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['recvidbutton'].grid(column=1,row=self.gridrow)
		
		self.widgets['recmodeLabel'] = Tkinter.Label(self.widgets['rmframe'],text='Video' if self.profile.jsonData['cap_mode'] == 'video' else 'Photo', anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['recmodeLabel'].grid(column=2,row=self.gridrow,padx=10, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['waitLabel'] = Tkinter.Label(self.widgets['tframe'],text='Wait', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['waitLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='W')
		
		self.widgets['waitframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['waitframe'].grid(column=1,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['profileLabel'] = Tkinter.Label(self.widgets['tframe'],text='Camera Profile', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['profileLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='W')
		
		self.variables['cam_profile'] = Tkinter.StringVar()
		camProfile = self.profile.getCamProfile() if self.profile.jsonData['cam_profile'] != None else None
		if(camProfile != None):
			self.variables['cam_profile'].set(camProfile.jsonData['profile_name'])
		else:
			self.variables['cam_profile'].set(self.camera.cam_profile.jsonData['profile_name'])
		
		names = Camera.CameraProfile.GetAllNames()
		
		self.widgets['camproentry'] = Tkinter.OptionMenu(self.widgets['tframe'],self.variables['cam_profile'], *names)
		self.widgets['camproentry'].config(bg=self.colours['inputbg'], fg=self.colours['inputfg'], activeforeground=self.colours['activefg'], activebackground=self.colours['activebg'])
		self.widgets['camproentry'].grid(column=1,row=self.gridrow,sticky='W')
		
		self.gridrow += 1
		
		self.updateCapMode()
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.gridrow = 0
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		if(self.profile.blobExists()):
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['deleteLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnManageClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['savepro'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Profile", image=self.images['save'], command=self.OnSaveProfileClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['savepro'].grid(column=1,row=self.gridrow)
		if(self.profile.blobExists()):
			self.widgets['deletepro'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete Profile", image=self.images['delete'], command=self.OnDeleteProfileClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['deletepro'].grid(column=2,row=self.gridrow)
	def stillWaitOptions(self, rootElem):
		""" partial view - adds elements for still options
		
		@param rootElem
		"""
		if ('waitbody' in self.widgets):
			self.widgets['waitbody'].grid_forget()
			del(self.widgets['waitbody'])
			
		self.widgets['waitbody'] = Tkinter.Frame(rootElem, bg=self.colours['bg'])
		self.widgets['waitbody'].grid(column=0,row=0,columnspan=2, sticky='EW')
		
		self.widgets['info1'] = Tkinter.Label(self.widgets['waitbody'],text='Capture an image every ', bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['info1'].grid(column=0,row=0,sticky='EW')
		
		self.variables['still_wait'] = Tkinter.IntVar()
		self.variables['still_wait'].set(self.profile.getWait())
		self.widgets['waitentry'] = Tkinter.Entry(self.widgets['waitbody'], textvariable=self.variables['still_wait'], width=5, bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['waitentry'].grid(column=1,row=0,sticky='EW')
		
		self.widgets['info1'] = Tkinter.Label(self.widgets['waitbody'],text=' seconds', bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['info1'].grid(column=2,row=0,sticky='EW')
	def videoWaitOptions(self, rootElem):
		""" partial view - adds elements for video options
		
		@param rootElem
		"""
		if ('waitbody' in self.widgets):
			self.widgets['waitbody'].grid_forget()
			del(self.widgets['waitbody'])
			
		self.widgets['waitbody'] = Tkinter.Frame(rootElem, bg=self.colours['bg'])
		self.widgets['waitbody'].grid(column=0,row=0,columnspan=2, sticky='EW')
		
		self.widgets['info1'] = Tkinter.Label(self.widgets['waitbody'],text='Capture ', bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['info1'].grid(column=0,row=0,sticky='EW')
		
		self.variables['video_length'] = Tkinter.IntVar()
		self.variables['video_length'].set(self.profile.jsonData['video_length'])
		self.widgets['waitentry'] = Tkinter.Entry(self.widgets['waitbody'], textvariable=self.variables['video_length'], width=5, bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['waitentry'].grid(column=1,row=0,sticky='EW')
		
		self.widgets['info2'] = Tkinter.Label(self.widgets['waitbody'],text=' seconds of footage every ', bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['info2'].grid(column=2,row=0,sticky='EW')
		
		self.variables['video_wait'] = Tkinter.IntVar()
		self.variables['video_wait'].set(self.profile.getWait())
		self.widgets['waitentry'] = Tkinter.Entry(self.widgets['waitbody'], textvariable=self.variables['video_wait'], width=5, bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['waitentry'].grid(column=3,row=0,sticky='EW')
		
		self.widgets['info3'] = Tkinter.Label(self.widgets['waitbody'],text=' seconds', bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
		self.widgets['info3'].grid(column=4,row=0,sticky='EW')
	def listMedia(self):
		""" view - lists media items associated with a timelapse
		"""
		self.open()
		
		self.widgets['mainlabel'] = Tkinter.Label(self.widgets['tframe'],text='Camera / Timelapse / Media', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['mainlabel'].grid(column=0,row=self.gridrow,columnspan=3,sticky='EW')
		
		self.gridrow += 1
		
		if (any(self.profile.jsonData['media'])):
			self.widgets['timeLabel'] = Tkinter.Label(self.widgets['tframe'],text='#', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['timeLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='W')
			self.widgets['timeLabel'] = Tkinter.Label(self.widgets['tframe'],text='Time', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['timeLabel'].grid(column=1,row=self.gridrow,padx=10,sticky='W')
			self.widgets['fileLabel'] = Tkinter.Label(self.widgets['tframe'],text='Filename', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['fileLabel'].grid(column=2,row=self.gridrow,padx=10,sticky='W')
			
			self.gridrow += 1
			
			rowcolour = self.colours['rowbg']
			rowcount = 1
			for x in self.profile.jsonData['media']:
				rowcolour = self.colours['rowaltbg'] if rowcount % 2 == 0 else self.colours['rowbg']
				
				self.widgets['numData{}'.format(x['time'])] = Tkinter.Label(self.widgets['tframe'],text='{}.'.format(rowcount), bg=rowcolour, fg=self.colours['headingfg'], height=2)
				self.widgets['numData{}'.format(x['time'])].grid(column=0,row=self.gridrow,sticky='EW')
				
				self.widgets['timeData{}'.format(x['time'])] = Tkinter.Label(self.widgets['tframe'],text=datetime.datetime.fromtimestamp(float(x['time'])/1000), bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['timeData{}'.format(x['time'])].grid(column=1,row=self.gridrow,sticky='W')
				
				self.widgets['fileData{}'.format(x['time'])] = Tkinter.Label(self.widgets['tframe'],text=x['filename'], bg=rowcolour, fg=self.colours['valuefg'], height=2)
				self.widgets['fileData{}'.format(x['time'])].grid(column=2,row=self.gridrow,sticky='EW')
				
				rowcount += 1
				self.gridrow += 1
			
		else:
			self.widgets['noLabel'] = Tkinter.Label(self.widgets['tframe'],text='This profile has no media', anchor=W, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.gridrow = 0
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['delLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['delLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnManageClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['del'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Delete", image=self.images['delete'], command=self.OnDeleteMediaClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['del'].grid(column=1,row=self.gridrow)
	def deleteMedia(self):
		""" view - delete media
		"""
		self.open()
		
		self.widgets['mainlabel'] = Tkinter.Label(self.widgets['tframe'],text='Camera / Timelapse / Media / Delete', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['mainlabel'].grid(column=0,row=self.gridrow,columnspan=3,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['mLabel'] = Tkinter.Label(self.widgets['tframe'],text='{} item(s)'.format(len(self.profile.jsonData['media'])), bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['mLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='W')
		
		self.gridrow += 1
		
		self.widgets['metaLabel'] = Tkinter.Label(self.widgets['tframe'],text='Clear Meta Data', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['metaLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='W')
		
		self.variables['meta'] = Tkinter.BooleanVar()
		self.variables['meta'].set(True)
		self.widgets['metaentry'] = Tkinter.Checkbutton(self.widgets['tframe'], variable=self.variables['meta'], text='', anchor=W, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['metaentry'].grid(column=1,row=self.gridrow, padx=5, sticky="W")
		
		self.gridrow += 1
		
		self.widgets['mediaLabel'] = Tkinter.Label(self.widgets['tframe'],text='Delete Media Files', bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['mediaLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='W')
		
		self.variables['media'] = Tkinter.BooleanVar()
		self.variables['media'].set(True)
		self.widgets['mediaentry'] = Tkinter.Checkbutton(self.widgets['tframe'], variable=self.variables['media'], text='', anchor=W, command=self.OnToggleDeleteMedia, bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'], disabledforeground=self.colours['greyborder'])
		self.widgets['mediaentry'].grid(column=1,row=self.gridrow, padx=5, sticky="W")
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		self.gridrow = 0
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['delLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['delLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=lambda x = self.profile.jbIndex: self.OnMediaClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['savemap'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save Map", image=self.images['save'], command=self.OnDeleteMediaConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['savemap'].grid(column=1,row=self.gridrow)
	#=== ACTIONS ===#
	def OnManageClick(self):
		""" action - manage timelapse
		"""
		self.profiles = JsonBlob.JsonBlob.all('Timelapse', 'TimelapseProfile')
		self.listProfiles()
	
	def OnAddProfileClick(self):
		""" action - display add profile page
		"""
		self.profile = Timelapse.TimelapseProfile()
		self.editProfile()
	def OnEditProfileClick(self, index):
		""" action - display edit profile page
		
		@param index
		"""
		self.profile = Timelapse.TimelapseProfile(index)
		if (self.profile.blobExists()):
			self.editProfile()
	def OnSaveProfileClick(self):
		""" action - saves a profile
		"""
		if (hasattr(self, 'profile')):
			name = self.variables['name'].get()
			waitError = False
			try:
				wait = int(self.variables['{}_wait'.format(self.profile.jsonData['cap_mode'])].get())
			except:
				wait = 10
				waitError = True
			lengthError = False
			try:
				length = int(self.variables['video_length'].get()) if self.profile.jsonData['cap_mode'] == 'video' else 0
			except:
				length = 1
				lengthError = True
			profile = self.variables['cam_profile'].get()
			if (len(name) < 2):
				self.notifier.addNotice('Name too short','error')
				return
			if (waitError):
				self.notifier.addNotice('Invalid wait value','error')
				return
			if (lengthError):
				self.notifier.addNotice('Invalid length value','error')
				return
			if (not self.profile.blobExists() and name in Timelapse.TimelapseProfile.GetAllNames()):
				self.notifier.addNotice('A timelapse with that name already exists','error')
				return
			elif (self.profile.blobExists() and name != self.profile.jsonData['name'] and name in Timelapse.TimelapseProfile.GetAllNames()):
				self.notifier.addNotice('A timelapse with that name already exists','error')
				return
			if (wait < 1):
				self.notifier.addNotice('Wait time must be at least 1','error')
				return
			if (self.profile.jsonData['cap_mode'] == 'video'):
				if (length < 1):
					self.notifier.addNotice('Footage time must be at least 1','error')
					return
				elif(length > wait -1):
					self.notifier.addNotice('Footage time must be less than wait time','error')
					return
				self.profile.jsonData['video_length'] = length #commit length
			camProfile = [x for x in Camera.CameraProfile.GetAll().values() if x.jsonData['profile_name'] == profile]
			if (not any(camProfile)):
				self.notifier.addNotice('Invalid profile name: {}'.format(profile),'error')
				return
			else:
				self.profile.jsonData['cam_profile'] = camProfile[0].jbIndex
			self.profile.jsonData['name'] = name
			self.profile.jsonData['{}_wait'.format(self.profile.jsonData['cap_mode'])] = wait
			self.profile.save()
			Timelapse.TimelapseProfile.ClearCache()
			self.OnManageClick()
			self.notifier.addNotice('Timelapse profile saved')
	def OnDeleteProfileClick(self):
		""" action - deletes a profile
		"""
		if (hasattr(self, 'profile') and self.profile.blobExists()):
			self.profile.delete()
			Timelapse.TimelapseProfile.ClearCache()
			self.OnManageClick()
	def OnStillModeClick(self):
		""" action - switch to still mode
		"""
		if (hasattr(self, 'profile')):
			self.profile.jsonData['cap_mode'] = 'still'
			self.updateCapMode()
	def OnVideoModeClick(self):
		""" action - switch to video mode
		"""
		if (hasattr(self, 'profile')):
			self.profile.jsonData['cap_mode'] = 'video'
			self.updateCapMode()
	def OnToggleActive(self, index = None):
		""" action - handle active checkbox
		
		@param index
		"""
		if (self.profile.jsonData['active']):
			self.profile.jsonData['active'] = False
		else:
			self.profile.jsonData['active'] = True
	def OnActivateClick(self, index):
		""" action - handle activate button
		
		@param index
		"""
		profile = Timelapse.TimelapseProfile(index)
		if (profile.blobExists()):
			if (profile.jsonData['active']):
				profile.jsonData['active'] = False
			else:
				profile.jsonData['active'] = True
			profile.save()
			self.widgets['actButton{}'.format(index)].configure(image=self.images['stop'] if profile.jsonData['active'] else self.images['play'])
			Timelapse.TimelapseProfile.ClearCache()
	def OnMediaClick(self, index):
		""" action - display media items page
		
		@param index
		"""
		self.profile = Timelapse.TimelapseProfile(index)
		if (self.profile.blobExists()):
			self.listMedia()
	def OnDeleteMediaClick(self):
		""" action - display delete media page
		"""
		self.deleteMedia()
	def OnDeleteMediaConfirmClick(self):
		""" action - delete media items
		"""
		res = {
			'success': 0,
			'missing': 0,
			'meta': False
		}
		if (self.variables['media'].get()):
			for x in self.profile.jsonData['media']:
				path = os.path.join(x['path'], x['filename'])
				if (os.path.exists(path)):
					os.remove(path)
					res['success'] += 1
				else:
					res['missing'] += 1
		if (self.variables['meta'].get()):
			self.profile.jsonData['media'] = []
			self.profile.save()
			res['meta'] = True
		self.notifier.addNotice('{} files deleted, {} missing. Meta data {}'.format(res['success'],res['missing'],'cleared' if res['meta'] else 'preserved'))
		self.OnMediaClick(self.profile.jbIndex)
	def OnToggleDeleteMedia(self):
		""" action - allows media to be preserved but meta data gets wiped
		"""
		if (self.variables['media'].get() and not self.variables['meta'].get()):
			self.variables['meta'].set(True)
			
	def updateCapMode(self):
		""" util - updates the capture mode state
		"""
		capMode = self.profile.jsonData['cap_mode']
		if (capMode == 'still'):
			self.widgets['recstillbutton'].configure(state='disabled')
			self.widgets['recvidbutton'].configure(state='normal')
			self.stillWaitOptions(self.widgets['waitframe'])
		else:
			self.widgets['recstillbutton'].configure(state='normal')
			self.widgets['recvidbutton'].configure(state='disabled')
			self.videoWaitOptions(self.widgets['waitframe'])
		self.widgets['recmodeLabel'].configure(text='Video' if capMode == 'video' else 'Photo')