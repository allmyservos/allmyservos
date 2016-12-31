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
import sys, os, distutils.core, traceback
from __bootstrap import AmsEnvironment
from xml.dom import minidom
from xml.dom.minidom import Document

## Manage XML theme data
class Theme(object):
	def __init__(self, name = 'NewTheme', screen = None):
		""" Initializes the Theme object
		"""
		self.name = name
		if(screen != None):
			self.screen = screen
		else:
			self.screen = { 'width': 0, 'height': 0 }
		self.basepath = os.path.join(AmsEnvironment.AppPath(), 'themes', self.safeName())
		self.filepath = '{0}/{1}.theme.xml'.format(self.basepath, self.name)
		self.profiles, self.images, self.colours, self.fonts = {}, {}, {}, {}
	def save(self):
		""" save theme XMl
		"""
		doc = Document()
		base = doc.createElement('theme')
		base.setAttribute('name', self.name)
		profilesElem = doc.createElement('profiles')
		imagesElem = doc.createElement('images')
		coloursElem = doc.createElement('colours')
		fontsElem = doc.createElement('fonts')
		for k, v in self.profiles.iteritems():
			profileElem = doc.createElement('profile')
			profileElem.setAttribute('name', str(v['name']))
			profileElem.setAttribute('minwidth', str(v['minwidth']))
			profileElem.setAttribute('maxwidth', str(v['maxwidth']))
			profileElem.setAttribute('scrollable', '1' if v['scrollable'] == True else '0')
			for f in v['frames']:
				frameElem = doc.createElement('frame')
				frameElem.setAttribute('name', str(f['name']))
				frameElem.setAttribute('row', str(f['row']))
				frameElem.setAttribute('column', str(f['column']))
				frameElem.setAttribute('rowspan', str(f['rowspan']))
				frameElem.setAttribute('columnspan', str(f['columnspan']))
				frameElem.setAttribute('padx', str(f['padx']))
				frameElem.setAttribute('pady', str(f['pady']))
				frameElem.setAttribute('sticky', str(f['sticky']))
				frameElem.setAttribute('scrollable', '1' if f['scrollable'] == True else '0')
				frameElem.setAttribute('columnweight', str(f['columnweight']))
				frameElem.setAttribute('rowweight', str(f['rowweight']))
				for w in f['widgets']:
					widgetElem = doc.createElement('widget')
					widgetElem.setAttribute('name', str(w['name']))
					widgetElem.setAttribute('row', str(w['row']))
					widgetElem.setAttribute('column', str(w['column']))
					if (isinstance(w['width'], int)):
						widgetElem.setAttribute('width', str(w['width']))
					if (isinstance(w['height'], int)):
						widgetElem.setAttribute('height', str(w['height']))
					widgetElem.setAttribute('rowspan', str(w['rowspan']))
					widgetElem.setAttribute('columnspan', str(w['columnspan']))
					widgetElem.setAttribute('padx', str(w['padx']))
					widgetElem.setAttribute('pady', str(w['pady']))
					widgetElem.setAttribute('sticky', str(w['sticky']))
					widgetElem.setAttribute('scrollable', '1' if w['scrollable'] == True else '0')
					widgetElem.setAttribute('columnweight', str(w['columnweight']))
					widgetElem.setAttribute('rowweight', str(w['rowweight']))
					if (isinstance(w['menuindex'], int)):
						widgetElem.setAttribute('menuindex', str(w['menuindex']))
					frameElem.appendChild(widgetElem)
				profileElem.appendChild(frameElem)
			profilesElem.appendChild(profileElem)
		for k, v in self.images.iteritems():
			imageElem = doc.createElement('image')
			imageElem.setAttribute('name', str(k))
			textElem = doc.createTextNode(str(v))
			imageElem.appendChild(textElem)
			imagesElem.appendChild(imageElem)
		for k, v in self.colours.iteritems():
			colourElem = doc.createElement('colour')
			colourElem.setAttribute('name', str(k))
			colour = str(v)
			if(colour.startswith('#')): colour = colour[1:]
			textElem = doc.createTextNode(colour)
			colourElem.appendChild(textElem)
			coloursElem.appendChild(colourElem)
		for k, v in self.fonts.iteritems():
			fontElem = doc.createElement('font')
			fontElem.setAttribute('name', str(k))
			fontElem.setAttribute('size', str(v['size']))
			textElem = doc.createTextNode(str(v['family']))
			fontElem.appendChild(textElem)
			fontsElem.appendChild(fontElem)
		base.appendChild(profilesElem)
		base.appendChild(imagesElem)
		base.appendChild(coloursElem)
		base.appendChild(fontsElem)
		doc.appendChild(base)
		if not os.path.exists(self.basepath):
			os.makedirs(self.basepath)
		f = open(self.filepath, 'w')
		doc.writexml(f, indent='\t', addindent='\t', newl='\r\n')
		f.close()
	def load(self):
		""" load theme XML
		"""
		try:
			if(len(self.filepath) > 0):
				xmldoc = minidom.parse(self.filepath)
				base = xmldoc.getElementsByTagName('theme')[0]
				self.name = base.getAttribute('name')
				self.parseProfiles(xmldoc.getElementsByTagName('profiles')[0])
				self.parseImages(xmldoc.getElementsByTagName('images')[0])
				self.parseColours(xmldoc.getElementsByTagName('colours')[0])
				self.parseFonts(xmldoc.getElementsByTagName('fonts')[0])
		except Exception,e:
			print('There was a problem parsing the theme xml: '+str(e)+ '\n' + str(traceback.format_exc()))
	def clone(self, newName):
		""" clone theme
		
		@param newName str
		"""
		newTheme = Theme(newName)
		newTheme.images = self.images
		newTheme.colours = self.colours
		newTheme.fonts = self.fonts
		newTheme.save()
		dirs = os.listdir(self.basepath)
		if(len(dirs) > 0):
			for d in dirs:
				srcpath = os.path.join(self.basepath, d)
				destpath = os.path.join(newTheme.basepath, d)
				if(os.path.isdir(srcpath)):
					if not os.path.exists(destpath):
						os.makedirs(destpath)
					distutils.dir_util.copy_tree(srcpath, destpath)
	def query(self):
		""" gets a list of available themes
		"""
		basepath = os.path.join(AmsEnvironment.AppPath(), 'themes')
		dirs = os.listdir(basepath)
		themes = {}
		if(len(dirs) > 0):
			for d in dirs:
				if(os.path.isdir(os.path.join(basepath, d)) and os.path.exists('{0}/{1}/{2}.theme.xml'.format(basepath, d, d))):
					themes[d] = Theme(d)
					themes[d].load()
		return themes
	def parseProfiles(self, profiles):
		""" loades profile data and selects the best profile for detected display size
		
		@param profiles 
		"""
		result = {}
		self.modules = {}
		for n in profiles.childNodes:
			if(n.nodeType == n.ELEMENT_NODE):
				if(n.tagName.lower() == 'profile'):
					profile = { 'name' : str(n.attributes['name'].value), 'minwidth': int(n.attributes['minwidth'].value), 'maxwidth': int(n.attributes['maxwidth'].value), 'scrollable': bool(int(n.attributes['scrollable'].value)), 'frames' : []}
					self.modules[profile['name']] = []
					f = n.firstChild
					while f != None:
						if(f.nodeType == f.ELEMENT_NODE):
							if(f.tagName.lower() == 'frame'):
								profile['frames'].append({ 'name': str(f.attributes['name'].value),
								'row': int(f.attributes['row'].value) if 'row' in f.attributes.keys() else None,
								'column': int(f.attributes['column'].value) if 'column' in f.attributes.keys() else None,
								'rowspan': int(f.attributes['rowspan'].value) if 'rowspan' in f.attributes.keys() else None, 
								'columnspan': int(f.attributes['columnspan'].value) if 'columnspan' in f.attributes.keys() else None, 
								'padx': int(f.attributes['padx'].value) if 'padx' in f.attributes.keys() else None, 
								'pady': int(f.attributes['pady'].value) if 'pady' in f.attributes.keys() else None, 
								'sticky': str(f.attributes['sticky'].value) if 'sticky' in f.attributes.keys() else None, 
								'scrollable': bool(int(f.attributes['scrollable'].value)) if 'scrollable' in f.attributes.keys() else None,
								'rowweight': int(f.attributes['rowweight'].value) if 'rowweight' in f.attributes.keys() else None, 
								'columnweight': int(f.attributes['columnweight'].value) if 'columnweight' in f.attributes.keys() else None,
								'widgets': []
								})
								for w in f.childNodes:
									if(w.nodeType == w.ELEMENT_NODE):
										if(w.tagName.lower() == 'widget'):
											profile['frames'][-1]['widgets'].append({
												'name': str(w.attributes['name'].value),
												'row': int(w.attributes['row'].value) if 'row' in w.attributes.keys() else None,
												'column': int(w.attributes['column'].value) if 'column' in w.attributes.keys() else None,
												'width': int(w.attributes['width'].value) if 'width' in w.attributes.keys() else None,
												'height': int(w.attributes['height'].value) if 'height' in w.attributes.keys() else None,
												'rowspan': int(w.attributes['rowspan'].value) if 'rowspan' in w.attributes.keys() else None, 
												'columnspan': int(w.attributes['columnspan'].value) if 'columnspan' in w.attributes.keys() else None, 
												'padx': int(w.attributes['padx'].value) if 'padx' in w.attributes.keys() else None, 
												'pady': int(w.attributes['pady'].value) if 'pady' in w.attributes.keys() else None, 
												'sticky': str(w.attributes['sticky'].value) if 'sticky' in w.attributes.keys() else None, 
												'scrollable': bool(int(w.attributes['scrollable'].value)) if 'scrollable' in w.attributes.keys() else None,
												'rowweight': int(w.attributes['rowweight'].value) if 'rowweight' in w.attributes.keys() else None, 
												'columnweight': int(w.attributes['columnweight'].value) if 'columnweight' in w.attributes.keys() else None,
												'menuindex': int(w.attributes['menuindex'].value) if 'menuindex' in w.attributes.keys() else None
											})
											self.modules[profile['name']].append(profile['frames'][-1]['widgets'][-1]['name'])
						f = f.nextSibling
					result.update({profile['name']: profile})
		self.profiles = result
		self.profile = { k: v for k, v in self.profiles.iteritems() if v['minwidth'] <= self.screen['width'] and (v['maxwidth'] == 0 or v['maxwidth'] >= self.screen['width']) }
		if(any(self.profile.keys())):
			self.profile = self.profile[self.profile.keys()[0]]
		else:
			self.profile = None
	def parseImages(self, images):
		""" parse image XML
		"""
		result = {}
		for n in images.childNodes:
			if(n.nodeType == n.ELEMENT_NODE):
				if(n.tagName.lower() == 'image'):
					result.update({str(n.attributes['name'].value): str(n.firstChild.nodeValue)})
		self.images = result
	def parseColours(self, colours):
		""" parse colour XML
		"""
		result = {}
		for n in colours.childNodes:
			if(n.nodeType == n.ELEMENT_NODE):
				if(n.tagName.lower() == 'colour'):
					result.update({str(n.attributes['name'].value): '#{0}'.format(str(n.firstChild.nodeValue))})
		self.colours = result
	def parseFonts(self, fonts):
		""" parse font XML
		"""
		result = {}
		for n in fonts.childNodes:
			if(n.nodeType == n.ELEMENT_NODE):
				if(n.tagName.lower() == 'font'):
					result.update({str(n.attributes['name'].value) : { 'family' : str(n.firstChild.nodeValue), 'size': int(n.attributes['size'].value) }})
		self.fonts = result
	def safeName(self):
		""" remove spaces from theme name
		"""
		return self.name.replace('\s', '')
if __name__ == "__main__":
	theme = Theme('DarkBlue')
	theme.load()
	theme.clone('Newb')