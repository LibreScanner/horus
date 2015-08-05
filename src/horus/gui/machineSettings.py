#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014-2015 Mundo Reader S.L.                             #
#                                                                       #
# Date: July 2015                                                       #
# Author: Nicanor Romero Venier <nicanor.romerovenier@bq.com>           #
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

import os
import wx._core
import threading
import wx.lib.intctrl

from horus.util import profile, resources
from horus.util.avrHelpers import AvrDude


class MachineSettingsDialog(wx.Dialog):
	def __init__(self, parent):
		super(MachineSettingsDialog, self).__init__(None, title=_("Machine Settings"))

		self.main = parent

		#-- Graphic elements
		self.machineShapeLabel = wx.StaticText(self, label=_("Platform Shape"))
		self.machineShapes = profile.getMachineSettingType("machine_shape")
		self.machineShapeCombo = wx.ComboBox(self, choices=self.machineShapes, size=(170,-1), style=wx.CB_READONLY)

		self.dimensionsStaticText = wx.StaticText(self, label=_("Platform Dimensions"), style=wx.ALIGN_CENTRE)
		self.diameterLabel = wx.StaticText(self, label=_("Diameter"))
		self.diameterField = wx.lib.intctrl.IntCtrl(self, size=(170,-1), style=wx.TE_RIGHT)
		self.widthLabel = wx.StaticText(self, label=_("Width"))
		self.widthField = wx.lib.intctrl.IntCtrl(self, size=(170,-1), style=wx.TE_RIGHT)
		self.heightLabel = wx.StaticText(self, label=_("Height"))
		self.heightField = wx.lib.intctrl.IntCtrl(self, size=(170,-1), style=wx.TE_RIGHT)
		self.depthLabel = wx.StaticText(self, label=_("Depth"))
		self.depthField = wx.lib.intctrl.IntCtrl(self, size=(170,-1), style=wx.TE_RIGHT)

		self.machineModelLabel = wx.StaticText(self, label=_("Machine Model"))
		self.machineModelButton = wx.Button(self, label=_("Browse"))
		self.machineModelField = wx.StaticText(self, size=(200,-1))

		self.defaultButton = wx.Button(self, label=_("Default"))
		self.cancelButton = wx.Button(self, label=_("Cancel"))
		self.saveButton = wx.Button(self, label=_("Save"))

		#-- Events
		self.machineShapeCombo.Bind(wx.EVT_COMBOBOX, self.onmachineShapeComboChanged)
		self.machineModelButton.Bind(wx.EVT_BUTTON, self.onMachineModelButton)
		self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButton)
		self.saveButton.Bind(wx.EVT_BUTTON, self.onSaveButton)
		self.defaultButton.Bind(wx.EVT_BUTTON, self.onDefaultButton)
		self.Bind(wx.EVT_CLOSE, self.onCancelButton)

		#-- Layout
		self.vbox = wx.BoxSizer(wx.VERTICAL)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.machineShapeLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		hbox.AddStretchSpacer()
		hbox.Add(self.machineShapeCombo, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		self.vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 10)
		self.vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)

		self.vbox.Add(self.dimensionsStaticText, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 10)
		# Diameter
		self.diam_hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.diam_hbox.Add(self.diameterLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		self.diam_hbox.AddStretchSpacer()
		self.diam_hbox.Add(self.diameterField, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		self.vbox.Add(self.diam_hbox, 0, wx.ALL|wx.EXPAND, 10)
		# Width
		self.width_hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.width_hbox.Add(self.widthLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		self.width_hbox.AddStretchSpacer()
		self.width_hbox.Add(self.widthField, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		self.vbox.Add(self.width_hbox, 0, wx.ALL|wx.EXPAND, 10)
		# Height
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.heightLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		hbox.AddStretchSpacer()
		hbox.Add(self.heightField, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		self.vbox.Add(hbox, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
		# Depth
		self.depth_hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.depth_hbox.Add(self.depthLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		self.depth_hbox.AddStretchSpacer()
		self.depth_hbox.Add(self.depthField, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		self.vbox.Add(self.depth_hbox, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
		self.vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)

		# Machine STL
		self.vbox.Add(self.machineModelLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 10)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.machineModelButton, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		hbox.AddStretchSpacer()
		hbox.Add(self.machineModelField, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		self.vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 10)
		self.vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.defaultButton, 0, wx.ALL^wx.RIGHT, 10)
		hbox.Add(self.cancelButton, 0, wx.ALL^wx.RIGHT, 10)
		hbox.Add(self.saveButton, 0, wx.ALL, 10)
		self.vbox.Add(hbox, 0, wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 5)

		#-- Fill data from settings
		self.machineShapeCombo.SetValue(profile.getMachineSetting('machine_shape'))
		self.diameterField.SetValue(profile.getMachineSettingInteger('machine_diameter'))
		self.widthField.SetValue(profile.getMachineSettingInteger('machine_width'))
		self.heightField.SetValue(profile.getMachineSettingInteger('machine_height'))
		self.depthField.SetValue(profile.getMachineSettingInteger('machine_depth'))
		self.machineModelPath = profile.getMachineSettingPath('machine_model_path')
		self.machineModelField.SetLabel(self._getFileName(self.machineModelPath))

		self.onmachineShapeComboChanged(None)

		self.SetSizer(self.vbox)

		self.Centre()
		self.Layout()
		self.Fit()


	def onCancelButton(self, event):
		self.EndModal(wx.ID_CANCEL)
		self.Destroy()

	def onSaveButton(self, event):
		profile.putMachineSetting('machine_shape', self.machineShapeCombo.GetValue())
		profile.putMachineSetting('machine_diameter', self.diameterField.GetValue())
		profile.putMachineSetting('machine_width', self.widthField.GetValue())
		profile.putMachineSetting('machine_height', self.heightField.GetValue())
		profile.putMachineSetting('machine_depth', self.depthField.GetValue())
		profile.putMachineSetting('machine_model_path', self.machineModelPath)
		# Settings are saved after mesh is loaded. This way we avoid saving a faulty STL model.
		self.EndModal(wx.ID_OK)
		self.Destroy()

	def onDefaultButton(self, event):
		self.machineShapeCombo.SetValue(profile.getDefaultMachineSetting('machine_shape'))
		self.onmachineShapeComboChanged(None)
		self.diameterField.SetValue(profile.getDefaultMachineSettingInteger('machine_diameter'))
		self.widthField.SetValue(profile.getDefaultMachineSettingInteger('machine_width'))
		self.heightField.SetValue(profile.getDefaultMachineSettingInteger('machine_height'))
		self.depthField.SetValue(profile.getDefaultMachineSettingInteger('machine_depth'))
		self.machineModelPath = profile.getDefaultMachineSetting('machine_model_path')
		self.machineModelField.SetLabel(self._getFileName(self.machineModelPath))

	def onmachineShapeComboChanged(self, event):
		if self.machineShapeCombo.GetValue() == "Circular":
			self.vbox.Show(self.diam_hbox, recursive=True)
			self.vbox.Hide(self.width_hbox, recursive=True)
			self.vbox.Hide(self.depth_hbox, recursive=True)
		elif self.machineShapeCombo.GetValue() == "Rectangular":
			self.vbox.Hide(self.diam_hbox, recursive=True)
			self.vbox.Show(self.width_hbox, recursive=True)
			self.vbox.Show(self.depth_hbox, recursive=True)
		self.Layout()
		self.Fit()

	def onMachineModelButton(self, event):
		dlg = wx.FileDialog(self, message=_("Select binary file to load"), style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
		dlg.SetWildcard("Model files (*.stl)|*.stl")
		if dlg.ShowModal() == wx.ID_OK:
			self.machineModelPath = dlg.GetPath()
			self.machineModelField.SetLabel(dlg.GetFilename())
		dlg.Destroy()

	def _getFileName(self, path):
		return os.path.basename(path)