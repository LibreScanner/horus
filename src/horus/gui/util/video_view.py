# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.gui.util.image_view import ImageView


class VideoView(ImageView):

    def __init__(self, parent, callback=None, milliseconds=1, size=(-1, -1), black=False):
        ImageView.__init__(self, parent, size=size, black=black)  # , style=wx.RAISED_BORDER)

        self.callback = callback
        self.milliseconds = milliseconds

        self.playing = False

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

    def on_timer(self, event):
        self.timer.Stop()
        if self.playing:
            if self.callback is not None:
                self.set_frame(self.callback())
            self._start()

    def set_callback(self, callback):
        self.callback = callback

    def set_milliseconds(self, milliseconds):
        self.milliseconds = milliseconds

    def play(self):
        if not self.playing:
            self.playing = True
            self._start()

    def _start(self):
        self.timer.Start(milliseconds=self.milliseconds)

    def pause(self):
        if self.playing:
            self.playing = False
            self.timer.Stop()

    def stop(self):
        if self.playing:
            self.playing = False
            self.timer.Stop()
            self.hide = True
            self.set_default_image()
