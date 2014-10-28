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
import numpy #TODO: move
import threading

from horus.gui.util.imageView import *

from horus.gui.wizard.wizardPage import *

from horus.engine.scanner import *
from horus.engine.calibration import *

class CalibrationPage(WizardPage):
	def __init__(self, parent, buttonPrevCallback=None, buttonNextCallback=None):
		WizardPage.__init__(self, parent,
							title=_("Calibration"),
							buttonPrevCallback=buttonPrevCallback,
							buttonNextCallback=buttonNextCallback)

		self.scanner = Scanner.Instance()
		self.calibration = Calibration.Instance()

		#TODO: use dictionaries

		value = getProfileSettingInteger('exposure_calibration')
		if value > 200:
			value = _("High")
		elif value > 100:
			value = _("Medium")
		else:
			value = _("Low")
		self.exposureLabel = wx.StaticText(self.panel, label=_("Luminosity"))
		self.exposureComboBox = wx.ComboBox(self.panel,
											value=value,
											choices=[_("High"), _("Medium"), _("Low")],
											style=wx.CB_READONLY)

		self.patternLabel = wx.StaticText(self.panel, label=_("Put the pattern on the platform and press \"Calibrate\""))
		self.imageView = ImageView(self.panel)
		self.imageView.setImage(wx.Image(getPathForImage("pattern-position-left.jpg")))
		self.calibrateButton = wx.Button(self.panel, label=_("Calibrate"))
		self.gauge = wx.Gauge(self.panel, range=100, size=(-1, 30))
		self.space = wx.Panel(self.panel, size=(-1, 30))
		self.resultLabel = wx.StaticText(self.panel, label=_("All OK. Please press next to continue"))

		self.resultLabel.Hide()
		self.gauge.Hide()
		self.skipButton.Enable()
		self.nextButton.Disable()

		#-- Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.exposureLabel, 0, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
		hbox.Add(self.exposureComboBox, 1, wx.TOP|wx.RIGHT|wx.EXPAND, 6)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
		vbox.Add(self.patternLabel, 0, wx.ALL|wx.CENTER, 5)
		vbox.Add(self.imageView, 1, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.calibrateButton, 0, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.resultLabel, 0, wx.ALL|wx.CENTER, 5)
		vbox.Add(self.gauge, 0, wx.ALL|wx.EXPAND, 5)
		vbox.Add(self.space, 0, wx.ALL|wx.EXPAND, 5)
		self.panel.SetSizer(vbox)

		self.Layout()

		self.exposureComboBox.Bind(wx.EVT_COMBOBOX, self.onExposureComboBoxChanged)
		self.calibrateButton.Bind(wx.EVT_BUTTON, self.onCalibrationButtonClicked)
		self.Bind(wx.EVT_SHOW, self.onShow)

		self.videoView.setMilliseconds(20)
		self.videoView.setCallback(self.getFrame)
		self.updateStatus(self.scanner.isConnected)

	def onShow(self, event):
		if event.GetShow():
			self.skipButton.Enable()
			self.nextButton.Disable()
			self.updateStatus(self.scanner.isConnected)
		else:
			try:
				self.videoView.stop()
			except:
				pass

	def onExposureComboBoxChanged(self, event):
		value = event.GetEventObject().GetValue()
		if value ==_("High"):
			value = 250
		elif value ==_("Medium"):
			value = 150
		elif value ==_("Low"):
			value = 80
		putProfileSetting('exposure_calibration', value)
		self.scanner.camera.setExposure(value)

	def onCalibrationButtonClicked(self, event):
		self.beforeCalibration()
		threading.Thread(target=self.performCalibration).start()

	def beforeCalibration(self):
		self.calibrateButton.Disable()
		self.prevButton.Disable()
		self.skipButton.Disable()
		self.nextButton.Disable()
		self.gauge.SetValue(0)
		self.resultLabel.Hide()
		self.gauge.Show()
		self.space.Hide()
		self.Layout()

	def afterCalibration(self, result):
		if result:
			self.skipButton.Disable()
			self.nextButton.Enable()
		else:
			self.skipButton.Enable()
			self.nextButton.Disable()
		self.gauge.Hide()
		self.resultLabel.Show()
		self.calibrateButton.Enable()
		self.prevButton.Enable()
		self.Layout()

	def performCalibration(self):
		wx.CallAfter(lambda: self.gauge.SetValue(10))

		retP = self.calibration.performPlatformExtrinsicsCalibration()
		wx.CallAfter(lambda: self.gauge.SetValue(70))

		ret = self.calibration.performLaserTriangulationCalibration()
		wx.CallAfter(lambda: self.gauge.SetValue(100))

		#-- Result
		result = False
		if retP is not None:
			if numpy.linalg.norm(retP[1]-[5,80,320]) > 1000:
				wx.CallAfter(lambda: self.resultLabel.SetLabel("Error in pattern: please check the pattern and try again"))
		if ret is not None:
			print ret[1], ret[0][0], ret[0][1]
			if 0 in ret[1][0] or 0 in ret[1][1]:
				wx.CallAfter(lambda: self.resultLabel.SetLabel("Error in lasers: please connect the lasers and try again"))
		if retP is None or ret is None:
			wx.CallAfter(lambda: self.resultLabel.SetLabel("Error: please check motor and pattern and try again"))
		else:
			result = True
			putProfileSettingNumpy('rotation_matrix', retP[0])
			putProfileSettingNumpy('translation_vector', retP[1])
			putProfileSettingNumpy('laser_coordinates', ret[1])
			putProfileSettingNumpy('laser_origin', ret[0][0])
			putProfileSettingNumpy('laser_normal', ret[0][1])
		wx.CallAfter(lambda: self.afterCalibration(result))

	def getFrame(self):
		frame = self.scanner.camera.captureImage()
		if frame is not None:
			retval, frame = self.calibration.detectChessboard(frame)
		return frame

	def updateStatus(self, status):
		if status:
			if getPreference('workbench') != 'calibration':
				putPreference('workbench', 'calibration')
				self.GetParent().parent.workbenchUpdate(False)
			self.videoView.play()
			self.calibrateButton.Enable()
		else:
			self.videoView.stop()
			self.calibrateButton.Disable()