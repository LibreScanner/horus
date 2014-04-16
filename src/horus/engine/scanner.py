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

import wx

import Queue
import threading

import datetime

from horus.engine.core import *
from horus.engine.camera import *
from horus.engine.device import *

class Scanner(wx.PyControl):
	"""Scanner class. For managing scanner"""
	"""
	"""

	def __init__(self, parent):
		""" """
		wx.PyControl.__init__(self, parent)
		self.Hide()

		self.theta = 0
		self.imageQueue = Queue.Queue(1000)
		self.pointCloudQueue = Queue.Queue(10000)

	def initialize(self, cameraId=0, serialName="/dev/ttyACM0", degrees=0.45, delay=10000):
		""" """
		self.degrees = degrees
		self.core = Core(degrees)
		self.camera = Camera(cameraId)
		self.device = Device(serialName, degrees, delay)

	def connect(self):
		""" """
		self.camera.connect()
		return self.device.connect()
		
	def disconnect(self):
		""" """
		self.camera.disconnect()
		return self.device.disconnect()
		
	def getCore(self):
		""" """
		return self.core

	def getCamera(self):
		""" """
		return self.camera

	def getDevice(self):
		""" """
		return self.device
		
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
		
	def stop(self):
		""" """
		self.captureFlag = False
		self.processFlag = False
		
		self.t1.shutdown = True
		self.t2.shutdown = True
		
		#self.t1.join()
		self.t2.join()

	def captureThread(self):
		""" """
		#-- Initialize angle
		self.theta = 0
		
		self.device.enable()

		while self.captureFlag:
			begin = datetime.datetime.now()
			
			#-- Get images
			self.device.setLeftLaserOff()
			imgRaw = self.camera.captureImage()
			self.device.setLeftLaserOn()
			imgLas = self.camera.captureImage()

			#-- Move motor
			self.device.setMotorCW()
			time.sleep(0.06)

			#-- Get diff image
			imgDiff = self.core.getDiffImage(imgRaw, imgLas)

			#-- Put images into the queue
			self.imageQueue.put((imgRaw, imgDiff))
			
			#-- Check stop condition
			self.theta += self.degrees
			if self.theta >= 360:
				self.stop()
			
			end = datetime.datetime.now()
			print "Capture: {0}. Theta: {1}".format(end - begin, self.theta)

		self.device.disable()

	def processThread(self):
		""" """
		while self.processFlag:
			begin = datetime.datetime.now()

			#-- Get images
			images = self.imageQueue.get()
			self.imageQueue.task_done()

			#-- Generate Point Cloud
			points, colors = self.core.getPointCloud(images[0], images[1])

			#-- Put point cloud into the queue
			self.pointCloudQueue.put((points, colors))

			end = datetime.datetime.now()
			
			print "Process: {0}. Theta = {1}".format(end - begin, self.theta)

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