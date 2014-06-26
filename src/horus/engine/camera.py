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

		self.width = 640
		self.height = 480

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

	def captureImage(self,*mirror):
		""" If mirror is set to True, the image will be displayed as a mirror, 
		otherwise it will be displayed as the camera sees it"""
		#for i in range(0,2):
		#	self.capture.read()
		ret, image = self.capture.read()
		image=cv2.transpose(image)
		if mirror:
			pass
		else:
			image=cv2.flip(image,1)
		imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

		return imageRGB