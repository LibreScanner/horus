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

from horus.util.resources import *

from horus.gui.util.imageView import *
from horus.gui.util.workbench import *
from horus.gui.control.panels import *

from horus.engine.scanner import *

class ControlWorkbench(WorkbenchConnection):

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
		self.playTool     = self.toolbar.AddLabelTool(wx.NewId(), _("Play"), wx.Bitmap(getPathForImage("play.png")), shortHelp=_("Play"))
		self.stopTool     = self.toolbar.AddLabelTool(wx.NewId(), _("Stop"), wx.Bitmap(getPathForImage("stop.png")), shortHelp=_("Stop"))
		#self.snapshotTool = self.toolbar.AddLabelTool(wx.NewId(), _("Snapshot"), wx.Bitmap(getPathForImage("snapshot.png")), shortHelp=_("Snapshot"))
		self.undoTool     = self.toolbar.AddLabelTool(wx.NewId(), _("Undo"), wx.Bitmap(getPathForImage("undo.png")), shortHelp=_("Undo"))
		self.toolbar.Realize()

		#-- Disable Toolbar Items
		self.enableLabelTool(self.playTool     , False)
		self.enableLabelTool(self.stopTool     , False)
		#self.enableLabelTool(self.snapshotTool , False)
		self.enableLabelTool(self.undoTool     , False)

		#-- Bind Toolbar Items
		self.Bind(wx.EVT_TOOL, self.onPlayToolClicked     , self.playTool)
		self.Bind(wx.EVT_TOOL, self.onStopToolClicked     , self.stopTool)
		#self.Bind(wx.EVT_TOOL, self.onSnapshotToolClicked , self.snapshotTool)
		self.Bind(wx.EVT_TOOL, self.onUndoToolClicked     , self.undoTool)

		self.scrollPanel = wx.lib.scrolledpanel.ScrolledPanel(self._panel, size=(290,-1))
		self.scrollPanel.SetAutoLayout(1)
		self.scrollPanel.SetupScrolling(scroll_x=False)
		self.cameraPanel = CameraPanel(self.scrollPanel)
		self.devicePanel = DevicePanel(self.scrollPanel)
		self.cameraPanel.Disable()
		self.devicePanel.Disable()

		self.videoView = ImageView(self._panel)
		self.videoView.SetBackgroundColour(wx.BLACK)

		#-- Layout
		vsbox = wx.BoxSizer(wx.VERTICAL)
		vsbox.Add(self.cameraPanel, 0, wx.ALL|wx.EXPAND, 2)
		vsbox.Add(self.devicePanel, 0, wx.ALL|wx.EXPAND, 2)
		self.scrollPanel.SetSizer(vsbox)
		vsbox.Fit(self.scrollPanel)

		self.addToPanel(self.scrollPanel, 0)
		self.addToPanel(self.videoView, 1)

		#-- Undo
		self.undoEvents = {self.cameraPanel.brightnessSlider.GetId() : self.cameraPanel.onBrightnessChanged,
						   self.cameraPanel.contrastSlider.GetId()   : self.cameraPanel.onContrastChanged,
						   self.cameraPanel.saturationSlider.GetId() : self.cameraPanel.onSaturationChanged,
						   self.cameraPanel.exposureSlider.GetId()   : self.cameraPanel.onExposureChanged}

		self.storyObjects = []
		self.storyValues = []
		self.flagFirstMove = True # When you drag the slider, the only undoable is the first position not the ones in between

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
			self.videoView.setFrame(frame)

	def onPlayToolClicked(self, event):
		if self.scanner.camera.fps > 0:
			self.playing = True
			self.enableLabelTool(self.playTool, False)
			self.enableLabelTool(self.stopTool, True)
			mseconds = 1000 / (self.scanner.camera.fps)
			if self.cameraPanel.useDistortion:
				mseconds *= 2.0
			self.timer.Stop()
			self.timer.Start(milliseconds=mseconds)
			self.scanner.camera.setUseDistortion(self.cameraPanel.useDistortion)

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

	def appendToUndo(self, _object, _value):
		if self.flagFirstMove:
			self.storyObjects.append(_object)
			self.storyValues.append(_value)
			self.flagFirstMove = False

	def releaseUndo(self, event):
		self.flagFirstMove = True
		self.enableLabelTool(self.undoTool, True)

	def undo(self):
		if len(self.storyObjects) > 0:
			objectToUndo = self.storyObjects.pop()
			valueToUndo = self.storyValues.pop()
			objectToUndo.SetValue(valueToUndo)
			self.updateValue(objectToUndo)
		return len(self.storyObjects) > 0

	def updateValue(self, objectToUndo):
		self.flagFirstMove = False
		self.undoEvents[objectToUndo.GetId()](None)
		self.flagFirstMove = True

	def updateToolbarStatus(self, status):
		if status:
			self.enableLabelTool(self.playTool     , True)
			self.enableLabelTool(self.stopTool     , False)
			#self.enableLabelTool(self.snapshotTool , True)
			self.cameraPanel.Enable()
			self.devicePanel.Enable()
		else:
			self.enableLabelTool(self.playTool     , False)
			self.enableLabelTool(self.stopTool     , False)
			#self.enableLabelTool(self.snapshotTool , False)
			self.cameraPanel.Disable()
			self.devicePanel.Disable()

	def updateProfileToAllControls(self):
		self.cameraPanel.updateProfileToAllControls()
		self.devicePanel.updateProfileToAllControls()