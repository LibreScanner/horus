#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: October 2014                                                    #
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
from horus.util.resources import *

from horus.engine.scanner import *

from horus.gui.wizard.connectionPage import *
from horus.gui.wizard.calibrationPage import *
from horus.gui.wizard.scanningPage import *

class Wizard(wx.Dialog):
    def __init__(self, parent):
        super(Wizard, self).__init__(parent, title="", size=(640+120,480+40))

        self.parent = parent

        self.scanner = Scanner.Instance()
        self.scanner.disconnect()
 
        self.connectionPage = ConnectionPage(self, buttonPrevCallback=self.onConnectionPagePrevClicked, buttonNextCallback=self.onConnectionPageNextClicked)
        self.calibrationPage = CalibrationPage(self, buttonPrevCallback=self.onCalibrationPagePrevClicked, buttonNextCallback=self.onCalibrationPageNextClicked)
        self.scanningPage = ScanningPage(self, buttonPrevCallback=self.onScanningPagePrevClicked, buttonNextCallback=self.onScanningPageNextClicked)

        pages = [self.connectionPage, self.calibrationPage, self.scanningPage]

        self.connectionPage.intialize(pages)
        self.calibrationPage.intialize(pages)
        self.scanningPage.intialize(pages)

        self.connectionPage.Show()
        self.calibrationPage.Hide()
        self.scanningPage.Hide()

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.connectionPage, 1, wx.ALL|wx.EXPAND, 0)
        hbox.Add(self.calibrationPage, 1, wx.ALL|wx.EXPAND, 0)
        hbox.Add(self.scanningPage, 1, wx.ALL|wx.EXPAND, 0)

        self.SetSizer(hbox)

        self.Centre()
        self.ShowModal()

    def onConnectionPagePrevClicked(self):
        putPreference('workbench', 'scanning')
        dlg = wx.MessageDialog(self, _("Do you really want to exit?"), _("Exit wizard"), wx.OK | wx.CANCEL |wx.ICON_INFORMATION)
        result = dlg.ShowModal() == wx.ID_OK
        dlg.Destroy()
        if result:
            self.scanner.disconnect()
            self.parent.workbenchUpdate()
            self.Destroy()

    def onCalibrationPagePrevClicked(self):
        self.calibrationPage.Hide()
        self.connectionPage.Show()
        self.Layout()

    def onScanningPagePrevClicked(self):
        self.scanningPage.Hide()
        self.calibrationPage.Show()
        self.Layout()

    def onConnectionPageNextClicked(self):
        self.connectionPage.Hide()
        self.calibrationPage.Show()
        self.Layout()

    def onCalibrationPageNextClicked(self):
        self.calibrationPage.Hide()
        self.scanningPage.Show()
        self.Layout()

    def onScanningPageNextClicked(self):
        self.scanner.device.setLeftLaserOff()
        self.scanner.device.setRightLaserOff()
        putPreference('workbench', 'scanning')
        saveProfile(os.path.join(getBasePath(), 'current-profile.ini'))
        dlg = wx.MessageDialog(self, _("You have finished the wizard.\nPress Play button to start scanning."), _("Ready to scan!"), wx.OK | wx.ICON_INFORMATION)
        result = dlg.ShowModal() == wx.ID_OK
        dlg.Destroy()
        if result:
            self.parent.workbenchUpdate()
            self.Destroy()
