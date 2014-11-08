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

import wx._core
import numpy as np

from horus.util import profile

from horus.gui.util.itemControls import *

from horus.engine.driver import Driver
from horus.engine import scan, calibration

#TODO: inheritance from CustomPanel
class CameraSettingsPanel(wx.Panel):
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, size=(275, -1))
        self.initialize()

    def initialize(self):
        self.driver = Driver.Instance()
        self.main = self.GetParent().GetParent().GetParent()

        if hasattr(self, 'controls'):
            del self.controls[:]
        self.controls = []

        #-- Graphic elements
        control = Control(self, _('Camera Settings'))
        control.append(Slider, 'brightness_calibration', self.driver.camera.setBrightness)
        control.append(Slider, 'contrast_calibration', self.driver.camera.setContrast)
        control.append(Slider, 'saturation_calibration', self.driver.camera.setSaturation)
        control.append(Slider, 'exposure_calibration', self.driver.camera.setExposure)
        control.append(ComboBox, 'framerate_calibration', lambda v: (self.driver.camera.setFrameRate(int(v)), self.reloadVideo()))
        control.append(ComboBox, 'resolution_calibration', lambda v: self.driver.camera.setResolution(int(v.split('x')[0]), int(v.split('x')[1])))
        control.append(CheckBox, 'use_distortion_calibration', lambda v: (self.driver.camera.setUseDistortion(v), self.reloadVideo()))
        control.append(Button, 'restore_default', self.restoreDefault)
        self.controls.append(control)

        # - Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        for control in self.controls:
            vbox.Add(control, 0, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(vbox)
        self.Layout()

        #-- Callbacks
        for control in self.controls:
            control.setUndoCallbacks(self.main.appendToUndo, self.main.releaseUndo)

        control.title.title.Bind(wx.EVT_LEFT_DOWN, self.onTitleClicked)

    def restoreDefault(self):
        dlg = wx.MessageDialog(self, _("This will reset calibration settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Calibration Settings reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            for control in self.controls:
                control.resetProfile()
            self.main.enableLabelTool(self.main.undoTool, False)
            self.reloadVideo()

    def disableContent(self):
        for control in self.controls:
            control.disableContent()

    def enableContent(self):
        for control in self.controls:
            control.enableContent()

    def hideContent(self):
        for control in self.controls:
            control.hideContent()

    def showContent(self):
        for control in self.controls:
            control.showContent()

    def reloadVideo(self):
        self.main.videoView.stop()
        if self.main.playing:
            self.main.videoView.play()

    def updateProfileToAllControls(self):
        for control in self.controls:
            control.updateProfile()

    def onTitleClicked(self, event):
        self.GetParent().GetParent().GetParent().hideAllPanels()
        self.showContent()
        self.Layout()


#TODO: inheritance from CustomPanel
class CalibrationPanel(wx.Panel):

    def __init__(self, parent, titleText="Workbench", buttonStartCallback=None, description="Workbench description"):
        wx.Panel.__init__(self, parent)

        self.buttonStartCallback = buttonStartCallback

        vbox = wx.BoxSizer(wx.VERTICAL)
        titleBox = wx.BoxSizer(wx.VERTICAL)
        contentBox = wx.BoxSizer(wx.VERTICAL)
        self.parametersBox = wx.BoxSizer(wx.VERTICAL)

        title = wx.Panel(self)
        self.content = wx.Panel(self)

        titleText = wx.StaticText(title, label=titleText)
        titleText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
        titleText.SetToolTip(wx.ToolTip(description))
        self.buttonEdit = wx.ToggleButton(self.content, wx.NewId(), label=_("Edit"))
        self.buttonEdit.SetMinSize((0,-1))
        self.buttonDefault = wx.Button(self.content, wx.NewId(), label=_("Default"))
        self.buttonDefault.SetMinSize((0,-1))
        self.buttonStart = wx.Button(self.content, wx.NewId(), label=_("Start"))
        self.buttonStart.SetMinSize((0,-1))

        titleBox.Add(titleText, 0, wx.ALL|wx.EXPAND, 5)
        titleBox.Add(wx.StaticLine(title), 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        title.SetSizer(titleBox)
        contentBox.Add(self.parametersBox, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.buttonEdit, 2, wx.ALL|wx.EXPAND, 3)
        hbox.Add(self.buttonDefault, 2, wx.ALL|wx.EXPAND, 3)
        hbox.Add(self.buttonStart, 3, wx.ALL|wx.EXPAND, 3)
        contentBox.Add(hbox, 0, wx.ALL|wx.EXPAND, 3)
        self.content.SetSizer(contentBox)

        vbox.Add(title, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 0)
        vbox.Add(self.content, 1, wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.EXPAND, 2)

        titleText.Bind(wx.EVT_LEFT_DOWN, self.onTitleClicked)
    	self.buttonEdit.Bind(wx.EVT_TOGGLEBUTTON, self.onButtonEditPressed)
    	self.buttonDefault.Bind(wx.EVT_BUTTON, self.onButtonDefaultPressed)
    	self.buttonStart.Bind(wx.EVT_BUTTON, self.onButtonStartPressed)

        self.SetSizer(vbox)
        self.Layout()

    def onButtonEditPressed(self, event):
        pass

    def onButtonDefaultPressed(self, event):
        pass

    def onButtonStartPressed(self, event):
        if self.buttonStartCallback is not None:
            self.buttonStartCallback()

    def hideContent(self):
        self.content.Hide()

    def onTitleClicked(self, event):
        self.GetParent().GetParent().GetParent().hideAllPanels()
        self.content.Show()
        self.Layout()


class CameraIntrinsicsPanel(CalibrationPanel):

    def __init__(self, parent, buttonStartCallback):
        CalibrationPanel.__init__(self, parent, titleText=_("Camera Intrinsics Calibration"), buttonStartCallback=buttonStartCallback,
                                  description=_("Determines the camera matrix and the distortion coefficients using Zhang2000 algorithm and pinhole camera model."))

        self.driver = Driver.Instance()
        self.pcg = scan.PointCloudGenerator.Instance()
        self.cameraIntrinsics = calibration.CameraIntrinsics.Instance()
        self.laserTriangulation = calibration.LaserTriangulation.Instance()
        self.platformExtrinsics = calibration.PlatformExtrinsics.Instance()

        cameraPanel = wx.Panel(self.content)
        distortionPanel = wx.Panel(self.content)

        cameraText = wx.StaticText(self.content, label=_("Camera matrix"))
        cameraText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.cameraTexts = [[0.0 for j in range(3)] for i in range(3)]
        self.cameraValues = np.zeros((3,3))

        cameraBox = wx.BoxSizer(wx.VERTICAL)
        cameraPanel.SetSizer(cameraBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            for j in range(3):
                jbox = wx.BoxSizer(wx.VERTICAL)
                self.cameraTexts[i][j] = wx.TextCtrl(cameraPanel, wx.ID_ANY, "")
                self.cameraTexts[i][j].SetMinSize((0,-1))
                self.cameraTexts[i][j].SetEditable(False)
                self.cameraTexts[i][j].Disable()
                jbox.Add(self.cameraTexts[i][j], 1, wx.ALL|wx.EXPAND, 2)
                ibox.Add(jbox, 1, wx.ALL|wx.EXPAND, 2)
            cameraBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        distortionText = wx.StaticText(self.content, label=_("Distortion vector"))
        distortionText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.distortionTexts = [0]*5
        self.distortionValues = np.zeros(5)

        distortionBox = wx.BoxSizer(wx.HORIZONTAL)
        distortionPanel.SetSizer(distortionBox)
        for i in range(5):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.distortionTexts[i] = wx.TextCtrl(distortionPanel, wx.ID_ANY, "")
            self.distortionTexts[i].SetMinSize((0,-1))
            self.distortionTexts[i].SetEditable(False)
            self.distortionTexts[i].Disable()
            ibox.Add(self.distortionTexts[i], 1, wx.ALL|wx.EXPAND, 2)
            distortionBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        self.parametersBox.Add(cameraText, 0, wx.ALL|wx.EXPAND, 8)
       	self.parametersBox.Add(cameraPanel, 0, wx.ALL|wx.EXPAND, 2)
        self.parametersBox.Add(distortionText, 0, wx.ALL|wx.EXPAND, 8)
       	self.parametersBox.Add(distortionPanel, 0, wx.ALL|wx.EXPAND, 2)

        self.Layout()

    def onButtonEditPressed(self, event):
        buttonEdit = self.GetParent().GetParent().buttonEdit
        enable = buttonEdit.GetValue()

        for i in range(3):
            for j in range(3):
                self.cameraTexts[i][j].SetEditable(enable)
                if enable:
                    self.cameraTexts[i][j].Enable()
                else:
                    self.cameraTexts[i][j].Disable()
                    self.cameraValues[i][j] = self.getValueFloat(self.cameraTexts[i][j].GetValue())

        for i in range(5):
            self.distortionTexts[i].SetEditable(enable)
            if enable:
                self.distortionTexts[i].Enable()
            else:
                self.distortionTexts[i].Disable()
                self.distortionValues[i] = self.getValueFloat(self.distortionTexts[i].GetValue())

        if enable:
            buttonEdit.SetLabel(_("OK"))
        else:
            buttonEdit.SetLabel(_("Edit"))
            self.updateAllControlsToProfile((self.cameraValues, self.distortionValues))

    def onButtonDefaultPressed(self, event):
        dlg = wx.MessageDialog(self, _("This will reset camera intrinsics profile settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Camera Intrinsics reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            profile.resetProfileSetting('camera_matrix')
            profile.resetProfileSetting('distortion_vector')
            self.updateProfileToAllControls()

    def getParameters(self):
        return self.cameraValues, self.distortionValues

    def setParameters(self, params):
        self.cameraValues = params[0]
        self.distortionValues = params[1]
        self.updateAllControls()

    def getProfileSettings(self):
        self.cameraValues = profile.getProfileSettingNumpy('camera_matrix')
        self.distortionValues = profile.getProfileSettingNumpy('distortion_vector')

    def putProfileSettings(self):
        profile.putProfileSettingNumpy('camera_matrix', self.cameraValues)
        profile.putProfileSettingNumpy('distortion_vector', self.distortionValues)

    def updateAllControls(self):
        for i in range(3):
            for j in range(3):
                self.cameraValues[i][j] = round(self.cameraValues[i][j], 3)
                self.cameraTexts[i][j].SetValue(str(self.cameraValues[i][j]))
        for i in range(5):
            self.distortionValues[i] = round(self.distortionValues[i], 4)
            self.distortionTexts[i].SetValue(str(self.distortionValues[i]))

    def updateEngine(self):
        if hasattr(self, 'driver'):
            self.driver.camera.setIntrinsics(self.cameraValues, self.distortionValues)
        if hasattr(self, 'cameraIntrinsics'):
            self.cameraIntrinsics.setIntrinsics(self.cameraValues, self.distortionValues)
        if hasattr(self, 'laserTriangulation'):
            self.laserTriangulation.setIntrinsics(self.cameraValues, self.distortionValues)
        if hasattr(self, 'platformExtrinsics'):
            self.platformExtrinsics.setIntrinsics(self.cameraValues, self.distortionValues)
        if hasattr(self, 'pcg'):
            self.pcg.setCameraIntrinsics(self.cameraValues, self.distortionValues)

    def updateProfileToAllControls(self):
        self.getProfileSettings()
        self.updateAllControls()
        self.updateEngine()

    def updateAllControlsToProfile(self):
        self.putProfileSettings()
        self.updateEngine()

    #TODO: move
    def getValueFloat(self, value): 
        try:
            return float(eval(value.replace(',', '.'), {}, {}))
        except:
            return 0.0


class LaserTriangulationPanel(CalibrationPanel):

    def __init__(self, parent, buttonStartCallback):
        CalibrationPanel.__init__(self, parent, titleText=_("Laser Triangulation Calibration"), buttonStartCallback=buttonStartCallback,
                                  description=_("Determines the depth of the intersection camera-laser considering the inclination of the lasers."))

        self.pcg = scan.PointCloudGenerator.Instance()

        coordinatesPanel = wx.Panel(self.content)
        originPanel = wx.Panel(self.content)
        normalPanel = wx.Panel(self.content)

        coordinatesText = wx.StaticText(self.content, label=_("Coordinates"))
        coordinatesText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.coordinatesTexts = [[0 for j in range(2)] for i in range(2)]
        self.coordinatesValues = np.zeros((2,2))

        coordinatesBox = wx.BoxSizer(wx.VERTICAL)
        coordinatesPanel.SetSizer(coordinatesBox)
        for i in range(2):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            for j in range(2):
                jbox = wx.BoxSizer(wx.VERTICAL)
                self.coordinatesTexts[i][j] = wx.TextCtrl(coordinatesPanel, wx.ID_ANY, "")
                self.coordinatesTexts[i][j].SetMinSize((0,-1))
                self.coordinatesTexts[i][j].SetEditable(False)
                self.coordinatesTexts[i][j].Disable()
                jbox.Add(self.coordinatesTexts[i][j], 1, wx.ALL|wx.EXPAND, 2)
                ibox.Add(jbox, 1, wx.ALL|wx.EXPAND, 2)
            coordinatesBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        originText = wx.StaticText(self.content, label=_("Origin"))
        originText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.originTexts = [0]*3
        self.originValues = np.zeros(3)

        originBox = wx.BoxSizer(wx.HORIZONTAL)
        originPanel.SetSizer(originBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.originTexts[i] = wx.TextCtrl(originPanel, wx.ID_ANY, "")
            self.originTexts[i].SetMinSize((0,-1))
            self.originTexts[i].SetEditable(False)
            self.originTexts[i].Disable()
            ibox.Add(self.originTexts[i], 1, wx.ALL|wx.EXPAND, 2)
            originBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        normalText = wx.StaticText(self.content, label=_("Normal"))
        normalText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.normalTexts = [0]*3
        self.normalValues = np.zeros(3)

        normalBox = wx.BoxSizer(wx.HORIZONTAL)
        normalPanel.SetSizer(normalBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.normalTexts[i] = wx.TextCtrl(normalPanel, wx.ID_ANY, "")
            self.normalTexts[i].SetMinSize((0,-1))
            self.normalTexts[i].SetEditable(False)
            self.normalTexts[i].Disable()
            ibox.Add(self.normalTexts[i], 1, wx.ALL|wx.EXPAND, 2)
            normalBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        self.parametersBox.Add(coordinatesText, 0, wx.ALL|wx.EXPAND, 8)
       	self.parametersBox.Add(coordinatesPanel, 0, wx.ALL|wx.EXPAND, 2)
        self.parametersBox.Add(originText, 0, wx.ALL|wx.EXPAND, 8)
       	self.parametersBox.Add(originPanel, 0, wx.ALL|wx.EXPAND, 2)
        self.parametersBox.Add(normalText, 0, wx.ALL|wx.EXPAND, 8)
        self.parametersBox.Add(normalPanel, 0, wx.ALL|wx.EXPAND, 2)

        self.Layout()

    def onButtonEditPressed(self, event):
        buttonEdit =self.GetParent().GetParent().buttonEdit
        enable = buttonEdit.GetValue()
        for i in range(2):
            for j in range(2):
                self.coordinatesTexts[i][j].SetEditable(enable)
                if enable:
                    self.coordinatesTexts[i][j].Enable()
                else:
                    self.coordinatesTexts[i][j].Disable()
                    self.coordinatesValues[i][j] = self.getValueFloat(self.coordinatesTexts[i][j].GetValue())

        for i in range(3):
            self.originTexts[i].SetEditable(enable)
            if enable:
                self.originTexts[i].Enable()
            else:
                self.originTexts[i].Disable()
                self.originValues[i] = self.getValueFloat(self.originTexts[i].GetValue())

        for i in range(3):
            self.normalTexts[i].SetEditable(enable)
            if enable:
                self.normalTexts[i].Enable()
            else:
                self.normalTexts[i].Disable()
                self.normalValues[i] = self.getValueFloat(self.normalTexts[i].GetValue())

        if enable:
            buttonEdit.SetLabel(_("OK"))
        else:
            buttonEdit.SetLabel(_("Edit"))
            self.updateAllControlsToProfile((self.coordinatesValues, self.originValues, self.normalValues))

    def onButtonDefaultPressed(self, event):
        dlg = wx.MessageDialog(self, _("This will reset laser triangulation profile settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Laser Triangulation reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            profile.resetProfileSetting('laser_coordinates')
            profile.resetProfileSetting('laser_origin')
            profile.resetProfileSetting('laser_normal')
            self.updateProfileToAllControls()

    def getParameters(self):
        return self.coordinatesValues, self.originValues, self.normalValues

    def setParameters(self, params):
        self.coordinatesValues = params[0]
        self.originValues = params[1]
        self.normalValues = params[2]
        self.updateAllControls()

    def getProfileSettings(self):
        self.coordinatesValues = profile.getProfileSettingNumpy('laser_coordinates')
        self.originValues = profile.getProfileSettingNumpy('laser_origin')
        self.normalValues = profile.getProfileSettingNumpy('laser_normal')

    def putProfileSettings(self):
        profile.putProfileSettingNumpy('laser_coordinates', self.coordinatesValues)
        profile.putProfileSettingNumpy('laser_origin', self.originValues)
        profile.putProfileSettingNumpy('laser_normal', self.normalValues)

    def updateAllControls(self):
        for i in range(2):
            for j in range(2):
                self.coordinatesValues[i][j] = round(self.coordinatesValues[i][j], 3)
                self.coordinatesTexts[i][j].SetValue(str(self.coordinatesValues[i][j]))

        for i in range(3):
            self.originValues[i] = round(self.originValues[i], 4)
            self.originTexts[i].SetValue(str(self.originValues[i]))

        for i in range(3):
            self.normalValues[i] = round(self.normalValues[i], 6)
            self.normalTexts[i].SetValue(str(self.normalValues[i]))

    def updateEngine(self):
        if hasattr(self, 'pcg'):
            self.pcg.setLaserTriangulation(self.coordinatesValues, self.originValues, self.normalValues)

    def updateProfileToAllControls(self):
        self.getProfileSettings()
        self.updateAllControls()
        self.updateEngine()

    def updateAllControlsToProfile(self):
        self.putProfileSettings()
        self.updateEngine()

    #TODO: move
    def getValueFloat(self, value): 
        try:
            return float(eval(value.replace(',', '.'), {}, {}))
        except:
            return 0.0


class PlatformExtrinsicsPanel(CalibrationPanel):

    def __init__(self, parent, buttonStartCallback):
        CalibrationPanel.__init__(self, parent, titleText=_("Platform Extrinsics Calibration"), buttonStartCallback=buttonStartCallback,
                                  description=_("Determines the transformation matrix between the camera and the platform using a circular interpolation method."))

        self.pcg = scan.PointCloudGenerator.Instance()

        vbox = wx.BoxSizer(wx.VERTICAL)

        rotationPanel = wx.Panel(self.content)
        translationPanel = wx.Panel(self.content)

        rotationText = wx.StaticText(self.content, label=_("Rotation matrix"))
        rotationText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.rotationTexts = [[0 for j in range(3)] for i in range(3)]
        self.rotationValues = np.zeros((3,3))

        rotationBox = wx.BoxSizer(wx.VERTICAL)
        rotationPanel.SetSizer(rotationBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            for j in range(3):
                jbox = wx.BoxSizer(wx.VERTICAL)
                self.rotationTexts[i][j] = wx.TextCtrl(rotationPanel, wx.ID_ANY, "")
                self.rotationTexts[i][j].SetMinSize((0,-1))
                self.rotationTexts[i][j].SetEditable(False)
                self.rotationTexts[i][j].Disable()
                jbox.Add(self.rotationTexts[i][j], 1, wx.ALL|wx.EXPAND, 2)
                ibox.Add(jbox, 1, wx.ALL|wx.EXPAND, 2)
            rotationBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        translationText = wx.StaticText(self.content, label=_("Translation vector"))
        translationText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.translationTexts = [0]*3
        self.translationValues = np.zeros(3)

        translationBox = wx.BoxSizer(wx.HORIZONTAL)
        translationPanel.SetSizer(translationBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.translationTexts[i] = wx.TextCtrl(translationPanel, wx.ID_ANY, "")
            self.translationTexts[i].SetMinSize((0,-1))
            self.translationTexts[i].SetEditable(False)
            self.translationTexts[i].Disable()
            ibox.Add(self.translationTexts[i], 1, wx.ALL|wx.EXPAND, 2)
            translationBox.Add(ibox, 1, wx.ALL|wx.EXPAND, 2)

        self.parametersBox.Add(rotationText, 0, wx.ALL|wx.EXPAND, 8)
        self.parametersBox.Add(rotationPanel, 0, wx.ALL|wx.EXPAND, 2)
        self.parametersBox.Add(translationText, 0, wx.ALL|wx.EXPAND, 8)
        self.parametersBox.Add(translationPanel, 0, wx.ALL|wx.EXPAND, 2)

        self.Layout

    def onButtonEditPressed(self, event):
        buttonEdit = self.GetParent().GetParent().buttonEdit
        enable = buttonEdit.GetValue()
        for i in range(3):
            for j in range(3):
                self.rotationTexts[i][j].SetEditable(enable)
                if enable:
                    self.rotationTexts[i][j].Enable()
                else:
                    self.rotationTexts[i][j].Disable()
                    self.rotationValues[i][j] = self.getValueFloat(self.rotationTexts[i][j].GetValue())
        for i in range(3):
            self.translationTexts[i].SetEditable(enable)
            if enable:
                self.translationTexts[i].Enable()
            else:
                self.translationTexts[i].Disable()
                self.translationValues[i] = self.getValueFloat(self.translationTexts[i].GetValue())

        if enable:
            buttonEdit.SetLabel(_("OK"))
        else:
            buttonEdit.SetLabel(_("Edit"))
            self.updateAllControlsToProfile((self.rotationValues, self.translationValues))

    def onButtonDefaultPressed(self, event):
        dlg = wx.MessageDialog(self, _("This will reset platform extrinsics profile settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Platform Extrinsics reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            profile.resetProfileSetting('rotation_matrix')
            profile.resetProfileSetting('translation_vector')
            self.updateProfileToAllControls()

    def getParameters(self):
        return self.rotationValues, self.translationValues

    def setParameters(self, params):
        self.rotationValues = params[0]
        self.translationValues = params[1]
        self.updateAllControls()

    def getProfileSettings(self):
        self.rotationValues = profile.getProfileSettingNumpy('rotation_matrix')
        self.translationValues = profile.getProfileSettingNumpy('translation_vector')

    def putProfileSettings(self):
        profile.putProfileSettingNumpy('rotation_matrix', self.rotationValues)
        profile.putProfileSettingNumpy('translation_vector', self.translationValues)

    def updateAllControls(self):
        for i in range(3):
            for j in range(3):
                self.rotationValues[i][j] = round(self.rotationValues[i][j], 6)
                self.rotationTexts[i][j].SetValue(str(self.rotationValues[i][j]))

        for i in range(3):
            self.translationValues[i] = round(self.translationValues[i], 4)
            self.translationTexts[i].SetValue(str(self.translationValues[i]))

    def updateEngine(self):
        if hasattr(self, 'pcg'):
            self.pcg.setPlatformExtrinsics(self.rotationValues, self.translationValues)

    def updateProfileToAllControls(self):
        self.getProfileSettings()
        self.updateAllControls()
        self.updateEngine()

    def updateAllControlsToProfile(self):
        self.putProfileSettings()
        self.updateEngine()

    #TODO: move
    def getValueFloat(self, value): 
        try:
            return float(eval(value.replace(',', '.'), {}, {}))
        except:
            return 0.0