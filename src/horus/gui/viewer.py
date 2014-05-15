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


import wx
import os
import sys

from horus.engine.scanner import *

from viewer_3d.plyview import *

from horus.language.multilingual import *

        
class VideoTabPanel(wx.Panel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.bmp = wx.Bitmap(os.path.join(os.path.dirname(__file__),
         "../resources/images/bq.png"))
        self.Bind(wx.EVT_PAINT, self.onPaint)
        
        self.SetBackgroundColour(wx.BLACK)
        self.Centre()
        
    def onPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)
        
    def setBitmap(self, bmp):
        self.bmp = bmp
        
    def updateImage(self, frame):
		height, width = frame.shape[:2]
		self.bmp = wx.BitmapFromBuffer(width, height, frame)
		self.Refresh()
        
class PointCloudTabPanel(wx.Panel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.parent = parent
        
        build_dimensions = [100, 0, 0, 0, 0]

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.refresh_timer = wx.CallLater(100, self.Refresh)
        self.platform = actors.Platform(build_dimensions)
        self.model = actors.PLYModel()
        self.objects = [PLYObject(self.platform), PLYObject(self.model)]

        self.glpanel = PLYViewPanel(self, build_dimensions=build_dimensions, realparent=self)
        self.glpanel.resetview()
        
        vbox.Add(self.glpanel, 1, flag = wx.EXPAND)

        #-- Events
        self.Bind(wx.EVT_TOOL, lambda x: self.glpanel.zoom_to_center(1.2), id=1)
        self.Bind(wx.EVT_TOOL, lambda x: self.glpanel.zoom_to_center(1/1.2), id=2)
        self.Bind(wx.EVT_TOOL, lambda x: self.glpanel.layerup(), id=3)
        self.Bind(wx.EVT_TOOL, lambda x: self.glpanel.layerdown(), id=4)
        self.Bind(wx.EVT_TOOL, lambda x: self.glpanel.resetview(), id=5)
        self.Bind(wx.EVT_TOOL, lambda x: self.glpanel.fit(), id=6)
        
        self.SetSizer(vbox)

    def updatePointCloud(self, points, colors):
        self.model.add_points(points, colors)
        self.model.create_vbo()
        self.glpanel.OnDraw()


class ViewNotebook(wx.Notebook):
    """
    """
    def __init__(self, parent, scanner):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)
        
        self.scanner = scanner

        #-- Create and add tab panels
        self.videoTabPanel = VideoTabPanel(self)
        self.AddPage(self.videoTabPanel, getString("TAB_VIDEO_STR"))

        self.pointCloudTabPanel = PointCloudTabPanel(self)
        self.AddPage(self.pointCloudTabPanel, getString("TAB_POINTCLOUD_STR"))

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onPageChanging)
        
        #-- Create timers
        self.refreshTimer = wx.Timer(self, wx.ID_OK)
        self.Bind(wx.EVT_TIMER, self.onRefreshTimer, self.refreshTimer)
        
    def onRefreshTimer(self, event):
        if self.scanner != None:
            frame = self.scanner.getCore().getImage()
            if frame != None:
                self.videoTabPanel.updateImage(frame)
            while not self.scanner.isPointCloudQueueEmpty():
                pc = None
                pc = self.scanner.getPointCloudIncrement()
                if pc != None and pc[0] != None and pc[1] != None:
                    self.pointCloudTabPanel.updatePointCloud(pc[0], pc[1])

    def refreshOn(self, t):
		self.t = t
		self.refreshTimer.Start(self.t)
		
    def refreshOff(self):
		self.refreshTimer.Stop()

    def onPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def onPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()
