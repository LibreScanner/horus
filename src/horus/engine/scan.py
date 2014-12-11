#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: March & November 2014                                           #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>                    #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 2 of the License, or     #
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
__license__ = "GNU General Public License v2 http://www.gnu.org/licenses/gpl.html"

import os
import cv2
import time
import Queue
import threading
import datetime
import numpy as np

from horus.engine.driver import Driver

import horus.util.error as Error
from horus.util.singleton import Singleton


class Scan:
	""" 
		Performs scanning process:

			- Multithread scanning:
				- Capture Thread
				- Process Thread: compute 3D point cloud from 2D points
	"""

	def __init__(self):
		""" """
		self.driver = Driver.Instance()
		self.pcg = PointCloudGenerator.Instance()

		self.points = None
		self.colors = None

		self.run = False
		self.moveMotor = True
		self.generatePointCloud = True

		self.fastScan = False
		self.speedMotor = 200
		self.accelerationMotor = 400

		self.imgType = 'laser'
		self.imgColor  = None
		self.imgLaser  = None
		self.imgGray = None
		self.imgLine = None

		#TODO: Callbacks to Observer pattern
		self.beforeCallback = None
		self.progressCallback = None
		self.afterCallback = None

		self.points2DQueue = Queue.Queue(1000)
		self.points3DQueue = Queue.Queue(10000)

	def setCallbacks(self, before, progress, after):
		self.beforeCallback = before
		self.progressCallback = progress
		self.afterCallback = after

	def start(self):
		if self.beforeCallback is not None:
			self.beforeCallback()

		self.initializeScan()
		
		self.run = True
		self.inactive = False

		threading.Thread(target=self._captureThread, args=(self.progressCallback,self.afterCallback)).start()
		threading.Thread(target=self._processThread).start()
		
	def stop(self):
		self.run = False

	def pause(self):
		self.inactive = True

	def resume(self):
		self.inactive = False

	def setFastScan(self, value):
		self.fastScan = value

	def setSpeedMotor(self, value):
		self.speedMotor = value

	def setAccelerationMotor(self, value):
		self.accelerationMotor = value

	def setImageType(self, imgType):
		self.imgType = imgType

	def getImage(self):
		img = { 'color' : self.imgColor,
				'laser' : self.imgLaser,
				'gray' : self.imgGray,
				'line' : self.imgLine
			  }[self.imgType]

		if img is not None:
			if self.pcg.viewROI:
				img = img.copy()
				cv2.rectangle(img, (self.pcg.umin, self.pcg.vmin), (self.pcg.umax, self.pcg.vmax), (0, 0, 255), 3)
			
		return img

	def applyROIMask(self, image):
		mask = np.zeros(image.shape,np.uint8)
		mask[self.pcg.vmin:self.pcg.vmax,
			 self.pcg.umin:self.pcg.umax] = image[self.pcg.vmin:self.pcg.vmax,
			 									  self.pcg.umin:self.pcg.umax]

		return mask

	def initializeScan(self):
		self.pcg.resetTheta()

		self.points2DQueue.queue.clear()
		self.points3DQueue.queue.clear()

		#-- Setup board
		if self.moveMotor:
			self.driver.board.enableMotor()
			self.driver.board.setSpeedMotor(self.speedMotor)
			self.driver.board.setAccelerationMotor(self.setAccelerationMotor)
			time.sleep(0.2)
		else:
			self.driver.board.disableMotor()

		self.driver.board.setLeftLaserOff()
		self.driver.board.setRightLaserOff()

		#-- Setup camera
		self.driver.camera.capture.read()

	#-- Threads

	def _captureThread(self):
		""""""
		pass

	def _processThread(self):
		""""""
		while self.run:
			if not self.inactive:
				#-- Get 2D points from the queue
				if not self.points2DQueue.empty():
					laser, points2D, colors = self.points2DQueue.get(timeout=0.1)
					self.points2DQueue.task_done()

					begin = datetime.datetime.now()

					#-- Compute 3D points
					points3D = self.pcg.compute3DPoints(points2D, laser)

					if points3D is not None and colors is not None:
						if self.points == None and self.colors == None:
							self.points = points3D
							self.colors = colors
						else:
							self.points = np.append(self.points, points3D, axis=1)
							self.colors = np.append(self.points, points3D, axis=1)

						if self.generatePointCloud:
							#-- Put point cloud into the queue
							self.points3DQueue.put((points3D, colors))

					end = datetime.datetime.now()
					print "Process end: {0}".format(end - begin)
			else:
				time.sleep(0.1)
		
	def getPointCloudIncrement(self):
		""" """
		if not self.points3DQueue.empty():
			pc = self.points3DQueue.get_nowait()
			if pc is not None:
				self.points3DQueue.task_done()
			return pc
		else:
			return None


@Singleton
class SimpleScan(Scan):
	""" 
		Capture geometry

			- Image processing
			- Red line laser detection
	"""

	def _captureThread(self, progressCallback, afterCallback):
		""""""
		ret = False

		self.driver.board.setLeftLaserOff()
		self.driver.board.setRightLaserOff()

		if self.pcg.useLeftLaser and not self.pcg.useRightLaser:
			self.driver.board.setLeftLaserOn()

		if not self.pcg.useLeftLaser and self.pcg.useRightLaser:
			self.driver.board.setRightLaserOn()

		while self.run:
			if not self.inactive:
				begin = datetime.datetime.now()

				#-- Left laser
				if self.pcg.useLeftLaser and not self.pcg.useRightLaser:
					image = self.driver.camera.captureImage()
					if image is not None:
						#-- Compute 2D points from images
						points2D, colors = self.compute2DPoints(image)
						#-- Put 2D points into the queue
						self.points2DQueue.put((True, points2D, colors))

				#-- Right laser
				if not self.pcg.useLeftLaser and self.pcg.useRightLaser:
					image = self.driver.camera.captureImage()
					if image is not None:
						#-- Compute 2D points from images
						points2D, colors = self.compute2DPoints(image)
						#-- Put 2D points into the queue
						self.points2DQueue.put((False, points2D, colors))

				##-- Both laser
				if self.pcg.useLeftLaser and self.pcg.useRightLaser:
					self.driver.board.setLeftLaserOn()
					self.driver.board.setRightLaserOff()
					imgLaserLeft = self.driver.camera.captureImage(flush=True, flushValue=1)

					self.driver.board.setRightLaserOn()
					self.driver.board.setLeftLaserOff()
					imgLaserRight = self.driver.camera.captureImage(flush=True, flushValue=1)

					if imgLaserLeft is not None:
						#-- Compute 2D points from images
						points2D, colors = self.compute2DPoints(imgLaserLeft)
						#-- Put 2D points into the queue
						self.points2DQueue.put((True, points2D, colors))

					if imgLaserRight is not None:
						#-- Compute 2D points from images
						points2D, colors = self.compute2DPoints(imgLaserRight)
						#-- Put 2D points into the queue
						self.points2DQueue.put((False, points2D, colors))

				#-- Move motor
				if self.moveMotor:
					self.driver.board.setRelativePosition(self.pcg.degrees)
					self.driver.board.moveMotor()
				else:
					time.sleep(0.05)
				
				if self.generatePointCloud:
					#-- Check stop condition
					if abs(self.pcg.theta * 180.0 / np.pi) >= 360.0:
						ret = True
						self.stop()
				
				end = datetime.datetime.now()
				print "----- Theta: {0}".format(self.pcg.theta * 180.0 / np.pi)
				print "Capture end: {0}".format(end - begin)
			else:
				time.sleep(0.1)

		#-- Disable board
		self.driver.board.setLeftLaserOff()
		self.driver.board.setRightLaserOff()
		self.driver.board.disableMotor()

		if progressCallback is not None:
			progressCallback(100)

		if ret:
			response = (True, None)
		else:
			response = (False, Error.ScanError)

		if afterCallback is not None:
			afterCallback(response)

	def setColor(self, value):
		self.color = value

	def setUseThreshold(self, enable):
		self.thresholdEnable = enable

	def setThresholdValue(self, value):
		self.thresholdValue = value

	def compute2DPoints(self, image):
		self.imgLaser = image
		tempColor = np.ones_like(image)
		tempColor[:,:,0] *= self.color[0]
		tempColor[:,:,1] *= self.color[1]
		tempColor[:,:,2] *= self.color[2]
		self.imgColor = tempColor

		#-- Convert tp Y Cr Cb format
		y,cr,cb = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YCR_CB))

		#-- Get Cr
		image = cr

		#-- Apply ROI mask
		image = self.applyROIMask(image)

		#-- Threshold image
		if self.thresholdEnable:
			image = cv2.threshold(image, self.thresholdValue, 255.0, cv2.THRESH_TOZERO)[1]

		#-- Detect peaks in rows
		s = image.sum(1)
		v = np.where((s > 0))[0]
		u = np.argmax(image, axis=1)[v]

		#-- Segment line
		"""#-- Line generation
		s = imageBin.sum(1)
		v = np.where((s > 2))[0]
		if self.useCompact:
			i = imageBin.argmax(1)
			u = ((i + (s/255.-1) / 2.)[v]).T.astype(int)
		else:
			w = (self.W * imageBin).sum(1)
			u = (w[v] / s[v].T).astype(int)"""
		
		tempLine = np.zeros_like(self.imgLaser)
		tempLine[v,u] = 255
		self.imgLine = tempLine
		self.imgGray = cv2.merge((image, image, image))

		colors = np.array(np.matrix(np.ones(len(u))).T*np.matrix(self.color)).T

		return (u, v), colors


@Singleton
class TextureScan(Scan):
	""" 
		Capture geometry and texture
	"""

	def _captureThread(self, progressCallback, afterCallback):
		""""""
		ret = False
		imgRaw = None
		imgLaserLeft = None
		imgLaserRight = None
		while self.run:
			if not self.inactive:
				begin = datetime.datetime.now()

				if self.fastScan: #-- FAST METHOD

					#-- Left laser
					if self.pcg.useLeftLaser and not self.pcg.useRightLaser:
						self.driver.board.setLeftLaserOff()
						imgLaserLeft = self.driver.camera.capture.read()[1]
						imgRaw = self.driver.camera.capture.read()[1]
						self.driver.board.setLeftLaserOn()

						imgRaw = cv2.transpose(imgRaw)
						imgRaw = cv2.flip(imgRaw, 1)
						imgRaw = cv2.cvtColor(imgRaw, cv2.COLOR_BGR2RGB)

						imgLaserRight = None

						imgLaserLeft = cv2.transpose(imgLaserLeft)
						imgLaserLeft = cv2.flip(imgLaserLeft, 1)
						imgLaserLeft = cv2.cvtColor(imgLaserLeft, cv2.COLOR_BGR2RGB)

					#-- Right laser
					if not self.pcg.useLeftLaser and self.pcg.useRightLaser:
						self.driver.board.setRightLaserOff()
						imgLaserRight = self.driver.camera.capture.read()[1]
						imgRaw = self.driver.camera.capture.read()[1]
						self.driver.board.setRightLaserOn()

						imgRaw = cv2.transpose(imgRaw)
						imgRaw = cv2.flip(imgRaw, 1)
						imgRaw = cv2.cvtColor(imgRaw, cv2.COLOR_BGR2RGB)

						imgLaserLeft = None

						imgLaserRight = cv2.transpose(imgLaserRight)
						imgLaserRight = cv2.flip(imgLaserRight, 1)
						imgLaserRight = cv2.cvtColor(imgLaserRight, cv2.COLOR_BGR2RGB)

					##-- Both laser
					if self.pcg.useLeftLaser and self.pcg.useRightLaser:
						imgRaw = self.driver.camera.capture.read()[1]
						self.driver.board.setLeftLaserOn()
						imgLaserLeft = self.driver.camera.capture.read()[1]
						self.driver.board.setLeftLaserOff()
						self.driver.board.setRightLaserOn()
						imgLaserRight = self.driver.camera.capture.read()[1]
						self.driver.board.setRightLaserOff()
						imgRaw = self.driver.camera.capture.read()[1]

						imgRaw = cv2.transpose(imgRaw)
						imgRaw = cv2.flip(imgRaw, 1)
						imgRaw = cv2.cvtColor(imgRaw, cv2.COLOR_BGR2RGB)

						imgLaserLeft = cv2.transpose(imgLaserLeft)
						imgLaserLeft = cv2.flip(imgLaserLeft, 1)
						imgLaserLeft = cv2.cvtColor(imgLaserLeft, cv2.COLOR_BGR2RGB)

						imgLaserRight = cv2.transpose(imgLaserRight)
						imgLaserRight = cv2.flip(imgLaserRight, 1)
						imgLaserRight = cv2.cvtColor(imgLaserRight, cv2.COLOR_BGR2RGB)

				else: #-- SLOW METHOD

					#-- Switch off laser
					if self.pcg.useLeftLaser:
						self.driver.board.setLeftLaserOff()
					if self.pcg.useRightLaser:
						self.driver.board.setRightLaserOff()

					#-- Capture images
					if os.name == 'nt':
						#TODO
						pass
					else:
						imgRaw = self.driver.camera.captureImage(flush=True, flushValue=1)

						if self.pcg.useLeftLaser:
							self.driver.board.setLeftLaserOn()
							self.driver.board.setRightLaserOff()
							imgLaserLeft = self.driver.camera.captureImage(flush=True, flushValue=1)
						else:
							imgLaserLeft = None

						if self.pcg.useRightLaser:
							self.driver.board.setRightLaserOn()
							self.driver.board.setLeftLaserOff()
							imgLaserRight = self.driver.camera.captureImage(flush=True, flushValue=1)
						else:
							imgLaserRight = None

				if self.pcg.useLeftLaser:
					if imgRaw is not None and imgLaserLeft is not None:
						#-- Compute 2D points from images
						points2D, colors = self.compute2DPoints(imgRaw, imgLaserLeft)
						#-- Put 2D points into the queue
						self.points2DQueue.put((True, points2D, colors))

				if self.pcg.useRightLaser:
					if imgRaw is not None and imgLaserRight is not None:
						#-- Compute 2D points from images
						points2D, colors = self.compute2DPoints(imgRaw, imgLaserRight)
						#-- Put 2D points into the queue
						self.points2DQueue.put((False, points2D, colors))

				#-- Move motor
				if self.moveMotor:
					self.driver.board.setRelativePosition(self.pcg.degrees)
					self.driver.board.moveMotor()
				else:
					time.sleep(0.05)
				
				if self.generatePointCloud:
					#-- Check stop condition
					if abs(self.pcg.theta * 180.0 / np.pi) >= 360.0:
						ret = True
						self.stop()
				
				end = datetime.datetime.now()
				print "----- Theta: {0}".format(self.pcg.theta * 180.0 / np.pi)
				print "Capture end: {0}".format(end - begin)
			else:
				time.sleep(0.1)

		#-- Disable board
		self.driver.board.setLeftLaserOff()
		self.driver.board.setRightLaserOff()
		self.driver.board.disableMotor()

		if progressCallback is not None:
			progressCallback(100)

		if ret:
			response = (True, None)
		else:
			response = (False, Error.ScanError)

		if afterCallback is not None:
			afterCallback(response)

	def setUseOpen(self, enable):
		self.openEnable = enable

	def setOpenValue(self, value):
		self.openValue = value

	def setUseThreshold(self, enable):
		self.thresholdEnable = enable

	def setThresholdValue(self, value):
		self.thresholdValue = value

	def compute2DPoints(self, imageColor, imageLaser):
		self.imgLaser = imageLaser
		self.imgColor = imageColor

		"""#-- Use R channel
		r1,g1,b1 = cv2.split(imageColor)
		r2,g1,b2 = cv2.split(imageLaser)

		image = cv2.subtract(r2, r1)"""

		#-- Use Cr channel
		y1,cr1,cb1 = cv2.split(cv2.cvtColor(imageColor, cv2.COLOR_RGB2YCR_CB))
		y2,cr2,cb2 = cv2.split(cv2.cvtColor(imageLaser, cv2.COLOR_RGB2YCR_CB))
		
		image = cv2.subtract(cr2, cr1)

		#-- Apply ROI mask
		image = self.applyROIMask(image)

		#-- Open image
		if self.openEnable:
			kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(self.openValue,self.openValue))
			image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

		#-- Threshold image
		if self.thresholdEnable:
			image = cv2.threshold(image, self.thresholdValue, 255.0, cv2.THRESH_TOZERO)[1]

		#-- Detect peaks in rows
		s = image.sum(1)
		v = np.where((s > 0))[0]
		u = np.argmax(image, axis=1)[v]

		#-- Segment line
		"""#-- Line generation
		s = imageBin.sum(1)
		v = np.where((s > 2))[0]
		if self.useCompact:
			i = imageBin.argmax(1)
			u = ((i + (s/255.-1) / 2.)[v]).T.astype(int)
		else:
			w = (self.W * imageBin).sum(1)
			u = (w[v] / s[v].T).astype(int)"""

		tempLine = np.zeros_like(imageLaser)
		tempLine[v,u] = 255.0
		self.imgLine = tempLine
		self.imgGray = cv2.merge((image, image, image))

		colors = imageColor[v,u].T

		return (u, v), colors


@Singleton
class PointCloudGenerator:
	""" 
		Contains all scanning algorithms:

			- Point cloud generation and filtering
	"""
	def __init__(self):
		self.theta = 0
		self.driver = Driver.Instance()

		self.rad = np.pi / 180.0

		self.umin = 0
		self.umax = 960
		self.vmin = 0
		self.vmax = 1280

		self.circleResolution = 30
		self.circleArray = np.array([[np.cos(i*2*np.pi/self.circleResolution) for i in range(self.circleResolution)],
									 [np.sin(i*2*np.pi/self.circleResolution) for i in range(self.circleResolution)],
									 np.zeros(self.circleResolution)])

	def setViewROI(self, value):
		self.viewROI = value

	def setROIDiameter(self, value):
		self.roiRadius = value / 2.0
		self.calculateROI()

	def setROIHeight(self, value):
		self.roiHeight = value
		self.calculateROI()

	def setDegrees(self, degrees):
		self.degrees = degrees

	def setResolution(self, width, height):
		self.width = width
		self.height = height
		self.W = np.ones((height,width))*np.linspace(0,width-1,width)

	def setUseLaser(self, useLeft, useRight):
		self.useLeftLaser = useLeft
		self.useRightLaser = useRight

	def setLaserAngles(self, angleLeft, angleRight):
		self.alphaLeft = angleLeft * self.rad
		self.alphaRight = angleRight * self.rad

	def setCameraIntrinsics(self, cameraMatrix, distortionVector):
		self.fx = cameraMatrix[0][0]
		self.fy = cameraMatrix[1][1]
		self.cx = cameraMatrix[0][2]
		self.cy = cameraMatrix[1][2]

	def setLaserTriangulation(self, dL, nL, dR, nR):
		self.dL = dL
		self.nL = nL
		self.dR = dR
		self.nR = nR

	def setPlatformExtrinsics(self, rotationMatrix, translationVector):
		self.rotationMatrix = rotationMatrix
		self.translationVector = translationVector

	def resetTheta(self):
		self.theta = 0

	def calculateROI(self):
		if hasattr(self, 'roiRadius') and \
		   hasattr(self, 'roiHeight') and \
		   hasattr(self, 'rotationMatrix') and \
		   hasattr(self, 'translationVector') and \
		   hasattr(self, 'fx') and hasattr(self, 'fy') and \
		   hasattr(self, 'cx') and hasattr(self, 'cy') and \
		   hasattr(self, 'width') and hasattr(self, 'height'):

			#-- Platform system
			bottom = np.matrix(self.roiRadius * self.circleArray)
			top = bottom + np.matrix([0,0,self.roiHeight]).T
			data = np.concatenate((bottom, top), axis=1)

			#-- Camera system
			data =  self.rotationMatrix * data + np.matrix(self.translationVector).T

			#-- Video system
			u = self.fx * data[0] / data[2] + self.cx
			v = self.fy * data[1] / data[2] + self.cy

			umin = int(round(np.min(u)))
			umax = int(round(np.max(u)))
			vmin = int(round(np.min(v)))
			vmax = int(round(np.max(v)))

			self.umin = max(umin, 0)
			self.umax = min(umax, self.width)
			self.vmin = max(vmin, 0)
			self.vmax = min(vmax, self.height)

	def pointCloudGeneration(self, points2D, leftLaser=True):
		""" """
		u, v = points2D

		#-- Obtaining point cloud in camera coordinates
		if leftLaser:
			d = self.dL
			n = self.nL
		else:
			d = self.dR
			n = self.nR

		x = np.concatenate(((u-self.cx)/self.fx, (v-self.cy)/self.fy, np.ones(len(u)))).reshape(3,len(u))

		Xc = d/np.dot(n,x)*x

		#-- Move point cloud to world coordinates
		R = np.matrix(self.rotationMatrix).T
		t = np.matrix(self.translationVector).T

		Xwo = R*Xc - R*t

		#-- Rotate point cloud
		c = np.cos(self.theta)
		s = np.sin(self.theta)
		Rz = np.matrix([[c, -s, 0],[s, c, 0], [0, 0, 1]])
		Xw = Rz * Xwo

		#-- Return result
		if Xw.size > 0:
			return np.array(Xw)
		else:
			return None

	def pointCloudFilter(self, points):
		""" """
		#-- Point Cloud Filter
		rho = np.sqrt(points[0,:]**2 + points[1,:]**2)
		z = points[2,:]

		idx = np.where((z >= 0) &
					   (z <= self.roiHeight) &
					   (rho >= -self.roiRadius) &
					   (rho <= self.roiRadius))[0]

		return points[:,idx]

	def compute3DPoints(self, points2D, leftLaser):
		""" """
		#-- Point Cloud Generation
		points3D = self.pointCloudGeneration(points2D, leftLaser)

		if points3D is not None:
			#-- Point Cloud Filter
			points3D = self.pointCloudFilter(points3D)

		#-- Update Theta
		self.theta -= self.degrees * self.rad

		return points3D