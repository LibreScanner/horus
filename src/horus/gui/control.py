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
from horus.gui.util.videoView import *

class ControlWorkbench(Workbench):

	def __init__(self, parent):
		Workbench.__init__(self, parent, 2, 3)

		self.load()

		self.scanner = self.GetParent().scanner

		self.laserLeft = False
		self.laserRight = False

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

		self.Bind(wx.EVT_SHOW, self.onShow)

	def load(self):

		#-- Toolbar Configuration

		self.connectTool       = self.toolbar.AddLabelTool(wx.NewId(), _("Connect"), wx.Bitmap(getPathForImage("connect.png")), shortHelp=_("Connect"))
		self.disconnectTool    = self.toolbar.AddLabelTool(wx.NewId(), _("Disconnect"), wx.Bitmap(getPathForImage("disconnect.png")), shortHelp=_("Disconnect"))
		self.playTool          = self.toolbar.AddLabelTool(wx.NewId(), _("Play"), wx.Bitmap(getPathForImage("play.png")), shortHelp=_("Play"))
		self.stopTool          = self.toolbar.AddLabelTool(wx.NewId(), _("Stop"), wx.Bitmap(getPathForImage("stop.png")), shortHelp=_("Stop"))
		self.snapshotTool      = self.toolbar.AddLabelTool(wx.NewId(), _("Snapshot"), wx.Bitmap(getPathForImage("snapshot.png")), shortHelp=_("Snapshot"))
		self.motorCCWTool      = self.toolbar.AddLabelTool(wx.NewId(), _("Motor CCW"), wx.Bitmap(getPathForImage("motor-ccw.png")), shortHelp=_("Motor CCW"))
		self.motorCWTool       = self.toolbar.AddLabelTool(wx.NewId(), _("Motor CW"), wx.Bitmap(getPathForImage("motor-cw.png")), shortHelp=_("Motor CW"))
		self.leftLaserOnTool   = self.toolbar.AddLabelTool(wx.NewId(), _("Left Laser On"), wx.Bitmap(getPathForImage("laser-left-on.png")), shortHelp=_("Left Laser On"))
		self.leftLaserOffTool  = self.toolbar.AddLabelTool(wx.NewId(), _("Left Laser Off"), wx.Bitmap(getPathForImage("laser-left-off.png")), shortHelp=_("Left Laser Off"))
		self.rightLaserOnTool  = self.toolbar.AddLabelTool(wx.NewId(), _("Right Laser On"), wx.Bitmap(getPathForImage("laser-right-on.png")), shortHelp=_("Right Laser On"))
		self.rightLaserOffTool = self.toolbar.AddLabelTool(wx.NewId(), _("Right Laser Off"), wx.Bitmap(getPathForImage("laser-right-off.png")), shortHelp=_("Right Laser Off"))
		self.toolbar.Realize()

		#-- Disable Toolbar Items

		self.enableLabelTool(self.connectTool      , True)
		self.enableLabelTool(self.disconnectTool   , False)
		self.enableLabelTool(self.playTool         , False)
		self.enableLabelTool(self.stopTool         , False)
		self.enableLabelTool(self.snapshotTool     , False)
		self.enableLabelTool(self.motorCCWTool     , False)
		self.enableLabelTool(self.motorCWTool      , False)
		self.enableLabelTool(self.leftLaserOnTool  , False)
		self.enableLabelTool(self.leftLaserOffTool , False)
		self.enableLabelTool(self.rightLaserOnTool , False)
		self.enableLabelTool(self.rightLaserOffTool, False)

		#-- Bind Toolbar Items

		self.Bind(wx.EVT_TOOL, self.onConnectToolClicked      , self.connectTool)
		self.Bind(wx.EVT_TOOL, self.onDisconnectToolClicked   , self.disconnectTool)
		self.Bind(wx.EVT_TOOL, self.onPlayToolClicked         , self.playTool)
		self.Bind(wx.EVT_TOOL, self.onStopToolClicked         , self.stopTool)
		self.Bind(wx.EVT_TOOL, self.onSnapshotToolClicked     , self.snapshotTool)
		self.Bind(wx.EVT_TOOL, self.onMotorCCWToolClicked     , self.motorCCWTool)
		self.Bind(wx.EVT_TOOL, self.onMotorCWToolClicked      , self.motorCWTool)
		self.Bind(wx.EVT_TOOL, self.onLeftLaserOnToolClicked  , self.leftLaserOnTool)
		self.Bind(wx.EVT_TOOL, self.onLeftLaserOffToolClicked , self.leftLaserOffTool)
		self.Bind(wx.EVT_TOOL, self.onRightLaserOnToolClicked , self.rightLaserOnTool)
		self.Bind(wx.EVT_TOOL, self.onRightLaserOffToolClicked, self.rightLaserOffTool)

		#-- Video View

		self.videoView = VideoView(self._leftPanel)
		self.videoView.SetBackgroundColour(wx.BLACK)
		self.addToLeft(self.videoView)

		#-- Image View

		self.imageView = VideoView(self._rightPanel)
		self.addToRight(self.imageView)

		self.imageView.setImage(wx.Image(getPathForImage("scanner.png")))

	def onTimer(self, event):
		frame = self.scanner.camera.captureImage()
		if frame is not None:
			self.videoView.setFrame(frame)

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
		self.timer.Start(milliseconds=150)

	def onStopToolClicked(self, event):
		self.enableLabelTool(self.playTool, True)
		self.enableLabelTool(self.stopTool, False)
		self.timer.Stop()
		self.videoView.setDefaultImage()

	def onSnapshotToolClicked(self, event):
		frame = self.scanner.camera.captureImage()
		if frame is not None:
			self.videoView.setFrame(frame)

	def onMotorCCWToolClicked(self, event):
		self.scanner.device.enable()
		self.scanner.device.setMotorCCW()
		self.scanner.device.disable()

	def onMotorCWToolClicked(self, event):
		self.scanner.device.enable()
		self.scanner.device.setMotorCW()
		self.scanner.device.disable()

	def onLeftLaserOnToolClicked(self, event):
		self.enableLabelTool(self.leftLaserOnTool , False)
		self.enableLabelTool(self.leftLaserOffTool, True)
		self.scanner.device.setLeftLaserOn()
		self.laserLeft = True
		self.updateScannerImage()

	def onLeftLaserOffToolClicked(self, event):
		self.enableLabelTool(self.leftLaserOnTool , True)
		self.enableLabelTool(self.leftLaserOffTool, False)
		self.scanner.device.setLeftLaserOff()
		self.laserLeft = False
		self.updateScannerImage()

	def onRightLaserOnToolClicked(self, event):
		self.enableLabelTool(self.rightLaserOnTool , False)
		self.enableLabelTool(self.rightLaserOffTool, True)
		self.scanner.device.setRightLaserOn()
		self.laserRight = True
		self.updateScannerImage()

	def onRightLaserOffToolClicked(self, event):
		self.enableLabelTool(self.rightLaserOnTool , True)
		self.enableLabelTool(self.rightLaserOffTool, False)
		self.scanner.device.setRightLaserOff()
		self.laserRight = False
		self.updateScannerImage()

	def enableLabelTool(self, item, enable):
		self.toolbar.EnableTool(item.GetId(), enable)

	def updateScannerImage(self):
		if self.laserLeft:
			if self.laserRight:
				self.imageView.setImage(wx.Image(getPathForImage("scannerlr.png")))
			else:
				self.imageView.setImage(wx.Image(getPathForImage("scannerl.png")))
		else:
			if self.laserRight:
				self.imageView.setImage(wx.Image(getPathForImage("scannerr.png")))
			else:
				self.imageView.setImage(wx.Image(getPathForImage("scanner.png")))

	def updateToolbarStatus(self, status):
		if status:
			self.enableLabelTool(self.connectTool      , False)
			self.enableLabelTool(self.disconnectTool   , True)
			self.enableLabelTool(self.playTool         , True)
			self.enableLabelTool(self.stopTool         , False)
			self.enableLabelTool(self.snapshotTool     , True)
			self.enableLabelTool(self.motorCCWTool     , True)
			self.enableLabelTool(self.motorCWTool      , True)
			self.enableLabelTool(self.leftLaserOnTool  , True)
			self.enableLabelTool(self.leftLaserOffTool , False)
			self.enableLabelTool(self.rightLaserOnTool , True)
			self.enableLabelTool(self.rightLaserOffTool, False)
		else:
			self.enableLabelTool(self.connectTool      , True)
			self.enableLabelTool(self.disconnectTool   , False)
			self.enableLabelTool(self.playTool         , False)
			self.enableLabelTool(self.stopTool         , False)
			self.enableLabelTool(self.snapshotTool     , False)
			self.enableLabelTool(self.motorCCWTool     , False)
			self.enableLabelTool(self.motorCWTool      , False)
			self.enableLabelTool(self.leftLaserOnTool  , False)
			self.enableLabelTool(self.leftLaserOffTool , False)
			self.enableLabelTool(self.rightLaserOnTool , False)
			self.enableLabelTool(self.rightLaserOffTool, False)