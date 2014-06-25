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

import wx

import sys
import random

class Page(wx.Panel):
	def __init__(self, parent, left="Left", right="Right"):
		wx.Panel.__init__(self, parent)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self._titlePanel = wx.Panel(self)
		self._upPanel = wx.Panel(self, id=wx.ID_ANY,style=wx.SUNKEN_BORDER)
		self._downPanel = wx.Panel(self)
		self._leftButton = wx.Button(self._downPanel, -1, left)
		self._rightButton = wx.Button(self._downPanel, -1, right)
		
		vbox.Add(self._titlePanel,1,wx.ALL|wx.EXPAND,20)

		vbox.Add(self._upPanel, 9, wx.ALL|wx.EXPAND, 1)
		vbox.Add(self._downPanel, 0, wx.ALL|wx.EXPAND, 1)
		
		hbox.Add(self._leftButton, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
		hbox.Add((0, 0), 1, wx.EXPAND)	
		hbox.Add(self._rightButton, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
		
		self._downPanel.SetSizer(hbox)
		self._downPanel.Layout()
			
		self.SetSizer(vbox)
		self.Layout()

	def getPanel(self):
		return self._upPanel
	def getTitlePanel(self):
		return self._titlePanel
	def getRightButton(self):
		return self._rightButton

	def getLeftButton(self):
		return self._leftButton
