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

import time
import wx._core

from horus.gui.util.imageView import ImageView

from horus.gui.wizard.wizardPage import WizardPage

import horus.util.error as Error
from horus.util import profile, resources

from horus.engine.driver import Driver
from horus.engine import calibration


class ConnectionPage(WizardPage):
	def __init__(self, parent, buttonPrevCallback=None, buttonNextCallback=None):
		WizardPage.__init__(self, parent,
							title=_("Connection"),
							buttonPrevCallback=buttonPrevCallback,
							buttonNextCallback=buttonNextCallback)

		self.driver = Driver.Instance()
		self.cameraIntrinsics = calibration.CameraIntrinsics.Instance()
		self.laserTriangulation = calibration.LaserTriangulation.Instance()

		self.connectButton = wx.Button(self.panel, label=_("Connect"))
		self.patternLabel = wx.StaticText(self.panel, label=_("Put the pattern on the platform and press \"Auto check\""))
		self.imageView = ImageView(self.panel)
		self.imageView.setImage(wx.Image(resources.getPathForImage("pattern-position-left.jpg")))
		self.autoCheckButton = wx.Button(self.panel, label=_("Auto check"))
		self.gauge = wx.Gauge(self.panel, range=100, size=(-1, 30))
		self.resultLabel = wx.StaticText(self.panel, label=_("All OK. Please press next to continue"), size=(-1, 30))

		self.connectButton.Enable()
		self.patternLabel.Disable()
		self.imageView.Disable()
		self.autoCheckButton.Disable()
		self.resultLabel.Hide()
		self.skipButton.Disable()
		self.nextButton.Disable()
		self.enableNext = False

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.connectButton, 0, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.patternLabel, 0, wx.ALL|wx.CENTER, 5)
		vbox.Add(self.imageView, 1, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.resultLabel, 0, wx.ALL|wx.CENTER, 5)
		vbox.Add(self.gauge, 0, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.autoCheckButton, 0, wx.ALL|wx.EXPAND, 5)
		self.panel.SetSizer(vbox)

		self.Layout()

		self.connectButton.Bind(wx.EVT_BUTTON, self.onConnectButtonClicked)
		self.autoCheckButton.Bind(wx.EVT_BUTTON, self.onAutoCheckButtonClicked)
		self.Bind(wx.EVT_SHOW, self.onShow)

		self.videoView.setMilliseconds(20)
		self.videoView.setCallback(self.getFrame)
		self.updateStatus(self.driver.isConnected)

	def onShow(self, event):
		if event.GetShow():
			self.updateStatus(self.driver.isConnected)
		else:
			try:
				self.videoView.stop()
			except:
				pass

	def getFrame(self):
		frame = self.driver.camera.captureImage()
		if frame is not None:
			retval, frame = self.cameraIntrinsics.detectChessboard(frame)
		return frame

	def onConnectButtonClicked(self, event):
		self.driver.setCallbacks(self.beforeConnect, lambda r: wx.CallAfter(self.afterConnect,r))
		self.driver.connect()

	def beforeConnect(self):
		self.connectButton.Disable()
		self.prevButton.Disable()
		self.waitCursor = wx.BusyCursor()

	def afterConnect(self, response):
		ret, result = response

		if not ret:
			if result is Error.WrongFirmware:
				dlg = wx.MessageDialog(self, _("Board has a wrong firmware.\nPlease select your Board\nand press Upload Firmware"), Error.str(result), wx.OK|wx.ICON_INFORMATION)
				dlg.ShowModal()
				dlg.Destroy()
				self.updateStatus(False)
				self.GetParent().parent.onPreferences(None)
			elif result is Error.BoardNotConnected:
				dlg = wx.MessageDialog(self, _("Board is not connected.\nPlease connect your board\nand select a valid Serial Name"), Error.str(result), wx.OK|wx.ICON_INFORMATION)
				dlg.ShowModal()
				dlg.Destroy()
				self.updateStatus(False)
				self.GetParent().parent.onPreferences(None)
			elif result is Error.CameraNotConnected:
				dlg = wx.MessageDialog(self, _("Please plug your camera. You have to restart the application to make the changes effective."), Error.str(result), wx.OK|wx.ICON_ERROR)
				dlg.ShowModal()
				dlg.Destroy()
				self.GetParent().parent.Close(True)
			elif result is Error.WrongCamera:
				dlg = wx.MessageDialog(self, _("You probably have selected a wrong camera.\nPlease select other Camera Id"), Error.str(result), wx.OK|wx.ICON_INFORMATION)
				dlg.ShowModal()
				dlg.Destroy()
				self.updateStatus(False)
				self.GetParent().parent.onPreferences(None)
			elif result is Error.InvalidVideo:
				dlg = wx.MessageDialog(self, _("Unplug and plug your camera USB cable.\nYou have to relaunch the wizard to make the changes effective"), Error.str(result), wx.OK|wx.ICON_ERROR)
				dlg.ShowModal()
				dlg.Destroy()
				self.GetParent().Close(True)

		if self.driver.isConnected:
			self.videoView.play()
			self.updateStatus(True)
			self.GetParent().parent.updateBoardCurrentProfile()
			self.GetParent().parent.updateCameraCurrentProfile()
			self.patternLabel.Enable()
			self.imageView.Enable()
			self.autoCheckButton.Enable()
			self.skipButton.Enable()
			self.enableNext = True
		else:
			self.connectButton.Enable()

		self.prevButton.Enable()
		del self.waitCursor

	def onAutoCheckButtonClicked(self, event):
		#-- Move motor
		self.driver.board.setSpeedMotor(200)
		self.driver.board.setRelativePosition(-180)
		self.driver.board.enableMotor()
		time.sleep(0.5)
		self.driver.board.moveMotor()
		self.driver.board.disableMotor()

		#-- Perform auto check
		self.laserTriangulation.setCallbacks(self.beforeAutoCheck,
											 lambda p: wx.CallAfter(self.progressAutoCheck,p),
											 lambda r: wx.CallAfter(self.afterAutoCheck,r))
		self.laserTriangulation.start()

	def beforeAutoCheck(self):
		self.autoCheckButton.Disable()
		self.prevButton.Disable()
		self.skipButton.Disable()
		self.nextButton.Disable()
		self.enableNext = False
		self.gauge.SetValue(30)
		self.resultLabel.Hide()
		self.gauge.Show()
		self.Layout()

	def progressAutoCheck(self, progress):
		self.gauge.SetValue(30 + 0.7*progress)

	def afterAutoCheck(self, response):
		ret, result = response

		if ret:
			self.resultLabel.SetLabel("All OK. Please press next to continue")
		else:
			self.resultLabel.SetLabel("Error in Auto check. Please try again")

		if ret:
			self.skipButton.Disable()
			self.nextButton.Enable()
		else:
			self.skipButton.Enable()
			self.nextButton.Disable()

		self.enableNext = True
		self.gauge.Hide()
		self.resultLabel.Show()
		self.autoCheckButton.Enable()
		self.prevButton.Enable()
		self.Layout()

	def performAutoCheck(self):
		self.driver.board.setLeftLaserOn()
		self.driver.board.setRightLaserOn()
		self.driver.board.enableMotor()
		time.sleep(0.2)
		wx.CallAfter(lambda: self.gauge.SetValue(10))

		self.driver.board.setSpeedMotor(150)
		self.driver.board.setRelativePosition(-100)
		self.driver.board.moveMotor()
		wx.CallAfter(lambda: self.gauge.SetValue(40))

		ret = True #self.laserTriangulation.start() TODO: move autocheck to Engine
		wx.CallAfter(lambda: self.gauge.SetValue(80))

		self.driver.board.setSpeedMotor(150)
		self.driver.board.setRelativePosition(90)
		self.driver.board.moveMotor()
		wx.CallAfter(lambda: self.gauge.SetValue(90))

		self.driver.board.disableMotor()
		self.driver.board.setLeftLaserOff()
		self.driver.board.setRightLaserOff()
		wx.CallAfter(lambda: self.gauge.SetValue(100))

		#-- Result: TODO
		#result = False
		#if ret is None:
		#	wx.CallAfter(lambda: self.resultLabel.SetLabel("Error: please check motor and pattern and try again"))
		#elif 0 in ret[1][0] or 0 in ret[1][1]:
		#	wx.CallAfter(lambda: self.resultLabel.SetLabel("Error in lasers: please connect the lasers and try again"))
		#else:
		result = True
		wx.CallAfter(lambda: self.afterAutoCheck(result))

	def updateStatus(self, status):
		if status:
			if profile.getPreference('workbench') != 'calibration':
				profile.putPreference('workbench', 'calibration')
				self.GetParent().parent.workbenchUpdate(False)
			self.videoView.play()
			self.connectButton.Disable()
			self.autoCheckButton.Enable()
		else:
			self.videoView.stop()
			self.connectButton.Enable()
			self.autoCheckButton.Disable()