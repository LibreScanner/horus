#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
# Copyright (C) 2013 David Braam from Cura Project                      #
#                                                                       #
# Date: June 2014                                                       #
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

"""
The printableObject module contains a printableObject class,
which is used to represent a single object that can be printed.
A single object can have 1 or more meshes which represent different sections for multi-material extrusion.
"""

import time
import math
import os

import numpy
numpy.seterr(all='ignore')

from horus.util import polygon

class printableObject(object):
	"""
	A printable object is an object that can be printed and is on the build platform.
	It contains 1 or more Meshes. Where more meshes are used for multi-extrusion.

	Each object has a 3x3 transformation matrix to rotate/scale the object.
	This object also keeps track of the 2D boundary polygon used for object collision in the objectScene class.
	"""
	def __init__(self, originFilename, isPointCloud):
		self._originFilename = originFilename
		if originFilename is None:
			self._name = 'None'
		else:
			self._name = os.path.basename(originFilename)
		if '.' in self._name:
			self._name = os.path.splitext(self._name)[0]
		self._mesh = None
		self._position = numpy.array([0.0, 0.0])
		self._matrix = numpy.matrix([[1,0,0],[0,1,0],[0,0,1]], numpy.float64)
		self._transformedMin = None
		self._transformedMax = None
		self._transformedSize = None
		self._boundaryCircleSize = None
		self._drawOffset = None
		self._boundaryHull = None

		self._position = [0, 0, 0]
		self._drawOffset = [0, 0, 0]
		self._transformedSize = [0, 0, 0]
		self._boundaryCircleSize = 20.0

		self._isPointCloud = isPointCloud

	def _addMesh(self):
		self._mesh = mesh(self)
		return self._mesh

	def _postProcessAfterLoad(self):
		if not self._isPointCloud:
			self._mesh._calculateNormals()
		self.processMatrix()
		"""if numpy.max(self.getSize()) > 10000.0:
			self._mesh.vertexes /= 1000.0
			self.processMatrix()
		if numpy.max(self.getSize()) < 1.0:
			self._mesh.vertexes *= 1000.0
			self.processMatrix()"""

	def applyMatrix(self, m):
		self._matrix *= m
		self.processMatrix()

	def processMatrix(self):
		self._transformedMin = numpy.array([999999999999,999999999999,999999999999], numpy.float64)
		self._transformedMax = numpy.array([-999999999999,-999999999999,-999999999999], numpy.float64)
		self._boundaryCircleSize = 0

		hull = numpy.zeros((0, 2), numpy.int)

		transformedVertexes = self._mesh.getTransformedVertexes()
		hull = polygon.convexHull(numpy.concatenate((numpy.rint(transformedVertexes[:,0:2]).astype(int), hull), 0))
		transformedMin = transformedVertexes.min(0)
		transformedMax = transformedVertexes.max(0)
		for n in xrange(0, 3):
			self._transformedMin[n] = min(transformedMin[n], self._transformedMin[n])
			self._transformedMax[n] = max(transformedMax[n], self._transformedMax[n])

		#Calculate the boundary circle
		transformedSize = transformedMax - transformedMin
		center = transformedMin + transformedSize / 2.0
		boundaryCircleSize = round(math.sqrt(numpy.max(((transformedVertexes[::,0] - center[0]) * (transformedVertexes[::,0] - center[0])) + ((transformedVertexes[::,1] - center[1]) * (transformedVertexes[::,1] - center[1])) + ((transformedVertexes[::,2] - center[2]) * (transformedVertexes[::,2] - center[2])))), 3)
		self._boundaryCircleSize = max(self._boundaryCircleSize, boundaryCircleSize)

		self._transformedSize = self._transformedMax - self._transformedMin
		self._drawOffset = (self._transformedMax + self._transformedMin) / 2
		self._drawOffset[2] = self._transformedMin[2]
		self._transformedMax -= self._drawOffset
		self._transformedMin -= self._drawOffset

		self._boundaryHull = polygon.minkowskiHull((hull.astype(numpy.float32) - self._drawOffset[0:2]), numpy.array([[-1,-1],[-1,1],[1,1],[1,-1]],numpy.float32))

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
		return numpy.array([
			numpy.linalg.norm(self._matrix[::,0].getA().flatten()),
			numpy.linalg.norm(self._matrix[::,1].getA().flatten()),
			numpy.linalg.norm(self._matrix[::,2].getA().flatten())], numpy.float64);

	def setScale(self, scale, axis, uniform):
		currentScale = numpy.linalg.norm(self._matrix[::,axis].getA().flatten())
		scale /= currentScale
		if scale == 0:
			return
		if uniform:
			matrix = [[scale,0,0], [0, scale, 0], [0, 0, scale]]
		else:
			matrix = [[1.0,0,0], [0, 1.0, 0], [0, 0, 1.0]]
			matrix[axis][axis] = scale
		self.applyMatrix(numpy.matrix(matrix, numpy.float64))

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
		self.applyMatrix(numpy.matrix(matrix, numpy.float64))

	def resetScale(self):
		x = 1/numpy.linalg.norm(self._matrix[::,0].getA().flatten())
		y = 1/numpy.linalg.norm(self._matrix[::,1].getA().flatten())
		z = 1/numpy.linalg.norm(self._matrix[::,2].getA().flatten())
		self.applyMatrix(numpy.matrix([[x,0,0],[0,y,0],[0,0,z]], numpy.float64))


class mesh(object):
	"""
	A mesh is a list of 3D triangles build from vertexes. Each triangle has 3 vertexes.

	A "VBO" can be associated with this object, which is used for rendering this object.
	"""
	def __init__(self, obj):
		self.vertexes = None
		self.colors = None
		self.vertexCount = 0
		self.vbo = None
		self._obj = obj

	def _addVertex(self, x, y, z, r, g, b):
		n = self.vertexCount
		self.vertexes[n][0] = x
		self.vertexes[n][1] = y
		self.vertexes[n][2] = z
		self.colors[n][0] = r
		self.colors[n][1] = g
		self.colors[n][2] = b
		self.vertexCount += 1
		#print  self.vertexCount

	def _addFace(self, x0, y0, z0, x1, y1, z1, x2, y2, z2):
		n = self.vertexCount
		self.vertexes[n][0] = x0
		self.vertexes[n][1] = y0
		self.vertexes[n][2] = z0
		n += 1
		self.vertexes[n][0] = x1
		self.vertexes[n][1] = y1
		self.vertexes[n][2] = z1
		n += 1
		self.vertexes[n][0] = x2
		self.vertexes[n][1] = y2
		self.vertexes[n][2] = z2
		self.vertexCount += 3

	def _prepareVertexCount(self, vertexNumber):
		#Set the amount of faces before loading data in them. This way we can create the numpy arrays before we fill them.
		self.vertexes = numpy.zeros((vertexNumber, 3), numpy.float32)
		self.colors = numpy.zeros((vertexNumber, 3), numpy.int32)
		self.normal = numpy.zeros((vertexNumber, 3), numpy.float32)
		self.vertexCount = 0

	def _prepareFaceCount(self, faceNumber):
		#Set the amount of faces before loading data in them. This way we can create the numpy arrays before we fill them.
		self.vertexes = numpy.zeros((faceNumber*3, 3), numpy.float32)
		self.normal = numpy.zeros((faceNumber*3, 3), numpy.float32)
		self.vertexCount = 0

	def _calculateNormals(self):
		#Calculate the normals
		tris = self.vertexes.reshape(self.vertexCount / 3, 3, 3)
		normals = numpy.cross( tris[::,1 ] - tris[::,0]  , tris[::,2 ] - tris[::,0] )
		lens = numpy.sqrt( normals[:,0]**2 + normals[:,1]**2 + normals[:,2]**2 )
		normals[:,0] /= lens
		normals[:,1] /= lens
		normals[:,2] /= lens
		
		n = numpy.zeros((self.vertexCount / 3, 9), numpy.float32)
		n[:,0:3] = normals
		n[:,3:6] = normals
		n[:,6:9] = normals
		self.normal = n.reshape(self.vertexCount, 3)
		self.invNormal = -self.normal

	def _vertexHash(self, idx):
		v = self.vertexes[idx]
		return int(v[0] * 100) | int(v[1] * 100) << 10 | int(v[2] * 100) << 20

	def _idxFromHash(self, map, idx):
		vHash = self._vertexHash(idx)
		for i in map[vHash]:
			if numpy.linalg.norm(self.vertexes[i] - self.vertexes[idx]) < 0.001:
				return i

	def getTransformedVertexes(self, applyOffsets = False):
		if applyOffsets:
			pos = self._obj._position.copy()
			pos.resize((3))
			pos[2] = self._obj.getSize()[2] / 2
			offset = self._obj._drawOffset.copy()
			offset[2] += self._obj.getSize()[2] / 2
			return (numpy.matrix(self.vertexes, copy = False) * numpy.matrix(self._obj._matrix, numpy.float32)).getA() - offset + pos
		return (numpy.matrix(self.vertexes, copy = False) * numpy.matrix(self._obj._matrix, numpy.float32)).getA()