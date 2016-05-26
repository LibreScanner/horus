# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import system as sys

from horus.gui.util.video_view import VideoView


class WizardPage(wx.Panel):

    def __init__(self, parent, title="Title", button_prev_callback=None, button_next_callback=None):
        wx.Panel.__init__(self, parent)

        self.title = title
        self.panel = wx.Panel(self)

        self.enable_next = True

        self.button_prev_callback = button_prev_callback
        self.button_skip_callback = button_next_callback
        self.button_next_callback = button_next_callback

        self.video_view = VideoView(self, size=(300, 400), wxtimer=False)
        self.prev_button = wx.Button(self, label=_("Previous"))
        self.skip_button = wx.Button(self, label=_("Skip"))
        self.next_button = wx.Button(self, label=_("Next"))

    def intialize(self, pages):
        self.breadcrumbs = Breadcrumbs(self, pages)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.breadcrumbs, 0, wx.ALL | wx.EXPAND, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.panel, 1, wx.RIGHT | wx.EXPAND, 10)
        hbox.Add(self.video_view, 0, wx.ALL, 0)
        vbox.Add(hbox, 1, wx.ALL | wx.EXPAND, 20)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.prev_button, 0, wx.ALL | wx.EXPAND |
                 wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, 2)
        hbox.Add((0, 0), 1, wx.EXPAND)
        hbox.Add(self.skip_button, 0, wx.ALL | wx.EXPAND |
                 wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 2)
        hbox.Add(self.next_button, 0, wx.ALL | wx.EXPAND |
                 wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 2)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(vbox)

        # Events
        self.prev_button.Bind(wx.EVT_BUTTON, self._on_prev_button_pressed)
        self.skip_button.Bind(wx.EVT_BUTTON, self._on_skip_button_pressed)
        self.next_button.Bind(wx.EVT_BUTTON, self._on_next_button_pressed)

        self.Layout()

    def add_to_panel(self, _object, _size):
        if _object is not None:
            self.panelBox.Add(_object, _size, wx.ALL | wx.EXPAND, 3)

    def _on_prev_button_pressed(self, event):
        if self.button_prev_callback is not None:
            self.button_prev_callback()

    def _on_skip_button_pressed(self, event):
        if self.button_skip_callback is not None:
            self.button_skip_callback()

    def _on_next_button_pressed(self, event):
        if self.button_next_callback is not None:
            self.button_next_callback()


class Breadcrumbs(wx.Panel):

    def __init__(self, parent, pages=[]):
        wx.Panel.__init__(self, parent)

        self.pages = pages

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        for page in self.pages:
            title = wx.StaticText(self, label=page.title)
            title.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
            if self.GetParent().title == page.title:
                title_font = title.GetFont()
                title_font.SetWeight(wx.BOLD)
                title.SetFont(title_font)
            else:
                title_font = title.GetFont()
                title_font.SetWeight(wx.LIGHT)
                title.SetFont(title_font)
            title.Bind(wx.EVT_LEFT_UP, self.on_title_pressed)
            hbox.Add(title, 0, wx.ALL | wx.EXPAND, 0)
            if page is not pages[-1]:
                line = wx.StaticText(self, label="  .....................  ")
                line_font = line.GetFont()
                line_font.SetWeight(wx.LIGHT)
                line.SetFont(line_font)
                hbox.Add(line, 0, wx.ALL | wx.EXPAND, 0)
        vbox.Add(hbox, 0, wx.ALL | wx.CENTER, 0)

        self.SetSizer(vbox)
        self.Layout()

    def _hide(self, label):
        for page in self.pages:
            if page.enable_next:
                if page.title != label:
                    page.Hide()
            else:
                break

    def _show(self, label):
        for page in self.pages:
            if page.enable_next:
                if page.title == label:
                    page.Show()
            else:
                break

    def on_title_pressed(self, event):
        label = event.GetEventObject().GetLabel()
        if sys.is_windows():
            self._show(label)
            self._hide(label)
        else:
            self._hide(label)
            self._show(label)

        self.GetParent().GetParent().Layout()
