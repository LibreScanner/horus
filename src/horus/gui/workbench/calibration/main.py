# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx.lib.scrolledpanel

from horus.util import profile

from horus.gui.util.imageView import VideoView
from horus.gui.util.customPanels import ExpandableControl
from horus.gui.util.patternDistanceWindow import PatternDistanceWindow

from horus.gui.workbench.workbench import WorkbenchConnection

from horus.gui.workbench.calibration.panels import PatternSettingsPanel, AutocheckPanel, \
    CameraIntrinsicsPanel, LaserTriangulationPanel, PlatformExtrinsicsPanel

from horus.gui.workbench.calibration.pages import AutocheckMainPage, CameraIntrinsicsMainPage, \
    CameraIntrinsicsResultPage, LaserTriangulationMainPage, LaserTriangulationResultPage, \
    PlatformExtrinsicsMainPage, PlatformExtrinsicsResultPage

from horus.engine.driver.driver import Driver
from horus.engine.calibration.camera_intrinsics import CameraIntrinsics
from horus.engine.algorithms.image_capture import ImageCapture
from horus.engine.algorithms.image_detection import ImageDetection


class CalibrationWorkbench(WorkbenchConnection):

    def __init__(self, parent):
        WorkbenchConnection.__init__(self, parent)

        self.calibrating = False

        self.driver = Driver()
        self.camera_intrinsics = CameraIntrinsics()
        self.image_capture = ImageCapture()
        self.image_detection = ImageDetection()

        self.toolbar.Realize()

        self.scrollPanel = wx.lib.scrolledpanel.ScrolledPanel(self._panel, size=(-1, -1))
        self.scrollPanel.SetupScrolling(scroll_x=False, scrollIntoView=False)
        self.scrollPanel.SetAutoLayout(1)

        self.controls = ExpandableControl(self.scrollPanel)

        self.video_image = None
        self.videoView = VideoView(self._panel, self.get_image, 10)
        self.videoView.SetBackgroundColour(wx.BLACK)

        # Add Scroll Panels
        self.controls.addPanel('pattern_settings', PatternSettingsPanel(self.controls))
        self.controls.addPanel('camera_intrinsics_panel', CameraIntrinsicsPanel(
            self.controls, buttonStartCallback=self.onCameraIntrinsicsStartCallback))
        self.controls.addPanel('autocheck_panel', AutocheckPanel(
            self.controls, buttonStartCallback=self.onAutocheckStartCallback,
            buttonStopCallback=self.onCancelCallback))
        self.controls.addPanel('laser_triangulation_panel', LaserTriangulationPanel(
            self.controls, buttonStartCallback=self.onLaserTriangulationStartCallback))
        self.controls.addPanel('platform_extrinsics_panel', PlatformExtrinsicsPanel(
            self.controls, buttonStartCallback=self.onPlatformExtrinsicsStartCallback))

        # Add Calibration Pages
        self.autocheckMainPage = AutocheckMainPage(
            self._panel,
            afterCancelCallback=self.onCancelCallback,
            afterCalibrationCallback=self.onCancelCallback)

        self.cameraIntrinsicsMainPage = CameraIntrinsicsMainPage(
            self._panel,
            afterCancelCallback=self.onCancelCallback,
            afterCalibrationCallback=self.onCameraIntrinsicsAfterCalibrationCallback)

        self.cameraIntrinsicsResultPage = CameraIntrinsicsResultPage(
            self._panel,
            buttonRejectCallback=self.onCancelCallback,
            buttonAcceptCallback=self.onCameraIntrinsicsAcceptCallback)

        self.laserTriangulationMainPage = LaserTriangulationMainPage(
            self._panel,
            afterCancelCallback=self.onCancelCallback,
            afterCalibrationCallback=self.onLaserTriangulationAfterCalibrationCallback)

        self.laserTriangulationResultPage = LaserTriangulationResultPage(
            self._panel,
            buttonRejectCallback=self.onCancelCallback,
            buttonAcceptCallback=self.onLaserTriangulationAcceptCallback)

        self.platformExtrinsicsMainPage = PlatformExtrinsicsMainPage(
            self._panel,
            afterCancelCallback=self.onCancelCallback,
            afterCalibrationCallback=self.onPlatformExtrinsicsAfterCalibrationCallback)

        self.platformExtrinsicsResultPage = PlatformExtrinsicsResultPage(
            self._panel,
            buttonRejectCallback=self.onCancelCallback,
            buttonAcceptCallback=self.onPlatformExtrinsicsAcceptCallback)

        self.autocheckMainPage.Hide()
        self.cameraIntrinsicsMainPage.Hide()
        self.cameraIntrinsicsResultPage.Hide()
        self.laserTriangulationMainPage.Hide()
        self.laserTriangulationResultPage.Hide()
        self.platformExtrinsicsMainPage.Hide()
        self.platformExtrinsicsResultPage.Hide()

        # Layout
        vsbox = wx.BoxSizer(wx.VERTICAL)
        vsbox.Add(self.controls, 0, wx.ALL | wx.EXPAND, 0)
        self.scrollPanel.SetSizer(vsbox)
        vsbox.Fit(self.scrollPanel)
        panel_size = self.scrollPanel.GetSize()[0] + wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
        self.scrollPanel.SetMinSize((panel_size, -1))

        self.controls.initPanels()

        self.addToPanel(self.scrollPanel, 0)
        self.addToPanel(self.videoView, 1)

        self.addToPanel(self.autocheckMainPage, 1)
        self.addToPanel(self.cameraIntrinsicsMainPage, 1)
        self.addToPanel(self.cameraIntrinsicsResultPage, 1)
        self.addToPanel(self.laserTriangulationMainPage, 1)
        self.addToPanel(self.laserTriangulationResultPage, 1)
        self.addToPanel(self.platformExtrinsicsMainPage, 1)
        self.addToPanel(self.platformExtrinsicsResultPage, 1)

        self.updateCallbacks()
        self.Layout()

    def updateCallbacks(self):
        self.controls.updateCallbacks()

    def get_image(self):
        image = self.image_capture.capture_pattern()
        image = self.image_detection.detect_pattern(image)
        return image

    def enableMenus(self, value):
        main = self.GetParent()
        main.menuFile.Enable(main.menuLaunchWizard.GetId(), value)
        main.menuFile.Enable(main.menuOpenCalibrationProfile.GetId(), value)
        main.menuFile.Enable(main.menuSaveCalibrationProfile.GetId(), value)
        main.menuFile.Enable(main.menuResetCalibrationProfile.GetId(), value)
        main.menuFile.Enable(main.menuOpenScanProfile.GetId(), value)
        main.menuFile.Enable(main.menuSaveScanProfile.GetId(), value)
        main.menuFile.Enable(main.menuResetScanProfile.GetId(), value)
        main.menuFile.Enable(main.menuExit.GetId(), value)
        main.menuEdit.Enable(main.menuPreferences.GetId(), value)
        main.menuHelp.Enable(main.menuWelcome.GetId(), value)
        main.Layout()

    def onAutocheckStartCallback(self):
        self.calibrating = True
        self.enableLabelTool(self.disconnectTool, False)
        self.controls.setExpandable(False)
        # self.controls.panels['autocheck_panel'].buttonsPanel.Disable()
        self.combo.Disable()
        self.enableMenus(False)
        self.videoView.stop()
        self.videoView.Hide()
        self.autocheckMainPage.Show()
        self.Layout()

    def onCameraIntrinsicsStartCallback(self):
        self.calibrating = True
        self.enableLabelTool(self.disconnectTool, False)
        self.controls.setExpandable(False)
        self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Disable()
        self.combo.Disable()
        self.enableMenus(False)
        self.videoView.stop()
        self.videoView.Hide()
        self.cameraIntrinsicsMainPage.Show()
        self.cameraIntrinsicsMainPage.videoView.SetFocus()
        self.Layout()

    def onLaserTriangulationStartCallback(self):
        self.calibrating = True
        self.enableLabelTool(self.disconnectTool, False)
        self.controls.setExpandable(False)
        self.controls.panels['laser_triangulation_panel'].buttonsPanel.Disable()
        self.combo.Disable()
        self.enableMenus(False)
        self.videoView.stop()
        self.videoView.Hide()
        self.laserTriangulationMainPage.Show()
        self.Layout()

    def onPlatformExtrinsicsStartCallback(self):
        if profile.settings['pattern_origin_distance'] == 0:
            PatternDistanceWindow(self)
            self.updateProfileToAllControls()
        else:
            self.calibrating = True
            self.enableLabelTool(self.disconnectTool, False)
            self.controls.setExpandable(False)
            self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Disable()
            self.combo.Disable()
            self.enableMenus(False)
            self.videoView.stop()
            self.videoView.Hide()
            self.platformExtrinsicsMainPage.Show()
            self.Layout()

    def onCancelCallback(self):
        self.calibrating = False
        self.enableLabelTool(self.disconnectTool, True)
        self.controls.setExpandable(True)
        self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Enable()
        self.controls.panels['laser_triangulation_panel'].buttonsPanel.Enable()
        self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Enable()
        self.controls.updateProfile()
        self.combo.Enable()
        self.enableMenus(True)
        self.autocheckMainPage.Hide()
        self.cameraIntrinsicsMainPage.Hide()
        self.cameraIntrinsicsResultPage.Hide()
        self.laserTriangulationMainPage.Hide()
        self.laserTriangulationResultPage.Hide()
        self.platformExtrinsicsMainPage.Hide()
        self.platformExtrinsicsResultPage.Hide()
        self.videoView.play()
        self.videoView.Show()
        self.Layout()

    def onCameraIntrinsicsAfterCalibrationCallback(self, result):
        self.cameraIntrinsicsResultPage.processCalibration(result)
        if result[0]:
            self.cameraIntrinsicsMainPage.Hide()
            self.cameraIntrinsicsResultPage.Show()
        else:
            self.cameraIntrinsicsMainPage.initialize()
        self.Layout()

    def onCameraIntrinsicsAcceptCallback(self):
        self.calibrating = False
        self.enableLabelTool(self.disconnectTool, True)
        self.controls.setExpandable(True)
        self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Enable()
        self.controls.panels['camera_intrinsics_panel'].updateAllControlsToProfile()
        self.camera_intrinsics.accept()
        self.combo.Enable()
        self.enableMenus(True)
        self.cameraIntrinsicsResultPage.Hide()
        self.videoView.play()
        self.videoView.Show()
        self.Layout()

    def onLaserTriangulationAfterCalibrationCallback(self, result):
        self.laserTriangulationResultPage.processCalibration(result)
        if result[0]:
            self.laserTriangulationMainPage.Hide()
            self.laserTriangulationResultPage.Show()
        else:
            self.laserTriangulationMainPage.initialize()
        self.Layout()

    def onLaserTriangulationAcceptCallback(self):
        self.calibrating = False
        self.enableLabelTool(self.disconnectTool, True)
        self.controls.setExpandable(True)
        self.controls.panels['laser_triangulation_panel'].buttonsPanel.Enable()
        self.controls.panels['laser_triangulation_panel'].updateAllControlsToProfile()
        self.combo.Enable()
        self.enableMenus(True)
        self.laserTriangulationResultPage.Hide()
        self.videoView.play()
        self.videoView.Show()
        self.Layout()

    def onPlatformExtrinsicsAfterCalibrationCallback(self, result):
        self.platformExtrinsicsResultPage.processCalibration(result)
        if result[0]:
            self.platformExtrinsicsMainPage.Hide()
            self.platformExtrinsicsResultPage.Show()
        else:
            self.platformExtrinsicsMainPage.initialize()
        self.Layout()

    def onPlatformExtrinsicsAcceptCallback(self):
        self.calibrating = False
        self.enableLabelTool(self.disconnectTool, True)
        self.controls.setExpandable(True)
        self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Enable()
        self.controls.panels['platform_extrinsics_panel'].updateAllControlsToProfile()
        self.combo.Enable()
        self.enableMenus(True)
        self.platformExtrinsicsResultPage.Hide()
        self.videoView.play()
        self.videoView.Show()
        self.Layout()

    def updateToolbarStatus(self, status):
        if status:
            if self.IsShown():
                self.videoView.play()
            self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Enable()
            self.controls.panels['laser_triangulation_panel'].buttonsPanel.Enable()
            self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Enable()
            self.controls.enableContent()
        else:
            self.videoView.stop()
            self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Disable()
            self.controls.panels['laser_triangulation_panel'].buttonsPanel.Disable()
            self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Disable()
            self.controls.disableContent()
            self.calibrating = False
            self.combo.Enable()
            self.controls.setExpandable(True)
            self.autocheckMainPage.Hide()
            self.cameraIntrinsicsMainPage.Hide()
            self.cameraIntrinsicsResultPage.Hide()
            self.laserTriangulationMainPage.Hide()
            self.laserTriangulationResultPage.Hide()
            self.platformExtrinsicsMainPage.Hide()
            self.platformExtrinsicsResultPage.Hide()

    def updateProfileToAllControls(self):
        self.controls.updateProfile()
