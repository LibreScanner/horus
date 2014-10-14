#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: October 2014                                                    #
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

from horus.gui.util.imageView import VideoView

class WizardPage(wx.Panel):
	def __init__(self, parent, title="Title", buttonLeftCallback=None, buttonRightCallback=None):
		wx.Panel.__init__(self, parent)

		self.title = title
		self.panel = wx.Panel(self)

		self.buttonLeftCallback = buttonLeftCallback
		self.buttonRightCallback = buttonRightCallback

		self.videoView = VideoView(self, size=(300, 400))
		self.videoView.SetBackgroundColour(wx.BLACK)
		self.leftButton = wx.Button(self, label=_("Prev"))
		self.rightButton = wx.Button(self, label=_("Next"))

	def intialize(self, pages):
		breadcrumbs = Breadcrumbs(self, pages)

		#-- Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(breadcrumbs, 0, wx.ALL^wx.TOP|wx.EXPAND, 10)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.panel, 1, wx.RIGHT|wx.EXPAND, 10)
		hbox.Add(self.videoView, 0, wx.ALL, 0)
		vbox.Add(hbox, 1, wx.ALL|wx.EXPAND, 20)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.leftButton, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 2)
		hbox.Add((0, 0), 1, wx.EXPAND)
		hbox.Add(self.rightButton, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 2)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 10)

		self.SetSizer(vbox)

		#-- Events
		self.leftButton.Bind(wx.EVT_BUTTON, self._onLeftButtonPressed)
		self.rightButton.Bind(wx.EVT_BUTTON, self._onRightButtonPressed)

		self.Layout()

	def enableNext(self):
		return True

	def addToPanel(self, _object, _size):
		if _object is not None:
			self.panelBox.Add(_object, _size, wx.ALL|wx.EXPAND, 3)

	def _onLeftButtonPressed(self, event):
		if self.buttonLeftCallback is not None:
			self.buttonLeftCallback()

	def _onRightButtonPressed(self, event):
		if self.buttonRightCallback is not None:
			self.buttonRightCallback()


class Breadcrumbs(wx.Panel):
	def __init__(self, parent, pages=[]):
		wx.Panel.__init__(self, parent)

		self.pages = pages

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		for page in self.pages:
			title = wx.StaticText(self, label=page.title)
			title.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
			if self.GetParent().title == page.title:
				title.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
			else:
				title.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_LIGHT)))
			title.Bind(wx.EVT_LEFT_UP, self.onTitlePressed)
			hbox.Add(title, 0, wx.ALL|wx.EXPAND, 0)
			if page is not pages[-1]:
				line = wx.StaticText(self, label="  .....................  ")
				line.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_LIGHT)))
				hbox.Add(line, 0, wx.ALL|wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.ALL|wx.CENTER, 0)

		self.SetSizer(vbox)
		self.Layout()

	def onTitlePressed(self, event):
		label = event.GetEventObject().GetLabel()
		for page in self.pages:
			if page.enableNext():
				if page.title == label:
					page.Show()
				else:
					page.Hide()

		self.GetParent().GetParent().Layout()