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
import math
import numpy as np

class Core:
	""" """
	def __init__(self, degrees):
		""" """
		self.points = None
		self.colors = None

		#-- Image type parameters
		self.imgType = 0
		
		self.imgRaw = None
		self.imgLas = None
		self.imgDiff = None
		self.imgBin = None

		#-- Image Processing Parameters
		self.blurEnable = True
		self.blurValue = 4

		self.openEnable = True
		self.openValue = 5

		self.colorMin = np.array([0, 180, 30],np.uint8)
		self.colorMax = np.array([180, 250, 140],np.uint8)

		#-- Point Cloud Parameters
		self.modeCW = True

		self.fx = 1150
		self.fy = 1150
		self.cx = 269
		self.cy = 240
		self.zs = 270
		self.ho = 50
		self.alpha = 60

		self.useCompact = True

		self.rhoMin = -60
		self.rhoMax = 60
		self.hMin = 0
		self.hMax = 80

		self.zOffset = 0

		self.width = 640
		self.height = 480

		self.degrees = degrees

		self.theta = 0

		#-- Constant Parameters initialization
		self.rad = math.pi / 180.0
		
		alpha = self.alpha * self.rad
		
		A = self.zs / math.sin(alpha)
		B = self.fx / math.tan(alpha)
		
		self.theta = 0
		self.points = None
		self.colors = None
		
		self.M_rho = np.zeros((self.height, self.width))
		self.M_z = np.zeros((self.height, self.width))
		
		for j in xrange(self.height):
			v = self.cy-j
			for i in xrange(self.width):
				u = i-self.cx
				self.M_rho[j,i] = rho = A*u/(u+B)
				self.M_z[j,i] = self.ho + (self.zs-rho*math.sin(alpha))*v/self.fy
				
		print "----------------R-------------"
		print self.M_rho
		print "----------------Z-------------"
		print self.M_z

		self.W = np.matrix(np.ones(self.height)).T * np.matrix(np.arange(self.width).reshape((self.width)))

	def setBlur(self, enable, value):
		self.blurEnable = enable
		self.blurValue = value

	def setOpen(self, enable, value):
		self.openEnable = enable
		self.openValue = value

	def setHSVRange(self, minH, minS, minV, maxH, maxS, maxV):
		self.colorMin = np.array([minH,minS,minV],np.uint8)
		self.colorMax = np.array([maxH,maxS,maxV],np.uint8)

	def setCalibrationParams(self, fx, fy, cx, cy, zs, ho):
		self.fx = fx
		self.fy = fy
		self.cx = cx
		self.cy = cy
		self.zs = zs
		self.ho = ho

	def setUseCompactAlgorithm(self, useCompact):
		self.useCompact = useCompact

	def setRangeFilter(self, rhoMin, rhoMax, hMin, hMax):
		self.rhoMin = rhoMin
		self.rhoMax = rhoMax
		self.hMin = hMin
		self.hMax = hMax

	def setZOffset(self, zOffset):
		self.zOffset = zOffset

	def getImage(self):
		""" """
		return { 0 : self.imgRaw,
				 1 : self.imgLas,
				 2 : self.imgDiff,
				 3 : self.imgBin
				}[self.imgType]

	def setImageType(self, imgType):
		""" """
		self.imgType = imgType

	def getDiffImage(self, img1, img2):
		""" """
		return cv2.absdiff(img1, img2)

	def imageProcessing(self, image):
		""" """
		#-- Image Processing
		if self.blurEnable:
			image = cv2.blur(image,(self.blurValue,self.blurValue))

		if self.openEnable:
			kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(self.openValue,self.openValue))
			image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

		#image = cv2.bitwise_not(image) # TODO: remove

		imageHSV = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

		self.src = cv2.inRange(imageHSV, self.colorMin, self.colorMax)

		temp = np.zeros_like(image)
		temp[:,:,0] = self.src
		temp[:,:,1] = self.src
		temp[:,:,2] = self.src
		self.imgBin = temp

		return self.src

	def pointCloudGeneration(self, imageDiff, imageRaw):
		""" """
		#-- Point Cloud Generation
		s = self.src.sum(1)
		v = np.nonzero(s)[0]
		if self.useCompact:
			i = self.src.argmax(1)
			l = ((i + (s/255-1) / 2)[v]).T.astype(int)
		else:
			self.w = (np.array(self.W)*np.array(imageDiff)).sum(1)
			l = (w[v] / s[v].T).astype(int)

		#-- Obtaining parameters
		rho = self.M_rho[v,l]
		thetaR = self.theta * self.rad
		x = rho * math.cos(thetaR)
		y = rho * math.sin(thetaR)
		z = self.M_z[v,l] + self.zOffset
		points = np.concatenate((x,y,z)).reshape(3,z.size).T
		colors = np.copy(imageRaw[v,l])

		return points, colors

	def pointCloudFilter(self, points, colors):
		""" """

		z = 0
		rho = 100

		#-- Point Cloud Filter
		idx = np.where((z > self.hMin) &
					   (z < self.hMax) &
					   (rho > self.rhoMin) &
					   (rho < self.rhoMax))[0]
		if len(idx):
			points = points[idx]
			colors = colors[idx]

		return points, colors

	def getPointCloud(self, imageRaw, imageDiff):
		""" """
 		
 		self.imgRaw = imageRaw
 		self.imgDiff = imageDiff

		src = self.imageProcessing(imageDiff)

		points, colors = self.pointCloudGeneration(imageDiff, imageRaw)

		if points != None and colors != None:
			points, colors = self.pointCloudFilter(points, colors)

		if points != None and colors != None:
			if self.points == None and self.colors == None:
				self.points = points
				self.colors = colors
			else:
				self.points = np.concatenate((self.points, points))
				self.colors = np.concatenate((self.colors, colors))

 		self.theta += self.degrees

		return points, colors

	def toPLY(self):
		"""
		Returns PLY string
		"""
		if self.points != None and self.colors != None and len(self.points) == len(self.colors):
			n = len(self.points)
			# Generate Header
			frame  = "ply\nformat ascii 1.0\n"
			frame += "element vertex {0}\n".format(n)
			frame += "property float x\n"
			frame += "property float y\n"
			frame += "property float z\n"
			frame += "property uchar diffuse_red\n"
			frame += "property uchar diffuse_green\n"
			frame += "property uchar diffuse_blue\n"
			frame += "element face 0\n"
			frame += "property list uchar int vertex_indices\n"
			frame += "end_header\n"
			#Generate Points
			for i in range(n):
				frame += "{0} ".format(self.points[i,0])
				frame += "{0} ".format(self.points[i,1])
				frame += "{0} ".format(self.points[i,2])
				frame += "{0} ".format(self.colors[i,0])
				frame += "{0} ".format(self.colors[i,1])
				frame += "{0}\n".format(self.colors[i,2])

			return frame