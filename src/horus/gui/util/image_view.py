# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import resources


class ImageView(wx.Panel):

    def __init__(self, parent, resize=True, quality=wx.IMAGE_QUALITY_NORMAL,
                 size=(-1, -1), black=False, style=wx.NO_BORDER):
        wx.Panel.__init__(self, parent, size=size, style=style)

        self.x_offset = 0
        self.y_offset = 0
        self.quality = quality

        self.default_image = wx.Image(resources.get_path_for_image("nusb.png"))
        self.image = self.default_image
        self.bitmap = wx.BitmapFromImage(self.default_image)

        self.black = black
        self.frame = None
        self.current_size = self.GetSizeTuple()
        self.SetDoubleBuffered(True)

        self.Bind(wx.EVT_SHOW, self.on_show)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        if resize:
            self.Bind(wx.EVT_SIZE, self.on_resize)

        self.hide = False

    def on_show(self, event):
        if event.GetShow():
            self.GetParent().Layout()
            self.Layout()

    def on_paint(self, event):
        if not self.hide:
            if self.black:
                dc = wx.BufferedPaintDC(self)
                dc.SetBackground(wx.BLACK_BRUSH)
                dc.Clear()
            else:
                dc = wx.PaintDC(self)
            dc.DrawBitmap(self.bitmap, self.x_offset, self.y_offset)

    def on_resize(self, size):
        new_size = size.GetSize()
        if self.current_size != new_size:
            self.current_size = new_size
            self.refresh_bitmap()

    def set_image(self, image):
        if image is not None:
            if self.hide:
                self.hide = False
            self.image = image
            self.refresh_bitmap()

    def set_default_image(self):
        self.set_image(self.default_image)

    def set_frame(self, frame):
        self.frame = frame
        if frame is not None:
            height, width = frame.shape[:2]
            self.set_image(wx.ImageFromBuffer(width, height, frame))

    def refresh_bitmap(self):
        (w, h, self.x_offset, self.y_offset) = self.get_best_size()
        if w > 0 and h > 0:
            self.bitmap = wx.BitmapFromImage(self.image.Scale(w, h, self.quality))
            self.Refresh()

    def get_best_size(self):
        (wwidth, wheight) = self.current_size
        (width, height) = self.image.GetSize()

        if height > 0 and wheight > 0:
            if float(width) / height > float(wwidth) / wheight:
                nwidth = wwidth
                nheight = float(wwidth * height) / width
                x_offset = 0
                y_offset = (wheight - nheight) / 2.0
            else:
                nwidth = float(wheight * width) / height
                nheight = wheight
                x_offset = (wwidth - nwidth) / 2.0
                y_offset = 0
            return (nwidth, nheight, x_offset, y_offset)
        else:
            return (0, 0, 0, 0)
