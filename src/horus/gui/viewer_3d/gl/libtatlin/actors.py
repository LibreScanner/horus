#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
# Copyright (C) 2013 Guillaume Seguin                                   #
# Copyright (C) 2011 Denis Kobozev                                      #
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

import time
import math
import logging

import random

from ctypes import sizeof

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

import numpy as np

def vec(*args):
    return (GLfloat * len(args))(*args)

def compile_display_list(func, *options):
    display_list = glGenLists(1)
    glNewList(display_list, GL_COMPILE)
    func(*options)
    glEndList()
    return display_list

def numpy2vbo(nparray, target = GL_ARRAY_BUFFER, usage = GL_STATIC_DRAW, use_vbos = True):
    vbo = create_buffer(nparray.nbytes, target = target, usage = usage, vbo = use_vbos)
    vbo.bind()
    vbo.set_data(nparray.ctypes.data)
    return vbo

def triangulate_rectangle(i1, i2, i3, i4):
    return [i1, i4, i3, i3, i2, i1]

def triangulate_box(i1, i2, i3, i4,
                    j1, j2, j3, j4):
    return [i1, i2, j2, j2, j1, i1, i2, i3, j3, j3, j2, i2,
            i3, i4, j4, j4, j3, i3, i4, i1, j1, j1, j4, i4]

class BoundingBox(object):
    """
    A rectangular box (cuboid) enclosing a 3D model, defined by lower and upper corners.
    """
    def __init__(self, upper_corner, lower_corner):
        self.upper_corner = upper_corner
        self.lower_corner = lower_corner

    @property
    def width(self):
        width = abs(self.upper_corner[0] - self.lower_corner[0])
        return round(width, 2)

    @property
    def depth(self):
        depth = abs(self.upper_corner[1] - self.lower_corner[1])
        return round(depth, 2)

    @property
    def height(self):
        height = abs(self.upper_corner[2] - self.lower_corner[2])
        return round(height, 2)

class Platform(object):
    """
    Platform on which models are placed.
    """
    graduations_major = 10

    def __init__(self, build_dimensions, light = False):
        self.light = light
        self.width = build_dimensions[0]
        self.depth = build_dimensions[1]
        self.height = build_dimensions[2]
        self.xoffset = build_dimensions[3]
        self.yoffset = build_dimensions[4]
        self.zoffset = build_dimensions[5]

        #self.color_grads_minor = (0xaf / 255, 0xdf / 255, 0x5f / 255, 0.1)
        #self.color_grads_interm = (0xaf / 255, 0xdf / 255, 0x5f / 255, 0.2)
        #self.color_grads_major = (0xaf / 255, 0xdf / 255, 0x5f / 255, 0.33)

        self.color_grads_minor = (1.0, 1.0, 1.0, 0.1)
        self.color_grads_interm = (1.0, 1.0, 1.0, 0.2)
        self.color_grads_major = (1.0, 1.0, 1.0, 0.3)

        self.initialized = False
        self.loaded = True

    def init(self):
        self.display_list = compile_display_list(self.draw)
        self.initialized = True

    def draw(self):
        glPushMatrix()

        glTranslatef(self.xoffset, self.yoffset, self.zoffset)

        def color(i):
            if i % self.graduations_major == 0:
                glColor4f(*self.color_grads_major)
            elif i % (self.graduations_major / 2) == 0:
                glColor4f(*self.color_grads_interm)
            else:
                if self.light: return False
                glColor4f(*self.color_grads_minor)
            return True

        # draw the grid
        glBegin(GL_LINES)
        for i in range(0, int(math.ceil(self.width + 1))):
            if color(i):
                glVertex3f(float(i), 0.0, 0.0)
                glVertex3f(float(i), self.depth, 0.0)

        for i in range(0, int(math.ceil(self.depth + 1))):
            if color(i):
                glVertex3f(0, float(i), 0.0)
                glVertex3f(self.width, float(i), 0.0)
        glEnd()

        glPopMatrix()

    def display(self, mode_2d=False):
        glCallList(self.display_list)

class Model(object):
    """
    Parent class for models that provides common functionality.
    """
    AXIS_X = (1, 0, 0)
    AXIS_Y = (0, 1, 0)
    AXIS_Z = (0, 0, 1)

    letter_axis_map = {
        'x': AXIS_X,
        'y': AXIS_Y,
        'z': AXIS_Z,
    }

    axis_letter_map = dict([(v, k) for k, v in letter_axis_map.items()])

    def __init__(self, offset_x=0, offset_y=0):
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.init_model_attributes()

    def init_model_attributes(self):
        """
        Set/reset saved properties.
        """
        self.invalidate_bounding_box()
        self.modified = False

    def invalidate_bounding_box(self):
        self._bounding_box = None

    @property
    def bounding_box(self):
        """
        Get a bounding box for the model.
        """
        if self._bounding_box is None:
            self._bounding_box = self._calculate_bounding_box()
        return self._bounding_box

    def _calculate_bounding_box(self):
        """
        Calculate an axis-aligned box enclosing the model.
        """
        # swap rows and columns in our vertex arrays so that we can do max and
        # min on axis 1
        xyz_rows = self.vertices.reshape(-1, order='F').reshape(3, -1)
        lower_corner = xyz_rows.min(1)
        upper_corner = xyz_rows.max(1)
        box = BoundingBox(upper_corner, lower_corner)
        return box

    @property
    def width(self):
        return self.bounding_box.width

    @property
    def depth(self):
        return self.bounding_box.depth

    @property
    def height(self):
        return self.bounding_box.height

def movement_angle(src, dst, precision=0):
    x = dst[0] - src[0]
    y = dst[1] - src[1]
    angle = math.degrees(math.atan2(y, -x))  # negate x for clockwise rotation angle
    return round(angle, precision)

def get_next_move(ply, layer_idx, gline_idx):
    gline_idx += 1
    while layer_idx < len(ply.all_layers):
        layer = ply.all_layers[layer_idx]
        while gline_idx < len(layer):
            gline = layer[gline_idx]
            if gline.is_move:
                return gline
            gline_idx += 1
        layer_idx += 1
        gline_idx = 0
    return None
    
class PLYModel(Model):
    """
    Model for displaying PLY data.
    """
    n = 0
    vbo_points = None
    vbo_colors = None
    points = None
    colors = None
    initialized = False
    
    def init(self):
        glPointSize(2)
        self.initialized = True
        
    def add_points(self, points, colors):
		
        if self.points == None and self.colors == None:
            self.points = points
            self.colors = colors
        else:
            self.points = np.concatenate((self.points, points))
            self.colors = np.concatenate((self.colors, colors))

        self.n += len(points)
        #print self.n
        
    def create_vbo(self):
		#self.updating = True
        if self.points != None and self.colors != None:
            self.points_array = np.require(self.points, np.float32, 'F')
            self.colors_array = np.require(self.colors, np.uint8)
            self.vbo_points = vbo.VBO(self.points_array)
            self.vbo_colors = vbo.VBO(self.colors_array)
			#self.vbo_points.set_array(self.points)
            #self.vbo_colors.set_array(self.colors)
		#self.updating = False

    # ------------------------------------------------------------------------
    # DRAWING
    # ------------------------------------------------------------------------

    def display(self, mode_2d=False):
		
		if self.vbo_points != None and self.vbo_colors != None: #and not self.updating:
		
			#glPushMatrix()
			
			glTranslatef(50, 50, 0)
			
			glEnableClientState(GL_VERTEX_ARRAY)
			glEnableClientState(GL_COLOR_ARRAY)
			
			self.vbo_points.bind()
			glVertexPointer(3, GL_FLOAT, 0, self.vbo_points)
			
			self.vbo_colors.bind()
			glColorPointer(3, GL_UNSIGNED_BYTE, 0, self.vbo_colors)
			
			glDrawArrays(GL_POINTS, 0, self.n)
			
			glDisableClientState(GL_COLOR_ARRAY)
			glDisableClientState(GL_VERTEX_ARRAY)
			
			self.vbo_points.unbind()
			self.vbo_colors.unbind()	

			#glPopMatrix()
