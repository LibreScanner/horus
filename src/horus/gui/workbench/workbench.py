# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
import wx.lib.scrolledpanel
from collections import OrderedDict

from horus.gui.engine import driver
from horus.gui.util.custom_panels import ExpandableCollection


class Workbench(wx.Panel):

    def __init__(self, parent, name='Workbench'):
        wx.Panel.__init__(self, parent)
        self.name = name

        # Elements
        self.scroll_panel = wx.lib.scrolledpanel.ScrolledPanel(self, size=(-1, -1))
        self.scroll_panel.SetupScrolling(scroll_x=False, scrollIntoView=False)
        self.scroll_panel.SetAutoLayout(1)
        self.panels_collection = ExpandableCollection(self.scroll_panel)
        self.pages_collection = OrderedDict()

        # Layout
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.scroll_panel, 0, wx.ALL ^ wx.RIGHT | wx.EXPAND, 1)
        self.SetSizer(self.hbox)

        self.add_panels()  # Add panels to collection
        self.panels_collection.init_panels_layout()

        vsbox = wx.BoxSizer(wx.VERTICAL)
        vsbox.Add(self.panels_collection, 1, wx.ALL | wx.EXPAND, 0)
        self.scroll_panel.SetSizer(vsbox)
        vsbox.Fit(self.scroll_panel)
        panel_size = self.scroll_panel.GetSize()[0] + wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
        self.scroll_panel.SetMinSize((panel_size, -1))
        self.scroll_panel.Disable()

        self.add_pages()
        self.Layout()

        # Events
        self.Bind(wx.EVT_SHOW, self.on_show)

    def add_panels(self):
        raise NotImplementedError

    def add_pages(self):
        raise NotImplementedError

    def setup_engine(self):
        raise NotImplementedError

    def on_open(self):
        raise NotImplementedError

    def on_close(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def add_panel(self, name, panel, on_selected_callback=None):
        self.panels_collection.add_panel(name, panel, on_selected_callback)

    def add_page(self, name, page):
        self.pages_collection[name] = page
        self.hbox.Add(page, 1, wx.ALL | wx.EXPAND, 2)

    def enable_content(self):
        self.scroll_panel.Enable()
        self.panels_collection.enable_content()

    def disable_content(self):
        self.panels_collection.disable_content()
        self.scroll_panel.Disable()

    def update_controls(self):
        self.panels_collection.update_from_profile()
        if driver.is_connected:
            self.setup_engine()

    def on_connect(self):
        if driver.is_connected:
            self.setup_engine()
            for _, p in self.pages_collection.iteritems():
                p.Enable()
            self.on_open()

    def on_disconnect(self):
        for _, p in self.pages_collection.iteritems():
            p.Disable()
        self.on_close()
        self.disable_content()
        self.reset()

    def on_show(self, event):
        if event.GetShow():
            if driver.is_connected:
                self.setup_engine()
                self.on_open()
        else:
            self.on_close()
