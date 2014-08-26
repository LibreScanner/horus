#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: August 2014                                                     #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>   	                #
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

from horus.util import profile

class CalibrationWorkbenchPanel(wx.Panel):

    def __init__(self, parent, titleText="Workbench", parametersType=None, buttonStartCallback=None, description="Workbench description"):

        wx.Panel.__init__(self, parent)

        self.buttonStartCallback = buttonStartCallback

        vbox = wx.BoxSizer(wx.VERTICAL)
        titleBox = wx.BoxSizer(wx.VERTICAL)
        contentBox = wx.BoxSizer(wx.VERTICAL)

        title = wx.Panel(self)
        content = wx.Panel(self)

        titleText = wx.StaticText(title, label=titleText)
        titleText.SetFont((wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
        descText = wx.StaticText(content, label=description)
        self.buttonEdit = wx.ToggleButton(content, wx.NewId(), label="Edit")
        self.buttonDefault = wx.Button(content, wx.NewId(), label="Default")
        self.buttonStart = wx.Button(content, wx.NewId(), label="Start")

        titleBox.Add(titleText, 0, wx.ALL|wx.EXPAND, 10)
        title.SetSizer(titleBox)
        contentBox.Add(descText, 0, wx.ALL|wx.EXPAND, 10)
        if parametersType is not None:
            self.parameters = parametersType(content)
            contentBox.Add(self.parameters, 1, wx.ALL|wx.EXPAND, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.buttonEdit, 1, wx.ALL|wx.EXPAND, 5)
        hbox.Add(self.buttonDefault, 2, wx.ALL|wx.EXPAND, 5)
        hbox.Add(self.buttonStart, 3, wx.ALL|wx.EXPAND, 5)
        contentBox.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        content.SetSizer(contentBox)

        vbox.Add(title, 0, wx.ALL|wx.EXPAND, 2)
        vbox.Add(content, 1, wx.ALL|wx.EXPAND, 2)

    	self.buttonEdit.Bind(wx.EVT_TOGGLEBUTTON, self.parameters.onButtonEditPressed)
    	self.buttonDefault.Bind(wx.EVT_BUTTON, self.parameters.onButtonDefaultPressed)
    	self.buttonStart.Bind(wx.EVT_BUTTON, self.onButtonStartPressed)

        self.SetSizer(vbox)
        self.Layout()

    def onButtonStartPressed(self, event):
        if self.buttonStartCallback is not None:
            self.buttonStartCallback()

class CameraIntrinsicsParameters(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)

        cameraPanel = wx.Panel(self)
        distortionPanel = wx.Panel(self)

        cameraText = wx.StaticText(self, label=_("Camera matrix"))
        cameraText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.cameraTexts = [[0 for j in range(3)] for i in range(3)]
        self.cameraValues = [[0 for j in range(3)] for i in range(3)]

        cameraBox = wx.BoxSizer(wx.VERTICAL)
        cameraPanel.SetSizer(cameraBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            for j in range(3):
                jbox = wx.BoxSizer(wx.VERTICAL)
                self.cameraTexts[i][j] = wx.TextCtrl(cameraPanel, wx.ID_ANY, "")
                self.cameraTexts[i][j].SetEditable(False)
                jbox.Add(self.cameraTexts[i][j], 1, wx.ALL|wx.EXPAND, 2)
                ibox.Add(jbox, 1, wx.ALL|wx.EXPAND, 2)
            cameraBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        distortionText = wx.StaticText(self, label=_("Distortion vector"))
        distortionText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.distortionTexts = [0]*5
        self.distortionValues = [0]*5

        distortionBox = wx.BoxSizer(wx.HORIZONTAL)
        distortionPanel.SetSizer(distortionBox)
        for i in range(5):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.distortionTexts[i] = wx.TextCtrl(distortionPanel, wx.ID_ANY, "")
            self.distortionTexts[i].SetEditable(False)
            ibox.Add(self.distortionTexts[i], 1, wx.ALL|wx.EXPAND, 2)
            distortionBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        vbox.Add(cameraText, 0, wx.ALL|wx.EXPAND, 5)
       	vbox.Add(cameraPanel, 0, wx.ALL|wx.EXPAND, 2)
        vbox.Add(distortionText, 0, wx.ALL|wx.EXPAND, 5)
       	vbox.Add(distortionPanel, 0, wx.ALL|wx.EXPAND, 2)

        self.SetSizer(vbox)
        self.Layout()

    def onButtonEditPressed(self, event):
        enable = self.GetParent().GetParent().buttonEdit.GetValue()
        for i in range(3):
            for j in range(3):
                self.cameraTexts[i][j].SetEditable(enable)
                if not enable:
                    self.cameraValues[i][j] = float(self.cameraTexts[i][j].GetValue())
        for i in range(5):
            self.distortionTexts[i].SetEditable(enable)
            if not enable:
                    self.distortionValues[i] = float(self.distortionTexts[i].GetValue())
        if not enable:
            profile.putProfileSettingNumpy('calibration_matrix', self.cameraValues)
            profile.putProfileSettingNumpy('distortion_vector', self.distortionValues)

    def onButtonDefaultPressed(self, event):
        profile.resetProfileSetting('calibration_matrix')
        profile.resetProfileSetting('distortion_vector')
        self.updateProfileToAllControls()

    def updateProfileToAllControls(self):
        cameraMatrix = profile.getProfileSettingNumpy('calibration_matrix')
        for i in range(3):
            for j in range(3):
                self.cameraTexts[i][j].SetValue(str(round(cameraMatrix[i][j], 3)))
        distortionVector = profile.getProfileSettingNumpy('distortion_vector')
        for i in range(5):
            self.distortionTexts[i].SetValue(str(round(distortionVector[i], 4)))


class LaserTriangulationParameters(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)

        coordinatesPanel = wx.Panel(self)
        depthPanel = wx.Panel(self)

        coordinatesText = wx.StaticText(self, label=_("Coordinates"))
        coordinatesText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.coordinatesTexts = [[0 for j in range(2)] for i in range(2)]
        self.coordinatesValues = [[0 for j in range(2)] for i in range(2)]

        coordinatesBox = wx.BoxSizer(wx.VERTICAL)
        coordinatesPanel.SetSizer(coordinatesBox)
        for i in range(2):
        	ibox = wx.BoxSizer(wx.HORIZONTAL)
        	for j in range(2):
        		jbox = wx.BoxSizer(wx.VERTICAL)
        		self.coordinatesTexts[i][j] = wx.TextCtrl(coordinatesPanel, wx.ID_ANY, "")
        		self.coordinatesTexts[i][j].SetEditable(False)
        		jbox.Add(self.coordinatesTexts[i][j], 1, wx.ALL|wx.EXPAND, 2)
        		ibox.Add(jbox, 1, wx.ALL|wx.EXPAND, 2)
        	coordinatesBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        depthText = wx.StaticText(self, label=_("Depth"))
        depthText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.depthText = 0
        self.depthValue = 0

        depthBox = wx.BoxSizer(wx.VERTICAL)
        depthPanel.SetSizer(depthBox)
        ibox = wx.BoxSizer(wx.HORIZONTAL)
        self.depthText = wx.TextCtrl(depthPanel, wx.ID_ANY, "")
        self.depthText.SetEditable(False)
        ibox.Add(self.depthText, 1, wx.ALL|wx.EXPAND, 2)
        depthBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        vbox.Add(coordinatesText, 0, wx.ALL|wx.EXPAND, 5)
       	vbox.Add(coordinatesPanel, 0, wx.ALL|wx.EXPAND, 2)
        vbox.Add(depthText, 0, wx.ALL|wx.EXPAND, 5)
       	vbox.Add(depthPanel, 0, wx.ALL|wx.EXPAND, 2)

        self.SetSizer(vbox)
        self.Layout()

    def onButtonEditPressed(self, event):
        enable = self.GetParent().GetParent().buttonEdit.GetValue()
        for i in range(2):
            for j in range(2):
                self.coordinatesTexts[i][j].SetEditable(enable)
                if not enable:
                    self.coordinatesValues[i][j] = float(self.coordinatesTexts[i][j].GetValue())
        self.depthText.SetEditable(enable)
        if not enable:
            self.depthValue = float(self.depthText.GetValue())
        if not enable:
            profile.putProfileSettingNumpy('laser_coordinates', self.coordinatesValues)
            profile.putProfileSettingFloat('laser_depth', self.depthValue)

    def onButtonDefaultPressed(self, event):
        profile.resetProfileSetting('laser_coordinates')
        profile.resetProfileSetting('laser_depth')
        self.updateProfileToAllControls()

    def updateProfileToAllControls(self):
    	laserCoordinates = profile.getProfileSettingNumpy('laser_coordinates')
    	for i in range(2):
    		for j in range(2):
    			self.coordinatesTexts[i][j].SetValue(str(round(laserCoordinates[i][j], 3)))
    	laserDepth = profile.getProfileSettingNumpy('laser_depth')
    	self.depthText.SetValue(str(round(laserDepth, 3)))


class PlatformExtrinsicsParameters(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)

        rotationPanel = wx.Panel(self)
        translationPanel = wx.Panel(self)

        rotationText = wx.StaticText(self, label=_("Rotation matrix"))
        rotationText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.rotationTexts = [[0 for j in range(3)] for i in range(3)]
        self.rotationValues = [[0 for j in range(3)] for i in range(3)]

        rotationBox = wx.BoxSizer(wx.VERTICAL)
        rotationPanel.SetSizer(rotationBox)
        for i in range(3):
        	ibox = wx.BoxSizer(wx.HORIZONTAL)
        	for j in range(3):
        		jbox = wx.BoxSizer(wx.VERTICAL)
        		self.rotationTexts[i][j] = wx.TextCtrl(rotationPanel, wx.ID_ANY, "")
        		self.rotationTexts[i][j].SetEditable(False)
        		jbox.Add(self.rotationTexts[i][j], 1, wx.ALL|wx.EXPAND, 2)
        		ibox.Add(jbox, 1, wx.ALL|wx.EXPAND, 2)
        	rotationBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        translationText = wx.StaticText(self, label=_("Translation vector"))
        translationText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.translationTexts = [0]*3
        self.translationValues = [0]*3

        translationBox = wx.BoxSizer(wx.HORIZONTAL)
        translationPanel.SetSizer(translationBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.translationTexts[i] = wx.TextCtrl(translationPanel, wx.ID_ANY, "")
            self.translationTexts[i].SetEditable(False)
            ibox.Add(self.translationTexts[i], 1, wx.ALL|wx.EXPAND, 2)
            translationBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        vbox.Add(rotationText, 0, wx.ALL|wx.EXPAND, 5)
       	vbox.Add(rotationPanel, 0, wx.ALL|wx.EXPAND, 2)
        vbox.Add(translationText, 0, wx.ALL|wx.EXPAND, 5)
       	vbox.Add(translationPanel, 0, wx.ALL|wx.EXPAND, 2)

        self.SetSizer(vbox)
        self.Layout

    def onButtonEditPressed(self, event):
        enable = self.GetParent().GetParent().buttonEdit.GetValue()
        for i in range(3):
            for j in range(3):
                self.rotationTexts[i][j].SetEditable(enable)
                if not enable:
                    self.rotationValues[i][j] = float(self.rotationTexts[i][j].GetValue())
        for i in range(3):
            self.translationTexts[i].SetEditable(enable)
            if not enable:
                self.translationValues[i] = float(self.translationTexts[i].GetValue())
        if not enable:
            profile.putProfileSettingNumpy('rotation_matrix', self.rotationValues)
            profile.putProfileSettingNumpy('translation_vector', self.translationValues)

    def onButtonDefaultPressed(self, event):
        profile.resetProfileSetting('rotation_matrix')
        profile.resetProfileSetting('translation_vector')
        self.updateProfileToAllControls()

    def updateProfileToAllControls(self):
    	rotationMatrix = profile.getProfileSettingNumpy('rotation_matrix')
    	for i in range(3):
    		for j in range(3):
    			self.rotationTexts[i][j].SetValue(str(round(rotationMatrix[i][j], 3)))
    	translationVector = profile.getProfileSettingNumpy('translation_vector')
    	for i in range(3):
    		self.translationTexts[i].SetValue(str(round(translationVector[i], 4)))