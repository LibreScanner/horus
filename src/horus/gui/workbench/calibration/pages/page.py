# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core


class Page(wx.Panel):

    def __init__(self, parent, title="Title", desc="", left="Left", right="Right",
                 button_left_callback=None, button_right_callback=None, view_progress=False):
        wx.Panel.__init__(self, parent)  # , style=wx.RAISED_BORDER)

        self.button_left_callback = button_left_callback
        self.button_right_callback = button_right_callback

        # Elements
        self.panel = wx.Panel(self)
        button_panel = wx.Panel(self)
        title_text = wx.StaticText(self, label=title)
        title_font = title_text.GetFont()
        title_font.SetWeight(wx.BOLD)
        title_text.SetFont(title_font)
        if desc != "":
            self.desc_text = wx.StaticText(self, label=desc)
        self.gauge = wx.Gauge(self, range=100, size=(-1, 30))
        self.left_button = wx.Button(button_panel, -1, left)
        self.right_button = wx.Button(button_panel, -1, right)
        if not view_progress:
            self.gauge.Hide()

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.panel_box = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(title_text, 0, wx.ALL ^ wx.BOTTOM | wx.EXPAND, 12)
        if desc != "":
            vbox.Add(self.desc_text, 0, wx.ALL | wx.EXPAND, 14)
        vbox.Add(self.panel, 1, wx.ALL | wx.EXPAND, 8)
        vbox.Add(self.gauge, 0, wx.ALL | wx.EXPAND, 10)
        self.panel.SetSizer(self.panel_box)
        vbox.Add(button_panel, 0, wx.ALL | wx.EXPAND, 1)
        hbox.Add(self.left_button, 0, wx.ALL | wx.EXPAND |
                 wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, 8)
        hbox.Add((0, 0), 1, wx.EXPAND)
        hbox.Add(self.right_button, 0, wx.ALL | wx.EXPAND |
                 wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 8)
        button_panel.SetSizer(hbox)
        self.SetSizer(vbox)
        self.Layout()

        # Events
        self.left_button.Bind(wx.EVT_BUTTON, self._on_left_button_pressed)
        self.right_button.Bind(wx.EVT_BUTTON, self._on_right_button_pressed)

    def _on_left_button_pressed(self, event):
        if self.button_left_callback is not None:
            self.button_left_callback()

    def _on_right_button_pressed(self, event):
        if self.button_right_callback is not None:
            self.button_right_callback()
