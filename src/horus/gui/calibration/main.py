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

import wx.lib.scrolledpanel

from horus.util.resources import *

from horus.gui.util.imageView import *
from horus.gui.util.workbench import *
from horus.gui.calibration.pages import *
from horus.gui.calibration.panels import *

from horus.engine.scanner import *

class CalibrationWorkbench(WorkbenchConnection):

    def __init__(self, parent):
        WorkbenchConnection.__init__(self, parent)

        self.playing = False

        self.scanner = Scanner.Instance()

        self.load()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

        self.Bind(wx.EVT_SHOW, self.onShow)

    def load(self):
        #-- Toolbar Configuration
        self.playTool = self.toolbar.AddLabelTool(wx.NewId(), _("Play"), wx.Bitmap(getPathForImage("play.png")), shortHelp=_("Play"))
        self.stopTool = self.toolbar.AddLabelTool(wx.NewId(), _("Stop"), wx.Bitmap(getPathForImage("stop.png")), shortHelp=_("Stop"))
        self.undoTool = self.toolbar.AddLabelTool(wx.NewId(), _("Undo"), wx.Bitmap(getPathForImage("undo.png")), shortHelp=_("Undo"))
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

        self.videoView = ImageView(self._panel)
        self.videoView.SetBackgroundColour(wx.BLACK)

        #-- Add Calibration Workbench Panels
        self.cameraIntrinsicsPanel = CalibrationWorkbenchPanel(self.scrollPanel,
                                                               titleText=_("Camera Intrinsics"),
                                                               parametersType=CameraIntrinsicsParameters,
                                                               buttonStartCallback=self.onCameraIntrinsicsStartCallback,
                                                               description=_("Determines the camera matrix and the distortion coefficients using Zhang2000 algorithm and pinhole camera model."))

        self.laserTriangulationPanel = CalibrationWorkbenchPanel(self.scrollPanel,
                                                                 titleText=_("Laser Triangulation"),
                                                                 parametersType=LaserTriangulationParameters,
                                                                 buttonStartCallback=self.onLaserTriangulationStartCallback,
                                                                 description=_("Determines the depth of the intersection camera-laser considering the inclination of the lasers."))

        self.platformExtrinsicsPanel = CalibrationWorkbenchPanel(self.scrollPanel,
                                                                 titleText=_("Platform Extrinsics"),
                                                                 parametersType=PlatformExtrinsicsParameters,
                                                                 buttonStartCallback=self.onPlatformExtrinsicsStartCallback,
                                                                 description=_("Determines the transformation matrix between the camera and the platform using a circular interpolation method."))

        #-- Add CalibrationPages
        self.cameraIntrinsicsMainPage = CameraIntrinsicsMainPage(self._panel,
                                                                 buttonCancelCallback=self.onCancelCallback,
                                                                 buttonPerformCallback=self.onCameraIntrinsicsPerformCallback)

        self.cameraIntrinsicsResultPage = CameraIntrinsicsResultPage(self._panel,
                                                                     buttonRejectCallback=self.onCancelCallback,
                                                                     buttonAcceptCallback=self.onCameraIntrinsicsAcceptCallback)

        self.laserTriangulationMainPage = LaserTriangulationMainPage(self._panel,
                                                                     buttonCancelCallback=self.onCancelCallback,
                                                                     buttonPerformCallback=self.onLaserTriangulationPerformCallback)

        self.laserTriangulationResultPage = LaserTriangulationResultPage(self._panel,
                                                                         buttonRejectCallback=self.onCancelCallback,
                                                                         buttonAcceptCallback=self.onLaserTriangulationAcceptCallback)

        self.platformExtrinsicsMainPage = PlatformExtrinsicsMainPage(self._panel,
                                                                     buttonCancelCallback=self.onCancelCallback,
                                                                     buttonPerformCallback=self.onPlatformExtrinsicsPerformCallback)

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
        vsbox.Add(self.cameraIntrinsicsPanel, 1, wx.ALL|wx.EXPAND, 2)
        vsbox.Add(self.laserTriangulationPanel, 1, wx.ALL|wx.EXPAND, 2)
        vsbox.Add(self.platformExtrinsicsPanel, 1, wx.ALL|wx.EXPAND, 2)
        self.scrollPanel.SetSizer(vsbox)

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
        pass
        #self.cameraPanel.initialize()
        #self.devicePanel.initialize()

    def onShow(self, event):
        if event.GetShow():
            self.updateStatus(self.scanner.isConnected)
        else:
            try:
                self.onStopToolClicked(None)
            except:
                pass

    def onTimer(self, event):
        self.timer.Stop()
        frame = self.scanner.camera.captureImage()
        if frame is not None:
            self.videoView.setFrame(frame)
        self.timer.Start(milliseconds=1)

    def onPlayToolClicked(self, event):
        if self.scanner.camera.fps > 0:
            self.playing = True
            self.enableLabelTool(self.playTool, False)
            self.enableLabelTool(self.stopTool, True)
            self.timer.Stop()
            self.timer.Start(milliseconds=1)

    def onStopToolClicked(self, event):
        self.playing = False
        self.enableLabelTool(self.playTool, True)
        self.enableLabelTool(self.stopTool, False)
        self.timer.Stop()
        self.videoView.setDefaultImage()

    def onSnapshotToolClicked(self, event):
        frame = self.scanner.camera.captureImage()
        if frame is not None:
            self.videoView.setFrame(frame)

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
        self.cameraIntrinsicsMainPage.videoManagement(status)
        if status:
            self.enableLabelTool(self.playTool, True)
            self.enableLabelTool(self.stopTool, False)
            self.cameraIntrinsicsPanel.buttonStart.Enable()
            self.laserTriangulationPanel.buttonStart.Enable()
            self.platformExtrinsicsPanel.buttonStart.Enable()
        else:
            self.enableLabelTool(self.playTool, False)
            self.enableLabelTool(self.stopTool, False)
            self.cameraIntrinsicsPanel.buttonStart.Disable()
            self.laserTriangulationPanel.buttonStart.Disable()
            self.platformExtrinsicsPanel.buttonStart.Disable()

    def onCameraIntrinsicsStartCallback(self):
        self.scrollPanel.Hide()
        self.videoView.Hide()
        self.cameraIntrinsicsPanel.Hide()
        self.laserTriangulationPanel.Hide()
        self.platformExtrinsicsPanel.Hide()
        self.cameraIntrinsicsMainPage.Show()
        self.cameraIntrinsicsMainPage.videoView.SetFocus()
        self.Layout()

    def onLaserTriangulationStartCallback(self):
        self.scrollPanel.Hide()
        self.videoView.Hide()
        self.cameraIntrinsicsPanel.Hide()
        self.laserTriangulationPanel.Hide()
        self.platformExtrinsicsPanel.Hide()
        self.laserTriangulationMainPage.Show()
        self.Layout()

    def onPlatformExtrinsicsStartCallback(self):
        self.scrollPanel.Hide()
        self.videoView.Hide()
        self.cameraIntrinsicsPanel.Hide()
        self.laserTriangulationPanel.Hide()
        self.platformExtrinsicsPanel.Hide()
        self.platformExtrinsicsMainPage.Show()
        self.Layout()

    def onCancelCallback(self):
        self.scrollPanel.Show()
        self.videoView.Show()
        self.cameraIntrinsicsPanel.Show()
        self.laserTriangulationPanel.Show()
        self.platformExtrinsicsPanel.Show()
        self.cameraIntrinsicsMainPage.Hide()
        self.cameraIntrinsicsResultPage.Hide()
        self.laserTriangulationMainPage.Hide()
        self.laserTriangulationResultPage.Hide()
        self.platformExtrinsicsMainPage.Hide()
        self.platformExtrinsicsResultPage.Hide()
        self.Layout()

    def onCameraIntrinsicsPerformCallback(self):
        self.cameraIntrinsicsMainPage.Hide()
        self.cameraIntrinsicsResultPage.Show()
        self.Layout()

    def onCameraIntrinsicsAcceptCallback(self):
        params = self.cameraIntrinsicsResultPage.cameraIntrinsicsParameters.getParameters()
        self.cameraIntrinsicsPanel.parameters.updateAllControlsToProfile(params)

        self.scrollPanel.Show()
        self.videoView.Show()
        self.cameraIntrinsicsPanel.Show()
        self.laserTriangulationPanel.Show()
        self.platformExtrinsicsPanel.Show()
        self.cameraIntrinsicsResultPage.Hide()
        self.Layout()

    def onLaserTriangulationPerformCallback(self):
        self.laserTriangulationMainPage.Hide()
        self.laserTriangulationResultPage.Show()
        self.Layout()

    def onLaserTriangulationAcceptCallback(self):
        params = self.laserTriangulationResultPage.laserTriangulationParameters.getParameters()
        self.laserTriangulationPanel.parameters.updateAllControlsToProfile(params)

        self.scrollPanel.Show()
        self.videoView.Show()
        self.cameraIntrinsicsPanel.Show()
        self.laserTriangulationPanel.Show()
        self.platformExtrinsicsPanel.Show()
        self.laserTriangulationResultPage.Hide()
        self.Layout()

    def onPlatformExtrinsicsPerformCallback(self):
        self.platformExtrinsicsMainPage.Hide()
        self.platformExtrinsicsResultPage.Show()
        self.Layout()

    def onPlatformExtrinsicsAcceptCallback(self):
        params = self.platformExtrinsicsResultPage.platformExtrinsicsParameters.getParameters()
        self.platformExtrinsicsPanel.parameters.updateAllControlsToProfile(params)

        self.scrollPanel.Show()
        self.videoView.Show()
        self.cameraIntrinsicsPanel.Show()
        self.laserTriangulationPanel.Show()
        self.platformExtrinsicsPanel.Show()
        self.platformExtrinsicsResultPage.Hide()
        self.Layout()

    def updateProfileToAllControls(self):
        self.cameraIntrinsicsPanel.parameters.updateProfileToAllControls()
        self.laserTriangulationPanel.parameters.updateProfileToAllControls()
        self.platformExtrinsicsPanel.parameters.updateProfileToAllControls()