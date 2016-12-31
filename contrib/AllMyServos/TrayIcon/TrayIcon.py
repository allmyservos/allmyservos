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
import os, gtk, Scheduler
from __bootstrap import AmsEnvironment

## System tray icon with context menus
class TrayIcon:
	def __init__(self, scheduler = None):
		""" Initializes the TrayIcon object
		"""
		if (scheduler != None):
			self.scheduler = scheduler
		else:
			self.scheduler = Scheduler.Scheduler()
		self.enabled = True
		try:
			icon = gtk.StatusIcon()
		except:
			self.enabled = False
		else:
			self.widgets = {
				'tray': icon
			}
			self.initLeftMenu()
			self.initRightMenu()
			self.widgets['tray'].set_visible(True)
			self.widgets['tray'].set_tooltip_text('AllMyServos')
			self.widgets['tray'].set_from_file(os.path.join(AmsEnvironment.AppPath(), 'images', 'tray-icon', 'tray-icon.png'))
			self.scheduler.addTask('tray_update', self.update, 0.01, False)
	def initLeftMenu(self):
		""" setup left click menu
		"""
		self.widgets['left'] = gtk.Window()
		self.widgets['left'].set_decorated(False)
		self.widgets['left'].set_gravity(gtk.gdk.GRAVITY_NORTH_EAST)
		
		self.widgets['info'] = self.displayAppInfo()
		self.widgets['left'].add(self.widgets['info'])
		
		self.widgets['left'].connect('focus-out-event', self.hideLeftMenu)
		self.widgets['tray'].connect('activate', self.showLeftMenu)
	def initRightMenu(self):
		""" setup right click menu
		"""
		self.widgets['right'] = gtk.Menu()
		i = gtk.MenuItem("About...")
		i.show()
		i.connect("activate", self.showAbout)
		self.widgets['right'].append(i)
		i = gtk.MenuItem("Exit")
		i.show()
		i.connect("activate", self.exit)
		self.widgets['right'].append(i)
		self.widgets['tray'].connect('popup-menu', self.showRightMenu, self.widgets['right'])
	def update(self):
		""" perform gtk iteration
		"""
		if (gtk.events_pending()):
			gtk.main_iteration_do(False)
	def exit(self, widget):
		""" run exit callback
		"""
		if (hasattr(self, 'exitCallback')):
			self.exitCallback()
	def setExitCallback(self, cb):
		""" set the exit callback
		"""
		self.exitCallback = cb
	def showLeftMenu(self, widget):
		""" show left menu
		"""
		if (not self.widgets['left'].get_visible()):
			trayPos = self.widgets['tray'].get_geometry()[1]
			self.widgets['left'].move(trayPos[0],trayPos[1])
			self.widgets['left'].set_skip_taskbar_hint(True)
			self.widgets['left'].set_visible(True)
			self.widgets['left'].present()
		else:
			self.widgets['left'].set_visible(False)
	def hideLeftMenu(self, widget, event):
		""" hide left menu
		"""
		if (self.widgets['left'].get_visible()):
			self.widgets['left'].set_visible(False)
	def showRightMenu(self, widget, event_button, event_time, menu):
		""" show right menu
		auto hides due to popup behaviour
		"""
		self.widgets['right'].popup(None, None,
			gtk.status_icon_position_menu,
			event_button,
			event_time,
			self.widgets['tray']
		)

	def showAbout(self, widget):
		""" show about info
		"""
		dialog = gtk.MessageDialog(
			None,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_INFO,
			gtk.BUTTONS_OK,
			'''
All My Servos - Fun with PWM
Visit:
http://allmyservos.co.uk
''')
		dialog.run()
		dialog.destroy()
	def displayAppInfo(self):
		""" display app information
		
		@return gtk.VBox
		"""
		vbox = gtk.VBox(spacing=3)
		vbox.set_visible(True)
		info = AmsEnvironment.AppInfo()
		
		if (any(info)):
			for k,v in info.items():
				if (isinstance(v, str)):
					p = self.displayPair(k, v)
					vbox.pack_start(p, True, True, 1)
				elif (isinstance(v, list)):
					p = self.displayPair(k, ''.join(v))
					vbox.pack_start(p, True, True, 1)
		else:
			l = gtk.Label()
			l.set_text('App Info Unavailable')
			l.set_visible(True)
			vbox.pack_start(l, True, True, 6)
		
		return vbox
	def displayPair(self, label, value):
		""" display label and value
		
		@return gtk.HBox
		"""
		h = gtk.HBox(spacing=3)
		h.set_visible(True)
		
		l = gtk.Label()
		l.set_markup('<b>{}</b>'.format(str(label)))
		l.set_alignment(xalign=0, yalign=0.5)
		
		l.set_visible(True)
		h.pack_start(l, False, False, 3)
		
		l = gtk.Label()
		l.set_text(value)
		l.set_alignment(xalign=0, yalign=0.5)
		l.set_visible(True)
		h.pack_start(l, False, False, 3)
		return h