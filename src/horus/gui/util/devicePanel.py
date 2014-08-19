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
from horus.util.resources import *

class DevicePanel(wx.lib.scrolledpanel.ScrolledPanel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent, size=(270, 0))

        self.parent = self.GetParent().GetParent().GetParent()

        self.scanner = self.parent.scanner

        self.SetupScrolling()

        #-- Graphic elements
        laserControlStaticText = wx.StaticText(self, wx.ID_ANY, _("Laser Control"), style=wx.ALIGN_CENTRE)
        laserControlStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.laserLeftButton = wx.ToggleButton(self, -1, _("Left"))
        self.laserRightButton = wx.ToggleButton(self, -1, _("Right"))

        motorControlStaticText = wx.StaticText(self, wx.ID_ANY, _("Motor Control"), style=wx.ALIGN_CENTRE)
        motorControlStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        stepDegreesLabel = wx.StaticText(self, label=_(u"Step degrees (º) :"))
        self.stepDegreesText = wx.TextCtrl(self, value=profile.getProfileSetting('step_degrees'), size=(70,-1))
        stepOCRLabel = wx.StaticText(self, label=_("Step OCR timer:"))
        self.stepOCRText = wx.TextCtrl(self, value=profile.getProfileSetting('step_ocr'), size=(78,-1))

        motorEnableButton = wx.Button(self, -1, _("Enable"))
        motorDisableButton = wx.Button(self, -1, _("Disable"))

        motorCCWButton = wx.Button(self, -1, _("CCW Step"))
        motorCWButton = wx.Button(self, -1, _("CW Step"))

        self.applyConfigButton = wx.Button(self, -1, _("Apply Configuration"), size=(200,-1))
        self.applyConfigButton.Disable()

        #-- Events
        self.laserLeftButton.Bind(wx.EVT_TOGGLEBUTTON, self.onLeftLaserClicked)
        self.laserRightButton.Bind(wx.EVT_TOGGLEBUTTON, self.onRightLaserClicked)

        self.stepDegreesText.Bind(wx.EVT_TEXT, lambda e: self.applyConfigButton.Enable())
        self.stepOCRText.Bind(wx.EVT_TEXT, lambda e: self.applyConfigButton.Enable())

        motorEnableButton.Bind(wx.EVT_BUTTON, self.onMotorEnableButtonClicked)
        motorDisableButton.Bind(wx.EVT_BUTTON, self.onMotorDisableButtonClicked)
        motorCCWButton.Bind(wx.EVT_BUTTON, self.onMotorCCWButtonClicked)
        motorCWButton.Bind(wx.EVT_BUTTON, self.onMotorCWButtonClicked)

        self.applyConfigButton.Bind(wx.EVT_BUTTON, self.onApplyConfigurationClicked)

        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        vbox.Add(laserControlStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(self.laserLeftButton, 0, wx.ALL, 15)
        hbox.Add(self.laserRightButton, 0, wx.ALL, 15)
        vbox.Add(hbox)

        vbox.Add(motorControlStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(stepDegreesLabel, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.stepDegreesText, 0, wx.ALL^wx.LEFT, 12)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(stepOCRLabel, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.stepOCRText, 0, wx.ALL^wx.LEFT, 12)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(motorEnableButton, 0, wx.ALL^wx.BOTTOM, 15)
        hbox.Add(motorDisableButton, 0, wx.ALL^wx.BOTTOM, 15)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(motorCCWButton, 0, wx.ALL, 15)
        hbox.Add(motorCWButton, 0, wx.ALL, 15)
        vbox.Add(hbox)

        vbox.Add((0, 0), 1, wx.EXPAND)

        vbox.Add(self.applyConfigButton, 0, wx.ALL, 15)

        self.SetSizer(vbox)

    def onLeftLaserClicked(self, event):
        if event.IsChecked():
            self.scanner.device.setLeftLaserOn()
        else:
            self.scanner.device.setLeftLaserOff()
        self.updateScannerImage()

    def onRightLaserClicked(self, event):
        if event.IsChecked():
            self.scanner.device.setRightLaserOn()
        else:
            self.scanner.device.setRightLaserOff()
        self.updateScannerImage()

    def onMotorEnableButtonClicked(self, event):
        self.scanner.device.enable()

    def onMotorDisableButtonClicked(self, event):
        self.scanner.device.disable()

    def onMotorCCWButtonClicked(self, event):
        self.scanner.device.setMotorCCW()

    def onMotorCWButtonClicked(self, event):
        self.scanner.device.setMoveMotor(float((self.stepDegreesText.GetValue()).replace(',','.')))

    def onApplyConfigurationClicked(self, event):

        if self.stepDegreesText.GetValue() is not None:
            profile.putProfileSetting('step_degrees', float((self.stepDegreesText.GetValue()).replace(',','.')))

        if self.stepOCRText.GetValue() is not None:
            profile.putProfileSetting('step_ocr', int(self.stepOCRText.GetValue()))

        if self.scanner.isConnected:
            self.scanner.device.sendConfiguration(profile.getProfileSettingFloat('step_degrees'), profile.getProfileSettingInteger('step_ocr'))

        self.applyConfigButton.Disable()

    def updateScannerImage(self):
        if self.laserLeftButton.GetValue():
            if self.laserRightButton.GetValue():
                self.parent.deviceView.setImage(wx.Image(getPathForImage("scannerlr.png")))
            else:
                self.parent.deviceView.setImage(wx.Image(getPathForImage("scannerl.png")))
        else:
            if self.laserRightButton.GetValue():
                self.parent.deviceView.setImage(wx.Image(getPathForImage("scannerr.png")))
            else:
                self.parent.deviceView.setImage(wx.Image(getPathForImage("scanner.png")))

    def updateProfileToAllControls(self):
        degrees = profile.getProfileSettingFloat('step_degrees')
        self.stepDegreesText.SetValue(str(degrees))
        ocr = profile.getProfileSettingInteger('step_ocr')
        self.stepOCRText.SetValue(str(ocr))

        if self.scanner.isConnected:
            self.scanner.device.sendConfiguration(degrees, ocr)

        self.applyConfigButton.Disable()