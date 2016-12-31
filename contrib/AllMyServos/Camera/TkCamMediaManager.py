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
from subprocess import Popen, PIPE

## UI for camera media
class TkCamMediaManager(TkPage):
	def __init__(self, parent, gui, **options):
		""" Initializes the TkCamMediaManager object
		
		@param parent
		@param gui
		@param options
		"""
		super(TkCamMediaManager,self).__init__(parent, gui, **options)
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
	def setup(self):
		""" setup gui menu
		"""
		try:
			self.gui.menus['cam']
		except:
			self.gui.menus['cam'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="Camera", menu=self.gui.menus['cam'])
		self.gui.menus['cam'].add_command(label="Media", command=self.OnMediaClick)
	def initIcons(self):
		""" Loads required icon images
		"""
		try:
			self.icons
		except:
			self.icons = {}
			self.icons['folderimg'] = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'camera','folder.gif'))
			self.icons['stillimg'] = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'camera','still.gif'))
			self.icons['videoimg'] = Tkinter.PhotoImage(file = os.path.join(AmsEnvironment.AppPath(), 'images', 'camera','video.gif'))
	#=== VIEWS ===#
	def media(self):
		""" view - displays the media browser
		"""
		self.open()
		
		self.initIcons()
		
		self.widgets['mainlabel'] = Tkinter.Label(self.widgets['tframe'],text='Camera / Camera Manager / Media', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['mainlabel'].grid(column=0,row=self.gridrow,sticky='W')
		
		self.gridrow += 1
		
		self.widgets['dirframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['dirframe'].grid(column=0,row=self.gridrow, pady=10, sticky='W')
		
		self.widgets['dirlabel'] = Tkinter.Label(self.widgets['dirframe'],text='Directory', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['dirlabel'].grid(column=0,row=0,sticky='W')
		
		self.widgets['dirvalue'] = Tkinter.Label(self.widgets['dirframe'],text=os.path.join(self.camera.info['file_path'], *self.basepath), anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['dirvalue'].grid(column=1,row=0,padx=10,sticky='W')
		
		if (any(self.basepath)):
			self.widgets['parentdir'] = Tkinter.Button(self.widgets['dirframe'],text=u"Back", image=self.images['back'], command=self.OnParentClick, bg=self.colours['bg'], activebackground=self.colours['bg'], highlightbackground=self.colours['buttonborder'])
			self.widgets['parentdir'].grid(column=2,row=0,sticky='EW')
		
		self.widgets['opendir'] = Tkinter.Button(self.widgets['dirframe'],text=u"Open", image=self.images['find'], command=lambda x = None:self.OnOpenFileClick(x), bg=self.colours['bg'], activebackground=self.colours['bg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['opendir'].grid(column=3,row=0,sticky='EW')
		
		self.gridrow += 1
		
		contents = self.camera.listDir(self.basepath)
		
		self.widgets['fileframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['fileframe'].grid(column=0,row=self.gridrow, pady=10, sticky='W')
		if (any(contents['items'])):
			col = 0
			row = 0
			for item in contents['items']:
				if (item['is_dir']):
					self.widgets['dir-{}'.format(item['filename'])] = self.displayDir(self.widgets['fileframe'], item)
					self.widgets['dir-{}'.format(item['filename'])].grid(column=col,row=row,sticky='EW')
				else:
					self.widgets['file-{}'.format(item['filename'])] = self.displayFile(self.widgets['fileframe'], item)
					self.widgets['file-{}'.format(item['filename'])].grid(column=col,row=row,sticky='EW')
				if (col < 2):
					col += 1
				else:
					col = 0
					row += 1
		else:
			self.widgets['nolabel'] = Tkinter.Label(self.widgets['fileframe'],text='Empty directory', anchor=NW, bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nolabel'].grid(column=0,row=0,sticky='EW')
	def displayDir(self, rootElem, item):
		""" partial view - returns a directory rendered for TkInter
		
		@param rootElem
		@param item
		
		@return Frame
		"""
		widget = Tkinter.Frame(rootElem, bg=self.colours['bg'], borderwidth=1, highlightthickness=1)
		
		self.widgets['icon'] = Tkinter.Button(widget,text=u"Open", image=self.icons['folderimg'], command=lambda x = item['filename']:self.OnOpenDirClick(x), bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['icon'].grid(column=0,row=0,rowspan=2,sticky='EW')
		
		self.widgets['label'] = Tkinter.Label(widget,text='Name', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['label'].grid(column=1,row=0,sticky='EW')
		
		self.widgets['value'] = Tkinter.Label(widget,text=item['filename'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['value'].grid(column=2,row=0,sticky='EW')
		
		self.widgets['label'] = Tkinter.Label(widget,text='Modified', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['label'].grid(column=1,row=1,sticky='EW')
		
		self.widgets['value'] = Tkinter.Label(widget,text=item['modified'].strftime('%D %T'), anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['value'].grid(column=2,row=1,sticky='EW')
		
		return widget
	def displayFile(self, rootElem, item):
		""" partial view - returns a file rendered for TkInter
		@param rootElem
		@param item
		
		@return Frame
		"""
		widget = Tkinter.Frame(rootElem, bg=self.colours['bg'], borderwidth=1, highlightthickness=1)
		
		self.widgets['icon'] = Tkinter.Button(widget,text=u"Open", image=self.icons['stillimg'], command=lambda x = item['filename']:self.OnOpenFileClick(x), bg=self.colours['bg'], activebackground=self.colours['bg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['icon'].grid(column=0,row=0,rowspan=2,sticky='EW')
		if(item['file_type'] == 'video'):
			self.widgets['icon'].configure(image=self.icons['videoimg'])
		
		self.widgets['label'] = Tkinter.Label(widget,text='Name', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['label'].grid(column=1,row=0,sticky='EW')
		
		self.widgets['value'] = Tkinter.Label(widget,text=item['filename'], anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['value'].grid(column=2,row=0,sticky='EW')
		
		self.widgets['label'] = Tkinter.Label(widget,text='Modified', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'])
		self.widgets['label'].grid(column=1,row=1,sticky='EW')
		
		self.widgets['value'] = Tkinter.Label(widget,text=item['modified'].strftime('%D %T'), anchor=NW, bg=self.colours['bg'], fg=self.colours['valuefg'])
		self.widgets['value'].grid(column=2,row=1,sticky='EW')
		
		return widget
	#=== ACTIONS ===#
	def OnMediaClick(self):
		""" action - display the media viewer
		"""
		self.basepath = []
		self.media()
	def OnOpenDirClick(self, filename):
		""" action - move to given directory
		
		@param filename
		"""
		self.basepath.append(filename)
		self.media()
	def OnParentClick(self):
		""" action - move to the parent directory
		"""
		if (any(self.basepath)):
			self.basepath.pop()
			self.media()
		else:
			self.notifier.addNotice('Unable to go above media directory','warning')
	def OnOpenFileClick(self, filename):
		""" action - open the supplied file
		
		@param filename
		"""
		#open file manager
		if (filename != None):
			self.basepath.append(filename) #append filename
		res = self.__openFileManager(os.path.join(self.camera.info['file_path'], *self.basepath))
		if (filename != None):
			self.basepath.pop() #remove filename
	#=== UTILS ===#
	def __openFileManager(self, dir=''):
		""" util - open the pi file manager to the given directory
		
		@param dir str containing a path
		"""
		try:
			if(len(dir) > 0):
				command = ['pcmanfm', dir]
				p = Popen(command, stdout=PIPE)
				o = p.communicate()[0]
				if(p.returncode == 0):
					return True
		except:
			pass
		return False