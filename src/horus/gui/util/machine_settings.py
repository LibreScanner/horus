# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Nicanor Romero Venier <nicanor.romerovenier@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import os
import wx._core
import wx.lib.intctrl

from horus.util import profile

# TODO: refactor PEP8


class MachineSettingsDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, None, title=_("Machine settings"))

        self.main = parent

        # Elements
        self.machineShapeLabel = wx.StaticText(self, label=_("Platform shape"))
        self.machineShapes = profile.settings.get_possible_values("machine_shape")
        self.translatedMachineShapes = [_(s) for s in self.machineShapes]
        self.machineShapeCombo = wx.ComboBox(
            self, choices=self.translatedMachineShapes, size=(170, -1), style=wx.CB_READONLY)

        self.dimensionsStaticText = wx.StaticText(
            self, label=_("Platform dimensions"), style=wx.ALIGN_CENTRE)
        self.diameterLabel = wx.StaticText(self, label=_("Diameter"))
        self.diameterField = wx.lib.intctrl.IntCtrl(self, size=(170, -1), style=wx.TE_RIGHT)
        self.widthLabel = wx.StaticText(self, label=_("Width"))
        self.widthField = wx.lib.intctrl.IntCtrl(self, size=(170, -1), style=wx.TE_RIGHT)
        self.heightLabel = wx.StaticText(self, label=_("Height"))
        self.heightField = wx.lib.intctrl.IntCtrl(self, size=(170, -1), style=wx.TE_RIGHT)
        self.depthLabel = wx.StaticText(self, label=_("Depth"))
        self.depthField = wx.lib.intctrl.IntCtrl(self, size=(170, -1), style=wx.TE_RIGHT)

        self.machineModelLabel = wx.StaticText(self, label=_("Machine model"))
        self.machineModelButton = wx.Button(self, label=_("Browse"))
        self.machineModelField = wx.StaticText(self, size=(200, -1))

        self.defaultButton = wx.Button(self, label=_("Default"))
        self.cancel_button = wx.Button(self, label=_("Cancel"))
        self.saveButton = wx.Button(self, label=_("Save"))

        # Events
        self.machineShapeCombo.Bind(wx.EVT_COMBOBOX, self.onMachineShapeComboChanged)
        self.machineModelButton.Bind(wx.EVT_BUTTON, self.onMachineModelButton)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.onCancelButton)
        self.saveButton.Bind(wx.EVT_BUTTON, self.onSaveButton)
        self.defaultButton.Bind(wx.EVT_BUTTON, self.onDefaultButton)
        self.Bind(wx.EVT_CLOSE, self.onCancelButton)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.machineShapeLabel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.machineShapeCombo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        vbox.Add(self.dimensionsStaticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        # Diameter
        self.diam_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.diam_hbox.Add(self.diameterLabel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        self.diam_hbox.AddStretchSpacer()
        self.diam_hbox.Add(self.diameterField, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(self.diam_hbox, 0, wx.ALL | wx.EXPAND, 10)
        # Width
        self.width_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.width_hbox.Add(self.widthLabel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        self.width_hbox.AddStretchSpacer()
        self.width_hbox.Add(self.widthField, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(self.width_hbox, 0, wx.ALL | wx.EXPAND, 10)
        # Height
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.heightLabel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.heightField, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        # Depth
        self.depth_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.depth_hbox.Add(self.depthLabel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        self.depth_hbox.AddStretchSpacer()
        self.depth_hbox.Add(self.depthField, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(self.depth_hbox, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        # Machine STL
        vbox.Add(self.machineModelLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.machineModelButton, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.machineModelField, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.defaultButton, 0, wx.ALL ^ wx.RIGHT, 10)
        hbox.Add(self.cancel_button, 0, wx.ALL ^ wx.RIGHT, 10)
        hbox.Add(self.saveButton, 0, wx.ALL, 10)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Fill data from settings
        self.machineShapeCombo.SetValue(_(profile.settings['machine_shape']))
        self.diameterField.SetValue(profile.settings['machine_diameter'])
        self.widthField.SetValue(profile.settings['machine_width'])
        self.heightField.SetValue(profile.settings['machine_height'])
        self.depthField.SetValue(profile.settings['machine_depth'])
        self.machineModelPath = profile.settings['machine_model_path']
        self.machineModelField.SetLabel(self._getFileName(self.machineModelPath))

        self.SetSizerAndFit(vbox)

        self.onMachineShapeComboChanged(None)

        self.Centre()
        self.Layout()
        self.Fit()

    def onCancelButton(self, event):
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()

    def onSaveButton(self, event):
        # Store the original value, not the translated one
        machine_shape = self.machineShapes[
            self.translatedMachineShapes.index(self.machineShapeCombo.GetValue())]
        profile.settings['machine_shape'] = machine_shape
        profile.settings['machine_diameter'] = self.diameterField.GetValue()
        profile.settings['machine_width'] = self.widthField.GetValue()
        profile.settings['machine_height'] = self.heightField.GetValue()
        profile.settings['machine_depth'] = self.depthField.GetValue()
        profile.settings['machine_model_path'] = self.machineModelPath
        # Settings are saved after mesh is loaded. This way we avoid saving a faulty STL model.
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def onDefaultButton(self, event):
        self.machineShapeCombo.SetValue(_(profile.settings.getDefault('machine_shape')))
        self.onMachineShapeComboChanged(None)
        self.diameterField.SetValue(profile.settings.getDefault('machine_diameter'))
        self.widthField.SetValue(profile.settings.getDefault('machine_width'))
        self.heightField.SetValue(profile.settings.getDefault('machine_height'))
        self.depthField.SetValue(profile.settings.getDefault('machine_depth'))
        self.machineModelPath = profile.settings.getDefault('machine_model_path')
        self.machineModelField.SetLabel(self._getFileName(self.machineModelPath))

    def onMachineShapeComboChanged(self, event):
        vbox = self.get_sizer()
        machine_shape = self.machineShapes[
            self.translatedMachineShapes.index(self.machineShapeCombo.GetValue())]
        if machine_shape == "Circular":
            vbox.Show(self.diam_hbox, recursive=True)
            vbox.Hide(self.width_hbox, recursive=True)
            vbox.Hide(self.depth_hbox, recursive=True)
        elif machine_shape == "Rectangular":
            vbox.Hide(self.diam_hbox, recursive=True)
            vbox.Show(self.width_hbox, recursive=True)
            vbox.Show(self.depth_hbox, recursive=True)
        vbox.Layout()
        self.SetSizerAndFit(vbox)

    def onMachineModelButton(self, event):
        dlg = wx.FileDialog(
            self, message=_("Select binary file to load"),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        dlg.SetWildcard("Model files (*.stl)|*.stl")
        if dlg.ShowModal() == wx.ID_OK:
            self.machineModelPath = dlg.GetPath()
            self.machineModelField.SetLabel(dlg.GetFilename())
        dlg.Destroy()

    def _getFileName(self, path):
        return os.path.basename(path)
