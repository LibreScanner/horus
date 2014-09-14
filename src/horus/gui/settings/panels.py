#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: September 2014                                                  #
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

class CalibrationPanel(wx.Panel):
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, size=(275, 0))

        self.main = self.GetParent().GetParent().GetParent()

        self.scanner = Scanner.Instance()

        self.useDistortion = False

        #-- Graphic elements
        calibrationStaticText = wx.StaticText(self, wx.ID_ANY, _("Calibration Settings"), style=wx.ALIGN_CENTRE)
        calibrationStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

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
        hbox.Add(calibrationStaticText, 0, wx.ALL, 10)
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
        self.frameRateCombo.Bind(wx.EVT_COMBOBOX, self.onSelectFrame)
        self.resolutionCombo.Bind(wx.EVT_COMBOBOX, self.onSelectResolution)
        self.useDistortionCheckBox.Bind(wx.EVT_CHECKBOX, self.onUseDistortionChanged)
        self.restoreButton.Bind(wx.EVT_BUTTON, self.restoreDefault)

    def onBrightnessChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('brightness_calibration'))
        value = self.brightnessSlider.GetValue()
        putProfileSetting('brightness_calibration', value)
        self.scanner.camera.setBrightness(value)

    def onContrastChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('contrast_calibration'))
        value = self.contrastSlider.GetValue()
        putProfileSetting('contrast_calibration', value)
        self.scanner.camera.setContrast(value)

    def onSaturationChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('saturation_calibration'))
        value = self.saturationSlider.GetValue()
        putProfileSetting('saturation_calibration', value)
        self.scanner.camera.setSaturation(value)

    def onExposureChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('exposure_calibration'))
        value = self.exposureSlider.GetValue() 
        putProfileSetting('exposure_calibration', value)
        self.scanner.camera.setExposure(value)

    def onSelectFrame(self, event):
        value = int(self.frameRateCombo.GetValue())
        putProfileSetting('framerate_calibration', value)
        self.scanner.camera.setFps(value)
        self.reloadVideo()
        
    def onSelectResolution(self, event):
        resolution = self.resolutionCombo.GetValue().replace('(', '').replace(')', '')
        h = int(resolution.split(',')[1])
        w = int(resolution.split(',')[0])
        putProfileSetting('camera_width_calibration', w)
        putProfileSetting('camera_height_calibration', h)
        self.scanner.camera.setWidth(w)
        self.scanner.camera.setHeight(h)

    def onUseDistortionChanged(self, event):
        self.useDistortion = self.useDistortionCheckBox.GetValue()
        putProfileSetting('use_distortion_calibration', self.useDistortion)
        self.main.timer.Stop()
        self.scanner.camera.setUseDistortion(self.useDistortion)
        self.reloadVideo()

    def restoreDefault(self, event):
        dlg = wx.MessageDialog(self, _("This will reset calibration settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Calibration Settings reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            resetProfileSetting('brightness_calibration')
            resetProfileSetting('contrast_calibration')
            resetProfileSetting('saturation_calibration')
            resetProfileSetting('exposure_calibration')
            resetProfileSetting('framerate_calibration')
            resetProfileSetting('camera_width_calibration')
            resetProfileSetting('camera_height_calibration')
            resetProfileSetting('use_distortion_calibration')
            self.updateProfileToAllControls()
            self.reloadVideo()

    def reloadVideo(self):
        self.main.timer.Stop()
        if self.main.playingCalibration or self.main.playingScanning:
            self.main.timer.Start(milliseconds=1)

    def updateProfileToAllControls(self):
        brightness = getProfileSettingInteger('brightness_calibration')
        self.brightnessSlider.SetValue(brightness)
        self.scanner.camera.setBrightness(brightness)

        contrast = getProfileSettingInteger('contrast_calibration')
        self.contrastSlider.SetValue(contrast)
        self.scanner.camera.setContrast(contrast)

        saturation = getProfileSettingInteger('saturation_calibration')
        self.saturationSlider.SetValue(saturation)
        self.scanner.camera.setSaturation(saturation)

        exposure = getProfileSettingInteger('exposure_calibration')
        self.exposureSlider.SetValue(exposure)
        self.scanner.camera.setExposure(exposure)

        framerate = getProfileSettingInteger('framerate_calibration')
        self.frameRateCombo.SetValue(str(framerate))
        self.scanner.camera.setFps(framerate)

        camera_width = getProfileSettingInteger('camera_width_calibration')
        camera_height = getProfileSettingInteger('camera_height_calibration')
        resolution=(camera_width, camera_height)
        self.resolutionCombo.SetValue(str(resolution))
        self.scanner.camera.setWidth(camera_width)
        self.scanner.camera.setHeight(camera_height)

        self.useDistortion = getProfileSettingBool('use_distortion_calibration')
        self.useDistortionCheckBox.SetValue(self.useDistortion)
        self.scanner.camera.setUseDistortion(self.useDistortion)


class ScanningPanel(wx.Panel):
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, size=(275, 0))

        self.main = self.GetParent().GetParent().GetParent()

        self.scanner = Scanner.Instance()

        self.useDistortion = False

        #-- Graphic elements
        scannerStaticText = wx.StaticText(self, wx.ID_ANY, _("Scanner Settings"), style=wx.ALIGN_CENTRE)
        scannerStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

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
        
        imgProcStaticText = wx.StaticText(self, wx.ID_ANY, _("Image Processing"), style=wx.ALIGN_CENTRE)
        imgProcStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))
        self.openCheckBox = wx.CheckBox(self, label=_("Open"), size=(67, -1))
        self.openSlider = wx.Slider(self, wx.ID_ANY, 0, 1, 10, size=(150, -1), style=wx.SL_LABELS)
        self.thresholdCheckBox = wx.CheckBox(self, label=_("Threshold"), size=(67, -1))
        self.thresholdSlider = wx.Slider(self, wx.ID_ANY, 20, 0, 255, size=(150, -1), style=wx.SL_LABELS)

        algorithmStaticText = wx.StaticText(self, label=_("Algorithm"))
        algorithmStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))
        self.compactAlgRadioButton = wx.RadioButton(self, label=_("Compact"), size=(100,-1))
        self.completeAlgRadioButton = wx.RadioButton(self, label=_("Complete"), size=(100,-1))
        
        filterStaticText = wx.StaticText(self, label=_("Filter"))
        filterStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))
        minRadiousStaticText = wx.StaticText(self, wx.ID_ANY, _("min R"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.minRadiousSlider = wx.Slider(self, wx.ID_ANY, 0, -200, 200, size=(150, -1), style=wx.SL_LABELS)
        maxRadiousStaticText = wx.StaticText(self, wx.ID_ANY, _("max R"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.maxRadiousSlider = wx.Slider(self, wx.ID_ANY, 0, -200, 200, size=(150, -1), style=wx.SL_LABELS)
        minHeightStaticText = wx.StaticText(self, wx.ID_ANY, _("min H"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.minHeightSlider = wx.Slider(self, wx.ID_ANY, 0, -100, 200, size=(150, -1), style=wx.SL_LABELS)
        maxHeightStaticText = wx.StaticText(self, wx.ID_ANY, _("max H"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.maxHeightSlider = wx.Slider(self, wx.ID_ANY, 0, -100, 200, size=(150, -1), style=wx.SL_LABELS)

        laserStaticText = wx.StaticText(self, wx.ID_ANY, _("Laser"), style=wx.ALIGN_CENTRE)
        laserStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))
        self.laserList = [_("Use Left Laser"), _("Use Right Laser"), _("Use Both Lasers")]
        self.laserCombo = wx.ComboBox(self, -1, size=(200, -1), choices=self.laserList, style=wx.CB_READONLY)

        motorStaticText = wx.StaticText(self, wx.ID_ANY, _("Motor"), style=wx.ALIGN_CENTRE)
        motorStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))
        stepDegreesLabel = wx.StaticText(self, label=_(u"Slice Step (º)"))
        self.stepDegreesText = wx.TextCtrl(self)
        feedRateLabel = wx.StaticText(self, label=_(u"Feed Rate (º/s)"))
        self.feedRateText = wx.TextCtrl(self)
        accelerationLabel = wx.StaticText(self, label=_(u"Acceleration (º/s^2)"))
        self.accelerationText = wx.TextCtrl(self)
        self.motorApplyButton = wx.Button(self, -1, _("Apply"))

        self.restoreButton = wx.Button(self, label=_("Restore Default"), size=(200,-1))

        # - Layout
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox=wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(scannerStaticText, 0, wx.ALL, 10)
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
        hbox.Add(self.useDistortionCheckBox, 0, wx.ALL^wx.TOP, 18)
        vbox.Add(hbox,0,wx.EXPAND,0)

        vbox.Add(imgProcStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.openCheckBox, 0, wx.ALL^wx.RIGHT, 15)
        hbox.Add(self.openSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.thresholdCheckBox, 0, wx.ALL^wx.RIGHT, 15)
        hbox.Add(self.thresholdSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)

        vbox.Add(algorithmStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL^wx.TOP, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.compactAlgRadioButton, 0, wx.ALL, 15);
        hbox.Add(self.completeAlgRadioButton, 0, wx.ALL, 15);
        vbox.Add(hbox) 
        
        vbox.Add(filterStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(minRadiousStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.minRadiousSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(maxRadiousStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.maxRadiousSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(minHeightStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.minHeightSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(maxHeightStaticText, 0, wx.ALL, 18)
        hbox.Add(self.maxHeightSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)

        vbox.Add(laserStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL^wx.TOP, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.laserCombo, 0, wx.ALL, 12)
        vbox.Add(hbox,0,wx.EXPAND,0)

        vbox.Add(motorStaticText, 0, wx.ALL, 10)
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
        vbox.Add(self.motorApplyButton, 0, wx.ALL, 18)

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
        self.frameRateCombo.Bind(wx.EVT_COMBOBOX, self.onSelectFrame)
        self.resolutionCombo.Bind(wx.EVT_COMBOBOX, self.onSelectResolution)
        self.useDistortionCheckBox.Bind(wx.EVT_CHECKBOX, self.onUseDistortionChanged)
        self.openCheckBox.Bind(wx.EVT_CHECKBOX, self.onOpenChanged)
        self.openSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.main.releaseUndo)
        self.openSlider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onOpenChanged)
        self.thresholdCheckBox.Bind(wx.EVT_CHECKBOX, self.onThresholdChanged)
        self.thresholdSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.main.releaseUndo)
        self.thresholdSlider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onThresholdChanged)
        self.compactAlgRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onAlgChanged)
        self.completeAlgRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onAlgChanged)
        self.minRadiousSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.main.releaseUndo)
        self.minRadiousSlider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onRadiousChanged)
        self.maxRadiousSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.main.releaseUndo)
        self.maxRadiousSlider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onRadiousChanged)
        self.minHeightSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.main.releaseUndo)
        self.minHeightSlider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onHeightChanged)
        self.maxHeightSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.main.releaseUndo)
        self.maxHeightSlider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onHeightChanged)
        self.laserCombo.Bind(wx.EVT_COMBOBOX, self.onSelectLaser)
        self.motorApplyButton.Bind(wx.EVT_BUTTON, self.onMotorApplyClicked)

        self.restoreButton.Bind(wx.EVT_BUTTON, self.restoreDefault)

    def onBrightnessChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('brightness_scanning'))
        value = self.brightnessSlider.GetValue()
        putProfileSetting('brightness_scanning', value)
        self.scanner.camera.setBrightness(value)

    def onContrastChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('contrast_scanning'))
        value = self.contrastSlider.GetValue()
        putProfileSetting('contrast_scanning', value)
        self.scanner.camera.setContrast(value)

    def onSaturationChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('saturation_scanning'))
        value = self.saturationSlider.GetValue()
        putProfileSetting('saturation_scanning', value)
        self.scanner.camera.setSaturation(value)

    def onExposureChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('exposure_scanning'))
        value = self.exposureSlider.GetValue() 
        putProfileSetting('exposure_scanning', value)
        self.scanner.camera.setExposure(value)

    def onSelectFrame(self, event):
        value = int(self.frameRateCombo.GetValue())
        putProfileSetting('framerate_scanning', value)
        self.scanner.camera.setFps(value)
        self.reloadVideo()
        
    def onSelectResolution(self, event):
        resolution = self.resolutionCombo.GetValue().replace('(', '').replace(')', '')
        h = int(resolution.split(',')[1])
        w = int(resolution.split(',')[0])
        putProfileSetting('camera_width_scanning', w)
        putProfileSetting('camera_height_scanning', h)
        self.scanner.camera.setWidth(w)
        self.scanner.camera.setHeight(h)

    def onUseDistortionChanged(self, event):
        self.useDistortion = self.useDistortionCheckBox.GetValue()
        putProfileSetting('use_distortion_scanning', self.useDistortion)
        self.reloadVideo()
        self.scanner.camera.setUseDistortion(self.useDistortion)

    def onOpenChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('open_value'))
        enable = self.openCheckBox.IsChecked()
        value = self.openSlider.GetValue()
        putProfileSetting('open', enable)
        putProfileSetting('open_value', value)
        self.scanner.core.setOpen(enable, value)

    def onThresholdChanged(self, event):
        if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('threshold_value'))
        enable = self.thresholdCheckBox.IsChecked()
        value = self.thresholdSlider.GetValue()
        putProfileSetting('threshold', enable)
        putProfileSetting('threshold_value', value)
        self.scanner.core.setThreshold(enable, value)

    def onAlgChanged(self, event):
        putProfileSetting('use_compact', self.compactAlgRadioButton.GetValue())
        self.scanner.core.setUseCompactAlgorithm(self.compactAlgRadioButton.GetValue())

    def onRadiousChanged(self, event):
    	if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('min_rho'))
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('max_rho'))
        minR = int(self.minRadiousSlider.GetValue())
        maxR = int(self.maxRadiousSlider.GetValue())
        if minR >= maxR:
            maxR = minR
        self.minRadiousSlider.SetValue(minR)
        self.maxRadiousSlider.SetValue(maxR)
        putProfileSetting('min_rho', minR)
        putProfileSetting('max_rho', maxR)
        self.scanner.core.setRangeFilter(int(self.minRadiousSlider.GetValue()),
                                         int(self.maxRadiousSlider.GetValue()),
                                         int(self.minHeightSlider.GetValue()),
                                         int(self.maxHeightSlider.GetValue()))

    def onHeightChanged(self, event):
    	if event is not None:
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('min_h'))
            self.main.appendToUndo(event.GetEventObject(), getProfileSettingInteger('max_h'))
        minH = int(self.minHeightSlider.GetValue())
        maxH = int(self.maxHeightSlider.GetValue())
        if minH >= maxH:
            maxH = minH
        self.minHeightSlider.SetValue(minH)
        self.maxHeightSlider.SetValue(maxH)
        putProfileSetting('min_h', minH)
        putProfileSetting('max_h', maxH)
        self.scanner.core.setRangeFilter(int(self.minRadiousSlider.GetValue()),
                                         int(self.maxRadiousSlider.GetValue()),
                                         int(self.minHeightSlider.GetValue()),
                                         int(self.maxHeightSlider.GetValue()))

    def onSelectLaser(self, event):
    	pass

    def onMotorApplyClicked(self, event):
        if self.stepDegreesText.GetValue() is not None and len(self.stepDegreesText.GetValue()) > 0:
            putProfileSetting('step_degrees_control', float((self.stepDegreesText.GetValue()).replace(',','.')))
        if self.feedRateText.GetValue() is not None and len(self.feedRateText.GetValue()) > 0:
            putProfileSetting('feed_rate_control', int(self.feedRateText.GetValue()))
        if self.accelerationText.GetValue() is not None and len(self.accelerationText.GetValue()) > 0:
            putProfileSetting('acceleration_control', int(self.accelerationText.GetValue()))

    def restoreDefault(self, event):
        dlg = wx.MessageDialog(self, _("This will reset scanner settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Scanner Settings reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            resetProfileSetting('brightness_scanning')
            resetProfileSetting('contrast_scanning')
            resetProfileSetting('saturation_scanning')
            resetProfileSetting('exposure_scanning')
            resetProfileSetting('framerate_scanning')
            resetProfileSetting('camera_width_scanning')
            resetProfileSetting('camera_height_scanning')
            resetProfileSetting('use_distortion_scanning')
            resetProfileSetting('open')
            resetProfileSetting('open_value')
            resetProfileSetting('threshold')
            resetProfileSetting('threshold_value')
            resetProfileSetting('use_compact')
            resetProfileSetting('min_rho')
            resetProfileSetting('max_rho')
            resetProfileSetting('min_h')
            resetProfileSetting('max_h')
            resetProfileSetting('use_left_laser')
            resetProfileSetting('use_right_laser')
            resetProfileSetting('step_degrees_scanning')
            resetProfileSetting('feed_rate_scanning')
            resetProfileSetting('acceleratin_scanning')
            self.updateProfileToAllControls()
            self.reloadVideo()

    def reloadVideo(self):
        self.main.timer.Stop()
        if self.main.playingScanning or self.main.playingScanning:
            self.main.timer.Start(milliseconds=1)

    def updateProfileToAllControls(self):
        brightness = getProfileSettingInteger('brightness_scanning')
        self.brightnessSlider.SetValue(brightness)
        self.scanner.camera.setBrightness(brightness)

        contrast = getProfileSettingInteger('contrast_scanning')
        self.contrastSlider.SetValue(contrast)
        self.scanner.camera.setContrast(contrast)

        saturation = getProfileSettingInteger('saturation_scanning')
        self.saturationSlider.SetValue(saturation)
        self.scanner.camera.setSaturation(saturation)

        exposure = getProfileSettingInteger('exposure_scanning')
        self.exposureSlider.SetValue(exposure)
        self.scanner.camera.setExposure(exposure)

        framerate = getProfileSettingInteger('framerate_scanning')
        self.frameRateCombo.SetValue(str(framerate))
        self.scanner.camera.setFps(framerate)

        camera_width = getProfileSettingInteger('camera_width_scanning')
        camera_height = getProfileSettingInteger('camera_height_scanning')
        resolution=(camera_width, camera_height)
        self.resolutionCombo.SetValue(str(resolution))
        self.scanner.camera.setWidth(camera_width)
        self.scanner.camera.setHeight(camera_height)

        self.useDistortion = getProfileSettingBool('use_distortion_scanning')
        self.useDistortionCheckBox.SetValue(self.useDistortion)
        self.scanner.camera.setUseDistortion(self.useDistortion)

        self.openCheckBox.SetValue(getProfileSettingBool('open'))
        self.openSlider.SetValue(getProfileSettingInteger('open_value'))
        ## set to core

        self.thresholdCheckBox.SetValue(getProfileSettingBool('threshold'))
        self.thresholdSlider.SetValue(getProfileSettingInteger('threshold_value'))
        ## set to core

        self.compactAlgRadioButton.SetValue(getProfileSettingBool('use_compact'))
        self.completeAlgRadioButton.SetValue(not getProfileSettingBool('use_compact'))
        ## set to core

        self.minRadiousSlider.SetValue(getProfileSettingInteger('min_rho'))
        self.maxRadiousSlider.SetValue(getProfileSettingInteger('max_rho'))
        ## set to core

        self.minHeightSlider.SetValue(getProfileSettingInteger('min_h'))
        self.maxHeightSlider.SetValue(getProfileSettingInteger('max_h'))
        ## set to core

        useLeftLaser = getProfileSettingInteger('use_left_laser')
        useRightLaser = getProfileSettingInteger('use_right_laser')
        if useLeftLaser:
            if useRightLaser:
                self.laserCombo.SetValue(_("Use Both Lasers"))
            else:
                self.laserCombo.SetValue(_("Use Left Laser"))
        else:
            if useRightLaser:
                self.laserCombo.SetValue(_("Use Right Laser"))
            else:
                self.laserCombo.SetValue("")
        ## set to core

        degrees = getProfileSettingFloat('step_degrees_scanning')
        self.stepDegreesText.SetValue(str(degrees))
        ## set to core

        feedRate = getProfileSettingInteger('feed_rate_scanning')
        self.feedRateText.SetValue(str(feedRate))
        ## set to core

        acceleration = getProfileSettingInteger('acceleration_scanning')
        self.accelerationText.SetValue(str(acceleration))
        ## set to core