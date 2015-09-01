# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import profile, system as sys
from horus.engine.driver.driver import Driver
from horus.engine.algorithms.image_capture import ImageCapture
from horus.engine.calibration.calibration_data import CalibrationData
from horus.gui.util.customPanels import ExpandablePanel, SectionItem, Slider, ComboBox, \
    CheckBox, Button, TextBox, ToggleButton, CallbackButton, FloatTextBox


class CameraControl(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Camera control"))

        self.driver = Driver()
        self.image_capture = ImageCapture()
        self.calibration_data = CalibrationData()

        self.current_framerate = None

        self.clearSections()
        section = self.createSection('camera_control')
        section.addItem(Slider, 'brightness_control', tooltip=_(
            "Image luminosity. Low values are better for environments with high ambient "
            "light conditions. High values are recommended for poorly lit places"))
        section.addItem(Slider, 'contrast_control', tooltip=_(
            "Relative difference in intensity between an image point and its surroundings. "
            "Low values are recommended for black or very dark colored objects. "
            "High values are better for very light colored objects"))
        section.addItem(Slider, 'saturation_control', tooltip=_(
            "Purity of color. Low values will cause colors to disappear from the image. "
            "High values will show an image with very intense colors"))
        section.addItem(Slider, 'exposure_control', tooltip=_(
            "Amount of light per unit area. It is controlled by the time the camera sensor "
            "is exposed during a frame capture. "
            "High values are recommended for poorly lit places"))
        section.addItem(ComboBox, 'framerate', tooltip=_(
            "Number of frames captured by the camera every second. "
            "Maximum frame rate is recommended"))
        section.addItem(ComboBox, 'resolution', tooltip=_(
            "Size of the video. Maximum resolution is recommended"))
        section.addItem(CheckBox, 'use_distortion', tooltip=_(
            "This option applies lens distortion correction to the video. "
            "This process slows the video feed from the camera"))

        if sys.isDarwin():
            section = self.sections['camera_control'].disable('framerate')
            section = self.sections['camera_control'].disable('resolution')

    def updateCallbacks(self):
        section = self.sections['camera_control']
        section.updateCallback('brightness_control', self.driver.camera.set_brightness)
        section.updateCallback('contrast_control', self.driver.camera.set_contrast)
        section.updateCallback('saturation_control', self.driver.camera.set_saturation)
        section.updateCallback('exposure_control', self.driver.camera.set_exposure)
        section.updateCallback('framerate', lambda v: self.set_framerate(int(v)))
        section.updateCallback('resolution', lambda v: self.set_resolution(
            int(v.split('x')[0]), int(v.split('x')[1])))
        section.updateCallback(
            'use_distortion', lambda v: self.image_capture.set_use_distortion(v))

    def set_framerate(self, v):
        if self.current_framerate != v:
            self.current_framerate = v
            self.driver.camera.set_frame_rate(v)

    def set_resolution(self, width, height):
        self.driver.camera.set_resolution(width, height)
        self.calibration_data.set_resolution(height, width)


class LaserControl(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Laser control"), hasUndo=False, hasRestore=False)

        self.driver = Driver()

        self.clearSections()
        self.section = self.createSection('laser_control')
        self.section.addItem(ToggleButton, 'left_button')
        self.section.addItem(ToggleButton, 'right_button')

    def updateCallbacks(self):
        self.section.updateCallback(
            'left_button', (lambda i=0: self.driver.board.laser_on(i),
                            lambda i=0: self.driver.board.laser_off(i)))
        self.section.updateCallback(
            'right_button', (lambda i=1: self.driver.board.laser_on(i),
                             lambda i=1: self.driver.board.laser_off(i)))


class LDRControl(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("LDR control"), hasUndo=False, hasRestore=False)

        self.driver = Driver()

        self.clearSections()
        section = self.createSection('ldr_control')
        section.addItem(LDRSection, 'ldr_value')

    def updateCallbacks(self):
        section = self.sections['ldr_control']
        section.updateCallback('ldr_value', lambda id: self.driver.board.ldr_sensor(id))


class LDRSection(SectionItem):

    def __init__(self, parent, name, engineCallback=None):
        SectionItem.__init__(self, parent, name, engineCallback)

        # Elements
        self.LDR0Button = wx.Button(self, label='LDR 0', size=(140, -1))
        self.LDR1Button = wx.Button(self, label='LDR 1', size=(140, -1))
        self.LDR0Label = wx.StaticText(self, label='0')
        self.LDR1Label = wx.StaticText(self, label='0')

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.LDR0Button, 0, wx.ALIGN_CENTER_VERTICAL)
        hbox.AddStretchSpacer()
        hbox.Add(self.LDR0Label, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.LDR1Button, 0, wx.ALIGN_CENTER_VERTICAL)
        hbox.AddStretchSpacer()
        hbox.Add(self.LDR1Label, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)

        self.SetSizer(vbox)
        self.Layout()

        # Events
        self.LDR0Button.Bind(wx.EVT_BUTTON, self.onButton0Clicked)
        self.LDR1Button.Bind(wx.EVT_BUTTON, self.onButton1Clicked)

    def onButton0Clicked(self, event):
        self.onLDRButtonClicked(self.LDR0Button, self.LDR0Label, '0')

    def onButton1Clicked(self, event):
        self.onLDRButtonClicked(self.LDR1Button, self.LDR1Label, '1')

    def onLDRButtonClicked(self, _object, _label, _value):
        self.waitCursor = wx.BusyCursor()
        _object.Disable()
        if self.engineCallback is not None:
            ret = self.engineCallback(_value)
        wx.CallAfter(_object.Enable)
        if ret is not None:
            wx.CallAfter(lambda: _label.SetLabel(str(ret)))
        if hasattr(self, 'waitCursor'):
            del self.waitCursor

    def updateProfile(self):
        if hasattr(self, 'control'):
            self.update(None)

    def update(self, value):
        if self.isVisible():
            self.Show()
        else:
            self.Hide()


class MotorControl(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Motor control"), hasUndo=False)

        self.driver = Driver()

        self.clearSections()
        section = self.createSection('motor_control')
        section.addItem(FloatTextBox, 'motor_step_control')
        section.addItem(FloatTextBox, 'motor_speed_control')
        section.addItem(FloatTextBox, 'motor_acceleration_control')
        section.addItem(CallbackButton, 'move_button')
        section.addItem(ToggleButton, 'enable_button')

    def updateCallbacks(self):
        section = self.sections['motor_control']
        section.updateCallback(
            'motor_step_control', lambda v: self.driver.board.motor_relative(v))
        section.updateCallback(
            'motor_speed_control', lambda v: self.driver.board.motor_speed(v))
        section.updateCallback(
            'motor_acceleration_control',
            lambda v: self.driver.board.motor_acceleration(v))
        section.updateCallback(
            'move_button', lambda c: self.driver.board.motor_move(nonblocking=True, callback=c))
        section.updateCallback(
            'enable_button', (self.driver.board.motor_enable, self.driver.board.motor_disable))


class GcodeControl(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Gcode Control"), hasUndo=False, hasRestore=False)

        self.driver = Driver()

        self.clearSections()
        section = self.createSection('gcode_control')
        section.addItem(GcodeSection, 'gcode_gui')

    def updateCallbacks(self):
        section = self.sections['gcode_control']
        section.updateCallback(
            'gcode_gui',
            lambda v, c: self.driver.board._send_command(v, callback=c, read_lines=True))


class GcodeSection(SectionItem):

    def __init__(self, parent, name, engineCallback=None):
        SectionItem.__init__(self, parent, name, engineCallback)

        # Elements
        self.request = wx.TextCtrl(self)
        self.control = wx.Button(self, label=self.setting._label, size=(80, -1))
        self.response = wx.TextCtrl(self, size=(-1, 240), style=wx.TE_MULTILINE)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.request, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.EXPAND)
        vbox.Add(self.response, 1, wx.TOP | wx.EXPAND, 8)

        self.SetSizer(vbox)
        self.Layout()

        # Events
        self.request.Bind(wx.wx.EVT_KEY_DOWN, self.onKeyPressed)
        self.control.Bind(wx.EVT_BUTTON, self.onButtonClicked)

    def onKeyPressed(self, event):
        if event.GetKeyCode() is wx.WXK_RETURN:
            self.sendRequest()
        event.Skip()

    def onButtonClicked(self, event):
        self.sendRequest()

    def sendRequest(self):
        self.control.Disable()
        self.waitCursor = wx.BusyCursor()
        if self.engineCallback is not None:
            ret = self.engineCallback(
                str(self.request.GetValue()), lambda r: wx.CallAfter(self.onFinishCallback, r))

    def onFinishCallback(self, ret):
        self.control.Enable()
        if ret is not None:
            self.response.SetValue(ret)
        if hasattr(self, 'waitCursor'):
            del self.waitCursor

    def updateProfile(self):
        if hasattr(self, 'control'):
            self.update(None)

    def update(self, value):
        if self.isVisible():
            self.Show()
        else:
            self.Hide()
