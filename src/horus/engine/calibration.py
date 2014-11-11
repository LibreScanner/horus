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
# Date: November 2014                                                   #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>   	                #
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

import os
import cv2
import time
import threading
import numpy as np
from scipy import optimize

from horus.engine.driver import Driver

import horus.util.error as Error
from horus.util.singleton import Singleton


class Calibration:
	""" 
		Performs calibration processes:

			- Multithread calibration
	"""

	def __init__(self):
		self.isCalibrating = False
		self.driver = Driver.Instance()

		#TODO: Callbacks to Observer pattern
		self.beforeCallback = None
		self.progressCallback = None
		self.afterCallback = None

	def setCallbacks(self, before, progress, after):
		self.beforeCallback = before
		self.progressCallback = progress
		self.afterCallback = after

	def start(self):
		if self.beforeCallback is not None:
			self.beforeCallback()

		if self.progressCallback is not None:
			self.progressCallback(0)

		self.isCalibrating = True
		threading.Thread(target=self._start, args=(self.progressCallback,self.afterCallback)).start()

	def _start(self, progressCallback, afterCallback):
		pass

	def cancel(self):
		self.isCalibrating = False


@Singleton
class CameraIntrinsics(Calibration):
	""" 
		Camera calibration algorithms, based on [Zhang2000] and [BouguetMCT]:

			- Camera matrix
			- Distortion vector
	"""
	def __init__(self):
		Calibration.__init__(self)
		self.objPointsStack = []
		self.imagePointsStack = []
		self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.0001)

	def setIntrinsics(self, cameraMatrix, distortionVector):
		self.cameraMatrix = cameraMatrix
		self.distortionVector = distortionVector

	def setUseDistortion(self, useDistortion):
		self.useDistortion = useDistortion

	def setPatternParameters(self, rows, columns, squareWidth, distance):
		self.patternRows = rows
		self.patternColumns = columns
		self.squareWidth = squareWidth
		self.patternDistance = distance
		self.objpoints = self.generateObjectPoints(self.patternColumns, self.patternRows, self.squareWidth)

	def generateObjectPoints(self, patternColumns, patternRows, squareWidth):
		objp = np.zeros((patternRows*patternColumns,3), np.float32)
		objp[:,:2] = np.mgrid[0:patternColumns,0:patternRows].T.reshape(-1,2)
		objp = np.multiply(objp, squareWidth)
		return objp

	def _start(self, progressCallback, afterCallback):
		ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objPointsStack, self.imagePointsStack, self.shape)
		
		if progressCallback is not None:
			progressCallback(100)

		if ret:
			response = (True, (mtx, dist[0], rvecs, tvecs))
		else:
			response = (False, Error.CalibrationError)

		if afterCallback is not None:
			afterCallback(response)

	def detectChessboard(self, frame, capture=False):
		gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
		self.shape = gray.shape
		retval, corners = cv2.findChessboardCorners(gray, (self.patternColumns,self.patternRows), flags=cv2.CALIB_CB_FAST_CHECK)
		if retval:
			cv2.cornerSubPix(gray, corners, winSize=(11,11), zeroZone=(-1,-1), criteria=self.criteria)
			if capture:
				if len(self.objPointsStack) < 12:
					self.imagePointsStack.append(corners)
					self.objPointsStack.append(self.objpoints) 
			cv2.drawChessboardCorners(frame, (self.patternColumns,self.patternRows), corners, retval)
		return retval, frame

	def clearImageStack(self):
		if hasattr(self, 'imagePointsStack'):
			del self.imagePointsStack[:]
		if hasattr(self, 'objPointsStack'):
			del self.objPointsStack[:]


@Singleton
class LaserTriangulation(Calibration):
	""" 
		Laser triangulation algorithms:

			- Laser coordinates matrix
			- Pattern's origin
			- Pattern's normal
	"""
	def __init__(self):
		Calibration.__init__(self)
		self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.0001)

	def setIntrinsics(self, cameraMatrix, distortionVector):
		self.cameraMatrix = cameraMatrix
		self.distortionVector = distortionVector

	def setUseDistortion(self, useDistortion):
		self.useDistortion = useDistortion

	def setPatternParameters(self, rows, columns, squareWidth, distance):
		self.patternRows = rows
		self.patternColumns = columns
		self.squareWidth = squareWidth
		self.patternDistance = distance
		self.objpoints = self.generateObjectPoints(self.patternColumns, self.patternRows, self.squareWidth)

	def generateObjectPoints(self, patternColumns, patternRows, squareWidth):
		objp = np.zeros((patternRows*patternColumns,3), np.float32)
		objp[:,:2] = np.mgrid[0:patternColumns,0:patternRows].T.reshape(-1,2)
		objp = np.multiply(objp, squareWidth)
		return objp

	def _start(self, progressCallback, afterCallback):
		t = None

		if self.driver.isConnected:

			board = self.driver.board
			camera = self.driver.camera

			##-- Switch off lasers
			board.setLeftLaserOff()
			board.setRightLaserOff()

			##-- Move pattern until ||(R-I)|| < e
			board.setSpeedMotor(1)
			board.enableMotor()
			time.sleep(0.3)

			t, n, corners = self.getPatternDepth(board, camera, progressCallback)

			if t is not None and corners is not None:
				time.sleep(0.1)

				#-- Get images
				if os.name == 'nt':
					imgRaw = camera.captureImage(flush=False)
					board.setLeftLaserOn()
					time.sleep(0.1)
					imgLasL = camera.captureImage(flush=False)
					board.setLeftLaserOff()
					board.setRightLaserOn()
					time.sleep(0.1)
					imgLasR = camera.captureImage(flush=False)
					board.setRightLaserOff()
				else:
					imgRaw = camera.captureImage(flush=True, flushValue=2)
					board.setLeftLaserOn()
					imgLasL = camera.captureImage(flush=True, flushValue=2)
					board.setLeftLaserOff()
					board.setRightLaserOn()
					imgLasR = camera.captureImage(flush=True, flushValue=2)
					board.setRightLaserOff()

				##-- Corners ROI mask
				imgLasL = self.cornersMask(imgLasL, corners)
				imgLasR = self.cornersMask(imgLasR, corners)

				##-- Obtain Left Laser Line
				retL = self.obtainLine(imgRaw, imgLasL)

				##-- Obtain Right Laser Line
				retR = self.obtainLine(imgRaw, imgLasR)

			#-- Disable motor
			board.disableMotor()

		if self.isCalibrating and t is not None and not (0 in retL[0] or 0 in retR[0]):
			response = (True, ([t, n], [retL[0], retR[0]], [retL[1], retR[1]]))
			if progressCallback is not None:
				progressCallback(100)
		else:
			if self.isCalibrating:
				response = (False, Error.CalibrationError)
			else:
				response = (False, Error.CalibrationCanceled)

		if afterCallback is not None:
			afterCallback(response)

	def getPatternDepth(self, board, camera, progressCallback):
		epsilon = 0.0002
		distance = np.inf
		distanceAnt = np.inf
		angle = 20
		t = None
		n = None
		corners = None
		tries = 5
		board.setRelativePosition(angle)
		board.setSpeedMotor(40)

		if progressCallback is not None:
			progressCallback(0)

		while self.isCalibrating and distance > epsilon and tries > 0:
			image = camera.captureImage(flush=True, flushValue=2)
			ret = self.solvePnp(image, self.objpoints, self.cameraMatrix, self.distortionVector, self.patternColumns, self.patternRows)
			if ret is not None:
				if ret[0]:
					R = ret[1]
					t = ret[2].T[0]
					n = R.T[2]
					corners = ret[3]
					distance = np.linalg.norm((0,0,1)-n)
					if distance < epsilon or distanceAnt < distance:
						board.setRelativePosition(-angle)
						board.moveMotor()
						break
					distanceAnt = distance
					angle = np.max(((distance-epsilon) * 15, 0.1))
			else:
				tries -= 1
			board.setRelativePosition(angle)
			board.moveMotor()

			if progressCallback is not None:
				if distance < np.inf:
					progressCallback(min(80,max(0,80-100*abs(distance-epsilon))))

		image = camera.captureImage(flush=True, flushValue=2)
		ret = self.solvePnp(image, self.objpoints, self.cameraMatrix, self.distortionVector, self.patternColumns, self.patternRows)
		if ret is not None:
			R = ret[1]
			t = ret[2].T[0]
			n = R.T[2]
			corners = ret[3]
			distance = np.linalg.norm((0,0,1)-n)
			angle = np.max(((distance-epsilon) * 15, 0.1))

			if progressCallback is not None:
				progressCallback(90)

		#print "Distance: {0} Angle: {1}".format(round(distance,3), round(angle,3))

		return t, n, corners

	def cornersMask(self, frame, corners):
		p1 = corners[0][0]
		p2 = corners[self.patternColumns-1][0]
		p3 = corners[self.patternColumns*(self.patternRows-1)-1][0]
		p4 = corners[self.patternColumns*self.patternRows-1][0]
		p11 = min(p1[1], p2[1], p3[1], p4[1])
		p12 = max(p1[1], p2[1], p3[1], p4[1])
		p21 = min(p1[0], p2[0], p3[0], p4[0])
		p22 = max(p1[0], p2[0], p3[0], p4[0])
		d = max(corners[1][0][0]-corners[0][0][0],
				corners[1][0][1]-corners[0][0][1],
				corners[self.patternColumns][0][1]-corners[0][0][1],
				corners[self.patternColumns][0][0]-corners[0][0][0])
		mask = np.zeros(frame.shape[:2], np.uint8)
		mask[p11-d:p12+d,p21-d:p22+d] = 255
		frame = cv2.bitwise_and(frame, frame, mask=mask)
		return frame

	def obtainLine(self, imgRaw, imgLas):
		u1 = u2 = 0

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
			cv2.cornerSubPix(gray, corners, winSize=(11,11), zeroZone=(-1,-1), criteria=self.criteria)
			if self.useDistortion:
				ret, rvecs, tvecs = cv2.solvePnP(objpoints, corners, cameraMatrix, distortionVector)
			else:
				ret, rvecs, tvecs = cv2.solvePnP(objpoints, corners, cameraMatrix, None)
			return (ret, cv2.Rodrigues(rvecs)[0], tvecs, corners)


@Singleton
class PlatformExtrinsics(Calibration):
	""" 
		Platform extrinsics algorithms:

			- Rotation matrix
			- Translation vector
	"""
	def __init__(self):
		Calibration.__init__(self)
		self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.0001)

	def setExtrinsicsStep(self, step):
		self.extrinsicsStep = step

	def setIntrinsics(self, cameraMatrix, distortionVector):
		self.cameraMatrix = cameraMatrix
		self.distortionVector = distortionVector

	def setUseDistortion(self, useDistortion):
		self.useDistortion = useDistortion

	def setPatternParameters(self, rows, columns, squareWidth, distance):
		self.patternRows = rows
		self.patternColumns = columns
		self.squareWidth = squareWidth
		self.patternDistance = distance
		self.objpoints = self.generateObjectPoints(self.patternColumns, self.patternRows, self.squareWidth)

	def generateObjectPoints(self, patternColumns, patternRows, squareWidth):
		objp = np.zeros((patternRows*patternColumns,3), np.float32)
		objp[:,:2] = np.mgrid[0:patternColumns,0:patternRows].T.reshape(-1,2)
		objp = np.multiply(objp, squareWidth)
		return objp

	def _start(self, progressCallback, afterCallback):
		t = None

		if self.driver.isConnected:

			board = self.driver.board
			camera = self.driver.camera

			x = []
			y = []
			z = []

			##-- Switch off lasers
			board.setLeftLaserOff()
			board.setRightLaserOff()

			##-- Move pattern 180 degrees
			step = self.extrinsicsStep # degrees
			angle = 0
			board.setSpeedMotor(1)
			board.enableMotor()
			board.setSpeedMotor(150)
			time.sleep(0.2)

			if progressCallback is not None:
				progressCallback(0)

			while self.isCalibrating and abs(angle) < 180:
				angle += step
				t = self.getPatternPosition(step, board, camera)
				if progressCallback is not None:
					progressCallback(1.1*abs(angle/2.))
				time.sleep(0.1)
				if t is not None:
					x += [t[0][0]]
					y += [t[1][0]]
					z += [t[2][0]]

			x = np.array(x)
			y = np.array(y)
			z = np.array(z)

			points = zip(x,y,z)

			if len(points) > 4:

				#-- Fitting a plane
				point, normal = self.fitPlane(points)

				#-- Fitting a circle inside the plane
				center, R, circle = self.fitCircle(point, normal, points)

				# Get real origin
				t = center - self.patternDistance * np.array(normal)

			#-- Disable motor
			board.disableMotor()

		if self.isCalibrating and t is not None and np.linalg.norm(t-[5,80,320]) < 20:
			response = (True, (R, t, center, point, normal, [x,y,z], circle))
			if progressCallback is not None:
				progressCallback(100)
		else:
			if self.isCalibrating:
				response = (False, Error.CalibrationError)
			else:
				response = (False, Error.CalibrationCanceled)

		if afterCallback is not None:
			afterCallback(response)

	def getPatternPosition(self, step, board, camera):
		t = None
		image = camera.captureImage(flush=True, flushValue=2)
		ret = self.solvePnp(image, self.objpoints, self.cameraMatrix, self.distortionVector, self.patternColumns, self.patternRows)
		if ret is not None:
			if ret[0]:
				t = ret[2]
		board.setRelativePosition(step)
		board.moveMotor()
		return t

	def solvePnp(self, image, objpoints, cameraMatrix, distortionVector, patternColumns, patternRows):
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		# the fast check flag reduces significantly the computation time if the pattern is out of sight 
		retval, corners = cv2.findChessboardCorners(gray, (patternColumns,patternRows), flags=cv2.CALIB_CB_FAST_CHECK)

		if retval:
			cv2.cornerSubPix(gray, corners, winSize=(11,11), zeroZone=(-1,-1), criteria=self.criteria)
			if self.useDistortion:
				ret, rvecs, tvecs = cv2.solvePnP(objpoints, corners, cameraMatrix, distortionVector)
			else:
				ret, rvecs, tvecs = cv2.solvePnP(objpoints, corners, cameraMatrix, None)
			return (ret, cv2.Rodrigues(rvecs)[0], tvecs, corners)

	#-- Fitting a plane
	def distanceToPlane(self, p0,n0,p):
		return np.dot(np.array(n0),np.array(p)-np.array(p0))    

	def residualsPlane(self, parameters,dataPoint):
		px,py,pz,theta,phi = parameters
		nx,ny,nz = np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)
		distances = [self.distanceToPlane([px,py,pz],[nx,ny,nz],[x,y,z]) for x,y,z in dataPoint]
		return distances

	def fitPlane(self, data):
		estimate = [0, 0, 0, 0, 0] # px,py,pz and zeta, phi
		#you may automize this by using the center of mass data
		# note that the normal vector is given in polar coordinates
		bestFitValues, ier = optimize.leastsq(self.residualsPlane, estimate, args=(data))
		xF,yF,zF,tF,pF = bestFitValues

		#self.point  = [xF,yF,zF]
		self.point = data[0]
		self.normal = -np.array([np.sin(tF)*np.cos(pF),np.sin(tF)*np.sin(pF),np.cos(tF)])

		return self.point, self.normal

	def residualsCircle(self, parameters, dataPoint):
		r,s,Ri = parameters
		planePoint = s*self.s + r*self.r + np.array(self.point)
		distance = [ np.linalg.norm( planePoint-np.array([x,y,z])) for x,y,z in dataPoint]
		res = [(Ri-dist) for dist in distance]
		return res

	def fitCircle(self, point, normal, data):
		#creating two inplane vectors
		self.s = np.cross(np.array([1,0,0]),np.array(normal))#assuming that normal not parallel x!
		self.s = self.s/np.linalg.norm(self.s)
		self.r = np.cross(np.array(normal),self.s)
		self.r = self.r/np.linalg.norm(self.r)#should be normalized already, but anyhow

		# Define rotation
		R = np.array([self.s,self.r,normal]).T

		estimateCircle = [0, 0, 0] # px,py,pz and zeta, phi
		bestCircleFitValues, ier = optimize.leastsq(self.residualsCircle, estimateCircle, args=(data))

		rF,sF,RiF = bestCircleFitValues

		# Synthetic Data
		centerPoint = sF*self.s + rF*self.r + np.array(self.point)
		synthetic = [list(centerPoint+ RiF*np.cos(phi)*self.r+RiF*np.sin(phi)*self.s) for phi in np.linspace(0, 2*np.pi,50)]
		[cxTupel,cyTupel,czTupel] = [ x for x in zip(*synthetic)]

		return centerPoint, R, [cxTupel,cyTupel,czTupel]