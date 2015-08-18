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

import horus.util.error as Error
from horus.util import profile, resources

from horus.engine.driver.driver import Driver
from horus.engine.calibration.laser_triangulation import LaserTriangulation
from horus.engine.calibration.platform_extrinsics import PlatformExtrinsics


class CalibrationPage(WizardPage):

    def __init__(self, parent, buttonPrevCallback=None, buttonNextCallback=None):
        WizardPage.__init__(self, parent,
                            title=_("Calibration"),
                            buttonPrevCallback=buttonPrevCallback,
                            buttonNextCallback=buttonNextCallback)

        self.driver = Driver()
        self.laser_triangulation = LaserTriangulation()
        self.platform_extrinsics = PlatformExtrinsics()
        self.phase = 'none'

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

        self.videoView.setMilliseconds(20)
        self.videoView.setCallback(self.getFrame)

    def onShow(self, event):
        if event.GetShow():
            self.updateStatus(self.driver.is_connected)
        else:
            try:
                self.videoView.stop()
            except:
                pass

    def getFrame(self):
        if self.phase is 'platformCalibration':
            frame = self.platform_extrinsics.image
        elif self.phase is 'laserTriangulation':
            frame = self.laser_triangulation.image
        else:
            frame = self.driver.camera.capture_image()

        if frame is not None and self.phase is not 'laserTriangulation':
            retval, frame = calibration.detect_chessboard(frame)

        return frame

    def onUnplugged(self):
        self.videoView.stop()
        self.laser_triangulation.cancel()
        self.platform_extrinsics.cancel()
        self.enableNext = True

    def onCalibrationButtonClicked(self, event):
        self.phase = 'laserTriangulation'
        self.laser_triangulation.threshold = profile.getProfileSettingFloat(
            'laser_threshold_value')
        self.laser_triangulation.exposure_normal = profile.getProfileSettingNumpy(
            'exposure_texture')
        self.laser_triangulation.exposure_laser = profile.getProfileSettingNumpy(
            'exposure_laser') / 2.
        self.laser_triangulation.set_callbacks(lambda: wx.CallAfter(self.beforeCalibration),
                                               lambda p: wx.CallAfter(
                                                   self.progressLaserCalibration, p),
                                               lambda r: wx.CallAfter(self.afterLaserCalibration, r))
        if profile.getProfileSettingFloat('pattern_origin_distance') == 0:
            PatternDistanceWindow(self)
        else:
            self.laser_triangulation.start()

    def onCancelButtonClicked(self, event):
        boardUnplugCallback = self.driver.board.unplug_callback
        cameraUnplugCallback = self.driver.camera.unplug_callback
        self.driver.board.set_unplug_callback(None)
        self.driver.camera.set_unplug_callback(None)
        self.phase = 'none'
        self.resultLabel.SetLabel(_("Calibration canceled. To try again press \"Calibrate\""))
        self.platform_extrinsics.cancel()
        self.laser_triangulation.cancel()
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

    def progressLaserCalibration(self, progress):
        self.gauge.SetValue(progress * 0.6)

    def afterLaserCalibration(self, response):
        self.phase = 'platformCalibration'
        ret, result = response

        if ret:
            profile.putProfileSetting('distance_left', result[0][0])
            profile.putProfileSettingNumpy('normal_left', result[0][1])
            profile.putProfileSetting('distance_right', result[1][0])
            profile.putProfileSettingNumpy('normal_right', result[1][1])
            self.platform_extrinsics.set_callbacks(None,
                                                   lambda p: wx.CallAfter(
                                                       self.progressPlatformCalibration, p),
                                                   lambda r: wx.CallAfter(self.afterPlatformCalibration, r))
            self.platform_extrinsics.start()
        else:
            if result == Error.CalibrationError:
                self.resultLabel.SetLabel(
                    _("Error in lasers: please connect the lasers and try again"))
                dlg = wx.MessageDialog(
                    self, _("Laser Calibration failed. Please try again"), _(result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.skipButton.Enable()
                self.onFinishCalibration()

    def progressPlatformCalibration(self, progress):
        self.gauge.SetValue(60 + progress * 0.4)

    def afterPlatformCalibration(self, response):
        self.phase = 'none'
        ret, result = response

        if ret:
            profile.putProfileSettingNumpy('rotation_matrix', result[0])
            profile.putProfileSettingNumpy('translation_vector', result[1])
        else:
            if result == Error.CalibrationError:
                self.resultLabel.SetLabel(
                    _("Error in pattern: please check the pattern and try again"))
                dlg = wx.MessageDialog(
                    self, _("Platform Calibration failed. Please try again"), _(result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

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
            if profile.getPreference('workbench') != 'Calibration workbench':
                profile.putPreference('workbench', 'Calibration workbench')
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
