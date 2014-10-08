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

import cv2
import math
import platform

class Camera:
	""" """
	def __init__(self, cameraId=0):
		""" """
		print ">>> Initializing camera ..."
		print " - Camera ID: {0}".format(cameraId)
		self.cameraId = cameraId

		self._initialize()

	def _initialize(self):
		self.isConnected = False

		self.capture = None
		
		self.fps = 30
		self.width = 800
		self.height = 600
		self.useDistortion = False

		self.cameraMatrix = None
		self.distortionVector = None
		self.distCameraMatrix = None

		if platform.system() == 'Windows':
			self.maxBrightness = 1.
			self.maxContrast = 1.
			self.maxSaturation = 1.
		else:
			self.maxBrightness = 255.
			self.maxContrast = 255.
			self.maxSaturation = 255.
			self.maxExposure = 10000.

	def connect(self):
		""" """
		print ">>> Connecting camera ..."
		self.capture = cv2.VideoCapture(self.cameraId)
		if self.capture.isOpened():
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

	def captureImage(self, mirror=False, flush=False, flushValue=1):
		""" If mirror is set to True, the image will be displayed as a mirror,
		otherwise it will be displayed as the camera sees it"""
		if self.isConnected:
			if flush:
				for i in range(0, flushValue):
					self.capture.grab()
			ret, image = self.capture.read()
			if ret:
				if self.useDistortion and \
				   self.cameraMatrix is not None and \
				   self.distortionVector is not None and \
				   self.distCameraMatrix is not None:
					mapx, mapy = cv2.initUndistortRectifyMap(self.cameraMatrix, self.distortionVector,
															 R=None, newCameraMatrix=self.distCameraMatrix,
															 size=(self.width, self.height), m1type=5)
					image = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)
				image = cv2.transpose(image)
				if not mirror:
					image = cv2.flip(image, 1)
				return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
			else:
				return None
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
			if platform.system() == 'Windows':
				value = int(-math.log(value)/math.log(2))
			else:
				value = int(value) / self.maxExposure
			self.capture.set(cv2.cv.CV_CAP_PROP_EXPOSURE, value)

	def setFrameRate(self, value):
		if self.isConnected:
			self.fps = value
			self.capture.set(cv2.cv.CV_CAP_PROP_FPS, value)

	def _setWidth(self, value):
		if self.isConnected:
			self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, value)

	def _setHeight(self, value):
		if self.isConnected:
			self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, value)	

	def _updateResolution(self):
		if self.isConnected:
			self.width = int(self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
			self.height = int(self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

	def setResolution(self, width, height):
		self._setWidth(width)
		self._setHeight(height)
		self._updateResolution()

	def setUseDistortion(self, value):
		self.useDistortion = value

	def setIntrinsics(self, cameraMatrix, distortionVector):
		self.cameraMatrix = cameraMatrix
		self.distortionVector = distortionVector
		self.distCameraMatrix = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.distortionVector, (self.width,self.height), alpha=1)[0]

	def getExposure(self):
		if self.isConnected:
			value = self.capture.get(cv2.cv.CV_CAP_PROP_EXPOSURE)
			if platform.system() == 'Windows':
				value = 2**-value
			else:
				value *= self.maxExposure
			return value