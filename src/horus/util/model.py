#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014-2015 Mundo Reader S.L.                             #
# Copyright (C) 2013 David Braam from Cura Project                      #
#                                                                       #
# Date: June 2014                                                       #
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
import time
import math

import numpy as np
np.seterr(all='ignore')

class Model(object):
	"""
	Each object has a Mesh and a 3x3 transformation matrix to rotate/scale the object.
	"""
	def __init__(self, originFilename, isPointCloud=False):
		self._originFilename = originFilename
		if originFilename is None:
			self._name = 'None'
		else:
			self._name = os.path.basename(originFilename)
		if '.' in self._name:
			self._name = os.path.splitext(self._name)[0]
		self._mesh = None
		self._position = np.array([0.0, 0.0, 0.0])
		self._matrix = np.matrix([[1,0,0],[0,1,0],[0,0,1]], np.float64)
		self._transformedMin = None
		self._transformedMax = None
		self._transformedSize = np.array([0.0, 0.0, 0.0])
		self._boundaryCircleSize = 20.0
		self._drawOffset = np.array([0.0, 0.0, 0.0])

		self._isPointCloud = isPointCloud

	def _addMesh(self):
		self._mesh = Mesh(self)
		return self._mesh

	def _postProcessAfterLoad(self):
		#if not self._isPointCloud:
		#	self._mesh._calculateNormals()
		self.processMatrix()

	def applyMatrix(self, m):
		self._matrix *= m
		self.processMatrix()

	def processMatrix(self):
		self._transformedMin = np.array([np.inf,np.inf,np.inf], np.float64)
		self._transformedMax = np.array([-np.inf,-np.inf,-np.inf], np.float64)
		self._boundaryCircleSize = 0

		transformedVertexes = self._mesh.getTransformedVertexes()
		transformedMin = transformedVertexes.min(0)
		transformedMax = transformedVertexes.max(0)
		for n in xrange(0, 3):
			self._transformedMin[n] = min(transformedMin[n], self._transformedMin[n])
			self._transformedMax[n] = max(transformedMax[n], self._transformedMax[n])

		#Calculate the boundary circle
		transformedSize = transformedMax - transformedMin
		center = transformedMin + transformedSize / 2.0
		boundaryCircleSize = round(math.sqrt(np.max(((transformedVertexes[::,0] - center[0]) * (transformedVertexes[::,0] - center[0])) + ((transformedVertexes[::,1] - center[1]) * (transformedVertexes[::,1] - center[1])) + ((transformedVertexes[::,2] - center[2]) * (transformedVertexes[::,2] - center[2])))), 3)
		self._boundaryCircleSize = max(self._boundaryCircleSize, boundaryCircleSize)

		self._transformedSize = self._transformedMax - self._transformedMin
		self._drawOffset = (self._transformedMax + self._transformedMin) / 2
		self._drawOffset[2] = self._transformedMin[2]
		self._transformedMax -= self._drawOffset
		self._transformedMin -= self._drawOffset

	def getName(self):
		return self._name
	def getOriginFilename(self):
		return self._originFilename
	def getPosition(self):
		return self._position
	def setPosition(self, newPos):
		self._position = newPos
	def getMatrix(self):
		return self._matrix

	def getMaximum(self):
		return self._transformedMax
	def getMinimum(self):
		return self._transformedMin
	def getSize(self):
		return self._transformedSize
	def getDrawOffset(self):
		return self._drawOffset
	def getBoundaryCircle(self):
		return self._boundaryCircleSize

	def isPointCloud(self):
		return self._isPointCloud

	def getScale(self):
		return np.array([
			np.linalg.norm(self._matrix[::,0].getA().flatten()),
			np.linalg.norm(self._matrix[::,1].getA().flatten()),
			np.linalg.norm(self._matrix[::,2].getA().flatten())], np.float64);

	def setScale(self, scale, axis, uniform):
		currentScale = np.linalg.norm(self._matrix[::,axis].getA().flatten())
		scale /= currentScale
		if scale == 0:
			return
		if uniform:
			matrix = [[scale,0,0], [0, scale, 0], [0, 0, scale]]
		else:
			matrix = [[1.0,0,0], [0, 1.0, 0], [0, 0, 1.0]]
			matrix[axis][axis] = scale
		self.applyMatrix(np.matrix(matrix, np.float64))

	def setSize(self, size, axis, uniform):
		scale = self.getSize()[axis]
		scale = size / scale
		if scale == 0:
			return
		if uniform:
			matrix = [[scale,0,0], [0, scale, 0], [0, 0, scale]]
		else:
			matrix = [[1,0,0], [0, 1, 0], [0, 0, 1]]
			matrix[axis][axis] = scale
		self.applyMatrix(np.matrix(matrix, np.float64))

	def resetScale(self):
		x = 1/np.linalg.norm(self._matrix[::,0].getA().flatten())
		y = 1/np.linalg.norm(self._matrix[::,1].getA().flatten())
		z = 1/np.linalg.norm(self._matrix[::,2].getA().flatten())
		self.applyMatrix(np.matrix([[x,0,0],[0,y,0],[0,0,z]], np.float64))


class Mesh(object):
	"""
	A mesh is a list of 3D triangles build from vertexes. Each triangle has 3 vertexes. It can be also a point cloud.
	A "VBO" can be associated with this object, which is used for rendering this object.
	"""
	def __init__(self, obj):
		self.vertexes = None
		self.colors = None
		self.normal = None
		self.vertexCount = 0
		self.vbo = None
		self._obj = obj

	def _addVertex(self, x, y, z, r=255, g=255, b=255):
		n = self.vertexCount
		self.vertexes[n], self.colors[n] = (x, y, z), (r, g, b)
		self.vertexCount += 1

	def _addFace(self, x0, y0, z0, x1, y1, z1, x2, y2, z2):
		n = self.vertexCount
		self.vertexes[n], self.vertexes[n+1], self.vertexes[n+2] = (x0, y0, z0), (x1, y1, z1), (x2, y2, z2)
		self.vertexCount += 3

	def _prepareVertexCount(self, vertexNumber):
		#Set the amount of vertex before loading data in them. This way we can create the np arrays before we fill them.
		self.vertexes = np.zeros((vertexNumber, 3), np.float32)
		self.colors = np.zeros((vertexNumber, 3), np.int32)
		self.normal = np.zeros((vertexNumber, 3), np.float32)
		self.vertexCount = 0

	def _prepareFaceCount(self, faceNumber):
		#Set the amount of faces before loading data in them. This way we can create the np arrays before we fill them.
		self.vertexes = np.zeros((faceNumber*3, 3), np.float32)
		self.normal = np.zeros((faceNumber*3, 3), np.float32)
		self.vertexCount = 0

	def _calculateNormals(self):
		#Calculate the normals
		tris = self.vertexes.reshape(self.vertexCount / 3, 3, 3)
		normals = np.cross( tris[::,1 ] - tris[::,0]  , tris[::,2 ] - tris[::,0] )
		lens = np.sqrt( normals[:,0]**2 + normals[:,1]**2 + normals[:,2]**2 )
		normals[:,0] /= lens
		normals[:,1] /= lens
		normals[:,2] /= lens
		
		n = np.zeros((self.vertexCount / 3, 9), np.float32)
		n[:,0:3] = normals
		n[:,3:6] = normals
		n[:,6:9] = normals
		self.normal = n.reshape(self.vertexCount, 3)

	def _vertexHash(self, idx):
		v = self.vertexes[idx]
		return int(v[0] * 100) | int(v[1] * 100) << 10 | int(v[2] * 100) << 20

	def _idxFromHash(self, map, idx):
		vHash = self._vertexHash(idx)
		for i in map[vHash]:
			if np.linalg.norm(self.vertexes[i] - self.vertexes[idx]) < 0.001:
				return iz

	def getTransformedVertexes(self, applyOffsets = False):
		if applyOffsets:
			pos = self._obj._position.copy()
			pos.resize((3))
			pos[2] = self._obj.getSize()[2] / 2
			offset = self._obj._drawOffset.copy()
			offset[2] += self._obj.getSize()[2] / 2
			return (np.matrix(self.vertexes, copy = False) * np.matrix(self._obj._matrix, np.float32)).getA() - offset + pos
		return (np.matrix(self.vertexes, copy = False) * np.matrix(self._obj._matrix, np.float32)).getA()