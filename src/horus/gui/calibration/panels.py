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

from horus.util.profile import *

from horus.engine.scanner import *
from horus.engine.calibration import *

class CalibrationWorkbenchPanel(wx.Panel):

    def __init__(self, parent, titleText="Workbench", parametersType=None, buttonStartCallback=None, description="Workbench description"):

        wx.Panel.__init__(self, parent)

        ##
        self.scanner = Scanner.Instance()
        self.calibration = Calibration.Instance()

        self.buttonStartCallback = buttonStartCallback

        vbox = wx.BoxSizer(wx.VERTICAL)
        titleBox = wx.BoxSizer(wx.VERTICAL)
        contentBox = wx.BoxSizer(wx.VERTICAL)

        title = wx.Panel(self)
        content = wx.Panel(self)

        titleText = wx.StaticText(title, label=titleText)
        titleText.SetFont((wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
        descText = wx.StaticText(content, label=description)
        self.buttonEdit = wx.ToggleButton(content, wx.NewId(), label=_("Edit"))
        self.buttonDefault = wx.Button(content, wx.NewId(), label=_("Default"))
        self.buttonStart = wx.Button(content, wx.NewId(), label=_("Start"))

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
                self.cameraTexts[i][j].Disable()
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
            self.distortionTexts[i].Disable()
            ibox.Add(self.distortionTexts[i], 1, wx.ALL|wx.EXPAND, 2)
            distortionBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        vbox.Add(cameraText, 0, wx.ALL|wx.EXPAND, 5)
       	vbox.Add(cameraPanel, 0, wx.ALL|wx.EXPAND, 2)
        vbox.Add(distortionText, 0, wx.ALL|wx.EXPAND, 5)
       	vbox.Add(distortionPanel, 0, wx.ALL|wx.EXPAND, 2)

        self.SetSizer(vbox)
        self.Layout()

    def onButtonEditPressed(self, event):
        buttonEdit = self.GetParent().GetParent().buttonEdit
        enable = buttonEdit.GetValue()
        for i in range(3):
            for j in range(3):
                self.cameraTexts[i][j].SetEditable(enable)
                if enable:
                    buttonEdit.SetLabel(_("OK"))
                    self.cameraTexts[i][j].Enable()
                else:
                    buttonEdit.SetLabel(_("Edit"))
                    self.cameraTexts[i][j].Disable()
                    self.cameraValues[i][j] = float(self.cameraTexts[i][j].GetValue())
        for i in range(5):
            self.distortionTexts[i].SetEditable(enable)
            if enable:
                self.distortionTexts[i].Enable()
            else:
                self.distortionTexts[i].Disable()
                self.distortionValues[i] = float(self.distortionTexts[i].GetValue())
        if not enable:
            self.updateAllControlsToProfile(self.cameraValues, self.distortionValues)

    def onButtonDefaultPressed(self, event):
        dlg = wx.MessageDialog(self, _("This will reset camera intrinsics profile settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Camera Intrinsics reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            resetProfileSetting('camera_matrix')
            resetProfileSetting('distortion_vector')
            self.updateProfileToAllControls()

    def Info(parent, message, caption = 'Insert program title'):
        dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def updateAllControls(self, cameraMatrix, distortionVector):
        for i in range(3):
            for j in range(3):
                self.cameraValues[i][j] = round(cameraMatrix[i][j], 3)
                self.cameraTexts[i][j].SetValue(str(self.cameraValues[i][j]))
        for i in range(5):
            self.distortionValues[i] = round(distortionVector[i], 4)
            self.distortionTexts[i].SetValue(str(self.distortionValues[i]))

        if hasattr(self, 'calibration'):
            self.calibration.setIntrinsics(cameraMatrix, distortionVector) ## TODO: remove setIntrinsics on calibration
        if hasattr(self, 'scanner'):
            self.scanner.camera.setIntrinsics(cameraMatrix, distortionVector)

    def updateAllControlsToProfile(self, cameraMatrix, distortionVector):
        putProfileSettingNumpy('camera_matrix', cameraMatrix)
        putProfileSettingNumpy('distortion_vector', distortionVector)
        self.updateAllControls(cameraMatrix, distortionVector)

    def updateProfileToAllControls(self):
        cameraMatrix = getProfileSettingNumpy('camera_matrix')
        distortionVector = getProfileSettingNumpy('distortion_vector')
        self.updateAllControls(cameraMatrix, distortionVector)

class LaserTriangulationParameters(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)

        coordinatesPanel = wx.Panel(self)
        originPanel = wx.Panel(self)
        normalPanel = wx.Panel(self)

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
                self.coordinatesTexts[i][j].Disable()
                jbox.Add(self.coordinatesTexts[i][j], 1, wx.ALL|wx.EXPAND, 2)
                ibox.Add(jbox, 1, wx.ALL|wx.EXPAND, 2)
            coordinatesBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        originText = wx.StaticText(self, label=_("Origin"))
        originText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.originTexts = [0]*3
        self.originValues = [0]*3

        originBox = wx.BoxSizer(wx.HORIZONTAL)
        originPanel.SetSizer(originBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.originTexts[i] = wx.TextCtrl(originPanel, wx.ID_ANY, "")
            self.originTexts[i].SetEditable(False)
            self.originTexts[i].Disable()
            ibox.Add(self.originTexts[i], 1, wx.ALL|wx.EXPAND, 2)
            originBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        normalText = wx.StaticText(self, label=_("Normal"))
        normalText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        self.normalTexts = [0]*3
        self.normalValues = [0]*3

        normalBox = wx.BoxSizer(wx.HORIZONTAL)
        normalPanel.SetSizer(normalBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.normalTexts[i] = wx.TextCtrl(normalPanel, wx.ID_ANY, "")
            self.normalTexts[i].SetEditable(False)
            self.normalTexts[i].Disable()
            ibox.Add(self.normalTexts[i], 1, wx.ALL|wx.EXPAND, 2)
            normalBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        vbox.Add(coordinatesText, 0, wx.ALL|wx.EXPAND, 5)
       	vbox.Add(coordinatesPanel, 0, wx.ALL|wx.EXPAND, 2)
        vbox.Add(originText, 0, wx.ALL|wx.EXPAND, 5)
       	vbox.Add(originPanel, 0, wx.ALL|wx.EXPAND, 2)
        vbox.Add(normalText, 0, wx.ALL|wx.EXPAND, 5)
        vbox.Add(normalPanel, 0, wx.ALL|wx.EXPAND, 2)

        self.SetSizer(vbox)
        self.Layout()

    def onButtonEditPressed(self, event):
        buttonEdit =self.GetParent().GetParent().buttonEdit
        enable = buttonEdit.GetValue()
        for i in range(2):
            for j in range(2):
                self.coordinatesTexts[i][j].SetEditable(enable)
                if enable:
                    buttonEdit.SetLabel(_("OK"))
                    self.coordinatesTexts[i][j].Enable()
                else:
                    buttonEdit.SetLabel(_("Edit"))
                    self.coordinatesTexts[i][j].Disable()
                    self.coordinatesValues[i][j] = round(float(self.coordinatesTexts[i][j].GetValue()), 3)

        for i in range(3):
            self.originTexts[i].SetEditable(enable)
            if enable:
                self.originTexts[i].Enable()
            else:
                self.originTexts[i].Disable()
                self.originValues[i] = round(float(self.coordinatesTexts[i][j].GetValue()), 5)

        for i in range(3):
            self.normalTexts[i].SetEditable(enable)
            if enable:
                self.normalTexts[i].Enable()
            else:
                self.normalTexts[i].Disable()
                self.normalValues[i] = round(float(self.coordinatesTexts[i][j].GetValue()), 5)

        if not enable:
            self.updateAllControlsToProfile(self.coordinatesValues, self.originValue, self.normalValues)

    def onButtonDefaultPressed(self, event):
        dlg = wx.MessageDialog(self, _("This will reset laser triangulation profile settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Laser Triangulation reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            resetProfileSetting('laser_coordinates')
            resetProfileSetting('laser_origin')
            resetProfileSetting('laser_normal')
            self.updateProfileToAllControls()

    def updateAllControls(self, laserCoordinates, laserOrigin, laserNormal):
        for i in range(2):
            for j in range(2):
                if laserCoordinates[i][j] is not None:
                    self.coordinatesValues[i][j] = round(laserCoordinates[i][j], 3)
                    self.coordinatesTexts[i][j].SetValue(str(self.coordinatesValues[i][j]))
                else:
                    self.coordinatesTexts[i][j].SetValue("0")

        for i in range(3):
            if laserOrigin[i] is not None:
                self.originValues[i] = round(laserOrigin[i], 5)
                self.originTexts[i].SetValue(str(self.originValues[i]))
            else:
                self.originTexts[i].SetValue("0")

        for i in range(3):
            if laserNormal[i] is not None:
                self.normalValues[i] = round(laserNormal[i], 5)
                self.normalTexts[i].SetValue(str(self.normalValues[i]))
            else:
                self.normalTexts[i].SetValue("0")

        if hasattr(self, 'scanner'):
            self.scanner.core.setLaserTriangulation(laserCoordinates, laserOrigin, laserNormal)

    def updateAllControlsToProfile(self, laserCoordinates, laserOrigin, laserNormal):
        putProfileSettingNumpy('laser_coordinates', laserCoordinates)
        putProfileSettingNumpy('laser_origin', laserOrigin)
        putProfileSettingNumpy('laser_normal', laserNormal)
        self.updateAllControls(laserCoordinates, laserOrigin, laserNormal)

    def updateProfileToAllControls(self):
        laserCoordinates = getProfileSettingNumpy('laser_coordinates')
        laserOrigin = getProfileSettingNumpy('laser_origin')
        laserNormal = getProfileSettingNumpy('laser_normal')
        self.updateAllControls(laserCoordinates, laserOrigin, laserNormal)


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
                self.rotationTexts[i][j].Disable()
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
            self.translationTexts[i].Disable()
            ibox.Add(self.translationTexts[i], 1, wx.ALL|wx.EXPAND, 2)
            translationBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        vbox.Add(rotationText, 0, wx.ALL|wx.EXPAND, 5)
        vbox.Add(rotationPanel, 0, wx.ALL|wx.EXPAND, 2)
        vbox.Add(translationText, 0, wx.ALL|wx.EXPAND, 5)
        vbox.Add(translationPanel, 0, wx.ALL|wx.EXPAND, 2)

        self.SetSizer(vbox)
        self.Layout

    def onButtonEditPressed(self, event):
        buttonEdit = self.GetParent().GetParent().buttonEdit
        enable = buttonEdit.GetValue()
        for i in range(3):
            for j in range(3):
                self.rotationTexts[i][j].SetEditable(enable)
                if enable:
                    buttonEdit.SetLabel(_("OK"))
                    self.rotationTexts[i][j].Enable()
                else:
                    buttonEdit.SetLabel(_("Edit"))
                    self.rotationTexts[i][j].Disable()
                    self.rotationValues[i][j] = float(self.rotationTexts[i][j].GetValue())
        for i in range(3):
            self.translationTexts[i].SetEditable(enable)
            if enable:
                self.translationTexts[i].Enable()
            else:
                self.translationTexts[i].Disable()
                self.translationValues[i] = float(self.translationTexts[i].GetValue())
        if not enable:
            self.updateAllControlsToProfile(self.rotationValues, self.translationValues)

    def onButtonDefaultPressed(self, event):
        dlg = wx.MessageDialog(self, _("This will reset platform extrinsics profile settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Platform Extrinsics reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            resetProfileSetting('rotation_matrix')
            resetProfileSetting('translation_vector')
            self.updateProfileToAllControls()

    def updateAllControls(self, rotationMatrix, translationVector):
        for i in range(3):
            for j in range(3):
                if rotationMatrix[i][j] is not None:
                    self.rotationValues[i][j] = round(rotationMatrix[i][j], 3)
                    self.rotationTexts[i][j].SetValue(str(self.rotationValues[i][j]))
                else:
                    self.rotationTexts[i][j].SetValue("")
        for i in range(3):
            if translationVector[i] is not None:
                self.translationValues[i] = round(translationVector[i], 3)
                self.translationTexts[i].SetValue(str(self.translationValues[i]))
            else:
                self.translationTexts[i].SetValue("")

        if hasattr(self, 'scanner'):
            self.scanner.core.setPlatformExtrinsics(rotationMatrix, translationVector)

    def updateAllControlsToProfile(self, rotationMatrix, translationVector):
        putProfileSettingNumpy('rotation_matrix', rotationMatrix)
        putProfileSettingNumpy('translation_vector', translationVector)
        self.updateAllControls(rotationMatrix, translationVector)

    def updateProfileToAllControls(self):
        rotationMatrix = getProfileSettingNumpy('rotation_matrix')
        translationVector = getProfileSettingNumpy('translation_vector')
        self.updateAllControls(rotationMatrix, translationVector)