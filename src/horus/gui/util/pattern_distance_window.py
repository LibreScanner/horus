# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Irene Sanz Nieto <irene.sanz@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
from horus.util import profile, resources

from horus.gui.engine import pattern


class PatternDistanceWindow(wx.Dialog):

    def __init__(self, parent):
        super(PatternDistanceWindow, self).__init__(
            parent, title=_("Pattern distance"),
            size=(420, -1), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        self.value = float(profile.settings['pattern_origin_distance'])

        # Elements
        self.description = wx.StaticText(self, label=_(
            "The pattern distance value must be higher than 0. "
            "Please change it in the textbox below."))
        self.description.Wrap(400)
        tooltip = _(
            "Minimum distance between the origin of the pattern (bottom-left corner) "
            "and the pattern's base surface (mm)")
        self.image = wx.Image(
            resources.get_path_for_image('pattern-distance.jpg'), wx.BITMAP_TYPE_ANY)
        self.image = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(self.image))
        self.image.SetToolTip(wx.ToolTip(tooltip))
        self.label = wx.StaticText(self, label=_("Pattern distance (mm)"))
        self.label.SetToolTip(wx.ToolTip(tooltip))
        self.text_box = wx.TextCtrl(
            self, value=str(profile.settings['pattern_origin_distance']))
        self.ok_button = wx.Button(self, label=_("Accept"))
        self.cancel_button = wx.Button(self, label=_("Cancel"))

        # Events
        self.text_box.Bind(wx.EVT_TEXT, self.on_text_box_changed)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_close)
        self.ok_button.Bind(wx.EVT_BUTTON, self.on_ok)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.description, 0, wx.ALL | wx.CENTER, 10)
        vbox.Add(self.image, 0, wx.ALL | wx.CENTER, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.label, 0, wx.ALL, 7)
        hbox.Add(self.text_box, 0, wx.ALL, 3)
        hbox.Add(self.ok_button, 0, wx.ALL, 3)
        hbox.Add(self.cancel_button, 0, wx.ALL, 3)
        vbox.Add(hbox, 0, wx.ALL | wx.CENTER, 10)
        self.SetSizer(vbox)
        self.CenterOnScreen()
        self.Fit()

        self.ShowModal()

    def on_text_box_changed(self, event):
        try:
            value = float(self.text_box.GetValue())
            if value >= 0:
                self.value = value
        except:
            pass

    def set_pattern_distance(self, distance):
        profile.settings['pattern_origin_distance'] = distance
        pattern.origin_distance = distance

    def on_ok(self, event):
        self.set_pattern_distance(self.value)
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def on_close(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()
