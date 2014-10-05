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

import os
import glob
import time

from horus.util.avrHelpers import AvrDude

from horus.util.profile import *
from horus.util.resources import *

class PreferencesDialog(wx.Dialog):
	def __init__(self, parent):
		super(PreferencesDialog, self).__init__(None, title=_("Preferences"))

		wx.EVT_CLOSE(self, self.onClose)

		self.main = parent

		#-- Graphic elements
		self.conParamsStaticText = wx.StaticText(self, -1, _("Connection Parameters"), style=wx.ALIGN_CENTRE)
		self.serialNameLabel = wx.StaticText(self, label=_("Serial Name"))
		self.serialNames = self.main.serialList()
		self.serialNameCombo = wx.ComboBox(self, choices=self.serialNames, size=(140,-1))
		self.cameraIdLabel = wx.StaticText(self, label=_("Camera Id"))
		self.cameraIdNames = self.main.videoList()
		self.cameraIdCombo = wx.ComboBox(self, choices=self.cameraIdNames, size=(143,-1))

		self.languageLabel = wx.StaticText(self, label=_("Language"))
		self.languages = [row[1] for row in getLanguageOptions()]
		self.languageCombo = wx.ComboBox(self, choices=self.languages, value=getPreference('language') , size=(110,-1))

		self.boardLabel = wx.StaticText(self, label=_("Board"))
		self.boards = getProfileSettingObject('board').getType()
		board = getProfileSetting('board')
		self.boardsCombo = wx.ComboBox(self, choices=self.boards, value=board , size=(110,-1))
		self.uploadFirmwareButton = wx.Button(self, -1, _("Upload Firmware"))
		self.clearEEPROMButton = wx.Button(self, -1, _("Clear EEPROM"))

		self.okButton = wx.Button(self, -1, _("Ok"))

		#-- Events
		self.serialNameCombo.Bind(wx.EVT_TEXT, self.onSerialNameTextChanged)
		self.cameraIdCombo.Bind(wx.EVT_TEXT, self.onCameraIdTextChanged)
		self.languageCombo.Bind(wx.EVT_COMBOBOX, self.onLanguageComboChanged)
		self.boardsCombo.Bind(wx.EVT_COMBOBOX, self.onBoardsComboChanged)
		self.uploadFirmwareButton.Bind(wx.EVT_BUTTON, self.onUploadFirmware)
		self.clearEEPROMButton.Bind(wx.EVT_BUTTON, self.onClearEEPROM)
		self.okButton.Bind(wx.EVT_BUTTON, lambda e: self.Close())

		#-- Fill data
		currentSerial = getProfileSetting('serial_name')
		if len(self.serialNames) > 0:
			if currentSerial not in self.serialNames:
				self.serialNameCombo.SetValue(self.serialNames[0])
			else:
				self.serialNameCombo.SetValue(currentSerial)

		currentVideoId = getProfileSetting('camera_id')
		if len(self.cameraIdNames) > 0:
			if currentVideoId not in self.cameraIdNames:
				self.cameraIdCombo.SetValue(self.cameraIdNames[0])
			else:
				self.cameraIdCombo.SetValue(currentVideoId)		

		#-- Call Events
		self.onSerialNameTextChanged(None)
		self.onCameraIdTextChanged(None)

		#-- Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		    
		vbox.Add(self.conParamsStaticText, 0, wx.ALL, 10)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.serialNameLabel, 0, wx.ALL^wx.RIGHT, 10)
		hbox.Add(self.serialNameCombo, 0, wx.ALL, 5)
		vbox.Add(hbox)
		hbox = wx.BoxSizer(wx.HORIZONTAL)   
		hbox.Add(self.cameraIdLabel, 0, wx.ALL, 10)
		hbox.Add(self.cameraIdCombo, 0, wx.ALL, 5)
		vbox.Add(hbox)

		vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL^wx.TOP, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.languageLabel, 0, wx.ALL, 10)
		hbox.Add(self.languageCombo, 0, wx.ALL, 5)
		vbox.Add(hbox)

		vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL^wx.TOP, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.boardLabel, 0, wx.ALL, 10)
		hbox.Add(self.boardsCombo, 0, wx.ALL, 5)
		vbox.Add(hbox)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.uploadFirmwareButton, 0, wx.ALL, 10)
		hbox.Add(self.clearEEPROMButton, 0, wx.ALL, 10)
		vbox.Add(hbox)

		vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL^wx.TOP, 5)

		vbox.Add(self.okButton, 0, wx.ALL, 10)

		self.SetSizer(vbox)
		self.Centre()

		self.Fit()

	def onSerialNameTextChanged(self, event):
		if len(self.serialNameCombo.GetValue()):
			putProfileSetting('serial_name', self.serialNameCombo.GetValue())

	def onCameraIdTextChanged(self, event):
		if len(self.cameraIdCombo.GetValue()) > 0:
			putProfileSetting('camera_id', self.cameraIdCombo.GetValue())

	def onBoardsComboChanged(self, event):
		putProfileSetting('board', self.boardsCombo.GetValue())
		self.main.updateScannerProfile()

	def onUploadFirmware(self, event):
		if self.boardsCombo.GetValue() == 'UNO':
			baudRate = 115200
			hexPath = getPathForFirmware("horus-fw-uno.hex")
		elif self.boardsCombo.GetValue() == 'BT-328':
			baudRate = 19200
			hexPath = getPathForFirmware("horus-fw-bt328.hex")
		self.loadFirmware(hexPath, baudRate)

	def onClearEEPROM(self, event):
		if self.boardsCombo.GetValue() == 'UNO':
			baudRate = 115200
		elif self.boardsCombo.GetValue() == 'BT-328':
			baudRate = 19200
		self.loadFirmware(getPathForFirmware("eeprom_clear.hex"), baudRate)

	def loadFirmware(self, hexPath, hexBaudRate):
		avr_dude = AvrDude(port=getProfileSetting('serial_name'), baud_rate=hexBaudRate)
		stdout, stderr = avr_dude.flash(hex_path=hexPath, extra_flags=["-D"])
		print stdout
		print stderr

	def onLanguageComboChanged(self, event):
		if getPreference('language') is not self.languageCombo.GetValue():
			putPreference('language', self.languageCombo.GetValue())
			setupLocalization(getPreference('language'))
			wx.MessageBox(_("You have to restart the application to make the changes effective."), 'Info', wx.OK | wx.ICON_INFORMATION)

	def onClose(self, e):
		self.Destroy()

