# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import os
import wx._core

from horus.util import profile

from horus.engine.driver.driver import Driver

from horus.gui.wizard.connectionPage import ConnectionPage
from horus.gui.wizard.calibrationPage import CalibrationPage
from horus.gui.wizard.scanningPage import ScanningPage


class Wizard(wx.Dialog):

    def __init__(self, parent):
        super(Wizard, self).__init__(parent, title="", size=(760, 520))

        self.parent = parent
        self.driver = Driver()

        self.currentWorkbench = profile.settings['workbench']

        self.connectionPage = ConnectionPage(
            self,
            buttonPrevCallback=self.onConnectionPagePrevClicked,
            buttonNextCallback=self.onConnectionPageNextClicked)
        self.calibrationPage = CalibrationPage(
            self,
            buttonPrevCallback=self.onCalibrationPagePrevClicked,
            buttonNextCallback=self.onCalibrationPageNextClicked)
        self.scanningPage = ScanningPage(
            self,
            buttonPrevCallback=self.onScanningPagePrevClicked,
            buttonNextCallback=self.onScanningPageNextClicked)

        pages = [self.connectionPage, self.calibrationPage, self.scanningPage]

        self.connectionPage.intialize(pages)
        self.calibrationPage.intialize(pages)
        self.scanningPage.intialize(pages)

        self.connectionPage.Show()
        self.calibrationPage.Hide()
        self.scanningPage.Hide()

        self.driver.board.set_unplug_callback(lambda: wx.CallAfter(self.onBoardUnplugged))
        self.driver.camera.set_unplug_callback(lambda: wx.CallAfter(self.onCameraUnplugged))

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.connectionPage, 1, wx.ALL | wx.EXPAND, 0)
        hbox.Add(self.calibrationPage, 1, wx.ALL | wx.EXPAND, 0)
        hbox.Add(self.scanningPage, 1, wx.ALL | wx.EXPAND, 0)

        self.SetSizer(hbox)

        self.Bind(wx.EVT_CLOSE, lambda e: self.onExit())

        self.Centre()
        self.ShowModal()

    def onBoardUnplugged(self):
        self.onUnplugged()
        self.parent.onBoardUnplugged()
        self.connectionPage.updateStatus(False)
        self.calibrationPage.updateStatus(False)

    def onCameraUnplugged(self):
        self.onUnplugged()
        self.parent.onCameraUnplugged()
        self.connectionPage.updateStatus(False)
        self.calibrationPage.updateStatus(False)

    def onUnplugged(self):
        if hasattr(self.connectionPage, 'waitCursor'):
            del self.connectionPage.waitCursor
        if hasattr(self.calibrationPage, 'waitCursor'):
            del self.calibrationPage.waitCursor
        self.connectionPage.onUnplugged()
        self.calibrationPage.onUnplugged()
        self.connectionPage.Show()
        self.calibrationPage.Hide()
        self.scanningPage.Hide()

    def onExit(self):
        self.driver.board.lasers_off()
        profile.settings['workbench'] = self.currentWorkbench
        dlg = wx.MessageDialog(
            self, _("Do you really want to exit?"),
            _("Exit wizard"), wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
        result = dlg.ShowModal() == wx.ID_OK
        dlg.Destroy()
        if result:
            self.connectionPage.videoView.stop()
            self.calibrationPage.videoView.stop()
            self.scanningPage.videoView.stop()
            self.parent.workbenchUpdate()
            self.EndModal(wx.ID_OK)
            self.Destroy()

    def onConnectionPagePrevClicked(self):
        self.onExit()

    def onCalibrationPagePrevClicked(self):
        self.calibrationPage.Hide()
        self.connectionPage.Show()
        self.Layout()

    def onScanningPagePrevClicked(self):
        self.scanningPage.Hide()
        self.calibrationPage.Show()
        self.Layout()

    def onConnectionPageNextClicked(self):
        self.connectionPage.Hide()
        self.calibrationPage.Show()
        self.Layout()

    def onCalibrationPageNextClicked(self):
        self.calibrationPage.Hide()
        self.scanningPage.Show()
        self.Layout()

    def onScanningPageNextClicked(self):
        self.driver.board.lasers_off()
        profile.settings.saveSettings(categories=["scan_settings"])
        dlg = wx.MessageDialog(
            self,
            _("You have finished the wizard.\nPress Play button to start scanning."),
            _("Ready to scan!"), wx.OK | wx.ICON_INFORMATION)
        result = dlg.ShowModal() == wx.ID_OK
        dlg.Destroy()
        if result:
            self.connectionPage.videoView.stop()
            self.calibrationPage.videoView.stop()
            self.scanningPage.videoView.stop()
            profile.settings['workbench'] = u'Scanning workbench'
            self.parent.updateCalibrationProfile()
            self.parent.workbenchUpdate()
            self.EndModal(wx.ID_OK)
            self.Destroy()
