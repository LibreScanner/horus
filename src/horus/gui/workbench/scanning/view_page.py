# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import profile

from horus.gui.engine import driver, current_video

from horus.gui.util.video_view import VideoView
from horus.gui.util.scene_view import SceneView


class ViewPage(wx.SplitterWindow):

    def __init__(self, parent, get_image):
        wx.SplitterWindow.__init__(self, parent, style=wx.SP_3D)  # | wx.SP_LIVE_UPDATE)

        self.get_image = get_image

        self.video_view = VideoView(self, get_image)

        self.scene_panel = wx.Panel(self)
        self.scene_view = SceneView(self.scene_panel)
        self.gauge = wx.Gauge(self.scene_panel, size=(-1, 30))
        self.gauge.Hide()

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.scene_view, 1, wx.ALL | wx.EXPAND, 0)
        vbox.Add(self.gauge, 0, wx.ALL | wx.EXPAND, 0)
        self.scene_panel.SetSizer(vbox)

        self.SplitVertically(self.video_view, self.scene_panel)
        self.SetMinimumPaneSize(200)

        # Video view selector
        _choices = []
        choices = profile.settings.get_possible_values('video_scanning')
        for i in choices:
            _choices.append(_(i))
        self.video_views_dict = dict(zip(_choices, choices))
        self.combo_video_views = wx.ComboBox(self.video_view,
                                             value=_(u'Texture'),
                                             choices=_choices, style=wx.CB_READONLY,
                                             size=(100, -1), pos=(0, -1))
        self.combo_video_views.Hide()
        self.combo_video_views.Bind(wx.EVT_COMBOBOX, self.on_combo_box_video_views_select)

        # Events
        self.video_view.Bind(wx.EVT_SHOW, self.on_show)

    def on_show(self, event):
        if event.GetShow():
            if driver.is_connected and profile.settings['workbench'] == 'scanning':
                self.video_view.play()
        else:
            try:
                self.video_view.stop()
            except:
                pass

    def on_combo_box_video_views_select(self, event):
        value = self.video_views_dict[self.combo_video_views.GetValue()]
        current_video.mode = value
        profile.settings['video_scanning'] = value
