# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
import threading

from horus.gui.engine import driver
from horus.util import profile, resources
from horus.util.avrHelpers import AvrDude


class PreferencesDialog(wx.Dialog):

    def __init__(self):
        wx.Dialog.__init__(self, None, title=_("Preferences"))

        # Elements
        self.hex_path = None
        self.con_params_static_text = wx.StaticText(
            self, label=_("Connection Parameters"), style=wx.ALIGN_CENTRE)
        self.serial_name_label = wx.StaticText(self, label=_("Serial Name"))
        self.serial_names = driver.board.get_serial_list()
        self.serial_name_combo = wx.ComboBox(self, choices=self.serial_names, size=(170, -1))
        self.baud_rate_label = wx.StaticText(self, label=_("Baud Rate"))
        self.baud_rates = [str(b) for b in profile.settings.get_possible_values('baud_rate')]
        self.baud_rate_combo = wx.ComboBox(
            self, choices=self.baud_rates, size=(170, -1), style=wx.CB_READONLY)
        self.camera_id_label = wx.StaticText(self, label=_("Camera Id"))
        self.camera_id_names = driver.camera.get_video_list()
        self.camera_id_combo = wx.ComboBox(
            self, choices=self.camera_id_names, size=(170, -1), style=wx.CB_READONLY)

        self.firmware_static_text = wx.StaticText(
            self, label=_("Burn Firmware"), style=wx.ALIGN_CENTRE)
        self.board_label = wx.StaticText(self, label=_("AVR Board"))
        self.boards = profile.settings.get_possible_values('board')
        self.boards_combo = wx.ComboBox(
            self, choices=self.boards, size=(168, -1), style=wx.CB_READONLY)

        self.hex_label = wx.StaticText(self, label=_("Binary file"))
        self.hex_combo = wx.ComboBox(self, choices=[_("Default"), _("External file...")], value=_(
            "Default"), size=(170, -1), style=wx.CB_READONLY)
        self.clear_check_box = wx.CheckBox(self, label=_("Clear EEPROM"))
        self.upload_firmware_button = wx.Button(self, label=_("Upload Firmware"))
        self.gauge = wx.Gauge(self, range=100, size=(180, -1))
        self.gauge.Hide()

        self.language_label = wx.StaticText(self, label=_("Language"))
        self.languages = [row[1] for row in resources.get_language_options()]
        self.language_combo = wx.ComboBox(self, choices=self.languages,
                                          value=profile.settings['language'],
                                          size=(175, -1), style = wx.CB_READONLY)

        self.invert_motor_check_box = wx.CheckBox(self, label=_("Invert the motor direction"))

        self.cancel_button = wx.Button(self, label=_("Cancel"), size=(110, -1))
        self.save_button = wx.Button(self, label=_("Save"), size=(110, -1))

        # Fill data
        current_serial = profile.settings['serial_name']
        if len(self.serial_names) > 0:
            if current_serial not in self.serial_names:
                self.serial_name_combo.SetValue(self.serial_names[0])
            else:
                self.serial_name_combo.SetValue(current_serial)

        current_baud_rate = str(profile.settings['baud_rate'])
        self.baud_rate_combo.SetValue(current_baud_rate)

        current_video_id = profile.settings['camera_id']
        if len(self.camera_id_names) > 0:
            if current_video_id not in self.camera_id_names:
                self.camera_id_combo.SetValue(self.camera_id_names[0])
            else:
                self.camera_id_combo.SetValue(current_video_id)

        current_board = profile.settings['board']
        self.boards_combo.SetValue(current_board)

        current_invert = profile.settings['invert_motor']
        self.invert_motor_check_box.SetValue(current_invert)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(self.con_params_static_text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.serial_name_label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.serial_name_combo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.baud_rate_label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.baud_rate_combo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.camera_id_label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.camera_id_combo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        vbox.Add(self.firmware_static_text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.board_label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.boards_combo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.hex_label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.hex_combo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.upload_firmware_button, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.clear_check_box, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

        vbox.Add(self.gauge, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)

        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL ^ wx.TOP, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.language_label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.language_combo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.invert_motor_check_box, 0, wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.cancel_button, 0, wx.ALL ^ wx.RIGHT, 10)
        hbox.Add(self.save_button, 0, wx.ALL, 10)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.SetSizerAndFit(vbox)
        self.Centre()
        self.Layout()
        self.Fit()

        # Events
        self.hex_combo.Bind(wx.EVT_COMBOBOX, self.on_hex_combo_changed)
        self.upload_firmware_button.Bind(wx.EVT_BUTTON, self.on_upload_firmware)
        self.language_combo.Bind(wx.EVT_COMBOBOX, self.on_language_combo_changed)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_close)
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save_button)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_hex_combo_changed(self, event):
        value = self.hex_combo.GetValue()
        if value == _("Default"):
            self.hex_path = None
        elif value == _("External file..."):
            dlg = wx.FileDialog(
                self, _("Select binary file to load"), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            dlg.SetWildcard("hex files (*.hex)|*.hex")
            if dlg.ShowModal() == wx.ID_OK:
                self.hex_path = dlg.GetPath()
                self.hex_combo.SetValue(dlg.GetFilename())
            else:
                self.hex_combo.SetValue(_("Default"))
            dlg.Destroy()

    def on_upload_firmware(self, event):
        if self.serial_name_combo.GetValue() != '':
            self.before_load_firmware()
            baud_rate = self._get_baud_rate(self.boards_combo.GetValue())
            clear_eeprom = self.clear_check_box.GetValue()
            threading.Thread(target=self.load_firmware, args=(baud_rate, clear_eeprom)).start()

    def _get_baud_rate(self, value):
        if value == 'Arduino Uno':
            return 115200
        elif value == 'BT ATmega328':
            return 19200

    def load_firmware(self, hex_baud_rate, clear_eeprom):
        avr_dude = AvrDude(port=profile.settings['serial_name'], baud_rate=hex_baud_rate)
        extra_flags = []
        if clear_eeprom:
            extra_flags = ["-D"]
        self.count = -50
        out = avr_dude.flash(
            extra_flags=extra_flags, hexPath=self.hexPath, callback=self.increment_progress)
        if 'not in sync' in out or 'Invalid' in out:
            wx.CallAfter(self.wrong_board_message)
        wx.CallAfter(self.after_load_firmware)

    def increment_progress(self):
        self.count += 1
        if self.count >= 0:
            wx.CallAfter(self.gauge.SetValue, self.count)

    def wrong_board_message(self):
        dlg = wx.MessageDialog(
            self, _("Probably you have selected the wrong board. Select other Board"),
            _('Wrong Board'), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def before_load_firmware(self):
        self.upload_firmware_button.Disable()
        self.clear_check_box.Disable()
        self.boards_combo.Disable()
        self.gauge.SetValue(0)
        self.gauge.Show()
        self.waitCursor = wx.BusyCursor()
        self.GetSizer().Layout()
        self.SetSizerAndFit(self.GetSizer())

    def after_load_firmware(self):
        self.upload_firmware_button.Enable()
        self.clear_check_box.Enable()
        self.boards_combo.Enable()
        self.gauge.Hide()
        del self.waitCursor
        self.GetSizer().Layout()
        self.SetSizerAndFit(self.GetSizer())

    def on_language_combo_changed(self, event):
        if profile.settings['language'] != self.language_combo.GetValue():
            wx.MessageBox(
                _("You have to restart the application to make the changes effective."),
                'Info', wx.OK | wx.ICON_INFORMATION)

    def on_save_button(self, event):
        # Update profile
        if len(self.serial_name_combo.GetValue()):
            profile.settings['serial_name'] = self.serial_name_combo.GetValue()
        if self.baud_rate_combo.GetValue() in self.baud_rates:
            profile.settings['baud_rate'] = int(self.baud_rate_combo.GetValue())
        if len(self.camera_id_combo.GetValue()):
            profile.settings['camera_id'] = self.camera_id_combo.GetValue()
        profile.settings['board'] = self.boards_combo.GetValue()
        if profile.settings['language'] != self.language_combo.GetValue():
            profile.settings['language'] = self.language_combo.GetValue()
        profile.settings['invert_motor'] = self.invert_motor_check_box.GetValue()
        profile.settings.save_settings(categories=["preferences"])
        # Update engine
        driver.board.serial_name = profile.settings['serial_name']
        driver.board.baud_rate = profile.settings['baud_rate']
        driver.camera.camera_id = int(profile.settings['camera_id'][-1:])
        driver.board.motor_invert(profile.settings['invert_motor'])
        self.on_close(None)

    def on_close(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()
