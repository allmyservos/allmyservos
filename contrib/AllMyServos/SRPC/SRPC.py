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
import socket, os, time, uuid, SocketServer, BaseHTTPServer, SimpleHTTPServer, SimpleXMLRPCServer, inspect, json
from Scheduler import *
from Setting import *
from OpenSSL import SSL
from base64 import b64decode
from SSLManager import *
from Motion import *
from Notifier import Notifier
from Specification import Specification

## SSL Secured Remote Procedure Call Server
class SRPCServer(object):
	def __init__(self, motionScheduler = None, specification = None, scheduler = None):
		""" Initializes the SRPCServer object
		Args passed to this object allow the SRPC server to share these objects
		All requests are subject to username and password authentication
		and connection are made over HTTPS.
		
		@param motionScheduler
		@param specification
		@param scheduler
		"""
		if(motionScheduler == None):
			self.motionScheduler = MotionScheduler.GetInstance()
		else:
			self.motionScheduler = motionScheduler
		if(specification == None):
			self.specification = Specification.GetInstance()
		else:
			self.specification = specification
		if(scheduler == None):
			self.scheduler = Scheduler.GetInstance()
		else:
			self.scheduler = scheduler
		self.notifier = Notifier()
		self.sslmanager = SSLManager()
		self.server_address = (Setting.get('rpc_server_hostname', '0.0.0.0'), Setting.get('rpc_server_port', 9000))
		try:
			self.server = SecureXMLRPCServer(self.server_address, SecureXMLRpcRequestHandler, Setting.get('rpc_server_log', False), self.sslmanager.key, self.sslmanager.certificate)
		except (socket.error):
			old = self.server_address[0]
			Setting.set('rpc_server_hostname', '0.0.0.0')
			self.server_address = (Setting.get('rpc_server_hostname', '0.0.0.0'), Setting.get('rpc_server_port', 9000))
			self.server = SecureXMLRPCServer(self.server_address, SecureXMLRpcRequestHandler, Setting.get('rpc_server_log', False), self.sslmanager.key, self.sslmanager.certificate)
			self.notifier.addNotice('Unable to bind to RPC Hostname: {}. Reset to 0.0.0.0.'.format(old), 'warning')
		self.exposed = Exposed(self.specification, self.motionScheduler)
		self.server.register_instance(self.exposed)
		self.scheduler.addTask('srpc_server', self.serve, 0.2, stopped=(not Setting.get('rpc_autostart', False)))
	def serve(self):
		""" handle a request
		"""
		self.server.handle_request()
	def start(self):
		""" start the SRPC service
		"""
		self.scheduler.startTask('srpc_server')
	def stop(self):
		""" stop the SRPC service
		"""
		self.scheduler.stopTask('srpc_server')
	def isRunning(self):
		""" is the SRPC service running
		"""
		return self.scheduler.isRunning('srpc_server')
	def listMethods(self):
		""" list available endpoints
		"""
		return self.exposed.listMethods()
## public methods of the Exposed class become endpoints for the RPC server
class Exposed:
	def __init__(self, specification, motionScheduler):
		""" Initiializes the Exposed object
		The public methods of this class are automatically made available
		as endpoints of the RPC service
		"""
		import string
		self.python_string = string
		self.specification = specification
		self.channelindex = {}
		for s in self.specification.servos.values():
			self.channelindex[int(s.channel)] = s
		self.motionScheduler = motionScheduler
	def listMethods(self):
		""" gets a list of exposed functions
		"""
		members = inspect.getmembers(self, lambda a:inspect.isroutine(a))
		l = []
		for m in members:
			if(not m[0].startswith('__')):
				l.append(m[0])
		return l
	def add(self, x, y):
		""" adds two numbers
		"""
		return x + y
	def mult(self,x,y):
		""" multiplies two numbers
		"""
		return x*y
	def div(self,x,y):
		""" divides two numbers
		"""
		return x//y
	def relax(self):
		""" relax all servos
		"""
		for s in self.specification.servos.values():
			s.disabled = True
			s.setServoAngle()
		return True
	def liveCommand(self, s):
		""" sync servos with this live command
		s is a json string containing a dict of channels and angles. these instructions are applied immediately.
		
		@param s
		"""
		hitcount = 0
		if(isinstance(s, (str, unicode))):
			s = json.loads(s)
			for k, v in s.iteritems():
				self.channelindex[int(k)].angle = v
				self.channelindex[int(k)].disabled = False
				self.channelindex[int(k)].setServoAngle()
				hitcount += 1
		return hitcount
	def listMotions(self):
		"""get a list of all existing motions
		"""
		return self.specification.motions
	def listChains(self):
		"""get a list of all chains"""
		return self.specification.chains 
	def triggerMotion(self, id, slow = False):
		""" trigger a motion
		id - index of a motion. queues this motion for execution
		slow - enable slow motion
		
		@param id str a 
		@param slow bool
		"""
		self.motionScheduler.triggerMotion(id)
		return 'motion trigger'
	def triggerChain(self, id):
		"""
		id - index of a chain. queues this chain for execution. resubmit while looping or the chain will stop.
		
		@param id
		"""
		self.motionScheduler.triggerChain(id)
		return 'chain triggered'
	def getServoConfig(self):
		""" gets the current servo configuration
		"""
		return self.specification.jsonData['servos']
	def uploadMotion(self, name, meta):
		""" receives motion data
		"""
		if (name in [x.jsonData['name'] for x in self.specification.motions.values()]):
			return 'exists'
		meta = json.loads(meta)
		if (not 'name' in meta.keys()):
			return 'missing-name'
		if (not 'fps' in meta.keys()):
			return 'missing-fps'
		if (not 'keyframes' in meta.keys()):
			return 'missing-keyframes'
		mo = Motion()
		mo.jsonData = meta
		mo.save()
		self.specification.motions[mo.jbIndex] = mo
		self.specification.save()
		return 'uploaded'
## Extends HTTPServer with SSL support
class SecureXMLRPCServer(BaseHTTPServer.HTTPServer,SimpleXMLRPCServer.SimpleXMLRPCDispatcher):
	def __init__(self, server_address, HandlerClass, logRequests=True, keyfile='key.pem', certfile='certificate.pem'):
		"""Secure XML-RPC server.
		It it very similar to SimpleXMLRPCServer but it uses HTTPS for transporting XML data.
		"""
		self.logRequests = logRequests
		
		try:
			SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self)
		except TypeError:
			# An exception is raised in Python 2.5 as the prototype of the __init__
			# method has changed and now has 3 arguments (self, allow_none, encoding)
			#
			SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self, False, None)

		SocketServer.BaseServer.__init__(self, server_address, HandlerClass)
		ctx = SSL.Context(SSL.SSLv23_METHOD)
		ctx.use_privatekey_file (keyfile)
		ctx.use_certificate_file(certfile)
		
		self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
														self.socket_type))
		try:
			self.server_bind()
			self.server_activate()
			self.ready = True
		except:
			self.ready = False
	def shutdown_request(self,request): pass
## Object for handling requests
class SecureXMLRpcRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
	def setup(self):
		"""Secure XML-RPC request handler class.
		It it very similar to SimpleXMLRPCRequestHandler but it uses HTTPS for transporting XML data.
		"""
		self.connection = self.request
		self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
		self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)
	def parse_request(self):
		""" triggers authentication
		"""
		if SimpleXMLRPCServer.SimpleXMLRPCRequestHandler.parse_request(self):
			if self.authenticate(self.headers):
				return True
			else:
				self.send_response(403)
				self.end_headers()
	def authenticate(self, headers):
		""" performs authentication
		"""
		try:
			(basic, _, encoded) = headers.get('Authorization').partition(' ')
			assert basic == 'Basic'
			(username, _, password) = b64decode(encoded).partition(':')
			assert username == Setting.get('rpc_server_username', 'remoteuser')
			assert password == Setting.get('rpc_server_password', str(uuid.uuid4()))
			return True
		except Exception as e:
			print(e)
			pass
		return False
	def do_POST(self):
		"""Handles the HTTPS POST request.
		It was copied out from SimpleXMLRPCServer.py and modified to shutdown the socket cleanly.
		"""
		try:
			# get arguments
			data = self.rfile.read(int(self.headers["content-length"]))
			# In previous versions of SimpleXMLRPCServer, _dispatch
			# could be overridden in this class, instead of in
			# SimpleXMLRPCDispatcher. To maintain backwards compatibility,
			# check to see if a subclass implements _dispatch and dispatch
			# using that method if present.
			response = self.server._marshaled_dispatch(
					data, getattr(self, '_dispatch', None)
				)
		except Exception, e: # This should only happen if the module is buggy
			# internal error, report as HTTP server error
			print("RPC Error %s:" % e.args[0])
			self.send_response(500)
			self.end_headers()
		else:
			# got a valid XML RPC response
			self.send_response(200)
			self.send_header("Content-type", "text/xml")
			self.send_header("Content-length", str(len(response)))
			self.end_headers()
			self.wfile.write(response)

			# shut down the connection
			self.wfile.flush()
			self.connection.shutdown() # Modified here!

if __name__ == '__main__':
	
	server = SRPCServer()

	# Here is the client for testing:
	import xmlrpclib

	server = xmlrpclib.Server('https://remoteuser:6392e0ad-3149-49c8-8324-81f9e4f72b42@127.0.0.1:9000')
	time.sleep(1)
	print server.add(1,2)
	print server.div(10,4)
	print(server.listMethods())
	print(server.liveCommand(json.dumps({ 0 : 100})))
	time.sleep(60)