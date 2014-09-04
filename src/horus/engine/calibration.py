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

	def initialize(self, cameraMatrix, distortionVector, patternRows, patternColumns, squareWidth):
		self.cameraMatrix = cameraMatrix
		self.distortionVector = distortionVector
		self.patternRows = patternRows # points_per_column
		self.patternColumns = patternColumns # points_per_row
		self.squareWidth = squareWidth # milimeters of each square's side

		self.objpoints = self.generateObjectPoints(self.patternColumns, self.patternRows, self.squareWidth)

		self.imagePointsStack=[]
		self.objPointsStack=[]

		self.thickness = 20

		self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.001)

		#-- Camera Intrinsics Guide Lines
		self.firstPointData  = [(270,250),(4,48),(20,20),(412,198),(550,148),(20,20),(20,20),(210,350),(260,680),(140,20),(20,20),(20,340)]
		self.secondPointData = [(725,250),(596,168),(460,180),(940,46),(940,20),(940,20),(940,20),(750,350),(700,680),(940,20),(740,20),(500,500)]
		self.thirdPointData  = [(725,1024),(596,1140),(460,1000),(940,1254),(940,1260),(730,870),(720,550),(940,1260),(940,1260),(940,880),(450,600),(780,1260)]
		self.forthPointData  = [(270,1024),(4,1268),(20,1260),(412,1140),(550,1076),(192,870),(240,550),(20,1260),(20,1260),(480,740),(20,720),(20,1260)]

	def generateGuides(self, width, height):
		xfactor = width / 960.
		yfactor = height / 1280.
		self.thickness = int(round(20*xfactor))
		self.firstPoint=[(int(a*xfactor),int(b*yfactor)) for (a,b) in self.firstPointData]
		self.secondPoint=[(int(a*xfactor),int(b*yfactor)) for (a,b) in self.secondPointData]
		self.thirdPoint=[(int(a*xfactor),int(b*yfactor)) for (a,b) in self.thirdPointData]
		self.forthPoint=[(int(a*xfactor),int(b*yfactor)) for (a,b) in self.forthPointData]

	def setGuides(self, frame, currentGrid):
		if currentGrid < len(self.firstPoint):
			cv2.line(frame, self.firstPoint[currentGrid], self.secondPoint[currentGrid], (240,240,140), self.thickness)
			cv2.line(frame, self.secondPoint[currentGrid], self.thirdPoint[currentGrid], (240,240,140), self.thickness)
			cv2.line(frame, self.thirdPoint[currentGrid], self.forthPoint[currentGrid], (240,240,140), self.thickness)
			cv2.line(frame, self.forthPoint[currentGrid], self.firstPoint[currentGrid], (240,240,140), self.thickness)
		return frame

	def detectChessboard(self, frame):
		gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
		self.shape = gray.shape
		retval, corners = cv2.findChessboardCorners(gray, (self.patternColumns,self.patternRows), flags=cv2.CALIB_CB_FAST_CHECK)
		if retval:
			cv2.cornerSubPix(gray, corners, winSize=(11,11), zeroZone=(-1,-1), criteria=self.criteria)
			self.imagePointsStack.append(corners)
			self.objPointsStack.append(self.objpoints)
			cv2.drawChessboardCorners(frame, (self.patternColumns,self.patternRows), corners, retval)
		return retval, frame

	def performCameraIntrinsicsCalibration(self):
		ret = cv2.calibrateCamera(self.objPointsStack, self.imagePointsStack, self.shape)
		
		if ret[0]:
			self.cameraMatrix = ret[1]
			self.distortionVector = ret[2][0]
			return self.cameraMatrix, self.distortionVector, ret[3], ret[4]
		else:
			"Calibrate Camera Error"

		#self.meanError()

	"""def meanError(self):
		mean_error = 0
		for i in xrange(len(self.objPointsStack)):
			imgpoints2,_=cv2.projectPoints(self.objPointsStack[i],self.rvecs[i],self.tvecs[i],self.cameraMatrix,self._distortionVector)
			error=cv2.norm(self.imagePointsStack[i],imgpoints2,cv2.NORM_L2)/len(imgpoints2)
			mean_error+=error
		self.mean_error=mean_error"""

	def clearImageStack(self):
		if hasattr(self, 'imagePointsStack'):
			del self.imagePointsStack[:]
		if hasattr(self, 'objPointsStack'):
			del self.objPointsStack[:]


	def performLaserTriangulationCalibration(self):
		if self.scanner.isConnected:

			device = self.scanner.device
			camera = self.scanner.camera

			##-- Switch off lasers
			device.setLeftLaserOff()
			device.setRightLaserOff()

			##-- Move pattern until ||(R-I)|| < e
			device.setSpeedMotor(1)
			device.enable()

			z = self.getPatternDepth(device, camera, self.objpoints, self.cameraMatrix, self.distortionVector, self.patternColumns, self.patternRows)

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

			if z is not None:
				return [z, [retL[0], retR[0]], [retL[1], retR[1]]]
			else:
				return None

	def getPatternDepth(self, device, camera, objpoints, cameraMatrix, distortionVector, patternColumns, patternRows):
		epsilon = 0.05
		distance = np.inf
		distanceAnt = np.inf
		I = np.identity(3)
		angle = 20
		z = None
		tries = 5
		device.setRelativePosition(angle)
		device.setSpeedMotor(50)
		while distance > epsilon and tries > 0:
			image = camera.captureImage(flush=True, flushValue=2)
			ret = self.solvePnp(image, objpoints, cameraMatrix, distortionVector, patternColumns, patternRows)
			if ret is not None:
				if ret[0]:
					R = ret[1]
					z = ret[2][2]
					distance = linalg.norm(R-I)
					if distance < epsilon or distanceAnt < distance:
						break
					distanceAnt = distance
					angle = np.max(((distance-epsilon) * 20, 0.3))
			else:
				tries -= 1
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

	def solvePnp(self, image, objpoints, cameraMatrix, distortionVector, patternColumns, patternRows):
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		# the fast check flag reduces significantly the computation time if the pattern is out of sight 
		retval, corners = cv2.findChessboardCorners(gray, (patternColumns,patternRows), flags=cv2.CALIB_CB_FAST_CHECK)
		
		if retval:
			criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.001)
			cv2.cornerSubPix(gray, corners, winSize=(11,11), zeroZone=(-1,-1), criteria=criteria)
			ret, rvecs, tvecs = cv2.solvePnP(objpoints, corners, cameraMatrix, distortionVector)
			return (ret, cv2.Rodrigues(rvecs)[0], tvecs)

	def generateObjectPoints(self, patternColumns, patternRows, squareWidth):
		objp = np.zeros((patternRows*patternColumns,3), np.float32)
		objp[:,:2] = np.mgrid[0:patternColumns,0:patternRows].T.reshape(-1,2)
		objp = np.multiply(objp, squareWidth)
		return objp


	def performPlatformExtrinsicsCalibration(self):
		if self.scanner.isConnected:

			device = self.scanner.device
			camera = self.scanner.camera

			x = []
			y = []
			z = []

			ret = False

			##-- Switch off lasers
			device.setLeftLaserOff()
			device.setRightLaserOff()

			##-- Move pattern 180 degrees
			step = 5 # degrees
			angle = 0
			device.setSpeedMotor(1)
			device.enable()
			device.setSpeedMotor(200)
			while angle <= 180:
				angle += step
				t = self.getPatternPosition(step, device, camera)
				if t is not None:
					x += [t[0][0]]
					y += [t[1][0]]
					z += [t[2][0]]

			#-- Obtain Circle
			if len(x) > 0: # len(z) > 0 too
				ret = True
				Ri, center = self.optimizeCircle(x, z)

			#-- Disable motor
			device.disable()

			if ret:
				return [[x,y,z], Ri, center]
			else:
				return None

	def getPatternPosition(self, step, device, camera):
		t = None
		image = camera.captureImage(flush=True, flushValue=2)
		ret = self.solvePnp(image, self.objpoints, self.cameraMatrix, self.distortionVector, self.patternColumns, self.patternRows)
		if ret is not None:
			if ret[0]:
				t = ret[2]
		device.setRelativePosition(step)
		device.setMoveMotor()
		return t

	def optimizeCircle(self, x2D, z2D):
		self.x2D = x2D
		self.z2D = z2D
		centerEstimate = 0, 310
 		center = optimize.leastsq(self.f, centerEstimate)[0]
		Ri = self.calc_R(*center)
		return Ri, center

	def calc_R(self, xc, zc):
		return np.sqrt((self.x2D-xc)**2 + (self.z2D-zc)**2)

	def f(self, c):
		Ri = self.calc_R(*c)
		return Ri - Ri.mean()