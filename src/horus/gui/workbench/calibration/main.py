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

        self.playing = False
        self.calibrating = False

        self.load()

        self.Bind(wx.EVT_SHOW, self.onShow)

    def load(self):
        #-- Toolbar Configuration
        self.playTool = self.toolbar.AddLabelTool(wx.NewId(), _("Play"), wx.Bitmap(resources.getPathForImage("play.png")), shortHelp=_("Play"))
        self.stopTool = self.toolbar.AddLabelTool(wx.NewId(), _("Stop"), wx.Bitmap(resources.getPathForImage("stop.png")), shortHelp=_("Stop"))
        self.undoTool = self.toolbar.AddLabelTool(wx.NewId(), _("Undo"), wx.Bitmap(resources.getPathForImage("undo.png")), shortHelp=_("Undo"))
        self.toolbar.Realize()

        #-- Disable Toolbar Items
        self.enableLabelTool(self.playTool, False)
        self.enableLabelTool(self.stopTool, False)
        self.enableLabelTool(self.undoTool, False)

        #-- Bind Toolbar Items
        self.Bind(wx.EVT_TOOL, self.onPlayToolClicked, self.playTool)
        self.Bind(wx.EVT_TOOL, self.onStopToolClicked, self.stopTool)
        self.Bind(wx.EVT_TOOL, self.onUndoToolClicked, self.undoTool)

        self.scrollPanel = wx.lib.scrolledpanel.ScrolledPanel(self._panel, size=(290,-1))
        self.scrollPanel.SetupScrolling(scroll_x=False, scrollIntoView=False)
        self.scrollPanel.SetAutoLayout(1)

        self.controls = ExpandableControl(self.scrollPanel)

        self.videoView = VideoView(self._panel, self.getFrame)
        self.videoView.SetBackgroundColour(wx.BLACK)

        #-- Add Scroll Panels
        self.controls.addPanel('camera_settings', CameraSettingsPanel(self.controls))
        self.controls.addPanel('camera_intrinsics_panel', CameraIntrinsicsPanel(self.controls, buttonStartCallback=self.onCameraIntrinsicsStartCallback))
        self.controls.addPanel('laser_triangulation_panel', SimpleLaserTriangulationPanel(self.controls, buttonStartCallback=self.onLaserTriangulationStartCallback))
        self.controls.addPanel('platform_extrinsics_panel', PlatformExtrinsicsPanel(self.controls, buttonStartCallback=self.onPlatformExtrinsicsStartCallback))

        self.controls.setUndoCallbacks(self.appendToUndo, self.releaseUndo)

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

        #-- Undo
        self.undoObjects = []

        self.Layout()

    def initialize(self):
        self.controls.initialize()

    def onShow(self, event):
        if event.GetShow():
            self.updateStatus(Driver.Instance().isConnected)
        else:
            try:
                self.onStopToolClicked(None)
            except:
                pass

    def getFrame(self):
        frame = Driver.Instance().camera.captureImage()
        if frame is not None:
            retval, frame = CameraIntrinsics.Instance().detectChessboard(frame)
        return frame

    def onPlayToolClicked(self, event):
        self.playing = True
        self.enableLabelTool(self.playTool, False)
        self.enableLabelTool(self.stopTool, True)
        self.videoView.play()

    def onStopToolClicked(self, event):
        self.videoView.stop()
        self.playing = False
        self.enableLabelTool(self.playTool, True)
        self.enableLabelTool(self.stopTool, False)

    def onUndoToolClicked(self, event):
        self.enableLabelTool(self.undoTool, self.undo())

    def appendToUndo(self, _object):
        self.undoObjects.append(_object)

    def releaseUndo(self):
        self.enableLabelTool(self.undoTool, True)

    def undo(self):
        if len(self.undoObjects) > 0:
            objectToUndo = self.undoObjects.pop()
            objectToUndo.undo()
        return len(self.undoObjects) > 0

    def updateToolbarStatus(self, status):
        if status:
            self.enableLabelTool(self.playTool, True)
            self.enableLabelTool(self.stopTool, False)
            self.controls.enableContent()
            self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Enable()
            self.controls.panels['laser_triangulation_panel'].buttonsPanel.Enable()
            self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Enable()
        else:
            self.enableLabelTool(self.playTool, False)
            self.enableLabelTool(self.stopTool, False)
            self.controls.disableContent()
            self.controls.panels['camera_intrinsics_panel'].buttonsPanel.Disable()
            self.controls.panels['laser_triangulation_panel'].buttonsPanel.Disable()
            self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Disable()
            self.videoView.stop()

    def onCameraIntrinsicsStartCallback(self):
        self.calibrating = True
        self.enableLabelTool(self.disconnectTool, False)
        self.enableLabelTool(self.playTool, False)
        self.enableLabelTool(self.stopTool, False)
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
        self.enableLabelTool(self.playTool, False)
        self.enableLabelTool(self.stopTool, False)
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
        self.enableLabelTool(self.playTool, False)
        self.enableLabelTool(self.stopTool, False)
        self.controls.setExpandable(False)
        self.controls.panels['platform_extrinsics_panel'].buttonsPanel.Disable()
        self.combo.Disable()
        self.videoView.stop()
        self.videoView.Hide()
        self.platformExtrinsicsMainPage.Show()
        self.Layout()

    def onCancelCallback(self):
        if self.playing:
            self.videoView.play()
            self.enableLabelTool(self.playTool, False)
            self.enableLabelTool(self.stopTool, True)
        else:
            self.enableLabelTool(self.playTool, True)
            self.enableLabelTool(self.stopTool, False)
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
        if self.playing:
            self.videoView.play()
            self.enableLabelTool(self.playTool, False)
            self.enableLabelTool(self.stopTool, True)
        else:
            self.enableLabelTool(self.playTool, True)
            self.enableLabelTool(self.stopTool, False)
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
        if self.playing:
            self.videoView.play()
            self.enableLabelTool(self.playTool, False)
            self.enableLabelTool(self.stopTool, True)
        else:
            self.enableLabelTool(self.playTool, True)
            self.enableLabelTool(self.stopTool, False)
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
        if self.playing:
            self.videoView.play()
            self.enableLabelTool(self.playTool, False)
            self.enableLabelTool(self.stopTool, True)
        else:
            self.enableLabelTool(self.playTool, True)
            self.enableLabelTool(self.stopTool, False)
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
        self.videoView.pause()
        if self.playing:
            self.GetParent().updateCameraProfile('calibration')
            self.videoView.play()
        self.Layout()