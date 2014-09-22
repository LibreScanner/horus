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

from horus.util.profile import *
from horus.util.resources import *

from horus.gui.util.imageView import *
from horus.gui.util.sceneView import *
from horus.gui.util.workbench import *

class ScanningWorkbench(WorkbenchConnection):

	def __init__(self, parent):
		WorkbenchConnection.__init__(self, parent)

		self.showVideoViews = False

		self.load()

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

	def load(self):
		#-- Toolbar Configuration
		self.playTool       = self.toolbar.AddLabelTool(wx.NewId(), _("Play"), wx.Bitmap(getPathForImage("play.png")), shortHelp=_("Play"))
		self.stopTool       = self.toolbar.AddLabelTool(wx.NewId(), _("Stop"), wx.Bitmap(getPathForImage("stop.png")), shortHelp=_("Stop"))
		self.pauseTool      = self.toolbar.AddLabelTool(wx.NewId(), _("Pause"), wx.Bitmap(getPathForImage("pause.png")), shortHelp=_("Pause"))
		self.resumeTool     = self.toolbar.AddLabelTool(wx.NewId(), _("Resume"), wx.Bitmap(getPathForImage("resume.png")), shortHelp=_("Resume"))
		self.deleteTool     = self.toolbar.AddLabelTool(wx.NewId(), _("Delete"), wx.Bitmap(getPathForImage("delete.png")), shortHelp=_("Clear"))
		self.toolbar.Realize()

		#-- Bind Toolbar Items
		self.Bind(wx.EVT_TOOL, self.onPlayToolClicked      , self.playTool)
		self.Bind(wx.EVT_TOOL, self.onStopToolClicked      , self.stopTool)
		self.Bind(wx.EVT_TOOL, self.onPauseToolClicked     , self.pauseTool)
		self.Bind(wx.EVT_TOOL, self.onResumeToolClicked    , self.resumeTool)
		self.Bind(wx.EVT_TOOL, self.onDeleteToolClicked    , self.deleteTool)

		self.splitterWindow = wx.SplitterWindow(self._panel)
		self.splitterWindow.SetBackgroundColour(wx.GREEN)

		self.videoView = ImageView(self.splitterWindow)
		self.sceneView = SceneView(self.splitterWindow)
		self.videoView.SetBackgroundColour(wx.BLACK)
		self.sceneView.SetBackgroundColour(wx.BLACK)

		self.splitterWindow.SplitVertically(self.videoView, self.sceneView)
		self.splitterWindow.SetMinimumPaneSize(200)

		#-- Layout
		self.addToPanel(self.splitterWindow, 1)

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

		self.Layout()

	def onShow(self, event):
		if event.GetShow():
			self.updateStatus(self.scanner.isConnected)
			self.timer.Stop()
			self.timer.Start(milliseconds=100)
		else:
			self.timer.Stop()

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

	def onSelectVideoView(self, event):
		selectedView = {self.buttonRaw.GetId()  : 'raw',
						self.buttonLas.GetId()  : 'las',
						self.buttonDiff.GetId() : 'diff',
						self.buttonBin.GetId()  : 'bin',
						self.buttonLine.GetId() : 'line'}.get(event.GetId())

		self.scanner.core.setImageType(selectedView)
		profile.putProfileSetting('img_type', selectedView)

	def onTimer(self, event):
		frame = self.scanner.core.getImage()
		if frame is not None:
			self.videoView.setFrame(frame)

		pointCloud = self.scanner.getPointCloudIncrement()

		if pointCloud is not None:
			if pointCloud[0] is not None and pointCloud[1] is not None:
				if len(pointCloud[0]) > 0:
					self.sceneView.appendPointCloud(pointCloud[0], pointCloud[1])

	def onPlayToolClicked(self, event):
		self.enableLabelTool(self.playTool, False)
		self.enableLabelTool(self.stopTool, True)
		self.enableLabelTool(self.pauseTool , True)
		self.enableLabelTool(self.resumeTool, False)
		
		self.sceneView.createDefaultObject()

		self.scanner.start()

	def onStopToolClicked(self, event):
		self.enableLabelTool(self.playTool, True)
		self.enableLabelTool(self.stopTool, False)
		self.enableLabelTool(self.pauseTool , False)
		self.enableLabelTool(self.resumeTool, False)
		
		self.scanner.stop()

	def onPauseToolClicked(self, event):
		self.enableLabelTool(self.pauseTool , False)
		self.enableLabelTool(self.resumeTool, True)
		
		self.scanner.pause()
		self.timer.Stop()

	def onResumeToolClicked(self, event):
		self.enableLabelTool(self.pauseTool , True)
		self.enableLabelTool(self.resumeTool, False)
		
		self.scanner.resume()
		self.timer.Start(milliseconds=100)

	def onDeleteToolClicked(self, event):
		self.sceneView._clearScene()

	def updateToolbarStatus(self, status):
		if status:
			self.enableLabelTool(self.playTool  , True)
			self.enableLabelTool(self.stopTool  , False)
			self.enableLabelTool(self.pauseTool , False)
			self.enableLabelTool(self.resumeTool, False)
			self.buttonShowVideoViews.Show()
		else:
			self.enableLabelTool(self.playTool  , False)
			self.enableLabelTool(self.stopTool  , False)
			self.enableLabelTool(self.pauseTool , False)
			self.enableLabelTool(self.resumeTool, False)
			self.buttonShowVideoViews.Hide()
			self.buttonRaw.Hide()
			self.buttonLas.Hide()
			self.buttonDiff.Hide()
			self.buttonBin.Hide()
			self.buttonLine.Hide()

	def updateProfileToAllControls(self):
		pass