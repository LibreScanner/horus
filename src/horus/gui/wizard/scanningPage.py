# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.gui.wizard.wizardPage import WizardPage

from horus.util import profile

from horus.engine.driver import Driver
from horus.engine.scan import PointCloudGenerator

class ScanningPage(WizardPage):
	def __init__(self, parent, buttonPrevCallback=None, buttonNextCallback=None):
		WizardPage.__init__(self, parent,
							title=_("Scanning"),
							buttonPrevCallback=buttonPrevCallback,
							buttonNextCallback=buttonNextCallback)

		self.driver = Driver.Instance()
		self.pcg = PointCloudGenerator.Instance()

		value = abs(float(profile.getProfileSetting('step_degrees_scanning')))
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

		_choices = []
		choices = profile.getProfileSettingObject('use_laser').getType()
		for i in choices:
			_choices.append(_(i))
		self.laserDict = dict(zip(_choices, choices))
		self.laserLabel = wx.StaticText(self.panel, label=_("Laser"))
		useLaser = profile.getProfileSettingObject('use_laser').getType()
		self.laserComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
										value=_(profile.getProfileSetting('use_laser')),
										choices=_choices,
										style=wx.CB_READONLY)

		_choices = []
		choices = profile.getProfileSettingObject('scan_type').getType()
		for i in choices:
			_choices.append(_(i))
		self.scanTypeDict = dict(zip(_choices, choices))
		self.scanTypeLabel = wx.StaticText(self.panel, label=_('Scan'))
		scanType = profile.getProfileSettingObject('scan_type').getType()
		self.scanTypeComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
											value=_(profile.getProfileSetting('scan_type')),
											choices=_choices,
											style=wx.CB_READONLY)

		self.skipButton.Hide()

		#-- Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.resolutionLabel, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 18)
		hbox.Add(self.resolutionComboBox, 1, wx.ALL^wx.BOTTOM|wx.EXPAND, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 5)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.laserLabel, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 18)
		hbox.Add(self.laserComboBox, 1, wx.ALL^wx.BOTTOM|wx.EXPAND, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 5)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.scanTypeLabel, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 18)
		hbox.Add(self.scanTypeComboBox, 1, wx.ALL^wx.BOTTOM|wx.EXPAND, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 5)
		self.panel.SetSizer(vbox)
		self.Layout()

		self.resolutionComboBox.Bind(wx.EVT_COMBOBOX, self.onResolutionComboBoxChanged)
		self.laserComboBox.Bind(wx.EVT_COMBOBOX, self.onLaserComboBoxChanged)
		self.scanTypeComboBox.Bind(wx.EVT_COMBOBOX, self.onScanTypeComboBoxChanged)
		self.Bind(wx.EVT_SHOW, self.onShow)

		self.videoView.setMilliseconds(20)
		self.videoView.setCallback(self.getFrame)

	def onShow(self, event):
		if event.GetShow():
			self.updateStatus(self.driver.is_connected)
		else:
			try:
				self.videoView.stop()
			except:
				pass

	def onResolutionComboBoxChanged(self, event):
		value = event.GetEventObject().GetValue()
		if value ==_("High"):
			value = -0.45
		elif value ==_("Medium"):
			value = -0.9
		elif value ==_("Low"):
			value = -1.8

		profile.putProfileSetting('step_degrees_scanning', value)
		self.pcg.setDegrees(value)

	def onLaserComboBoxChanged(self, event):
		value = self.laserDict[event.GetEventObject().GetValue()]
		profile.putProfileSetting('use_laser', value)
		useLeft = value == 'Left' or value == 'Both'
		useRight = value == 'Right' or value == 'Both'
		if useLeft:
			self.driver.board.left_laser_on()
		else:
			self.driver.board.left_laser_off()

		if useRight:
			self.driver.board.right_laser_on()
		else:
			self.driver.board.right_laser_off()
		self.pcg.setUseLaser(useLeft, useRight)

	def onScanTypeComboBoxChanged(self, event):
		value = self.scanTypeDict[event.GetEventObject().GetValue()]
		profile.putProfileSetting('scan_type', value)
		if value == 'Simple Scan':
			self.driver.camera.set_exposure(profile.getProfileSettingInteger('laser_exposure_scanning'))
		elif value == 'Texture Scan':
			self.driver.camera.set_exposure(profile.getProfileSettingInteger('color_exposure_scanning'))

	def getFrame(self):
		frame = self.driver.camera.capture_image()
		return frame

	def updateStatus(self, status):
		if status:
			profile.putPreference('workbench', 'Scanning workbench')
			self.GetParent().parent.workbenchUpdate(False)
			self.videoView.play()
			value = profile.getProfileSetting('use_laser')
			if value == 'Left':
				self.driver.board.left_laser_on()
				self.driver.board.right_laser_off()
			elif value == 'Right':
				self.driver.board.left_laser_off()
				self.driver.board.right_laser_on()
			elif value == 'Both':
				self.driver.board.left_laser_on()
				self.driver.board.right_laser_on()
		else:
			self.videoView.stop()