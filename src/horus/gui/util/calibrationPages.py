#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: August 2014                                                     #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>   	                #
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

from horus.gui.util.page import *
from horus.gui.util.videoView import *
from horus.gui.util.calibrationPanels import *

from horus.util import resources

from horus.engine.calibration import *


class LaserTriangulationMainPage(Page):

	def __init__(self, parent, buttonCancelCallback=None, buttonPerformCallback=None):
		Page.__init__(self, parent,
							title=_("Laser Triangulation"),
							left=_("Cancel"),
							right=_("Perform"),
							buttonLeftCallback=buttonCancelCallback,
							buttonRightCallback=buttonPerformCallback,
							panelOrientation=wx.VERTICAL)

		detailsBox = wx.BoxSizer(wx.HORIZONTAL)

		imageView = VideoView(self._panel)
		imageView.setImage(wx.Image(resources.getPathForImage("patternPosition.png")))
		detailsText = wx.StaticText(self._panel, label=_("Put the pattern on the platform"))
		detailsText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

		detailsBox.Add((0, 0), 1, wx.EXPAND)
		detailsBox.Add(detailsText, 0, wx.ALL|wx.EXPAND, 3)
		detailsBox.Add((0, 0), 1, wx.EXPAND)

		self.addToPanel(imageView, 1)
		self.addToPanel(detailsBox, 0)


class LaserTriangulationResultPage(Page):

	def __init__(self, parent, buttonRejectCallback=None, buttonAcceptCallback=None):
		Page.__init__(self, parent,
							title=_("Laser Triangulation"),
							left=_("Reject"),
							right=_("Accept"),
							buttonLeftCallback=buttonRejectCallback,
							buttonRightCallback=buttonAcceptCallback,
							panelOrientation=wx.HORIZONTAL)

		vbox = wx.BoxSizer(wx.VERTICAL)

		laserTriangulationParameters = LaserTriangulationParameters(self._panel)

		leftLaserImageSequence = LaserTriangulationImageSequence(self._panel, "Left Laser Image Sequence")
		rightLaserImageSequence = LaserTriangulationImageSequence(self._panel, "Right Laser Image Sequence")

		#-- Layout
		vbox.Add(leftLaserImageSequence, 1, wx.ALL|wx.EXPAND, 3)
		vbox.Add(rightLaserImageSequence, 1, wx.ALL|wx.EXPAND, 3)

		self.addToPanel(laserTriangulationParameters, 1)
		self.addToPanel(vbox, 3)

		#-- Events
		self.Bind(wx.EVT_SHOW, self.onShow)

	def onShow(self, event):
		if event.GetShow():
			self.performCalibration()

	def performCalibration(self):
		Calibration.Instance().performLaserTriangulationCalibration()


class LaserTriangulationImageSequence(wx.Panel):

	def __init__(self, parent, title="Title"):
		wx.Panel.__init__(self, parent)

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)

		titleText = wx.StaticText(self, label=title)
		titleText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

		panel = wx.Panel(self)
		imageLaser = VideoView(panel)
		imageBin = VideoView(panel)
		imageLine = VideoView(panel)

		imageLaser.SetBackgroundColour(wx.BLACK)
		imageBin.SetBackgroundColour(wx.BLACK)
		imageLine.SetBackgroundColour(wx.BLACK)

		#-- Layout
		vbox.Add(titleText, 0, wx.ALL|wx.EXPAND, 5)
		hbox.Add(imageLaser, 1, wx.ALL|wx.EXPAND, 3)
		hbox.Add(imageBin, 1, wx.ALL|wx.EXPAND, 3)
		hbox.Add(imageLine, 1, wx.ALL|wx.EXPAND, 3)
		panel.SetSizer(hbox)
		vbox.Add(panel, 1, wx.ALL|wx.EXPAND, 3)

		self.SetSizer(vbox)
		self.Layout()