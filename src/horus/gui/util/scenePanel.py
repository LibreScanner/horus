#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: June 2014                                                       #
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

class ScenePanel(wx.lib.scrolledpanel.ScrolledPanel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent, size=(270, 0))

        self.scanner = self.GetParent().GetParent().GetParent().scanner

        self.SetupScrolling()
        
        #-- Graphic elements
        algorithmStaticText = wx.StaticText(self, label=_("Algorithm"))
        algorithmStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
        self.compactAlgRadioButton = wx.RadioButton(self, label=_("Compact"), size=(100,-1))
        self.completeAlgRadioButton = wx.RadioButton(self, label=_("Complete"), size=(100,-1))
        filterStaticText = wx.StaticText(self, label=_("Filter"))
        filterStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
        self.rhoMinTextCtrl = wx.TextCtrl(self, wx.ID_ANY, '', pos=(40, 10))
        self.rhoStaticText = wx.StaticText(self, label=_("<  R  <"))
        self.rhoMaxTextCtrl = wx.TextCtrl(self, wx.ID_ANY, '', pos=(40, 10))
        self.hMinTextCtrl = wx.TextCtrl(self, wx.ID_ANY, '', pos=(40, 10))
        self.hStaticText = wx.StaticText(self, label=_("<  H  <"))
        self.hMaxTextCtrl = wx.TextCtrl(self, wx.ID_ANY, '', pos=(40, 10))

        moveStaticText = wx.StaticText(self, wx.ID_ANY, _("Move"), style=wx.ALIGN_CENTRE)
        moveStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
        zStaticText = wx.StaticText(self, wx.ID_ANY, _("z"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.zSlider = wx.Slider(self, wx.ID_ANY, 0, -50, 50, size=(150, -1), style=wx.SL_LABELS)
        
        applyButton = wx.Button(self, label=_("Apply"), size=(100,-1))
        applyButton.Bind(wx.EVT_BUTTON, self.apply)

        #-- Bind
        self.Bind(wx.EVT_RADIOBUTTON, self.onAlgChanged, self.compactAlgRadioButton)
        self.Bind(wx.EVT_RADIOBUTTON, self.onAlgChanged, self.completeAlgRadioButton)
        self.Bind(wx.EVT_SLIDER, self.onZChanged, self.zSlider)
        self.Bind(wx.EVT_BUTTON, self.apply, applyButton)
        
        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(algorithmStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL^wx.TOP, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.compactAlgRadioButton, 0, wx.ALL, 15);
        hbox.Add(self.completeAlgRadioButton, 0, wx.ALL, 15);
        vbox.Add(hbox) 

        vbox.Add(filterStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.rhoMinTextCtrl, 0, wx.ALL, 15);
        hbox.Add(self.rhoStaticText, 0, wx.TOP, 20);
        hbox.Add(self.rhoMaxTextCtrl, 0, wx.ALL, 15);
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.hMinTextCtrl, 0, wx.ALL, 15);
        hbox.Add(self.hStaticText, 0, wx.TOP, 20);
        hbox.Add(self.hMaxTextCtrl, 0, wx.ALL, 15);
        vbox.Add(hbox)

        vbox.Add(moveStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(zStaticText, 0, wx.ALL^wx.RIGHT, 18)
        hbox.Add(self.zSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)

        vbox.Add((0, 0), 1, wx.EXPAND)  

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(applyButton, 1, wx.ALL, 10);
        vbox.Add(hbox)
        
        self.SetSizer(vbox)
        self.Centre()

    def onAlgChanged(self, event):
        self.scanner.getCore().setUseCompactAlgorithm(self.compactAlgRadioButton.GetValue())
        profile.putProfileSetting('use_compact', self.compactAlgRadioButton.GetValue())

    def onZChanged(self, event):
        self.scanner.getCore().setZOffset(self.zSlider.GetValue())
        profile.putProfileSetting('z_offset', self.zSlider.GetValue())
        
    def apply(self, event):
        self.scanner.getCore().setRangeFilter(int(self.rhoMinTextCtrl.GetValue()),
                                              int(self.rhoMaxTextCtrl.GetValue()),
                                              int(self.hMinTextCtrl.GetValue()),
                                              int(self.hMaxTextCtrl.GetValue()))
        profile.putProfileSetting('min_rho', int(self.rhoMinTextCtrl.GetValue()))
        profile.putProfileSetting('max_rho', int(self.rhoMaxTextCtrl.GetValue()))
        profile.putProfileSetting('min_h', int(self.hMinTextCtrl.GetValue()))
        profile.putProfileSetting('max_h', int(self.hMaxTextCtrl.GetValue()))

    def updateProfileToAllControls(self):
        self.compactAlgRadioButton.SetValue(profile.getProfileSettingBool('use_compact'))
        self.completeAlgRadioButton.SetValue(not profile.getProfileSettingBool('use_compact'))
        self.rhoMinTextCtrl.SetValue(profile.getProfileSetting('min_rho'))
        self.rhoMaxTextCtrl.SetValue(profile.getProfileSetting('max_rho'))
        self.hMinTextCtrl.SetValue(profile.getProfileSetting('min_h'))
        self.hMaxTextCtrl.SetValue(profile.getProfileSetting('max_h'))
        self.zSlider.SetValue(profile.getProfileSettingInteger('z_offset'))