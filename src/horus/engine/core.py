#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: March & September 2014                                          #
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
import numpy as np

class Core:
	""" """
	def __init__(self):
		""" """
		self._initialize()

	def _initialize(self):
		self.points = None
		self.colors = None
		
		self.imgRaw  = None
		self.imgLas  = None
		self.imgDiff = None
		self.imgBin  = None
		self.imgLine = None

		self.points = None
		self.colors = None

		self.imgType = 0

		self.rad = math.pi / 180.0

	def resetTheta(self):
		self.theta = 0

	def setImageType(self, imgType):
		""" """
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

	def setMinR(self, value):
		self.rhoMin = value

	def setMaxR(self, value):
		self.rhoMax = value

	def setMinH(self, value):
		self.hMin = value

	def setMaxH(self, value):
		self.hMax = value

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

	def setIntrinsics(self, cameraMatrix, distortionVector):
		self.cameraMatrix = cameraMatrix
		self.distortionVector = distortionVector
		if cameraMatrix is not None:
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

	def setExtrinsics(self, rotationMatrix, translationVector):
		self.rotationMatrix = rotationMatrix
		self.translationVector = translationVector

	def getImage(self):
		""" """
		return { 'raw' : self.imgRaw,
				 'las' : self.imgLas,
				 'diff' : self.imgDiff,
				 'bin' : self.imgBin,
				 'line' : self.imgLine
				}[self.imgType]

	def getDiffImage(self, img1, img2):
		""" """
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

		zl = z * (1 + (self.u1 - self.cx + ((self.u2-self.u1)/self.height) * np.linspace(0,self.height-1,self.height)) / (self.fx * math.tan(self.alpha)))

		##TODO: Optimize

		Zc = ((np.ones((self.width,self.height)) * zl).T * (1. / (1 + a / math.tan(self.alpha)))).T
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
		x = np.array(xw * math.cos(self.theta) - yw * math.sin(self.theta))
		y = np.array(xw * math.sin(self.theta) + yw * math.cos(self.theta))
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
		idx = np.where((z >= self.hMin) &
					   (z <= self.hMax) &
					   (rho >= self.rhoMin) &
					   (rho <= self.rhoMax))[1]

		return points[idx], colors[idx]

	def getPointCloud(self, imageRaw=None, imageLaserLeft=None, imageLaserRight=None):
		""" """
		#-- Check images
		if (imageRaw is not None) and not (self.useLeftLaser^(imageLaserLeft is not None)) and not (self.useRightLaser^(imageLaserRight is not None)):

			points = None
			colors = None
			self.imgRaw = imageRaw

			if self.useLeftLaser:
				self.imgLas = imageLaserLeft
				imgDiff = self.getDiffImage(imageLaserLeft, imageRaw)
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
				self.imgLas = imageLaserRight
				imgDiff = self.getDiffImage(imageLaserRight, imageRaw)
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