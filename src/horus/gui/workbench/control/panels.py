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
# the Free Software Foundation, either version 2 of the License, or     #
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
__license__ = "GNU General Public License v2 http://www.gnu.org/licenses/gpl.html"

import wx._core

from horus.gui.util.itemControls import *

from horus.util import profile

from horus.engine.driver import Driver

class CameraPanel(wx.Panel):
    """
    """
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, size=(275, 0))
        self.initialize()
        
    def initialize(self):
        self.driver = Driver.Instance()
        self.main = self.GetParent().GetParent().GetParent()

        if hasattr(self, 'controls'):
            del self.controls[:]
        self.controls = []

        #-- Graphic elements
        control = Control(self, _('Camera Control'))
        control.append(Slider, 'brightness_control', self.driver.camera.setBrightness)
        control.append(Slider, 'contrast_control', self.driver.camera.setContrast)
        control.append(Slider, 'saturation_control', self.driver.camera.setSaturation)
        control.append(Slider, 'exposure_control', self.driver.camera.setExposure)
        control.append(ComboBox, 'framerate_control', lambda v: (self.driver.camera.setFrameRate(int(v)), self.reloadVideo()))
        control.append(ComboBox, 'resolution_control', lambda v: self.driver.camera.setResolution(int(v.split('x')[0]), int(v.split('x')[1])))
        control.append(CheckBox, 'use_distortion_control', lambda v: (self.driver.camera.setUseDistortion(v), self.reloadVideo()))
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
        self.main.videoView.pause()
        if self.main.playing:
            self.main.videoView.play()

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
        self.control.Disable()
        self.waitCursor = wx.BusyCursor()
        if self.engineCallback is not None:
            ret = self.engineCallback(str(self.request.GetValue()), self.onFinishCallback)

    def onFinishCallback(self, ret):
        wx.CallAfter(self.control.Enable)
        wx.CallAfter(lambda: self.response.SetValue(ret))
        del self.waitCursor

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
        wx.Panel.__init__(self, parent=parent, size=(275, 0))
        self.initialize()

    def initialize(self):
        self.driver = Driver.Instance()
        self.main = self.GetParent().GetParent().GetParent()

        if hasattr(self, 'controls'):
            del self.controls[:]
        self.controls = []

        #-- Graphic elements
        control = Control(self, _('Laser Control'))
        control.append(ToggleButton, 'left_button', (self.driver.board.setLeftLaserOn, self.driver.board.setLeftLaserOff))
        control.append(ToggleButton, 'right_button', (self.driver.board.setRightLaserOn, self.driver.board.setRightLaserOff))
        self.controls.append(control)

        control = Control(self, _('Motor Control'))
        control.append(TextBox, 'step_degrees_control', lambda v: self.driver.board.setRelativePosition(self.getValueFloat(v)))
        control.append(TextBox, 'feed_rate_control', lambda v: self.driver.board.setSpeedMotor(self.getValueInteger(v)))
        control.append(TextBox, 'acceleration_control', lambda v: self.driver.board.setAccelerationMotor(self.getValueInteger(v)))
        control.append(CallbackButton, 'move_button', lambda c: self.driver.board.moveMotor(nonblocking=True, callback=c))
        control.append(ToggleButton, 'enable_button', (self.driver.board.enableMotor, self.driver.board.disableMotor))
        self.controls.append(control)

        control = Control(self, _('Gcode Commands'))
        control.append(GcodeGui, 'gcode_gui', lambda v, c: self.driver.board.sendRequest(v, nonblocking=True, callback=c, readLines=True))
        self.controls.append(control)

        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        for control in self.controls:
            vbox.Add(control, 0, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(vbox)

        #-- Callbacks
        for control in self.controls:
            control.setUndoCallbacks(self.main.appendToUndo, self.main.releaseUndo)

    #TODO: move
    def getValueInteger(self, value):
        try:
            return int(eval(value, {}, {}))
        except:
            return 0

    def getValueFloat(self, value): 
        try:
            return float(eval(value.replace(',', '.'), {}, {}))
        except:
            return 0.0

    def updateProfileToAllControls(self):
        for control in self.controls:
            control.updateProfile()