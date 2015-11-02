# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import profile

from horus.gui.engine import driver, pattern, image_capture, image_detection
from horus.gui.workbench.workbench import Workbench
from horus.gui.workbench.calibration.panels import PatternSettings, CameraIntrinsics, \
    ScannerAutocheck, LaserTriangulation, PlatformExtrinsics

from horus.gui.workbench.calibration.pages.camera_intrinsics import CameraIntrinsicsPages
from horus.gui.workbench.calibration.pages.scanner_autocheck import ScannerAutocheckPages
from horus.gui.workbench.calibration.pages.laser_triangulation import LaserTriangulationPages
from horus.gui.workbench.calibration.pages.platform_extrinsics import PlatformExtrinsicsPages


class CalibrationWorkbench(Workbench):

    def __init__(self, parent):
        Workbench.__init__(self, parent, name=_('Calibration workbench'))

    def add_panels(self):
        self.add_panel('pattern_settings', PatternSettings,
                       self.on_pattern_settings_selected)
        self.add_panel('camera_intrinsics', CameraIntrinsics,
                       self.on_camera_intrinsics_selected)
        self.add_panel('scanner_autocheck', ScannerAutocheck,
                       self.on_scanner_autocheck_selected)
        self.add_panel('laser_triangulation', LaserTriangulation,
                       self.on_laser_triangulation_selected)
        self.add_panel('platform_extrinsics', PlatformExtrinsics,
                       self.on_platform_extrinsics_selected)

        # Add pages
        self.camera_intrinsics_pages = CameraIntrinsicsPages(self,
            start_callback=self.disable_panels, exit_callback=self.update_panels)
        self.scanner_autocheck_pages = ScannerAutocheckPages(self)
        self.laser_triangulation_pages = LaserTriangulationPages(self)
        self.platform_extrinsics_pages = PlatformExtrinsicsPages(self)

        self.hbox.Add(self.camera_intrinsics_pages, 1, wx.ALL | wx.EXPAND, 1)
        self.hbox.Add(self.scanner_autocheck_pages, 1, wx.ALL | wx.EXPAND, 1)
        self.hbox.Add(self.laser_triangulation_pages, 1, wx.ALL | wx.EXPAND, 1)
        self.hbox.Add(self.platform_extrinsics_pages, 1, wx.ALL | wx.EXPAND, 1)

        self.camera_intrinsics_pages.Hide()
        self.scanner_autocheck_pages.Hide()
        self.laser_triangulation_pages.Hide()
        self.platform_extrinsics_pages.Hide()

    def setup_engine(self):
        resolution = profile.settings['resolution'].split('x')
        driver.camera.set_frame_rate(int(profile.settings['framerate']))
        driver.camera.set_resolution(int(resolution[1]), int(resolution[0]))
        image_capture.set_mode_pattern()
        image_capture.pattern_mode.set_brightness(
            profile.settings['brightness_pattern_calibration'])
        image_capture.pattern_mode.set_contrast(profile.settings['contrast_pattern_calibration'])
        image_capture.pattern_mode.set_saturation(
            profile.settings['saturation_pattern_calibration'])
        image_capture.pattern_mode.set_exposure(profile.settings['exposure_pattern_calibration'])
        image_capture.set_use_distortion(profile.settings['use_distortion'])
        pattern.rows = profile.settings['pattern_rows']
        pattern.columns = profile.settings['pattern_columns']
        pattern.square_width = profile.settings['pattern_square_width']
        pattern.origin_distance = profile.settings['pattern_origin_distance']

    def video_frame(self):
        image = image_capture.capture_pattern()
        return image_detection.detect_pattern(image)

    def on_pattern_settings_selected(self):
        self._on_panel_selected(self.video_view)

    def on_camera_intrinsics_selected(self):
        self._on_panel_selected(self.camera_intrinsics_pages)

    def on_scanner_autocheck_selected(self):
        self._on_panel_selected(self.scanner_autocheck_pages)

    def on_laser_triangulation_selected(self):
        self._on_panel_selected(self.laser_triangulation_pages)

    def on_platform_extrinsics_selected(self):
        self._on_panel_selected(self.platform_extrinsics_pages)

    def disable_panels(self):
        pass

    def update_panels(self):
        pass

    def _on_panel_selected(self, panel):
        self.video_view.Hide()
        self.camera_intrinsics_pages.Hide()
        self.scanner_autocheck_pages.Hide()
        self.laser_triangulation_pages.Hide()
        self.platform_extrinsics_pages.Hide()
        panel.Show()
        self.Layout()
