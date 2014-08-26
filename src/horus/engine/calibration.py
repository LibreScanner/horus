#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: August 2014                                                     #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>   	                #
#         Carlos Crespo <carlos.crespo@bq.com>                          #
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
import numpy as np
from scipy import optimize  

from horus.util import profile
from horus.util.singleton import *

from horus.engine.scanner import *

@Singleton
class Calibration:

	def __init__(self):
		self.scanner = Scanner.Instance()

	def performCameraIntrinsicsCalibration(self):
		pass

	def performLaserTriangulationCalibration(self):
		if self.scanner.isConnected:

			u1L = u2L = u1R = u2R = None

			device = self.scanner.device
			camera = self.scanner.camera

			##-- Left Laser

			#-- Get images
			device.setLeftLaserOff()
			imgRawL = camera.captureImage(flush=True, flushValue=2)
			device.setLeftLaserOn()
			imgLasL = camera.captureImage(flush=True, flushValue=2)
			device.setLeftLaserOff()

			height, width, depth = imgRawL.shape
			imgLineL = np.zeros((height,width,depth), np.uint8)

			diffL = cv2.subtract(imgLasL, imgRawL)
			rL,gL,bL = cv2.split(diffL)
			imgGrayL = cv2.merge((rL,rL,rL))
			edgesL = cv2.threshold(rL, 30.0, 255.0, cv2.THRESH_BINARY)[1]
			edges3L = cv2.merge((edgesL,edgesL,edgesL))
			linesL = cv2.HoughLines(edgesL, 1, np.pi/180, 200)

			if linesL is not None:
				rho, theta = linesL[0][0]

				#-- Draw line
				a = np.cos(theta)
				b = np.sin(theta)
				x0 = a*rho
				y0 = b*rho
				x1 = int(x0 + 1000*(-b))
				y1 = int(y0 + 1000*(a))
				x2 = int(x0 - 1000*(-b))
				y2 = int(y0 - 1000*(a))
				cv2.line(imgLineL,(x1,y1),(x2,y2),(255,255,255),3)

				#-- Calculate coordinates
				u1L = rho / np.cos(theta)
				u2L = u1L - height * np.tan(theta)

			##-- Right Laser

			#-- Get images
			imgRawR = imgRawL
			device.setRightLaserOn()
			imgLasR = camera.captureImage(flush=True, flushValue=2)
			device.setRightLaserOff()

			height, width, depth = imgRawR.shape
			imgLineR = np.zeros((height,width,depth), np.uint8)

			diffR = cv2.subtract(imgLasR, imgRawR)
			rR,gR,bR = cv2.split(diffR)
			imgGrayR = cv2.merge((rR,rR,rR))
			edgesR = cv2.threshold(rR, 30.0, 255.0, cv2.THRESH_BINARY)[1]
			edges3R = cv2.merge((edgesR,edgesR,edgesR))
			linesR = cv2.HoughLines(edgesR, 1, np.pi/180, 200)

			if linesR is not None:
				rho, theta = linesR[0][0]

				#-- Draw line
				a = np.cos(theta)
				b = np.sin(theta)
				x0 = a*rho
				y0 = b*rho
				x1 = int(x0 + 1000*(-b))
				y1 = int(y0 + 1000*(a))
				x2 = int(x0 - 1000*(-b))
				y2 = int(y0 - 1000*(a))
				cv2.line(imgLineR,(x1,y1),(x2,y2),(255,255,255),3)

				#-- Calculate coordinates
				u1R = rho / np.cos(theta)
				u2R = u1R - height * np.tan(theta)

			return (((u1L, u2L), (u1R, u2R)),
					((imgLasL, imgGrayL, edges3L, imgLineL), (imgLasR, imgGrayR, edges3R, imgLineR)))

	def performPlatformExtrinsicsCalibration(self):
		pass