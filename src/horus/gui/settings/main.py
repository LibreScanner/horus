#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: September 2014                                                  #
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
from horus.gui.settings.panels import *

from horus.engine.scanner import *
from horus.engine.calibration import *

class SettingsWorkbench(WorkbenchConnection):

	def __init__(self, parent):
		WorkbenchConnection.__init__(self, parent)

		self.playingCalibration = False
		self.playingScanning = False

		self.scanner = Scanner.Instance()
		self.calibration = Calibration.Instance()

		self.load()

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

		self.Bind(wx.EVT_SHOW, self.onShow)

	def load(self):
		#-- Toolbar Configuration
		self.playCalibrationTool = self.toolbar.AddLabelTool(wx.NewId(), _("Play Calibration"), wx.Bitmap(getPathForImage("play_calibration.png")), shortHelp=_("Play Calibration"))
		self.playScanningTool    = self.toolbar.AddLabelTool(wx.NewId(), _("Play Scanning"), wx.Bitmap(getPathForImage("play_scanning.png")), shortHelp=_("Play Scanning"))
		self.stopTool            = self.toolbar.AddLabelTool(wx.NewId(), _("Stop"), wx.Bitmap(getPathForImage("stop.png")), shortHelp=_("Stop"))
		self.undoTool            = self.toolbar.AddLabelTool(wx.NewId(), _("Undo"), wx.Bitmap(getPathForImage("undo.png")), shortHelp=_("Undo"))
		self.toolbar.Realize()

		#-- Disable Toolbar Items
		self.enableLabelTool(self.playCalibrationTool , False)
		self.enableLabelTool(self.playScanningTool    , False)
		self.enableLabelTool(self.stopTool            , False)
		self.enableLabelTool(self.undoTool            , False)

		#-- Bind Toolbar Items
		self.Bind(wx.EVT_TOOL, self.onPlayCalibrationToolClicked , self.playCalibrationTool)
		self.Bind(wx.EVT_TOOL, self.onPlayScanningToolClicked    , self.playScanningTool)
		self.Bind(wx.EVT_TOOL, self.onStopToolClicked            , self.stopTool)
		self.Bind(wx.EVT_TOOL, self.onUndoToolClicked            , self.undoTool)

		self.scrollPanel = wx.lib.scrolledpanel.ScrolledPanel(self._panel, size=(290,-1))
		self.scrollPanel.SetAutoLayout(1)
		self.scrollPanel.SetupScrolling(scroll_x=False)
		self.calibrationPanel = CalibrationPanel(self.scrollPanel)
		self.scanningPanel = ScanningPanel(self.scrollPanel)
		self.calibrationPanel.Disable()
		self.scanningPanel.Disable()

		self.videoView = ImageView(self._panel)
		self.videoView.SetBackgroundColour(wx.BLACK)

		#-- Layout
		vsbox = wx.BoxSizer(wx.VERTICAL)
		vsbox.Add(self.calibrationPanel, 0, wx.ALL|wx.EXPAND, 2)
		vsbox.Add(self.scanningPanel, 0, wx.ALL|wx.EXPAND, 2)
		self.scrollPanel.SetSizer(vsbox)
		vsbox.Fit(self.scrollPanel)

		self.addToPanel(self.scrollPanel, 0)
		self.addToPanel(self.videoView, 1)

		#-- Undo
		self.undoEvents = {self.calibrationPanel.brightnessSlider.GetId() : self.calibrationPanel.onBrightnessChanged,
						   self.calibrationPanel.contrastSlider.GetId()   : self.calibrationPanel.onContrastChanged,
						   self.calibrationPanel.saturationSlider.GetId() : self.calibrationPanel.onSaturationChanged,
						   self.calibrationPanel.exposureSlider.GetId()   : self.calibrationPanel.onExposureChanged,
						   self.scanningPanel.brightnessSlider.GetId() : self.scanningPanel.onBrightnessChanged,
						   self.scanningPanel.contrastSlider.GetId()   : self.scanningPanel.onContrastChanged,
						   self.scanningPanel.saturationSlider.GetId() : self.scanningPanel.onSaturationChanged,
						   self.scanningPanel.exposureSlider.GetId()   : self.scanningPanel.onExposureChanged,
						   self.scanningPanel.openSlider.GetId()       : self.scanningPanel.onOpenChanged,
						   self.scanningPanel.thresholdSlider.GetId()  : self.scanningPanel.onThresholdChanged,
						   self.scanningPanel.minRadiousSlider.GetId() : self.scanningPanel.onRadiousChanged,
						   self.scanningPanel.maxRadiousSlider.GetId() : self.scanningPanel.onRadiousChanged,
						   self.scanningPanel.minHeightSlider.GetId()  : self.scanningPanel.onHeightChanged,
						   self.scanningPanel.maxHeightSlider.GetId()  : self.scanningPanel.onHeightChanged}

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
		self.timer.Stop()
		frame = self.scanner.camera.captureImage(flush=False)
		if frame is not None:
			if self.playingCalibration:
				retval, frame = self.calibration.detectChessboard(frame)
			self.videoView.setFrame(frame)
		self.timer.Start(milliseconds=1)

	def onPlayCalibrationToolClicked(self, event):
		if self.scanner.camera.fps > 0:
			self.calibrationPanel.Enable()
			self.scanningPanel.Disable()
			self.playingCalibration = True
			self.playingScanning = False
			self.enableLabelTool(self.playCalibrationTool, False)
			self.enableLabelTool(self.playScanningTool, True)
			self.enableLabelTool(self.stopTool, True)
			self.timer.Stop()
			self.calibrationPanel.updateProfileToAllControls()
			self.timer.Start(milliseconds=1)

	def onPlayScanningToolClicked(self, event):
		if self.scanner.camera.fps > 0:
			self.calibrationPanel.Disable()
			self.scanningPanel.Enable()
			self.playingCalibration = False
			self.playingScanning = True
			self.enableLabelTool(self.playCalibrationTool, True)
			self.enableLabelTool(self.playScanningTool, False)
			self.enableLabelTool(self.stopTool, True)
			self.timer.Stop()
			self.scanningPanel.updateProfileToAllControls()
			self.timer.Start(milliseconds=1)

	def onStopToolClicked(self, event):
		self.calibrationPanel.Disable()
		self.scanningPanel.Disable()
		self.playingCalibration = False
		self.playingScanning = False
		self.enableLabelTool(self.playCalibrationTool, True)
		self.enableLabelTool(self.playScanningTool, True)
		self.enableLabelTool(self.stopTool, False)
		self.timer.Stop()
		self.videoView.setDefaultImage()

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
			self.enableLabelTool(self.playCalibrationTool , True)
			self.enableLabelTool(self.playScanningTool    , True)
			self.enableLabelTool(self.stopTool            , False)
		else:
			self.enableLabelTool(self.playCalibrationTool , False)
			self.enableLabelTool(self.playScanningTool    , False)
			self.enableLabelTool(self.stopTool            , False)

	def updateProfileToAllControls(self):
		self.calibrationPanel.updateProfileToAllControls()
		self.scanningPanel.updateProfileToAllControls()