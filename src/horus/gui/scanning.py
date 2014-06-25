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

from horus.util.resources import *

from horus.gui.util.workbench import *
from horus.gui.util.videoPanel import *
from horus.gui.util.videoView import *
from horus.gui.util.scenePanel import *
from horus.gui.util.sceneView import *

class ScanningWorkbench(Workbench):

	def __init__(self, parent):
		Workbench.__init__(self, parent, 0, 1)

		self.view3D = True

		self.load()

		self.scanner = self.GetParent().scanner

		self.Bind(wx.EVT_SHOW, self.onShow)

	def load(self):

		#-- Toolbar Configuration
		
		self.connectTool    = self.toolbar.AddLabelTool(wx.NewId(), _("Connect"), wx.Bitmap(getPathForImage("connect.png")), shortHelp=_("Connect"))
		self.disconnectTool = self.toolbar.AddLabelTool(wx.NewId(), _("Disconnect"), wx.Bitmap(getPathForImage("disconnect.png")), shortHelp=_("Disconnect"))
		self.playTool       = self.toolbar.AddLabelTool(wx.NewId(), _("Play"), wx.Bitmap(getPathForImage("play.png")), shortHelp=_("Play"))
		self.stopTool       = self.toolbar.AddLabelTool(wx.NewId(), _("Stop"), wx.Bitmap(getPathForImage("stop.png")), shortHelp=_("Stop"))
		self.pauseTool      = self.toolbar.AddLabelTool(wx.NewId(), _("Pause"), wx.Bitmap(getPathForImage("pause.png")), shortHelp=_("Pause"))
		self.resumeTool     = self.toolbar.AddLabelTool(wx.NewId(), _("Resume"), wx.Bitmap(getPathForImage("resume.png")), shortHelp=_("Resume"))
		self.deleteTool     = self.toolbar.AddLabelTool(wx.NewId(), _("Delete"), wx.Bitmap(getPathForImage("delete.png")), shortHelp=_("Clear"))
		self.viewTool       = self.toolbar.AddLabelTool(wx.NewId(), _("View"), wx.Bitmap(getPathForImage("view.png")), shortHelp=_("3D / Camera"))
		self.toolbar.Realize()

		#-- Bind Toolbar Items

		self.Bind(wx.EVT_TOOL, self.onConnectToolClicked   , self.connectTool)
		self.Bind(wx.EVT_TOOL, self.onDisconnectToolClicked, self.disconnectTool)
		self.Bind(wx.EVT_TOOL, self.onPlayToolClicked      , self.playTool)
		self.Bind(wx.EVT_TOOL, self.onStopToolClicked      , self.stopTool)
		self.Bind(wx.EVT_TOOL, self.onPauseToolClicked     , self.pauseTool)
		self.Bind(wx.EVT_TOOL, self.onResumeToolClicked    , self.resumeTool)
		self.Bind(wx.EVT_TOOL, self.onDeleteToolClicked    , self.deleteTool)
		self.Bind(wx.EVT_TOOL, self.onViewToolClicked      , self.viewTool)

		#-- Left Panel
		self.videoPanel = VideoPanel(self._leftPanel)
		self.scenePanel = ScenePanel(self._leftPanel)

		#-- Right Views

		self.videoView = VideoView(self._rightPanel)
		self.sceneView = SceneView(self._rightPanel)
		self.videoView.SetBackgroundColour(wx.BLACK)
		self.sceneView.SetBackgroundColour(wx.BLACK)
		
		self.updateView()

	def onShow(self, event):
		if event.GetShow():
			self.updateToolbarStatus(self.scanner.isConnected)
		else:
			self.onStopToolClicked(None)

	def onConnectToolClicked(self, event):
		self.updateToolbarStatus(True)
		self.scanner.connect()

	def onDisconnectToolClicked(self, event):
		self.scanner.disconnect()
		self.updateToolbarStatus(False)

	def onPlayToolClicked(self, event):
		self.enableLabelTool(self.playTool, False)
		self.enableLabelTool(self.stopTool, True)
		
		self.scanner.start()

	def onStopToolClicked(self, event):
		self.enableLabelTool(self.playTool, True)
		self.enableLabelTool(self.stopTool, False)
		
		self.scanner.stop()

	def onPauseToolClicked(self, event):
		self.enableLabelTool(self.pauseTool , False)
		self.enableLabelTool(self.resumeTool, True)
		pass

	def onResumeToolClicked(self, event):
		self.enableLabelTool(self.pauseTool , True)
		self.enableLabelTool(self.resumeTool, False)
		pass

	def onDeleteToolClicked(self, event):
		self.sceneView._clearScene()

	def onViewToolClicked(self, event):
		self.view3D = not self.view3D
		self.updateView()

	def updateView(self):
		if self.view3D:
			self.videoPanel.Hide()
			self.videoView.Hide()
			self.scenePanel.Show()
			self.sceneView.Show()
			self.addToLeft(self.scenePanel)
			self.addToRight(self.sceneView)
		else:
			self.scenePanel.Hide()
			self.sceneView.Hide()
			self.videoPanel.Show()
			self.videoView.Show()
			self.addToLeft(self.videoPanel)
			self.addToRight(self.videoView)
		self.Layout()

	def enableLabelTool(self, item, enable):
		self.toolbar.EnableTool(item.GetId(), enable)

	def updateToolbarStatus(self, status):
		if status:
			self.enableLabelTool(self.connectTool   , False)
			self.enableLabelTool(self.disconnectTool, True)
			self.enableLabelTool(self.playTool      , True)
			self.enableLabelTool(self.stopTool      , False)
			self.enableLabelTool(self.pauseTool     , True)
			self.enableLabelTool(self.resumeTool    , False)
		else:
			self.enableLabelTool(self.connectTool   , True)
			self.enableLabelTool(self.disconnectTool, False)
			self.enableLabelTool(self.playTool      , False)
			self.enableLabelTool(self.stopTool      , False)
			self.enableLabelTool(self.pauseTool     , False)
			self.enableLabelTool(self.resumeTool    , False)