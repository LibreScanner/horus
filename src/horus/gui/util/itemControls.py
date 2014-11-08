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

import wx._core
from collections import OrderedDict

from horus.util import profile

class Control(wx.Panel):
	def __init__(self, parent, title, bold=True):
		wx.Panel.__init__(self, parent)

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)

		self.title = TitleText(self, title, bold)
		self.sizer.Add(self.title, 0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=5)

		self.items = OrderedDict()

		self.Layout()

	def append(self, _type, _name, _callback):
		item = _type(self, _name, _callback)
		self.items.update({_name : item})
		self.sizer.Add(item, 0, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
		self.Layout()

	def setUndoCallbacks(self, appendUndoCallback=None, releaseUndoCallback=None):
		for item in self.items.values():
			item.setUndoCallbacks(appendUndoCallback, releaseUndoCallback)

	def resetProfile(self):
		for item in self.items.values():
			item.resetProfile()

	def disableContent(self):
		for item in self.items.values():
			item.Disable()
		self.Layout()

	def enableContent(self):
		for item in self.items.values():
			item.Enable()
		self.Layout()

	def hideContent(self):
		for item in self.items.values():
			item.Hide()
		self.Layout()

	def showContent(self):
		for item in self.items.values():
			item.Show()
		self.Layout()

	def updateProfile(self):
		v = 0
		for item in self.items.values():
			item.updateProfile()
			if item.isVisible():
				v += 1
		if v > 0:
			self.Show()
		else:
			self.Hide()


class TitleText(wx.Panel):
	def __init__(self, parent, title, bold=True):
		wx.Panel.__init__(self, parent)

		#-- Elements
		self.title = wx.StaticText(self, wx.ID_ANY, title)
		if bold:
			fontWeight = wx.FONTWEIGHT_BOLD
		else:
			fontWeight = wx.FONTWEIGHT_NORMAL
		self.title.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, fontWeight)))

		#-- Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.title, 0, flag=wx.ALL|wx.EXPAND, border=5)
		vbox.Add(wx.StaticLine(self), 1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=5)
		self.SetSizer(vbox)
		self.Layout()


class ControlItem(wx.Panel):
	def __init__(self, parent, name, engineCallback=None):
		wx.Panel.__init__(self, parent)
		self.engineCallback = engineCallback
		self.appendUndoCallback = None
		self.releaseUndoCallback = None

		self.undoValues = []

		self.control = None

		self.name = name
		self.setting = profile.getProfileSettingObject(self.name)

	def setEngineCallback(self, engineCallback=None):
		self.engineCallback = engineCallback

	def setUndoCallbacks(self, appendUndoCallback=None, releaseUndoCallback=None):
		self.appendUndoCallback = appendUndoCallback
		self.releaseUndoCallback = releaseUndoCallback

	def isVisible(self):
		if profile.getPreferenceBool('basic_mode'):
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
			profile.putProfileSetting(self.name, value)
			self.update(value)

	def resetProfile(self):
		profile.resetProfileSetting(self.name)
		del self.undoValues[:]
		self.updateProfile()


class Slider(ControlItem):
	def __init__(self, parent, name, engineCallback=None):
		""" """
		ControlItem.__init__(self, parent, name, engineCallback)

		self.flagFirstMove = True

		#-- Elements
		self.label = wx.StaticText(self, label=self.setting.getLabel())
		self.control = wx.Slider(self, wx.ID_ANY,
								 profile.getProfileSettingInteger(self.name),
								 int(eval(self.setting.getMinValue(), {}, {})),
								 int(eval(self.setting.getMaxValue(), {}, {})),
								 size=(150,-1),
								 style=wx.SL_LABELS)

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.label, 0, wx.TOP|wx.RIGHT|wx.EXPAND, 20)
		hbox.Add(self.control, 1, wx.RIGHT|wx.EXPAND, 12)
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
			value = profile.getProfileSettingInteger(self.name)
			self.undoValues.append(value)
			if self.appendUndoCallback is not None:
				self.appendUndoCallback(self)
			self.flagFirstMove = False
		value = self.control.GetValue()
		profile.putProfileSetting(self.name, value)
		self._updateEngine(value)

	def updateProfile(self):
		if hasattr(self,'control'):
			value = profile.getProfileSettingInteger(self.name)
			self.update(value)


class ComboBox(ControlItem):
	def __init__(self, parent, name, engineCallback=None):
		""" """
		ControlItem.__init__(self, parent, name, engineCallback)

		#-- Elements
		self.label = wx.StaticText(self, label=self.setting.getLabel())
		self.control = wx.ComboBox(self, wx.ID_ANY,
								   value=profile.getProfileSetting(self.name),
								   choices=self.setting.getType(),
								   size=(150, -1),
								   style=wx.CB_READONLY)

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.label, 0, wx.TOP|wx.RIGHT|wx.EXPAND, 18)
		hbox.Add(self.control, 1, wx.TOP|wx.RIGHT|wx.EXPAND, 12)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.control.Bind(wx.EVT_COMBOBOX, self.onComboBoxChanged)

	def onComboBoxChanged(self, event):
		self.undoValues.append(profile.getProfileSetting(self.name))
		value = self.control.GetValue()
		profile.putProfileSetting(self.name, value)
		self._updateEngine(value)
		if self.appendUndoCallback is not None:
			self.appendUndoCallback(self)
		if self.releaseUndoCallback is not None:
			self.releaseUndoCallback()

	def updateProfile(self):
		if hasattr(self,'control'):
			value = profile.getProfileSetting(self.name)
			self.update(value)


class CheckBox(ControlItem):
	def __init__(self, parent, name, engineCallback=None):
		""" """
		ControlItem.__init__(self, parent, name, engineCallback)

		#-- Elements
		self.label = wx.StaticText(self, label=self.setting.getLabel())
		self.control = wx.CheckBox(self, style=wx.ALIGN_RIGHT)

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.label, 0, wx.TOP|wx.RIGHT|wx.EXPAND, 7)
		hbox.Add(self.control, 1, wx.TOP|wx.BOTTOM|wx.EXPAND, 7)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.control.Bind(wx.EVT_CHECKBOX, self.onCheckBoxChanged)

	def onCheckBoxChanged(self, event):
		self.undoValues.append(profile.getProfileSettingBool(self.name))
		value = self.control.GetValue()
		profile.putProfileSetting(self.name, value)
		self._updateEngine(value)
		if self.appendUndoCallback is not None:
			self.appendUndoCallback(self)
		if self.releaseUndoCallback is not None:
			self.releaseUndoCallback()

	def updateProfile(self):
		if hasattr(self,'control'):
			value = profile.getProfileSettingBool(self.name)
			self.update(value)

class RadioButton(ControlItem):
	def __init__(self, parent, name, engineCallback=None):
		""" """
		ControlItem.__init__(self, parent, name, engineCallback)

		#-- Elements
		self.label = wx.StaticText(self, label=self.setting.getLabel())
		self.control = wx.RadioButton(self, style=wx.ALIGN_RIGHT)

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.label, 0, wx.TOP|wx.RIGHT|wx.EXPAND, 15)
		hbox.Add(self.control, 1, wx.TOP|wx.EXPAND, 16)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.control.Bind(wx.EVT_RADIOBUTTON, self.onRadioButtonChanged)

	def onRadioButtonChanged(self, event):
		self.undoValues.append(profile.getProfileSettingBool(self.name))
		value = self.control.GetValue()
		profile.putProfileSetting(self.name, value)
		self._updateEngine(value)
		if self.appendUndoCallback is not None:
			self.appendUndoCallback(self)
		if self.releaseUndoCallback is not None:
			self.releaseUndoCallback()

	def updateProfile(self):
		if hasattr(self,'control'):
			value = profile.getProfileSettingBool(self.name)
			self.update(value)

class TextBox(ControlItem):
	def __init__(self, parent, name, engineCallback=None):
		""" """
		ControlItem.__init__(self, parent, name, engineCallback)

		#-- Elements
		self.label = wx.StaticText(self, label=self.setting.getLabel())
		self.control = wx.TextCtrl(self)

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.label, 0, wx.ALL^wx.LEFT|wx.EXPAND, 18)
		hbox.Add(self.control, 1, wx.ALL^wx.LEFT|wx.EXPAND, 12)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.control.Bind(wx.EVT_TEXT, self.onTextBoxChanged)

	def onTextBoxChanged(self, event):
		#self.undoValues.append(profile.getProfileSetting(self.name))
		value = self.control.GetValue()
		profile.putProfileSetting(self.name, value)
		self._updateEngine(value)
		#if self.appendUndoCallback is not None:
		#	self.appendUndoCallback(self)
		#if self.releaseUndoCallback is not None:
		#	self.releaseUndoCallback()

	def updateProfile(self):
		if hasattr(self,'control'):
			value = profile.getProfileSetting(self.name)
			self.update(value)

class Button(ControlItem):
	def __init__(self, parent, name, engineCallback=None):
		""" """
		ControlItem.__init__(self, parent, name, engineCallback)

		#-- Elements
		self.control = wx.Button(self, label=self.setting.getLabel())

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.control, 1, wx.ALL^wx.LEFT|wx.EXPAND, 10)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.control.Bind(wx.EVT_BUTTON, self.onButtonClicked)

	def onButtonClicked(self, event):
		if self.engineCallback is not None:
			self.engineCallback()

	def updateProfile(self):
		if hasattr(self,'control'):
			self.update(None)

	def update(self, value):
		if self.isVisible():
			self.Show()
		else:
			self.Hide()

class ToggleButton(ControlItem):
	def __init__(self, parent, name, engineCallback=None):
		""" """
		ControlItem.__init__(self, parent, name, engineCallback)

		#-- Elements
		self.control = wx.ToggleButton(self, label=self.setting.getLabel())

		#-- Layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.control, 1, wx.ALL^wx.LEFT|wx.EXPAND, 10)
		self.SetSizer(hbox)
		self.Layout()

		#-- Events
		self.control.Bind(wx.EVT_TOGGLEBUTTON, self.onButtonToggle)

	def onButtonToggle(self, event):
		if self.engineCallback is not None:
			if event.IsChecked():
				function = 0
			else:
				function = 1

			if self.engineCallback[function] is not None:
				self.engineCallback[function]()

	def updateProfile(self):
		if hasattr(self,'control'):
			self.update(None)

	def update(self, value):
		if self.isVisible():
			self.Show()
		else:
			self.Hide()