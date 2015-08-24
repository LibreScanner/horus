# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx.lib.scrolledpanel

from horus.util import resources

from horus.gui.util.imageView import VideoView
from horus.gui.util.customPanels import ExpandableControl
from horus.gui.workbench.workbench import WorkbenchConnection
from horus.gui.workbench.control.panels import CameraControl, LaserControl, \
    LDRControl, MotorControl, GcodeControl

from horus.engine.algorithms.image_capture import ImageCapture


class ControlWorkbench(WorkbenchConnection):

    def __init__(self, parent):
        WorkbenchConnection.__init__(self, parent)

        self.image_capture = ImageCapture()

        # Elements
        self.toolbar.Realize()

        self.scrollPanel = wx.lib.scrolledpanel.ScrolledPanel(self._panel, size=(290, -1))
        self.scrollPanel.SetupScrolling(scroll_x=False, scrollIntoView=False)
        self.scrollPanel.SetAutoLayout(1)

        self.controls = ExpandableControl(self.scrollPanel)
        self.controls.addPanel('camera_control', CameraControl(self.controls))
        self.controls.addPanel('laser_control', LaserControl(self.controls))
        self.controls.addPanel('ldr_value', LDRControl(self.controls))
        self.controls.addPanel('motor_control', MotorControl(self.controls))
        self.controls.addPanel('gcode_control', GcodeControl(self.controls))

        self.videoView = VideoView(self._panel, self.image_capture.capture_image, 10)
        self.videoView.SetBackgroundColour(wx.BLACK)

        # Layout
        vsbox = wx.BoxSizer(wx.VERTICAL)
        vsbox.Add(self.controls, 0, wx.ALL | wx.EXPAND, 0)
        self.scrollPanel.SetSizer(vsbox)
        vsbox.Fit(self.scrollPanel)

        self.addToPanel(self.scrollPanel, 0)
        self.addToPanel(self.videoView, 1)

        self.updateCallbacks()
        self.Layout()

    def updateCallbacks(self):
        self.controls.updateCallbacks()

    def updateToolbarStatus(self, status):
        if status:
            if self.IsShown():
                self.videoView.play()
                self.controls.panels['laser_control'].section.items[
                    'left_button'].control.SetValue(False)
                self.controls.panels['laser_control'].section.items[
                    'right_button'].control.SetValue(False)
            self.controls.enableContent()
        else:
            self.videoView.stop()
            self.controls.disableContent()

    def updateProfileToAllControls(self):
        self.controls.updateProfile()
