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

from horus.engine.scanner import *
from horus.engine.calibration import *

class CameraIntrinsicsMainPage(Page):

	def __init__(self, parent, buttonCancelCallback=None, buttonPerformCallback=None):
		Page.__init__(self, parent,
							title=_("Camera Intrinsics"),
							left=_("Cancel"),
							right=_("Perform"),
							buttonLeftCallback=buttonCancelCallback,
							buttonRightCallback=buttonPerformCallback,
							panelOrientation=wx.HORIZONTAL)

		self.scanner = Scanner.Instance()

		self.playing = False

		#-- Video View
		self.videoView = VideoView(self._panel)
		self.videoView.SetBackgroundColour(wx.BLACK)
		self.videoView.setImage(wx.Image(resources.getPathForImage("bq.png")))
		
		#--Guide Panel
		self.guidePanel = wx.Panel(self._panel)
		guideBox = wx.BoxSizer(wx.VERTICAL)

		self.guidePage = 0

		self.guideTitleText = wx.StaticText(self.guidePanel, label=_("1. Place the pattern in the plate"))
		self.guideTitleText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
		self.guideTitleText.SetFont( wx.Font(pointSize=16,family=wx.FONTFAMILY_DECORATIVE,style=wx.FONTSTYLE_ITALIC,weight=wx.FONTWEIGHT_NORMAL))
		self.guideTitleText.SetForegroundColour((100,100,100))

		self.guideImage = VideoView(self.guidePanel)
		self.guideImage.setImage(wx.Image(resources.getPathForImage("instructions-1.png")))

		self.guideProgress = VideoView(self.guidePanel)
		self.guideProgress.size = (100,100)
		self.guideProgress.setImage(wx.Image(resources.getPathForImage("progress-1.png")))

		guideSpacebarText = wx.StaticText(self.guidePanel, label=_("Press spacebar to continue"))

		guideBox.Add(self.guideTitleText, 0, wx.CENTER, 3)
		guideBox.Add((0, 0), 1, wx.EXPAND)
		guideBox.Add(self.guideImage, 10, wx.ALL|wx.EXPAND, 3)
		guideBox.Add((0, 0), 2, wx.EXPAND)
		guideBox.Add(self.guideProgress, 0, wx.ALL|wx.EXPAND|wx.CENTER, 3)
		guideBox.Add((0, 0), 1, wx.EXPAND)
		guideBox.Add(guideSpacebarText, 0, wx.CENTER, 3)

		self.guidePanel.SetSizer(guideBox)

		#-- Image Grid Panel
		self.imageGridPanel = wx.Panel(self._panel)
		self.imageGridPanel.Hide()
		self.currentGrid = 0
		self.rows, self.columns = 2, 6
		gridSizer = wx.GridSizer(self.rows, self.columns, 3, 3)
		self.panelGrid=[]
		for panel in range(self.rows*self.columns):
			self.panelGrid.append(VideoView(self.imageGridPanel)) 
			self.panelGrid[panel].SetBackgroundColour((221, 221, 221))
			self.panelGrid[panel].setImage(wx.Image(getPathForImage("void.png")))
			self.panelGrid[panel].index = panel
			gridSizer.Add(self.panelGrid[panel], 0 , wx.ALL|wx.EXPAND)
		self.imageGridPanel.SetSizer(gridSizer)

		self.addToPanel(self.videoView, 2)
		self.addToPanel(self.guidePanel, 3)
		self.addToPanel(self.imageGridPanel, 3)

		self._rightButton.Disable()

		self.timer = wx.Timer(self)

		#-- Events
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
		self.Bind(wx.EVT_SHOW, self.onShow)
		self.videoView.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
		
		self.videoView.SetFocus()

		self.Layout()

	def onShow(self, event):
		if event.GetShow():
			mseconds = 1000/(self.scanner.camera.fps)
			self.timer.Start(milliseconds=mseconds)
		else:
			self.timer.Stop()

	def onTimer(self, event):
		if self.scanner.isConnected:
			frame = self.scanner.camera.captureImage()
			if frame is not None:
				self.videoView.setFrame(frame)

	def onKeyPress(self, event):
		if event.GetKeyCode() == 32: #-- spacebar
			if self.guidePage == 0:
				self.guideTitleText.SetLabel("2. Move it according to the yellow lines")
				self.guideImage.setImage(wx.Image(resources.getPathForImage("instructions-2.png")))
				self.guideProgress.setImage(wx.Image(resources.getPathForImage("progress-2.png")))
				self.guidePage = 1
			elif self.guidePage == 1:
				self.guideTitleText.SetLabel("3. Press spacebar to perform captures")
				self.guideImage.setImage(wx.Image(resources.getPathForImage("instructions-3.png")))
				self.guideProgress.setImage(wx.Image(resources.getPathForImage("progress-3.png")))
				self.guidePage = 2
			elif self.guidePage == 2:
				self.guidePanel.Hide()
				self.imageGridPanel.Show()
				self.Layout()
				self.guidePage = 3
			elif self.guidePage == 3:
				if self.scanner.isConnected:
					frame = self.scanner.camera.captureImage(mirror=True, flush=True)
					#TODO #retval, frame = self.calibration.detectPrintChessboard(frame)
					self.addFrameToGrid(True, frame)

	def addFrameToGrid(self, retval, image):
		if self.currentGrid < (self.columns*self.rows):
			if retval:
				self.panelGrid[self.currentGrid].setFrame(image)
				#self.panelGrid[self.currentGrid].SetBackgroundColour((45,178,0))
				self.currentGrid += 1
			else:
				self.panelGrid[self.currentGrid].setFrame(image)
				#self.panelGrid[self.currentGrid].SetBackgroundColour((217,0,0))

		if self.currentGrid is (self.columns*self.rows):
			self._rightButton.Enable()


class CameraIntrinsicsResultPage(Page):

	def __init__(self, parent, buttonRejectCallback=None, buttonAcceptCallback=None):
		Page.__init__(self, parent,
							title=_("Camera Intrinsics"),
							left=_("Reject"),
							right=_("Accept"),
							buttonLeftCallback=buttonRejectCallback,
							buttonRightCallback=buttonAcceptCallback,
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

		self.laserTriangulationParameters = LaserTriangulationParameters(self._panel)

		self.leftLaserImageSequence = LaserTriangulationImageSequence(self._panel, "Left Laser Image Sequence")
		self.rightLaserImageSequence = LaserTriangulationImageSequence(self._panel, "Right Laser Image Sequence")

		#-- Layout
		vbox.Add(self.leftLaserImageSequence, 1, wx.ALL|wx.EXPAND, 3)
		vbox.Add(self.rightLaserImageSequence, 1, wx.ALL|wx.EXPAND, 3)

		self.addToPanel(self.laserTriangulationParameters, 1)
		self.addToPanel(vbox, 3)

		#-- Events
		self.Bind(wx.EVT_SHOW, self.onShow)

	def onShow(self, event):
		if event.GetShow():
			self.performCalibration()

	def performCalibration(self):
		ret = Calibration.Instance().performLaserTriangulationCalibration()

		self.laserTriangulationParameters.updateAllControlsToProfile(ret[1], ret[0])

		self.leftLaserImageSequence.imageLas.setFrame(ret[2][0][0])
		self.leftLaserImageSequence.imageGray.setFrame(ret[2][0][1])
		self.leftLaserImageSequence.imageBin.setFrame(ret[2][0][2])
		self.leftLaserImageSequence.imageLine.setFrame(ret[2][0][3])
		self.rightLaserImageSequence.imageLas.setFrame(ret[2][1][0])
		self.rightLaserImageSequence.imageGray.setFrame(ret[2][1][1])
		self.rightLaserImageSequence.imageBin.setFrame(ret[2][1][2])
		self.rightLaserImageSequence.imageLine.setFrame(ret[2][1][3])

class LaserTriangulationImageSequence(wx.Panel):

	def __init__(self, parent, title="Title"):
		wx.Panel.__init__(self, parent)

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)

		titleText = wx.StaticText(self, label=title)
		titleText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

		panel = wx.Panel(self)
		self.imageLas = VideoView(panel)
		self.imageGray = VideoView(panel)
		self.imageBin = VideoView(panel)
		self.imageLine = VideoView(panel)

		self.imageLas.SetBackgroundColour('#AAAAAA')
		self.imageGray.SetBackgroundColour('#AAAAAA')
		self.imageBin.SetBackgroundColour('#AAAAAA')
		self.imageLine.SetBackgroundColour('#AAAAAA')

		#-- Layout
		vbox.Add(titleText, 0, wx.ALL|wx.EXPAND, 5)
		hbox.Add(self.imageLas, 1, wx.ALL|wx.EXPAND, 3)
		hbox.Add(self.imageGray, 1, wx.ALL|wx.EXPAND, 3)
		hbox.Add(self.imageBin, 1, wx.ALL|wx.EXPAND, 3)
		hbox.Add(self.imageLine, 1, wx.ALL|wx.EXPAND, 3)
		panel.SetSizer(hbox)
		vbox.Add(panel, 1, wx.ALL|wx.EXPAND, 3)

		self.SetSizer(vbox)
		self.Layout()