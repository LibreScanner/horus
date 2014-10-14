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

from horus.gui.wizard.wizardPage import *

from horus.engine.scanner import *

class ScanningPage(WizardPage):
	def __init__(self, parent, buttonPrevCallback=None, buttonNextCallback=None):
		WizardPage.__init__(self, parent,
							title=_("Scanning"),
							buttonLeftCallback=buttonPrevCallback,
							buttonRightCallback=buttonNextCallback)

		self.scanner = Scanner.Instance()

		#TODO: use dictionaries

		value = getProfileSetting('exposure_scanning')
		if value > 200:
			value = _("High")
		elif value > 100:
			value = _("Medium")
		else:
			value = _("Low")
		self.luminosityLabel = wx.StaticText(self.panel, label=_("Luminosity"))
		self.luminosityComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
											value=value,
											choices=[_("High"), _("Medium"), _("Low")],
											style=wx.CB_READONLY)

		value = abs(float(getProfileSetting('step_degrees_scanning')))
		if value > 1.35:
			value = _("Low")
		elif value > 0.625:
			value = _("Medium")
		else:
			value = _("High")
		self.resolutionLabel = wx.StaticText(self.panel, label=_("Resolution"))
		self.resolutionComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
												value=value,
												choices=[_("High"), _("Medium"), _("Low")],
												style=wx.CB_READONLY)

		value = getProfileSetting('use_laser')
		if value ==_("Use Left Laser"):
			self.scanner.device.setLeftLaserOn()
			self.scanner.device.setRightLaserOff()
		elif value ==_("Use Right Laser"):
			self.scanner.device.setLeftLaserOff()
			self.scanner.device.setRightLaserOn()
		elif value ==_("Use Both Laser"):
			self.scanner.device.setLeftLaserOn()
			self.scanner.device.setRightLaserOn()
		self.laserLabel = wx.StaticText(self.panel, label=_("Laser"))
		self.laserComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
										value=value,
										choices=[_("Use Left Laser"), _("Use Right Laser"), _("Use Both Laser")],
										style=wx.CB_READONLY)

		self.textureLabel = wx.StaticText(self.panel, label=_("Texture"))
		self.textureComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
											value=_("Yes"),
											choices=[_("Yes"), _("No")],
											style=wx.CB_READONLY)

		self.textureLabel.Disable()
		self.textureComboBox.Disable()

		#-- Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.luminosityLabel, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 18)
		hbox.Add(self.luminosityComboBox, 1, wx.ALL^wx.BOTTOM|wx.EXPAND, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 5)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.resolutionLabel, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 18)
		hbox.Add(self.resolutionComboBox, 1, wx.ALL^wx.BOTTOM|wx.EXPAND, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 5)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.laserLabel, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 18)
		hbox.Add(self.laserComboBox, 1, wx.ALL^wx.BOTTOM|wx.EXPAND, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 5)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.textureLabel, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 18)
		hbox.Add(self.textureComboBox, 1, wx.ALL^wx.BOTTOM|wx.EXPAND, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 5)
		self.panel.SetSizer(vbox)
		self.Layout()

		self.luminosityComboBox.Bind(wx.EVT_COMBOBOX, self.onLuminosityComboBoxChanged)
		self.resolutionComboBox.Bind(wx.EVT_COMBOBOX, self.onResolutionComboBoxChanged)
		self.laserComboBox.Bind(wx.EVT_COMBOBOX, self.onLaserComboBoxChanged)
		self.Bind(wx.EVT_SHOW, self.onShow)

		self.videoView.setCallback(self.getFrame)

	def onShow(self, event):
		if event.GetShow():
			self.updateStatus(self.scanner.isConnected)
		else:
			try:
				self.videoView.stop()
			except:
				pass

	def onLuminosityComboBoxChanged(self, event):
		value = event.GetEventObject().GetValue()
		if value ==_("High"):
			value = 250
		elif value ==_("Medium"):
			value = 150
		elif value ==_("Low"):
			value = 80
		putProfileSetting('exposure_scanning', value)
		self.scanner.camera.setExposure(value)

	def onResolutionComboBoxChanged(self, event):
		value = event.GetEventObject().GetValue()
		if value ==_("High"):
			value = -0.45
		elif value ==_("Medium"):
			value = -0.9
		elif value ==_("Low"):
			value = -1.8
		putProfileSetting('step_degrees_scanning', value)

	def onLaserComboBoxChanged(self, event):
		value = event.GetEventObject().GetValue()
		putProfileSetting('use_laser', value)
		if value ==_("Use Left Laser"):
			self.scanner.device.setLeftLaserOn()
			self.scanner.device.setRightLaserOff()
		elif value ==_("Use Right Laser"):
			self.scanner.device.setLeftLaserOff()
			self.scanner.device.setRightLaserOn()
		elif value ==_("Use Both Laser"):
			self.scanner.device.setLeftLaserOn()
			self.scanner.device.setRightLaserOn()
		self.scanner.core.setUseLaser(value==_("Use Left Laser"), value==_("Use Right Laser"))

	def getFrame(self):
		frame = self.scanner.camera.captureImage()
		return frame

	def updateStatus(self, status):
		if status:
			putPreference('workbench', 'scanning')
			self.GetParent().GetParent().parent.workbenchUpdate()
			self.videoView.play()
		else:
			self.videoView.stop()