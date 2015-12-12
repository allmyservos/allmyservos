bl_info = {
	"name": "AllMyServos",
	"category": "Robotics",
	"author": "Luke Hynek",
	"version": (0, 7),
	"description": "Send live commands to a robot running AllMyServos and export key-framed animations.",
}

import bpy, sys, os, threading, xmlrpc.client, json, time, copy
from bpy.types import Header, Menu, Panel, Operator
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import StringProperty, BoolProperty, IntProperty
from mathutils import Matrix, Vector
from math import acos, degrees
from xml.dom import minidom
from xml.dom.minidom import Document

#blender ui

class RoboticsPanel(Panel):
	"""Interface for AllMyServos functionality"""
	bl_label = "AllMyServos"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "render"

	def draw(self, context):
		'''Sets up the panel UI'''
		layout = self.layout
		scene = context.scene
		rd = context.scene.render
		row = layout.row()
		row.label(text="RPC Config")
		row = layout.row()
		row.prop(scene, 'commandhost')
		row = layout.row()
		row.prop(scene, 'commandport')
		row = layout.row()
		row.prop(scene, 'commandusername')
		row = layout.row()
		row.prop(scene, 'commandpassword')
		row = layout.row()
		row.label(text="Servo Config")
		row.operator('ams.download_config')
		row = layout.row()
		row.label(text="%s servos loaded" % len(scene.servoconfig.servos))
		row = layout.row()
		row.label(text="Live Commands")
		row = layout.row()
		row.operator('ams.toggle_live', text='Enabled' if ToggleLiveCommands.enabled == True else 'Disabled')
		split = layout.split()
		col = split.column(align=True)
		col.label(text="Export Motion:")
		col.prop(scene, "frame_start")
		col.prop(scene, "frame_end")
		col.prop(scene.render,"fps")
		row = layout.row()
		row.label(text="Upload Motion")
		col = layout.column(align=True)
		col.prop(scene, "motionname")
		row = layout.row()
		row.operator('ams.upload_motion', text="Upload")

class UploadMotion(Operator):
	bl_idname = "ams.upload_motion"
	bl_label = "Upload motion"
	bl_options = {'REGISTER', 'UNDO'}
	def execute(self, context):
		'''constructs a motion dict and uploads it'''
		if bpy.context.scene.motionname == '':
			self.report({'WARNING'}, "Motion name cannot be empty.")
			return {'FINISHED'}
		try:
			int(bpy.context.scene.motionname)
		except:
			pass
		else:
			self.report({'WARNING'}, "Motion name cannot be an integer.")
			return {'FINISHED'}
		config = context.scene.servoconfig
		if(len(config.servos) > 0):
			initial_frame = bpy.context.scene.frame_current
			first_frame = bpy.context.scene.frame_start
			cursor_frame = bpy.context.scene.frame_start
			end_frame = bpy.context.scene.frame_end
			self.meta = {
				'name': bpy.context.scene.motionname,
				'fps': bpy.context.scene.render.fps,
				'keyframes': []
			}
			while(cursor_frame <= end_frame):
				bpy.context.scene.frame_set(cursor_frame)
				kf = {
					'time': int(round((float(cursor_frame - first_frame))*(1000/int(self.meta['fps'])),0)),
					'instructions': []
				}
				for v in config.servos.values():
					la = get_local_angle(v['boneArmature'],v['boneName'],v['boneAxis'])
					fa = int(v['angle'] + la)
					kf['instructions'].append({
						'channel': v['channel'],
						'angle': fa,
						'disabled': False
					})
				self.meta['keyframes'].append(kf)
				cursor_frame += 1
			res = self.upload()
			if (res == 'exists'):
				self.report({'WARNING'}, "A motiion with that name already exists in this specification.")
				return
			elif (res != 'uploaded'):
				self.report({'WARNING'}, "Upload failed: "+str(res))
				return
			self.report({'INFO'}, "Uploaded motion: %s" % bpy.context.scene.motionname)
		else:
			self.report({'WARNING'}, "Unable to upload motion. Config missing.")
		return {'FINISHED'}
	def upload(self):
		self.url = 'https://{0}:{1}@{2}:{3}'.format(bpy.context.scene.commandusername, bpy.context.scene.commandpassword, bpy.context.scene.commandhost, bpy.context.scene.commandport)
		self.server = xmlrpc.client.ServerProxy(self.url)
		return self.server.uploadMotion(self.safeName(str(self.meta['name'])), json.dumps(self.meta))
	def safeName(self, name):
		name = str(name).lower()
		name = name.replace(' ', '-')
		return name
class DownloadConfig(Operator):
	bl_idname = "ams.download_config"
	bl_label = "Download Config"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		context.scene.servoconfig.configure(
			context.scene.servoconfig,
			context.scene.commandhost,
			context.scene.commandport,
			context.scene.commandusername,
			context.scene.commandpassword
		)
		context.scene.servoconfig.load()
		self.report({'INFO'}, "%s servos downloaded" % len(context.scene.servoconfig.servos))
		return {'FINISHED'}
class ToggleLiveCommands(Operator):
	"""Turn live commands on or off"""
	bl_idname = "ams.toggle_live"
	bl_label = "Enable"
	bl_options = {'REGISTER', 'UNDO'}
	
	enabled = BoolProperty(name="Enabled", default=False)
	def execute(self, context):
		self.__class__.enabled = False if self.__class__.enabled == True else True
		if(self.__class__.enabled == True):
			context.scene.livecommand.configure(
				context.scene.servoconfig,
				context.scene.commandhost,
				context.scene.commandport,
				context.scene.commandusername,
				context.scene.commandpassword
			)
			context.scene.livecommand.stopped = False
			self.report({'INFO'}, "Live commands have been enabled")
		else:
			context.scene.livecommand.stopped = True
			self.report({'INFO'}, "Live commands have been disabled")
		return {'FINISHED'}

class RobotProperties(bpy.types.PropertyGroup):
	@classmethod
	def register(cls):
		bpy.types.Scene.commandhost = StringProperty(name="Host", default="192.168.0.152")
		bpy.types.Scene.commandport = IntProperty(name="Port", default=9000)
		bpy.types.Scene.commandusername = StringProperty(name="Username", default="remoteuser")
		bpy.types.Scene.commandpassword = StringProperty(name="Password", default="")
		bpy.types.Scene.motionname = StringProperty(name="Motion Name", default="newmotion")
		bpy.types.Scene.servoconfig = RobotConfig()
		bpy.types.Scene.livecommand = LiveCommand()
	def unregister(cls):
		del bpy.types.Scene.commandhost
		del bpy.types.Scene.commandport
		del bpy.types.Scene.commandusername
		del bpy.types.Scene.commandpassword
		del bpy.types.Scene.motionname
		del bpy.types.Scene.servoconfigfile
		del bpy.types.Scene.servoconfig
		del bpy.types.Scene.livecommand

#robot config

class RobotConfig:
	def __init__(self):
		self.servos = {}
	def configure(self, config, host, port, username, password):
		self.config = config
		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.url = 'https://{0}:{1}@{2}:{3}'.format(self.username, self.password, self.host, self.port)
		if(self.host != None and self.port != None and self.username != None, self.password != None):
			self.server = xmlrpc.client.ServerProxy(self.url)
			return True
		return False
	def load(self):
		try:
			self.servos = self.server.getServoConfig()
		except xmlrpc.client.ProtocolError as e:
			print(e)

#robot live command

class LiveCommand(threading.Thread):
	def __init__(self, stopped = True):
		threading.Thread.__init__(self)
		self.setName('LiveCommand')
		self.interval = 0.1
		self.servocount = 0
		self.servos = {}
		self.server, self.config, self.host, self.port, self.username, self.password = None, None, None, None, None, None
		self.stopped = stopped
		self.relaxed = True
		self.start()
	def configure(self, config, host, port, username, password):
		self.config = config
		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.url = 'https://{0}:{1}@{2}:{3}'.format(self.username, self.password, self.host, self.port)
		self.servocount = len(self.config.servos)
		self.servos = self.config.servos
		if(self.servocount > 0 and self.host != None and self.port != None and self.username != None, self.password != None):
			self.server = xmlrpc.client.ServerProxy(self.url)
			return True
		return False
	def run(self):
		while True:
			if(not self.stopped):	
				if(self.servocount > 0 and self.server != None):
					self.relaxed = False
					command = {}
					for k, v in self.servos.items():
						relative = get_local_angle(v['boneArmature'],v['boneName'],v['boneAxis'])
						command[int(v['channel'])] = int(v['angle']) + int(relative)
					self.server.liveCommand(json.dumps(command))
			elif(not self.relaxed):
				self.relaxed = True
				self.server.relax()
			time.sleep(self.interval)

#bone helpers

def get_pose_matrix_in_other_space(mat, pose_bone):
	""" Returns the transform matrix relative to pose_bone's current
	transform space. In other words, presuming that mat is in
	armature space, slapping the returned matrix onto pose_bone
	should give it the armature-space transforms of mat.
	TODO: try to handle cases with axis-scaled parents better.
	"""
	rest = pose_bone.bone.matrix_local.copy()
	rest_inv = rest.inverted()
	if pose_bone.parent:
		par_mat = pose_bone.parent.matrix.copy()
		par_inv = par_mat.inverted()
		par_rest = pose_bone.parent.bone.matrix_local.copy()
	else:
		par_mat = Matrix()
		par_inv = Matrix()
		par_rest = Matrix()
	# Get matrix in bone's current transform space
	smat = rest_inv * (par_rest * (par_inv * mat))
	# Compensate for non-local location
	#if not pose_bone.bone.use_local_location:
	# loc = smat.to_translation() * (par_rest.inverted() * rest).to_quaternion()
	# smat.translation = loc
	return smat

def get_local_pose_matrix(pose_bone):
	""" Returns the local transform matrix of the given pose bone.
	"""
	return get_pose_matrix_in_other_space(pose_bone.matrix, pose_bone)
def get_local_angle(armatureName, boneName, axis):
	""" Returns the local angle of the given pose bone and axis. Integer rounded
	"""
	pb = bpy.data.objects[armatureName].pose.bones[boneName]
	mat = get_local_pose_matrix(pb)
	x,y,z = mat.to_euler()
	angle = x
	if(axis.lower() == 'y'):
		angle = y
	elif(axis.lower() == 'z'):
		angle = z
	return round(degrees(angle))

if __name__ == "__main__":  # only for live edit.
	bpy.utils.register_module(__name__)