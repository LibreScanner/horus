# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
import wx.lib.scrolledpanel

from horus.gui.engine import driver
from horus.gui.util.image_view import VideoView
from horus.gui.util.custom_panels import ExpandableCollection


class Workbench(wx.Panel):

    def __init__(self, parent, name='Workbench'):
        wx.Panel.__init__(self, parent)
        self.name = name

        # Elements
        self.scroll_panel = wx.lib.scrolledpanel.ScrolledPanel(self, size=(-1, -1))
        self.scroll_panel.SetupScrolling(scroll_x=False, scrollIntoView=False)
        self.scroll_panel.SetAutoLayout(1)
        self.video_view = VideoView(self, self.video_frame, 10, black=True)

        self.collection = ExpandableCollection(self.scroll_panel)
        self.collection.SetBackgroundColour(wx.BLUE)
        self.add_panels()  # Add panels to collection
        self.collection.init_panels_layout()

        # Layout
        vsbox = wx.BoxSizer(wx.VERTICAL)
        vsbox.Add(self.collection, 1, wx.ALL | wx.EXPAND, 0)
        self.scroll_panel.SetSizer(vsbox)
        vsbox.Fit(self.scroll_panel)
        panel_size = self.scroll_panel.GetSize()[0] + wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
        self.scroll_panel.SetMinSize((panel_size, -1))

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.scroll_panel, 0, wx.ALL | wx.EXPAND, 1)
        hbox.Add(self.video_view, 1, wx.ALL | wx.EXPAND, 1)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.Bind(wx.EVT_SHOW, self.on_show)

    def add_panels(self):
        raise NotImplementedError

    def setup_engine(self):
        raise NotImplementedError

    def video_frame(self):
        raise NotImplementedError

    def add_panel(self, name, panel):
        self.collection.add_panel(name, panel)

    def enable_content(self):
        self.collection.enable_content()

    def disable_content(self):
        self.collection.disable_content()

    def update_controls(self):
        self.collection.update_from_profile()
        if driver.is_connected:
            self.setup_engine()

    def on_connect(self):
        if driver.is_connected:
            self.setup_engine()
        self.video_view.play()

    def on_disconnect(self):
        self.video_view.stop()

    def on_open(self):
        if driver.is_connected:
            self.setup_engine()
        self.video_view.play()

    def on_close(self):
        try:
            if self.video_view is not None:
                self.video_view.stop()
        except:
            pass

    def on_show(self, event):
        if event.GetShow():
            self.on_open()
        else:
            self.on_close()
