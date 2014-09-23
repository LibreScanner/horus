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

from collections import OrderedDict

from horus.gui.util.itemControls import *

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

        self.controls = OrderedDict()

        #-- Graphic elements
        self.controls.update({'camera_control' : TitleText(self,'camera_control')})
        self.controls.update({'brightness_control' : Slider(self,'brightness_control')})
        self.controls.update({'contrast_control' : Slider(self,'contrast_control')})
        self.controls.update({'saturation_control' : Slider(self,'saturation_control')})
        self.controls.update({'exposure_control' : Slider(self,'exposure_control')})
        self.controls.update({'framerate_control' : ComboBox(self,'framerate_control')})
        self.controls.update({'resolution_control' : ComboBox(self,'resolution_control')})
        self.controls.update({'use_distortion_control' : CheckBox(self,'use_distortion_control')})
        self.controls.update({'restore_default' : Button(self,'restore_default')})

        # - Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        for control in self.controls.values():
            vbox.Add(control, 0, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(vbox)
        self.Centre()

        #-- Callbacks
        for control in self.controls.values():
            control.setUndoCallbacks(self.main.appendToUndo, self.main.releaseUndo)

        self.controls['brightness_control'].setEngineCallback(self.scanner.camera.setBrightness)
        self.controls['contrast_control'].setEngineCallback(self.scanner.camera.setContrast)
        self.controls['saturation_control'].setEngineCallback(self.scanner.camera.setSaturation)
        self.controls['exposure_control'].setEngineCallback(self.scanner.camera.setExposure)
        self.controls['framerate_control'].setEngineCallback(lambda v: (self.scanner.camera.setFrameRate(int(v)), self.reloadVideo()))
        self.controls['resolution_control'].setEngineCallback(lambda v: self.scanner.camera.setResolution(int(v.split('x')[0]), int(v.split('x')[1])))
        self.controls['use_distortion_control'].setEngineCallback(lambda v: (self.scanner.camera.setUseDistortion(v), self.reloadVideo()))

        #-- Events
        self.controls['restore_default'].Bind(wx.EVT_BUTTON, self.restoreDefault)

    def restoreDefault(self, event):
        dlg = wx.MessageDialog(self, _("This will reset control camera settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Camera Control reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            for control in self.controls:
                control.resetProfile()
            self.main.enableLabelTool(self.main.undoTool, False)
            self.reloadVideo()

    def reloadVideo(self):
        self.main.timer.Stop()
        if self.main.playing and self.scanner.camera.fps > 0:
            self.main.timer.Start(milliseconds=1)

    def updateProfileToAllControls(self):
        for control in self.controls.values():
            control.updateProfile()

        ## TODO: Force repaint!


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