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
import time
import threading

from horus.gui.util.imageView import *

from horus.gui.wizard.wizardPage import *

from horus.engine.scanner import *
from horus.engine.calibration import *

class ConnectionPage(WizardPage):
	def __init__(self, parent, buttonPrevCallback=None, buttonNextCallback=None):
		WizardPage.__init__(self, parent,
							title=_("Connection"),
							buttonPrevCallback=buttonPrevCallback,
							buttonNextCallback=buttonNextCallback)

		self.scanner = Scanner.Instance()
		self.calibration = Calibration.Instance()

		self.connectButton = wx.Button(self.panel, label=_("Connect"))
		self.patternLabel = wx.StaticText(self.panel, label=_("Put the pattern on the platform and press \"Auto check\""))
		self.imageView = ImageView(self.panel)
		self.imageView.setImage(wx.Image(getPathForImage("pattern-position-left.jpg")))
		self.checkButton = wx.Button(self.panel, label=_("Auto check"))
		self.gauge = wx.Gauge(self.panel, range=100, size=(-1, 30))
		self.space = wx.Panel(self.panel, size=(-1, 30))
		self.resultLabel = wx.StaticText(self.panel, label=_("All OK. Please press next to continue"), size=(-1, 30))

		self.connectButton.Enable()
		self.patternLabel.Disable()
		self.imageView.Disable()
		self.checkButton.Disable()
		self.resultLabel.Hide()
		self.gauge.Hide()
		self.skipButton.Disable()
		self.nextButton.Disable()
		self.enableNext = False

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.connectButton, 0, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.patternLabel, 0, wx.ALL|wx.CENTER, 5)
		vbox.Add(self.imageView, 1, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.checkButton, 0, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.resultLabel, 0, wx.ALL|wx.CENTER, 5)
		vbox.Add(self.gauge, 0, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.space, 0, wx.ALL|wx.EXPAND, 5)
		self.panel.SetSizer(vbox)

		self.Layout()

		self.connectButton.Bind(wx.EVT_BUTTON, self.onConnectButtonClicked)
		self.checkButton.Bind(wx.EVT_BUTTON, self.onCheckButtonClicked)
		self.Bind(wx.EVT_SHOW, self.onShow)

		self.videoView.setCallback(self.getFrame)
		self.updateStatus(self.scanner.isConnected)

	def onShow(self, event):
		if event.GetShow():
			self.updateStatus(self.scanner.isConnected)
		else:
			try:
				self.videoView.stop()
			except:
				pass

	def onConnectButtonClicked(self, event):
		self.connectButton.Disable()
		try:
			self.scanner.connect()
		except WrongFirmware as e:
			dlg = wx.MessageDialog(self, _("Board has a wrong firmware.\nPlease select your Board\nand press Upload Firmware"), _("Wrong firmware"), wx.OK|wx.ICON_INFORMATION)
			result = dlg.ShowModal() == wx.ID_OK
			dlg.Destroy()
			self.scanner.disconnect()
			self.updateStatus(False)
			self.GetParent().parent.onPreferences(None)
		except DeviceNotConnected as e:
			dlg = wx.MessageDialog(self, _("Board is not connected.\nPlease connect your board\nand select a valid Serial Name"), _("Device not connected"), wx.OK|wx.ICON_INFORMATION)
			result = dlg.ShowModal() == wx.ID_OK
			dlg.Destroy()
			self.scanner.disconnect()
			self.updateStatus(False)
			self.GetParent().parent.onPreferences(None)
		except CameraNotConnected as e:
			dlg = wx.MessageDialog(self, _("Please plug your camera. You have to restart the application to make the changes effective"), _("Camera not connected"), wx.OK|wx.ICON_ERROR)
			result = dlg.ShowModal() == wx.ID_OK
			dlg.Destroy()
			self.scanner.disconnect()
			self.GetParent().Close()
			self.GetParent().parent.Close(True)
		except WrongCamera as e:
			dlg = wx.MessageDialog(self, _("You probably have selected a wrong camera.\nPlease select other Camera Id"), _("Wrong camera"), wx.OK|wx.ICON_INFORMATION)
			result = dlg.ShowModal() == wx.ID_OK
			dlg.Destroy()
			self.scanner.disconnect()
			self.updateStatus(False)
			self.GetParent().parent.onPreferences(None)
		except InvalidVideo as e:
			dlg = wx.MessageDialog(self, _("Unplug and plug your camera USB cable. You have to restart the application to make the changes effective"), _("Camera Error"), wx.OK|wx.ICON_ERROR)
			result = dlg.ShowModal() == wx.ID_OK
			dlg.Destroy()
			self.scanner.disconnect()
			self.GetParent().Close()
			self.GetParent().parent.Close(True)
		else:		
			if self.scanner.isConnected:
				self.videoView.play()
				self.updateStatus(True)
				self.GetParent().parent.updateDeviceCurrentProfile()
				self.GetParent().parent.updateCameraCurrentProfile()
				#self.GetParent().parent.updateCoreCurrentProfile()
				self.patternLabel.Enable()
				self.imageView.Enable()
				self.checkButton.Enable()
				self.skipButton.Enable()
				self.enableNext = True
		if not self.scanner.isConnected:
			self.connectButton.Enable()

	def onCheckButtonClicked(self, event):
		self.beforeAutoCheck()
		thread = threading.Thread(target=self.performAutoCheck).start()

	def beforeAutoCheck(self):
		self.videoView.setMilliseconds(20)
		self.checkButton.Disable()
		self.prevButton.Disable()
		self.skipButton.Disable()
		self.nextButton.Disable()
		self.enableNext = False
		self.gauge.SetValue(0)
		self.resultLabel.Hide()
		self.gauge.Show()
		self.space.Hide()
		self.Layout()

	def afterAutoCheck(self, result):
		self.videoView.setMilliseconds(1)
		if result:
			self.skipButton.Disable()
			self.nextButton.Enable()
		else:
			self.skipButton.Enable()
			self.nextButton.Disable()
		self.enableNext = True
		self.gauge.Hide()
		self.resultLabel.Show()
		self.checkButton.Enable()
		self.prevButton.Enable()
		self.Layout()

	def performAutoCheck(self):
		self.scanner.device.setLeftLaserOn()
		self.scanner.device.setRightLaserOn()
		self.scanner.device.enable()
		time.sleep(0.2)
		wx.CallAfter(lambda: self.gauge.SetValue(10))

		self.scanner.device.setSpeedMotor(150)
		self.scanner.device.setRelativePosition(-100)
		self.scanner.device.setMoveMotor()
		wx.CallAfter(lambda: self.gauge.SetValue(40))

		ret = self.calibration.performLaserTriangulationCalibration()
		wx.CallAfter(lambda: self.gauge.SetValue(80))

		self.scanner.device.setSpeedMotor(150)
		self.scanner.device.setRelativePosition(90)
		self.scanner.device.setMoveMotor()
		wx.CallAfter(lambda: self.gauge.SetValue(90))

		self.scanner.device.disable()
		self.scanner.device.setLeftLaserOff()
		self.scanner.device.setRightLaserOff()
		wx.CallAfter(lambda: self.gauge.SetValue(100))

		#-- Result
		result = False
		if ret is None:
			wx.CallAfter(lambda: self.resultLabel.SetLabel("Error: please check motor and pattern and try again"))
		elif 0 in ret[1][0] or 0 in ret[1][1]:
			wx.CallAfter(lambda: self.resultLabel.SetLabel("Error in lasers: please connect the lasers and try again"))
		else:
			result = True
		wx.CallAfter(lambda: self.afterAutoCheck(result))

	def getFrame(self):
		return self.scanner.camera.captureImage()

	def updateStatus(self, status):
		if status:
			if getPreference('workbench') != 'calibration':
				putPreference('workbench', 'calibration')
				self.GetParent().parent.workbenchUpdate(False)
			self.videoView.play()
			self.connectButton.Disable()
			self.checkButton.Enable()
		else:
			self.videoView.stop()
			self.connectButton.Enable()
			self.checkButton.Disable()