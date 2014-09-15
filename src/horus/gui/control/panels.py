#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: August 2014                                                     #
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

from horus.util.profile import *

from horus.engine.scanner import *

class CameraPanel(wx.Panel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, size=(275, 0))

        self.main = self.GetParent().GetParent().GetParent()

        self.scanner = Scanner.Instance()

        self.useDistortion = False

        #-- Graphic elements
        cameraControlStaticText = wx.StaticText(self, wx.ID_ANY, _("Camera Control"), style=wx.ALIGN_CENTRE)
        cameraControlStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.brightnessText = wx.StaticText(self,label=_("Brightness"))
        self.brightnessSlider = wx.Slider(self,wx.ID_ANY,1,0,255,size=(150,-1), style=wx.SL_LABELS)
        self.contrastText = wx.StaticText(self,label=_("Contrast"))
        self.contrastSlider = wx.Slider(self,wx.ID_ANY,1,0,255,size=(150,-1), style=wx.SL_LABELS)
        self.saturationText = wx.StaticText(self,label=_("Saturation"))
        self.saturationSlider = wx.Slider(self,wx.ID_ANY,1,0,255,size=(150,-1), style=wx.SL_LABELS)
        self.exposureText = wx.StaticText(self,label=_("Exposure"))
        self.exposureSlider = wx.Slider(self,wx.ID_ANY,60,0,300,size=(150,-1), style=wx.SL_LABELS)
        self.framerates = [str(30),str(25),str(20),str(15),str(10),str(5)]
        self.frameRateText = wx.StaticText(self,label=_("Frame rate"), size=(70, -1), style=wx.ALIGN_CENTRE)
        self.frameRateCombo = wx.ComboBox(self, -1, size=(150, -1), choices=self.framerates, style=wx.CB_READONLY)
        self.resolutions = [str((1280,960)),str((960,720)),str((800,600)),str((320,240)),str((160,120))]
        self.resolutionText = wx.StaticText(self,label=_("Resolution"), size=(70, -1), style=wx.ALIGN_CENTRE)
        self.resolutionCombo = wx.ComboBox(self, -1,str((1280,960)), size=(150, -1), choices=self.resolutions, style=wx.CB_READONLY)
        self.useDistortionCheckBox = wx.CheckBox(self, label=_("Use distortion"))
        self.restoreButton = wx.Button(self,label=_("Restore Default"),size=(200,-1))

        # - Layout
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox=wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(cameraControlStaticText, 0, wx.ALL, 10)
        hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
        vbox.Add(hbox,0,wx.EXPAND|wx.LEFT|wx.RIGHT,0)

        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.brightnessText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.brightnessSlider, 0, wx.ALL, 0)
        vbox.Add(hbox,0,wx.EXPAND,0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.contrastText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.contrastSlider, 0, wx.ALL, 0)
        vbox.Add(hbox,0,wx.EXPAND,0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.saturationText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.saturationSlider, 0, wx.ALL, 0)
        vbox.Add(hbox,0,wx.EXPAND,0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        hbox.Add(self.exposureText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.exposureSlider, 0, wx.ALL, 0)
        vbox.Add(hbox,0,wx.EXPAND,0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        hbox.Add(self.frameRateText, 0, wx.ALL, 18)
        hbox.Add(self.frameRateCombo, 0, wx.TOP, 12)
        vbox.Add(hbox,0,wx.EXPAND,0)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.resolutionText, 0, wx.ALL, 18)
        hbox.Add(self.resolutionCombo, 0, wx.TOP, 12)
        vbox.Add(hbox,0,wx.EXPAND,0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.useDistortionCheckBox, 0, wx.ALL^wx.BOTTOM^wx.TOP, 18)
        vbox.Add(hbox,0,wx.EXPAND,0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.restoreButton, 0, wx.ALL, 18)
        
        vbox.Add(hbox,0,wx.ALIGN_CENTRE,5)
        self.updateProfileToAllControls()
        
        self.SetSizer(vbox)
        self.Centre()

        #-- Events
        self.brightnessSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.main.releaseUndo)
        self.brightnessSlider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onBrightnessChanged)
        self.contrastSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE,self.main.releaseUndo)
        self.contrastSlider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onContrastChanged)
        self.saturationSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.main.releaseUndo)
        self.saturationSlider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onSaturationChanged)
        self.exposureSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.main.releaseUndo)
        self.exposureSlider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onExposureChanged)
        self.frameRateCombo.Bind(wx.EVT_COMBOBOX, self.OnSelectFrame)
        self.resolutionCombo.Bind(wx.EVT_COMBOBOX, self.OnSelectResolution)
        self.useDistortionCheckBox.Bind(wx.EVT_CHECKBOX, self.onUseDistortionChanged)
        self.restoreButton.Bind(wx.EVT_BUTTON, self.restoreDefault)

    def onBrightnessChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('brightness_control'))
        value = self.brightnessSlider.GetValue()
        putProfileSetting('brightness_control', value)
        self.scanner.camera.setBrightness(value)

    def onContrastChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('contrast_control'))
        value = self.contrastSlider.GetValue()
        putProfileSetting('contrast_control', value)
        self.scanner.camera.setContrast(value)

    def onSaturationChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('saturation_control'))
        value = self.saturationSlider.GetValue()
        putProfileSetting('saturation_control', value)
        self.scanner.camera.setSaturation(value)

    def onExposureChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('exposure_control'))
        value = self.exposureSlider.GetValue() 
        putProfileSetting('exposure_control', value)
        self.scanner.camera.setExposure(value)

    def OnSelectFrame(self, event):
        value = int(self.frameRateCombo.GetValue())
        putProfileSetting('framerate_control', value)
        self.scanner.camera.setFps(value)
        self.reloadVideo()
        
    def OnSelectResolution(self, event):
        resolution = self.resolutionCombo.GetValue().replace('(', '').replace(')', '')
        h = int(resolution.split(',')[1])
        w = int(resolution.split(',')[0])
        putProfileSetting('camera_width_control', w)
        putProfileSetting('camera_height_control', h)
        self.scanner.camera.setWidth(w)
        self.scanner.camera.setHeight(h)

    def onUseDistortionChanged(self, event):
        self.useDistortion = self.useDistortionCheckBox.GetValue()
        putProfileSetting('use_distortion_control', self.useDistortion)
        self.reloadVideo()
        self.scanner.camera.setUseDistortion(self.useDistortion)

    def restoreDefault(self, event):
        dlg = wx.MessageDialog(self, _("This will reset control camera settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Camera Control reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            resetProfileSetting('brightness_control')
            resetProfileSetting('contrast_control')
            resetProfileSetting('saturation_control')
            resetProfileSetting('exposure_control')
            resetProfileSetting('framerate_control')
            resetProfileSetting('camera_width_control')
            resetProfileSetting('camera_height_control')
            resetProfileSetting('use_distortion_control')
            self.main.enableLabelTool(self.main.undoTool, False)
            self.updateProfileToAllControls()
            self.reloadVideo()

    def reloadVideo(self):
        self.main.timer.Stop()
        if self.main.playing and self.scanner.camera.fps > 0:
            self.main.timer.Start(milliseconds=1)

    def updateProfileToAllControls(self):
        brightness = getProfileSettingInteger('brightness_control')
        self.brightnessSlider.SetValue(brightness)
        self.scanner.camera.setBrightness(brightness)

        contrast = getProfileSettingInteger('contrast_control')
        self.contrastSlider.SetValue(contrast)
        self.scanner.camera.setContrast(contrast)

        saturation = getProfileSettingInteger('saturation_control')
        self.saturationSlider.SetValue(saturation)
        self.scanner.camera.setSaturation(saturation)

        exposure = getProfileSettingInteger('exposure_control')
        self.exposureSlider.SetValue(exposure)
        self.scanner.camera.setExposure(exposure)

        framerate = getProfileSettingInteger('framerate_control')
        self.frameRateCombo.SetValue(str(framerate))
        self.scanner.camera.setFps(framerate)

        camera_width = getProfileSettingInteger('camera_width_control')
        camera_height = getProfileSettingInteger('camera_height_control')
        resolution=(camera_width, camera_height)
        self.resolutionCombo.SetValue(str(resolution))
        self.scanner.camera.setWidth(camera_width)
        self.scanner.camera.setHeight(camera_height)

        self.useDistortion = getProfileSettingBool('use_distortion_control')
        self.useDistortionCheckBox.SetValue(self.useDistortion)
        self.scanner.camera.setUseDistortion(self.useDistortion)


class DevicePanel(wx.Panel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, size=(270, 0))

        self.parent = self.GetParent().GetParent().GetParent()

        self.scanner = Scanner.Instance()

        #-- Graphic elements
        laserControlStaticText = wx.StaticText(self, wx.ID_ANY, _("Laser Control"), style=wx.ALIGN_CENTRE)
        laserControlStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.laserLeftButton = wx.ToggleButton(self, -1, _("Left"))
        self.laserRightButton = wx.ToggleButton(self, -1, _("Right"))

        motorControlStaticText = wx.StaticText(self, wx.ID_ANY, _("Motor Control"), style=wx.ALIGN_CENTRE)
        motorControlStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        stepDegreesLabel = wx.StaticText(self, label=_(u"Slice Step (º)"))
        self.stepDegreesText = wx.TextCtrl(self)
        feedRateLabel = wx.StaticText(self, label=_(u"Feed Rate (º/s)"))
        self.feedRateText = wx.TextCtrl(self)
        accelerationLabel = wx.StaticText(self, label=_(u"Acceleration (º/s^2)"))
        self.accelerationText = wx.TextCtrl(self)

        self.motorEnableButton = wx.ToggleButton(self, -1, _("Enable"))
        self.motorMoveButton = wx.Button(self, -1, _("Move"))

        gcodeCommandsStaticText = wx.StaticText(self, wx.ID_ANY, _("Gcode commands"), style=wx.ALIGN_CENTRE)
        gcodeCommandsStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.gcodeRequestText = wx.TextCtrl(self, size=(145,-1))
        self.gcodeSendButton = wx.Button(self, -1, _("Send"))
        self.gcodeResponseText = wx.TextCtrl(self, value="['$' for help]", size=(-1,250), style= wx.TE_MULTILINE)

        #-- Events
        self.laserLeftButton.Bind(wx.EVT_TOGGLEBUTTON, self.onLeftLaserClicked)
        self.laserRightButton.Bind(wx.EVT_TOGGLEBUTTON, self.onRightLaserClicked)

        self.stepDegreesText.Bind(wx.EVT_TEXT, self.onStepDegreesTextChanged)
        self.feedRateText.Bind(wx.EVT_TEXT, self.onFeedRateTextChanged)

        self.motorEnableButton.Bind(wx.EVT_TOGGLEBUTTON, self.onMotorEnableButtonClicked)
        self.motorMoveButton.Bind(wx.EVT_BUTTON, self.onMotorMoveButtonClicked)

        self.gcodeSendButton.Bind(wx.EVT_BUTTON, self.onGcodeSendButtonClicked)

        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        vbox.Add(laserControlStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(self.laserLeftButton, 0, wx.ALL, 12)
        hbox.Add(self.laserRightButton, 0, wx.ALL, 12)
        vbox.Add(hbox)

        vbox.Add(motorControlStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(stepDegreesLabel, 0, wx.ALL|wx.EXPAND, 18)
        hbox.Add(self.stepDegreesText, 1, wx.EXPAND|wx.ALL^wx.LEFT, 12)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(feedRateLabel, 0, wx.ALL|wx.EXPAND, 18)
        hbox.Add(self.feedRateText, 1, wx.EXPAND|wx.ALL^wx.LEFT, 12)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(accelerationLabel, 0, wx.ALL|wx.EXPAND, 18)
        hbox.Add(self.accelerationText, 1, wx.EXPAND|wx.ALL^wx.LEFT, 12)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.motorMoveButton, 0, wx.ALL, 12)
        hbox.Add(self.motorEnableButton, 0, wx.ALL^wx.BOTTOM, 12)
        vbox.Add(hbox)

        vbox.Add(gcodeCommandsStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.gcodeRequestText, 0, wx.ALL^wx.RIGHT, 12)
        hbox.Add(self.gcodeSendButton, 0, wx.ALL, 12)
        vbox.Add(hbox)

        vbox.Add(self.gcodeResponseText, 1, wx.ALL|wx.EXPAND^wx.RIGHT, 10)

        self.SetSizer(vbox)

    def onLeftLaserClicked(self, event):
        if event.IsChecked():
            self.scanner.device.setLeftLaserOn()
        else:
            self.scanner.device.setLeftLaserOff()

    def onRightLaserClicked(self, event):
        if event.IsChecked():
            self.scanner.device.setRightLaserOn()
        else:
            self.scanner.device.setRightLaserOff()

    def onMotorEnableButtonClicked(self, event):
        if event.IsChecked():
            self.motorEnableButton.SetLabel(_("Disable"))
            self.scanner.device.enable()
        else:
            self.motorEnableButton.SetLabel(_("Enable"))
            self.scanner.device.disable()

    def onMotorMoveButtonClicked(self, event):
        if self.feedRateText.GetValue() is not None:
            self.scanner.device.setSpeedMotor(int(self.feedRateText.GetValue()))
        if self.accelerationText.GetValue() is not None:
            self.scanner.device.setAccelerationMotor(int(self.accelerationText.GetValue()))
        if self.stepDegreesText.GetValue() is not None:
            self.scanner.device.setRelativePosition(float((self.stepDegreesText.GetValue()).replace(',','.')))
            self.scanner.device.setMoveMotor()

    def onStepDegreesTextChanged(self, event):
        if self.stepDegreesText.GetValue() is not None and len(self.stepDegreesText.GetValue()) > 0:
            putProfileSetting('step_degrees_control', float((self.stepDegreesText.GetValue()).replace(',','.')))

    def onFeedRateTextChanged(self, event):
        if self.feedRateText.GetValue() is not None and len(self.feedRateText.GetValue()) > 0:
            putProfileSetting('feed_rate_control', int(self.feedRateText.GetValue()))

    def onAccelerationTextChanged(self, event):
        if self.accelerationText.GetValue() is not None and len(self.accelerationText.GetValue()) > 0:
            putProfileSetting('acceleration_control', int(self.accelerationText.GetValue()))

    def onGcodeSendButtonClicked(self, event):
        ret = self.scanner.device.sendCommand(self.gcodeRequestText.GetValue(), ret=True, readLines=True)
        self.gcodeResponseText.SetValue(ret)

    def updateProfileToAllControls(self):
        degrees = getProfileSettingFloat('step_degrees_control')
        self.stepDegreesText.SetValue(str(degrees))
        feedRate = getProfileSettingInteger('feed_rate_control')
        self.feedRateText.SetValue(str(feedRate))
        acceleration = getProfileSettingInteger('acceleration_control')
        self.accelerationText.SetValue(str(acceleration))