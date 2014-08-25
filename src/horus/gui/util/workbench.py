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

	def __init__(self, parent, leftSize=1, middleSize=None, rightSize=1):
		wx.Panel.__init__(self, parent)

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)

		self._leftObject = None
		self._middleObject = None
		self._rightObject = None

		self.leftSize = leftSize
		self.middleSize = middleSize
		self.rightSize = rightSize
		
		if leftSize is not None:
			self.leftBox = wx.BoxSizer(wx.VERTICAL)
		if middleSize is not None:
			self.middleBox = wx.BoxSizer(wx.VERTICAL)
		if rightSize is not None:
			self.rightBox = wx.BoxSizer(wx.VERTICAL)

		self.toolbar = wx.ToolBar(self)
		self._panel = wx.Panel(self)
		if leftSize is not None:
			self._leftPanel = wx.Panel(self._panel)
		if middleSize is not None:
			self._middlePanel = wx.Panel(self._panel)
		if rightSize is not None:
			self._rightPanel = wx.Panel(self._panel)

		vbox.Add(self.toolbar, 0, wx.ALL|wx.EXPAND, 1)
		vbox.Add(self._panel, 1, wx.ALL|wx.EXPAND, 1)

		if leftSize is not None:
			hbox.Add(self._leftPanel, leftSize, wx.ALL|wx.EXPAND, 2)
		if middleSize is not None:
			hbox.Add(self._middlePanel, middleSize, wx.ALL|wx.EXPAND, 2)
		if rightSize is not None:
			hbox.Add(self._rightPanel, rightSize, wx.ALL|wx.EXPAND, 2)

		if leftSize is not None:
			self._leftPanel.SetSizer(self.leftBox)
		if middleSize is not None:
			self._middlePanel.SetSizer(self.middleBox)
		if rightSize is not None:
			self._rightPanel.SetSizer(self.rightBox)
		self._panel.SetSizer(hbox)
		self._panel.Layout()

		self.SetSizer(vbox)
		self.Layout()
		self.Hide()

	def getPanel(self):
		return self._panel

	def addToLeft(self, _object):
		if self.leftSize is not None:
			self._leftObject = _object
			self.leftBox.Add(_object, 1, wx.ALL|wx.EXPAND, 3)

	def addToMiddle(self, _object):
		if self.middleSize is not None:
			self._middleObject = _object
			self.middleBox.Add(_object, 1, wx.ALL|wx.EXPAND, 3)

	def addToRight(self, _object):
		if self.rightSize is not None:
			self._rightObject = _object
			self.rightBox.Add(_object, 1, wx.ALL|wx.EXPAND, 3)