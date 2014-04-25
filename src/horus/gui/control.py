#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: March 2014                                                      #
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

import os
import glob

import wx

from horus.language.multilingual import *

class ControlTabPanel(wx.Panel):
    """
    """

    def __init__(self, parent, scanner, viewer):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.scanner = scanner
        self.viewer = viewer
              
        #-- Graphic elements

        self.conParamsStaticText = wx.StaticText(self, -1, getString("PANEL_CONTROL_CONNECTION_PARAMETERS"), style=wx.ALIGN_CENTRE)
        self.serialNameLabel = wx.StaticText(self, label=getString("PANEL_CONTROL_SERIAL_NAME"))
        self.serialNames = self.serialList()
        self.serialNameCombo = wx.ComboBox(self, choices=self.serialNames, size=(110,-1))
        if len(self.serialNames) > 0:
            self.serialNameCombo.SetValue(self.serialNames[0])
        self.serialNameCombo.Bind(wx.EVT_COMBOBOX, self.resetMessage)
        self.cameraIdLabel = wx.StaticText(self, label=getString("PANEL_CONTROL_CAMERA_ID"))
        self.cameraIdNames = self.videoList()
        self.cameraIdCombo = wx.ComboBox(self, choices=self.cameraIdNames, size=(123,-1))
        if len(self.cameraIdNames) > 0:
            self.cameraIdCombo.SetValue(self.cameraIdNames[0])
        self.cameraIdCombo.Bind(wx.EVT_COMBOBOX, self.resetMessage)
        self.stepDegreesLabel = wx.StaticText(self, label=getString("PANEL_CONTROL_STEP_DEGREES"))
        self.stepDegreesText = wx.TextCtrl(self, value="0.45", size=(82,-1))
        self.stepDegreesText.Bind(wx.EVT_TEXT, self.resetMessage)
        self.stepDelayLabel = wx.StaticText(self, label=getString("PANEL_CONTROL_STEP_DELAY"))
        self.stepDelayText = wx.TextCtrl(self, value="800", size=(92,-1))
        self.stepDelayText.Bind(wx.EVT_TEXT, self.resetMessage)
        
        self.connectButton = wx.ToggleButton(self, label=getString("PANEL_CONTROL_CONNECT"), size=(100,-1))
        self.connectButton.Bind(wx.EVT_TOGGLEBUTTON, self.connect)
        self.startButton = wx.ToggleButton(self, label=getString("PANEL_CONTROL_START"), size=(100,-1))
        self.startButton.Bind(wx.EVT_TOGGLEBUTTON, self.start)
        self.scanStepButton = wx.Button(self, label=getString("PANEL_CONTROL_SCAN_STEP"), size=(100,-1))
        self.scanStepButton.Disable() # TODO
        self.scanStepButton.Bind(wx.EVT_BUTTON, self.scanStep)
        self.refreshButton = wx.ToggleButton(self, label=getString("PANEL_CONTROL_REFRESH_ON"), size=(100,-1))
        self.refreshButton.Bind(wx.EVT_TOGGLEBUTTON, self.refresh)
        
        self.laserLeftButton = wx.ToggleButton(self, label=getString("PANEL_CONTROL_LASER_L_ON"), size=(100,-1))
        self.laserLeftButton.Bind(wx.EVT_TOGGLEBUTTON, self.laserLeft)
        self.laserRightButton = wx.ToggleButton(self, label=getString("PANEL_CONTROL_LASER_R_ON"), size=(100,-1))
        self.laserRightButton.Bind(wx.EVT_TOGGLEBUTTON, self.laserRight)
        self.motorCCWButton = wx.Button(self, label=getString("PANEL_CONTROL_MOTOR_CCW"), size=(100,-1))
        self.motorCCWButton.Bind(wx.EVT_BUTTON, self.motorCCW)
        self.motorCWButton = wx.Button(self, label=getString("PANEL_CONTROL_MOTOR_CW"), size=(100,-1))
        self.motorCWButton.Bind(wx.EVT_BUTTON, self.motorCW)

        rawImageRadioButton = wx.RadioButton(self, label=getString("PANEL_CONTROL_RAW_IMAGE"), size=(100, -1))
        rawImageRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onRawImageSelected)
        laserImageRadioButton = wx.RadioButton(self, label=getString("PANEL_CONTROL_LASER_IMAGE"), size=(120, -1))
        laserImageRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onLaserImageSelected)
        diffImageRadioButton = wx.RadioButton(self, label=getString("PANEL_CONTROL_DIFF_IMAGE"), size=(100, -1))
        diffImageRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onDiffImageSelected)
        binImageRadioButton = wx.RadioButton(self, label=getString("PANEL_CONTROL_BINARY_IMAGE"), size=(120, -1))
        binImageRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onBinImageSelected)
        
        self.statusLabel = wx.StaticText(self, label=getString("PANEL_CONTROL_EMPTY"))
        
        #-- Layout
        
        vbox = wx.BoxSizer(wx.VERTICAL)
            
        vbox.Add(self.conParamsStaticText, 0, wx.ALL, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.serialNameLabel, 0, wx.ALL, 10)
        hbox.Add(self.serialNameCombo, 0, wx.ALL, 5)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(self.cameraIdLabel, 0, wx.ALL, 10)
        hbox.Add(self.cameraIdCombo, 0, wx.ALL, 5)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(self.stepDegreesLabel, 0, wx.ALL, 10)
        hbox.Add(self.stepDegreesText, 0, wx.ALL, 5)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(self.stepDelayLabel, 0, wx.ALL, 10)
        hbox.Add(self.stepDelayText, 0, wx.ALL, 5)
        vbox.Add(hbox)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(self.connectButton, 0, wx.ALL, 10);
        hbox.Add(self.startButton, 0, wx.ALL, 10);
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(self.scanStepButton, 0, wx.ALL, 10);
        hbox.Add(self.refreshButton, 0, wx.ALL, 10);
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(self.laserLeftButton, 0, wx.ALL, 10);
        hbox.Add(self.laserRightButton, 0, wx.ALL, 10);
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.motorCCWButton, 0, wx.ALL, 10);
        hbox.Add(self.motorCWButton, 0, wx.ALL, 10);
        vbox.Add(hbox)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(rawImageRadioButton, 0, wx.ALL^wx.RIGHT, 10)
        hbox.Add(laserImageRadioButton, 0, wx.ALL^wx.RIGHT, 10)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(diffImageRadioButton, 0, wx.ALL^wx.RIGHT, 10)
        hbox.Add(binImageRadioButton, 0, wx.ALL^wx.RIGHT, 10)
        vbox.Add(hbox)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(self.statusLabel, 0, wx.CENTER, 0);
        vbox.Add(hbox)
        
        self.SetSizer(vbox)
        self.Centre()

    def serialList(self):
        return self._deviceList("SERIALCOMM", ['/dev/ttyACM*', '/dev/ttyUSB*', "/dev/tty.usb*", "/dev/cu.*", "/dev/rfcomm*"])

    def videoList(self):
        return self._deviceList("VIDEO", ['/dev/video*'])

    def _deviceList(self, win_devices, linux_devices):
        baselist=[]
        if os.name=="nt":
            try:
                key=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"HARDWARE\\DEVICEMAP\\" + win_devices)
                i=0
                while(1):
                    baselist+=[_winreg.EnumValue(key,i)[1]]
                    i+=1
            except:
                pass
        for device in linux_devices:
            baselist = baselist + glob.glob(device)
        return baselist

    def connect(self, event):
        if not self.startButton.GetValue():
            if self.connectButton.GetValue():
                self.scanner.initialize(int(self.cameraIdCombo.GetValue()[-1:]),
                                        self.serialNameCombo.GetValue(),
                                        float((self.stepDegreesText.GetValue()).replace(',','.')),
                                        int(self.stepDelayText.GetValue()))
                if self.scanner.connect():
				    self.connectButton.SetLabel(getString("PANEL_CONTROL_DISCONNECT"))
				    self.statusLabel.SetLabel(u"")
            else:
                if self.scanner.disconnect():
                    self.connectButton.SetLabel(getString("PANEL_CONTROL_CONNECT"))
                    self.statusLabel.SetLabel(u"")
        else:
			self.connectButton.SetValue(not self.connectButton.GetValue())
			print getString("PANEL_CONTROL_STOP_SCAN")

    def start(self, event):
		if self.connectButton.GetValue():
			if self.startButton.GetValue():
				self.scanner.start()
				self.startButton.SetLabel(getString("PANEL_CONTROL_STOP"))
			else:
				self.scanner.stop()
				self.startButton.SetLabel(getString("PANEL_CONTROL_START"))
		else:
			self.startButton.SetValue(not self.startButton.GetValue())
			print getString("PANEL_CONTROL_DEVICE_NOT_CONNECTED")

    def scanStep(self, event=None):
        pass

    def refresh(self, event):
        btn = event.GetEventObject()
        if btn.GetValue():
            self.viewer.refreshOn(150) #280
            btn.SetLabel(getString("PANEL_CONTROL_REFRESH_OFF"))
        else:
            self.viewer.refreshOff()
            btn.SetLabel(getString("PANEL_CONTROL_REFRESH_ON"))

    def laserLeft(self, event):
		if self.connectButton.GetValue():
			if self.laserLeftButton.GetValue():
				self.scanner.getDevice().setLeftLaserOn()
				self.laserLeftButton.SetLabel(getString("PANEL_CONTROL_LASER_L_OFF"))
			else:
				self.scanner.getDevice().setLeftLaserOff()
				self.laserLeftButton.SetLabel(getString("PANEL_CONTROL_LASER_L_ON"))
		else:
			self.laserLeftButton.SetValue(not self.laserLeftButton.GetValue())
			print getString("PANEL_CONTROL_DEVICE_NOT_CONNECTED")
			
    def laserRight(self, event):
		if self.connectButton.GetValue():
			if self.laserRightButton.GetValue():
				self.scanner.getDevice().setRightLaserOn()
				self.laserRightButton.SetLabel(getString("PANEL_CONTROL_LASER_R_OFF"))
			else:
				self.scanner.getDevice().setRightLaserOff()
				self.laserRightButton.SetLabel(getString("PANEL_CONTROL_LASER_R_ON"))
		else:
			self.laserRightButton.SetValue(not self.laserRightButton.GetValue())
			print getString("PANEL_CONTROL_DEVICE_NOT_CONNECTED")

    def motorCW(self, event=None):
        if self.connectButton.GetValue():
            device = self.scanner.getDevice()
            device.enable()
            device.setMotorCW()
            device.disable()
        else:
            print getString("PANEL_CONTROL_DEVICE_NOT_CONNECTED")

    def motorCCW(self, event=None):
        if self.connectButton.GetValue():
            device = self.scanner.getDevice()
            device.enable()
            device.setMotorCCW()
            device.disable()
        else:
            print getString("PANEL_CONTROL_DEVICE_NOT_CONNECTED")

    def onRawImageSelected(self, event):
        self.scanner.getCore().setImageType(0)
    
    def onLaserImageSelected(self, event):
        self.scanner.getCore().setImageType(1)
        
    def onDiffImageSelected(self, event):
        self.scanner.getCore().setImageType(2)

    def onBinImageSelected(self, event):
        self.scanner.getCore().setImageType(3)
		
    def resetMessage(self, event=None):
		self.statusLabel.SetLabel(getString("PANEL_CONTROL_CONFIG_CHANGED_REBOOT"))

class VideoTabPanel(wx.Panel):
    """
    """
    def __init__(self, parent, scanner, viewer):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.scanner = scanner
        self.viewer = viewer
        
        #-- Graphic elements
        
        imgProcStaticText = wx.StaticText(self, -1, getString("PANEL_VIDEO_IMAGE_PROCESSING"), style=wx.ALIGN_CENTRE)
        self.blurCheckBox = wx.CheckBox(self, label=getString("PANEL_VIDEO_BLUR"), size=(67, -1))
        self.blurCheckBox.SetValue(True)
        self.blurCheckBox.Bind(wx.EVT_CHECKBOX, self.onBlurChanged)
        self.blurSlider = wx.Slider(self, -1, 4, 1, 10, size=(150, -1), style=wx.SL_LABELS)
        self.blurSlider.Bind(wx.EVT_SLIDER, self.onBlurChanged)
        self.openCheckBox = wx.CheckBox(self, label=getString("PANEL_VIDEO_OPEN"), size=(67, -1))
        self.openCheckBox.SetValue(True)
        self.openCheckBox.Bind(wx.EVT_CHECKBOX, self.onOpenChanged)
        self.openSlider = wx.Slider(self, -1, 5, 1, 10, size=(150, -1), style=wx.SL_LABELS)
        self.openSlider.Bind(wx.EVT_SLIDER, self.onOpenChanged)
        self.minHStaticText = wx.StaticText(self, -1, getString("PANEL_VIDEO_MIN_H"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.minHSlider = wx.Slider(self, -1, 0, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.minHSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.minSStaticText = wx.StaticText(self, -1, getString("PANEL_VIDEO_MIN_S"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.minSSlider = wx.Slider(self, -1, 180, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.minSSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.minVStaticText = wx.StaticText(self, -1, getString("PANEL_VIDEO_MIN_V"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.minVSlider = wx.Slider(self, -1, 30, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.minVSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.maxHStaticText = wx.StaticText(self, -1, getString("PANEL_VIDEO_MAX_H"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.maxHSlider = wx.Slider(self, -1, 180, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.maxHSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.maxSStaticText = wx.StaticText(self, -1, getString("PANEL_VIDEO_MAX_S"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.maxSSlider = wx.Slider(self, -1, 250, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.maxSSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.maxVStaticText = wx.StaticText(self, -1, getString("PANEL_VIDEO_MAX_V"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.maxVSlider = wx.Slider(self, -1, 140, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.maxVSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)

        roiStaticText = wx.StaticText(self, -1, getString("PANEL_VIDEO_ROI_SELECTION"), style=wx.ALIGN_CENTRE)
        rhoStaticText = wx.StaticText(self, -1, getString("PANEL_VIDEO_RADIUS"), size=(45, -1), style=wx.ALIGN_CENTRE)
        rhoSlider = wx.Slider(self, -1, 0, 0, 639, size=(150, -1), style=wx.SL_LABELS)
        rhoSlider.Bind(wx.EVT_SLIDER, self.onROIChanged)
        rhoSlider.Disable()
        #hStaticText = wx.StaticText(self, -1, " hight", size=(45, -1), style=wx.ALIGN_CENTRE)
        #hSlider = wx.Slider(self, -1, 0, 0, 479, size=(150, -1), style=wx.SL_LABELS)
        #hSlider.Bind(wx.EVT_SLIDER, self.OnROIChanged)
        #hSlider.Disable()
        
        #-- Layout
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        vbox.Add(imgProcStaticText, 0, wx.ALL, 10)
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
        
        vbox.Add(roiStaticText, 0, wx.ALL, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(rhoStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(rhoSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)
        #hbox = wx.BoxSizer(wx.HORIZONTAL)
        #hbox.Add(hStaticText, 0, wx.ALL, 18)
        #hbox.Add(hSlider, 0, wx.ALL, 0)
        #vbox.Add(hbox)
        
        self.SetSizer(vbox)
        self.Centre()

    def onBlurChanged(self, event):
        enable = self.blurCheckBox.IsChecked()
        value = self.blurSlider.GetValue()
        self.scanner.getCore().setBlur(enable, value)

    def onOpenChanged(self, event):
        enable = self.openCheckBox.IsChecked()
        value = self.openSlider.GetValue()
        self.scanner.getCore().setOpen(enable, value)

    def onHSVRangeChanged(self, event):
        self.scanner.getCore().setHSVRange(self.minHSlider.GetValue(),
                                         self.minSSlider.GetValue(),
                                         self.minVSlider.GetValue(),
                                         self.maxHSlider.GetValue(),
                                         self.maxSSlider.GetValue(),
                                         self.maxVSlider.GetValue())

    def onROIChanged(self, event):
        pass


class PointCloudTabPanel(wx.Panel):
    """
    """
    def __init__(self, parent, scanner):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.scanner = scanner
        
        #-- Graphic elements
        calParamsStaticText = wx.StaticText(self, label=getString("PANEL_POINTCLOUD_CALIBRATION_PARAMETERS"))
        self.fxParamStaticText = wx.StaticText(self, label=getString("PANEL_POINTCLOUD_FX"), size=(18, -1))
        self.fxParamTextCtrl = wx.TextCtrl(self, -1, u"1150", pos=(40, 10))
        self.fyParamStaticText = wx.StaticText(self, label=getString("PANEL_POINTCLOUD_FY"), size=(18, -1))
        self.fyParamTextCtrl = wx.TextCtrl(self, -1, u"1150", pos=(40, 10))
        self.cxParamStaticText = wx.StaticText(self, label=getString("PANEL_POINTCLOUD_CX"), size=(18, -1))
        self.cxParamTextCtrl = wx.TextCtrl(self, -1, u"269", pos=(40, 10))
        self.cyParamStaticText = wx.StaticText(self, label=getString("PANEL_POINTCLOUD_CY"), size=(18, -1))
        self.cyParamTextCtrl = wx.TextCtrl(self, -1, u"240", pos=(40, 10))
        self.zsParamStaticText = wx.StaticText(self, label=getString("PANEL_POINTCLOUD_ZS"), size=(18, -1))
        self.zsParamTextCtrl = wx.TextCtrl(self, -1, u"270", pos=(40, 10))
        self.hoParamStaticText = wx.StaticText(self, label=getString("PANEL_POINTCLOUD_HO"), size=(18, -15))
        self.hoParamTextCtrl = wx.TextCtrl(self, -1, u"50", pos=(40, 10))

        algorithmStaticText = wx.StaticText(self, label=getString("PANEL_POINTCLOUD_ALGORITHM"))
        self.compactAlgRadioButton = wx.RadioButton(self, label=getString("PANEL_POINTCLOUD_COMPACT"), size=(100,-1))
        self.compactAlgRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onAlgChanged)
        self.completeAlgRadioButton = wx.RadioButton(self, label=getString("PANEL_POINTCLOUD_COMPLETE"), size=(100,-1))
        self.completeAlgRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onAlgChanged)

        filterStaticText = wx.StaticText(self, label=getString("PANEL_POINTCLOUD_FILTER"))
        self.rhoMinTextCtrl = wx.TextCtrl(self, -1, u"-60", pos=(40, 10))
        self.rhoStaticText = wx.StaticText(self, label=getString("PANEL_POINTCLOUD_R"))
        self.rhoMaxTextCtrl = wx.TextCtrl(self, -1, u"60", pos=(40, 10))
        self.hMinTextCtrl = wx.TextCtrl(self, -1, u"0", pos=(40, 10))
        self.hStaticText = wx.StaticText(self, label=getString("PANEL_POINTCLOUD_H"))
        self.hMaxTextCtrl = wx.TextCtrl(self, -1, u"80", pos=(40, 10))

        moveStaticText = wx.StaticText(self, -1, getString("PANEL_POINTCLOUD_MOVE"), style=wx.ALIGN_CENTRE)
        zStaticText = wx.StaticText(self, -1, getString("PANEL_POINTCLOUD_Z"), size=(45, -1), style=wx.ALIGN_CENTRE)
        self.zSlider = wx.Slider(self, -1, 0, -50, 50, size=(150, -1), style=wx.SL_LABELS)
        self.zSlider.Bind(wx.EVT_SLIDER, self.onZChanged)
        
        saveButton = wx.Button(self, label=getString("PANEL_POINTCLOUD_SAVE"), size=(100,-1))
        saveButton.Bind(wx.EVT_BUTTON, self.save)
        applyButton = wx.Button(self, label=getString("PANEL_POINTCLOUD_APPLY"), size=(100,-1))
        applyButton.Bind(wx.EVT_BUTTON, self.apply)
        
        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        vbox.Add(calParamsStaticText, 0, wx.ALL, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.fxParamStaticText, 0, wx.ALL^wx.RIGHT, 10);
        hbox.Add(self.fxParamTextCtrl, 0, wx.ALL, 5);
        hbox.Add(self.fyParamStaticText, 0, wx.ALL^wx.RIGHT, 10);
        hbox.Add(self.fyParamTextCtrl, 0, wx.ALL, 5);
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.cxParamStaticText, 0, wx.ALL^wx.RIGHT, 10);
        hbox.Add(self.cxParamTextCtrl, 0, wx.ALL, 5);
        hbox.Add(self.cyParamStaticText, 0, wx.ALL^wx.RIGHT, 10);
        hbox.Add(self.cyParamTextCtrl, 0, wx.ALL, 5);
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.zsParamStaticText, 0, wx.ALL^wx.RIGHT, 10);
        hbox.Add(self.zsParamTextCtrl, 0, wx.ALL, 5);
        hbox.Add(self.hoParamStaticText, 0, wx.ALL^wx.RIGHT, 10);
        hbox.Add(self.hoParamTextCtrl, 0, wx.ALL, 5);
        vbox.Add(hbox)

        vbox.Add(algorithmStaticText, 0, wx.ALL, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.compactAlgRadioButton, 0, wx.ALL, 10);
        hbox.Add(self.completeAlgRadioButton, 0, wx.ALL, 10);
        vbox.Add(hbox) 

        vbox.Add(filterStaticText, 0, wx.ALL, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.rhoMinTextCtrl, 0, wx.ALL, 10);
        hbox.Add(self.rhoStaticText, 0, wx.TOP, 15);
        hbox.Add(self.rhoMaxTextCtrl, 0, wx.ALL, 10);
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.hMinTextCtrl, 0, wx.ALL, 10);
        hbox.Add(self.hStaticText, 0, wx.TOP, 15);
        hbox.Add(self.hMaxTextCtrl, 0, wx.ALL, 10);
        vbox.Add(hbox)

        vbox.Add(moveStaticText, 0, wx.ALL^wx.BOTTOM, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(zStaticText, 0, wx.ALL^wx.BOTTOM, 18)
        hbox.Add(self.zSlider, 0, wx.ALL, 0)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(applyButton, 0, wx.ALL^wx.BOTTOM, 10);
        hbox.Add(saveButton, 0, wx.ALL^wx.BOTTOM, 10);
        vbox.Add(hbox)
        
        self.SetSizer(vbox)
        self.Centre()

    def onAlgChanged(self, event):
        self.scanner.getCore().setUseCompactAlgorithm(self.compactAlgRadioButton.GetValue())

    def onZChanged(self, event):
        self.scanner.getCore().setZOffset(self.zSlider.GetValue())
		
    def apply(self, event):
        self.scanner.getCore().setCalibrationParams(int(self.fxParamTextCtrl.GetValue()),
                                                  int(self.fyParamTextCtrl.GetValue()),
                                                  int(self.cxParamTextCtrl.GetValue()),
                                                  int(self.cyParamTextCtrl.GetValue()),
                                                  int(self.zsParamTextCtrl.GetValue()),
                                                  int(self.hoParamTextCtrl.GetValue()))

        self.scanner.getCore().getCore().setRangeFilter(int(self.rhoMinTextCtrl.GetValue()),
                                                        int(self.rhoMaxTextCtrl.GetValue()),
                                                        int(self.hMinTextCtrl.GetValue()),
                                                        int(self.hMaxTextCtrl.GetValue()))    

    def save(self, event):
        saveFileDialog = wx.FileDialog(self, getString("PANEL_POINTCLOUD_SAVE_AS"), getString("PANEL_POINTCLOUD_EMPTY"), getString("PANEL_POINTCLOUD_EMPTY"), 
            getString("PANEL_POINTCLOUD_PLY_FILES"), wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if saveFileDialog.ShowModal() == wx.ID_OK:
            myCursor= wx.StockCursor(wx.CURSOR_WAIT)
            self.SetCursor(myCursor)
            plyData = self.scanner.getCore().toPLY()
            if plyData != None:
                with open(saveFileDialog.GetPath() + ".ply", 'w') as f:
                    f.write(plyData)
                    f.close()
            myCursor= wx.StockCursor(wx.CURSOR_ARROW)
            self.SetCursor(myCursor)
        saveFileDialog.Destroy()


class ControlNotebook(wx.Notebook):
    """
    """
    def __init__(self, parent, scanner, viewer):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)

        #-- Create and add tab panels
        self.AddPage(ControlTabPanel(self, scanner, viewer), getString("TAB_CONTROL_STR"))
        self.AddPage(VideoTabPanel(self, scanner, viewer), getString("TAB_VIDEO_STR"))
        self.AddPage(PointCloudTabPanel(self, scanner), getString("TAB_POINTCLOUD_STR"))

        #-- Events
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onPageChanging)

    def onPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def onPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()
