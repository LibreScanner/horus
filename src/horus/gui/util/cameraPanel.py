#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: July 2014                                                       #
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
import wx.lib.scrolledpanel

import cv2

from horus.util import profile

class CameraPanel(wx.lib.scrolledpanel.ScrolledPanel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent, size=(270, 0))

        self.scanner = self.GetParent().GetParent().GetParent().scanner

        self.SetupScrolling()
        
        #-- Graphic elements
        cameraParamsStaticText = wx.StaticText(self, wx.ID_ANY, _("Camera Parameters"), style=wx.ALIGN_CENTRE)
        cameraParamsStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.brightnessStaticText = wx.StaticText(self, wx.ID_ANY, _("Brightness"), size=(70, -1), style=wx.ALIGN_CENTRE)
        self.brightnessSlider = wx.Slider(self, wx.ID_ANY, 50, 0, 255, size=(150, -1), style=wx.SL_LABELS)

        ## TODO: Complete parameters

        #-- Bind
        self.Bind(wx.EVT_SLIDER, self.onBrightnessChanged, self.brightnessSlider)

        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        vbox.Add(cameraParamsStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.brightnessStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.brightnessSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)

        self.SetSizer(vbox)
        self.Centre()

    def onBrightnessChanged(self, event):
        value = self.brightnessSlider.GetValue()
        #self.scanner.getCamera().capture.set(cv2.cv.CV_CAP_PROP_EXPOSURE, value/255.0) #-- TODO: move to class Camera
        profile.putProfileSetting('brightness_value', value)

    def updateProfileToAllControls(self):
        self.brightnessSlider.SetValue(profile.getProfileSettingInteger('brightness_value'))
