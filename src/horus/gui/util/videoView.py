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

from horus.util import resources

class VideoView(wx.Panel):

	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.bmp = wx.Bitmap(resources.getPathForImage("bq.png"))
		self.Bind(wx.EVT_PAINT, self.onPaint)

		self.SetBackgroundColour(wx.GREEN)
		self.Centre()

	def onPaint(self, event):
		dc = wx.PaintDC(self)
		dc.DrawBitmap(self.bmp, 0, 0)

	def setBitmap(self, bmp):
		self.bmp = bmp
		self.Refresh()

	def setFrame(self, frame):
		height, width = frame.shape[:2]
		self.bmp = wx.BitmapFromBuffer(width, height, frame)
		self.Refresh()

