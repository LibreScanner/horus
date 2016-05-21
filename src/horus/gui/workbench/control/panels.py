# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import profile, system as sys

from horus.gui.engine import driver
from horus.gui.util.custom_panels import ExpandablePanel, ControlPanel, Slider, \
    ToggleButton, Button, CallbackButton, FloatTextBox


class CameraControl(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(self, parent, _("Camera control"))
        self.current_framerate = None

    def add_controls(self):
        self.add_control(
            'brightness_control', Slider,
            _("Image luminosity. Low values are better for environments with high ambient "
              "light conditions. High values are recommended for poorly lit places"))
        self.add_control(
            'contrast_control', Slider,
            _("Relative difference in intensity between an image point and its "
              "surroundings. Low values are recommended for black or very dark colored "
              "objects. High values are better for very light colored objects"))
        self.add_control(
            'saturation_control', Slider,
            _("Purity of color. Low values will cause colors to disappear from the image. "
              "High values will show an image with very intense colors"))
        self.add_control(
            'exposure_control', Slider,
            _("Amount of light per unit area. It is controlled by the time the camera "
              "sensor is exposed during a frame capture. "
              "High values are recommended for poorly lit places"))
        self.add_control('save_image_button', Button)

    def update_callbacks(self):
        self.update_callback('brightness_control', driver.camera.set_brightness)
        self.update_callback('contrast_control', driver.camera.set_contrast)
        self.update_callback('saturation_control', driver.camera.set_saturation)
        self.update_callback('exposure_control', driver.camera.set_exposure)
        self.update_callback('save_image_button', self._save_image)

    def on_selected(self):
        profile.settings['current_panel_control'] = 'camera_control'

    def _save_image(self):
        image = driver.camera.capture_image()
        dlg = wx.FileDialog(self, _("Save image"), style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        wildcard_list = ';'.join(map(lambda s: '*' + s, ['.png']))
        wildcard_filter = "Image files (%s)|%s;%s" % (wildcard_list, wildcard_list,
                                                      wildcard_list.upper())
        dlg.SetWildcard(wildcard_filter)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not filename.endswith('.png'):
                if sys.is_linux():  # hack for linux, as for some reason the .ply is not appended.
                    filename += '.png'
            driver.camera.save_image(filename, image)
        dlg.Destroy()


class LaserControl(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(
            self, parent, _("Laser control"), has_undo=False, has_restore=False)

    def add_controls(self):
        self.add_control('left_button', ToggleButton)
        self.add_control('right_button', ToggleButton)

    def update_callbacks(self):
        self.update_callback('left_button',
                             (lambda i=0: driver.board.laser_on(i),
                              lambda i=0: driver.board.laser_off(i)))
        self.update_callback('right_button',
                             (lambda i=1: driver.board.laser_on(i),
                              lambda i=1: driver.board.laser_off(i)))

    def on_selected(self):
        profile.settings['current_panel_control'] = 'laser_control'


class LDRControl(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(
            self, parent, _("LDR control"), has_undo=False, has_restore=False)

    def add_controls(self):
        self.add_control('ldr_value', LDRSection)

    def update_callbacks(self):
        self.update_callback('ldr_value', lambda id: driver.board.ldr_sensor(id))

    def on_selected(self):
        profile.settings['current_panel_control'] = 'ldr_value'


class LDRSection(ControlPanel):

    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        self.ldr_buttons = []
        self.ldr_labels = []
        self.ldr_buttons += [wx.Button(self, label='LDR 0', size=(140, -1))]
        self.ldr_buttons += [wx.Button(self, label='LDR 1', size=(140, -1))]
        self.ldr_labels += [wx.StaticText(self, label='0')]
        self.ldr_labels += [wx.StaticText(self, label='0')]

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.ldr_buttons[0], 0, wx.ALIGN_CENTER_VERTICAL)
        hbox.AddStretchSpacer()
        hbox.Add(self.ldr_labels[0], 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.ldr_buttons[1], 0, wx.ALIGN_CENTER_VERTICAL)
        hbox.AddStretchSpacer()
        hbox.Add(self.ldr_labels[1], 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)
        self.SetSizer(vbox)
        self.Layout()

        # Events
        self.ldr_buttons[0].Bind(wx.EVT_BUTTON, self.on_button_0_clicked)
        self.ldr_buttons[1].Bind(wx.EVT_BUTTON, self.on_button_1_clicked)

    def on_button_0_clicked(self, event):
        self.on_ldr_button_clicked(0)

    def on_button_1_clicked(self, event):
        self.on_ldr_button_clicked(1)

    def on_ldr_button_clicked(self, index):
        self.wait_cursor = wx.BusyCursor()
        self.ldr_buttons[index].Disable()
        if self.engine_callback is not None:
            ret = self.engine_callback(str(index))
        wx.CallAfter(self.ldr_buttons[index].Enable)
        if ret is not None:
            wx.CallAfter(lambda: self.ldr_labels[index].SetLabel(str(ret)))
        if hasattr(self, 'wait_cursor'):
            del self.wait_cursor


class MotorControl(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(self, parent, _("Motor control"), has_undo=False)

    def add_controls(self):
        self.add_control('motor_step_control', FloatTextBox)
        self.add_control('motor_speed_control', FloatTextBox)
        self.add_control('motor_acceleration_control', FloatTextBox)
        self.add_control('move_button', CallbackButton)
        self.add_control('enable_button', ToggleButton)
        self.add_control('reset_origin_button', Button)

    def update_callbacks(self):
        self.update_callback('motor_speed_control', driver.board.motor_speed)
        self.update_callback('motor_acceleration_control', driver.board.motor_acceleration)
        self.update_callback('move_button', lambda c: self._on_move_button(c))
        self.update_callback('enable_button',
                             (driver.board.motor_enable, driver.board.motor_disable))
        self.update_callback('reset_origin_button', driver.board.motor_reset_origin)

    def on_selected(self):
        profile.settings['current_panel_control'] = 'motor_control'

    def _on_move_button(self, callback):
        step = self.get_control('motor_step_control').control.GetValue()
        driver.board.motor_move(step, nonblocking=True, callback=callback)


class GcodeControl(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(
            self, parent, _("Gcode Control"), has_undo=False, has_restore=False)

    def add_controls(self):
        self.add_control('gcode_gui', GcodeSection)

    def update_callbacks(self):
        self.update_callback(
            'gcode_gui',
            lambda v, c: driver.board.send_command(v, nonblocking=True,
                                                   callback=c, read_lines=True))

    def on_selected(self):
        profile.settings['current_panel_control'] = 'gcode_control'


class GcodeSection(ControlPanel):

    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        self.request = wx.TextCtrl(self)
        self.control = wx.Button(self, label=_(self.setting._label), size=(-1, -1))
        self.response = wx.TextCtrl(self, size=(-1, 275), style=wx.TE_MULTILINE)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.request, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.EXPAND)
        vbox.Add(self.response, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 8)
        self.SetSizer(vbox)
        self.Layout()

        # Events
        self.request.Bind(wx.wx.EVT_KEY_DOWN, self.on_key_pressed)
        self.control.Bind(wx.EVT_BUTTON, self.on_button_clicked)

    def on_key_pressed(self, event):
        if event.GetKeyCode() is wx.WXK_RETURN:
            self.send_request()
        event.Skip()

    def on_button_clicked(self, event):
        self.send_request()

    def send_request(self):
        self.control.Disable()
        self.wait_cursor = wx.BusyCursor()
        if self.engine_callback is not None:
            self.engine_callback(
                str(self.request.GetValue()), lambda r: wx.CallAfter(self.on_finish_callback, r))

    def on_finish_callback(self, ret):
        self.control.Enable()
        if ret is not None:
            self.response.SetValue(ret)
        if hasattr(self, 'wait_cursor'):
            del self.wait_cursor
