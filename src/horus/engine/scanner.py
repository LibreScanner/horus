#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: March 2014                                                      #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>                    #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
# GNU General Public License for more details.                          #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>.  #
#                                                                       #
#-----------------------------------------------------------------------#

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v3 http://www.gnu.org/licenses/gpl.html"

import Queue
import threading

import datetime

from horus.engine.core import *
from horus.engine.camera import *
from horus.engine.device import *

from horus.util.singleton import *

from horus.util.profile import *

@Singleton
class Scanner:
	"""Scanner class. For managing scanner"""

	def __init__(self):
		""" """
		self.isConnected = False
		self.isRunning = False

		self.useLeftLaser = True
		self.useRightLaser = False

		self.moveMotor = True
		self.generatePointCloud = True

		self.core = Core()

		self.theta = 0
		self.imageQueue = Queue.Queue(1000)
		self.pointCloudQueue = Queue.Queue(10000)

	def initialize(self, cameraId=0, serialName="/dev/ttyACM0", baudRate=9600, degrees=0.45):
		""" """
		self.degrees = degrees
		self.core.setDegrees(degrees)
		self.camera = Camera(cameraId)
		self.device = Device(serialName, baudRate)

	def connect(self):
		""" """
		if self.camera.connect():
			if self.device.connect():
				self.isConnected = True
			else:
				self.camera.disconnect()
				self.isConnected = False
		else:
			self.isConnected = False
		return self.isConnected
		
	def disconnect(self):
		""" """		
		self.camera.disconnect()
		self.device.disconnect()
		self.isConnected = False
		return True # Fake
		
	def start(self):
		""" """
		self.captureFlag = True
		self.processFlag = True
		
		self.t1 = threading.Thread(target=self.captureThread)
		self.t2 = threading.Thread(target=self.processThread)
		
		self.t1.daemon = True
		self.t2.daemon = True
		
		self.t1.start()
		self.t2.start()

		self.isRunning = True
		
	def stop(self):
		""" """
		if self.isRunning:
			self.captureFlag = False
			self.processFlag = False
			
			self.t1.shutdown = True
			self.t2.shutdown = True
			
			#self.t1.join()
			self.t2.join()

			self.isRunning = False

	def captureThread(self):
		""" """
		#-- Initialize angle
		self.theta = 0

		if self.moveMotor:
			self.device.setSpeedMotor(1)
			self.device.enable()
		else:
			self.device.disable()

		while self.captureFlag:
			begin = datetime.datetime.now()

			#-- Get images

			if self.useLeftLaser:
				self.device.setLeftLaserOff()
			if self.useRightLaser:
				self.device.setRightLaserOff()
			imgRaw = self.camera.captureImage(flush=True, flushValue=2)

			if self.useLeftLaser:
				self.device.setLeftLaserOn()
				imgLas = self.camera.captureImage(flush=True, flushValue=2)

			if self.useRightLaser:
				self.device.setRightLaserOn()
				imgLas = self.camera.captureImage(flush=True, flushValue=2)

			#-- Move motor
			if self.moveMotor:
				self.device.setRelativePosition(self.degrees)
				self.device.setMoveMotor()
				time.sleep(0.1)
			else:
				time.sleep(0.2)
			
			#-- Put images into the queue
			self.imageQueue.put((imgRaw, imgLas))
			
			if self.generatePointCloud:
				#-- Check stop condition
				self.theta += self.degrees
				if abs(self.theta) >= 360:
					self.stop()
			
			end = datetime.datetime.now()
			print "Capture: {0}. Theta: {1}".format(end - begin, self.theta)

		self.device.setLeftLaserOff()
		self.device.setRightLaserOff()
		self.device.disable()

	def processThread(self):
		""" """
		while self.processFlag:

			#-- Get images
			images = self.imageQueue.get()
			self.imageQueue.task_done()

			begin = datetime.datetime.now()

			#-- Generate Point Cloud
			points, colors = self.core.getPointCloud(images[0], images[1])

			if self.generatePointCloud:
				#-- Put point cloud into the queue
				self.pointCloudQueue.put((points, colors))

			end = datetime.datetime.now()
			
			print "Process: {0}. Theta = {1}".format(end - begin, self.theta)

		"""import numpy as np
		np.set_printoptions(threshold=np.nan)
		uvPointCloud = str((self.core.uCoordinates, self.core.vCoordinates))
		putProfileSetting('uv_left_pointcloud', uvPointCloud)"""

	def isPointCloudQueueEmpty(self):
		return self.pointCloudQueue.empty()
		
	def getPointCloudIncrement(self):
		""" """
		if not self.isPointCloudQueueEmpty():
			pc = self.pointCloudQueue.get_nowait()
			if pc != None:
				self.pointCloudQueue.task_done()
			return pc
		else:
			return None