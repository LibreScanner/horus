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

from horus.engine.camera import *
from horus.engine.device import *

from horus.util.resources import *

from horus.gui.util.workbench import *
from horus.gui.util.videoView import *

class ControlWorkbench(Workbench):

	def __init__(self, parent):
		Workbench.__init__(self, parent, 2, 3)

		self.load()

		self.camera = Camera()

		self.timer = wx.Timer(self)

		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

	def load(self):

		#-- Toolbar Configuration

		connectTool    = self._toolbar.AddLabelTool(wx.ID_ANY, _("Connect"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Connect / Disconnect"))
		playTool       = self._toolbar.AddLabelTool(wx.ID_ANY, _("Play"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Play / Stop"))
		snapshotTool   = self._toolbar.AddLabelTool(wx.ID_ANY, _("Snapshot"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Snapshot"))
		motorCCWTool   = self._toolbar.AddLabelTool(wx.ID_ANY, _("Motor CCW"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Motor CCW"))
		motorCWTool    = self._toolbar.AddLabelTool(wx.ID_ANY, _("Motor CW"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Motor CW"))
		leftLaserTool  = self._toolbar.AddLabelTool(wx.ID_ANY, _("Left Laser On"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Left Laser On / Off"))
		rightLaserTool = self._toolbar.AddLabelTool(wx.ID_ANY, _("Right Laser On"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Right Laser On / Off"))
		self._toolbar.Realize()

		#-- Bind Toolbar Items

		self.Bind(wx.EVT_TOOL, self.onConnectToolEnter, connectTool)
		self.Bind(wx.EVT_TOOL, self.onPlayToolEnter, playTool)
		self.Bind(wx.EVT_TOOL, self.onSnapshotToolEnter, snapshotTool)
		self.Bind(wx.EVT_TOOL, self.onMotorCCWToolEnter, motorCCWTool)
		self.Bind(wx.EVT_TOOL, self.onMotorCWToolEnter, motorCWTool)
		self.Bind(wx.EVT_TOOL, self.onLeftLaserToolEnter, leftLaserTool)
		self.Bind(wx.EVT_TOOL, self.onRightLaserToolEnter, rightLaserTool)

		#-- Video View

		leftSizer = wx.BoxSizer(wx.VERTICAL)
		self._leftPanel.SetSizer(leftSizer)

		self.videoView = VideoView(self._leftPanel)
		self.videoView.SetBackgroundColour(wx.BLACK)
		leftSizer.Add(self.videoView, 1, wx.ALL|wx.EXPAND, 5)

		#-- Image View
		
		rightSizer = wx.BoxSizer(wx.VERTICAL)
		self._rightPanel.SetSizer(rightSizer)

		imageView = VideoView(self._rightPanel)
		rightSizer.Add(imageView, 1, wx.ALL|wx.EXPAND, 5)

		imageView.setImage(wx.Image(getPathForImage("render.png")))

	def onTimer(self, event):
		frame = self.camera.captureImage()
		self.videoView.setFrame(frame)

	def onConnectToolEnter(self, event):
		self.camera.connect()

	def onPlayToolEnter(self, event):
		self.timer.Start(milliseconds = 200)

	def onSnapshotToolEnter(self, event):
		frame = self.camera.captureImage()
		self.videoView.setFrame(frame)

	def onMotorCCWToolEnter(self, event):
		pass

	def onMotorCWToolEnter(self, event):
		pass

	def onLeftLaserToolEnter(self, event):
		pass

	def onRightLaserToolEnter(self, event):
		pass