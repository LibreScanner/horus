# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Irene Sanz Nieto <irene.sanz@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
from horus.util import profile, resources

from horus.engine.calibration.pattern import Pattern


class PatternDistanceWindow(wx.Dialog):

    def __init__(self, parent):
        super(PatternDistanceWindow, self).__init__(
            parent, title=_('Pattern distance'),
            size=(420, -1), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        self.value = float(profile.getProfileSetting('pattern_origin_distance'))
        self.pattern = Pattern()

        # Elements
        self.description = wx.StaticText(self, label=_(
            'Pattern distance value must be a number higher than 0. '
            'Please, change it in the textbox below.'))
        self.description.Wrap(400)
        tooltip = _(
            "Minimum distance between the origin of the pattern (bottom-left corner) "
            "and the pattern's base surface")
        self.image = wx.Image(
            resources.getPathForImage("pattern-distance.jpg"), wx.BITMAP_TYPE_ANY)
        self.patternImage = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(self.image))
        self.patternImage.SetToolTip(wx.ToolTip(tooltip))
        self.patternLabel = wx.StaticText(self, label=_('Pattern distance (mm)'))
        self.patternLabel.SetToolTip(wx.ToolTip(tooltip))
        self.patternTextbox = wx.TextCtrl(
            self, value=str(profile.getProfileSettingFloat('pattern_origin_distance')))
        self.okButton = wx.Button(self, label=_('OK'))
        self.cancelButton = wx.Button(self, label=_('Cancel'))

        # Events
        self.patternTextbox.Bind(wx.EVT_TEXT, self.onTextBoxChanged)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onClose)
        self.okButton.Bind(wx.EVT_BUTTON, self.onOk)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.description, 0, wx.ALL | wx.CENTER, 10)
        vbox.Add(self.patternImage, 0, wx.ALL | wx.CENTER, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.patternLabel, 0, wx.ALL, 7)
        hbox.Add(self.patternTextbox, 0, wx.ALL, 3)
        hbox.Add(self.okButton, 0, wx.ALL, 3)
        hbox.Add(self.cancelButton, 0, wx.ALL, 3)
        vbox.Add(hbox, 0, wx.ALL | wx.CENTER, 10)
        self.SetSizer(vbox)
        self.Center()
        self.Fit()

        self.ShowModal()

    def onTextBoxChanged(self, event):
        try:
            value = float(self.patternTextbox.GetValue())
            if value >= 0:
                self.value = value
        except:
            pass

    def setPatternDistance(self, distance):
        profile.putProfileSetting('pattern_origin_distance', distance)
        self.pattern.distance = distance

    def onOk(self, event):
        self.setPatternDistance(self.value)
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def onClose(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()
