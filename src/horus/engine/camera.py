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
# This program is free software: you can redibute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# This program is dibuted in the hope that it will be useful,       #
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

import cv2, platform
from horus.util import profile

class Camera:
	""" """

	def __init__(self, cameraId=0):
		""" """
		print ">>> Initializing camera ..."
		print " - Camera ID: {0}".format(cameraId)
		self.cameraId = cameraId
		self.isConnected=False
		print ">>> Done"

		#todo put these lists in preferences
		self.framerates = [30,25,20,15,10,5]
		self.resolutions = [(1280,960),(1184,656),(1024,576),(960,720),(960,544),(864,480),(800,600),(800,448),(800,448),(752,416),(640,360),(544,288),(432,240),(544,288),(432,240),(352,288),(320,240),(176,144),(160,120)]
		self.system=platform.system()

		self.fps=self.framerates[profile.getProfileSettingInteger('framerate_value')]
		self.width,self.height=self.resolutions[profile.getProfileSettingInteger('resolution_value')]
		if self.system=='Linux':
			self.maxBrightness=255.
			self.maxContrast=255.
			self.maxSaturation=255.
			self.maxExposure=10000.
		else:
			print "Operative system: ",self.system,platform.release()
			self.maxBrightness=1.
			self.maxContrast=1.
			self.maxSaturation=1.
			self.maxExposure=-9/200.

	def connect(self):
		""" """
		print ">>> Connecting camera ..."
		self.isConnected=True
		self.capture = cv2.VideoCapture(self.cameraId)
		self.setCameraControlFromProfile()
		##
		self.captureImage(flush=True)
		##
		print ">>> Done"
		
	def disconnect(self):
		""" """
		print ">>> Disconnecting camera ..."
		self.capture.release()
		self.isConnected=False
		print ">>> Done"

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

	def setBrightness(self,value):
		if self.isConnected:
			value=int(value)/self.maxBrightness
			self.capture.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS,value)

	def setContrast(self,value):
		if self.isConnected:
			value=int(value)/self.maxContrast
			self.capture.set(cv2.cv.CV_CAP_PROP_CONTRAST,value)


	def setSaturation(self,value):
		if self.isConnected:
			value=int(value)/self.maxSaturation
			self.capture.set(cv2.cv.CV_CAP_PROP_SATURATION,value)


	def setExposure(self,value):
		if self.isConnected:
			value=int(value)/self.maxExposure
			self.capture.set(cv2.cv.CV_CAP_PROP_EXPOSURE,value)

	def setFps(self,value):
		if self.isConnected:
			self.fps=self.framerates[value]
			self.capture.set(cv2.cv.CV_CAP_PROP_FPS,self.fps)

	def setResolution(self,value):
		if self.isConnected:
			width,height=self.resolutions[value]

			self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,width)
			self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,height)

			actualWidth=self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
			actualHeight=self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

	def setCameraControl(self,brightness,contrast,saturation,exposure,fps,resolution):
		self.setBrightness(brightness)
		self.setContrast(contrast)
		self.setSaturation(saturation)
		self.setExposure(exposure)
		self.setFps(fps)
		self.setResolution(resolution)

	def setCameraControlFromProfile(self):

		brightness=profile.getProfileSettingInteger('brightness_value')
		self.setBrightness(brightness)
		
		contrast=profile.getProfileSettingInteger('contrast_value')
		self.setContrast(contrast)
		
		saturation=profile.getProfileSettingInteger('saturation_value')
		self.setSaturation(saturation)
		
		exposure=profile.getProfileSettingInteger('exposure_value')
		self.setExposure(exposure)
		framerate=profile.getProfileSettingInteger('framerate_value')
		self.setFps(framerate)
		
		resolution=profile.getProfileSettingInteger('resolution_value')
		self.setResolution(resolution)