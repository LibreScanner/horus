# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

from horus.gui.workbench.calibration.pages.page import Page
from horus.gui.workbench.calibration.pages.video_page import VideoPage


class ScannerAutocheckPages(wx.Panel):

    def __init__(self, parent, accept_callback=None, cancel_callback=None):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)

        self.accept_callback = accept_callback
        self.cancel_callback = cancel_callback

        self.SetBackgroundColour(wx.BLUE)

        self.video_page = VideoPage(self, title=_('Scanner autocheck'),
                                    start_callback=self.on_start, cancel_callback=self.on_cancel)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.video_page, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(hbox)

        self._initialize()
        self.Layout()

    def _initialize(self):
        self.video_page.Show()

    def on_cancel(self):
        self.Hide()
        self._initialize()
        if self.cancel_callback is not None:
            self.cancel_callback()

    def on_start(self):
        self.video_page.Show()
        self.result_page.Hide()
        pass

    def on_accept(self, result):
        self.Hide()
        self._initialize()
        if self.accept_callback is not None:
            self.accept_callback(result)
