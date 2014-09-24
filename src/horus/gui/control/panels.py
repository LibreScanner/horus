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

from horus.gui.util.itemControls import *

from horus.util.profile import *

from horus.engine.scanner import *

class CameraPanel(wx.Panel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, size=(275, 0))

        self.scanner = Scanner.Instance()
        self.main = self.GetParent().GetParent().GetParent()
        
        self.controls = []

        #-- Graphic elements
        control = Control(self, _('Camera Control'))
        control.append(Slider, 'brightness_control', self.scanner.camera.setBrightness)
        control.append(Slider, 'contrast_control', self.scanner.camera.setContrast)
        control.append(Slider, 'saturation_control', self.scanner.camera.setSaturation)
        control.append(Slider, 'exposure_control', self.scanner.camera.setExposure)
        control.append(ComboBox, 'framerate_control', lambda v: (self.scanner.camera.setFrameRate(int(v)), self.reloadVideo()))
        control.append(ComboBox, 'resolution_control', lambda v: self.scanner.camera.setResolution(int(v.split('x')[0]), int(v.split('x')[1])))
        control.append(CheckBox, 'use_distortion_control', lambda v: (self.scanner.camera.setUseDistortion(v), self.reloadVideo()))
        control.append(Button, 'restore_default', self.restoreDefault)
        self.controls.append(control)

        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        for control in self.controls:
            vbox.Add(control, 0, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(vbox)
        self.Layout()

        #-- Callbacks
        for control in self.controls:
            control.setUndoCallbacks(self.main.appendToUndo, self.main.releaseUndo)

    def restoreDefault(self):
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
        for control in self.controls:
            control.updateProfile()


class GcodeGui(ControlItem):
    def __init__(self, parent, name, engineCallback=None):
        """ """
        ControlItem.__init__(self, parent, name, engineCallback)

        #-- Elements
        self.request = wx.TextCtrl(self, size=(10,10))
        self.control = wx.Button(self, label=self.setting.getLabel())
        self.response = wx.TextCtrl(self, size=(10,150), style=wx.TE_MULTILINE)

        #-- Layout
        vbox =wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.request, 1, wx.ALL^wx.RIGHT^wx.LEFT|wx.EXPAND, 12)
        hbox.Add(self.control, 0, wx.ALL|wx.EXPAND, 12)
        vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 0)
        vbox.Add(self.response, 1, wx.ALL^wx.LEFT|wx.EXPAND, 12)
        self.SetSizer(vbox)
        self.Layout()

        #-- Events
        self.control.Bind(wx.EVT_BUTTON, self.onButtonClicked)

    def onButtonClicked(self, event):
        if self.engineCallback is not None:
            ret = self.engineCallback(self.request.GetValue())
            self.response.SetValue(ret)

    def updateProfile(self):
        if hasattr(self,'control'):
            self.update(None)

    def update(self, value):
        if self.isVisible():
            self.Show()
        else:
            self.Hide()

class DevicePanel(wx.Panel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, size=(270, 0))

        self.scanner = Scanner.Instance()
        self.main = self.GetParent().GetParent().GetParent()

        self.controls = []

        #-- Graphic elements
        control = Control(self, _('Laser Control'))
        control.append(ToggleButton, 'left_button', (self.scanner.device.setLeftLaserOn, self.scanner.device.setLeftLaserOff))
        control.append(ToggleButton, 'right_button', (self.scanner.device.setRightLaserOn, self.scanner.device.setRightLaserOff))
        self.controls.append(control)

        control = Control(self, _('Motor Control'))
        control.append(TextBox, 'step_degrees_control', lambda v: self.scanner.device.setRelativePosition(float(v)))
        control.append(TextBox, 'feed_rate_control', lambda v: self.scanner.device.setSpeedMotor(int(v)))
        control.append(TextBox, 'acceleration_control', lambda v: self.scanner.device.setAccelerationMotor(int(v)))
        control.append(Button, 'move_button', self.scanner.device.setMoveMotor)
        control.append(ToggleButton, 'enable_button', (self.scanner.device.enable, self.scanner.device.disable))
        self.controls.append(control)

        control = Control(self, _('Gcode Commands'))
        control.append(GcodeGui, 'gcode_gui', lambda v: self.scanner.device.sendCommand(v, readLines=True))
        self.controls.append(control)

        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        for control in self.controls:
            vbox.Add(control, 0, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(vbox)

        #-- Callbacks
        for control in self.controls:
            control.setUndoCallbacks(self.main.appendToUndo, self.main.releaseUndo)

    def updateProfileToAllControls(self):
        for control in self.controls:
            control.updateProfile()