# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
import numpy as np

from horus.gui.util.customPanels import ExpandablePanel, Slider, ComboBox, \
    CheckBox, ToggleButton, Button, TextBox
from horus.gui.util.resolutionWindow import ResolutionWindow

from horus.util import profile, system as sys

from horus.engine.driver.driver import Driver
from horus.engine.calibration.pattern import Pattern
from horus.engine.calibration.autocheck import Autocheck, PatternNotDetected, \
                                               WrongMotorDirection, LaserNotDetected

driver = Driver()
pattern = Pattern()


class CameraSettingsPanel(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Camera Settings"))

        self.last_resolution = profile.getProfileSetting('resolution_calibration')

        self.clearSections()
        section = self.createSection('camera_calibration')
        section.addItem(Slider, 'brightness_calibration', tooltip=_(
            'Image luminosity. Low values are better for environments with high ambient light conditions. High values are recommended for poorly lit places'))
        section.addItem(Slider, 'contrast_calibration', tooltip=_(
            'Relative difference in intensity between an image point and its surroundings. Low values are recommended for black or very dark colored objects. High values are better for very light colored objects'))
        section.addItem(Slider, 'saturation_calibration', tooltip=_(
            'Purity of color. Low values will cause colors to disappear from the image. High values will show an image with very intense colors'))
        section.addItem(Slider, 'exposure_calibration', tooltip=_(
            'Amount of light per unit area. It is controlled by the time the camera sensor is exposed during a frame capture. High values are recommended for poorly lit places'))
        section.addItem(ComboBox, 'framerate_calibration', tooltip=_(
            'Number of frames captured by the camera every second. Maximum frame rate is recommended'))
        section.addItem(ComboBox, 'resolution_calibration', tooltip=_(
            'Size of the video. Maximum resolution is recommended'))
        section.addItem(CheckBox, 'use_distortion_calibration', tooltip=_(
            "This option applies lens distortion correction to the video. This process slows the video feed from the camera"))

        if sys.isDarwin():
            section = self.sections['camera_calibration'].disable('framerate_calibration')
            section = self.sections['camera_calibration'].disable('resolution_calibration')

    def updateCallbacks(self):
        section = self.sections['camera_calibration']
        section.updateCallback('brightness_calibration', driver.camera.set_brightness)
        section.updateCallback('contrast_calibration', driver.camera.set_contrast)
        section.updateCallback('saturation_calibration', driver.camera.set_saturation)
        section.updateCallback('exposure_calibration', driver.camera.set_exposure)
        section.updateCallback(
            'framerate_calibration', lambda v: driver.camera.set_frame_rate(int(v)))
        section.updateCallback('resolution_calibration', lambda v: self.setResolution(v))
        section.updateCallback(
            'use_distortion_calibration', lambda v: driver.camera.set_use_distortion(v))

    def setResolution(self, value):
        if value != self.last_resolution:
            ResolutionWindow(self)
        driver.camera.set_resolution(int(value.split('x')[0]), int(value.split('x')[1]))
        self.last_resolution = profile.getProfileSetting('resolution_calibration')


class PatternSettingsPanel(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Pattern Settings"), hasUndo=False)

        self.clearSections()
        section = self.createSection('pattern_settings')
        section.addItem(TextBox, 'pattern_square_width')
        section.addItem(TextBox, 'pattern_rows', tooltip=_('Number of corner rows in the pattern'))
        section.addItem(TextBox, 'pattern_columns', tooltip=_(
            'Number of corner columns in the pattern'))
        section.addItem(TextBox, 'pattern_distance', tooltip=_(
            "Minimum distance between the origin of the pattern (bottom-left corner) and the pattern's base surface"))

    def updateCallbacks(self):
        section = self.sections['pattern_settings']
        section.updateCallback('pattern_square_width', lambda v: self.updatePatternParameters())
        section.updateCallback('pattern_rows', lambda v: self.updatePatternParameters())
        section.updateCallback('pattern_columns', lambda v: self.updatePatternParameters())
        section.updateCallback('pattern_distance', lambda v: self.updatePatternParameters())

    def updatePatternParameters(self):
        pattern.rows = profile.getProfileSettingInteger('pattern_rows')
        pattern.columns = profile.getProfileSettingInteger('pattern_columns')
        pattern.square_width = profile.getProfileSettingInteger('pattern_square_width')
        pattern.distance = profile.getProfileSettingInteger('pattern_distance')


class AutocheckPanel(ExpandablePanel):

    def __init__(self, parent, buttonStartCallback=None, buttonStopCallback=None):
        ExpandablePanel.__init__(self, parent, _("Autocheck"), hasUndo=False, hasRestore=False)

        self.autocheck = Autocheck()
        self.buttonStartCallback = buttonStartCallback
        self.buttonStopCallback = buttonStopCallback

        self.clearSections()
        section = self.createSection('autocheck')
        section.addItem(Button, 'autocheck_button')

    def updateCallbacks(self):
        section = self.sections['autocheck']
        section.updateCallback('autocheck_button', self.performAutocheck)

    def performAutocheck(self):
        # Perform auto check
        self.autocheck.set_callbacks(lambda: wx.CallAfter(self.beforeAutocheck),
                                     None, lambda r: wx.CallAfter(self.afterAutocheck, r))
        self.autocheck.start()

    def beforeAutocheck(self):
        section = self.sections['autocheck'].items['autocheck_button'].Disable()
        if self.buttonStartCallback is not None:
            self.buttonStartCallback()
        self.waitCursor = wx.BusyCursor()

    def afterAutocheck(self, result):
        section = self.sections['autocheck'].items['autocheck_button'].Enable()
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
                self, _("Please, check the lasers conection"),
                _(result), wx.OK | wx.ICON_ERROR)
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

    def __init__(self, parent, titleText="Workbench", buttonStartCallback=None, description="_(Workbench description)"):
        ExpandablePanel.__init__(self, parent, titleText, hasUndo=False, hasRestore=False)

        self.buttonStartCallback = buttonStartCallback
        self.description = description

        self.parametersBox = wx.BoxSizer(wx.VERTICAL)
        self.buttonsPanel = wx.Panel(self.content)

        self.buttonEdit = wx.ToggleButton(self.buttonsPanel, wx.NewId(), label=_("Edit"))
        self.buttonEdit.SetMinSize((0, -1))
        self.buttonDefault = wx.Button(self.buttonsPanel, wx.NewId(), label=_("Default"))
        self.buttonDefault.SetMinSize((0, -1))
        self.buttonStart = wx.Button(self.buttonsPanel, wx.NewId(), label=_("Start"))
        self.buttonStart.SetMinSize((0, -1))
        self.buttonStart.SetToolTip(wx.ToolTip(description))

        self.contentBox.Add(self.parametersBox, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.buttonEdit, 2, wx.ALL | wx.EXPAND, 3)
        self.hbox.Add(self.buttonDefault, 2, wx.ALL | wx.EXPAND, 3)
        self.hbox.Add(self.buttonStart, 3, wx.ALL | wx.EXPAND, 3)
        self.buttonsPanel.SetSizer(self.hbox)
        self.contentBox.Add(self.buttonsPanel, 0, wx.ALL | wx.EXPAND, 3)

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
        CalibrationPanel.__init__(self, parent, titleText=_("Camera Intrinsics"), buttonStartCallback=buttonStartCallback,
                                  description=_("This calibration acquires the camera intrinsic parameters (focal lenghts and optical centers) and the lens distortion"))

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
                jbox = wx.BoxSizer(wx.VERTICAL)
                self.cameraTexts[i][j] = wx.TextCtrl(cameraPanel, wx.ID_ANY, "")
                self.cameraTexts[i][j].SetMinSize((0, -1))
                self.cameraTexts[i][j].SetEditable(False)
                self.cameraTexts[i][j].Disable()
                jbox.Add(self.cameraTexts[i][j], 1, wx.ALL | wx.EXPAND, 2)
                ibox.Add(jbox, 1, wx.ALL | wx.EXPAND, 2)
            cameraBox.Add(ibox, 1, wx.ALL | wx.EXPAND, 2)

        distortionText = wx.StaticText(self.content, label=_("Distortion vector"))
        distortionText.SetFont(
            (wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.distortionTexts = [0] * 5
        self.distortionValues = np.zeros(5)

        distortionBox = wx.BoxSizer(wx.HORIZONTAL)
        distortionPanel.SetSizer(distortionBox)
        for i in range(5):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.distortionTexts[i] = wx.TextCtrl(distortionPanel, wx.ID_ANY, "")
            self.distortionTexts[i].SetMinSize((0, -1))
            self.distortionTexts[i].SetEditable(False)
            self.distortionTexts[i].Disable()
            ibox.Add(self.distortionTexts[i], 1, wx.ALL | wx.EXPAND, 2)
            distortionBox.Add(ibox, 1, wx.ALL | wx.EXPAND, 2)

        self.parametersBox.Add(cameraText, 0, wx.ALL | wx.EXPAND, 8)
        self.parametersBox.Add(cameraPanel, 0, wx.ALL | wx.EXPAND, 2)
        self.parametersBox.Add(distortionText, 0, wx.ALL | wx.EXPAND, 8)
        self.parametersBox.Add(distortionPanel, 0, wx.ALL | wx.EXPAND, 2)

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

    def onButtonDefaultPressed(self, event):
        dlg = wx.MessageDialog(self, _("This will reset camera intrinsics profile settings to defaults.\nUnless you have saved your current profile, all settings will be lost! Do you really want to reset?"), _(
            "Camera Intrinsics reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            profile.resetProfileSetting('camera_matrix')
            profile.resetProfileSetting('distortion_vector')
            self.updateProfile()

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
        driver.camera.camera_matrix = self.cameraValues
        driver.camera.distortion_values = self.distortionValues

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
        CalibrationPanel.__init__(self, parent, titleText=_("Laser Triangulation"), buttonStartCallback=buttonStartCallback,
                                  description=_("This calibration determines the lasers' planes relative to the camera's coordinate system"))

        distanceLeftPanel = wx.Panel(self.content)
        normalLeftPanel = wx.Panel(self.content)
        distanceRightPanel = wx.Panel(self.content)
        normalRightPanel = wx.Panel(self.content)

        laserLeftText = wx.StaticText(self.content, label=_("Left Laser Plane"))
        laserLeftText.SetFont(
            (wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.distanceLeftValue = 0

        distanceLeftBox = wx.BoxSizer(wx.HORIZONTAL)
        distanceLeftPanel.SetSizer(distanceLeftBox)
        self.distanceLeftText = wx.TextCtrl(distanceLeftPanel, wx.ID_ANY, "")
        self.distanceLeftText.SetMinSize((0, -1))
        self.distanceLeftText.SetEditable(False)
        self.distanceLeftText.Disable()
        distanceLeftBox.Add(self.distanceLeftText, 1, wx.ALL | wx.EXPAND, 4)

        self.normalLeftTexts = [0] * 3
        self.normalLeftValues = np.zeros(3)

        normalLeftBox = wx.BoxSizer(wx.HORIZONTAL)
        normalLeftPanel.SetSizer(normalLeftBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.normalLeftTexts[i] = wx.TextCtrl(normalLeftPanel, wx.ID_ANY, "")
            self.normalLeftTexts[i].SetMinSize((0, -1))
            self.normalLeftTexts[i].SetEditable(False)
            self.normalLeftTexts[i].Disable()
            ibox.Add(self.normalLeftTexts[i], 1, wx.ALL | wx.EXPAND, 2)
            normalLeftBox.Add(ibox, 1, wx.ALL | wx.EXPAND, 2)

        laserRightText = wx.StaticText(self.content, label=_("Right Laser Plane"))
        laserRightText.SetFont(
            (wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.distanceRightValue = 0

        distanceRightBox = wx.BoxSizer(wx.HORIZONTAL)
        distanceRightPanel.SetSizer(distanceRightBox)
        self.distanceRightText = wx.TextCtrl(distanceRightPanel, wx.ID_ANY, "")
        self.distanceRightText.SetMinSize((0, -1))
        self.distanceRightText.SetEditable(False)
        self.distanceRightText.Disable()
        distanceRightBox.Add(self.distanceRightText, 1, wx.ALL | wx.EXPAND, 4)

        self.normalRightTexts = [0] * 3
        self.normalRightValues = np.zeros(3)

        normalRightBox = wx.BoxSizer(wx.HORIZONTAL)
        normalRightPanel.SetSizer(normalRightBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.normalRightTexts[i] = wx.TextCtrl(normalRightPanel, wx.ID_ANY, "")
            self.normalRightTexts[i].SetMinSize((0, -1))
            self.normalRightTexts[i].SetEditable(False)
            self.normalRightTexts[i].Disable()
            ibox.Add(self.normalRightTexts[i], 1, wx.ALL | wx.EXPAND, 2)
            normalRightBox.Add(ibox, 1, wx.ALL | wx.EXPAND, 2)

        self.parametersBox.Add(laserLeftText, 0, wx.ALL | wx.EXPAND, 8)
        self.parametersBox.Add(distanceLeftPanel, 1, wx.ALL | wx.EXPAND, 2)
        self.parametersBox.Add(normalLeftPanel, 0, wx.ALL | wx.EXPAND, 2)
        self.parametersBox.Add(laserRightText, 0, wx.ALL | wx.EXPAND, 8)
        self.parametersBox.Add(distanceRightPanel, 1, wx.ALL | wx.EXPAND, 2)
        self.parametersBox.Add(normalRightPanel, 0, wx.ALL | wx.EXPAND, 2)

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
        dlg = wx.MessageDialog(self, _("This will reset laser triangulation profile settings to defaults.\nUnless you have saved your current profile, all settings will be lost! Do you really want to reset?"), _(
            "Laser Triangulation reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            profile.resetProfileSetting('distance_left')
            profile.resetProfileSetting('normal_left')
            profile.resetProfileSetting('distance_right')
            profile.resetProfileSetting('normal_right')
            self.updateProfile()

    def getParameters(self):
        return self.distanceLeftValue, self.normalLeftValues, self.distanceLeftValue, self.normalRightValues

    def setParameters(self, params):
        self.distanceLeftValue = params[0]
        self.normalLeftValues = params[1]
        self.distanceRightValue = params[2]
        self.normalRightValues = params[3]
        self.updateAllControls()

    def getProfileSettings(self):
        self.distanceLeftValue = profile.getProfileSettingFloat('distance_left')
        self.normalLeftValues = profile.getProfileSettingNumpy('normal_left')
        self.distanceRightValue = profile.getProfileSettingFloat('distance_right')
        self.normalRightValues = profile.getProfileSettingNumpy('normal_right')

    def putProfileSettings(self):
        profile.putProfileSettingNumpy('distance_left', self.distanceLeftValue)
        profile.putProfileSettingNumpy('normal_left', self.normalLeftValues)
        profile.putProfileSettingNumpy('distance_right', self.distanceRightValue)
        profile.putProfileSettingNumpy('normal_right', self.normalRightValues)

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
        #    self.pcg.setLaserTriangulation(self.distanceLeftValue, self.normalLeftValues, self.distanceRightValue, self.normalRightValues)

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
        CalibrationPanel.__init__(self, parent, titleText=_("Platform Extrinsics"), buttonStartCallback=buttonStartCallback,
                                  description=_("This calibration determines the position and orientation of the rotating platform relative to the camera's coordinate system"))

        self.pcg = None

        vbox = wx.BoxSizer(wx.VERTICAL)

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
                jbox = wx.BoxSizer(wx.VERTICAL)
                self.rotationTexts[i][j] = wx.TextCtrl(rotationPanel, wx.ID_ANY, "")
                self.rotationTexts[i][j].SetMinSize((0, -1))
                self.rotationTexts[i][j].SetEditable(False)
                self.rotationTexts[i][j].Disable()
                jbox.Add(self.rotationTexts[i][j], 1, wx.ALL | wx.EXPAND, 2)
                ibox.Add(jbox, 1, wx.ALL | wx.EXPAND, 2)
            rotationBox.Add(ibox, 1, wx.ALL | wx.EXPAND, 2)

        translationText = wx.StaticText(self.content, label=_("Translation vector"))
        translationText.SetFont(
            (wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        self.translationTexts = [0] * 3
        self.translationValues = np.zeros(3)

        translationBox = wx.BoxSizer(wx.HORIZONTAL)
        translationPanel.SetSizer(translationBox)
        for i in range(3):
            ibox = wx.BoxSizer(wx.HORIZONTAL)
            self.translationTexts[i] = wx.TextCtrl(translationPanel, wx.ID_ANY, "")
            self.translationTexts[i].SetMinSize((0, -1))
            self.translationTexts[i].SetEditable(False)
            self.translationTexts[i].Disable()
            ibox.Add(self.translationTexts[i], 1, wx.ALL | wx.EXPAND, 2)
            translationBox.Add(ibox, 1, wx.ALL | wx.EXPAND, 2)

        self.parametersBox.Add(rotationText, 0, wx.ALL | wx.EXPAND, 8)
        self.parametersBox.Add(rotationPanel, 0, wx.ALL | wx.EXPAND, 2)
        self.parametersBox.Add(translationText, 0, wx.ALL | wx.EXPAND, 8)
        self.parametersBox.Add(translationPanel, 0, wx.ALL | wx.EXPAND, 2)

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
        dlg = wx.MessageDialog(self, _("This will reset platform extrinsics profile settings to defaults.\nUnless you have saved your current profile, all settings will be lost! Do you really want to reset?"), _(
            "Platform Extrinsics reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            profile.resetProfileSetting('rotation_matrix')
            profile.resetProfileSetting('translation_vector')
            self.updateProfile()

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
