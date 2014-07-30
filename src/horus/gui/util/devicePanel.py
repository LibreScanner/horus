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

class DevicePanel(wx.lib.scrolledpanel.ScrolledPanel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent, size=(270, 0))

        self.scanner = self.GetParent().GetParent().GetParent().scanner

        self.SetupScrolling()

        #-- Graphic elements
        cameraParamsStaticText = wx.StaticText(self, wx.ID_ANY, _("Device Parameters"), style=wx.ALIGN_CENTRE)
        cameraParamsStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        stepDegreesLabel = wx.StaticText(self, label=_(u"Step degrees (º) :"))
        self.stepDegreesText = wx.TextCtrl(self, value=profile.getProfileSetting('step_degrees'), size=(82,-1))
        stepDelayLabel = wx.StaticText(self, label=_("Step delay (us) :"))
        self.stepDelayText = wx.TextCtrl(self, value=profile.getProfileSetting('step_delay'), size=(92,-1))

        applyConfigButton = wx.Button(self, -1, _("Apply Configuration"), size=(215,-1))

        #applyConfigButton = wx.Button(self, -1, _("Apply Configuration"))

        #-- Event

        applyConfigButton.Bind(wx.EVT_BUTTON, self.onApplyConfiguration)

        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        vbox.Add(cameraParamsStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(stepDegreesLabel, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.stepDegreesText, 0, wx.ALL^wx.LEFT, 12)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(stepDelayLabel, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.stepDelayText, 0, wx.ALL^wx.LEFT, 12)
        vbox.Add(hbox)

        vbox.Add((0, 0), 1, wx.EXPAND)

        vbox.Add(applyConfigButton, 0, wx.ALL, 18)

        self.SetSizer(vbox)

    def onApplyConfiguration(self, event):

        if self.stepDegreesText.GetValue() is not None:
            profile.putProfileSetting('step_degrees', float((self.stepDegreesText.GetValue()).replace(',','.')))

        if self.stepDelayText.GetValue() is not None:
            profile.putProfileSetting('step_delay', int(self.stepDelayText.GetValue()))

        if self.scanner.isConnected:
            self.scanner.device.sendConfiguration(profile.getProfileSettingFloat('step_degrees'), profile.getProfileSettingInteger('step_delay'))

    def updateProfileToAllControls(self):
        degrees = profile.getProfileSettingFloat('step_degrees')
        self.stepDegreesText.SetValue(str(degrees))
        delay = profile.getProfileSettingInteger('step_delay')
        self.stepDelayText.SetValue(str(delay))

        if self.scanner.isConnected:
            self.scanner.device.sendConfiguration(degrees, delay)