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
from horus.gui.util.videoView import *
from horus.gui.util.videoPanel import *

class ScanningWorkbench(Workbench):

	def __init__(self, parent):
		Workbench.__init__(self, parent, 1, 2)

		self.load()

	def load(self):

		#-- Toolbar Configuration

		connectTool = self.toolbar.AddLabelTool(wx.ID_ANY, _("Connect"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Connect / Disconnect"))
		startTool   = self.toolbar.AddLabelTool(wx.ID_ANY, _("Start"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Start / Stop"))
		pauseTool   = self.toolbar.AddLabelTool(wx.ID_ANY, _("Pause"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Pause / Resume"))
		clearTool   = self.toolbar.AddLabelTool(wx.ID_ANY, _("Clear"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Clear"))
		toggleTool  = self.toolbar.AddLabelTool(wx.ID_ANY, _("Toogle"), wx.Bitmap(getPathForImage("load.png")), shortHelp=_("Camera / 3D"))
		self.toolbar.Realize()

		#-- Bind Toolbar Items

		self.Bind(wx.EVT_TOOL, self.onConnectToolEnter, connectTool)
		self.Bind(wx.EVT_TOOL, self.onStartToolEnter, startTool)
		self.Bind(wx.EVT_TOOL, self.onPauseToolEnter, pauseTool)
		self.Bind(wx.EVT_TOOL, self.onClearToolEnter, clearTool)
		self.Bind(wx.EVT_TOOL, self.onToogleToolEnter, toggleTool)

		#-- Video Panel

		self.leftPanel.SetBackgroundColour(wx.GREEN)

		self.videoPanel = VideoPanel(self.leftPanel)
		self.videoPanel.SetBackgroundColour(wx.BLACK)
		self.addToLeft(self.videoPanel, 1, wx.ALL|wx.EXPAND, 5)

		#-- Video View

		self.videoView = VideoView(self.rightPanel)
		self.videoView.SetBackgroundColour(wx.BLACK)
		self.addToRight(self.videoView, 1, wx.ALL|wx.EXPAND, 5)

	def onConnectToolEnter(self, event):
		pass

	def onStartToolEnter(self, event):
		pass

	def onPauseToolEnter(self, event):
		pass

	def onClearToolEnter(self, event):
		pass

	def onToogleToolEnter(self, event):
		pass