# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import resources

from horus.gui.engine import image_capture, image_detection, laser_triangulation
from horus.gui.workbench.calibration.pages.page import Page
from horus.gui.util.image_view import ImageView
from horus.gui.util.video_view import VideoView


class VideoPage(Page):

    def __init__(self, parent, title='Video page', cancel_callback=None, start_callback=None):
        Page.__init__(self, parent,
                      title=title,
                      desc=_("Put the pattern on the platform as shown in the "
                             "picture and press Start"),
                      left=_("Cancel"),
                      right=_("Start"),
                      button_left_callback=cancel_callback,
                      button_right_callback=start_callback,
                      view_progress=True)

        # Elements
        image_view = ImageView(self.panel, quality=wx.IMAGE_QUALITY_HIGH)
        image_view.set_image(wx.Image(resources.get_path_for_image("pattern-position.png")))
        self.video_view = VideoView(self.panel, self.get_image, 10, black=True)

        # Layout
        self.panel_box.Add(image_view, 3, wx.ALL | wx.EXPAND, 3)
        self.panel_box.Add(self.video_view, 2, wx.ALL | wx.EXPAND, 3)
        self.Layout()

        # Events
        self.Bind(wx.EVT_SHOW, self.on_show)

    def initialize(self):
        self.gauge.SetValue(0)
        self.right_button.Enable()

    def on_show(self, event):
        if event.GetShow():
            self.video_view.play()
            self.GetParent().Layout()
            self.Layout()
        else:
            try:
                self.initialize()
                self.video_view.stop()
            except:
                pass

    def get_image(self):
        if laser_triangulation.has_image:
            image = laser_triangulation.image
        else:
            image = image_capture.capture_pattern()
            if not laser_triangulation._is_calibrating:
                image = image_detection.detect_pattern(image)
        return image
