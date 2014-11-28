#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: August & November 2014                                          #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>   	                #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 2 of the License, or     #
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
__license__ = "GNU General Public License v2 http://www.gnu.org/licenses/gpl.html"

import wx.lib.scrolledpanel

from horus.util import resources

from horus.gui.util.imageView import VideoView
from horus.gui.util.customPanels import ExpandableControl

from horus.gui.workbench.workbench import WorkbenchConnection
from horus.gui.workbench.calibration.panels import CameraSettingsPanel, CameraIntrinsicsPanel, \
                                                   SimpleLaserTriangulationPanel, PlatformExtrinsicsPanel
from horus.gui.workbench.calibration.pages import CameraIntrinsicsMainPage, CameraIntrinsicsResultPage, \
                                                  SimpleLaserTriangulationMainPage, SimpleLaserTriangulationResultPage, \
                                                  PlatformExtrinsicsMainPage, PlatformExtrinsicsResultPage

from horus.engine.driver import Driver
from horus.engine.calibration import CameraIntrinsics

class CalibrationWorkbench(WorkbenchConnection):

    def __init__(self, parent):
        WorkbenchConnection.__init__(self, parent)

        self.calibrating = False

        self.load()

        self.Bind(wx.EVT_SHOW, self.onShow)

    def load(self):
        #-- Toolbar Configuration
        self.toolbar.Realize()

        self.scrollPanel = wx.lib.scrolledpanel.ScrolledPanel(self._panel, size=(290,-1))
        self.scrollPanel.SetupScrolling(scroll_x=False, scrollIntoView=False)
        self.scrollPanel.SetAutoLayout(1)

        self.controls = ExpandableControl(self.scrollPanel)

        self.videoView = VideoView(self._panel, self.getFrame, 5)
        self.videoView.SetBackgroundColour(wx.BLACK)

        #-- Add Scroll Panels
        self.controls.addPanel('camera_settings', CameraSettingsPanel(self.controls))
        self.controls.addPanel('camera_intrinsics_panel', CameraIntrinsicsPanel(self.controls, buttonStartCallback=self.onCameraIntrinsicsStartCallback))
        self.controls.addPanel('laser_triangulation_panel', SimpleLaserTriangulationPanel(self.controls, buttonStartCallback=self.onLaserTriangulationStartCallback))
        self.controls.addPanel('platform_extrinsics_panel', PlatformExtrinsicsPanel(self.controls, buttonStartCallback=self.onPlatformExtrinsicsStartCallback))

        #-- Add Calibration Pages
        self.cameraIntrinsicsMainPage = CameraIntrinsicsMainPage(self._panel,
                                                                 afterCancelCallback=self.onCancelCallback,
                                                                 afterCalibrationCallback=self.onCameraIntrinsicsAfterCalibrationCallback)

        self.cameraIntrinsicsResultPage = CameraIntrinsicsResultPage(self._panel,
                                                                     buttonRejectCallback=self.onCancelCallback,
                                                                     buttonAcceptCallback=self.onCameraIntrinsicsAcceptCallback)

        self.laserTriangulationMainPage = SimpleLaserTriangulationMainPage(self._panel,
                                                                     afterCancelCallback=self.onCancelCallback,
                                                                     afterCalibrationCallback=self.onLaserTriangulationAfterCalibrationCallback)

        self.laserTriangulationResultPage = SimpleLaserTriangulationResultPage(self._panel,
                                                                         buttonRejectCallback=self.onCancelCallback,
                                                                         buttonAcceptCallback=self.onLaserTriangulationAcceptCallback)

        self.platformExtrinsicsMainPage = PlatformExtrinsicsMainPage(self._panel,
                                                                     afterCancelCallback=self.onCancelCallback,
                                                                     afterCalibrationCallback=self.onPlatformExtrinsicsAfterCalibrationCallback)

        self.platformExtrinsicsResultPage = PlatformExtrinsicsResultPage(self._panel,
                                                                         buttonRejectCallback=self.onCancelCallback,
                                                                         buttonAcceptCallback=self.onPlatformExtrinsicsAcceptCallback)

        self.cameraIntrinsicsMainPage.Hide()
        self.cameraIntrinsicsResultPage.Hide()
        self.laserTriangulationMainPage.Hide()
        self.laserTriangulationResultPage.Hide()
        self.platformExtrinsicsMainPage.Hide()
        self.platformExtrinsicsResultPage.Hide()

        #-- Layout
        vsbox = wx.BoxSizer(wx.VERTICAL)
        vsbox.Add(self.controls, 0, wx.ALL|wx.EXPAND, 0)
        self.scrollPanel.SetSizer(vsbox)
        vsbox.Fit(self.scrollPanel)

        self.addToPanel(self.scrollPanel, 0)
        self.addToPanel(self.videoView, 1)

        self.addToPanel(self.cameraIntrinsicsMainPage, 1)
        self.addToPanel(self.cameraIntrinsicsResultPage, 1)
        self.addToPanel(self.laserTriangulationMainPage, 1)
        self.addToPanel(self.laserTriangulationResultPage, 1)
        self.addToPanel(self.platformExtrinsicsMainPage, 1)
        self.addToPanel(self.platformExtrinsicsResultPage, 1)

        self.Layout()

    def initialize(self):
        self.controls.initialize()

    def onShow(self, event):
        if event.GetShow():
            self.updateStatus(self.driver.isConnected)
        else:
            try:
                self.videoView.stop()
            except:
                pass

    def getFrame(self):
        frame = Driver.Instance().camera.captureImage()
        if frame is not None:
            retval, frame = CameraIntrinsics.Instance().detectChessboard(frame)
        return frame

    def updateToolbarStatus(self, status):
        if status:
            if self.IsShown():
                self.videoView.play()
            self.controls.enableContent()
            self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Enable()
            self.controls.panels['laser_triangulation_panel'].buttonsPanel.Enable()
            self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Enable()
        else:
            self.videoView.stop()
            self.controls.disableContent()
            self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Disable()
            self.controls.panels['laser_triangulation_panel'].buttonsPanel.Disable()
            self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Disable()

    def onCameraIntrinsicsStartCallback(self):
        self.calibrating = True
        self.enableLabelTool(self.disconnectTool, False)
        self.controls.setExpandable(False)
        self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Disable()
        self.combo.Disable()
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
        self.videoView.stop()
        self.videoView.Hide()
        self.laserTriangulationMainPage.Show()
        self.Layout()

    def onPlatformExtrinsicsStartCallback(self):
        self.calibrating = True
        self.enableLabelTool(self.disconnectTool, False)
        self.controls.setExpandable(False)
        self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Disable()
        self.combo.Disable()
        self.videoView.stop()
        self.videoView.Hide()
        self.platformExtrinsicsMainPage.Show()
        self.Layout()

    def onCancelCallback(self):
        self.videoView.play()
        self.calibrating = False
        self.enableLabelTool(self.disconnectTool, True)
        self.controls.setExpandable(True)
        self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Enable()
        self.controls.panels['laser_triangulation_panel'].buttonsPanel.Enable()
        self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Enable()
        self.controls.updateProfile()
        self.combo.Enable()
        self.cameraIntrinsicsMainPage.Hide()
        self.cameraIntrinsicsResultPage.Hide()
        self.laserTriangulationMainPage.Hide()
        self.laserTriangulationResultPage.Hide()
        self.platformExtrinsicsMainPage.Hide()
        self.platformExtrinsicsResultPage.Hide()
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
        self.videoView.play()
        self.calibrating = False
        self.enableLabelTool(self.disconnectTool, True)
        self.controls.setExpandable(True)
        self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Enable()
        self.controls.panels['camera_intrinsics_panel'].updateAllControlsToProfile()
        self.combo.Enable()
        self.cameraIntrinsicsResultPage.Hide()
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
        self.videoView.play()
        self.calibrating = False
        self.enableLabelTool(self.disconnectTool, True)
        self.controls.setExpandable(True)
        self.controls.panels['laser_triangulation_panel'].buttonsPanel.Enable()
        self.controls.panels['laser_triangulation_panel'].updateAllControlsToProfile()
        self.combo.Enable()
        self.laserTriangulationResultPage.Hide()
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
        self.videoView.play()
        self.calibrating = False
        self.enableLabelTool(self.disconnectTool, True)
        self.controls.setExpandable(True)
        self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Enable()
        self.controls.panels['platform_extrinsics_panel'].updateAllControlsToProfile()
        self.combo.Enable()
        self.platformExtrinsicsResultPage.Hide()
        self.videoView.Show()
        self.Layout()

    def updateProfileToAllControls(self):
        self.controls.updateProfile()
        self.GetParent().updateCameraProfile('calibration')
        self.Layout()