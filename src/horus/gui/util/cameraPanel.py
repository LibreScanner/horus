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
        cameraControlStaticText = wx.StaticText(self, wx.ID_ANY, _("Camera Control"), style=wx.ALIGN_CENTRE)
        cameraControlStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.brightnessText = wx.StaticText(self,label=_("Brightness"), size=(70, -1), style=wx.ALIGN_CENTRE)
        self.brightnessSlider = wx.Slider(self,wx.ID_ANY,1,0,255,size=(150,-1), style=wx.SL_LABELS)
        self.Bind(wx.EVT_SLIDER,self.onbrightnessChanged,self.brightnessSlider)

        self.contrastText = wx.StaticText(self,label=_("Contrast"), size=(70, -1), style=wx.ALIGN_CENTRE)
        self.contrastSlider = wx.Slider(self,wx.ID_ANY,1,0,255,size=(150,-1), style=wx.SL_LABELS)
        self.Bind(wx.EVT_SLIDER,self.oncontrastChanged,self.contrastSlider)

        self.saturationText = wx.StaticText(self,label=_("Saturation"), size=(70, -1), style=wx.ALIGN_CENTRE)
        self.saturationSlider = wx.Slider(self,wx.ID_ANY,1,0,255,size=(150,-1), style=wx.SL_LABELS)
        self.Bind(wx.EVT_SLIDER,self.onsaturationChanged,self.saturationSlider)

        self.exposureText = wx.StaticText(self,label=_("Exposure"), size=(70, -1), style=wx.ALIGN_CENTRE)
        self.exposureSlider = wx.Slider(self,wx.ID_ANY,60,0,200,size=(150,-1), style=wx.SL_LABELS)
        self.Bind(wx.EVT_SLIDER,self.onexposureChanged,self.exposureSlider)

        self.framerates = [str(30),str(25),str(20),str(15),str(10),str(5)]

        self.frameRateText = wx.StaticText(self,label=_("Frame rate"), size=(70, -1), style=wx.ALIGN_CENTRE)
        self.frameRateCombo = wx.ComboBox(self, -1, size=(150, -1), choices=self.framerates, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectFrame,self.frameRateCombo)

        self.resolutions = [str((1280,960)),str((1184,656)),str((1024,576)),str((960,720)),str((960,544)),str((864,480)),str((800,600)),str((800,448)),str((800,448)),str((752,416)),str((640,360)),str((544,288)),str((432,240)),str((544,288)),str((432,240)),str((352,288)),str((320,240)),str((176,144)),str((160,120))]

        self.resolutionText = wx.StaticText(self,label=_("Resolution"), size=(70, -1), style=wx.ALIGN_CENTRE)
        self.resolutionCombo = wx.ComboBox(self, -1,str((1280,960)), size=(150, -1), choices=self.resolutions, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectResolution,self.resolutionCombo)

        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        vbox.Add(cameraControlStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.brightnessText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.brightnessSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.contrastText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.contrastSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.saturationText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.saturationSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.exposureText, 0, wx.ALL, 18)
        hbox.Add(self.exposureSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.frameRateText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.frameRateCombo, 0, wx.ALL^wx.LEFT, 12)
        vbox.Add(hbox)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.resolutionText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.resolutionCombo, 0, wx.ALL^wx.LEFT, 12)
        vbox.Add(hbox)
        
        self.SetSizer(vbox)
        self.Centre()

    def onbrightnessChanged(self,event):
        value=self.brightnessSlider.GetValue()  
        profile.putProfileSetting('brightness_value', value)
        self.scanner.camera.setBrightness(value)

    def oncontrastChanged(self,event):
        value=self.contrastSlider.GetValue()    
        profile.putProfileSetting('contrast_value', value)
        self.scanner.camera.setContrast(value)

    def onsaturationChanged(self,event):
        value=self.saturationSlider.GetValue()  
        profile.putProfileSetting('saturation_value', value)
        self.scanner.camera.setSaturation(value)

    def onexposureChanged(self,event):
        value=self.exposureSlider.GetValue()    
        profile.putProfileSetting('exposure_value', value)
        self.scanner.camera.setExposure(value)

    def OnSelectFrame(self,event):
        value= int(event.GetSelection())
        profile.putProfileSetting('framerate_value', value)
        self.GetParent().GetParent().GetParent().timer.Stop()
        self.scanner.camera.setFps(value)
        self.GetParent().GetParent().GetParent().timer.Start(milliseconds=(1000/self.scanner.camera.fps))
        
    def OnSelectResolution(self,event):
        value= event.GetSelection()
        profile.putProfileSetting('resolution_value', value)
        self.scanner.camera.setResolution(value)

    def updateProfileToAllControls(self):
        brightness=profile.getProfileSettingInteger('brightness_value')
        self.brightnessSlider.SetValue(brightness)
        self.scanner.camera.setBrightness(brightness)

        contrast=profile.getProfileSettingInteger('contrast_value')
        self.contrastSlider.SetValue(contrast)
        self.scanner.camera.setContrast(contrast)

        saturation=profile.getProfileSettingInteger('saturation_value')
        self.saturationSlider.SetValue(saturation)
        self.scanner.camera.setSaturation(saturation)

        exposure=profile.getProfileSettingInteger('exposure_value')
        self.exposureSlider.SetValue(exposure)
        self.scanner.camera.setExposure(exposure)

        framerate=profile.getProfileSettingInteger('framerate_value')
        self.frameRateCombo.SetSelection(framerate)
        self.scanner.camera.setFps(framerate)

        resolution=profile.getProfileSettingInteger('resolution_value')
        self.resolutionCombo.SetSelection(resolution)
        self.scanner.camera.setResolution(resolution)
