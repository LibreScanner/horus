#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: June 2014                                                       #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>                    #
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


from horus.util.resources import *
from horus.util import profile

from horus.gui.util.cameraPanel import *
from horus.gui.util.videoView import *
from horus.gui.util.devicePanel import *
from horus.gui.util.videoView import *
from horus.gui.util.workbenchConnection import *

class ControlWorkbench(WorkbenchConnection):

	def __init__(self, parent):
		WorkbenchConnection.__init__(self, parent)

		self.viewCamera = True

		#self.undistort = True
		##-- TODO: move undistort to Camera class

		self.playing = False

		self.load()

		self.laserLeft = False
		self.laserRight = False

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

		self.Bind(wx.EVT_SHOW, self.onShow)
		#self.undistortCounter = 0 # The software cannot handle realtime undistort processing, joining threads should be implemented for optimal perfomrance

	def load(self):
		#-- Toolbar Configuration
		self.playTool          = self.toolbar.AddLabelTool(wx.NewId(), _("Play"), wx.Bitmap(getPathForImage("play.png")), shortHelp=_("Play"))
		self.stopTool          = self.toolbar.AddLabelTool(wx.NewId(), _("Stop"), wx.Bitmap(getPathForImage("stop.png")), shortHelp=_("Stop"))
		#self.undistortTool      = self.toolbar.AddCheckTool(id=wx.NewId(),bitmap= wx.Bitmap(getPathForImage("undistort.png")),bmpDisabled=wx.Bitmap(getPathForImage("undistortOff.png")), shortHelp=_("Undistort"))
		self.snapshotTool      = self.toolbar.AddLabelTool(wx.NewId(), _("Snapshot"), wx.Bitmap(getPathForImage("snapshot.png")), shortHelp=_("Snapshot"))
		self.viewTool          = self.toolbar.AddLabelTool(wx.NewId(), _("View"), wx.Bitmap(getPathForImage("view.png")), shortHelp=_("Camera / Device"))
		self.toolbar.Realize()

		#-- Disable Toolbar Items
		self.enableLabelTool(self.playTool     , False)
		self.enableLabelTool(self.stopTool     , False)
		self.enableLabelTool(self.snapshotTool , False)
		#self.enableLabelTool(self.undistortTool, False)
		self.enableLabelTool(self.viewTool     , True)

		#-- Bind Toolbar Items
		self.Bind(wx.EVT_TOOL, self.onPlayToolClicked     , self.playTool)
		self.Bind(wx.EVT_TOOL, self.onStopToolClicked     , self.stopTool)
		self.Bind(wx.EVT_TOOL, self.onSnapshotToolClicked , self.snapshotTool)
		#self.Bind(wx.EVT_TOOL, self.onUndistortToolClicked, self.undistortTool)
		self.Bind(wx.EVT_TOOL, self.onViewToolClicked     , self.viewTool)

		#-- Left Panel
		self.cameraPanel = CameraPanel(self._panel)
		self.devicePanel = DevicePanel(self._panel)

		self.cameraPanel.Disable()
		self.devicePanel.Disable()

		#-- Right Views
		self.cameraView = VideoView(self._panel)
		self.deviceView = VideoView(self._panel)
		self.cameraView.SetBackgroundColour(wx.BLACK)

		self.addToPanel(self.cameraPanel, 0)
		self.addToPanel(self.cameraView, 1)

		self.addToPanel(self.devicePanel, 0)
		self.addToPanel(self.deviceView, 1)

		self.deviceView.setImage(wx.Image(getPathForImage("scanner.png")))

		self.updateView()

	def onShow(self, event):
		if event.GetShow():
			self.updateStatus(self.scanner.isConnected)
		else:
			try:
				self.onStopToolClicked(None)
			except:
				pass

	def onTimer(self, event):
		frame = self.scanner.camera.captureImage()
		if frame is not None:
			self.cameraView.setFrame(frame)

	def onPlayToolClicked(self, event):
		if self.scanner.camera.fps > 0:
			self.enableLabelTool(self.playTool, False)
			self.enableLabelTool(self.stopTool, True)
			mseconds = 1000/(self.scanner.camera.fps)
			self.timer.Start(milliseconds=mseconds)
			self.playing = True

	def onStopToolClicked(self, event):
		self.enableLabelTool(self.playTool, True)
		self.enableLabelTool(self.stopTool, False)
		self.timer.Stop()
		self.playing = False
		self.cameraView.setDefaultImage()

	def onSnapshotToolClicked(self, event):
		frame = self.scanner.camera.captureImage()
		if frame is not None:
			self.cameraView.setFrame(frame)

	#def onUndistortToolClicked(self,event):
		#self.undistort = self.undistortTool.IsToggled()

	def onViewToolClicked(self, event):
		self.viewCamera = not self.viewCamera
		profile.putPreference('view_camera', self.viewCamera)
		self.updateView()

	def updateView(self):
		if self.viewCamera:
			self.cameraPanel.Show()
			self.cameraView.Show()
			self.devicePanel.Hide()
			self.deviceView.Hide()
		else:
			self.cameraPanel.Hide()
			self.cameraView.Hide()
			self.devicePanel.Show()
			self.deviceView.Show()
		self.Layout()

	def updateToolbarStatus(self, status):
		if status:
			self.enableLabelTool(self.playTool     , True)
			self.enableLabelTool(self.stopTool     , False)
			self.enableLabelTool(self.snapshotTool , True)
			self.cameraPanel.Enable()
			self.devicePanel.Enable()
			#self.enableLabelTool(self.undistortTool, True)
			self.laserLeft = False
			self.laserRight = False
		else:
			self.enableLabelTool(self.playTool     , False)
			self.enableLabelTool(self.stopTool     , False)
			self.enableLabelTool(self.snapshotTool , False)
			self.cameraPanel.Disable()
			self.devicePanel.Disable()
			#self.enableLabelTool(self.undistortTool, False)

	def updateProfileToAllControls(self):
		self.cameraPanel.updateProfileToAllControls()
		self.devicePanel.updateProfileToAllControls()
		self.viewCamera = profile.getPreferenceBool('view_camera')
		self.updateView()