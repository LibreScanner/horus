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

class Camera:
	""" """

	def __init__(self, cameraId=0):
		""" """
		print ">>> Initializing camera ..."
		print " - Camera ID: {0}".format(cameraId)
		self.cameraId = cameraId
		print ">>> Done"

		self.width = 1280
		self.height = 960

		self.fps=30 #TODO put al this in preferences

	def connect(self):
		""" """
		print ">>> Connecting camera ..."
		self.capture = cv2.VideoCapture(self.cameraId)
		self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.width)
		self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.height)
		##
		self.captureImage()
		##
		print ">>> Done"
		
	def disconnect(self):
		""" """
		print ">>> Disconnecting camera ..."
		self.capture.release()
		print ">>> Done"

	def captureImage(self, mirror=False):
		""" If mirror is set to True, the image will be displayed as a mirror, 
		otherwise it will be displayed as the camera sees it"""
		#for i in range(0,2):
		#	self.capture.read()
		ret, image = self.capture.read()

		if ret:
			image = cv2.transpose(image)
			if not mirror:
				image = cv2.flip(image, 1)
			return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		else:
			return None

	def setBrightness(self,value):
		value=int(value)/255.
		self.capture.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS,value)

	def setContrast(self,value):
		value=int(value)/255.
		self.capture.set(cv2.cv.CV_CAP_PROP_CONTRAST,value)

	def setSaturation(self,value):
		value=int(value)/255.
		self.capture.set(cv2.cv.CV_CAP_PROP_SATURATION,value)

	def setExposure(self,value):
		value=int(value)/10000.
		self.capture.set(cv2.cv.CV_CAP_PROP_EXPOSURE,value)

	def setFps(self,value):
		self.fps=value
		self.capture.set(cv2.cv.CV_CAP_PROP_FPS,value)
		

	def setResolution(self,value):
		value=value.replace('(','')
		value=value.replace(')','')	
		value=value.split(',')
		width,height=int(value[0]),int(value[1])

		self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,width)
		self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,height)

		actualWidth=self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
		actualHeight=self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
