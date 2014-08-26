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
		self.hbox = wx.BoxSizer(wx.HORIZONTAL)

		self.toolbar = wx.ToolBar(self)
		self._panel = wx.Panel(self)

		vbox.Add(self.toolbar, 0, wx.ALL|wx.EXPAND, 1)
		vbox.Add(self._panel, 1, wx.ALL|wx.EXPAND, 1)

		self._panel.SetSizer(self.hbox)
		self._panel.Layout()

		self.SetSizer(vbox)
		self.Layout()
		self.Hide()

	def addToPanel(self, _object, _size):
		if _object is not None:
			self.hbox.Add(_object, _size, wx.ALL|wx.EXPAND, 3)