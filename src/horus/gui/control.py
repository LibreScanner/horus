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

import wx

class ControlTabPanel(wx.Panel):
    """
    """

    def __init__(self, parent, scanner, viewer):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.scanner = scanner
        self.viewer = viewer
              
        #-- Graphic elements

        self.conParamsStaticText = wx.StaticText(self, -1, "Connection Parameters", style=wx.ALIGN_CENTRE)
        self.serialNameLabel = wx.StaticText(self, label=" Serial Name :")
        self.serialNameText = wx.TextCtrl(self, value="/dev/ttyACM0",  size=(110,-1))
        self.serialNameText.Bind(wx.EVT_TEXT, self.resetMessage)
        self.cameraIdLabel = wx.StaticText(self, label=" Camera Id :")
        self.cameraIdText = wx.TextCtrl(self, value="0",  size=(123,-1))
        self.cameraIdText.Bind(wx.EVT_TEXT, self.resetMessage)
        self.stepDegreesLabel = wx.StaticText(self, label=" Step degrees (º) :")
        self.stepDegreesText = wx.TextCtrl(self, value="0.45",  size=(82,-1))
        self.stepDegreesText.Bind(wx.EVT_TEXT, self.resetMessage)
        self.stepDelayLabel = wx.StaticText(self, label=" Step delay (us) :")
        self.stepDelayText = wx.TextCtrl(self, value="10000",  size=(92,-1))
        self.stepDelayText.Bind(wx.EVT_TEXT, self.resetMessage)
        
        self.connectButton = wx.ToggleButton(self, label='Connect', size=(100,-1))
        self.connectButton.Bind(wx.EVT_TOGGLEBUTTON, self.connect)
        self.startButton = wx.ToggleButton(self, label='Start', size=(100,-1))
        self.startButton.Bind(wx.EVT_TOGGLEBUTTON, self.start)
        self.scanStepButton = wx.Button(self, label='Scan Step', size=(100,-1))
        self.scanStepButton.Disable() # TODO
        self.scanStepButton.Bind(wx.EVT_BUTTON, self.scanStep)
        self.refreshButton = wx.ToggleButton(self, label='Refresh On', size=(100,-1))
        self.refreshButton.Bind(wx.EVT_TOGGLEBUTTON, self.refresh)
        
        self.laserLeftButton = wx.ToggleButton(self, label='Laser L On', size=(100,-1))
        self.laserLeftButton.Bind(wx.EVT_TOGGLEBUTTON, self.laserLeft)
        self.laserRightButton = wx.ToggleButton(self, label='Laser R On', size=(100,-1))
        self.laserRightButton.Bind(wx.EVT_TOGGLEBUTTON, self.laserRight)
        self.motorCCWButton = wx.Button(self, label='Motor CCW', size=(100,-1))
        self.motorCCWButton.Bind(wx.EVT_BUTTON, self.motorCCW)
        self.motorCWButton = wx.Button(self, label='Motor CW', size=(100,-1))
        self.motorCWButton.Bind(wx.EVT_BUTTON, self.motorCW)

        rawImageRadioButton = wx.RadioButton(self, label="Raw image", size=(100, -1))
        rawImageRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onRawImageSelected)
        laserImageRadioButton = wx.RadioButton(self, label="Laser image", size=(120, -1))
        laserImageRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onLaserImageSelected)
        diffImageRadioButton = wx.RadioButton(self, label="Diff image", size=(100, -1))
        diffImageRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onDiffImageSelected)
        binImageRadioButton = wx.RadioButton(self, label="Binary image", size=(120, -1))
        binImageRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onBinImageSelected)
        
        self.statusLabel = wx.StaticText(self, label="")
        
        #-- Layout
        
        vbox = wx.BoxSizer(wx.VERTICAL)
            
        vbox.Add(self.conParamsStaticText, 0, wx.ALL, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.serialNameLabel, 0, wx.ALL, 10)
        hbox.Add(self.serialNameText, 0, wx.ALL, 5)
        vbox.Add(hbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        hbox.Add(self.cameraIdLabel, 0, wx.ALL, 10)
        hbox.Add(self.cameraIdText, 0, wx.ALL, 5)
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
   
    def connect(self, event):
		if not self.startButton.GetValue():
			if self.connectButton.GetValue():
				self.scanner.initialize(int(self.cameraIdText.GetValue()),
										self.serialNameText.GetValue(),
										float(self.stepDegreesText.GetValue()),
										int(self.stepDelayText.GetValue()))
				self.scanner.connect()
				self.connectButton.SetLabel("Disconnect")
				self.statusLabel.SetLabel("")
			else:
				self.scanner.Disconnect()
				self.connectButton.SetLabel("Connect")
				self.statusLabel.SetLabel("")
		else:
			self.connectButton.SetValue(not self.connectButton.GetValue())
			print "Stop scan!"

    def start(self, event):
		if self.connectButton.GetValue():
			if self.startButton.GetValue():
				self.scanner.start()
				self.startButton.SetLabel("Stop")
			else:
				self.scanner.stop()
				self.startButton.SetLabel("Start")
		else:
			self.startButton.SetValue(not self.startButton.GetValue())
			print "Device not connected"

    def scanStep(self, event=None):
        pass

    def refresh(self, event):
        btn = event.GetEventObject()
        if btn.GetValue():
            self.viewer.refreshOn(150) #280
            btn.SetLabel("Refresh Off")
        else:
            self.viewer.refreshOff()
            btn.SetLabel("Refresh On")

    def laserLeft(self, event):
		if self.connectButton.GetValue():
			if self.laserLeftButton.GetValue():
				self.scanner.getDevice().setLeftLaserOn()
				self.laserLeftButton.SetLabel("Laser L Off")
			else:
				self.scanner.getDevice().setLeftLaserOff()
				self.laserLeftButton.SetLabel("Laser L On")
		else:
			self.laserLeftButton.SetValue(not self.laserLeftButton.GetValue())
			print "Device not connected"
			
    def laserRight(self, event):
		if self.connectButton.GetValue():
			if self.laserRightButton.GetValue():
				self.scanner.getDevice().setRightLaserOn()
				self.laserRightButton.SetLabel("Laser R Off")
			else:
				self.scanner.getDevice().setRightLaserOff()
				self.laserRightButton.SetLabel("Laser R On")
		else:
			self.laserRightButton.SetValue(not self.laserRightButton.GetValue())
			print "Device not connected"

    def motorCW(self, event=None):
		if self.connectButton.GetValue():
			self.scanner.getDevice().setMotorCW()
		else:
			print "Device not connected"

    def motorCCW(self, event=None):
		if self.connectButton.getValue():
			self.scanner.getDevice().setMotorCCW()
		else:
			print "Device not connected"

    def onRawImageSelected(self, event):
        self.scanner.getCore().setImageType(0)
    
    def onLaserImageSelected(self, event):
        self.scanner.getCore().setImageType(1)
        
    def onDiffImageSelected(self, event):
        self.scanner.getCore().setImageType(2)

    def onBinImageSelected(self, event):
        self.scanner.getCore().setImageType(3)
		
    def resetMessage(self, event=None):
		self.statusLabel.SetLabel("   Config changed. You must reboot")


class VideoTabPanel(wx.Panel):
    """
    """
    def __init__(self, parent, scanner, viewer):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.scanner = scanner
        self.viewer = viewer
        
        #-- Graphic elements
        
        imgProcStaticText = wx.StaticText(self, -1, "Image Processing", style=wx.ALIGN_CENTRE)
        self.blurCheckBox = wx.CheckBox(self, label='Blur', size=(67, -1))
        self.blurCheckBox.SetValue(True)
        self.blurCheckBox.Bind(wx.EVT_CHECKBOX, self.onBlurChanged)
        self.blurSlider = wx.Slider(self, -1, 4, 1, 10, size=(150, -1), style=wx.SL_LABELS)
        self.blurSlider.Bind(wx.EVT_SLIDER, self.onBlurChanged)
        self.openCheckBox = wx.CheckBox(self, label='Open', size=(67, -1))
        self.openCheckBox.SetValue(True)
        self.openCheckBox.Bind(wx.EVT_CHECKBOX, self.onOpenChanged)
        self.openSlider = wx.Slider(self, -1, 5, 1, 10, size=(150, -1), style=wx.SL_LABELS)
        self.openSlider.Bind(wx.EVT_SLIDER, self.onOpenChanged)
        self.minHStaticText = wx.StaticText(self, -1, " min H", size=(45, -1), style=wx.ALIGN_CENTRE)
        self.minHSlider = wx.Slider(self, -1, 0, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.minHSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.minSStaticText = wx.StaticText(self, -1, " min S", size=(45, -1), style=wx.ALIGN_CENTRE)
        self.minSSlider = wx.Slider(self, -1, 180, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.minSSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.minVStaticText = wx.StaticText(self, -1, " min V", size=(45, -1), style=wx.ALIGN_CENTRE)
        self.minVSlider = wx.Slider(self, -1, 30, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.minVSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.maxHStaticText = wx.StaticText(self, -1, " max H", size=(45, -1), style=wx.ALIGN_CENTRE)
        self.maxHSlider = wx.Slider(self, -1, 180, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.maxHSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.maxSStaticText = wx.StaticText(self, -1, " max S", size=(45, -1), style=wx.ALIGN_CENTRE)
        self.maxSSlider = wx.Slider(self, -1, 250, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.maxSSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)
        self.maxVStaticText = wx.StaticText(self, -1, " max V", size=(45, -1), style=wx.ALIGN_CENTRE)
        self.maxVSlider = wx.Slider(self, -1, 140, 0, 255, size=(150, -1), style=wx.SL_LABELS)
        self.maxVSlider.Bind(wx.EVT_SLIDER, self.onHSVRangeChanged)

        roiStaticText = wx.StaticText(self, -1, "ROI Selection", style=wx.ALIGN_CENTRE)
        rhoStaticText = wx.StaticText(self, -1, " radius", size=(45, -1), style=wx.ALIGN_CENTRE)
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
        self.scanner.SetBlur(enable, value)

    def onOpenChanged(self, event):
        enable = self.openCheckBox.IsChecked()
        value = self.openSlider.GetValue()
        self.scanner.SetOpen(enable, value)

    def onHSVRangeChanged(self, event):
        self.scanner.SetHSVRange(self.minHSlider.GetValue(),
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
        calParamsStaticText = wx.StaticText(self, label="Calibration Parameters")
        self.fxParamStaticText = wx.StaticText(self, label="fx", size=(18, -1))
        self.fxParamTextCtrl = wx.TextCtrl(self, -1, "1150", pos=(40, 10))
        self.fyParamStaticText = wx.StaticText(self, label="fy", size=(18, -1))
        self.fyParamTextCtrl = wx.TextCtrl(self, -1, "1150", pos=(40, 10))
        self.cxParamStaticText = wx.StaticText(self, label="cx", size=(18, -1))
        self.cxParamTextCtrl = wx.TextCtrl(self, -1, "269", pos=(40, 10))
        self.cyParamStaticText = wx.StaticText(self, label="cy", size=(18, -1))
        self.cyParamTextCtrl = wx.TextCtrl(self, -1, "240", pos=(40, 10))
        self.zsParamStaticText = wx.StaticText(self, label="zs", size=(18, -1))
        self.zsParamTextCtrl = wx.TextCtrl(self, -1, "270", pos=(40, 10))
        self.hoParamStaticText = wx.StaticText(self, label="ho", size=(18, -15))
        self.hoParamTextCtrl = wx.TextCtrl(self, -1, "50", pos=(40, 10))

        algorithmStaticText = wx.StaticText(self, label="Algorithm")
        self.compactAlgRadioButton = wx.RadioButton(self, label='Compact', size=(100,-1))
        self.compactAlgRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onAlgChanged)
        self.completeAlgRadioButton = wx.RadioButton(self, label='Complete', size=(100,-1))
        self.completeAlgRadioButton.Bind(wx.EVT_RADIOBUTTON, self.onAlgChanged)

        filterStaticText = wx.StaticText(self, label="Filter")
        self.rhoMinTextCtrl = wx.TextCtrl(self, -1, "-60", pos=(40, 10))
        self.rhoStaticText = wx.StaticText(self, label="<  r  <")
        self.rhoMaxTextCtrl = wx.TextCtrl(self, -1, "60", pos=(40, 10))
        self.hMinTextCtrl = wx.TextCtrl(self, -1, "0", pos=(40, 10))
        self.hStaticText = wx.StaticText(self, label="<  h  <")
        self.hMaxTextCtrl = wx.TextCtrl(self, -1, "80", pos=(40, 10))

        moveStaticText = wx.StaticText(self, -1, "Move", style=wx.ALIGN_CENTRE)
        zStaticText = wx.StaticText(self, -1, " z", size=(45, -1), style=wx.ALIGN_CENTRE)
        self.zSlider = wx.Slider(self, -1, 0, -50, 50, size=(150, -1), style=wx.SL_LABELS)
        self.zSlider.Bind(wx.EVT_SLIDER, self.onZChanged)
        
        saveButton = wx.Button(self, label='Save', size=(100,-1))
        saveButton.Bind(wx.EVT_BUTTON, self.save)
        applyButton = wx.Button(self, label='Apply', size=(100,-1))
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
        self.scanner.setUseCompactAlgorithm(self.compactAlgRadioButton.GetValue())

    def onZChanged(self, event):
        self.scanner.setZOffset(self.zSlider.GetValue())
		
    def apply(self, event):
        self.scanner.setCalibrationParams(int(self.fxParamTextCtrl.GetValue()),
                                          int(self.fyParamTextCtrl.GetValue()),
                                          int(self.cxParamTextCtrl.GetValue()),
                                          int(self.cyParamTextCtrl.GetValue()),
                                          int(self.zsParamTextCtrl.GetValue()),
                                          int(self.hoParamTextCtrl.GetValue()))

        self.scanner.setRangeFilter(int(self.rhoMinTextCtrl.GetValue()),
                                    int(self.rhoMaxTextCtrl.GetValue()),
                                    int(self.hMinTextCtrl.GetValue()),
                                    int(self.hMaxTextCtrl.GetValue()))    

    def save(self, event):
        saveFileDialog = wx.FileDialog(self, "Save As", "", "", "PLY files (*.ply)|*.ply", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if saveFileDialog.ShowModal() == wx.ID_OK:
            myCursor= wx.StockCursor(wx.CURSOR_WAIT)
            self.SetCursor(myCursor)
            with open(saveFileDialog.GetPath() + ".ply", 'w') as f:
                f.write(self.scanner.GetPointCloudPLY())
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
        self.AddPage(ControlTabPanel(self, scanner, viewer), "Control")
        self.AddPage(VideoTabPanel(self, scanner, viewer), "Video")
        self.AddPage(PointCloudTabPanel(self, scanner), "Point Cloud")

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
