# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.gui.wizard.wizardPage import WizardPage

from horus.util import profile

from horus.engine.driver.driver import Driver
from horus.engine.scan.ciclop_scan import CiclopScan
from horus.engine.algorithms.image_capture import ImageCapture


class ScanningPage(WizardPage):

    def __init__(self, parent, buttonPrevCallback=None, buttonNextCallback=None):
        WizardPage.__init__(self, parent,
                            title=_("Scanning"),
                            buttonPrevCallback=buttonPrevCallback,
                            buttonNextCallback=buttonNextCallback)

        self.driver = Driver()
        self.ciclop_scan = CiclopScan()
        self.image_capture = ImageCapture()

        value = abs(float(profile.settings['motor_step_scanning']))
        if value > 1.35:
            value = _("Low")
        elif value > 0.625:
            value = _("Medium")
        else:
            value = _("High")
        self.resolutionLabel = wx.StaticText(self.panel, label=_(u"Resolution (º)"))
        self.resolutionComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
                                              value=value,
                                              choices=[_("High"), _("Medium"), _("Low")],
                                              style=wx.CB_READONLY)

        _choices = []
        choices = profile.settings.getPossibleValues('use_laser')
        for i in choices:
            _choices.append(_(i))
        self.laserDict = dict(zip(_choices, choices))
        self.laserLabel = wx.StaticText(self.panel, label=_("Use laser"))
        self.laserComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
                                         value=_(profile.settings['use_laser']),
                                         choices=_choices,
                                         style=wx.CB_READONLY)

        self.skipButton.Hide()

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.resolutionLabel, 0, wx.ALL ^ wx.BOTTOM | wx.EXPAND, 18)
        hbox.Add(self.resolutionComboBox, 1, wx.ALL ^ wx.BOTTOM | wx.EXPAND, 12)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.laserLabel, 0, wx.ALL ^ wx.BOTTOM | wx.EXPAND, 18)
        hbox.Add(self.laserComboBox, 1, wx.ALL ^ wx.BOTTOM | wx.EXPAND, 12)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 5)
        self.panel.SetSizer(vbox)
        self.Layout()

        self.resolutionComboBox.Bind(wx.EVT_COMBOBOX, self.onResolutionComboBoxChanged)
        self.laserComboBox.Bind(wx.EVT_COMBOBOX, self.onLaserComboBoxChanged)
        self.Bind(wx.EVT_SHOW, self.onShow)

        self.videoView.setMilliseconds(10)
        self.videoView.setCallback(self.get_image)

    def onShow(self, event):
        if event.GetShow():
            self.updateStatus(self.driver.is_connected)
        else:
            try:
                self.videoView.stop()
            except:
                pass

    def onResolutionComboBoxChanged(self, event):
        value = event.GetEventObject().GetValue()
        if value == _("High"):
            value = -0.45
        elif value == _("Medium"):
            value = -0.9
        elif value == _("Low"):
            value = -1.8
        profile.settings['motor_step_scanning'] = value
        self.ciclop_scan.motor_step = value

    def onLaserComboBoxChanged(self, event):
        value = self.laserDict[event.GetEventObject().GetValue()]
        profile.settings['use_laser'] = value
        useLeft = value == 'Left' or value == 'Both'
        useRight = value == 'Right' or value == 'Both'
        if useLeft:
            self.driver.board.laser_on(0)
        else:
            self.driver.board.laser_off(0)

        if useRight:
            self.driver.board.laser_on(1)
        else:
            self.driver.board.laser_off(1)
        self.ciclop_scan.set_use_left_laser(useLeft)
        self.ciclop_scan.set_use_right_laser(useRight)

    def get_image(self):
        return self.image_capture.capture_texture()

    def updateStatus(self, status):
        if status:
            profile.settings['workbench'] = u'Scanning workbench'
            self.GetParent().parent.workbenchUpdate(False)
            self.videoView.play()
            value = profile.settings['use_laser']
            if value == 'Left':
                self.driver.board.laser_on(0)
                self.driver.board.laser_off(1)
            elif value == 'Right':
                self.driver.board.laser_off(0)
                self.driver.board.laser_on(1)
            elif value == 'Both':
                self.driver.board.lasers_on()
        else:
            self.videoView.stop()
