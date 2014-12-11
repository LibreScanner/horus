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

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v2 http://www.gnu.org/licenses/gpl.html"

import wx._core
import time

from horus.gui.util.imageView import ImageView

from horus.gui.wizard.wizardPage import WizardPage

import horus.util.error as Error
from horus.util import profile, resources

from horus.engine.driver import Driver
from horus.engine import calibration


class CalibrationPage(WizardPage):
	def __init__(self, parent, buttonPrevCallback=None, buttonNextCallback=None):
		WizardPage.__init__(self, parent,
							title=_("Calibration"),
							buttonPrevCallback=buttonPrevCallback,
							buttonNextCallback=buttonNextCallback)

		self.driver = Driver.Instance()
		self.cameraIntrinsics = calibration.CameraIntrinsics.Instance()
		self.laserTriangulation = calibration.LaserTriangulation.Instance()
		self.platformExtrinsics = calibration.PlatformExtrinsics.Instance()

		#TODO: use dictionaries

		value = profile.getProfileSettingInteger('exposure_calibration')
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
		self.imageView.setImage(wx.Image(resources.getPathForImage("pattern-position-right.jpg")))
		self.calibrateButton = wx.Button(self.panel, label=_("Calibrate"))
		self.cancelButton = wx.Button(self.panel, label=_("Cancel"))
		self.gauge = wx.Gauge(self.panel, range=100, size=(-1, 30))
		self.resultLabel = wx.StaticText(self.panel, label=_("All OK. Please press next to continue"), size=(-1, 30))

		self.cancelButton.Disable()
		self.resultLabel.Hide()
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
		vbox.Add(self.resultLabel, 0, wx.ALL|wx.CENTER, 5)
		vbox.Add(self.gauge, 0, wx.ALL|wx.EXPAND, 5)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.cancelButton, 1, wx.ALL|wx.EXPAND, 5)
		hbox.Add(self.calibrateButton, 1, wx.ALL|wx.EXPAND, 5)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
		self.panel.SetSizer(vbox)

		self.Layout()

		self.exposureComboBox.Bind(wx.EVT_COMBOBOX, self.onExposureComboBoxChanged)
		self.calibrateButton.Bind(wx.EVT_BUTTON, self.onCalibrationButtonClicked)
		self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButtonClicked)
		self.Bind(wx.EVT_SHOW, self.onShow)

		self.videoView.setMilliseconds(50)
		self.videoView.setCallback(self.getFrame)
		self.updateStatus(self.driver.isConnected)

	def onShow(self, event):
		if event.GetShow():
			self.skipButton.Enable()
			self.nextButton.Disable()
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

	def onExposureComboBoxChanged(self, event):
		value = event.GetEventObject().GetValue()
		if value ==_("High"):
			value = 250
		elif value ==_("Medium"):
			value = 150
		elif value ==_("Low"):
			value = 80
		profile.putProfileSetting('exposure_calibration', value)
		self.driver.camera.setExposure(value)

	def onCalibrationButtonClicked(self, event):
		self.laserTriangulation.setCallbacks(self.beforeCalibration,
											 lambda p: wx.CallAfter(self.progressLaserCalibration,p),
											 lambda r: wx.CallAfter(self.afterLaserCalibration,r))
		self.laserTriangulation.start()

	def onCancelButtonClicked(self, event):
		self.resultLabel.SetLabel("Calibration canceled. To try again press \"Calibrate\"")
		self.platformExtrinsics.cancel()
		self.laserTriangulation.cancel()
		self.skipButton.Enable()
		self.onFinishCalibration()

	def beforeCalibration(self):
		self.calibrateButton.Disable()
		self.cancelButton.Enable()
		self.prevButton.Disable()
		self.skipButton.Disable()
		self.nextButton.Disable()
		self.enableNext = False
		self.gauge.SetValue(0)
		self.resultLabel.Hide()
		self.gauge.Show()
		self.Layout()
		self.waitCursor = wx.BusyCursor()

	def progressLaserCalibration(self, progress):
		self.gauge.SetValue(progress*0.7)

	def afterLaserCalibration(self, response):
		ret, result = response

		if ret:
			profile.putProfileSettingNumpy('laser_coordinates', result[1])
			profile.putProfileSettingNumpy('laser_origin', result[0][0])
			profile.putProfileSettingNumpy('laser_normal', result[0][1])
			self.platformExtrinsics.setCallbacks(None,
												 lambda p: wx.CallAfter(self.progressPlatformCalibration,p),
												 lambda r: wx.CallAfter(self.afterPlatformCalibration,r))
			self.platformExtrinsics.start()
		else:
			if result == Error.CalibrationError:
				self.resultLabel.SetLabel("Error in lasers: please connect the lasers and try again")
				dlg = wx.MessageDialog(self, _("Laser Calibration failed. Please try again"), Error.str(result), wx.OK|wx.ICON_ERROR)
				dlg.ShowModal()
				dlg.Destroy()
				self.skipButton.Enable()
				self.onFinishCalibration()

	def progressPlatformCalibration(self, progress):
		self.gauge.SetValue(70 + progress*0.3)	

	def afterPlatformCalibration(self, response):
		ret, result = response
		
		if ret:
			profile.putProfileSettingNumpy('rotation_matrix', result[0])
			profile.putProfileSettingNumpy('translation_vector', result[1])
		else:
			if result == Error.CalibrationError:
				self.resultLabel.SetLabel("Error in pattern: please check the pattern and try again")
				dlg = wx.MessageDialog(self, _("Platform Calibration failed. Please try again"), Error.str(result), wx.OK|wx.ICON_ERROR)
				dlg.ShowModal()
				dlg.Destroy()

		if ret:
			self.skipButton.Disable()
			self.nextButton.Enable()
		else:
			self.skipButton.Enable()
			self.nextButton.Disable()

		self.onFinishCalibration()

	def onFinishCalibration(self):
		self.enableNext = True
		self.gauge.Hide()
		self.resultLabel.Show()
		self.calibrateButton.Enable()
		self.cancelButton.Disable()
		self.prevButton.Enable()
		self.Layout()
		if hasattr(self, 'waitCursor'):
			del self.waitCursor

	def updateStatus(self, status):
		if status:
			if profile.getPreference('workbench') != 'calibration':
				profile.putPreference('workbench', 'calibration')
				self.GetParent().parent.workbenchUpdate(False)
			self.videoView.play()
			self.calibrateButton.Enable()
		else:
			self.videoView.stop()
			self.calibrateButton.Disable()