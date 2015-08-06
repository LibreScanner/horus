# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import resources, system as sys


class ImageView(wx.Panel):

    def __init__(self, parent, resize=True, size=(-1, -1)):
        wx.Panel.__init__(self, parent, size=size)  # , style=wx.SIMPLE_BORDER)

        self.xOffset = 0
        self.yOffset = 0

        self.defaultImage = wx.Image(resources.getPathForImage("nusb.png"))
        self.image = self.defaultImage
        self.bitmap = wx.BitmapFromImage(self.defaultImage)

        self.SetDoubleBuffered(True)

        self.Bind(wx.EVT_SHOW, self.onShow)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        if resize:
            self.Bind(wx.EVT_SIZE, self.onResize)

        self.hide = True

    def onShow(self, event):
        if event.GetShow():
            self.GetParent().Layout()
            self.Layout()

    def onPaint(self, event):
        if not self.hide:
            dc = wx.PaintDC(self)
            dc.DrawBitmap(self.bitmap, self.xOffset, self.yOffset)

    def onResize(self, size):
        self.refreshBitmap()

    def setImage(self, image):
        if image is not None:
            if self.hide:
                self.hide = False
            self.image = image
            self.refreshBitmap()

    def setDefaultImage(self):
        self.setImage(self.defaultImage)

    def setFrame(self, frame):
        if frame is not None:
            height, width = frame.shape[:2]
            self.setImage(wx.ImageFromBuffer(width, height, frame))

    def refreshBitmap(self):
        (w, h, self.xOffset, self.yOffset) = self.getBestSize()
        if w > 0 and h > 0:
            self.bitmap = wx.BitmapFromImage(self.image.Scale(w, h))
            self.Refresh()

    def getBestSize(self):
        (wwidth, wheight) = self.GetSizeTuple()
        (width, height) = self.image.GetSize()

        if height > 0 and wheight > 0:
            if float(width) / height > float(wwidth) / wheight:
                nwidth = wwidth
                nheight = float(wwidth * height) / width
                xoffset = 0
                yoffset = (wheight - nheight) / 2.0
            else:
                nwidth = float(wheight * width) / height
                nheight = wheight
                xoffset = (wwidth - nwidth) / 2.0
                yoffset = 0

            return (nwidth, nheight, xoffset, yoffset)
        else:
            return (0, 0, 0, 0)


class VideoView(ImageView):

    def __init__(self, parent, callback=None, milliseconds=1, size=(-1, -1)):
        ImageView.__init__(self, parent, size=size)

        self.callback = callback
        self.milliseconds = milliseconds

        self.playing = False

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

    def onTimer(self, event):
        self.timer.Stop()
        if self.playing:
            if self.callback is not None:
                self.setFrame(self.callback())
            self._start()

    def setMilliseconds(self, milliseconds):
        self.milliseconds = milliseconds

    def setCallback(self, callback):
        self.callback = callback

    def play(self):
        if not self.playing:
            self.playing = True
            self._start()

    def _start(self):
        self.timer.Start(milliseconds=self.milliseconds)

    def pause(self):
        self.playing = False
        self.timer.Stop()

    def stop(self):
        self.playing = False
        self.hide = True
        self.timer.Stop()
        self.setDefaultImage()
