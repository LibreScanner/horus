# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import version


class VersionWindow(wx.Dialog):

    def __init__(self, parent):
        super(VersionWindow, self).__init__(parent, title=_('New version available!'), size=(420,-1), style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

        #-- Elements
        self.description = wx.StaticText(self, label= _('A new version of Horus is available, would you like to download?'))
        self.downloadButton = wx.Button(self, label=_('Download'))
        self.cancelButton = wx.Button(self, label=_('Cancel'))

        self.download = False

        #-- Events
        self.downloadButton.Bind(wx.EVT_BUTTON, self.onDownloadButton)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButton)
        self.Bind(wx.EVT_CLOSE, self.onCancelButton)

        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.description, 0, wx.ALL|wx.CENTER, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.cancelButton, 0, wx.ALL, 3)
        hbox.Add(self.downloadButton, 0, wx.ALL, 3)
        vbox.Add(hbox, 0, wx.ALL|wx.CENTER, 10)
        self.SetSizer(vbox)
        self.Center()
        self.Fit()

        self.ShowModal()

    def onDownloadButton(self, event):
        self.download = True
        version.downloadLatestVersion()
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def onCancelButton(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()