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
				laser, motor and video synchronized
	"""
	def __init__(self):
		""" """
		self.driver = Driver.Instance()
		self.pcg = PointCloudGenerator.Instance()

		self.isRunning = False
		self.moveMotor = True
		self.generatePointCloud = True

		#TODO: Callbacks to Observer pattern
		self.beforeCallback = None
		self.progressCallback = None
		self.afterCallback = None

		self.imageQueue = Queue.Queue(1000)
		self.pointCloudQueue = Queue.Queue(10000)

	def setCallbacks(self, before, progress, after):
		self.beforeCallback = before
		self.progressCallback = progress
		self.afterCallback = after

	def start(self):
		if self.beforeCallback is not None:
			self.beforeCallback()

		self.imageQueue.queue.clear()
		self.pointCloudQueue.queue.clear()
		
		self.inactive = False
		self.isRunning = True

		threading.Thread(target=self._captureThread, args=(self.progressCallback,self.afterCallback)).start()
		threading.Thread(target=self._processThread).start()
		
	def stop(self):
		self.isRunning = False

	def pause(self):
		self.inactive = True

	def resume(self):
		self.inactive = False

	#-- Threads

	def _captureThread(self):
		""" """
		pass

	def _processThread(self):
		""" """
		while self.isRunning:
			if not self.inactive:
				#-- Get images
				images = self.imageQueue.get()
				self.imageQueue.task_done()

				begin = datetime.datetime.now()

				#-- Generate Point Cloud
				points, colors = self.pcg.getPointCloud(images[0], images[1], images[2])

				if self.generatePointCloud:
					#-- Put point cloud into the queue
					self.pointCloudQueue.put((points, colors))

				end = datetime.datetime.now()
				
				print "Process end: {0}".format(end - begin)
			else:
				time.sleep(0.1)

	def isPointCloudQueueEmpty(self):
		return self.pointCloudQueue.empty()
		
	def getPointCloudIncrement(self):
		""" """
		if not self.isPointCloudQueueEmpty():
			pc = self.pointCloudQueue.get_nowait()
			if pc != None:
				self.pointCloudQueue.task_done()
			return pc
		else:
			return None


@Singleton
class SimpleScan(Scan):

	def _captureThread(self, progressCallback, afterCallback):
		""" """
		ret = False
		self.pcg.resetTheta()

		#-- Setup board
		if self.moveMotor:
			self.driver.board.setSpeedMotor(50)
			self.driver.board.enableMotor()
			time.sleep(0.5)
		else:
			self.driver.board.disableMotor()

		self.driver.board.setLeftLaserOff()
		self.driver.board.setRightLaserOff()

		#-- Main loop
		while self.isRunning:
			if not self.inactive:
				begin = datetime.datetime.now()

				#-- Switch of laser
				if self.pcg.useLeftLaser:
					self.driver.board.setLeftLaserOff()
				if self.pcg.useRightLaser:
					self.driver.board.setRightLaserOff()

				#-- Capture images
				imgRaw = self.driver.camera.captureImage(flush=True, flushValue=2)
				if self.pcg.useLeftLaser:
					self.driver.board.setLeftLaserOn()
					imgLaserLeft = self.driver.camera.captureImage(flush=True, flushValue=2)
				else:
					imgLaserLeft = None
				if self.pcg.useRightLaser:
					self.driver.board.setRightLaserOn()
					imgLaserRight = self.driver.camera.captureImage(flush=True, flushValue=2)
				else:
					imgLaserRight = None

				#-- Move motor
				if self.moveMotor:
					self.driver.board.setRelativePosition(self.pcg.degrees)
					self.driver.board.moveMotor()
				else:
					time.sleep(0.2)
				
				#-- Put images into the queue
				self.imageQueue.put((imgRaw, imgLaserLeft, imgLaserRight))
				
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


@Singleton
class PointCloudGenerator:
	""" 
		Contains all scanning algorithms:

			- Image processing
			- Red line laser detection
			- Point cloud generation and filtering
	"""
	def __init__(self):
		self.theta = 0
		self.points = None
		self.colors = None
		self.driver = Driver.Instance()

		self.imgRaw  = None
		self.imgLas  = None
		self.imgDiff = None
		self.imgBin  = None
		self.imgLine = None

		self.imgType = 0

		self.rad = np.pi / 180.0

		self.roiChanged = False
		self.circleResolution = 30
		self.circleArray = np.array([[np.cos(i*2*np.pi/self.circleResolution) for i in range(self.circleResolution)],
									 [np.sin(i*2*np.pi/self.circleResolution) for i in range(self.circleResolution)],
									 np.zeros(self.circleResolution)])

	def setImageType(self, imgType):
		self.imgType = imgType

	def setUseOpen(self, enable):
		self.openEnable = enable

	def setOpenValue(self, value):
		self.openValue = value

	def setUseThreshold(self, enable):
		self.thresholdEnable = enable

	def setThresholdValue(self, value):
		self.thresholdValue = value

	def setUseCompact(self, enable):
		self.useCompact = enable

	def setViewROI(self, value):
		self.viewROI = value

	def setROIDiameter(self, value):
		self.roiRadius = value / 2.0
		self.roiChanged = True

	def setROIHeight(self, value):
		self.roiHeight = value
		self.roiChanged = True

	def calculateROI(self):
		if hasattr(self, 'roiRadius') and \
		   hasattr(self, 'roiHeight') and \
		   hasattr(self, 'rotationMatrix') and \
		   hasattr(self, 'translationVector') and \
		   hasattr(self, 'fx') and hasattr(self, 'fy') and \
		   hasattr(self, 'cx') and hasattr(self, 'cy'):

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

			self.roiChanged = False

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

	def setLaserTriangulation(self, laserCoordinates, laserOrigin, laserNormal):
		if laserCoordinates is not None:
			self.u1L = laserCoordinates[0][0]
			self.u2L = laserCoordinates[0][1]
			self.u1R = laserCoordinates[1][0]
			self.u2R = laserCoordinates[1][1]

		if laserOrigin is not None:
			self.origin = laserOrigin

		if laserNormal is not None:
			self.normal = laserNormal

	def setPlatformExtrinsics(self, rotationMatrix, translationVector):
		self.rotationMatrix = rotationMatrix
		self.translationVector = translationVector

	def resetTheta(self):
		self.theta = 0

	def getImage(self):
		img = { 'raw' : self.imgRaw,
				'las' : self.imgLas,
				'diff' : self.imgDiff,
				'bin' : self.imgBin,
				'line' : self.imgLine
			  }[self.imgType]

		if img is not None:
			if self.viewROI:
				img = img.copy()
				cv2.rectangle(img, (self.umin, self.vmin), (self.umax, self.vmax), (0, 0, 255), 3)
			
		return img

	def getDiffImage(self, img1, img2):
		""" Returns img1 - img2 """
		r1 = cv2.split(img1)[0]
		r2 = cv2.split(img2)[0]

		return cv2.subtract(r1, r2)

	def imageProcessing(self, image):
		""" """
		#-- Image Processing

		if self.openEnable:
			kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(self.openValue,self.openValue))
			image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

		if self.thresholdEnable:
			image = cv2.threshold(image, self.thresholdValue, 255.0, cv2.THRESH_BINARY)[1]

		return image

	def applyROIMask(self, image):
		mask = np.zeros(image.shape,np.uint8)
		mask[self.vmin:self.vmax,self.umin:self.umax] = image[self.vmin:self.vmax,self.umin:self.umax]

		return mask

	def pointCloudGeneration(self, imageRaw, imageBin, leftLaser=True):
		""" """
		#-- Line generation
		s = imageBin.sum(1)
		v = np.where((s > 2))[0]
		if self.useCompact:
			i = imageBin.argmax(1)
			u = ((i + (s/255.-1) / 2.)[v]).T.astype(int)
		else:
			w = (self.W * imageBin).sum(1)
			u = (w[v] / s[v].T).astype(int)

		self.imgLine = np.zeros_like(imageRaw)
		self.imgLine[v,u] = 255.0

		#-- Obtaining point cloud in camera coordinates
		if leftLaser:
			self.u1 = self.u1L
			self.u2 = self.u2L
			self.alpha = self.alphaLeft
		else:
			self.u1 = self.u1R
			self.u2 = self.u2R
			self.alpha = self.alphaRight

		a = (np.linspace(0,self.width-1,self.width) - self.cx) / self.fx
		b = (np.linspace(0,self.height-1,self.height) - self.cy) / self.fy

		y0 = self.origin[1]
		z0 = self.origin[2]

		ny0 = self.normal[1]
		nz0 = self.normal[2]

		z = (ny0*y0 + nz0*z0) / (ny0*b + nz0)

		zl = z * (1 + (self.u1 - self.cx + ((self.u2-self.u1)/self.height) * np.linspace(0,self.height-1,self.height)) / (self.fx * np.tan(self.alpha)))

		##TODO: Optimize

		Zc = ((np.ones((self.width,self.height)) * zl).T * (1. / (1 + a / np.tan(self.alpha)))).T
		Xc = (a * Zc.T).T
		Yc = b * Zc

		#-- Move point cloud to world coordinates
		R = np.matrix(self.rotationMatrix)
		Rt = R.T
		RT = R.T*np.matrix(self.translationVector).T

		self.Xw = (Rt[0,0] * Xc + Rt[0,1] * Yc + Rt[0,2] * Zc - RT[0]).T
		self.Yw = (Rt[1,0] * Xc + Rt[1,1] * Yc + Rt[1,2] * Zc - RT[1]).T
		self.Zw = (Rt[2,0] * Xc + Rt[2,1] * Yc + Rt[2,2] * Zc - RT[2]).T

		xw = self.Xw[v,u]
		yw = self.Yw[v,u]
		zw = self.Zw[v,u]

		#-- Rotating point cloud
		x = np.array(xw * np.cos(self.theta) - yw * np.sin(self.theta))
		y = np.array(xw * np.sin(self.theta) + yw * np.cos(self.theta))
		z = np.array(zw)

		#-- Return result
		if z.size > 0:
			points = np.concatenate((x,y,z)).reshape(3,z.size).T
			colors = np.copy(imageRaw[v,u])
			rho = np.sqrt(x*x + y*y)
			return points, colors, rho, z
		else:
			return None, None, None, None

	def pointCloudFilter(self, points, colors, rho, z):
		""" """
		#-- Point Cloud Filter
		idx = np.where((z >= 0) &
					   (z <= self.roiHeight) &
					   (rho >= -self.roiRadius) &
					   (rho <= self.roiRadius))[1]

		return points[idx], colors[idx]

	def getPointCloud(self, imageRaw=None, imageLaserLeft=None, imageLaserRight=None):
		""" """
		#-- Check images
		if (imageRaw is not None) and not (self.useLeftLaser^(imageLaserLeft is not None)) and not (self.useRightLaser^(imageLaserRight is not None)):

			points = None
			colors = None
			if self.roiChanged:
				self.calculateROI()
			self.imgRaw = self.applyROIMask(imageRaw)

			if self.useLeftLaser:
				self.imgLas = self.applyROIMask(imageLaserLeft)
				imgDiff = self.getDiffImage(self.imgLas, self.imgRaw)
				self.imgDiff = cv2.merge((imgDiff,imgDiff,imgDiff))

				imgBin = self.imageProcessing(imgDiff)
				self.imgBin = cv2.merge((imgBin,imgBin,imgBin))

				points, colors, rho, z = self.pointCloudGeneration(imageRaw, imgBin, True)

				if points != None and colors != None:
					points, colors = self.pointCloudFilter(points, colors, rho, z)

				if points != None and colors != None:
					if self.points == None and self.colors == None:
						self.points = points
						self.colors = colors
					else:
						self.points = np.concatenate((self.points, points))
						self.colors = np.concatenate((self.colors, colors))

			if self.useRightLaser:
				self.imgLas = self.applyROIMask(imageLaserRight)
				imgDiff = self.getDiffImage(self.imgLas, self.imgRaw)
				self.imgDiff = cv2.merge((imgDiff,imgDiff,imgDiff))

				imgBin = self.imageProcessing(imgDiff)
				self.imgBin = cv2.merge((imgBin,imgBin,imgBin))

				points, colors, rho, z = self.pointCloudGeneration(imageRaw, imgBin, False)

				if points != None and colors != None:
					points, colors = self.pointCloudFilter(points, colors, rho, z)

				if points != None and colors != None:
					if self.points == None and self.colors == None:
						self.points = points
						self.colors = colors
					else:
						self.points = np.concatenate((self.points, points))
						self.colors = np.concatenate((self.colors, colors))

			#-- Update images

			#-- Update Theta
			self.theta -= self.degrees * self.rad

			return points, colors

		else:
			return None, None