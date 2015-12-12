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
import Tkinter
from Tkinter import *
from TkBlock import *
from Motion import *
from TkGraphs import *

class TkServoGrid(TkBlock):
	def __init__(self, parent, gui, **options):
		super(TkServoGrid,self).__init__(parent, gui, **options)
		self.OnShowGridClick()
	def showGrid(self):
		self.open()
		if(any(self.servos)):
			self.gridrow = 0
			for s in self.channelindex:
				self.widgets['servo'+s.jbIndex] = TkServo(self.widget, s, self.colours, self.images)
				self.widgets['servo'+s.jbIndex].widget.grid(column=0,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['emptylabel'] = Tkinter.Label(self.widget,text='No Servos', bg=self.colours['bg'], fg=self.colours['headingfg'], height=3)
			self.widgets['emptylabel'].grid(column=0,row=self.gridrow,sticky='EW')
	def OnShowGridClick(self):
		self.servos = self.gui.specification.servos
		self.channelindex = sorted(self.servos.values(), key=lambda x: x.jsonData['channel'])
		self.showGrid()
		
class TkServo():
	def __init__(self, parent, servo, colours={}, images={}):
		self.widget = Frame(parent)
		self.servo = servo
		self.servo.setCallback(self.update)
		self._angle = Tkinter.IntVar()
		self._angle.set(int(self.servo.angle))
		self._modifier = Tkinter.IntVar()
		self._modifier.set(int(self.servo.modifier))
		self.last = { 'angle': 0, 'modifier': 0 }
		self.initColours(colours)
		self.initImages(images)
		self.setup()
	@property
	def angle(self):
		return self._angle.get()
	@angle.setter
	def angle(self,value):
		value = int(value)
		self.servo.angle = value
		self._angle.set(int(self.servo.angle))
		self.update()
	@property
	def disabled(self):
		return self.servo.disabled
	@disabled.setter
	def disabled(self,value):
		self.servo.disabled = value
	def update(self):
		if(self.last['angle'] != self.servo.angle):
			self.last['angle'] = self.servo.angle
			self._angle.set(int(self.servo.angle))
			self.widgets['graph'].update(int(self.servo.angle))
		if(self.last['modifier'] != self.servo.modifier):
			self.last['modifier'] = self.servo.modifier
			self._modifier.set(int(self.servo.modifier))
	def sync(self):
		self.servo.setServoAngle()
	def save(self):
		self.servo.save()
	def initColours(self, colours):
		try:
			TkServo.colours
		except:
			TkServo.colours = colours
		try:
			self.widget.configure(borderwidth=3, bg = TkServo.colours['bg'])
		except:
			self.widget.configure(borderwidth=3)
	def initImages(self, images):
		try:
			TkServo.images
		except:
			TkServo.images = images
	def setup(self):
		self.widgets = {}
		gridrow = 0
		self.widgets['nameData'] = Tkinter.Label(self.widget,text=self.servo.jsonData['name'], anchor=NW, bg=TkServo.colours['bg'], fg=TkServo.colours['headingfg'], width=15)
		self.widgets['nameData'].grid(column=1,row=gridrow, sticky='EW')

		#self.widgets['graph'] = TkLineGraph(self.widget, { }, {'bg': TkServo.colours['bg'], 'fg': TkServo.colours['fg'], 'line': TkServo.colours['lightfg']}, height = 50, width = 150, yrange = { 'min': 0, 'max': 180})
		self.widgets['graph'] = TkBarGraph(self.widget, TkServo.colours, height = 14, width = 120, grange = { 'min': 0, 'max': 180})
		self.widgets['graph'].widget.grid(column=2,row=gridrow, sticky='EW')
		self.widgets['graph'].update(int(self.servo.angle))
		self.widgets['channelLabel'] = Tkinter.Label(self.widget,text='Ch.', bg=TkServo.colours['bg'], fg=TkServo.colours['fg'])
		self.widgets['channelLabel'].grid(column=3,row=gridrow, padx=10,sticky='EW')
		self.widgets['channelData'] = Tkinter.Label(self.widget,text=int(self.servo.channel), anchor='nw', bg=TkServo.colours['bg'], fg=TkServo.colours['lightfg'], width=3)
		self.widgets['channelData'].grid(column=4,row=gridrow, sticky='EW')
		self.widgets['angleLabel'] = Tkinter.Label(self.widget,text='Angle', bg=TkServo.colours['bg'], fg=TkServo.colours['fg'])
		self.widgets['angleLabel'].grid(column=5,row=gridrow, padx=10, sticky='EW')
		self.widgets['angleData'] = Tkinter.Label(self.widget,textvariable=self._angle, anchor='nw', bg=TkServo.colours['bg'], fg=TkServo.colours['lightfg'], width=3)
		self.widgets['angleData'].grid(column=6,row=gridrow, sticky='EW')
		self.widgets['modifierLabel'] = Tkinter.Label(self.widget,text='Mod.', bg=TkServo.colours['bg'], fg=TkServo.colours['fg'])
		self.widgets['modifierLabel'].grid(column=7,row=gridrow, padx=10, sticky='EW')
		self.widgets['modifierData'] = Tkinter.Label(self.widget,textvariable=self._modifier, anchor='nw', bg=TkServo.colours['bg'], fg=TkServo.colours['lightfg'], width=3)
		self.widgets['modifierData'].grid(column=8,row=gridrow, sticky='EW')
		if(self.servo.jsonData['boneName'] != ''):
			self.widgets['boneLabel'] = Tkinter.Label(self.widget,text='Bone', bg=TkServo.colours['bg'], fg=TkServo.colours['fg'])
			self.widgets['boneLabel'].grid(column=9,row=gridrow, padx=10, sticky='EW')
			self.widgets['boneData'] = Tkinter.Label(self.widget,text=self.servo.jsonData['boneName'], anchor='nw', bg=TkServo.colours['bg'], fg=TkServo.colours['lightfg'])
			self.widgets['boneData'].grid(column=10,row=gridrow, sticky='EW')
			self.widgets['armatureLabel'] = Tkinter.Label(self.widget,text='Armature', bg=TkServo.colours['bg'], fg=TkServo.colours['fg'])
			self.widgets['armatureLabel'].grid(column=11,row=gridrow, padx=10, sticky='EW')
			self.widgets['armatureData'] = Tkinter.Label(self.widget,text=self.servo.jsonData['boneArmature'], anchor='nw', bg=TkServo.colours['bg'], fg=TkServo.colours['lightfg'])
			self.widgets['armatureData'].grid(column=12,row=gridrow, sticky='EW')
			self.widgets['axisLabel'] = Tkinter.Label(self.widget,text='Axis', bg=TkServo.colours['bg'], fg=TkServo.colours['fg'])
			self.widgets['axisLabel'].grid(column=13,row=gridrow, padx=10, sticky='EW')
			self.widgets['axisData'] = Tkinter.Label(self.widget,text=self.servo.jsonData['boneAxis'], anchor='nw', bg=TkServo.colours['bg'], fg=TkServo.colours['lightfg'])
			self.widgets['axisData'].grid(column=14,row=gridrow, sticky='EW')