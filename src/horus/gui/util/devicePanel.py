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

from horus.util import profile
from horus.util.resources import *

from horus.engine.scanner import *

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

        stepDegreesLabel = wx.StaticText(self, label=_("Step"))
        self.stepDegreesText = wx.TextCtrl(self, value=profile.getProfileSetting('step_degrees'), size=(60,-1))
        feedRateLabel = wx.StaticText(self, label=_("Speed"))
        self.feedRateText = wx.TextCtrl(self, value=profile.getProfileSetting('feed_rate'), size=(60,-1))

        self.motorEnableButton = wx.ToggleButton(self, -1, _("Enable"))
        self.motorMoveButton = wx.Button(self, -1, _("Move"))

        gcodeCommandsStaticText = wx.StaticText(self, wx.ID_ANY, _("Gcode commands"), style=wx.ALIGN_CENTRE)
        gcodeCommandsStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.gcodeRequestText = wx.TextCtrl(self, size=(145,-1))
        self.gcodeSendButton = wx.Button(self, -1, _("Send"))
        self.gcodeResponseText = wx.TextCtrl(self, value="['$' for help]", style= wx.TE_MULTILINE)

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
        hbox.Add(stepDegreesLabel, 0, wx.ALL^wx.BOTTOM^wx.RIGHT, 18)
        hbox.Add(self.stepDegreesText, 0, wx.ALL^wx.BOTTOM, 12)
        hbox.Add(feedRateLabel, 0, wx.ALL^wx.RIGHT^wx.LEFT, 18)
        hbox.Add(self.feedRateText, 0, wx.ALL^wx.RIGHT, 12)
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
        if self.stepDegreesText.GetValue() is not None:
            self.scanner.device.setRelativePosition(float((self.stepDegreesText.GetValue()).replace(',','.')))
            self.scanner.device.setMoveMotor()

    def onStepDegreesTextChanged(self, event):
        if self.stepDegreesText.GetValue() is not None and len(self.stepDegreesText.GetValue()) > 0:
            profile.putProfileSetting('step_degrees', float((self.stepDegreesText.GetValue()).replace(',','.')))

    def onFeedRateTextChanged(self, event):
        if self.feedRateText.GetValue() is not None and len(self.feedRateText.GetValue()) > 0:
            profile.putProfileSetting('feed_rate', int(self.feedRateText.GetValue()))

    def onGcodeSendButtonClicked(self, event):
        if self.scanner.isConnected:
            ret = self.scanner.device.sendCommand(self.gcodeRequestText.GetValue(), ret=True, readLines=True)
            self.gcodeResponseText.SetValue(ret)

    def updateProfileToAllControls(self):
        degrees = profile.getProfileSettingFloat('step_degrees')
        self.stepDegreesText.SetValue(str(degrees))
        feedRate = profile.getProfileSettingInteger('feed_rate')
        self.feedRateText.SetValue(str(feedRate))