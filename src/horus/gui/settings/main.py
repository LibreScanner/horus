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

		self.showVideoViews = False

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
		self.scrollPanel.SetupScrolling(scroll_x=False, scrollIntoView=False)
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
		self.undoObjects = []

		#-- Video View Selector
		self.buttonShowVideoViews = wx.BitmapButton(self.videoView, wx.NewId(), wx.Bitmap(getPathForImage("views.png"), wx.BITMAP_TYPE_ANY), (10,10))
		self.buttonRaw  = wx.RadioButton(self.videoView, wx.NewId(), _("Raw"), pos=(10,15+40))
		self.buttonLas  = wx.RadioButton(self.videoView, wx.NewId(), _("Laser"), pos=(10,15+80))
		self.buttonDiff = wx.RadioButton(self.videoView, wx.NewId(), _("Diff"), pos=(10,15+120))
		self.buttonBin  = wx.RadioButton(self.videoView, wx.NewId(), _("Binary"), pos=(10,15+160))
		self.buttonLine = wx.RadioButton(self.videoView, wx.NewId(), _("Line"), pos=(10,15+200))

		self.buttonShowVideoViews.Hide()
		self.buttonRaw.Hide()
		self.buttonLas.Hide()
		self.buttonDiff.Hide()
		self.buttonBin.Hide()
		self.buttonLine.Hide()

		self.buttonRaw.SetForegroundColour(wx.WHITE)
		self.buttonLas.SetForegroundColour(wx.WHITE)
		self.buttonDiff.SetForegroundColour(wx.WHITE)
		self.buttonBin.SetForegroundColour(wx.WHITE)
		self.buttonLine.SetForegroundColour(wx.WHITE)

		self.buttonRaw.SetBackgroundColour(wx.BLACK)
		self.buttonLas.SetBackgroundColour(wx.BLACK)
		self.buttonDiff.SetBackgroundColour(wx.BLACK)
		self.buttonBin.SetBackgroundColour(wx.BLACK)
		self.buttonLine.SetBackgroundColour(wx.BLACK)

		self.Bind(wx.EVT_BUTTON, self.onShowVideoViews, self.buttonShowVideoViews)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSelectVideoView, self.buttonRaw)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSelectVideoView, self.buttonLas)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSelectVideoView, self.buttonDiff)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSelectVideoView, self.buttonBin)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSelectVideoView, self.buttonLine)

	def initialize(self):
		self.calibrationPanel.initialize()
		self.scanningPanel.initialize()
		
	def onShow(self, event):
		if event.GetShow():
			self.updateStatus(self.scanner.isConnected)
		else:
			try:
				self.onStopToolClicked(None)
			except:
				pass

	def onShowVideoViews(self, event):
		self.showVideoViews = not self.showVideoViews
		if self.showVideoViews:
			self.buttonRaw.Show()
			self.buttonLas.Show()
			self.buttonDiff.Show()
			self.buttonBin.Show()
			self.buttonLine.Show()
		else:
			self.buttonRaw.Hide()
			self.buttonLas.Hide()
			self.buttonDiff.Hide()
			self.buttonBin.Hide()
			self.buttonLine.Hide()

	def onTimer(self, event):
		self.timer.Stop()
		if self.playingCalibration:
			frame = self.scanner.camera.captureImage(flush=False)
			if frame is not None:
				retval, frame = self.calibration.detectChessboard(frame)
				self.videoView.setFrame(frame)
		elif self.playingScanning:
			frame = self.scanner.core.getImage()
			if frame is not None:
				self.videoView.setFrame(frame)
		self.timer.Start(milliseconds=1)

	def onPlayCalibrationToolClicked(self, event):
		if self.scanner.camera.fps > 0:
			#self.calibrationPanel.Enable()
			#self.scanningPanel.Disable()
			self.buttonShowVideoViews.Hide()
			self.buttonRaw.Hide()
			self.buttonLas.Hide()
			self.buttonDiff.Hide()
			self.buttonBin.Hide()
			self.buttonLine.Hide()
			self.playingCalibration = True
			self.playingScanning = False
			self.enableLabelTool(self.playCalibrationTool, False)
			self.enableLabelTool(self.playScanningTool, True)
			self.enableLabelTool(self.stopTool, True)
			self.timer.Stop()
			self.scanner.stop()
			self.GetParent().updateCameraProfile('calibration')
			self.calibrationPanel.updateProfileToAllControls()
			self.timer.Start(milliseconds=1)

	def onPlayScanningToolClicked(self, event):
		if self.scanner.camera.fps > 0:
			#self.calibrationPanel.Disable()
			#self.scanningPanel.Enable()
			self.buttonShowVideoViews.Show()
			self.playingCalibration = False
			self.playingScanning = True
			self.enableLabelTool(self.playCalibrationTool, True)
			self.enableLabelTool(self.playScanningTool, False)
			self.enableLabelTool(self.stopTool, True)
			self.timer.Stop()
			self.GetParent().updateCameraProfile('scanning')
			self.scanningPanel.updateProfileToAllControls()
			self.scanner.start()
			self.timer.Start(milliseconds=1)

	def onStopToolClicked(self, event):
		#self.calibrationPanel.Disable()
		#self.scanningPanel.Disable()
		self.buttonShowVideoViews.Hide()
		self.buttonRaw.Hide()
		self.buttonLas.Hide()
		self.buttonDiff.Hide()
		self.buttonBin.Hide()
		self.buttonLine.Hide()
		self.playingCalibration = False
		self.playingScanning = False
		self.enableLabelTool(self.playCalibrationTool, True)
		self.enableLabelTool(self.playScanningTool, True)
		self.enableLabelTool(self.stopTool, False)
		self.timer.Stop()
		self.scanner.stop()
		self.videoView.setDefaultImage()

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

	def onSelectVideoView(self, event):
		selectedView = {self.buttonRaw.GetId()  : 'raw',
						self.buttonLas.GetId()  : 'las',
						self.buttonDiff.GetId() : 'diff',
						self.buttonBin.GetId()  : 'bin',
						self.buttonLine.GetId() : 'line'}.get(event.GetId())
		profile.putProfileSetting('img_type', selectedView)
		self.scanner.core.setImageType(selectedView)

	def updateToolbarStatus(self, status):
		if status:
			self.calibrationPanel.Enable()
			self.scanningPanel.Enable()
			self.enableLabelTool(self.playCalibrationTool , True)
			self.enableLabelTool(self.playScanningTool    , True)
			self.enableLabelTool(self.stopTool            , False)
		else:
			self.calibrationPanel.Disable()
			self.scanningPanel.Disable()
			self.enableLabelTool(self.playCalibrationTool , False)
			self.enableLabelTool(self.playScanningTool    , False)
			self.enableLabelTool(self.stopTool            , False)

	def updateProfileToAllControls(self):
		self.timer.Stop()
		self.scanner.stop()
		self.calibrationPanel.updateProfileToAllControls()
		self.scanningPanel.updateProfileToAllControls()
		if self.playingCalibration:
			self.GetParent().updateCameraProfile('calibration')
			self.calibrationPanel.updateProfileToAllControls()
			self.timer.Start(milliseconds=1)
		elif self.playingScanning:
			self.GetParent().updateCameraProfile('scanning')
			self.scanningPanel.updateProfileToAllControls()
			self.scanner.start()
			self.timer.Start(milliseconds=1)