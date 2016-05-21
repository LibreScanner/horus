# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import resources

from horus.gui.engine import image_capture, image_detection, camera_intrinsics
from horus.gui.workbench.calibration.pages.page import Page
from horus.gui.util.image_view import ImageView
from horus.gui.util.video_view import VideoView


class CapturePage(Page):

    def __init__(self, parent, start_callback=None):
        Page.__init__(self, parent,
                      title=_("Camera intrinsics (advanced)"),
                      desc=_("Default values are recommended. To perform the calibration, "
                             "click over the video panel and press "
                             "space bar to perform the captures."),
                      left=_("Reset"),
                      right=_("Start"),
                      button_left_callback=self.initialize,
                      button_right_callback=start_callback,
                      view_progress=True)

        self.right_button.Hide()

        # Elements
        self.video_view = VideoView(self.panel, self.get_image)
        self.rows, self.columns = 3, 5
        self.panel_grid = []
        self.current_grid = 0
        self.image_grid_panel = wx.Panel(self.panel)
        self.grid_sizer = wx.GridSizer(self.rows, self.columns, 3, 3)
        for panel in xrange(self.rows * self.columns):
            self.panel_grid.append(ImageView(self.image_grid_panel))
            self.panel_grid[panel].Bind(wx.EVT_KEY_DOWN, self.on_key_press)
            self.grid_sizer.Add(self.panel_grid[panel], 0, wx.ALL | wx.EXPAND)
        self.image_grid_panel.SetSizer(self.grid_sizer)

        # Layout
        self.panel_box.Add(self.video_view, 2, wx.ALL | wx.EXPAND, 2)
        self.panel_box.Add(self.image_grid_panel, 3, wx.ALL | wx.EXPAND, 3)
        self.Layout()

        # Events
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_press)
        self.video_view.Bind(wx.EVT_KEY_DOWN, self.on_key_press)
        self.image_grid_panel.Bind(wx.EVT_KEY_DOWN, self.on_key_press)

    def initialize(self):
        self.desc_text.SetLabel(
            _("Default values are recommended. To perform the calibration, "
              "click over the video panel and press "
              "space bar to perform the captures."))
        self.current_grid = 0
        self.gauge.SetValue(0)
        camera_intrinsics.reset()
        for panel in xrange(self.rows * self.columns):
            self.panel_grid[panel].SetBackgroundColour((221, 221, 221))
            self.panel_grid[panel].set_image(wx.Image(resources.get_path_for_image("void.png")))

    def play(self):
        self.gauge.SetValue(0)
        self.video_view.play()
        self.image_grid_panel.SetFocus()
        self.GetParent().Layout()
        self.Layout()

    def stop(self):
        self.initialize()
        self.video_view.stop()

    def reset(self):
        self.video_view.reset()

    def get_image(self):
        image = image_capture.capture_pattern()
        chessboard = image_detection.detect_pattern(image)
        return chessboard

    def on_key_press(self, event):
        if event.GetKeyCode() == 32:  # spacebar
            self.video_view.stop()
            image = camera_intrinsics.capture()
            if image is not None:
                self.add_frame_to_grid(image)
                if self.current_grid <= self.rows * self.columns:
                    self.gauge.SetValue(self.current_grid * 100.0 / self.rows / self.columns)
            self.video_view.play()

    def add_frame_to_grid(self, image):
        if self.current_grid < (self.columns * self.rows):
            self.panel_grid[self.current_grid].set_frame(image)
            self.current_grid += 1
        if self.current_grid is (self.columns * self.rows):
            self.desc_text.SetLabel(_("Press space bar to continue"))
            if self.button_right_callback is not None:
                self.button_right_callback()
