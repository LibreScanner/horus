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

class ScenePanel(wx.lib.scrolledpanel.ScrolledPanel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent, size=(270, 0))

        self.SetupScrolling()
        
        #-- Graphic elements


        algorithmStaticText = wx.StaticText(self, label=_("Algorithm"))
        algorithmStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
        self.compactAlgRadioButton = wx.RadioButton(self, label=_("Compact"), size=(100,-1))
        self.compactAlgRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onAlgChanged)
        self.completeAlgRadioButton = wx.RadioButton(self, label=_("Complete"), size=(100,-1))
        self.completeAlgRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onAlgChanged)

        filterStaticText = wx.StaticText(self, label=_("Filter"))
        filterStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
        self.rhoMinTextCtrl = wx.TextCtrl(self, -1, u"-60", pos=(40, 10))
        self.rhoStaticText = wx.StaticText(self, label=_("<  r  <"))
        self.rhoMaxTextCtrl = wx.TextCtrl(self, -1, u"60", pos=(40, 10))
        self.hMinTextCtrl = wx.TextCtrl(self, -1, u"0", pos=(40, 10))
        self.hStaticText = wx.StaticText(self, label=_("<  h  <"))
        self.hMaxTextCtrl = wx.TextCtrl(self, -1, u"80", pos=(40, 10))

        moveStaticText = wx.StaticText(self, -1, _("Move"), style=wx.ALIGN_CENTRE)
        moveStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
        zStaticText = wx.StaticText(self, -1, _("z"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.zSlider = wx.Slider(self, -1, 0, -50, 50, size=(150, -1), style=wx.SL_LABELS)
        self.zSlider.Bind(wx.EVT_SLIDER, self.onZChanged)
        
        saveButton = wx.Button(self, label=_("Save"), size=(100,-1))
        saveButton.Bind(wx.EVT_BUTTON, self.save)
        applyButton = wx.Button(self, label=_("Apply"), size=(100,-1))
        applyButton.Bind(wx.EVT_BUTTON, self.apply)
        
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
        hbox.Add(saveButton, 1, wx.ALL, 10);
        vbox.Add(hbox)
        
        self.SetSizer(vbox)
        self.Centre()

    def onAlgChanged(self, event):
        pass
        #self.scanner.getCore().setUseCompactAlgorithm(self.compactAlgRadioButton.GetValue())

    def onZChanged(self, event):
        pass
        #self.scanner.getCore().setZOffset(self.zSlider.GetValue())
        
    def apply(self, event):
        pass
        #self.scanner.getCore().setCalibrationParams(int(self.fxParamTextCtrl.GetValue()),
        #                                          int(self.fyParamTextCtrl.GetValue()),
        #                                          int(self.cxParamTextCtrl.GetValue()),
        #                                          int(self.cyParamTextCtrl.GetValue()),
        #                                          int(self.zsParamTextCtrl.GetValue()),
        #                                          int(self.hoParamTextCtrl.GetValue()))

        #self.scanner.getCore().getCore().setRangeFilter(int(self.rhoMinTextCtrl.GetValue()),
        #                                                int(self.rhoMaxTextCtrl.GetValue()),
        #                                                int(self.hMinTextCtrl.GetValue()),
        #                                                int(self.hMaxTextCtrl.GetValue()))    

    def save(self, event):
        pass
        #saveFileDialog = wx.FileDialog(self, _("Save As"), "", "", 
        #    _("PLY files (*.ply)|*.ply"), wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        #if saveFileDialog.ShowModal() == wx.ID_OK:
        #    myCursor= wx.StockCursor(wx.CURSOR_WAIT)
        #    self.SetCursor(myCursor)
        #    plyData = self.scanner.getCore().toPLY()
        #    if plyData != None:
        #        with open(saveFileDialog.GetPath() + ".ply", 'w') as f:
        #            f.write(plyData)
        #            f.close()
        #    myCursor= wx.StockCursor(wx.CURSOR_ARROW)
        #    self.SetCursor(myCursor)
        #saveFileDialog.Destroy()