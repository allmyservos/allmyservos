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
import sys, traceback, logging, os, re
from subprocess import Popen, PIPE
from StringIO import StringIO

## The AmsEnvironment object collects required information from the host pi
class AmsEnvironment:
	patterns = {
		'pid': re.compile(r'(?P<pid>\d+)')
	}
	info = {}
	now = lambda: int(round(time.time() * 1000))
	@staticmethod
	def AppInfo():
		""" Returns environment info
		"""
		if (not any(AmsEnvironment.info)):
			a = AmsEnvironment.info
			a['app_path'] = os.path.dirname(__file__)
			a['contrib_path'] = os.path.join(a['app_path'],'contrib')
			a['file_path'] = os.path.join(a['app_path'],'files')
			a['command_script'] = sys.argv[0]
			a['command_args'] = sys.argv[1:]
			try:
				a['terminal'] = os.ttyname(sys.stdout.fileno())
			except:
				a['terminal'] = '';
		return AmsEnvironment.info
	@staticmethod
	def AppPath():
		""" Returns app path
		"""
		try:
			AmsEnvironment.info['app_path']
		except:
			AmsEnvironment.AppInfo()
		return AmsEnvironment.info['app_path']
	@staticmethod
	def ContribPath():
		""" Returns contrib path
		"""
		try:
			AmsEnvironment.info['contrib_path']
		except:
			AmsEnvironment.AppInfo()
		return AmsEnvironment.info['contrib_path']
	@staticmethod
	def FilePath():
		""" Returns file path
		"""
		try:
			AmsEnvironment.info['file_path']
		except:
			AmsEnvironment.AppInfo()
		return AmsEnvironment.info['file_path']
	@staticmethod
	def Terminal():
		""" Returns the current terminal
		"""
		try:
			AmsEnvironment.info['terminal']
		except:
			AmsEnvironment.AppInfo()
		return AmsEnvironment.info['terminal']
	@staticmethod
	def Vendors():
		""" Returns list of vendor names
		"""
		try:
			AmsEnvironment.__vendors
		except:
			AmsEnvironment.__vendors = os.listdir(AmsEnvironment.ContribPath())
			AmsEnvironment.__vendors = [ x for x in AmsEnvironment.__vendors if os.path.isdir(os.path.join(AmsEnvironment.ContribPath(), x)) ]
		return AmsEnvironment.__vendors
	@staticmethod
	def IsLxdeRunning():
		""" Returns whether lxde is running
		"""
		try:
			AmsEnvironment.__lxdeRunning
		except:
			AmsEnvironment.__lxdeRunning = AmsEnvironment.__isLxdeRunning()
		return AmsEnvironment.__lxdeRunning
	@staticmethod
	def Scan():
		""" Adds system paths required to import modules in the contrib folder
		"""
		try:
			AmsEnvironment.__scanned
		except:
			AmsEnvironment.__scanned = True
			vendors = AmsEnvironment.Vendors()
			if (any(vendors)):
				for v in vendors:
					vpath = os.path.join(AmsEnvironment.ContribPath(), v)
					mods = os.listdir(vpath)
					mods = [ x for x in mods if os.path.isdir(os.path.join(vpath, x)) ]
					for m in mods:
						sys.path.append(os.path.join(vpath, m))
	@staticmethod
	def EnableErrorLogging():
		logpath = os.path.join(AmsEnvironment.FilePath(),'logs')
		if (not os.path.exists(logpath)):
			os.makedirs(logpath)
		logging.basicConfig(filename=os.path.join(AmsEnvironment.FilePath(),'logs','exception.log'),filemode='a',level=logging.DEBUG, format= '%(asctime)s - %(levelname)s - %(message)s')
		AmsEnvironment.logger = logging.getLogger('amslogger')
		sys.excepthook = AmsEnvironment.errorHandler
	@staticmethod
	def EnableOutputLogging():
		AmsEnvironment._old_stdout = sys.stdout
		AmsEnvironment._old_stderr = sys.stderr
		AmsEnvironment.outlogger = OutLogger(AmsEnvironment._old_stdout, AmsEnvironment._old_stderr, os.path.join(AmsEnvironment.FilePath(),'logs'))
		sys.stdout = AmsEnvironment.outlogger
		sys.stderr = AmsEnvironment.outlogger
	@staticmethod
	def outputHandler(value):
		AmsEnvironment.logger.debug(value)
	@staticmethod
	def errorHandler(type, value, tb):
		AmsEnvironment.logger.exception("Uncaught exception: {0}".format(str(value)))
	@staticmethod
	def __extract_function_name():
		tb = sys.exc_info()[-1]
		stk = traceback.extract_tb(tb, 1)
		fname = stk[0][3]
		return fname
	def LogException(e):
		logging.error(
		"Function {function_name} raised {exception_class} ({exception_docstring}): {exception_message}".format(
		function_name = AmsEnvironment.__extract_function_name(), #this is optional
		exception_class = e.__class__,
		exception_docstring = e.__doc__,
		exception_message = e.message))
	@staticmethod
	def __isLxdeRunning():
		""" Utility
		"""
		if(not 'console' in AmsEnvironment.Terminal()):
			#not running from rc.local
			for l in AmsEnvironment.__pgrepX().split('\n'):
				match = AmsEnvironment.patterns['pid'].match(l)
				if(match):
					return True
		return False
	@staticmethod
	def __pgrepX():
		""" Utility
		"""
		p = Popen(['pgrep', 'X'], stdout=PIPE)
		o = p.communicate()[0]
		if(p.returncode == 0):
			return o
		return ''
## Custom StdOut handler to copy ouput to a log file.
class OutLogger(StringIO):
	def __init__(self, old_stdout, old_stderr, logpath, useold = True):
		""" Initializes the Logger object
		Extends StringIO in order to capture stdout and stderr
		
		@param parent
		@param gui
		@param options
		"""
		StringIO.__init__(self) #overriding object must implement StringIO
		self.logpath = logpath
		if (not os.path.exists(self.logpath)):
			os.makedirs(self.logpath)
		self.logfile = os.path.join(self.logpath, 'output.log')
		self.useold = useold
		self.old_stdout = old_stdout
		self.old_stderr = old_stderr
	def write(self, value):
		''' capture and reverse console output
		'''
		try:
			StringIO.write(self,value)
			f = open(self.logfile, 'a')
			f.write(value)
			f.close()
		except Exception as e:
			pass
		if(self.useold):
				self.old_stdout.write(value) #repeat to command line
AmsEnvironment.Scan()