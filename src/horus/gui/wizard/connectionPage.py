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

class ConnectionPage(WizardPage):
	def __init__(self, parent, buttonPrevCallback=None, buttonNextCallback=None):
		WizardPage.__init__(self, parent,
							title=_("Connection"),
							buttonLeftCallback=buttonPrevCallback,
							buttonRightCallback=buttonNextCallback)

		self.scanner = Scanner.Instance()

		self.connectButton = wx.Button(self.panel, label=_("Connect"))
		self.patternLabel = wx.StaticText(self.panel, label=_("Put the pattern on the platform and press \"Auto check\""))
		self.imageView = ImageView(self.panel)
		self.imageView.setImage(wx.Image(getPathForImage("pattern-position-left.jpg")))
		self.checkButton = wx.Button(self.panel, label=_("Auto check"))
		self.resultLabel = wx.StaticText(self.panel, label=_("All OK. Please press next to continue"))

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.connectButton, 0, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.patternLabel, 0, wx.ALL|wx.CENTER, 5)
		vbox.Add(self.imageView, 1, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.checkButton, 0, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.resultLabel, 0, wx.ALL|wx.CENTER, 5)
		self.panel.SetSizer(vbox)

		self.connectButton.Enable()
		self.patternLabel.Disable()
		self.imageView.Disable()
		self.checkButton.Disable()
		self.resultLabel.Disable()
		self.rightButton.Disable()

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
			self.GetParent().GetParent().GetParent().onPreferences(None)
		except DeviceNotConnected as e:
			self.GetParent().GetParent().GetParent().onPreferences(None)
		except CameraNotConnected as e:
			self.GetParent().GetParent().GetParent().onPreferences(None)
		except WrongCamera as e:
			dlg = wx.MessageDialog(self, _("You probably have selected a wrong camera. Please select other Camera Id"), _("Incorrect camera"), wx.OK|wx.ICON_INFORMATION)
			result = dlg.ShowModal() == wx.ID_OK
			dlg.Destroy()
			self.scanner.disconnect()
			self.updateStatus(False)
			self.GetParent().GetParent().GetParent().onPreferences(None)
		except InvalidVideo as e:
			dlg = wx.MessageDialog(self, _("Unplug and plug your camera USB cable. You have to restart the application to make the changes effective."), _("Camera Error"), wx.OK|wx.ICON_ERROR)
			result = dlg.ShowModal() == wx.ID_OK
			dlg.Destroy()
			self.scanner.disconnect()
			self.GetParent().GetParent().GetParent().Close(True)
		else:		
			if self.scanner.isConnected:
				self.videoView.play()
				self.GetParent().GetParent().GetParent().updateDeviceCurrentProfile()
				self.GetParent().GetParent().GetParent().updateCameraCurrentProfile()
				#self.GetParent().GetParent().GetParent().updateCoreCurrentProfile()
				self.patternLabel.Enable()
				self.imageView.Enable()
				self.checkButton.Enable()
			else:
				self.connectButton.Enable()

	def onCheckButtonClicked(self, event):
		self.checkButton.Disable()
		self.leftButton.Disable()
		threading.Thread(target=self.performAutoCheck).start()

	def performAutoCheck(self):
		self.scanner.device.setLeftLaserOn()
		self.scanner.device.setRightLaserOn()
		self.scanner.device.enable()
		time.sleep(0.2)
		self.scanner.device.setSpeedMotor(150)
		self.scanner.device.setRelativePosition(-180)
		self.scanner.device.setMoveMotor()
		self.scanner.device.setRelativePosition(180)
		self.scanner.device.setMoveMotor()
		self.scanner.device.disable()
		self.scanner.device.setLeftLaserOff()
		self.scanner.device.setRightLaserOff()
		wx.CallAfter(lambda: (self.resultLabel.Enable(), self.leftButton.Enable(), self.rightButton.Enable()))

	def getFrame(self):
		return self.scanner.camera.captureImage()

	def updateStatus(self, status):
		if status:
			putPreference('workbench', 'control')
			self.GetParent().GetParent().parent.workbenchUpdate()
			self.videoView.play()
			self.connectButton.Disable()
			self.checkButton.Enable()
		else:
			self.videoView.stop()
			self.connectButton.Enable()
			self.checkButton.Disable()