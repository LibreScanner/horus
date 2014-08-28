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
from numpy import linalg
from scipy import optimize  

import time

from horus.util import profile
from horus.util.singleton import *

from horus.engine.scanner import *

@Singleton
class Calibration:

	def __init__(self):
		self.scanner = Scanner.Instance()

	def performCameraIntrinsicsCalibration(self):
		if self.scanner.isConnected:
			pass

	def performLaserTriangulationCalibration(self):
		if self.scanner.isConnected:

			device = self.scanner.device
			camera = self.scanner.camera

			##-- Load profile parameters
			calMatrix = profile.getProfileSettingNumpy('calibration_matrix')
			distortionVector = profile.getProfileSettingNumpy('distortion_vector')
			patternRows = profile.getProfileSettingInteger('pattern_rows') # points_per_column
			patternColumns = profile.getProfileSettingInteger('pattern_columns') # points_per_row
			squareWidth = profile.getProfileSettingInteger('square_width') # milimeters of each square's side

			objpoints = self.generateObjectPoints(patternColumns, patternRows, squareWidth)

			##-- Switch off lasers
			device.setLeftLaserOff()
			device.setRightLaserOff()

			##-- Move pattern until ||(R-I)|| < e
			device.setSpeedMotor(1)
			device.enable()

			z = self.getPatternDepth(device, camera, objpoints, calMatrix, distortionVector, patternColumns, patternRows)

			time.sleep(0.5)

			#-- Get images
			imgRaw = camera.captureImage(flush=True, flushValue=2)
			device.setLeftLaserOn()
			imgLasL = camera.captureImage(flush=True, flushValue=2)
			device.setLeftLaserOff()
			device.setRightLaserOn()
			imgLasR = camera.captureImage(flush=True, flushValue=2)
			device.setRightLaserOff()

			##-- Obtain Left Laser Line
			retL = self.obtainLine(imgRaw, imgLasL)

			##-- Obtain Right Laser Line
			retR = self.obtainLine(imgRaw, imgLasR)

			#-- Disable motor
			device.disable()

			return [z, [retL[0], retR[0]], [retL[1], retR[1]]]

	def getPatternDepth(self, device, camera, objpoints, calMatrix, distortionVector, patternColumns, patternRows):
		epsilon = 0.05
		distance = np.inf
		distanceAnt = np.inf
		I = np.identity(3)
		angle = 20
		z = None
		device.setRelativePosition(angle)
		device.setSpeedMotor(50)
		while distance > epsilon:
			image = camera.captureImage(flush=True, flushValue=2)
			ret = self.solvePnp(image, objpoints, calMatrix, distortionVector, patternColumns, patternRows)
			if ret is not None:
				if ret[0]:
					R = ret[1]
					z = ret[2][2]
					distance = linalg.norm(R-I)
					if distance < epsilon or distanceAnt < distance:
						break
					distanceAnt = distance
					angle = np.max(((distance-epsilon) * 20, 0.3))
			device.setRelativePosition(angle)
			device.setMoveMotor()

		print "Distance: {0} Angle: {1}".format(round(distance,3), round(angle,3))

		return z

	def obtainLine(self, imgRaw, imgLas):
		u1 = u2 = None

		height, width, depth = imgRaw.shape
		imgLine = np.zeros((height,width,depth), np.uint8)

		diff = cv2.subtract(imgLas, imgRaw)
		r,g,b = cv2.split(diff)
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
		r = cv2.morphologyEx(r, cv2.MORPH_OPEN, kernel)
		imgGray = cv2.merge((r,r,r))
		edges = cv2.threshold(r, 20.0, 255.0, cv2.THRESH_BINARY)[1]
		edges3 = cv2.merge((edges,edges,edges))
		lines = cv2.HoughLines(edges, 1, np.pi/180, 200)

		if lines is not None:
			rho, theta = lines[0][0]
			#-- Calculate coordinates
			u1 = rho / np.cos(theta)
			u2 = u1 - height * np.tan(theta)
			#-- Draw line
			cv2.line(imgLine,(int(round(u1)),0),(int(round(u2)),height-1),(255,0,0),5)

		return [[u1, u2], [imgLas, imgGray, edges3, imgLine]]

	def solvePnp(self, image, objpoints, calMatrix, distortionVector, patternColumns, patternRows):
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		# the fast check flag reduces significantly the computation time if the pattern is out of sight 
		retval, corners = cv2.findChessboardCorners(gray, (patternColumns,patternRows), flags=cv2.CALIB_CB_FAST_CHECK)
		
		if retval:
			criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.001)
			cv2.cornerSubPix(gray, corners, winSize=(11,11), zeroZone=(-1,-1), criteria=criteria)
			ret, rvecs, tvecs = cv2.solvePnP(objpoints, corners, calMatrix, distortionVector)
			return (ret, cv2.Rodrigues(rvecs)[0], tvecs)

	def generateObjectPoints(self, patternColumns, patternRows, squareWidth):
		objp = np.zeros((patternRows*patternColumns,3), np.float32)
		objp[:,:2] = np.mgrid[0:patternColumns,0:patternRows].T.reshape(-1,2)
		objp = np.multiply(objp, squareWidth)
		return objp

	def performPlatformExtrinsicsCalibration(self):
		pass