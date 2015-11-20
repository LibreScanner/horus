# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import profile

from horus.gui.util.video_view import VideoView
from horus.gui.util.scene_view import SceneView


class ViewPage(wx.SplitterWindow):

    def __init__(self, parent, get_image):
        wx.SplitterWindow.__init__(self, parent)

        self.get_image = get_image

        self.video_view = VideoView(self, get_image, 10, _reload=True)
        self.video_view.SetBackgroundColour(wx.BLACK)

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

        """# Video View Selector
        _choices = []
        choices = profile.settings.get_possible_values('video_scanning')
        for i in choices:
            _choices.append(_(i))
        self.videoViewsDict = dict(zip(_choices, choices))

        self.buttonShowVideoViews = wx.BitmapButton(self.videoView, wx.NewId(), wx.Bitmap(
            resources.get_path_for_image("views.png"), wx.BITMAP_TYPE_ANY), (10, 10))
        self.comboVideoViews = wx.ComboBox(self.videoView,
                                           value=_(profile.settings['video_scanning']),
                                           choices=_choices, style=wx.CB_READONLY, pos=(60, 10))

        self.buttonShowVideoViews.Hide()
        self.comboVideoViews.Hide()

        self.buttonShowVideoViews.Bind(wx.EVT_BUTTON, self.onShowVideoViews)
        self.comboVideoViews.Bind(wx.EVT_COMBOBOX, self.onComboBoVideoViewsSelect)"""

    def onShowVideoViews(self, event):
        self.show_video_views = not self.show_video_views
        if self.show_video_views:
            self.comboVideoViews.Show()
        else:
            self.comboVideoViews.Hide()

    def onComboBoVideoViewsSelect(self, event):
        value = self.videoViewsDict[self.comboVideoViews.GetValue()]
        current_video.mode = value
        profile.settings['video_scanning'] = value
