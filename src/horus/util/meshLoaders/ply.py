#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
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
PLY file point cloud loader.

	- Binary, which is easy and quick to read.
	- Ascii, which is harder to read, as can come with windows, mac and unix style newlines.

This module also contains a function to save objects as an PLY file.

http://en.wikipedia.org/wiki/PLY_(file_format)
"""

import sys
import os
import struct
import time

from horus.util import printableObject

def _loadAscii(m, f): # TODO: improve parser: normals, colors, faces, etc.
	cnt = 0
	sections = f.read().split('end_header')

	header = sections[0].split('\n')
	for line in header:
		if 'element vertex ' in line:
			cnt = int(line.split('element vertex ')[1])

	m._prepareVertexCount(int(cnt))

	body = sections[1].split('\n')
	for i in range(1,cnt):
		data = body[i].split(' ')
		if len(data) == 6: # colors
			m._addVertex(float(data[0]),float(data[1]),float(data[2]),int(data[3]),int(data[4]),int(data[5]))
		if len(data) == 11: # normals
			m._addVertex(float(data[0]),float(data[1]),float(data[2]),int(data[6]),int(data[7]),int(data[8]))

def _loadBinary(m, f):
	pass

def loadScene(filename):
	obj = printableObject.printableObject(filename, isPointCloud=True)
	m = obj._addMesh()
	f = open(filename, "rb")
	if f.read(3).lower() == "ply":
		_loadAscii(m, f)
	else:
		pass
		#_loadBinary(m, f)
	f.close()
	obj._postProcessAfterLoad()
	return obj

def saveScene(filename, _object):
	f = open(filename, 'wb')
	saveSceneStream(f, _object)
	f.close()

def saveSceneStream(stream, _object):
	m = _object._mesh

	if m is not None:
		frame  = "ply\nformat ascii 1.0\n"
		frame += "element vertex {0}\n".format(m.vertexCount)
		frame += "property float x\n"
		frame += "property float y\n"
		frame += "property float z\n"
		frame += "property uchar diffuse_red\n"
		frame += "property uchar diffuse_green\n"
		frame += "property uchar diffuse_blue\n"
		frame += "element face 0\n"
		frame += "property list uchar int vertex_indices\n"
		frame += "end_header\n"
		if m.vertexCount > 0:
			points = m.vertexes
			colors = m.colors
			for i in range(m.vertexCount):
				frame += "{0} ".format(points[i,0])
				frame += "{0} ".format(points[i,1])
				frame += "{0} ".format(points[i,2])
				frame += "{0} ".format(colors[i,0])
				frame += "{0} ".format(colors[i,1])
				frame += "{0}\n".format(colors[i,2])
		stream.write(frame)
