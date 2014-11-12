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
# the Free Software Foundation, either version 2 of the License, or     #
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
__license__ = "GNU General Public License v2 http://www.gnu.org/licenses/gpl.html"

import wx._core

class Page(wx.Panel):
	def __init__(self, parent, title="Title", subTitle="", left="Left", right="Right",
				 buttonLeftCallback=None, buttonRightCallback=None, panelOrientation=wx.VERTICAL, viewProgress=False):
		wx.Panel.__init__(self, parent)
		
		self.buttonLeftCallback = buttonLeftCallback
		self.buttonRightCallback = buttonRightCallback

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.panelBox = wx.BoxSizer(panelOrientation)

		self._panel = wx.Panel(self)
		self._downPanel = wx.Panel(self)

		titleText = wx.StaticText(self, label=title)
		titleText.SetFont((wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
		if subTitle != "":
			self.subTitleText = wx.StaticText(self, label=subTitle)
		self.gauge = wx.Gauge(self, range=100, size=(-1, 30))
		self._leftButton = wx.Button(self._downPanel, -1, left)
		self._rightButton = wx.Button(self._downPanel, -1, right)

		#-- Layout
		vbox.Add(titleText, 0, wx.ALL|wx.EXPAND, 10)
		if subTitle != "":
			vbox.Add(self.subTitleText, 0, wx.ALL|wx.EXPAND, 10)
		vbox.Add(self._panel, 1, wx.ALL|wx.EXPAND, 8)
		vbox.Add(self.gauge, 0, wx.ALL|wx.EXPAND, 8)
		self._panel.SetSizer(self.panelBox)
		vbox.Add(self._downPanel, 0, wx.ALL|wx.EXPAND, 1)
		hbox.Add(self._leftButton, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 7)
		hbox.Add((0, 0), 1, wx.EXPAND)
		hbox.Add(self._rightButton, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 7)
		self._downPanel.SetSizer(hbox)

		if not viewProgress:
			self.gauge.Hide()
			
		self.SetSizer(vbox)

		#-- Events
		self._leftButton.Bind(wx.EVT_BUTTON, self._onLeftButtonPressed)
		self._rightButton.Bind(wx.EVT_BUTTON, self._onRightButtonPressed)

		self.Layout()

	def addToPanel(self, _object, _size):
		if _object is not None:
			self.panelBox.Add(_object, _size, wx.ALL|wx.EXPAND, 3)

	def _onLeftButtonPressed(self, event):
		if self.buttonLeftCallback is not None:
			self.buttonLeftCallback()

	def _onRightButtonPressed(self, event):
		if self.buttonRightCallback is not None:
			self.buttonRightCallback()