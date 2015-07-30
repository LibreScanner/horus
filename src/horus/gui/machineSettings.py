#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014-2015 Mundo Reader S.L.                             #
#                                                                       #
# Date: June, November 2014                                             #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>                    #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 2 of the License, or     #
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

__author__ = "Nicanor Romero Venier <nicanor.romerovenier@bq.com>"
__license__ = "GNU General Public License v2 http://www.gnu.org/licenses/gpl.html"

import wx._core
import threading

from horus.util import profile, resources
from horus.util.avrHelpers import AvrDude


class MachineSettingsDialog(wx.Dialog):
	def __init__(self, parent):
		super(MachineSettingsDialog, self).__init__(None, title=_("Machine Settings"))

		self.main = parent

		#-- Graphic elements
		self.platformShapeLabel = wx.StaticText(self, label=_("Platform Shape"))
		self.platformShapes = self.main.platformShapesList()
		self.platformShapeCombo = wx.ComboBox(self, choices=self.platformShapes, size=(170,-1), style=wx.CB_READONLY)

		self.dimensionsStaticText = wx.StaticText(self, label=_("Platform Dimensions"), style=wx.ALIGN_CENTRE)
		self.diameterLabel = wx.StaticText(self, label=_("Diameter"))
		self.diameterField = wx.TextCtrl(self, size=(170,-1))
		self.heightLabel = wx.StaticText(self, label=_("Height"))
		self.heightField = wx.TextCtrl(self, size=(170,-1))
		self.widthLabel = wx.StaticText(self, label=_("Width"))
		self.widthField = wx.TextCtrl(self, size=(170,-1))
		self.depthLabel = wx.StaticText(self, label=_("Depth"))
		self.depthField = wx.TextCtrl(self, size=(170,-1))

		self.machineModelLabel = wx.StaticText(self, label=_("Machine STL"))
		self.machineModelField = wx.TextCtrl(self, size=(200,-1))
		self.machineModelButton = wx.Button(self, label=_("Browse"))

		self.cancelButton = wx.Button(self, label=_("Cancel"))
		self.saveButton = wx.Button(self, label=_("Save"))
		self.defaultButton = wx.Button(self, label=_("Default"))

		#-- Events
		self.platformShapeCombo.Bind(wx.EVT_COMBOBOX, self.onPlatformShapeComboChanged)
		self.machineModelButton.Bind(wx.EVT_BUTTON, self.onMachineModelButton)
		self.saveButton.Bind(wx.EVT_BUTTON, self.onClose)
		self.Bind(wx.EVT_CLOSE, self.onClose)

		#-- Fill data

		#currentPlatformShape = profile.getProfileSetting('platfrom_shape')
		#self.platformShapeCombo.SetValue(currentPlatformShape)

		#-- Layout
		vbox = wx.BoxSizer(wx.VERTICAL)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.platformShapeLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		hbox.AddStretchSpacer()
		hbox.Add(self.platformShapeCombo, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 10)
		vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)

		vbox.Add(self.dimensionsStaticText, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 10)
		# Diameter
		diam_hbox = wx.BoxSizer(wx.HORIZONTAL)
		diam_hbox.Add(self.diameterLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		diam_hbox.AddStretchSpacer()
		diam_hbox.Add(self.diameterField, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		vbox.Add(diam_hbox, 0, wx.ALL|wx.EXPAND, 10)
		# Width
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.widthLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		hbox.AddStretchSpacer()
		hbox.Add(self.widthField, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 10)
		# Height
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.heightLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		hbox.AddStretchSpacer()
		hbox.Add(self.heightField, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		vbox.Add(hbox, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
		# Depth
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.depthLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		hbox.AddStretchSpacer()
		hbox.Add(self.depthField, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		vbox.Add(hbox, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
		vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)

		# Machine STL
		vbox.Add(self.machineModelLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 10)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.machineModelField, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		hbox.AddStretchSpacer()
		hbox.Add(self.machineModelButton, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 10)
		vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.cancelButton, 0, wx.ALL^wx.RIGHT, 10)
		hbox.Add(self.saveButton, 0, wx.ALL^wx.RIGHT, 10)
		hbox.Add(self.defaultButton, 0, wx.ALL, 10)
		vbox.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)

		self.SetSizer(vbox)

		self.Centre()
		self.Layout()
		self.Fit()

		#vbox.Hide(diam_hbox, recursive=True)
		#vbox.Show(diam_hbox, recursive=True)

	def onClose(self, event):
		self.EndModal(wx.ID_OK)
		self.Destroy()

	def onPlatformShapeComboChanged(self, event):
		if len(self.platformShapeCombo.GetValue()):
			profile.putProfileSetting('serial_name', self.platformShapeCombo.GetValue())

	def onBoardsComboChanged(self, event):
		profile.putProfileSetting('board', self.boardsCombo.GetValue())

	def onMachineModelButton(self, event):
		dlg = wx.FileDialog(self, message=_("Select binary file to load"), style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
		dlg.SetWildcard("Model files (*.stl)|*.stl")
		if dlg.ShowModal() == wx.ID_OK:
			self.machineModelPath = dlg.GetPath()
			self.machineModelField.SetValue(dlg.GetFilename())
		dlg.Destroy()

	def onUploadFirmware(self, event):
		if self.platformShapeCombo.GetValue() != '':
			self.beforeLoadFirmware()
			baudRate = self._getBaudRate(self.boardsCombo.GetValue())
			clearEEPROM = self.clearCheckBox.GetValue()
			threading.Thread(target=self.loadFirmware, args=(baudRate,clearEEPROM)).start()

	def _getBaudRate(self, value):
		if value == 'Arduino Uno':
			return 115200
		elif value == 'BT ATmega328':
			return 19200

	def loadFirmware(self, hexBaudRate, clearEEPROM):
		avr_dude = AvrDude(port=profile.getProfileSetting('serial_name'), baudRate=hexBaudRate)
		extraFlags = []
		if clearEEPROM:
			extraFlags = ["-D"]
		self.count = -50
		out = avr_dude.flash(extraFlags=extraFlags, hexPath=self.hexPath, callback=self.incrementProgress)
		if 'not in sync' in out or 'Invalid' in out:
			wx.CallAfter(self.wrongBoardMessage)
		wx.CallAfter(self.afterLoadFirmware)

	def incrementProgress(self):
		self.count += 1
		if self.count >= 0:
			wx.CallAfter(self.gauge.SetValue,self.count)

	def wrongBoardMessage(self):
		dlg = wx.MessageDialog(self, _("Probably you have selected the wrong board. Select other Board"), 'Wrong Board', wx.OK|wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()

	def beforeLoadFirmware(self):
		self.uploadFirmwareButton.Disable()
		self.clearCheckBox.Disable()
		self.boardsCombo.Disable()
		self.saveButton.Disable()
		self.gauge.SetValue(0)
		self.gauge.Show()
		self.waitCursor = wx.BusyCursor()
		self.Layout()
		self.Fit()

	def afterLoadFirmware(self):
		self.uploadFirmwareButton.Enable()
		self.clearCheckBox.Enable()
		self.boardsCombo.Enable()
		self.saveButton.Enable()
		self.gauge.Hide()
		del self.waitCursor
		self.Layout()
		self.Fit()

	def onLanguageComboChanged(self, event):
		if profile.getPreference('language') is not self.languageCombo.GetValue():
			profile.putPreference('language', self.languageCombo.GetValue())
			wx.MessageBox(_("You have to restart the application to make the changes effective."), 'Info', wx.OK | wx.ICON_INFORMATION)

	def onInvertMotor(self, event):
		profile.putProfileSetting('invert_motor', self.invertMotorCheckBox.GetValue())