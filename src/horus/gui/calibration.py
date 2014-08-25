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

from horus.util import profile

from horus.gui.util.workbenchConnection import *

class CalibrationWorkbench(WorkbenchConnection):

    def __init__(self, parent):
        WorkbenchConnection.__init__(self, parent, leftSize=1, middleSize=1, rightSize=1)


        self.addToLeft(CalibrationItemWorkbench(self._leftPanel,
        									    titleText=_("Camera Intrinsics"),
        									    itemType=CameraIntrinsicsPanel,
        									    description=_("Determines the camera matrix and the distortion coefficients using Zhang2000 algorithm and pinhole camera model.")))

        self.addToMiddle(CalibrationItemWorkbench(self._middlePanel,
        										  titleText=_("Laser Triangulation"),
        										  itemType=LaserTriangulationPanel,
        										  description=_("Determines the depth of the intersection camera-laser considering the inclination of the lasers.")))

        self.addToRight(CalibrationItemWorkbench(self._rightPanel,
        										 titleText=_("Platform Extrinsics"),
        										 itemType=PlatformExtrinsicsPanel,
        										 description=_("Determines the transformation matrix between the camera and the platform using a circular interpolation method.")))

        self.Layout()

	def updateToolbarStatus(self, status):
		if status:
			self._leftPanel.Enable()
		else:
			self._leftPanel.Disable()

    def updateProfileToAllControls(self):

	if self._leftObject is not None:
		self._leftObject.item.updateProfileToAllControls()

	if self._middleObject is not None:
		self._middleObject.item.updateProfileToAllControls()

	if self._rightObject is not None:
		self._rightObject.item.updateProfileToAllControls()

class CalibrationItemWorkbench(wx.Panel):

    def __init__(self, parent, titleText="Workbench", itemType=None, description="Workbench description"):
        wx.Panel.__init__(self, parent)

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
        if itemType is not None:
            self.item = itemType(content)
            contentBox.Add(self.item, 1, wx.ALL|wx.EXPAND, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.buttonEdit, 1, wx.ALL|wx.EXPAND, 5)
        hbox.Add(self.buttonDefault, 1, wx.ALL|wx.EXPAND, 5)
        hbox.Add(self.buttonStart, 2, wx.ALL|wx.EXPAND, 5)
        contentBox.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        content.SetSizer(contentBox)

        vbox.Add(title, 0, wx.ALL|wx.EXPAND, 2)
        vbox.Add(content, 1, wx.ALL|wx.EXPAND, 2)

        if itemType is not None:
        	self.buttonEdit.Bind(wx.EVT_TOGGLEBUTTON, self.item.onButtonEditPressed)
        	self.buttonDefault.Bind(wx.EVT_BUTTON, self.item.onButtonDefaultPressed)
        	self.buttonStart.Bind(wx.EVT_BUTTON, self.item.onButtonStartPressed)

        self.SetSizer(vbox)
        self.Layout()

class CameraIntrinsicsPanel(wx.Panel):

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

    def onButtonStartPressed(self, event):
    	pass

    def updateProfileToAllControls(self):
        cameraMatrix = profile.getProfileSettingNumpy('calibration_matrix')
        for i in range(3):
        	for j in range(3):
        		self.cameraTexts[i][j].SetValue(str(round(cameraMatrix[i][j], 3)))
        distortionVector = profile.getProfileSettingNumpy('distortion_vector')
        for i in range(5):
        	self.distortionTexts[i].SetValue(str(round(distortionVector[i], 4)))

class LaserTriangulationPanel(wx.Panel):

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

        self.depthTexts = [[0 for j in range(2)] for i in range(2)]
        self.depthValues = [[0 for j in range(2)] for i in range(2)]

        depthBox = wx.BoxSizer(wx.VERTICAL)
        depthPanel.SetSizer(depthBox)
        for i in range(2):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            for j in range(2):
                jbox = wx.BoxSizer(wx.VERTICAL)
                self.depthTexts[i][j] = wx.TextCtrl(depthPanel, wx.ID_ANY, "")
                self.depthTexts[i][j].SetEditable(False)
                jbox.Add(self.depthTexts[i][j], 1, wx.ALL|wx.EXPAND, 2)
                ibox.Add(jbox, 1, wx.ALL|wx.EXPAND, 2)
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
    	for i in range(2):
    		for j in range(2):
    			self.depthTexts[i][j].SetEditable(enable)
    			if not enable:
    				self.depthValues[i][j] = float(self.depthTexts[i][j].GetValue())
    	if not enable:
    		profile.putProfileSettingNumpy('laser_coordinates', self.coordinatesValues)
    		profile.putProfileSettingNumpy('laser_depth', self.depthValues)

    def onButtonDefaultPressed(self, event):
    	profile.resetProfileSetting('laser_coordinates')
    	profile.resetProfileSetting('laser_depth')
    	self.updateProfileToAllControls()

    def onButtonStartPressed(self, event):
    	pass

    def updateProfileToAllControls(self):
    	laserCoordinates = profile.getProfileSettingNumpy('laser_coordinates')
    	for i in range(2):
    		for j in range(2):
    			self.coordinatesTexts[i][j].SetValue(str(round(laserCoordinates[i][j], 3)))
    	laserDepth = profile.getProfileSettingNumpy('laser_depth')
    	for i in range(2):
    		for j in range(2):
    			self.depthTexts[i][j].SetValue(str(round(laserDepth[i][j], 3)))

class PlatformExtrinsicsPanel(wx.Panel):

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

    def onButtonStartPressed(self, event):
    	pass

    def updateProfileToAllControls(self):
    	rotationMatrix = profile.getProfileSettingNumpy('rotation_matrix')
    	for i in range(3):
    		for j in range(3):
    			self.rotationTexts[i][j].SetValue(str(round(rotationMatrix[i][j], 3)))
    	translationVector = profile.getProfileSettingNumpy('translation_vector')
    	for i in range(3):
    		self.translationTexts[i].SetValue(str(round(translationVector[i], 4)))