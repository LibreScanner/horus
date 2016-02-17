# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.gui.util.image_view import ImageView


class VideoView(ImageView):

    def __init__(self, parent, callback=None, size=(-1, -1)):
        ImageView.__init__(self, parent, size=size, black=True)

        self.callback = callback

        self.playing = False
        self._tries = 0  # Check if command fails
        self._number_frames_fail = 3

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

    def on_timer(self, event):
        self.timer.Stop()
        if self.playing:
            if self.callback is not None:
                frame = self.callback()
                if frame is None:
                    self._tries += 1
                    if self._tries >= self._number_frames_fail:
                        self._tries = 0
                else:
                    self._tries = 0
                    self.set_frame(frame)
                self._start()

    def set_callback(self, callback):
        self.callback = callback

    def play(self):
        if not self.playing:
            self.playing = True
            self._start()

    def _start(self):
        self.timer.Start(milliseconds=100)

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
