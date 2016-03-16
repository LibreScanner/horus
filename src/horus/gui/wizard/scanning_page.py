# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.gui.wizard.wizard_page import WizardPage

from horus.util import profile

from horus.gui.engine import driver, ciclop_scan, image_capture


class ScanningPage(WizardPage):

    def __init__(self, parent, button_prev_callback=None, button_next_callback=None):
        WizardPage.__init__(self, parent,
                            title=_("Scanning"),
                            button_prev_callback=button_prev_callback,
                            button_next_callback=button_next_callback)

        value = abs(float(profile.settings['motor_step_scanning']))
        if value > 1.35:
            value = _("Low")
        elif value > 0.625:
            value = _("Medium")
        else:
            value = _("High")
        self.resolution_label = wx.StaticText(self.panel, label=_("Resolution"))
        self.resolution_label.SetToolTip(wx.ToolTip(_(u"Set the motor step. High (0.45º),"
                                                      u" Medium (0.9º), Low (1.8º)")))
        self.resolution_combo_box = wx.ComboBox(self.panel, wx.ID_ANY,
                                                size=(200, -1),
                                                value=value,
                                                choices=[_("High"), _("Medium"), _("Low")],
                                                style=wx.CB_READONLY)

        _choices = []
        choices = profile.settings.get_possible_values('use_laser')
        for i in choices:
            _choices.append(_(i))
        self.laser_dict = dict(zip(_choices, choices))
        self.laser_label = wx.StaticText(self.panel, label=_("Use laser"))
        self.laser_combo_box = wx.ComboBox(self.panel, wx.ID_ANY,
                                           size=(200, -1),
                                           value=_(profile.settings['use_laser']),
                                           choices=_choices,
                                           style=wx.CB_READONLY)

        self.capture_texture_label = wx.StaticText(self.panel, label=_("Capture texture"))
        self.capture_texture_checkbox = wx.CheckBox(self.panel,
                                                    size=(200, -1))
        self.capture_texture_checkbox.SetValue(profile.settings['capture_texture'])

        self.skip_button.Hide()

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.resolution_label, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.Add(self.resolution_combo_box, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 15)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.laser_label, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.Add(self.laser_combo_box, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 15)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.capture_texture_label, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.Add(self.capture_texture_checkbox, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 15)
        self.panel.SetSizer(vbox)
        self.Layout()

        self.resolution_combo_box.Bind(wx.EVT_COMBOBOX, self.on_resolution_combo_box_changed)
        self.laser_combo_box.Bind(wx.EVT_COMBOBOX, self.on_laser_combo_box_changed)
        self.capture_texture_checkbox.Bind(
            wx.EVT_CHECKBOX, self.on_capture_texture_checkbox_changed)
        self.Bind(wx.EVT_SHOW, self.on_show)

        self.video_view.set_callback(self.get_image)

    def on_show(self, event):
        if event.GetShow():
            self.update_status(driver.is_connected)
        else:
            try:
                self.video_view.stop()
            except:
                pass

    def on_resolution_combo_box_changed(self, event):
        value = event.GetEventObject().GetValue()
        if value == _("High"):
            value = 0.45
        elif value == _("Medium"):
            value = 0.9
        elif value == _("Low"):
            value = 1.8
        profile.settings['motor_step_scanning'] = value
        ciclop_scan.motor_step = value

    def on_laser_combo_box_changed(self, event):
        value = self.laser_dict[event.GetEventObject().GetValue()]
        profile.settings['use_laser'] = value
        use_left = value == 'Left' or value == 'Both'
        use_right = value == 'Right' or value == 'Both'
        if use_left:
            driver.board.laser_on(0)
        else:
            driver.board.laser_off(0)

        if use_right:
            driver.board.laser_on(1)
        else:
            driver.board.laser_off(1)
        ciclop_scan.set_use_left_laser(use_left)
        ciclop_scan.set_use_right_laser(use_right)

    def on_capture_texture_checkbox_changed(self, event):
        value = event.GetEventObject().GetValue()
        profile.settings['capture_texture'] = value
        ciclop_scan.set_capture_texture(value)

    def get_image(self):
        return image_capture.capture_texture()

    def update_status(self, status):
        if status:
            self.GetParent().parent.workbench['scanning'].setup_engine()
            self.video_view.play()
            value = profile.settings['use_laser']
            if value == 'Left':
                driver.board.laser_on(0)
                driver.board.laser_off(1)
            elif value == 'Right':
                driver.board.laser_off(0)
                driver.board.laser_on(1)
            elif value == 'Both':
                driver.board.lasers_on()
        else:
            self.video_view.stop()
