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

from horus.gui.util.workbench import *
from horus.gui.util.cameraPanel import *
from horus.gui.util.videoView import *
from horus.gui.util.devicePanel import *
from horus.gui.util.videoView import *
import cv2
class ControlWorkbench(Workbench):

	def __init__(self, parent):
		Workbench.__init__(self, parent, 0, 1)

		self.viewCamera = True

		self.scanner = self.GetParent().scanner
		self.calibration = self.GetParent().calibration
		self.undistort=True
		self.load()

		self.laserLeft = False
		self.laserRight = False

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

		self.Bind(wx.EVT_SHOW, self.onShow)
		self.undistortCounter=0 # The software cannot handle realtime undistort processing, joining threads should be implemented for optimal perfomrance

	def load(self):

		#-- Toolbar Configuration
		self.connectTool       = self.toolbar.AddLabelTool(wx.NewId(), _("Connect"), wx.Bitmap(getPathForImage("connect.png")), shortHelp=_("Connect"))
		self.disconnectTool    = self.toolbar.AddLabelTool(wx.NewId(), _("Disconnect"), wx.Bitmap(getPathForImage("disconnect.png")), shortHelp=_("Disconnect"))
		self.playTool          = self.toolbar.AddLabelTool(wx.NewId(), _("Play"), wx.Bitmap(getPathForImage("play.png")), shortHelp=_("Play"))
		self.stopTool          = self.toolbar.AddLabelTool(wx.NewId(), _("Stop"), wx.Bitmap(getPathForImage("stop.png")), shortHelp=_("Stop"))
		self.undistortTool      = self.toolbar.AddCheckTool(id=wx.NewId(),bitmap= wx.Bitmap(getPathForImage("undistort.png")),bmpDisabled=wx.Bitmap(getPathForImage("undistortOff.png")), shortHelp=_("Undistort"))
		
		self.snapshotTool      = self.toolbar.AddLabelTool(wx.NewId(), _("Snapshot"), wx.Bitmap(getPathForImage("snapshot.png")), shortHelp=_("Snapshot"))
		self.viewTool          = self.toolbar.AddLabelTool(wx.NewId(), _("View"), wx.Bitmap(getPathForImage("view.png")), shortHelp=_("Camera / Device"))
		self.toolbar.Realize()

		#-- Disable Toolbar Items
		self.enableLabelTool(self.connectTool      , True)
		self.enableLabelTool(self.disconnectTool   , False)
		self.enableLabelTool(self.playTool         , False)
		self.enableLabelTool(self.stopTool         , False)
		self.enableLabelTool(self.undistortTool    , False)
		self.enableLabelTool(self.snapshotTool     , False)
		self.enableLabelTool(self.viewTool         , True)

		#-- Bind Toolbar Items
		self.Bind(wx.EVT_TOOL, self.onConnectToolClicked      , self.connectTool)
		self.Bind(wx.EVT_TOOL, self.onDisconnectToolClicked   , self.disconnectTool)
		self.Bind(wx.EVT_TOOL, self.onPlayToolClicked         , self.playTool)
		self.Bind(wx.EVT_TOOL, self.onStopToolClicked         , self.stopTool)
		self.Bind(wx.EVT_TOOL, self.onUndistortToolClicked    , self.undistortTool)
		self.Bind(wx.EVT_TOOL, self.onSnapshotToolClicked     , self.snapshotTool)
		self.Bind(wx.EVT_TOOL, self.onViewToolClicked         , self.viewTool)

		#-- Left Panel
		self.cameraPanel = CameraPanel(self._leftPanel)
		self.devicePanel = DevicePanel(self._leftPanel)

		#-- Right Views
		self.cameraView = VideoView(self._rightPanel)
		self.deviceView = VideoView(self._rightPanel)
		self.cameraView.SetBackgroundColour(wx.BLACK)

		self.addToLeft(self.cameraPanel)
		self.addToRight(self.cameraView)

		self.addToLeft(self.devicePanel)
		self.addToRight(self.deviceView)

		self.deviceView.setImage(wx.Image(getPathForImage("scanner.png")))

		self.updateView()

	def onUndistortToolClicked(self,event):
		if self.undistortTool.IsToggled():
			self.undistort=True
		else:
			self.undistort=False


	def onTimer(self, event):
		
		frame = self.scanner.camera.captureImage()
		if frame is not None:

			if self.undistort:
				if self.undistortCounter==1:
					self.undistortCounter=0
					frame=self.calibration.undistortImage(frame)
					self.cameraView.setFrame(frame)
				else:
					self.undistortCounter+=1
			else:
				self.cameraView.setFrame(frame)

	def onShow(self, event):
		if event.GetShow():
			self.updateToolbarStatus(self.scanner.isConnected)
		else:
			pass
			#self.onStopToolClicked(None)

	def onConnectToolClicked(self, event):
		self.updateToolbarStatus(True)

		self.laserLeft = False
		self.laserRight = False

		self.scanner.connect()

	def onDisconnectToolClicked(self, event):
		self.scanner.disconnect() # Not working camera disconnect :S

		# TODO: Check disconnection
		self.updateToolbarStatus(False)

	def onPlayToolClicked(self, event):
		self.enableLabelTool(self.playTool, False)
		self.enableLabelTool(self.stopTool, True)
		mseconds= 1000/(self.scanner.camera.fps)
		self.timer.Start(milliseconds=mseconds)

	def onStopToolClicked(self, event):
		self.enableLabelTool(self.playTool, True)
		self.enableLabelTool(self.stopTool, False)
		self.timer.Stop()
		self.cameraView.setDefaultImage()

	def onSnapshotToolClicked(self, event):
		frame = self.scanner.camera.captureImage()
		if frame is not None:
			self.cameraView.setFrame(frame)

	def enableLabelTool(self, item, enable):
		self.toolbar.EnableTool(item.GetId(), enable)

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
			self.enableLabelTool(self.connectTool      , False)
			self.enableLabelTool(self.disconnectTool   , True)
			self.enableLabelTool(self.playTool         , True)
			self.enableLabelTool(self.stopTool         , False)
			self.enableLabelTool(self.snapshotTool     , True)
			self.enableLabelTool(self.undistortTool    , True)
			#self.enableLabelTool(self.motorCCWTool     , True)
			#self.enableLabelTool(self.motorCWTool      , True)
			#self.enableLabelTool(self.leftLaserOnTool  , True)
			#self.enableLabelTool(self.leftLaserOffTool , False)
			#self.enableLabelTool(self.rightLaserOnTool , True)
			#self.enableLabelTool(self.rightLaserOffTool, False)
		else:
			self.enableLabelTool(self.connectTool      , True)
			self.enableLabelTool(self.disconnectTool   , False)
			self.enableLabelTool(self.playTool         , False)
			self.enableLabelTool(self.stopTool         , False)
			self.enableLabelTool(self.snapshotTool     , False)
			self.enableLabelTool(self.undistortTool    , False)
			#self.enableLabelTool(self.motorCCWTool     , False)
			#self.enableLabelTool(self.motorCWTool      , False)
			#self.enableLabelTool(self.leftLaserOnTool  , False)
			#self.enableLabelTool(self.leftLaserOffTool , False)
			#self.enableLabelTool(self.rightLaserOnTool , False)
			#self.enableLabelTool(self.rightLaserOffTool, False)

	def updateProfileToAllControls(self):
		self.cameraPanel.updateProfileToAllControls()
		self.devicePanel.updateProfileToAllControls()
		self.viewCamera = profile.getPreferenceBool('view_camera')
		self.updateView()