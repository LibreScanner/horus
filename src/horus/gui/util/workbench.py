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

import wx

class Workbench(wx.Panel):

	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox = wx.BoxSizer(wx.HORIZONTAL)

		self.toolbar = wx.ToolBar(self)
		self.combo = wx.ComboBox(self, -1, style=wx.CB_READONLY)
		self._panel = wx.Panel(self)

		hbox.Add(self.toolbar, 0, wx.ALL|wx.EXPAND, 1)
		hbox.Add((0,0), 1, wx.ALL|wx.EXPAND, 1)
		hbox.Add(self.combo, 0, wx.ALL, 10)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 1)
		vbox.Add(self._panel, 1, wx.ALL|wx.EXPAND, 1)

		self._panel.SetSizer(self.hbox)
		self._panel.Layout()

		self.SetSizer(vbox)
		self.Layout()
		self.Hide()

	def addToPanel(self, _object, _size):
		if _object is not None:
			self.hbox.Add(_object, _size, wx.ALL|wx.EXPAND, 3)


from horus.util.resources import *

from horus.engine.scanner import *

class WorkbenchConnection(Workbench):

	def __init__(self, parent):
		Workbench.__init__(self, parent)

		self.scanner = Scanner.Instance()

		#-- Toolbar Configuration
		self.connectTool    = self.toolbar.AddLabelTool(wx.NewId(), _("Connect"), wx.Bitmap(getPathForImage("connect.png")), shortHelp=_("Connect"))
		self.disconnectTool = self.toolbar.AddLabelTool(wx.NewId(), _("Disconnect"), wx.Bitmap(getPathForImage("disconnect.png")), shortHelp=_("Disconnect"))
		self.toolbar.Realize()

		#-- Disable Toolbar Items
		self.enableLabelTool(self.connectTool   , True)
		self.enableLabelTool(self.disconnectTool, False)

		#-- Bind Toolbar Items
		self.Bind(wx.EVT_TOOL, self.onConnectToolClicked   , self.connectTool)
		self.Bind(wx.EVT_TOOL, self.onDisconnectToolClicked, self.disconnectTool)

		self.Layout()

		self.Bind(wx.EVT_SHOW, self.onShow)

	def onShow(self, event):
		if event.GetShow():
			self.updateStatus(self.scanner.isConnected)

	def onConnectToolClicked(self, event):
		self.updateStatus(True)
		if not self.scanner.connect():
			self.updateStatus(False)
			self.GetParent().onPreferences(None)
		else:
			self.GetParent().updateCameraCurrentProfile()

	def onDisconnectToolClicked(self, event):
		self.scanner.stop()
		if self.scanner.disconnect():
			self.updateStatus(False)

	def enableLabelTool(self, item, enable):
		self.toolbar.EnableTool(item.GetId(), enable)

	def updateStatus(self, status):
		if status:
			self.enableLabelTool(self.connectTool   , False)
			self.enableLabelTool(self.disconnectTool, True)
		else:
			self.enableLabelTool(self.connectTool   , True)
			self.enableLabelTool(self.disconnectTool, False)
		self.updateToolbarStatus(status)

	def updateToolbarStatus(self, status):
		pass