# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
import time

from horus.gui.util.imageView import ImageView
from horus.gui.util.patternDistanceWindow import PatternDistanceWindow

from horus.gui.wizard.wizardPage import WizardPage

from horus.util import profile, resources

from horus.engine.driver.driver import Driver
from horus.engine.calibration.combo_calibration import ComboCalibration, ComboCalibrationError

from horus.engine.algorithms.image_capture import ImageCapture
from horus.engine.algorithms.image_detection import ImageDetection


class CalibrationPage(WizardPage):

    def __init__(self, parent, buttonPrevCallback=None, buttonNextCallback=None):
        WizardPage.__init__(self, parent,
                            title=_("Calibration"),
                            buttonPrevCallback=buttonPrevCallback,
                            buttonNextCallback=buttonNextCallback)

        self.driver = Driver()
        self.image_capture = ImageCapture()
        self.image_detection = ImageDetection()
        self.combo_calibration = ComboCalibration()

        self.patternLabel = wx.StaticText(self.panel, label=_(
            "Put the pattern on the platform as shown in the picture and press \"Calibrate\""))
        self.patternLabel.Wrap(400)
        self.imageView = ImageView(self.panel)
        self.imageView.setImage(wx.Image(resources.getPathForImage("pattern-position-right.jpg")))
        self.calibrateButton = wx.Button(self.panel, label=_("Calibrate"))
        self.cancelButton = wx.Button(self.panel, label=_("Cancel"))
        self.gauge = wx.Gauge(self.panel, range=100, size=(-1, 30))
        self.resultLabel = wx.StaticText(self.panel, size=(-1, 30))

        self.cancelButton.Disable()
        self.resultLabel.Hide()
        self.skipButton.Enable()
        self.nextButton.Disable()

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.patternLabel, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(self.imageView, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(self.resultLabel, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(self.gauge, 0, wx.ALL | wx.EXPAND, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.cancelButton, 1, wx.ALL | wx.EXPAND, 5)
        hbox.Add(self.calibrateButton, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 2)
        self.panel.SetSizer(vbox)

        self.Layout()

        self.calibrateButton.Bind(wx.EVT_BUTTON, self.onCalibrationButtonClicked)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButtonClicked)
        self.Bind(wx.EVT_SHOW, self.onShow)

        self.videoView.setMilliseconds(10)
        self.videoView.setCallback(self.get_image)

    def onShow(self, event):
        if event.GetShow():
            self.updateStatus(self.driver.is_connected)
        else:
            try:
                self.videoView.stop()
            except:
                pass

    def get_image(self):
        if self.combo_calibration._is_calibrating:
            image = self.combo_calibration.image
        else:
            image = self.image_capture.capture_pattern()
            image = self.image_detection.detect_pattern(image)
        return image

    def onUnplugged(self):
        self.videoView.stop()
        self.combo_calibration.cancel()
        self.enableNext = True

    def onCalibrationButtonClicked(self, event):
        self.combo_calibration.set_callbacks(
            lambda: wx.CallAfter(self.beforeCalibration),
            lambda p: wx.CallAfter(self.progressCalibration, p),
            lambda r: wx.CallAfter(self.afterCalibration, r))
        if profile.settings['pattern_origin_distance'] == 0.0:
            PatternDistanceWindow(self)
        else:
            self.combo_calibration.start()

    def onCancelButtonClicked(self, event):
        boardUnplugCallback = self.driver.board.unplug_callback
        cameraUnplugCallback = self.driver.camera.unplug_callback
        self.driver.board.set_unplug_callback(None)
        self.driver.camera.set_unplug_callback(None)
        self.resultLabel.SetLabel(_("Calibration canceled. To try again press \"Calibrate\""))
        self.combo_calibration.cancel()
        self.skipButton.Enable()
        self.onFinishCalibration()
        self.driver.board.set_unplug_callback(boardUnplugCallback)
        self.driver.camera.set_unplug_callback(cameraUnplugCallback)

    def beforeCalibration(self):
        self.breadcrumbs.Disable()
        self.calibrateButton.Disable()
        self.cancelButton.Enable()
        self.prevButton.Disable()
        self.skipButton.Disable()
        self.nextButton.Disable()
        self.enableNext = False
        self.gauge.SetValue(0)
        self.resultLabel.Hide()
        self.gauge.Show()
        self.Layout()
        self.waitCursor = wx.BusyCursor()

    def progressCalibration(self, progress):
        self.gauge.SetValue(progress)

    def afterCalibration(self, response):
        ret, result = response

        if ret:
            response_platform_extrinsics = result[0]
            response_laser_triangulation = result[1]

            profile.settings['rotation_matrix'] = response_platform_extrinsics[0]
            profile.settings['translation_vector'] = response_platform_extrinsics[1]

            profile.settings['distance_left'] = response_laser_triangulation[0][0]
            profile.settings['normal_left'] = response_laser_triangulation[0][1]
            profile.settings['distance_right'] = response_laser_triangulation[1][0]
            profile.settings['normal_right'] = response_laser_triangulation[1][1]
        else:
            if isinstance(result, ComboCalibrationError):
                self.resultLabel.SetLabel(
                    _("Calibration failed. Please try again"))
                dlg = wx.MessageDialog(
                    self, _("Calibration failed. Please try again"),
                    _(result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.skipButton.Enable()
                self.onFinishCalibration()

        if ret:
            self.skipButton.Disable()
            self.nextButton.Enable()
            self.resultLabel.SetLabel(_("All OK. Please press next to continue"))
        else:
            self.skipButton.Enable()
            self.nextButton.Disable()

        self.onFinishCalibration()

    def onFinishCalibration(self):
        self.breadcrumbs.Enable()
        self.enableNext = True
        self.gauge.Hide()
        self.resultLabel.Show()
        self.calibrateButton.Enable()
        self.cancelButton.Disable()
        self.prevButton.Enable()
        self.panel.Fit()
        self.panel.Layout()
        self.Layout()
        if hasattr(self, 'waitCursor'):
            del self.waitCursor

    def updateStatus(self, status):
        if status:
            if profile.settings['workbench'] != 'Calibration workbench':
                profile.settings['workbench'] = 'Calibration workbench'
                self.GetParent().parent.workbenchUpdate(False)
            self.videoView.play()
            self.calibrateButton.Enable()
            self.skipButton.Enable()
            self.driver.board.lasers_off()
        else:
            self.videoView.stop()
            self.gauge.SetValue(0)
            self.gauge.Show()
            self.prevButton.Enable()
            self.skipButton.Disable()
            self.nextButton.Disable()
            self.calibrateButton.Disable()
            self.cancelButton.Disable()
