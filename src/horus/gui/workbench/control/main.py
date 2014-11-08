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

import wx.lib.scrolledpanel

from horus.util import resources

from horus.gui.util.imageView import VideoView

from horus.gui.workbench.workbench import WorkbenchConnection
from horus.gui.workbench.control.panels import CameraPanel, DevicePanel

from horus.engine.driver import Driver

class ControlWorkbench(WorkbenchConnection):

	def __init__(self, parent):
		WorkbenchConnection.__init__(self, parent)

		self.playing = False

		self.driver = Driver.Instance()

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
		self.cameraPanel = CameraPanel(self.scrollPanel)
		self.devicePanel = DevicePanel(self.scrollPanel)
		self.cameraPanel.Disable()
		self.devicePanel.Disable()

		self.videoView = VideoView(self._panel, self.getFrame)
		self.videoView.SetBackgroundColour(wx.BLACK)

		#-- Layout
		vsbox = wx.BoxSizer(wx.VERTICAL)
		vsbox.Add(self.cameraPanel, 0, wx.ALL|wx.EXPAND, 2)
		vsbox.Add(self.devicePanel, 0, wx.ALL|wx.EXPAND, 2)
		self.scrollPanel.SetSizer(vsbox)
		vsbox.Fit(self.scrollPanel)

		self.addToPanel(self.scrollPanel, 0)
		self.addToPanel(self.videoView, 1)

		self.Layout()

		#-- Undo
		self.undoObjects = []

	def initialize(self):
		self.cameraPanel.initialize()
		self.devicePanel.initialize()

	def onShow(self, event):
		if event.GetShow():
			self.updateStatus(self.driver.isConnected)
		else:
			try:
				self.onStopToolClicked(None)
			except:
				pass

	def getFrame(self):
		return self.driver.camera.captureImage()

	def onPlayToolClicked(self, event):
		self.playing = True
		self.enableLabelTool(self.playTool, False)
		self.enableLabelTool(self.stopTool, True)
		self.videoView.play()

	def onStopToolClicked(self, event):
		self.playing = False
		self.enableLabelTool(self.playTool, True)
		self.enableLabelTool(self.stopTool, False)
		self.videoView.stop()

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
			self.cameraPanel.Enable()
			self.devicePanel.Enable()
		else:
			self.enableLabelTool(self.playTool, False)
			self.enableLabelTool(self.stopTool, False)
			self.cameraPanel.Disable()
			self.devicePanel.Disable()
			self.videoView.stop()

	def updateProfileToAllControls(self):
		self.cameraPanel.updateProfileToAllControls()
		self.devicePanel.updateProfileToAllControls()