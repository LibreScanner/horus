# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import version


class VersionWindow(wx.Dialog):

    def __init__(self, parent):
        super(VersionWindow, self).__init__(
            parent, title=_('New version available!'),
            size=(420, -1), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        # Elements
        self.description = wx.StaticText(
            self, label=_('A new version of Horus is available, would you like to download it?'))
        self.download_button = wx.Button(self, label=_('Download'))
        self.cancel_button = wx.Button(self, label=_('Cancel'))

        self.download = False

        # Events
        self.download_button.Bind(wx.EVT_BUTTON, self.on_download_button)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel_button)
        self.Bind(wx.EVT_CLOSE, self.on_cancel_button)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.description, 0, wx.ALL | wx.CENTER, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.cancel_button, 0, wx.ALL, 3)
        hbox.Add(self.download_button, 0, wx.ALL, 3)
        vbox.Add(hbox, 0, wx.ALL | wx.CENTER, 10)
        self.SetSizer(vbox)
        self.Center()
        self.Fit()

        self.ShowModal()

    def on_download_button(self, event):
        self.download = True
        version.download_latest_version()
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def on_cancel_button(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()
