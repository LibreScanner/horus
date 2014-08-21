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
# This program is free software: you can redibute it and/or modify      #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# This program is dibuted in the hope that it will be useful,           #
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

import cv2
import platform

class Camera:
	""" """
	def __init__(self, cameraId=0):
		""" """
		print ">>> Initializing camera ..."
		print " - Camera ID: {0}".format(cameraId)
		self.cameraId = cameraId

		self.isConnected = False

		self.fps = 30

		self.width = 800
		self.height = 600
		
		if platform.system()=='Linux':
			self.maxBrightness = 255.
			self.maxContrast = 255.
			self.maxSaturation = 255.
			self.maxExposure = 10000.
		else:
			print "Operative system: ",self.system,platform.release()
			self.maxBrightness = 1.
			self.maxContrast = 1.
			self.maxSaturation = 1.
			self.maxExposure = -9/200.

	def initialize(self, brightness, contrast, saturation, exposure, fps, width, height):
		self.setBrightness(brightness)
		self.setContrast(contrast)
		self.setSaturation(saturation)
		self.setExposure(exposure)
		self.setFps(fps)
		self.setWidth(width)
		self.setHeight(height)

	def connect(self):
		""" """
		print ">>> Connecting camera ..."
		self.capture = cv2.VideoCapture(self.cameraId)
		if self.capture.isOpened():
			self.captureImage(flush=True)
			print ">>> Done"
			self.isConnected = True
		else:
			print ">>> Error"
			self.isConnected = False
		return self.isConnected
		
	def disconnect(self):
		""" """
		print ">>> Disconnecting camera ..."
		if self.capture is not None:
			if self.capture.isOpened():
				self.capture.release()
			self.isConnected = False
		print ">>> Done"
		return True

	def captureImage(self, mirror=False, flush=False):
		""" If mirror is set to True, the image will be displayed as a mirror,
		otherwise it will be displayed as the camera sees it"""
		if flush:
			for i in range(0,2):
				self.capture.read()
		ret, image = self.capture.read()

		if ret:
			image = cv2.transpose(image)
			if not mirror:
				image = cv2.flip(image, 1)
			return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		else:
			return None

	def getResolution(self):
		return self.height, self.width #-- Inverted values because of transpose

	def setBrightness(self, value):
		if self.isConnected:
			value = int(value)/self.maxBrightness
			self.capture.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, value)

	def setContrast(self, value):
		if self.isConnected:
			value = int(value)/self.maxContrast
			self.capture.set(cv2.cv.CV_CAP_PROP_CONTRAST, value)

	def setSaturation(self, value):
		if self.isConnected:
			value = int(value)/self.maxSaturation
			self.capture.set(cv2.cv.CV_CAP_PROP_SATURATION, value)

	def setExposure(self, value):
		if self.isConnected:
			value = int(value)/self.maxExposure
			self.capture.set(cv2.cv.CV_CAP_PROP_EXPOSURE, value)

	def setFps(self, value):
		if self.isConnected:
			self.fps = value
			self.capture.set(cv2.cv.CV_CAP_PROP_FPS, value)

	def setWidth(self, value):
		if self.isConnected:
			self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, value)
			self.width = self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)

	def setHeight(self, value):
		if self.isConnected:
			self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, value)
			self.height = self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
