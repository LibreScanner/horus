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

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v3 http://www.gnu.org/licenses/gpl.html"

import sys
import os
import struct
import time

from horus.util import model

def _loadAscii(m, cnt, idx, body):
	for i in range(1,cnt):
		data = body[i].split(' ')
		m._addVertex(float(data[idx[0]]),float(data[idx[1]]),float(data[idx[2]]),int(data[idx[3]]),int(data[idx[4]]),int(data[idx[5]]))

def _loadBinary(m, cnt, idx, step, format, body):
	a = b = 0
	for i in range(cnt):
		b = a+step
		data = struct.unpack(format, body[step*i:step*(i+1)])
		m._addVertex(float(data[idx[0]]),float(data[idx[1]]),float(data[idx[2]]),int(data[idx[3]]),int(data[idx[4]]),int(data[idx[5]]))
		a = b

def loadScene(filename):
	obj = model.Model(filename, isPointCloud=True)
	m = obj._addMesh()
	f = open(filename, "rb")

	cnt = 0
	idx = []
	pidx = []
	ridx = ['x', 'y', 'z', 'red', 'green', 'blue'] #-- Current addVertex prototype
	step = 0
	format = ""
	sections = f.read().split('end_header\n')
	header = sections[0].split('element face ')[0].split('\n') #-- Discart faces

	if header[0] == 'ply':

		for line in header:
			if 'element vertex ' in line:
				cnt = int(line.split('element vertex ')[1])
			elif 'property ' in line:
				props = line.split(' ')
				pidx += [props[2]]
				if props[1] == 'float':
					format += 'f'
					step += 4
				if props[1] == 'uchar':
					format += 'B'
					step += 1

		for item in ridx:
			if item in pidx:
				idx += [pidx.index(item)]

		codec = None
		for line in header:
			if 'format ' in line:
				codec = line.split(' ')[1]

		m._prepareVertexCount(cnt)

		if codec is not None:
			if codec == 'ascii':
				_loadAscii(m, cnt, idx, sections[1].split('\n'))
			elif codec == 'binary_big_endian':
				_loadBinary(m, cnt, idx, step, '>'+format, sections[1])
			elif codec == 'binary_little_endian':
				_loadBinary(m, cnt, idx, step, '<'+format, sections[1])
	else:
		print "Error: incorrect file format."

	f.close()
	obj._postProcessAfterLoad()
	return obj

def saveScene(filename, _object):
	f = open(filename, 'wb')
	saveSceneStream(f, _object)
	f.close()

def saveSceneStream(stream, _object):
	m = _object._mesh

	binary = False

	if m is not None:
		frame  = "ply\n"
		if binary:
			frame += "format ascii 1.0\n"
		else:
			frame += "format binary_little_endian 1.0\n"
		frame += "element vertex {0}\n".format(m.vertexCount)
		frame += "property float x\n"
		frame += "property float y\n"
		frame += "property float z\n"
		frame += "property uchar red\n"
		frame += "property uchar green\n"
		frame += "property uchar blue\n"
		frame += "element face 0\n"
		frame += "property list uchar int vertex_indices\n"
		frame += "end_header\n"
		if binary:
			pass
		else:
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