# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Irene Sanz Nieto <irene.sanz@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core


class ResolutionWindow(wx.Dialog):

    def __init__(self, parent):
        super(ResolutionWindow, self).__init__(parent, title=_('Resolution updated'), size=(420,-1), style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

        #-- Elements
        self.description = wx.StaticText(self, label=_('WARNING: if you change the resolution, you need to calibrate again with the same resolution!'))
        self.description.Wrap(400)

        self.okButton = wx.Button(self, label=_('OK'))

        #-- Events
        self.okButton.Bind(wx.EVT_BUTTON, self.onClose)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        #-- Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.description, 0, wx.ALL|wx.CENTER, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.okButton, 0, wx.ALL, 3)
        vbox.Add(hbox, 0, wx.ALL|wx.CENTER, 10)
        self.SetSizer(vbox)
        self.Center()
        self.Fit()

        self.ShowModal()

    def onClose(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()