#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project and comes from Printrun suite  #
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

import wx

from horus.gui.viewer_3d.gl.panel import wxGLPanel
from horus.gui.viewer_3d.gl.trackball import build_rotmatrix
from horus.gui.viewer_3d.gl.libtatlin import actors
from horus.gui.viewer_3d.gl.libtatlin.actors import vec

from OpenGL.GL import *


class PLYViewPanel(wxGLPanel):

    def __init__(self, parent, id = wx.ID_ANY,
                 build_dimensions = None, realparent = None):
        super(PLYViewPanel, self).__init__(parent, id, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.canvas.Bind(wx.EVT_MOUSE_EVENTS, self.move)
        self.canvas.Bind(wx.EVT_LEFT_DCLICK, self.double)
        self.initialized = 0
        self.canvas.Bind(wx.EVT_MOUSEWHEEL, self.wheel)
        self.parent = realparent if realparent else parent
        self.initpos = None
        if build_dimensions:
            self.build_dimensions = build_dimensions
        else:
            self.build_dimensions = [100, 0, 0, 0, 0]
        self.dist = 2 * self.build_dimensions[0]
        self.basequat = [0, 0, 0, 1]
        self.mousepos = [0, 0]

    def setlayercb(self, layer):
        pass

    def OnInitGL(self, *args, **kwargs):
        super(PLYViewPanel, self).OnInitGL(*args, **kwargs)

        ############
        if self.GLinitialized:
            return
        self.GLinitialized = True
        #create a pyglet context for this panel
        self.pygletcontext = gl.Context(gl.current_context)
        self.pygletcontext.canvas = self
        self.pygletcontext.set_current()
        #normal gl init
        glClearColor(0, 0, 0, 1)
        glColor3f(1, 0, 0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        # Uncomment this line for a wireframe view
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
        # but this is not the case on Linux or Mac, so remember to always
        # include it.
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)

        glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
        glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
        glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, vec(0, 0.1, 0, 0.9))
        if call_reshape:
            self.OnReshape()
        ###########

        if hasattr(self.parent, "filenames") and self.parent.filenames:
            for filename in self.parent.filenames:
                self.parent.load_file(filename)
            self.parent.autoplate()
            if hasattr(self.parent, "loadcb"):
                self.parent.loadcb()
            self.parent.filenames = None

    def create_objects(self):
        '''create opengl objects when opengl is initialized'''
        for obj in self.parent.objects:
            if obj.model and not obj.model.initialized:
                obj.model.init()

    def update_object_resize(self):
        '''called when the window recieves only if opengl is initialized'''
        pass

    def draw_objects(self):
        '''called in the middle of ondraw after the buffer has been cleared'''
        self.create_objects()

        glPushMatrix()
        glTranslatef(0, 0, -self.dist) ##
        # Rotate according to trackball
        glMultMatrixd(build_rotmatrix(self.basequat))

        light_z = max(self.parent.platform.width, self.parent.platform.depth)
        glLightfv(GL_LIGHT0, GL_POSITION, vec(0,
                                              self.parent.platform.depth / 2,
                                              light_z, 0))
        glLightfv(GL_LIGHT1, GL_POSITION, vec(self.parent.platform.width,
                                              self.parent.platform.depth / 2,
                                              light_z, 0))

        for obj in self.parent.objects:
            if not obj.model \
               or not obj.model.initialized:
                continue
            glPushMatrix()
            glTranslatef(*(obj.offsets))
            glTranslatef(*(obj.centeroffset))
            glRotatef(obj.rot, 0.0, 0.0, 1.0)
            glScalef(*obj.scale)

            obj.model.display()
            glPopMatrix()
        glPopMatrix()

    def double(self, event):
        if self.parent.clickcb:
            self.parent.clickcb(event)

    def move(self, event):
        """react to mouse actions:
        no mouse: show red mousedrop
        LMB: rotate viewport
        RMB: move viewport
        """
        if event.Entering():
            self.canvas.SetFocus()
            event.Skip()
            return
        if event.Dragging() and event.LeftIsDown():
            self.handle_rotation(event)
        elif event.Dragging() and event.RightIsDown():
            self.handle_translation(event)
        elif event.LeftUp():
            self.initpos = None
        elif event.RightUp():
            self.initpos = None
        else:
            event.Skip()
            return
        event.Skip()
        wx.CallAfter(self.Refresh)

    def layerup(self):
        if not self.parent.model:
            return
        max_layers = self.parent.model.max_layers
        current_layer = self.parent.model.num_layers_to_draw
        # accept going up to max_layers + 1
        # max_layers means visualizing the last layer differently,
        # max_layers + 1 means visualizing all layers with the same color
        new_layer = min(max_layers + 1, current_layer + 1)
        self.parent.model.num_layers_to_draw = new_layer
        self.parent.setlayercb(new_layer)
        wx.CallAfter(self.Refresh)

    def layerdown(self):
        if not self.parent.model:
            return
        current_layer = self.parent.model.num_layers_to_draw
        new_layer = max(1, current_layer - 1)
        self.parent.model.num_layers_to_draw = new_layer
        self.parent.setlayercb(new_layer)
        wx.CallAfter(self.Refresh)

    def handle_wheel(self, event):
        delta = event.GetWheelRotation()
        factor = 1.05
        if hasattr(self.parent, "model") and event.ShiftDown():
            if not self.parent.model:
                return
            count = 1 if not event.ControlDown() else 10
            for i in range(count):
                if delta > 0: self.layerup()
                else: self.layerdown()
            return
        x, y = event.GetPositionTuple()
        x, y, _ = self.mouse_to_3d(x, y)
        if delta > 0:
            self.zoom(factor, (x, y))
        else:
            self.zoom(1 / factor, (x, y))

    def wheel(self, event):
        """react to mouse wheel actions:
            without shift: set max layer
            with shift: zoom viewport
        """
        self.handle_wheel(event)
        wx.CallAfter(self.Refresh)

    def fit(self):
        if not self.parent.model or not self.parent.model.loaded:
            return
        self.canvas.SetCurrent(self.context)
        dims = self.parent.model.dims
        self.reset_mview(1.0)
        center_x = (dims[0][0] + dims[0][1]) / 2
        center_y = (dims[1][0] + dims[1][1]) / 2
        center_x = self.build_dimensions[0] / 2 - center_x
        center_y = self.build_dimensions[1] / 2 - center_y
        if self.orthographic:
            ratio = float(self.dist) / max(dims[0][2], dims[1][2])
            glScalef(ratio, ratio, 1)
        glTranslatef(center_x, center_y, 0)
        wx.CallAfter(self.Refresh)

    def resetview(self):
        self.canvas.SetCurrent(self.context)
        #self.reset_mview(0.9)
        self.basequat = [0.55, -0.15, -0.2, 1]
        wx.CallAfter(self.Refresh)

class PLYObject(object):

    def __init__(self, model):
        self.offsets = [0, 0, 0]
        self.centeroffset = [0, 0, 0]
        self.rot = 0
        self.curlayer = 0.0
        self.scale = [1.0, 1.0, 1.0]
        self.model = model
