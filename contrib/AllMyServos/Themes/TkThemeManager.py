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
import Tkinter, tkColorChooser, os, shutil, sys
from Tkinter import *
from TkBlock import *
from tkFileDialog import askopenfilename
from Theme import *
from Setting import *

class TkThemeManager(TkPage):
	def __init__(self, parent, gui, **options):
		super(TkThemeManager,self).__init__(parent, gui, **options)
	def setup(self):
		try:
			self.gui.menus['settings']
		except:
			self.gui.menus['settings'] = Tkinter.Menu(self.gui.menubar, tearoff=0, bg=self.colours['menubg'], fg=self.colours['menufg'], activeforeground=self.colours['menuactivefg'], activebackground=self.colours['menuactivebg'])
			self.addMenu(label="Settings", menu=self.gui.menus['settings'])
		self.gui.menus['settings'].insert_command(label="Themes", index=0, command=self.OnListThemesClick)
	#=== VIEWS ===#
	##== Theme ==##
	def listThemes(self):
		self.open()
		self.themes = Theme()
		self.themes = self.themes.query()
		
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings / Themes ', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		
		if(len(self.themes) > 0):
			self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['editLabel'] = Tkinter.Label(self.widgets['tframe'],text='Edit', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['editLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['activateLabel'] = Tkinter.Label(self.widgets['tframe'],text='Activate', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['activateLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['deleteLabel'] = Tkinter.Label(self.widgets['tframe'],text='Delete', bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['deleteLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			rowcount = 1
			for t in self.themes:
				rowcolour = self.colours['rowbg']
				if(rowcount % 2 == 0):
					rowcolour = self.colours['rowaltbg']
				rowcount += 1
				self.widgets['name'+self.themes[t].name] = Tkinter.Label(self.widgets['tframe'],text=self.themes[t].name, bg=rowcolour, fg=self.colours['fg'], height=2)
				self.widgets['name'+self.themes[t].name].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['edit'+self.themes[t].name] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = self.themes[t].name:self.OnEditThemeClick(x))
				self.widgets['edit'+self.themes[t].name].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['activate'+self.themes[t].name] = Tkinter.Button(self.widgets['tframe'],text=u"Activate", image=self.images['play'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = self.themes[t].name:self.OnActivateThemeClick(x))
				self.widgets['activate'+self.themes[t].name].grid(column=2,row=self.gridrow,sticky='EW')
				
				if(Setting.get('gui_theme_name','DarkBlue') == self.themes[t].name):
					self.widgets['activate'+self.themes[t].name].configure(state='disabled')
				else:
					self.widgets['activate'+self.themes[t].name].configure(state='normal')
				self.widgets['delete'+self.themes[t].name] = Tkinter.Button(self.widgets['tframe'],text=u"Delete", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = self.themes[t].name:self.OnDeleteClick(x))
				self.widgets['delete'+self.themes[t].name].grid(column=3,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['nothemeslabel'] = Tkinter.Label(self.widgets['tframe'],text="There are currently no themes", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nothemeslabel'].grid(column=0,row=self.gridrow,sticky='EW')
	def editTheme(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings / Themes / Edit / {0}'.format(self.theme.name), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['fileLabel'] = Tkinter.Label(self.widgets['tframe'], text='File', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['fileLabel'].grid(column=0,row=self.gridrow,padx=10,pady=10,sticky='EW')
		
		self.widgets['fileData'] = Tkinter.Label(self.widgets['tframe'],text=self.theme.filepath, anchor=W, bg=self.colours['bg'], fg=self.colours['valuefg'], font=self.fonts['heading2'])
		self.widgets['fileData'].grid(column=1,row=self.gridrow,padx=10,pady=10,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['pframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['pframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.widgets['profilesLabel'] = Tkinter.Label(self.widgets['pframe'],image=self.images['profile'], anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['profilesLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['profilesTextLabel'] = Tkinter.Label(self.widgets['pframe'],text='Profiles', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['profilesTextLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		if(len(self.theme.profiles) > 0):
			self.widgets['profileNameLabel'] = Tkinter.Label(self.widgets['pframe'],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['profileNameLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['profileMinWidthLabel'] = Tkinter.Label(self.widgets['pframe'],text='Min Width', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['profileMinWidthLabel'].grid(column=1,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['profileMaxWidthLabel'] = Tkinter.Label(self.widgets['pframe'],text='Max Width', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['profileMaxWidthLabel'].grid(column=2,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['profileChangeLabel'] = Tkinter.Label(self.widgets['pframe'],text='Change', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['profileChangeLabel'].grid(column=3,row=self.gridrow,padx=10,sticky='EW')
			
			self.gridrow += 1
			
			for k, v in self.theme.profiles.iteritems():
				self.widgets[k+'label'] = Tkinter.Label(self.widgets['pframe'],text=k, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets[k+'label'].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets[k+'min'] = Tkinter.Label(self.widgets['pframe'],text=v['minwidth'], bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets[k+'min'].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets[k+'max'] = Tkinter.Label(self.widgets['pframe'],text=v['maxwidth'], bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets[k+'max'].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets[k+'change'] = Tkinter.Button(self.widgets['pframe'],text=u"Change", image=self.images['profile'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnChangeProfileClick(x))
				self.widgets[k+'change'].grid(column=3,row=self.gridrow, padx=10, sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['noprofileslabel'] = Tkinter.Label(self.widgets['pframe'],text="There are currently no profiles", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noprofileslabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['cframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['cframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.widgets['coloursLabel'] = Tkinter.Label(self.widgets['cframe'],image=self.images['colour'], anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['coloursLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['coloursTextLabel'] = Tkinter.Label(self.widgets['cframe'],text='Colours', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['coloursTextLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		
		if(len(self.theme.colours) > 0):
			self.widgets['colourNameLabel'] = Tkinter.Label(self.widgets['cframe'],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['colourNameLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['colourHexLabel'] = Tkinter.Label(self.widgets['cframe'],text='Hex', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['colourHexLabel'].grid(column=1,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['colourDisplayLabel'] = Tkinter.Label(self.widgets['cframe'],text='Colour', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['colourDisplayLabel'].grid(column=2,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['colourChangeLabel'] = Tkinter.Label(self.widgets['cframe'],text='Change', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['colourChangeLabel'].grid(column=3,row=self.gridrow,padx=10,sticky='EW')
			self.gridrow += 1
			for k, v in self.theme.colours.iteritems():
				self.widgets['colourName'+str(k)] = Tkinter.Label(self.widgets['cframe'],text=str(k), bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['colourName'+str(k)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['colourHex'+str(k)] = Tkinter.Label(self.widgets['cframe'],text=v, bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['colourHex'+str(k)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['colourDisplay'+str(k)] = Tkinter.Label(self.widgets['cframe'], bg=v, fg=self.colours['fg'], width= 4, height=2)
				self.widgets['colourDisplay'+str(k)].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['colourChange'+str(k)] = Tkinter.Button(self.widgets['cframe'],text=u"Change", image=self.images['colour'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnChangeColourClick(x))
				self.widgets['colourChange'+str(k)].grid(column=3,row=self.gridrow, sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['nocolourslabel'] = Tkinter.Label(self.widgets['cframe'],text="There are currently no colours", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nocolourslabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['iframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['iframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.widgets['imagesLabel'] = Tkinter.Label(self.widgets['iframe'],image=self.images['image'], anchor=W, bg=self.colours['bg'])
		self.widgets['imagesLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['imagesTextLabel'] = Tkinter.Label(self.widgets['iframe'],text='Images', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['imagesTextLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		
		if(len(self.theme.images) > 0):
			self.widgets['imageNameLabel'] = Tkinter.Label(self.widgets['iframe'],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['imageNameLabel'].grid(column=0,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['imageFileLabel'] = Tkinter.Label(self.widgets['iframe'],text='File', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['imageFileLabel'].grid(column=1,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['imageChangeLabel'] = Tkinter.Label(self.widgets['iframe'],text='Change', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['imageChangeLabel'].grid(column=2,row=self.gridrow,padx=10,sticky='EW')
			self.widgets['imagePreviewLabel'] = Tkinter.Label(self.widgets['iframe'],text='Preview', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['imagePreviewLabel'].grid(column=3,row=self.gridrow,padx=10,sticky='EW')
			self.gridrow += 1
			for k, v in self.theme.images.iteritems():
				self.widgets['imageName'+str(k)] = Tkinter.Label(self.widgets['iframe'],text=str(k), bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['imageName'+str(k)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['imageFile'+str(k)] = Tkinter.Label(self.widgets['iframe'],text=str(v), bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['imageFile'+str(k)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['imageChange'+str(k)] = Tkinter.Button(self.widgets['iframe'],text=u"Change", image=self.images['image'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnChangeImageClick(x))
				self.widgets['imageChange'+str(k)].grid(column=2,row=self.gridrow, sticky='EW')
				self.widgets['imagePreview'+str(k)] = Tkinter.Label(self.widgets['iframe'],image=self.images[k], bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['imagePreview'+str(k)].grid(column=3,row=self.gridrow,sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['noimageslabel'] = Tkinter.Label(self.widgets['iframe'],text="There are currently no images", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['noimageslabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['fframe'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['fframe'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.widgets['fontsLabel'] = Tkinter.Label(self.widgets['fframe'],image=self.images['font'], anchor=W, bg=self.colours['bg'])
		self.widgets['fontsLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['fontsTextLabel'] = Tkinter.Label(self.widgets['fframe'],text='Fonts', anchor=W, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading2'])
		self.widgets['fontsTextLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		self.gridrow += 1

		if(len(self.theme.fonts) > 0):
			self.widgets['fontNameLabel'] = Tkinter.Label(self.widgets['fframe'],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['fontNameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.widgets['fontFamilyLabel'] = Tkinter.Label(self.widgets['fframe'],text='Family', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['fontFamilyLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			self.widgets['fontSizeLabel'] = Tkinter.Label(self.widgets['fframe'],text='Size', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['fontSizeLabel'].grid(column=2,row=self.gridrow,sticky='EW')
			self.widgets['fontChangeLabel'] = Tkinter.Label(self.widgets['fframe'],text='Change', bg=self.colours['bg'], fg=self.colours['headingfg'])
			self.widgets['fontChangeLabel'].grid(column=3,row=self.gridrow,sticky='EW')
			self.gridrow += 1
			for k, v in self.theme.fonts.iteritems():
				self.widgets['fontName'+str(k)] = Tkinter.Label(self.widgets['fframe'],text=str(k), bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['fontName'+str(k)].grid(column=0,row=self.gridrow,sticky='EW')
				self.widgets['fontFamily'+str(k)] = Tkinter.Label(self.widgets['fframe'],text=str(v['family']), bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['fontFamily'+str(k)].grid(column=1,row=self.gridrow,sticky='EW')
				self.widgets['fontSize'+str(k)] = Tkinter.Label(self.widgets['fframe'],text=str(v['size']), bg=self.colours['bg'], fg=self.colours['fg'])
				self.widgets['fontSize'+str(k)].grid(column=2,row=self.gridrow,sticky='EW')
				self.widgets['fontChange'+str(k)] = Tkinter.Button(self.widgets['fframe'],text=u"Change", image=self.images['font'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = k:self.OnChangeFontClick(x))
				self.widgets['fontChange'+str(k)].grid(column=3,row=self.gridrow, sticky='EW')
				self.gridrow += 1
		else:
			self.widgets['nofontslabel'] = Tkinter.Label(self.widgets['fframe'],text="There are currently no fonts", bg=self.colours['bg'], fg=self.colours['fg'])
			self.widgets['nofontslabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
		self.widgets['cloneLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Clone', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['cloneLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.listThemes, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['savetheme'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['savetheme'].grid(column=1,row=self.gridrow)
		self.widgets['clonetheme'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Clone", image=self.images['ram'], command=self.OnCloneThemeClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['clonetheme'].grid(column=2,row=self.gridrow)
	def cloneTheme(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings / Themes / Clone / {0}'.format(self.theme.name), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['themeLabel'] = Tkinter.Label(self.widgets['tframe'],text='Please confirm the new name for the cloned theme', anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['themeLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['nameData'] = Tkinter.Label(self.widgets['tframe'],text=self.theme.name, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['newLabel'] = Tkinter.Label(self.widgets['tframe'],text='New Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['newLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['newname'] = Tkinter.StringVar()
		self.widgets['newentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['newname'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['newentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['newname'].set('{0}_new'.format(self.theme.name))
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.editTheme, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['cloneconfirm'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['accept'], command=self.OnCloneThemeConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['cloneconfirm'].grid(column=1,row=self.gridrow)
	def deleteTheme(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings / Themes / Delete / {0}'.format(self.theme.name), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['nameData'] = Tkinter.Label(self.widgets['tframe'],text=self.theme.name, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['infoLabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this theme?', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['infoLabel'].grid(column=0,row=self.gridrow, columnspan = 2, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['acceptLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['acceptLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.editTheme, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['deleteconfirm'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['accept'], command=self.OnDeleteConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['deleteconfirm'].grid(column=1,row=self.gridrow)
		
	##== Profile ==##
	def editProfile(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings / Themes / Edit / {0} / Profile / {1}'.format(self.theme.name, self.profile['name']), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['aFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['aFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.widgets['anameLabel'] = Tkinter.Label(self.widgets['aFrame'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['anameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.variables['aname'] = Tkinter.StringVar()
		self.widgets['anameentry'] = Tkinter.Entry(self.widgets['aFrame'], textvariable=self.variables['aname'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['anameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['aname'].set(self.profile['name'])
		
		self.gridrow += 1
		
		self.widgets['aminLabel'] = Tkinter.Label(self.widgets['aFrame'],text='Minimum Width', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['aminLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.variables['amin'] = Tkinter.StringVar()
		self.widgets['aminentry'] = Tkinter.Entry(self.widgets['aFrame'], textvariable=self.variables['amin'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['aminentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['amin'].set(self.profile['minwidth'])
		
		self.gridrow += 1
		
		self.widgets['amaxLabel'] = Tkinter.Label(self.widgets['aFrame'],text='Maximum Width', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['amaxLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.variables['amax'] = Tkinter.StringVar()
		self.widgets['amaxentry'] = Tkinter.Entry(self.widgets['aFrame'], textvariable=self.variables['amax'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['amaxentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['amax'].set(self.profile['maxwidth'])
		
		self.gridrow += 1
		
		self.widgets['ascrollLabel'] = Tkinter.Label(self.widgets['aFrame'],text='Scrollable', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['ascrollLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.variables['ascroll'] = Tkinter.BooleanVar()
		self.widgets['ascrollentry'] = Tkinter.Checkbutton(self.widgets['aFrame'], text="Enabled", variable=self.variables['ascroll'], bg=self.colours['inputbg'], fg=self.colours['inputfg'], activebackground=self.colours['activebg'], selectcolor=self.colours['inputbg'])
		self.widgets['ascrollentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['ascroll'].set(bool(self.profile['scrollable']))
		
		self.gridrow += 1
		
		self.widgets['layoutLabel'] = Tkinter.Label(self.widgets['aFrame'],text='Layout', bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
		self.widgets['layoutLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['lFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['lFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		if (any(self.profile['frames'])):
			for f in self.profile['frames']:
				self.widgets['fwFrame'+f['name']] = Tkinter.Frame(self.widgets['lFrame'], bg=self.colours['bg'], highlightthickness=1)
				self.widgets['fwFrame'+f['name']].grid(column=f['column'],row=f['row'],columnspan=f['columnspan'], rowspan=f['rowspan'], sticky='WENS')
				
				self.widgets['lFrame'].rowconfigure(f['row'], weight=1)
				self.widgets['fwFrame'+f['name']].columnconfigure(0, weight=1)
				
				self.widgets['fFrame'+f['name']] = Tkinter.Frame(self.widgets['fwFrame'+f['name']], bg=self.colours['bg'], highlightthickness=1)
				self.widgets['fFrame'+f['name']].grid(column=0,row=0, sticky='WENS')
				
				self.widgets['fOptFrame'+f['name']] = Tkinter.Frame(self.widgets['fwFrame'+f['name']], bg=self.colours['bg'], highlightthickness=1)
				self.widgets['fOptFrame'+f['name']].grid(column=0,row=1, sticky='WENS')
				
				self.widgets['fnameLabel'+f['name']] = Tkinter.Label(self.widgets['fOptFrame'+f['name']],text=f['name'], bg=self.colours['bg'], fg=self.colours['headingfg'], height=2)
				self.widgets['fnameLabel'+f['name']].grid(column=0,row=0, padx=10,sticky='EW')
				
				self.widgets['fChange'+f['name']] = Tkinter.Button(self.widgets['fOptFrame'+f['name']],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = f['name']:self.OnChangeFrameClick(x))
				self.widgets['fChange'+f['name']].grid(column=1,row=0, sticky='E')
				
				self.widgets['fAdd'+f['name']] = Tkinter.Button(self.widgets['fOptFrame'+f['name']],text=u"Add", image=self.images['add'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = f['name']:self.OnAddWidgetClick(x))
				self.widgets['fAdd'+f['name']].grid(column=2,row=0, sticky='E')
				
				self.widgets['fDelete'+f['name']] = Tkinter.Button(self.widgets['fOptFrame'+f['name']],text=u"Delete", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = f['name']:self.OnDeleteFrameClick(x))
				self.widgets['fDelete'+f['name']].grid(column=3,row=0, sticky='E')
				
				if (any(f['widgets'])):
					for w in f['widgets']:
						frameKey = f['name']+str(w['column'])+'x'+str(w['row'])
						try:
							self.widgets['wwFrame'+frameKey]
						except:
							self.widgets['wwFrame'+frameKey] = Tkinter.Frame(self.widgets['fFrame'+f['name']], bg=self.colours['rowbg'], highlightthickness=1)
							self.widgets['wwFrame'+frameKey].grid(column=w['column'],row=w['row'],columnspan=w['columnspan'], rowspan=w['rowspan'], sticky='EW')
						self.widgets['wFrame'+f['name']+w['name']] = Tkinter.Frame(self.widgets['wwFrame'+frameKey], bg=self.colours['bg'], highlightthickness=1)
						self.widgets['wFrame'+f['name']+w['name']].grid(column=0,row=self.gridrow,columnspan=w['columnspan'], rowspan=w['rowspan'], sticky='EW')
						
						self.widgets['Label'+f['name']+w['name']] = Tkinter.Label(self.widgets['wFrame'+f['name']+w['name']],text=w['name'], bg=self.colours['bg'], fg=self.colours['valuefg'], height=2)
						self.widgets['Label'+f['name']+w['name']].grid(column=0,row=0, padx=10,sticky='EW')
						
						self.widgets['wChange'+f['name']+w['name']] = Tkinter.Button(self.widgets['wFrame'+f['name']+w['name']],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = (f['name'],w['name']):self.OnChangeWidgetClick(x))
						self.widgets['wChange'+f['name']+w['name']].grid(column=1,row=0, sticky='E')
						
						self.widgets['wDelete'+f['name']+w['name']] = Tkinter.Button(self.widgets['wFrame'+f['name']+w['name']],text=u"Delete", image=self.images['delete'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=lambda x = (f['name'],w['name']):self.OnDeleteWidgetClick(x))
						self.widgets['wDelete'+f['name']+w['name']].grid(column=2,row=0, sticky='E')
						
						self.gridrow += 1
				else:
					self.widgets['noWidgets'+f['name']] = Tkinter.Label(self.widgets['fFrame'+f['name']],text='No widgets', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
					self.widgets['noWidgets'+f['name']].grid(column=0,row=self.gridrow,sticky='EW')
		else:
			self.widgets['noframesLabel'] = Tkinter.Label(self.widgets['lFrame'],text='No existing frames', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
			self.widgets['noframeslabel'].grid(column=0,row=self.gridrow,sticky='EW')
			self.gridrow += 1
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.editTheme, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['saveimage'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveProfileClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['saveimage'].grid(column=1,row=self.gridrow)
	
	##== Frame ==##
	def editFrame(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings / Themes / Edit / {0} / Profile / {1} / Frame / {2} / Edit'.format(self.theme.name, self.profile['name'], self.tframe['name']), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['dataFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['dataFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['name'] = Tkinter.StringVar()
		self.widgets['nameentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['name'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['nameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['name'].set(self.tframe['name'])
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Identifies this frame. eg. "left"', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['rowLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Row', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['rowLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['row'] = Tkinter.StringVar()
		self.widgets['rowentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['row'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['rowentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['row'].set(self.tframe['row'])
		
		self.gridrow += 1
		
		self.widgets['columnLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Column', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['columnLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['column'] = Tkinter.StringVar()
		self.widgets['columnentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['column'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['columnentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['column'].set(self.tframe['column'])
		
		self.gridrow += 1
		
		self.widgets['rowspanLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Row Span', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['rowspanLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['rowspan'] = Tkinter.StringVar()
		self.widgets['rowspanentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['rowspan'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['rowspanentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['rowspan'].set(self.tframe['rowspan'])
		
		self.gridrow += 1
		
		self.widgets['columnspanLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Column Span', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['columnspanLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['columnspan'] = Tkinter.StringVar()
		self.widgets['columnspanentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['columnspan'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['columnspanentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['columnspan'].set(self.tframe['columnspan'])
		
		self.gridrow += 1
		
		self.widgets['padxLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Pad X', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['padxLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['padx'] = Tkinter.StringVar()
		self.widgets['padxentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['padx'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['padxentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['padx'].set(self.tframe['padx'])
		
		self.gridrow += 1
		
		self.widgets['padyLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Pad Y', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['padyLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['pady'] = Tkinter.StringVar()
		self.widgets['padyentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['pady'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['padyentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['pady'].set(self.tframe['pady'])
		
		self.gridrow += 1
		
		self.widgets['stickyLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Sticky', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['stickyLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['sticky'] = Tkinter.StringVar()
		self.widgets['stickyentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['sticky'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['stickyentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['sticky'].set(self.tframe['sticky'])
		
		self.gridrow += 1
		
		self.widgets['scrollableLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Scrollable', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['scrollableLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['scrollable'] = Tkinter.StringVar()
		self.widgets['scrollableentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['scrollable'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['scrollableentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['scrollable'].set(self.tframe['scrollable'])
		
		self.gridrow += 1
		
		self.widgets['rowweightLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Row Weight', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['rowweightLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['rowweight'] = Tkinter.StringVar()
		self.widgets['rowweightentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['rowweight'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['rowweightentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['rowweight'].set(self.tframe['rowweight'])
		
		self.gridrow += 1
		
		self.widgets['columnweightLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Column Weight', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['columnweightLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['columnweight'] = Tkinter.StringVar()
		self.widgets['columnweightentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['columnweight'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['columnweightentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['columnweight'].set(self.tframe['columnweight'])
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnFrameBackClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['saveimage'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveFrameClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['saveimage'].grid(column=1,row=self.gridrow)
	def deleteFrame(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings / Themes / Edit / {0} / Profile / {1} / Frame / {2} / Delete'.format(self.theme.name, self.profile['name'], self.tframe['name']), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['confirmLabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this frame?', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['confirmLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['acceptLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['acceptLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnFrameBackClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['deleteconfirm'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['accept'], command=self.OnDeleteFrameConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['deleteconfirm'].grid(column=1,row=self.gridrow)
	
	##== Widget ==##
	def editWidget(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings / Themes / Edit / {0} / Profile / {1} / Frame / {2} / Widget / {3} / Edit'.format(self.theme.name, self.profile['name'], self.tframe['name'], self.twidget['name']), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.gridrow += 1
		
		self.widgets['dataFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['dataFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['name'] = Tkinter.StringVar()
		self.widgets['nameentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['name'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['nameentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['name'].set('' if self.twidget['name'] == None else self.twidget['name'])
		
		self.widgets['helpLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Format: module.class (must be a class which extends either TkBlock or TkPage)', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['helpLabel'].grid(column=2,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['rowLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Row', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['rowLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['row'] = Tkinter.StringVar()
		self.widgets['rowentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['row'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['rowentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['row'].set(self.twidget['row'])
		
		self.gridrow += 1
		
		self.widgets['columnLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Column', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['columnLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['column'] = Tkinter.StringVar()
		self.widgets['columnentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['column'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['columnentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['column'].set(self.twidget['column'])
		
		self.gridrow += 1
		
		self.widgets['widthLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Width', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['widthLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['width'] = Tkinter.StringVar()
		self.widgets['widthentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['width'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['widthentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['width'].set(self.twidget['width'] if self.twidget['width'] != None else '')
		
		self.gridrow += 1
		
		self.widgets['heightLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Height', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['heightLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['height'] = Tkinter.StringVar()
		self.widgets['heightentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['height'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['heightentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['height'].set(self.twidget['height'] if self.twidget['height'] != None else '')
		
		self.gridrow += 1
		
		self.widgets['rowspanLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Row Span', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['rowspanLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['rowspan'] = Tkinter.StringVar()
		self.widgets['rowspanentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['rowspan'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['rowspanentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['rowspan'].set(self.twidget['rowspan'])
		
		self.gridrow += 1
		
		self.widgets['columnspanLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Column Span', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['columnspanLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['columnspan'] = Tkinter.StringVar()
		self.widgets['columnspanentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['columnspan'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['columnspanentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['columnspan'].set(self.twidget['columnspan'])
		
		self.gridrow += 1
		
		self.widgets['padxLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Pad X', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['padxLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['padx'] = Tkinter.StringVar()
		self.widgets['padxentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['padx'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['padxentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['padx'].set(self.twidget['padx'])
		
		self.gridrow += 1
		
		self.widgets['padyLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Pad Y', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['padyLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['pady'] = Tkinter.StringVar()
		self.widgets['padyentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['pady'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['padyentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['pady'].set(self.twidget['pady'])
		
		self.gridrow += 1
		
		self.widgets['stickyLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Sticky', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['stickyLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['sticky'] = Tkinter.StringVar()
		self.widgets['stickyentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['sticky'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['stickyentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['sticky'].set(self.twidget['sticky'])
		
		self.gridrow += 1
		
		self.widgets['scrollableLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Scrollable', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['scrollableLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['scrollable'] = Tkinter.StringVar()
		self.widgets['scrollableentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['scrollable'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['scrollableentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['scrollable'].set(self.twidget['scrollable'])
		
		self.gridrow += 1
		
		self.widgets['rowweightLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Row Weight', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['rowweightLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['rowweight'] = Tkinter.StringVar()
		self.widgets['rowweightentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['rowweight'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['rowweightentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['rowweight'].set(self.twidget['rowweight'])
		
		self.gridrow += 1
		
		self.widgets['columnweightLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Column Weight', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['columnweightLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['columnweight'] = Tkinter.StringVar()
		self.widgets['columnweightentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['columnweight'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['columnweightentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['columnweight'].set(self.twidget['columnweight'])
		
		self.gridrow += 1
		
		self.widgets['menuindexLabel'] = Tkinter.Label(self.widgets['dataFrame'],text='Menu Index', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['menuindexLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['menuindex'] = Tkinter.StringVar()
		self.widgets['menuindexentry'] = Tkinter.Entry(self.widgets['dataFrame'], textvariable=self.variables['menuindex'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['menuindexentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['menuindex'].set(self.twidget['menuindex'] if self.twidget['menuindex'] != None else '')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnWidgetBackClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['saveimage'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveWidgetClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['saveimage'].grid(column=1,row=self.gridrow)
	def deleteWidget(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings / Themes / Edit / {0} / Profile / {1} / Frame / {2} / Delete'.format(self.theme.name, self.profile['name'], self.tframe['name'], self.twidget['name']), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['confirmLabel'] = Tkinter.Label(self.widgets['tframe'],text='Are you sure you want to delete this widget?', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['confirmLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['acceptLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Accept', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['acceptLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.OnWidgetBackClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['deleteconfirm'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['accept'], command=self.OnDeleteWidgetConfirmClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['deleteconfirm'].grid(column=1,row=self.gridrow)
	
	##== Font ==##
	def editFont(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings / Themes / Edit / {0} / Font'.format(self.theme.name), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		self.gridrow += 1
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['nameData'] = Tkinter.Label(self.widgets['tframe'],text=self.currentfont, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		
		self.widgets['familyLabel'] = Tkinter.Label(self.widgets['tframe'],text='Family', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['familyLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['family'] = Tkinter.StringVar()
		self.widgets['familyentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['family'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['familyentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['family'].set(self.theme.fonts[self.currentfont]['family'])
		
		self.gridrow += 1
		
		self.widgets['sizeLabel'] = Tkinter.Label(self.widgets['tframe'],text='Size', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['sizeLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.variables['size'] = Tkinter.IntVar()
		self.widgets['sizeentry'] = Tkinter.Entry(self.widgets['tframe'], textvariable=self.variables['size'], bg=self.colours['inputbg'], fg=self.colours['inputfg'])
		self.widgets['sizeentry'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['size'].set(self.theme.fonts[self.currentfont]['size'])
		
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.editTheme, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['savefont'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveFontClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['savefont'].grid(column=1,row=self.gridrow)
	
	##== Image ==##
	def editImage(self):
		self.open()
		self.widgets['frameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Settings / Themes / Edit / {0} / Image'.format(self.theme.name), anchor=NW, bg=self.colours['bg'], fg=self.colours['headingfg'], font=self.fonts['heading'])
		self.widgets['frameLabel'].grid(column=0,row=self.gridrow,columnspan=2,sticky='EW')
		
		self.gridrow += 1
		self.widgets['nameLabel'] = Tkinter.Label(self.widgets['tframe'],text='Name', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		
		self.widgets['nameData'] = Tkinter.Label(self.widgets['tframe'],text=self.currentimage, bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['nameData'].grid(column=1,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		self.widgets['fileLabel'] = Tkinter.Label(self.widgets['tframe'],text='File', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['fileLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.variables['file'] = Tkinter.StringVar()
		self.widgets['fileData'] = Tkinter.Label(self.widgets['tframe'],textvariable=self.variables['file'], bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['fileData'].grid(column=1,row=self.gridrow,sticky='EW')
		self.variables['file'].set(self.theme.images[self.currentimage])
		self.widgets['fileEdit'] = Tkinter.Button(self.widgets['tframe'],text=u"Edit", image=self.images['process'], bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'], command=self.OnPickImageClick)
		self.widgets['fileEdit'].grid(column=2,row=self.gridrow,sticky='EW')
		
		self.gridrow += 1
		self.widgets['previewLabel'] = Tkinter.Label(self.widgets['tframe'],text='Preview', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['previewLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['previewData'] = Tkinter.Label(self.widgets['tframe'],text="Preview",image=self.images[self.currentimage], bg=self.colours['bg'], fg=self.colours['fg'])
		self.widgets['previewData'].grid(column=1,row=self.gridrow,sticky='EW')
		self.gridrow += 1
		
		self.widgets['optionsFrame'] = Tkinter.Frame(self.widgets['tframe'], bg=self.colours['bg'])
		self.widgets['optionsFrame'].grid(column=0,row=self.gridrow,columnspan=2, sticky='EW')
		
		self.gridrow = 0
		
		self.widgets['backLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Back', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['backLabel'].grid(column=0,row=self.gridrow,sticky='EW')
		self.widgets['saveLabel'] = Tkinter.Label(self.widgets['optionsFrame'],text='Save', bg=self.colours['bg'], fg=self.colours['fg'], height=2)
		self.widgets['saveLabel'].grid(column=1,row=self.gridrow,sticky='EW')
			
		self.gridrow += 1

		self.widgets['back'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Back", image=self.images['back'], command=self.editTheme, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['back'].grid(column=0,row=self.gridrow)
		self.widgets['saveimage'] = Tkinter.Button(self.widgets['optionsFrame'],text=u"Save", image=self.images['save'], command=self.OnSaveImageClick, bg=self.colours['buttonbg'], activebackground=self.colours['buttonhighlightbg'], highlightbackground=self.colours['buttonborder'])
		self.widgets['saveimage'].grid(column=1,row=self.gridrow)
	
	
	#=== ACTIONS ===#
	##== Theme ==##
	def OnListThemesClick(self):
		self.listThemes()
	def OnEditThemeClick(self, name):
		self.theme = Theme(name)
		self.theme.load()
		self.images = {}
		for k, v in self.theme.images.iteritems():
			self.images[k] = Tkinter.PhotoImage(file = os.path.join(self.theme.basepath, v))
		self.editTheme()
	def OnCloneThemeClick(self):
		self.cloneTheme()
	def OnCloneThemeConfirmClick(self):
		name = self.variables['newname'].get()
		if(name != '' and name != self.theme.name):
			themes = self.theme.query()
			for k, v in themes.iteritems():
				if(k == name):
					return False
			self.theme.clone(name)
			self.notifier.addNotice('Theme cloned')
		return False
	def OnActivateThemeClick(self, name):
		Setting.set('gui_theme_name', name)
		self.listThemes()
		self.notifier.addNotice('Theme {0} activated', name)
	def OnSaveClick(self):
		self.theme.save()
		self.listThemes()
		self.notifier.addNotice('Theme saved')
	def OnDeleteClick(self, name):
		self.theme = Theme(name)
		self.theme.load()
		self.deleteTheme()
	def OnDeleteConfirmClick(self):
		self.theme = Theme(name)
		self.theme.load()
		self.deleteTheme()
	
	##== Colour ==##
	def OnChangeColourClick(self, name):
		result = tkColorChooser.askcolor(self.theme.colours[name])
		if(result != (None, None)):
			rgb, hex = result
			self.theme.colours[name] = hex
			self.widgets['colourHex'+str(name)].configure(text = hex)
			self.widgets['colourDisplay'+str(name)].configure(bg = hex)
			self.notifier.addNotice('Colour changed. Click Save to commit', 'warning')
	
	##== Font ==##
	def OnChangeFontClick(self, name):
		self.currentfont = name
		self.editFont()
	def OnSaveFontClick(self):
		self.theme.fonts[self.currentfont]['family'] = self.variables['family'].get()
		self.theme.fonts[self.currentfont]['size'] = self.variables['size'].get()
		self.editTheme()
		self.notifier.addNotice('Font changed. Click Save to commit', 'warning')
	
	##== Image ==##
	def OnChangeImageClick(self, name):
		self.currentimage = name
		self.editImage()
	def OnPickImageClick(self):
		filename = askopenfilename()
		if(len(filename) > 0):
			parts = os.path.splitext(filename)
			if('.gif' == parts[-1]):
				if(self.theme.basepath in filename):
					filename = filename.replace(self.theme.basepath+'/', '')
				else:
					filename = self.__copyAsset(filename)
				self.variables['file'].set(filename)
				self.im = Tkinter.PhotoImage(file = os.path.join(self.theme.basepath, filename))
				self.widgets['previewData'].configure(image=self.im)
				self.notifier.addNotice('Image preview updated')
			else:
				self.notifier.addNotice('Images must be in gif format', 'error')
		else:
			self.notifier.addNotice('Change cancelled', 'warning')
	def OnSaveImageClick(self):
		if(hasattr(self, 'currentimage')):
			self.theme.images[self.currentimage] = self.variables['file'].get()
			self.notifier.addNotice('Image changed. Click Save to commit', 'warning')

	##== Profile ==##
	def OnChangeProfileClick(self, name):
		self.profile = self.theme.profiles[name]
		self.editProfile()
	def OnSaveProfileClick(self):
		p = self.theme.profiles[self.profile.name]
		p['name'] = self.variables['aname'].get()
		p['minwidth'] = self.variables['amin'].get()
		p['maxwidth'] = self.variables['amax'].get()
		p['scrollable'] = self.variables['ascroll'].get()
		self.theme.save()
		self.notifier.addNotice('Profile Saved', 'message')
	
	##== Frame ==##
	def OnChangeFrameClick(self, index):
		self.tframe = self.profile['frames'][self.__getFrameIndex(index)]
		self.editFrame()
	def OnSaveFrameClick(self):
		if (not self.__validateFrameName()):
			return
		f = self.profile['frames'][self.__getFrameIndex(self.tframe['name'])]
		f['name'] = self.variables['name'].get()
		f['column'] = self.variables['column'].get()
		f['row'] = self.variables['row'].get()
		f['columnspan'] = self.variables['columnspan'].get()
		f['rowspan'] = self.variables['rowspan'].get()
		f['padx'] = self.variables['padx'].get()
		f['pady'] = self.variables['pady'].get()
		f['sticky'] = self.variables['sticky'].get()
		f['scrollable'] = self.variables['scrollable'].get()
		f['columnweight'] = self.variables['columnweight'].get()
		f['rowweight'] = self.variables['rowweight'].get()
		self.theme.save()
		self.notifier.addNotice('Frame Saved', 'message')
		self.editProfile()
	def OnDeleteFrameClick(self, index):
		self.tframe = self.profile['frames'][self.__getFrameIndex(index)]
		self.deleteFrame()
	def OnDeleteFrameConfirmClick(self):
		del(self.profile['frames'][self.__getFrameIndex(self.tframe['name'])])
		self.theme.save()
		self.notifier.addNotice('Frame Deleted', 'message')
		self.editProfile()
	def OnFrameBackClick(self):
		self.editProfile()
	
	##== Widget ==##
	def OnAddWidgetClick(self, index):
		self.tframe = self.profile['frames'][self.__getFrameIndex(index)]
		self.twidget = {
			'name': None,
			'row': 0,
			'column': 0,
			'width': None,
			'height': None,
			'rowspan': 1, 
			'columnspan': 1, 
			'padx': 0, 
			'pady': 0, 
			'sticky': 'WENS', 
			'scrollable': False,
			'rowweight': 1, 
			'columnweight': 1,
			'menuindex': None
		}
		self.editWidget()
	def OnChangeWidgetClick(self, index):
		findex = self.__getFrameIndex(index[0])
		self.tframe = self.profile['frames'][findex]
		self.twidget = self.tframe['widgets'][self.__getWidgetIndex(findex, index[1])]
		self.editWidget()
	def OnSaveWidgetClick(self):
		if (not self.__validateWidgetName()):
			return
		findex = self.__getFrameIndex(self.tframe['name'])
		if (findex == None):
			self.notifier.addNotice('Unknown frame', 'error')
			self.editProfile()
			return
		if (self.twidget['name'] != None):
			w = self.profile['frames'][findex]['widgets'][self.__getWidgetIndex(findex, self.twidget['name'])]
			w['name'] = self.variables['name'].get()
			w['column'] = self.variables['column'].get()
			w['row'] = self.variables['row'].get()
			w['width'] = self.variables['width'].get()
			w['height'] = self.variables['height'].get()
			w['columnspan'] = self.variables['columnspan'].get()
			w['rowspan'] = self.variables['rowspan'].get()
			w['padx'] = self.variables['padx'].get()
			w['pady'] = self.variables['pady'].get()
			w['sticky'] = self.variables['sticky'].get()
			w['scrollable'] = self.variables['scrollable'].get()
			w['columnweight'] = self.variables['columnweight'].get()
			w['rowweight'] = self.variables['rowweight'].get()
			w['menuindex'] = self.variables['menuindex'].get()
		else:
			self.profile['frames'][findex]['widgets'].append({
				'name': self.variables['name'].get(),
				'column': self.variables['column'].get(),
				'row': self.variables['row'].get(),
				'width': self.variables['width'].get(),
				'height': self.variables['height'].get(),
				'columnspan': self.variables['columnspan'].get(),
				'rowspan': self.variables['rowspan'].get(),
				'padx': self.variables['padx'].get(),
				'pady': self.variables['pady'].get(),
				'sticky': self.variables['sticky'].get(),
				'scrollable': self.variables['scrollable'].get(),
				'columnweight': self.variables['columnweight'].get(),
				'rowweight': self.variables['rowweight'].get(),
				'menuindex': self.variables['menuindex'].get(),
			})
		
		self.theme.save()
		self.notifier.addNotice('Widget Saved', 'message')
		self.editProfile()
	def OnDeleteWidgetClick(self, index):
		findex = self.__getFrameIndex(index[0])
		self.tframe = self.profile['frames'][findex]
		self.twidget = self.tframe['widgets'][self.__getWidgetIndex(findex, index[1])]
		self.deleteWidget()
	def OnDeleteWidgetConfirmClick(self):
		print(self.twidget['name'])
		findex = self.__getFrameIndex(self.tframe['name'])
		del(self.profile['frames'][findex]['widgets'][self.__getWidgetIndex(findex, self.twidget['name'])])
		self.theme.save()
		self.notifier.addNotice('Widget Deleted', 'message')
		self.editProfile()
	def OnWidgetBackClick(self):
		self.editFrame()
	
	##== Utils ==##
	def __getFrameIndex(self, name):
		ind = 0
		for f in self.profile['frames']:
			if (name == f['name']):
				return ind
			else:
				ind += 1
		return None
	def __getWidgetIndex(self, findex, name):
		ind = 0
		for f in self.profile['frames'][findex]['widgets']:
			if (name == f['name']):
				return ind
			else:
				ind += 1
		return None
	def __copyAsset(self, filename):
		newbase = os.path.join(self.theme.basepath, 'images')
		parts = filename.split('/')
		file = parts[-1]
		if not os.path.exists(newbase):
			os.makedirs(newbase)
		shutil.copyfile(filename, os.path.join(newbase, file))
		return os.path.join('images',file)
	def __validateFrameName(self):
		name = self.variables['name'].get()
		if (name == ''):
			self.notifier.addNotice('Name must not be empty', 'error')
			return False
		if (' ' in name):
			self.notifier.addNotice('Name must not contain spaces', 'error')
			return False
		return True
	def __validateWidgetName(self):
		name = self.variables['name'].get()
		if (name == ''):
			self.notifier.addNotice('Name must not be empty', 'error')
			return False
		if (' ' in name):
			self.notifier.addNotice('Name must not contain spaces', 'error')
			return False
		if (not '.' in name):
			self.notifier.addNotice('Name must contain "." separating module and class', 'error')
			return False
		nameparts = name.split('.')
		if (len(nameparts) != 2):
			self.notifier.addNotice('Name must contain a single "."', 'error')
			return False
		return True