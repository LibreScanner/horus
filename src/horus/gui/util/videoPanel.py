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

import wx
import wx.lib.scrolledpanel

class VideoPanel(wx.lib.scrolledpanel.ScrolledPanel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent, size=(270, 0))

        self.SetupScrolling()
        
        #-- Graphic elements
        
        imgProcStaticText = wx.StaticText(self, -1, _("Image Processing"), style=wx.ALIGN_CENTRE)
        imgProcStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
        self.blurCheckBox = wx.CheckBox(self, label=_("Blur"), size=(67, -1))
        self.blurCheckBox.SetValue(True)
        self.blurCheckBox.Bind(wx.EVT_CHECKBOX, self.onBlurChanged)
        self.blurSlider = wx.Slider(self, -1, 4, 1, 10, size=(150, -1), style=wx.SL_LABELS)
        self.blurSlider.Bind(wx.EVT_SLIDER, self.onBlurChanged)
        self.openCheckBox = wx.CheckBox(self, label=_("Open"), size=(67, -1))
        self.openCheckBox.SetValue(True)
        self.openCheckBox.Bind(wx.EVT_CHECKBOX, self.onOpenChanged)
        self.openSlider = wx.Slider(self, -1, 5, 1, 10, size=(150, -1), style=wx.SL_LABELS)
        self.openSlider.Bind(wx.EVT_SLIDER, self.onOpenChanged)
        self.minHStaticText = wx.StaticText(self, -1, _("min H"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.minHSlider = wx.Slider(self, -1, 0, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.minHSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.minSStaticText = wx.StaticText(self, -1, _("min S"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.minSSlider = wx.Slider(self, -1, 180, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.minSSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.minVStaticText = wx.StaticText(self, -1, _("min V"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.minVSlider = wx.Slider(self, -1, 30, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.minVSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.maxHStaticText = wx.StaticText(self, -1, _("max H"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.maxHSlider = wx.Slider(self, -1, 180, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.maxHSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.maxSStaticText = wx.StaticText(self, -1, _("max S"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.maxSSlider = wx.Slider(self, -1, 250, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.maxSSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.maxVStaticText = wx.StaticText(self, -1, _("max V"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.maxVSlider = wx.Slider(self, -1, 140, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.maxVSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)

        #roiStaticText = wx.StaticText(self, -1, _("ROI Selection"), style=wx.ALIGN_CENTRE)
        #rhoStaticText = wx.StaticText(self, -1, _("radius"), size=(45, -1), style=wx.ALIGN_CENTRE)
        #rhoSlider = wx.Slider(self, -1, 0, 0, 639, size=(150, -1), style=wx.SL_LABELS)
        #rhoSlider.Bind(wx.EVT_SLIDER, self.onROIChanged)
        #rhoSlider.Disable()
        #hStaticText = wx.StaticText(self, -1, " hight", size=(45, -1), style=wx.ALIGN_CENTRE)
        #hSlider = wx.Slider(self, -1, 0, 0, 479, size=(150, -1), style=wx.SL_LABELS)
        #hSlider.Bind(wx.EVT_SLIDER, self.OnROIChanged)
        #hSlider.Disable()
        
        #-- Layout
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        vbox.Add(imgProcStaticText, 0, wx.ALL, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.blurCheckBox, 0, wx.ALL^wx.RIGHT, 15)
        hbox.Add(self.blurSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.openCheckBox, 0, wx.ALL^wx.RIGHT, 15)
        hbox.Add(self.openSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.minHStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.minHSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.minSStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.minSSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.minVStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.minVSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.maxHStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.maxHSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.maxSStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.maxSSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.maxVStaticText, 0, wx.ALL, 18)
        hbox.Add(self.maxVSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        
        #vbox.Add(roiStaticText, 0, wx.ALL, 10)
        #hbox = wx.BoxSizer(wx.HORIZONTAL)
        #hbox.Add(rhoStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        #hbox.Add(rhoSlider, 0, wx.ALL, 0)
        #vbox.Add(hbox)
        #hbox = wx.BoxSizer(wx.HORIZONTAL)
        #hbox.Add(hStaticText, 0, wx.ALL, 18)
        #hbox.Add(hSlider, 0, wx.ALL, 0)
        #vbox.Add(hbox)
        
        self.SetSizer(vbox)
        self.Centre()

    def onBlurChanged(self, event):
    	pass
        """enable = self.blurCheckBox.IsChecked()
        value = self.blurSlider.GetValue()
        self.scanner.getCore().setBlur(enable, value)"""

    def onOpenChanged(self, event):
    	pass
        """enable = self.openCheckBox.IsChecked()
        value = self.openSlider.GetValue()
        self.scanner.getCore().setOpen(enable, value)"""

    def onHSVRangeChanged(self, event):
    	pass
        """self.scanner.getCore().setHSVRange(self.minHSlider.GetValue(),
                                         self.minSSlider.GetValue(),
                                         self.minVSlider.GetValue(),
                                         self.maxHSlider.GetValue(),
                                         self.maxSSlider.GetValue(),
                                         self.maxVSlider.GetValue())"""

    def onROIChanged(self, event):
        pass