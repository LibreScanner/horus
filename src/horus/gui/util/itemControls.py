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

		self.control = None

		self.name = name
		self.setting = getProfileSettingObject(self.name)

	def setEngineCallback(self, engineCallback=None):
		self.engineCallback = engineCallback

	def setUndoCallbacks(self, appendUndoCallback=None, releaseUndoCallback=None):
		self.appendUndoCallback = appendUndoCallback
		self.releaseUndoCallback = releaseUndoCallback

	def isVisible(self):
		if getPreferenceBool('basic_mode'):
			return self.setting.getCategory() is 'basic'
		else:
			return self.setting.getCategory() is 'basic' or self.setting.getCategory() is 'advanced'

	def update(self, value):
		if self.isVisible():
			self.Show()
			self.control.SetValue(value)
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


class Slider(ControlItem):
	def __init__(self, parent, name):
		""" """
		ControlItem.__init__(self, parent, name)

		self.flagFirstMove = True

		#-- Elements
		self.label = wx.StaticText(self, label=self.setting.getLabel())
		self.control = wx.Slider(self, wx.ID_ANY,
								 getProfileSettingInteger(self.name),
								 int(eval(self.setting.getMinValue(), {}, {})),
								 int(eval(self.setting.getMaxValue(), {}, {})),
								 size=(150,-1),
								 style=wx.SL_LABELS)

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.label, 0, wx.ALL^wx.BOTTOM, 18)
		hbox.Add(self.control, 0, wx.ALL, 0)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.control.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.onSliderReleased)
		self.control.Bind(wx.EVT_SCROLL_THUMBTRACK, self.onSliderTracked)

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
		value = self.control.GetValue()
		putProfileSetting(self.name, value)
		self._updateEngine(value)

	def updateProfile(self):
		if hasattr(self,'control'):
			value = getProfileSettingInteger(self.name)
			self.update(value)


class ComboBox(ControlItem):
	def __init__(self, parent, name):
		""" """
		ControlItem.__init__(self, parent, name)

		#-- Elements
		self.label = wx.StaticText(self, label=self.setting.getLabel())
		self.control = wx.ComboBox(self, wx.ID_ANY,
								   value=getProfileSetting(self.name),
								   choices=self.setting.getType(),
								   size=(150, -1),
								   style=wx.CB_READONLY)

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.label, 0, wx.ALL, 18)
		hbox.Add(self.control, 0, wx.TOP, 12)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.control.Bind(wx.EVT_COMBOBOX, self.onComboBoxChanged)

	def onComboBoxChanged(self, event):
		self.undoValues.append(getProfileSetting(self.name))
		value = self.control.GetValue()
		putProfileSetting(self.name, value)
		self._updateEngine(value)
		if self.appendUndoCallback is not None:
			self.appendUndoCallback(self)
		if self.releaseUndoCallback is not None:
			self.releaseUndoCallback()

	def updateProfile(self):
		if hasattr(self,'control'):
			value = getProfileSetting(self.name)
			self.update(value)


class CheckBox(ControlItem):
	def __init__(self, parent, name):
		""" """
		ControlItem.__init__(self, parent, name)

		#-- Elements
		self.control = wx.CheckBox(self, label=self.setting.getLabel())

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.control, 0, wx.ALL^wx.BOTTOM, 18)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.control.Bind(wx.EVT_CHECKBOX, self.onCheckBoxChanged)

	def onCheckBoxChanged(self, event):
		self.undoValues.append(getProfileSettingBool(self.name))
		value = self.control.GetValue()
		putProfileSetting(self.name, value)
		self._updateEngine(value)
		if self.appendUndoCallback is not None:
			self.appendUndoCallback(self)
		if self.releaseUndoCallback is not None:
			self.releaseUndoCallback()

	def updateProfile(self):
		if hasattr(self,'control'):
			value = getProfileSettingBool(self.name)
			self.update(value)

class RadioButton(ControlItem):
	def __init__(self, parent, name):
		""" """
		ControlItem.__init__(self, parent, name)

		#-- Elements
		self.control = wx.RadioButton(self, label=self.setting.getLabel())

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.control, 0, wx.ALL^wx.BOTTOM, 18)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.control.Bind(wx.EVT_RADIOBUTTON, self.onRadioButtonChanged)

	def onCheckBoxChanged(self, event):
		self.undoValues.append(getProfileSettingBool(self.name))
		value = self.control.GetValue()
		putProfileSetting(self.name, value)
		self._updateEngine(value)
		if self.appendUndoCallback is not None:
			self.appendUndoCallback(self)
		if self.releaseUndoCallback is not None:
			self.releaseUndoCallback()

	def updateProfile(self):
		if hasattr(self,'control'):
			value = getProfileSettingBool(self.name)
			self.update(value)

class TextBox(ControlItem):
	def __init__(self, parent, name):
		""" """
		ControlItem.__init__(self, parent, name)

		#-- Elements
		self.label = wx.StaticText(self, label=self.setting.getLabel())
		self.control = wx.TextCtrl(self)

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.label, 0, wx.ALL|wx.EXPAND, 18)
		hbox.Add(self.control, 1, wx.EXPAND|wx.ALL^wx.LEFT, 12)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.control.Bind(wx.EVT_TEXT, self.onTextBoxChanged)

	def onTextBoxChanged(self, event):
		self.undoValues.append(getProfileSetting(self.name))
		value = self.control.GetValue()
		putProfileSetting(self.name, value)
		self._updateEngine(value)
		if self.appendUndoCallback is not None:
			self.appendUndoCallback(self)
		if self.releaseUndoCallback is not None:
			self.releaseUndoCallback()

	def updateProfile(self):
		if hasattr(self,'control'):
			value = getProfileSetting(self.name)
			self.update(value)

class TitleText(ControlItem):
	def __init__(self, parent, name):
		""" """
		ControlItem.__init__(self, parent, name)

		#-- Elements
		self.control = wx.StaticText(self, wx.ID_ANY, self.setting.getLabel(), style=wx.ALIGN_CENTRE)
		self.control.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

		#-- Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.control, 0, wx.ALL, 10)
		vbox.Add(wx.StaticLine(self), 0, wx.EXPAND, 0)
		self.SetSizer(vbox)
		self.Layout()
		self.Fit()

	def updateProfile(self):
		if hasattr(self,'control'):
			self.update(None)

	def update(self, value):
		if self.isVisible():
			self.Show()
		else:
			self.Hide()

class Button(ControlItem):
	def __init__(self, parent, name):
		""" """
		ControlItem.__init__(self, parent, name)

		#-- Elements
		self.control = wx.Button(self,label=self.setting.getLabel())

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.control, 0, wx.ALL, 18)
		self.SetSizer(hbox)
		self.Layout()

	def updateProfile(self):
		if hasattr(self,'control'):
			self.update(None)

	def update(self, value):
		if self.isVisible():
			self.Show()
		else:
			self.Hide()