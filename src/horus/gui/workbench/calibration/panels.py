# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
import numpy as np

from horus.gui.util.customPanels import ExpandablePanel, Slider, Button, FloatTextBox

from horus.util import profile

from horus.engine.driver.driver import Driver
from horus.engine.calibration.pattern import Pattern
from horus.engine.calibration.autocheck import Autocheck, PatternNotDetected, \
    WrongMotorDirection, LaserNotDetected

driver = Driver()
pattern = Pattern()


class PatternSettingsPanel(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(
            self, parent, _("Pattern settings"), hasUndo=False)

        self.clearSections()
        section = self.createSection('pattern_settings')
        section.addItem(Slider, 'pattern_rows', tooltip=_(
            'Number of corner rows in the pattern'))
        section.addItem(Slider, 'pattern_columns', tooltip=_(
            'Number of corner columns in the pattern'))
        section.addItem(FloatTextBox, 'pattern_square_width')
        section.addItem(FloatTextBox, 'pattern_origin_distance', tooltip=_(
            "Minimum distance between the origin of the pattern (bottom-left corner) "
            "and the pattern's base surface"))

    def updateCallbacks(self):
        section = self.sections['pattern_settings']
        section.updateCallback('pattern_rows', lambda v: self.updatePatternParameters())
        section.updateCallback('pattern_columns', lambda v: self.updatePatternParameters())
        section.updateCallback('pattern_square_width', lambda v: self.updatePatternParameters())
        section.updateCallback('pattern_origin_distance', lambda v: self.updatePatternParameters())

    def updatePatternParameters(self):
        pattern.rows = profile.settings['pattern_rows']
        pattern.columns = profile.settings['pattern_columns']
        pattern.square_width = profile.settings['pattern_square_width']
        pattern.distance = profile.settings['pattern_origin_distance']


class AutocheckPanel(ExpandablePanel):

    def __init__(self, parent, buttonStartCallback=None, buttonStopCallback=None):
        ExpandablePanel.__init__(
            self, parent, _("Scanner autocheck"), hasUndo=False, hasRestore=False)

        self.autocheck = Autocheck()
        self.buttonStartCallback = buttonStartCallback
        self.buttonStopCallback = buttonStopCallback

        self.clearSections()
        section = self.createSection('scanner_autocheck')
        section.addItem(Button, 'autocheck_button')

    def updateCallbacks(self):
        section = self.sections['scanner_autocheck']
        section.updateCallback('autocheck_button', self.buttonStartCallback)

    # def performAutocheck(self):
    #    # Perform auto check
    #    self.autocheck.set_callbacks(lambda: wx.CallAfter(self.beforeAutocheck),
    #                                 None, lambda r: wx.CallAfter(self.afterAutocheck, r))
    #    self.autocheck.start()

    # def beforeAutocheck(self):
    #    self.sections['scanner_autocheck'].items['autocheck_button'].Disable()
    #    if self.buttonStartCallback is not None:
    #        self.buttonStartCallback()
    #    self.waitCursor = wx.BusyCursor()

    def afterAutocheck(self, result):
        self.sections['scanner_autocheck'].items['autocheck_button'].Enable()
        if isinstance(result, PatternNotDetected):
            dlg = wx.MessageDialog(
                self, _("Please, put the pattern on the platform"),
                _(result), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        elif isinstance(result, WrongMotorDirection):
            dlg = wx.MessageDialog(
                self, _('Please, go to "Prefecences" and select "Invert the motor direction"'),
                _(result), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        elif isinstance(result, LaserNotDetected):
            dlg = wx.MessageDialog(
                self, _("Please, check the lasers connection"),
                _(result), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        elif result is not None:
            dlg = wx.MessageDialog(
                self, _(result), _("Exception"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(
                self, _("Autocheck executed correctly"),
                _("Success!"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        if self.buttonStopCallback is not None:
            self.buttonStopCallback()
        if hasattr(self, 'waitCursor'):
            del self.waitCursor


# TODO: Use TextBoxArray

class CalibrationPanel(ExpandablePanel):

    def __init__(self, parent, titleText="", buttonStartCallback=None, description=""):
        ExpandablePanel.__init__(
            self, parent, titleText, hasUndo=False, hasRestore=False)

        self.buttonStartCallback = buttonStartCallback
        self.description = description

        self.parametersBox = wx.BoxSizer(wx.VERTICAL)
        self.buttonsPanel = wx.Panel(self.content)

        self.buttonEdit = wx.ToggleButton(self.buttonsPanel, wx.NewId(), label=_("Edit"))
        self.buttonDefault = wx.Button(self.buttonsPanel, wx.NewId(), label=_("Default"))
        self.buttonStart = wx.Button(self.buttonsPanel, wx.NewId(), label=_("Start"))
        self.buttonStart.SetToolTip(wx.ToolTip(description))

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.buttonEdit, 1, wx.RIGHT, 4)
        self.hbox.Add(self.buttonDefault, 1, wx.LEFT | wx.RIGHT, 4)
        self.hbox.Add(self.buttonStart, 1, wx.LEFT, 4)
        self.buttonsPanel.SetSizer(self.hbox)

        self.contentBox.Add(
            self.parametersBox, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, 5)
        self.contentBox.Add(
            self.buttonsPanel, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, 7)

        self.buttonEdit.Bind(wx.EVT_TOGGLEBUTTON, self.onButtonEditPressed)
        self.buttonDefault.Bind(wx.EVT_BUTTON, self.onButtonDefaultPressed)
        self.buttonStart.Bind(wx.EVT_BUTTON, self.onButtonStartPressed)

        self.Layout()

    def onButtonEditPressed(self, event):
        pass

    def onButtonDefaultPressed(self, event):
        pass

    def onButtonStartPressed(self, event):
        if self.buttonStartCallback is not None:
            self.buttonStartCallback()


class CameraIntrinsicsPanel(CalibrationPanel):

    def __init__(self, parent, buttonStartCallback):
        CalibrationPanel.__init__(
            self, parent,
            titleText=_("Camera intrinsics"), buttonStartCallback=buttonStartCallback,
            description=_("This calibration acquires the camera intrinsic parameters "
                          "(focal lenghts and optical centers) and the lens distortion"))

        cameraPanel = wx.Panel(self.content)
        distortionPanel = wx.Panel(self.content)

        cameraText = wx.StaticText(self.content, label=_("Camera matrix"))
        cameraText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.cameraTexts = [[0.0 for j in range(3)] for i in range(3)]
        self.cameraValues = np.zeros((3, 3))

        cameraBox = wx.BoxSizer(wx.VERTICAL)
        cameraPanel.SetSizer(cameraBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            for j in range(3):
                self.cameraTexts[i][j] = wx.TextCtrl(cameraPanel, wx.ID_ANY, "")
                self.cameraTexts[i][j].SetEditable(False)
                self.cameraTexts[i][j].Disable()
                ibox.Add(self.cameraTexts[i][j], 1, wx.ALL, 2)
            cameraBox.Add(ibox, 0, wx.ALL | wx.EXPAND, 2)

        distortionText = wx.StaticText(self.content, label=_("Distortion vector"))
        distortionText.SetFont(
            (wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.distortionTexts = [0] * 5
        self.distortionValues = np.zeros(5)

        distortionBox = wx.BoxSizer(wx.HORIZONTAL)
        distortionPanel.SetSizer(distortionBox)
        for i in range(5):
            self.distortionTexts[i] = wx.TextCtrl(distortionPanel, wx.ID_ANY, "", size=(20, -1))
            self.distortionTexts[i].SetEditable(False)
            self.distortionTexts[i].Disable()
            distortionBox.Add(self.distortionTexts[i], 1, wx.ALL, 2)

        self.parametersBox.Add(cameraText, 0, wx.ALL | wx.EXPAND, 8)
        self.parametersBox.Add(cameraPanel, 0, wx.ALL | wx.EXPAND, 2)
        self.parametersBox.Add(distortionText, 0, wx.ALL | wx.EXPAND, 8)
        self.parametersBox.Add(distortionPanel, 0, wx.ALL | wx.EXPAND, 4)

        cameraText.SetToolTip(wx.ToolTip(self.description))
        cameraPanel.SetToolTip(wx.ToolTip(self.description))
        distortionText.SetToolTip(wx.ToolTip(self.description))
        distortionPanel.SetToolTip(wx.ToolTip(self.description))

        self.Layout()

    def onButtonEditPressed(self, event):
        enable = self.buttonEdit.GetValue()

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
            self.buttonEdit.SetLabel(_("OK"))
        else:
            self.buttonEdit.SetLabel(_("Edit"))
            self.updateAllControlsToProfile()

    def onButtonDefaultPressed(self, event):
        dlg = wx.MessageDialog(
            self, _("This will reset camera intrinsics profile settings to defaults.\n"
                    "Unless you have saved your current profile, all settings will be lost! "
                    "Do you really want to reset?"),
            _("Camera Intrinsics reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            profile.settings.resetToDefault('camera_matrix')
            profile.settings.resetToDefault('distortion_vector')
            self.updateProfile()

    def getParameters(self):
        return self.cameraValues, self.distortionValues

    def setParameters(self, params):
        self.cameraValues = params[0]
        self.distortionValues = params[1]
        self.updateAllControls()

    def getProfileSettings(self):
        self.cameraValues = profile.settings['camera_matrix']
        self.distortionValues = profile.settings['distortion_vector']

    def putProfileSettings(self):
        profile.settings['camera_matrix'] = self.cameraValues
        profile.settings['distortion_vector'] = self.distortionValues

    def updateAllControls(self):
        for i in range(3):
            for j in range(3):
                self.cameraValues[i][j] = round(self.cameraValues[i][j], 3)
                self.cameraTexts[i][j].SetValue(str(self.cameraValues[i][j]))
        for i in range(5):
            self.distortionValues[i] = round(self.distortionValues[i], 4)
            self.distortionTexts[i].SetValue(str(self.distortionValues[i]))

    def updateEngine(self):
        driver.camera.camera_matrix = self.cameraValues
        driver.camera.distortion_vector = self.distortionValues

    def updateProfile(self):
        self.getProfileSettings()
        self.updateAllControls()
        self.updateEngine()

    def updateAllControlsToProfile(self):
        self.putProfileSettings()
        self.updateEngine()

    # TODO: move
    def getValueFloat(self, value):
        try:
            return float(eval(value.replace(',', '.'), {}, {}))
        except:
            return 0.0


class LaserTriangulationPanel(CalibrationPanel):

    def __init__(self, parent, buttonStartCallback):
        CalibrationPanel.__init__(
            self, parent,
            titleText=_("Laser triangulation"), buttonStartCallback=buttonStartCallback,
            description=_("This calibration determines the lasers' planes "
                          "relative to the ""camera's coordinate system"))

        distanceLeftPanel = wx.Panel(self.content)
        normalLeftPanel = wx.Panel(self.content)
        distanceRightPanel = wx.Panel(self.content)
        normalRightPanel = wx.Panel(self.content)

        laserLeftText = wx.StaticText(self.content, label=_("Left laser plane"))
        laserLeftText.SetFont(
            (wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.distanceLeftValue = 0

        distanceLeftBox = wx.BoxSizer(wx.HORIZONTAL)
        distanceLeftPanel.SetSizer(distanceLeftBox)
        self.distanceLeftText = wx.TextCtrl(distanceLeftPanel, wx.ID_ANY, "")
        self.distanceLeftText.SetEditable(False)
        self.distanceLeftText.Disable()
        distanceLeftBox.Add(self.distanceLeftText, 1, wx.ALL, 4)

        self.normalLeftTexts = [0] * 3
        self.normalLeftValues = np.zeros(3)

        normalLeftBox = wx.BoxSizer(wx.HORIZONTAL)
        normalLeftPanel.SetSizer(normalLeftBox)
        for i in range(3):
            self.normalLeftTexts[i] = wx.TextCtrl(normalLeftPanel, wx.ID_ANY, "")
            self.normalLeftTexts[i].SetEditable(False)
            self.normalLeftTexts[i].Disable()
            normalLeftBox.Add(self.normalLeftTexts[i], 1, wx.ALL, 2)

        laserRightText = wx.StaticText(self.content, label=_("Right laser plane"))
        laserRightText.SetFont(
            (wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.distanceRightValue = 0

        distanceRightBox = wx.BoxSizer(wx.HORIZONTAL)
        distanceRightPanel.SetSizer(distanceRightBox)
        self.distanceRightText = wx.TextCtrl(distanceRightPanel, wx.ID_ANY, "")
        self.distanceRightText.SetMinSize((0, -1))
        self.distanceRightText.SetEditable(False)
        self.distanceRightText.Disable()
        distanceRightBox.Add(self.distanceRightText, 1, wx.ALL, 4)

        self.normalRightTexts = [0] * 3
        self.normalRightValues = np.zeros(3)

        normalRightBox = wx.BoxSizer(wx.HORIZONTAL)
        normalRightPanel.SetSizer(normalRightBox)
        for i in range(3):
            self.normalRightTexts[i] = wx.TextCtrl(normalRightPanel, wx.ID_ANY, "")
            self.normalRightTexts[i].SetEditable(False)
            self.normalRightTexts[i].Disable()
            normalRightBox.Add(self.normalRightTexts[i], 1, wx.ALL, 2)

        self.parametersBox.Add(laserLeftText, 0, wx.ALL | wx.EXPAND, 8)
        self.parametersBox.Add(distanceLeftPanel, 0, wx.ALL | wx.EXPAND, 2)
        self.parametersBox.Add(normalLeftPanel, 0, wx.ALL | wx.EXPAND, 4)
        self.parametersBox.Add(laserRightText, 0, wx.ALL | wx.EXPAND, 8)
        self.parametersBox.Add(distanceRightPanel, 0, wx.ALL | wx.EXPAND, 2)
        self.parametersBox.Add(normalRightPanel, 0, wx.ALL | wx.EXPAND, 4)

        laserLeftText.SetToolTip(wx.ToolTip(self.description))
        distanceLeftPanel.SetToolTip(wx.ToolTip(self.description))
        normalLeftPanel.SetToolTip(wx.ToolTip(self.description))
        laserRightText.SetToolTip(wx.ToolTip(self.description))
        distanceRightPanel.SetToolTip(wx.ToolTip(self.description))
        normalRightPanel.SetToolTip(wx.ToolTip(self.description))

        self.Layout()

    def onButtonEditPressed(self, event):
        enable = self.buttonEdit.GetValue()

        self.distanceLeftText.SetEditable(enable)
        if enable:
            self.distanceLeftText.Enable()
        else:
            self.distanceLeftText.Disable()
            self.distanceLeftValue = self.getValueFloat(self.distanceLeftText.GetValue())

        for i in range(3):
            self.normalLeftTexts[i].SetEditable(enable)
            if enable:
                self.normalLeftTexts[i].Enable()
            else:
                self.normalLeftTexts[i].Disable()
                self.normalLeftValues[i] = self.getValueFloat(self.normalLeftTexts[i].GetValue())

        self.distanceRightText.SetEditable(enable)
        if enable:
            self.distanceRightText.Enable()
        else:
            self.distanceRightText.Disable()
            self.distanceRightValue = self.getValueFloat(self.distanceRightText.GetValue())

        for i in range(3):
            self.normalRightTexts[i].SetEditable(enable)
            if enable:
                self.normalRightTexts[i].Enable()
            else:
                self.normalRightTexts[i].Disable()
                self.normalRightValues[i] = self.getValueFloat(self.normalRightTexts[i].GetValue())

        if enable:
            self.buttonEdit.SetLabel(_("OK"))
        else:
            self.buttonEdit.SetLabel(_("Edit"))
            self.updateAllControlsToProfile()

    def onButtonDefaultPressed(self, event):
        dlg = wx.MessageDialog(
            self, _("This will reset laser triangulation profile settings to defaults.\n"
                    "Unless you have saved your current profile, all settings will be lost! "
                    "Do you really want to reset?"),
            _("Laser Triangulation reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            profile.settings.resetToDefault('distance_left')
            profile.settings.resetToDefault('normal_left')
            profile.settings.resetToDefault('distance_right')
            profile.settings.resetToDefault('normal_right')
            self.updateProfile()

    def getParameters(self):
        return self.distanceLeftValue, self.normalLeftValues, \
            self.distanceLeftValue, self.normalRightValues

    def setParameters(self, params):
        self.distanceLeftValue = params[0]
        self.normalLeftValues = params[1]
        self.distanceRightValue = params[2]
        self.normalRightValues = params[3]
        self.updateAllControls()

    def getProfileSettings(self):
        self.distanceLeftValue = profile.settings['distance_left']
        self.normalLeftValues = profile.settings['normal_left']
        self.distanceRightValue = profile.settings['distance_right']
        self.normalRightValues = profile.settings['normal_right']

    def putProfileSettings(self):
        profile.settings['distance_left'] = self.distanceLeftValue
        profile.settings['normal_left'] = self.normalLeftValues
        profile.settings['distance_right'] = self.distanceRightValue
        profile.settings['normal_right'] = self.normalRightValues

    def updateAllControls(self):
        self.distanceLeftValue = round(self.distanceLeftValue, 6)
        self.distanceLeftText.SetValue(str(self.distanceLeftValue))

        for i in range(3):
            self.normalLeftValues[i] = round(self.normalLeftValues[i], 6)
            self.normalLeftTexts[i].SetValue(str(self.normalLeftValues[i]))

        self.distanceRightValue = round(self.distanceRightValue, 6)
        self.distanceRightText.SetValue(str(self.distanceRightValue))

        for i in range(3):
            self.normalRightValues[i] = round(self.normalRightValues[i], 6)
            self.normalRightTexts[i].SetValue(str(self.normalRightValues[i]))

    def updateEngine(self):
        pass
        # if hasattr(self, 'pcg'):
        #    self.pcg.setLaserTriangulation(self.distanceLeftValue,
        #    self.normalLeftValues, self.distanceRightValue, self.normalRightValues)

    def updateProfile(self):
        self.getProfileSettings()
        self.updateAllControls()
        self.updateEngine()

    def updateAllControlsToProfile(self):
        self.putProfileSettings()
        self.updateEngine()

    # TODO: move
    def getValueFloat(self, value):
        try:
            return float(eval(value.replace(',', '.'), {}, {}))
        except:
            return 0.0


class PlatformExtrinsicsPanel(CalibrationPanel):

    def __init__(self, parent, buttonStartCallback):
        CalibrationPanel.__init__(
            self, parent,
            titleText=_("Platform extrinsics"), buttonStartCallback=buttonStartCallback,
            description=_("This calibration determines the position and orientation of "
                          "the rotating platform relative to the camera's coordinate system"))

        self.pcg = None

        rotationPanel = wx.Panel(self.content)
        translationPanel = wx.Panel(self.content)

        rotationText = wx.StaticText(self.content, label=_("Rotation matrix"))
        rotationText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.rotationTexts = [[0 for j in range(3)] for i in range(3)]
        self.rotationValues = np.zeros((3, 3))

        rotationBox = wx.BoxSizer(wx.VERTICAL)
        rotationPanel.SetSizer(rotationBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            for j in range(3):
                self.rotationTexts[i][j] = wx.TextCtrl(rotationPanel, wx.ID_ANY, "")
                self.rotationTexts[i][j].SetEditable(False)
                self.rotationTexts[i][j].Disable()
                ibox.Add(self.rotationTexts[i][j], 1, wx.ALL, 2)
            rotationBox.Add(ibox, 0, wx.ALL | wx.EXPAND, 2)

        translationText = wx.StaticText(self.content, label=_("Translation vector"))
        translationText.SetFont(
            (wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.translationTexts = [0] * 3
        self.translationValues = np.zeros(3)

        translationBox = wx.BoxSizer(wx.HORIZONTAL)
        translationPanel.SetSizer(translationBox)
        for i in range(3):
            self.translationTexts[i] = wx.TextCtrl(translationPanel, wx.ID_ANY, "")
            self.translationTexts[i].SetEditable(False)
            self.translationTexts[i].Disable()
            translationBox.Add(self.translationTexts[i], 1, wx.ALL, 2)

        self.parametersBox.Add(rotationText, 0, wx.ALL, 8)
        self.parametersBox.Add(rotationPanel, 0, wx.ALL | wx.EXPAND, 2)
        self.parametersBox.Add(translationText, 0, wx.ALL, 8)
        self.parametersBox.Add(translationPanel, 0, wx.ALL | wx.EXPAND, 4)

        rotationText.SetToolTip(wx.ToolTip(self.description))
        rotationPanel.SetToolTip(wx.ToolTip(self.description))
        translationText.SetToolTip(wx.ToolTip(self.description))
        translationPanel.SetToolTip(wx.ToolTip(self.description))

        self.Layout

    def onButtonEditPressed(self, event):
        enable = self.buttonEdit.GetValue()
        for i in range(3):
            for j in range(3):
                self.rotationTexts[i][j].SetEditable(enable)
                if enable:
                    self.rotationTexts[i][j].Enable()
                else:
                    self.rotationTexts[i][j].Disable()
                    self.rotationValues[i][j] = self.getValueFloat(
                        self.rotationTexts[i][j].GetValue())
        for i in range(3):
            self.translationTexts[i].SetEditable(enable)
            if enable:
                self.translationTexts[i].Enable()
            else:
                self.translationTexts[i].Disable()
                self.translationValues[i] = self.getValueFloat(self.translationTexts[i].GetValue())

        if enable:
            self.buttonEdit.SetLabel(_("OK"))
        else:
            self.buttonEdit.SetLabel(_("Edit"))
            self.updateAllControlsToProfile()

    def onButtonDefaultPressed(self, event):
        dlg = wx.MessageDialog(
            self, _("This will reset platform extrinsics profile settings to defaults.\n"
                    "Unless you have saved your current profile, all settings will be lost! "
                    "Do you really want to reset?"),
            _("Platform Extrinsics reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            profile.settings.resetToDefault('rotation_matrix')
            profile.settings.resetToDefault('translation_vector')
            self.updateProfile()

    def getParameters(self):
        return self.rotationValues, self.translationValues

    def setParameters(self, params):
        self.rotationValues = params[0]
        self.translationValues = params[1]
        self.updateAllControls()

    def getProfileSettings(self):
        self.rotationValues = profile.settings['rotation_matrix']
        self.translationValues = profile.settings['translation_vector']

    def putProfileSettings(self):
        profile.settings['rotation_matrix'] = self.rotationValues
        profile.settings['translation_vector'] = self.translationValues

    def updateAllControls(self):
        for i in range(3):
            for j in range(3):
                self.rotationValues[i][j] = round(self.rotationValues[i][j], 6)
                self.rotationTexts[i][j].SetValue(str(self.rotationValues[i][j]))

        for i in range(3):
            self.translationValues[i] = round(self.translationValues[i], 4)
            self.translationTexts[i].SetValue(str(self.translationValues[i]))

    def updateEngine(self):
        pass
        # if hasattr(self, 'pcg'):
        #    self.pcg.setPlatformExtrinsics(self.rotationValues, self.translationValues)

    def updateProfile(self):
        self.getProfileSettings()
        self.updateAllControls()
        self.updateEngine()

    def updateAllControlsToProfile(self):
        self.putProfileSettings()
        self.updateEngine()

    # TODO: move
    def getValueFloat(self, value):
        try:
            return float(eval(value.replace(',', '.'), {}, {}))
        except:
            return 0.0
