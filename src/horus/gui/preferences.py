# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
import threading

from horus.util import profile, resources
from horus.util.avrHelpers import AvrDude


class PreferencesDialog(wx.Dialog):

    def __init__(self, parent):
        super(PreferencesDialog, self).__init__(None, title=_("Preferences"))

        self.main = parent

        # Graphic elements
        self.conParamsStaticText = wx.StaticText(
            self, label=_("Connection Parameters"), style=wx.ALIGN_CENTRE)
        self.serialNameLabel = wx.StaticText(self, label=_("Serial Name"))
        self.serialNames = self.main.serialList()
        self.serialNameCombo = wx.ComboBox(self, choices=self.serialNames, size=(170, -1))
        self.baudRateLabel = wx.StaticText(self, label=_("Baud Rate"))
        self.baudRates = self.main.baudRateList()
        self.baudRateCombo = wx.ComboBox(
            self, choices=self.baudRates, size=(170, -1), style=wx.CB_READONLY)
        self.cameraIdLabel = wx.StaticText(self, label=_("Camera Id"))
        self.cameraIdNames = self.main.videoList()
        self.cameraIdCombo = wx.ComboBox(
            self, choices=self.cameraIdNames, size=(170, -1), style=wx.CB_READONLY)

        self.firmwareStaticText = wx.StaticText(
            self, label=_("Burn Firmware"), style=wx.ALIGN_CENTRE)
        self.boardLabel = wx.StaticText(self, label=_("AVR Board"))

        self.boards = profile.settings.getPossibleValues('board')
        self.boardsCombo = wx.ComboBox(
            self, choices=self.boards, value=board, size=(168, -1), style=wx.CB_READONLY)

        self.hexLabel = wx.StaticText(self, label=_("Binary file"))
        self.hexCombo = wx.ComboBox(self, choices=[_("Default"), _("External file...")], value=_(
            "Default"), size=(170, -1), style=wx.CB_READONLY)
        self.clearCheckBox = wx.CheckBox(self, label=_("Clear EEPROM"))
        self.uploadFirmwareButton = wx.Button(self, label=_("Upload Firmware"))
        self.gauge = wx.Gauge(self, range=100, size=(180, -1))
        self.gauge.Hide()

        self.languageLabel = wx.StaticText(self, label=_("Language"))
        self.languages = [row[1] for row in resources.getLanguageOptions()]
        self.languageCombo = wx.ComboBox(self, choices=self.languages,
                                         value=profile.settings['language'],
                                         size=(175, -1), style = wx.CB_READONLY)

        self.invertMotorCheckBox = wx.CheckBox(self, label=_("Invert the motor direction"))

        self.cancelButton = wx.Button(self, label=_("Cancel"), size=(110, -1))
        self.saveButton = wx.Button(self, label=_("Save"), size=(110, -1))

        # Events
        self.boardsCombo.Bind(wx.EVT_COMBOBOX, self.onBoardsComboChanged)

        self.hexCombo.Bind(wx.EVT_COMBOBOX, self.onHexComboChanged)
        self.uploadFirmwareButton.Bind(wx.EVT_BUTTON, self.onUploadFirmware)
        self.languageCombo.Bind(wx.EVT_COMBOBOX, self.onLanguageComboChanged)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onClose)
        self.saveButton.Bind(wx.EVT_BUTTON, self.onSaveButton)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Fill data
        currentSerial = profile.settings['serial_name']
        if len(self.serialNames) > 0:
            if currentSerial not in self.serialNames:
                self.serialNameCombo.SetValue(self.serialNames[0])
            else:
                self.serialNameCombo.SetValue(currentSerial)

        currentBaudRate = profile.settings['baud_rate']
        self.baudRateCombo.SetValue(str(currentBaudRate))

        currentVideoId = profile.settings['camera_id']
        if len(self.cameraIdNames) > 0:
            if currentVideoId not in self.cameraIdNames:
                self.cameraIdCombo.SetValue(self.cameraIdNames[0])
            else:
                self.cameraIdCombo.SetValue(currentVideoId)

        currentBoard = profile.settings['board']
        self.boardsCombo.SetValue(currentBoard)

        currentInvert = profile.settings['invert_motor']
        self.invertMotorCheckBox.SetValue(currentInvert)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(self.conParamsStaticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.serialNameLabel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.serialNameCombo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.baudRateLabel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.baudRateCombo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.cameraIdLabel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.cameraIdCombo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        vbox.Add(self.firmwareStaticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.boardLabel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.boardsCombo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.hexLabel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.hexCombo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.uploadFirmwareButton, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.clearCheckBox, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

        vbox.Add(self.gauge, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)

        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL ^ wx.TOP, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.languageLabel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.languageCombo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.invertMotorCheckBox, 0, wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.cancelButton, 0, wx.ALL ^ wx.RIGHT, 10)
        hbox.Add(self.saveButton, 0, wx.ALL, 10)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.hexPath = None

        self.SetSizerAndFit(vbox)

        self.Centre()
        self.Layout()
        self.Fit()

    def onSaveButton(self, event):
        if len(self.serialNameCombo.GetValue()):
            profile.settings['serial_name'] = self.serialNameCombo.GetValue()
        if self.baudRateCombo.GetValue() in self.baudRates:
            profile.settings['baud_rate'] = int(self.baudRateCombo.GetValue())
        if len(self.cameraIdCombo.GetValue()):
            profile.settings['camera_id'] = self.cameraIdCombo.GetValue()
        profile.settings['board'] = self.boardsCombo.GetValue()
        if profile.settings['language'] != self.languageCombo.GetValue():
            profile.settings['language'] = self.languageCombo.GetValue()
        profile.settings['invert_motor'] = self.invertMotorCheckBox.GetValue()

        profile.settings.saveSettings(categories=["preferences"])
        self.onClose(None)

    def onClose(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def onHexComboChanged(self, event):
        value = self.hexCombo.GetValue()
        if value == _("Default"):
            self.hexPath = None
        elif value == _("External file..."):
            dlg = wx.FileDialog(
                self, _("Select binary file to load"), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            dlg.SetWildcard("hex files (*.hex)|*.hex")
            if dlg.ShowModal() == wx.ID_OK:
                self.hexPath = dlg.GetPath()
                self.hexCombo.SetValue(dlg.GetFilename())
            else:
                self.hexCombo.SetValue(_("Default"))
            dlg.Destroy()

    def onUploadFirmware(self, event):
        if self.serialNameCombo.GetValue() != '':
            self.beforeLoadFirmware()
            baudRate = self._getBaudRate(self.boardsCombo.GetValue())
            clearEEPROM = self.clearCheckBox.GetValue()
            threading.Thread(target=self.loadFirmware, args=(baudRate, clearEEPROM)).start()

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
        out = avr_dude.flash(
            extraFlags=extraFlags, hexPath=self.hexPath, callback=self.incrementProgress)
        if 'not in sync' in out or 'Invalid' in out:
            wx.CallAfter(self.wrongBoardMessage)
        wx.CallAfter(self.afterLoadFirmware)

    def incrementProgress(self):
        self.count += 1
        if self.count >= 0:
            wx.CallAfter(self.gauge.SetValue, self.count)

    def wrongBoardMessage(self):
        dlg = wx.MessageDialog(
            self,
            _("Probably you have selected the wrong board. Select other Board"),
            'Wrong Board', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def beforeLoadFirmware(self):
        self.uploadFirmwareButton.Disable()
        self.clearCheckBox.Disable()
        self.boardsCombo.Disable()
        self.okButton.Disable()
        self.gauge.SetValue(0)
        self.gauge.Show()
        self.waitCursor = wx.BusyCursor()
        self.GetSizer().Layout()
        self.SetSizerAndFit(self.GetSizer())

    def afterLoadFirmware(self):
        self.uploadFirmwareButton.Enable()
        self.clearCheckBox.Enable()
        self.boardsCombo.Enable()
        self.okButton.Enable()
        self.gauge.Hide()
        del self.waitCursor
        self.GetSizer().Layout()
        self.SetSizerAndFit(self.GetSizer())

    def onLanguageComboChanged(self, event):
        if profile.settings['language'] != self.languageCombo.GetValue():
            wx.MessageBox(
                _("You have to restart the application to make the changes effective."),
                'Info', wx.OK | wx.ICON_INFORMATION)
