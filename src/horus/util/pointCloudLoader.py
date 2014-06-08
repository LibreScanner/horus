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

import os

from horus.util.pointCloudLoaders import ply

def loadSupportedExtensions():
	""" return a list of supported file extensions for loading. """
	return ['.ply']

def saveSupportedExtensions():
	""" return a list of supported file extensions for saving. """
	return ['.ply']

def loadPointCloud(filename):
	"""
	PLY files contains a color pointcloud.
	"""
	ext = os.path.splitext(filename)[1].lower()
	if ext == '.ply':
		return ply.loadScene(filename)
	print 'Error: Unknown point cloud extension: %s' % (ext)
	return []

def savePointCloud(filename, objects):
	"""
	Save a list of objects into the file given by the filename. Use the filename extension to find out the file format.
	"""
	ext = os.path.splitext(filename)[1].lower()
	if ext == '.ply':
		ply.saveScene(filename, objects)
		return
	print 'Error: Unknown point cloud extension: %s' % (ext)
