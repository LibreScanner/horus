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
STL file mesh loader.
STL is the most common file format used for 3D printing right now.
STLs come in 2 flavors.
	Binary, which is easy and quick to read.
	Ascii, which is harder to read, as can come with windows, mac and unix style newlines.
	The ascii reader has been designed so it has great compatibility with all kinds of formats or slightly broken exports from tools.

This module also contains a function to save objects as an STL file.

http://en.wikipedia.org/wiki/STL_(file_format)
"""

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v3 http://www.gnu.org/licenses/gpl.html"

import sys
import os
import struct
import numpy as np

from horus.util import model

def _loadAscii(m, f):
	cnt = 0
	for lines in f:
		for line in lines.split('\r'):
			if 'vertex' in line:
				cnt += 1
	m._prepareFaceCount(int(cnt) / 3)
	f.seek(5, os.SEEK_SET)
	cnt = 0
	data = [None,None,None]
	for lines in f:
		for line in lines.split('\r'):
			if 'vertex' in line:
				data[cnt] = line.split()[1:]
				cnt += 1
				if cnt == 3:
					m._addFace(float(data[0][0]), float(data[0][1]), float(data[0][2]),
							   float(data[1][0]), float(data[1][1]), float(data[1][2]),
							   float(data[2][0]), float(data[2][1]), float(data[2][2]))
					cnt = 0

def _loadBinary(m, f):
	#Skip the header
	f.read(80-5)
	count = struct.unpack('<I', f.read(4))[0]

	dtype = np.dtype([
			('n', np.float32,(3,)),
			('v', np.float32,(9,)),
			('atttr', '<i2',(1,))])

	data = np.fromfile(f, dtype=dtype , count=count)
	
	m.vertexCount = 3 * count
	m.vertexes = np.reshape(data['v'], (m.vertexCount, 3))

def loadScene(filename):
	obj = model.Model(filename)
	m = obj._addMesh()
	f = open(filename, "rb")
	if f.read(5).lower() == "solid":
		_loadAscii(m, f)
	else:
		_loadBinary(m, f)
	f.close()
	obj._postProcessAfterLoad()
	return obj