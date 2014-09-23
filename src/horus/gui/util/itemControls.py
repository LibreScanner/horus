#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: September 2014                                                  #
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

from horus.util.profile import *

class ControlItem(wx.Control):
	def __init__(self, parent, name):
		wx.Control.__init__(self, parent)
		self.engineCallback = None
		self.appendUndoCallback = None
		self.releaseUndoCallback = None

		self.undoValues = []

		self.name = name
		self.setting = getProfileSettingObject(self.name)

	def isVisible(self):
		if getPreferenceBool('basic_mode'):
			return self.setting.getCategory() is 'basic'
		else:
			return self.setting.getCategory() is 'basic' or self.setting.getCategory() is 'advanced'

class Slider(ControlItem):
	def __init__(self, parent, name):
		""" """
		ControlItem.__init__(self, parent, name)

		self.flagFirstMove = True

		#-- Elements
		self.label = wx.StaticText(self, label=self.setting.getLabel())
		self.slider = wx.Slider(self, wx.ID_ANY,
								getProfileSettingInteger(self.name),
								int(eval(self.setting.getMinValue(), {}, {})),
								int(eval(self.setting.getMaxValue(), {}, {})),
								size=(150,-1),
								style=wx.SL_LABELS)

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.label, 0, wx.ALL^wx.BOTTOM, 18)
		hbox.Add(self.slider, 0, wx.ALL, 0)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.slider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.onSliderReleased)
		self.slider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onSliderTracked)

	def setEngineCallback(self, engineCallback=None):
		self.engineCallback = engineCallback

	def setUndoCallbacks(self, appendUndoCallback=None, releaseUndoCallback=None):
		self.appendUndoCallback = appendUndoCallback
		self.releaseUndoCallback = releaseUndoCallback

	def onSliderReleased(self, event):
		self.flagFirstMove = True
		if self.releaseUndoCallback is not None:
			self.releaseUndoCallback()

	def onSliderTracked(self, event):
		if self.flagFirstMove:
			value = getProfileSettingInteger(self.name)
			self.undoValues.append(value)
			if self.appendUndoCallback is not None:
				self.appendUndoCallback(self)
			self.flagFirstMove = False
		value = self.slider.GetValue()
		putProfileSetting(self.name, value)
		self._updateEngine(value)

	def updateProfile(self):
		if hasattr(self,'slider'):
			value = getProfileSettingInteger(self.name)
			self.update(value)

	def update(self, value):
		if self.isVisible():
			self.Show()
			self.slider.SetValue(value)
			self._updateEngine(value)
		else:
			self.Hide()

	def _updateEngine(self, value):
		if self.engineCallback is not None:
			self.engineCallback(value)

	def undo(self):
		if len(self.undoValues) > 0:
			value = self.undoValues.pop()
			putProfileSetting(self.name, value)
			self.update(value)

	def resetProfile(self):
		resetProfileSetting(self.name)
		del self.undoValues[:]
		self.updateProfile()


class ComboBox(ControlItem):
	def __init__(self, parent, name):
		""" """
		ControlItem.__init__(self, parent, name)

		#-- Elements
		self.label = wx.StaticText(self, label=self.setting.getLabel())
		self.combo = wx.ComboBox(self, wx.ID_ANY,
								 value=getProfileSetting(self.name),
								 choices=self.setting.getType(),
								 size=(150, -1),
								 style=wx.CB_READONLY)

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.label, 0, wx.ALL, 18)
		hbox.Add(self.combo, 0, wx.TOP, 12)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.combo.Bind(wx.EVT_COMBOBOX, self.onComboBoxChanged)

	def setEngineCallback(self, engineCallback=None):
		self.engineCallback = engineCallback

	def setUndoCallbacks(self, appendUndoCallback=None, releaseUndoCallback=None):
		self.appendUndoCallback = appendUndoCallback
		self.releaseUndoCallback = releaseUndoCallback

	def onComboBoxChanged(self, event):
		self.undoValues.append(getProfileSetting(self.name))
		value = self.combo.GetValue()
		putProfileSetting(self.name, value)
		self._updateEngine(value)
		if self.appendUndoCallback is not None:
			self.appendUndoCallback(self)
		if self.releaseUndoCallback is not None:
			self.releaseUndoCallback()

	def updateProfile(self):
		if hasattr(self,'combo'):
			value = getProfileSetting(self.name)
			self.update(value)

	def update(self, value):
		if self.isVisible():
			self.Show()
			self.combo.SetValue(value)
			self._updateEngine(value)
		else:
			self.Hide()

	def _updateEngine(self, value):
		if self.engineCallback is not None:
			self.engineCallback(value)

	def undo(self):
		if len(self.undoValues) > 0:
			value = self.undoValues.pop()
			putProfileSetting(self.name, value)
			self.update(value)

	def resetProfile(self):
		resetProfileSetting(self.name)
		del self.undoValues[:]
		self.updateProfile()


class CheckBox(ControlItem):
	def __init__(self, parent, name):
		""" """
		ControlItem.__init__(self, parent, name)

		#-- Elements
		self.checkbox = wx.CheckBox(self, label=self.setting.getLabel())

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.checkbox, 0, wx.ALL^wx.BOTTOM, 18)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.checkbox.Bind(wx.EVT_CHECKBOX, self.onCheckBoxChanged)

	def setEngineCallback(self, engineCallback=None):
		self.engineCallback = engineCallback

	def setUndoCallbacks(self, appendUndoCallback=None, releaseUndoCallback=None):
		self.appendUndoCallback = appendUndoCallback
		self.releaseUndoCallback = releaseUndoCallback

	def onCheckBoxChanged(self, event):
		self.undoValues.append(getProfileSettingBool(self.name))
		value = self.checkbox.GetValue()
		putProfileSetting(self.name, value)
		self._updateEngine(value)
		if self.appendUndoCallback is not None:
			self.appendUndoCallback(self)
		if self.releaseUndoCallback is not None:
			self.releaseUndoCallback()

	def updateProfile(self):
		if hasattr(self,'checkbox'):
			value = getProfileSettingBool(self.name)
			self.update(value)

	def update(self, value):
		if self.isVisible():
			self.Show()
			self.checkbox.SetValue(value)
			self._updateEngine(value)
		else:
			self.Hide()

	def _updateEngine(self, value):
		if self.engineCallback is not None:
			self.engineCallback(value)

	def undo(self):
		if len(self.undoValues) > 0:
			value = self.undoValues.pop()
			putProfileSetting(self.name, value)
			self.update(value)

	def resetProfile(self):
		resetProfileSetting(self.name)
		del self.undoValues[:]
		self.updateProfile()