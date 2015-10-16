# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx.lib.scrolledpanel

from horus.gui.util.imageView import VideoView
from horus.gui.util.customPanels import ExpandableControl

from horus.gui.workbench.workbench import WorkbenchConnection

from horus.gui.workbench.adjustment.current_video import CurrentVideo
from horus.gui.workbench.adjustment.panels import ScanCapturePanel, ScanSegmentationPanel, \
    CalibrationCapturePanel, CalibrationSegmentationPanel

from horus.engine.driver.driver import Driver
from horus.engine.algorithms.image_capture import ImageCapture
from horus.engine.algorithms.image_detection import ImageDetection


class AdjustmentWorkbench(WorkbenchConnection):

    def __init__(self, parent):
        WorkbenchConnection.__init__(self, parent)

        self.calibrating = False

        self.driver = Driver()
        self.image_capture = ImageCapture()
        self.image_detection = ImageDetection()
        self.current_video = CurrentVideo()

        self.toolbar.Realize()

        self.scrollPanel = wx.lib.scrolledpanel.ScrolledPanel(self._panel, size=(-1, -1))
        self.scrollPanel.SetupScrolling(scroll_x=False, scrollIntoView=False)
        self.scrollPanel.SetAutoLayout(1)

        self.controls = ExpandableControl(self.scrollPanel)

        self.video_image = None
        self.videoView = VideoView(self._panel, self.get_image, 10)
        self.videoView.SetBackgroundColour(wx.BLACK)

        # Add Scroll Panels
        self.controls.addPanel('scan_capture', ScanCapturePanel(self.controls))
        self.controls.addPanel('scan_segmentation', ScanSegmentationPanel(self.controls))
        self.controls.addPanel('calibration_capture', CalibrationCapturePanel(self.controls))
        self.controls.addPanel('calibration_segmentation',
                               CalibrationSegmentationPanel(self.controls))

        # Layout
        vsbox = wx.BoxSizer(wx.VERTICAL)
        vsbox.Add(self.controls, 0, wx.ALL | wx.EXPAND, 0)
        self.scrollPanel.SetSizer(vsbox)
        vsbox.Fit(self.scrollPanel)
        panel_size = self.scrollPanel.GetSize()[0] + wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
        self.scrollPanel.SetMinSize((panel_size, -1))

        self.controls.initPanels()

        self.addToPanel(self.scrollPanel, 0)
        self.addToPanel(self.videoView, 1)

        self.updateCallbacks()
        self.Layout()

    def updateCallbacks(self):
        self.controls.updateCallbacks()

    def get_image(self):
        return self.current_video.capture()

    def updateToolbarStatus(self, status):
        if status:
            if self.IsShown():
                self.videoView.play()
            self.controls.enableContent()
        else:
            self.videoView.stop()
            self.controls.disableContent()
            self.combo.Enable()
            self.controls.setExpandable(True)

    def updateProfileToAllControls(self):
        self.controls.updateProfile()
