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
from horus.util import resources

class CameraPanel(wx.lib.scrolledpanel.ScrolledPanel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent, size=(270, 0))

        self.scanner = self.GetParent().GetParent().GetParent().scanner

        self.SetupScrolling()
        
        self.brightnessId=8416 # BRIGhtness
        self.contrastId=6017 # CONTrast
        self.saturationId=5470 # SATUration
        self.exposureId=3870   # EXPOsure

        #-- Graphic elements
        cameraParamsStaticText = wx.StaticText(self, wx.ID_ANY, _("Camera Parameters"), style=wx.ALIGN_CENTRE)
        cameraParamsStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.brightnessText = wx.StaticText(self,label=_("Brightness"))
        self.brightnessSlider = wx.Slider(self,self.brightnessId,1,0,255,size=(150,-1), style=wx.SL_LABELS)
        self.Bind(wx.EVT_SCROLL_THUMBRELEASE,self.release,self.brightnessSlider)
        self.Bind(wx.EVT_SCROLL_THUMBTRACK,self.onbrightnessChanged,self.brightnessSlider)
        

        self.contrastText = wx.StaticText(self,label=_("Contrast"))
        self.contrastSlider = wx.Slider(self,self.contrastId,1,0,255,size=(150,-1), style=wx.SL_LABELS)
        self.Bind(wx.EVT_SCROLL_THUMBTRACK,self.oncontrastChanged,self.contrastSlider)
        self.Bind(wx.EVT_SCROLL_THUMBRELEASE,self.release,self.contrastSlider)

        self.saturationText = wx.StaticText(self,label=_("Saturation"))
        self.saturationSlider = wx.Slider(self,self.saturationId,1,0,255,size=(150,-1), style=wx.SL_LABELS)
        self.Bind(wx.EVT_SCROLL_THUMBTRACK,self.onsaturationChanged,self.saturationSlider)
        self.Bind(wx.EVT_SCROLL_THUMBRELEASE,self.release,self.saturationSlider)

        self.exposureText = wx.StaticText(self,label=_("Exposure"))
        self.exposureSlider = wx.Slider(self,self.exposureId,60,0,200,size=(150,-1), style=wx.SL_LABELS)
        self.Bind(wx.EVT_SCROLL_THUMBTRACK,self.onexposureChanged,self.exposureSlider)
        self.Bind(wx.EVT_SCROLL_THUMBRELEASE,self.release,self.exposureSlider)

        self.framerates = [str(30),str(25),str(20),str(15),str(10),str(5)]

        self.frameRateText = wx.StaticText(self,label=_("Frame rate"))
        self.frameRateCombo = wx.ComboBox(self, -1, size=(150, -1), choices=self.framerates, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectFrame,self.frameRateCombo)

        self.resolutions = [str((1280,960)),str((1184,656)),str((1024,576)),str((960,720)),str((960,544)),str((864,480)),str((800,600)),str((800,448)),str((800,448)),str((752,416)),str((640,360)),str((544,288)),str((432,240)),str((544,288)),str((432,240)),str((352,288)),str((320,240)),str((176,144)),str((160,120))]

        self.resolutionText = wx.StaticText(self,label=_("Resolution"))
        self.resolutionCombo = wx.ComboBox(self, -1,str((1280,960)), size=(150, -1), choices=self.resolutions, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectResolution,self.resolutionCombo)

        self.restoreButton = wx.Button(self,label=_("Restore Default"),size=(200,-1))
        self.restoreButton.Bind(wx.EVT_BUTTON,self.restoreDefault)

        image1=wx.Bitmap(resources.getPathForImage("undo.png"))

        self.undoButton = wx.BitmapButton(self, id=-1, bitmap=image1, size = (image1.GetWidth()+5, image1.GetHeight()+5))
        self.undoButton.Bind(wx.EVT_BUTTON,self.undo)
        self.undoButton.Disable()

        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        hbox=wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(cameraParamsStaticText, 0, wx.ALL, 10)
        hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
        hbox.Add(self.undoButton, 0, wx.ALL, 0)
        vbox.Add(hbox,0,wx.EXPAND|wx.LEFT|wx.RIGHT,0)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.brightnessText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
        hbox.Add(self.brightnessSlider, 0, wx.ALL, 0)
        vbox.Add(hbox,0,wx.EXPAND,0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.contrastText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
        hbox.Add(self.contrastSlider, 0, wx.ALL, 0)
        vbox.Add(hbox,0,wx.EXPAND,0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.saturationText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
        hbox.Add(self.saturationSlider, 0, wx.ALL, 0)
        vbox.Add(hbox,0,wx.EXPAND,0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.exposureText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
        hbox.Add(self.exposureSlider, 0, wx.ALL, 0)
        vbox.Add(hbox,0,wx.EXPAND,0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.frameRateText, 0, wx.ALL, 18)
        hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
        hbox.Add(self.frameRateCombo, 0, wx.TOP, 10)
        vbox.Add(hbox,0,wx.EXPAND,0)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.resolutionText, 0, wx.ALL, 18)
        hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
        hbox.Add(self.resolutionCombo, 0, wx.TOP, 10)
        vbox.Add(hbox,0,wx.EXPAND,0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.restoreButton, 0, wx.ALL^wx.BOTTOM, 18)
        vbox.Add(hbox,0,wx.ALIGN_CENTRE,0)

        self.updateProfileToAllControls()
        
        self.SetSizer(vbox)
        self.Centre()

        self.storyObjects=[]
        self.storyValues=[]
        self.flagFirstMove=True # When you drag the slider, the only undoable is the first position not the ones in between

    def onbrightnessChanged(self,event):
        self.firstMove(event,profile.getProfileSettingInteger('brightness_value'))
        value=self.brightnessSlider.GetValue()  
        profile.putProfileSetting('brightness_value', value)
        self.scanner.camera.setBrightness(value)
        

    def oncontrastChanged(self,event):
        self.firstMove(event,profile.getProfileSettingInteger('contrast_value'))
        value=self.contrastSlider.GetValue()    
        profile.putProfileSetting('contrast_value', value)
        self.scanner.camera.setContrast(value)

    def onsaturationChanged(self,event):
        self.firstMove(event,profile.getProfileSettingInteger('saturation_value'))
        value=self.saturationSlider.GetValue()  
        profile.putProfileSetting('saturation_value', value)
        self.scanner.camera.setSaturation(value)

    def onexposureChanged(self,event):
        self.firstMove(event,profile.getProfileSettingInteger('exposure_value'))
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

    def release(self,event):
        self.flagFirstMove=True
        self.undoButton.Enable()

    def firstMove(self,event,value):
        if self.flagFirstMove:
            self.storyObjects.append(event.GetEventObject())
            self.storyValues.append(value)
            self.flagFirstMove=False


    def undo(self,event):
        
        if len(self.storyObjects)==1:
            self.undoButton.Disable()
        objectToUndo=self.storyObjects.pop()
        valueToUndo=self.storyValues.pop()
        objectToUndo.SetValue(valueToUndo)
        self.updateValue(objectToUndo)
       

    def updateValue(self,objectToUndo):
        self.flagFirstMove=False
        if (objectToUndo.GetId() == self.brightnessId):
            self.onbrightnessChanged(0)
        elif(objectToUndo.GetId() == self.contrastId):
            self.oncontrastChanged(0)
        elif(objectToUndo.GetId() == self.saturationId):
            self.onsaturationChanged(0)
        elif(objectToUndo.GetId() == self.exposureId):
            self.onexposureChanged(0)
        self.flagFirstMove=True

    def restoreDefault(self,event):
        profile.resetProfileSetting('brightness_value')
        profile.resetProfileSetting('contrast_value')
        profile.resetProfileSetting('saturation_value')
        profile.resetProfileSetting('exposure_value')
        profile.resetProfileSetting('framerate_value')
        profile.resetProfileSetting('resolution_value')
        self.GetParent().GetParent().GetParent().timer.Stop()
        self.updateProfileToAllControls()
        self.GetParent().GetParent().GetParent().timer.Start(milliseconds=(1000/self.scanner.camera.fps))
        exposure=profile.getProfileSettingInteger('exposure_value')
        self.scanner.camera.setExposure(exposure)
        

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
