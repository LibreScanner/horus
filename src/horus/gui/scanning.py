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

from horus.gui.util.videoPanel import *
from horus.gui.util.videoView import *
from horus.gui.util.scenePanel import *
from horus.gui.util.sceneView import *
from horus.gui.util.workbenchConnection import *

class ScanningWorkbench(WorkbenchConnection):

	def __init__(self, parent):
		WorkbenchConnection.__init__(self, parent)

		self.view3D = False
		self.showVideoViews = False

		self.load()

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

	def load(self):
		#-- Toolbar Configuration
		self.playTool       = self.toolbar.AddLabelTool(wx.NewId(), _("Play"), wx.Bitmap(getPathForImage("play.png")), shortHelp=_("Play"))
		self.stopTool       = self.toolbar.AddLabelTool(wx.NewId(), _("Stop"), wx.Bitmap(getPathForImage("stop.png")), shortHelp=_("Stop"))
		self.resumeTool     = self.toolbar.AddLabelTool(wx.NewId(), _("Resume"), wx.Bitmap(getPathForImage("resume.png")), shortHelp=_("Resume"))
		self.pauseTool      = self.toolbar.AddLabelTool(wx.NewId(), _("Pause"), wx.Bitmap(getPathForImage("pause.png")), shortHelp=_("Pause"))
		#self.deleteTool     = self.toolbar.AddLabelTool(wx.NewId(), _("Delete"), wx.Bitmap(getPathForImage("delete.png")), shortHelp=_("Clear"))
		self.viewTool       = self.toolbar.AddLabelTool(wx.NewId(), _("View"), wx.Bitmap(getPathForImage("view.png")), shortHelp=_("3D / Camera"))
		self.toolbar.Realize()

		#-- Bind Toolbar Items
		self.Bind(wx.EVT_TOOL, self.onPlayToolClicked      , self.playTool)
		self.Bind(wx.EVT_TOOL, self.onStopToolClicked      , self.stopTool)
		self.Bind(wx.EVT_TOOL, self.onResumeToolClicked    , self.resumeTool)
		self.Bind(wx.EVT_TOOL, self.onPauseToolClicked     , self.pauseTool)
		#self.Bind(wx.EVT_TOOL, self.onDeleteToolClicked    , self.deleteTool)
		self.Bind(wx.EVT_TOOL, self.onViewToolClicked      , self.viewTool)

		#-- Left Panel
		self.videoPanel = VideoPanel(self._panel)
		self.scenePanel = ScenePanel(self._panel)

		self.videoPanel.Disable()
		self.scenePanel.Disable()

		#-- Right Views
		self.videoView = VideoView(self._panel)
		self.sceneView = SceneView(self._panel)
		self.videoView.SetBackgroundColour(wx.BLACK)
		self.sceneView.SetBackgroundColour(wx.BLACK)

		self.addToPanel(self.scenePanel, 0)
		self.addToPanel(self.sceneView, 1)

		self.addToPanel(self.videoPanel, 0)
		self.addToPanel(self.videoView, 1)

		#-- Video View Selector
		self.buttonShowVideoViews = wx.BitmapButton(self.videoView, wx.NewId(), wx.Bitmap(resources.getPathForImage("views.png"), wx.BITMAP_TYPE_ANY), (10,10))
		self.buttonRaw  = wx.RadioButton(self.videoView, wx.NewId(), _("Raw"), pos=(10,15+40))
		self.buttonLas  = wx.RadioButton(self.videoView, wx.NewId(), _("Laser"), pos=(10,15+80))
		self.buttonDiff = wx.RadioButton(self.videoView, wx.NewId(), _("Diff"), pos=(10,15+120))
		self.buttonBin  = wx.RadioButton(self.videoView, wx.NewId(), _("Binary"), pos=(10,15+160))

		self.buttonShowVideoViews.Hide()
		self.buttonRaw.Hide()
		self.buttonLas.Hide()
		self.buttonDiff.Hide()
		self.buttonBin.Hide()

		self.buttonRaw.SetForegroundColour(wx.WHITE)
		self.buttonLas.SetForegroundColour(wx.WHITE)
		self.buttonDiff.SetForegroundColour(wx.WHITE)
		self.buttonBin.SetForegroundColour(wx.WHITE)

		self.buttonRaw.SetBackgroundColour(wx.BLACK)
		self.buttonLas.SetBackgroundColour(wx.BLACK)
		self.buttonDiff.SetBackgroundColour(wx.BLACK)
		self.buttonBin.SetBackgroundColour(wx.BLACK)

		self.Bind(wx.EVT_BUTTON, self.onShowVideoViews, self.buttonShowVideoViews)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSelectVideoView, self.buttonRaw)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSelectVideoView, self.buttonLas)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSelectVideoView, self.buttonDiff)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSelectVideoView, self.buttonBin)
		
		self.updateView()

	def onShowVideoViews(self, event):
		self.showVideoViews = not self.showVideoViews
		if self.showVideoViews:
			self.buttonRaw.Show()
			self.buttonLas.Show()
			self.buttonDiff.Show()
			self.buttonBin.Show()
		else:
			self.buttonRaw.Hide()
			self.buttonLas.Hide()
			self.buttonDiff.Hide()
			self.buttonBin.Hide()

	def onSelectVideoView(self, event):
		selectedView = {self.buttonRaw.GetId()  : 'raw',
						self.buttonLas.GetId()  : 'las',
						self.buttonDiff.GetId() : 'diff',
						self.buttonBin.GetId()  : 'bin'}.get(event.GetId())

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
		
		self.sceneView.createDefaultObject()

		self.scanner.start()

	def onStopToolClicked(self, event):
		self.enableLabelTool(self.playTool, True)
		self.enableLabelTool(self.stopTool, False)
		
		self.scanner.stop()

	def onResumeToolClicked(self, event):
		self.enableLabelTool(self.pauseTool , True)
		self.enableLabelTool(self.resumeTool, False)
		
		self.timer.Start(milliseconds=100)

	def onPauseToolClicked(self, event):
		self.enableLabelTool(self.pauseTool , False)
		self.enableLabelTool(self.resumeTool, True)
		
		self.timer.Stop()

	def onDeleteToolClicked(self, event):
		self.sceneView._clearScene()

	def onViewToolClicked(self, event):
		self.view3D = not self.view3D
		profile.putPreference('view_3d', self.view3D)
		self.updateView()

	def updateView(self):
		if self.view3D:
			self.videoPanel.Hide()
			self.videoView.Hide()
			self.scenePanel.Show()
			self.sceneView.Show()
		else:
			self.scenePanel.Hide()
			self.sceneView.Hide()
			self.videoPanel.Show()
			self.videoView.Show()
		self.Layout()

	def updateToolbarStatus(self, status):
		if status:
			self.enableLabelTool(self.playTool  , True)
			self.enableLabelTool(self.stopTool  , False)
			self.enableLabelTool(self.resumeTool, True)
			self.enableLabelTool(self.pauseTool , False)
			self.videoPanel.Enable()
			self.scenePanel.Enable()
			self.buttonShowVideoViews.Show()
		else:
			self.enableLabelTool(self.playTool  , False)
			self.enableLabelTool(self.stopTool  , False)
			self.enableLabelTool(self.resumeTool, False)
			self.enableLabelTool(self.pauseTool , False)
			self.videoPanel.Disable()
			self.scenePanel.Disable()
			self.buttonShowVideoViews.Hide()
			self.buttonRaw.Hide()
			self.buttonLas.Hide()
			self.buttonDiff.Hide()
			self.buttonBin.Hide()

	def updateProfileToAllControls(self):
		self.videoPanel.updateProfileToAllControls()
		self.scenePanel.updateProfileToAllControls()
		self.view3D = profile.getPreferenceBool('view_3d')
		self.updateView()