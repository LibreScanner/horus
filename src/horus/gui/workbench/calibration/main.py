# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.util import profile

from horus.gui.engine import driver, pattern, calibration_data, image_capture, image_detection
from horus.gui.util.video_view import VideoView
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
        self.add_panel(
            'pattern_settings', PatternSettings, self.on_pattern_settings_selected)
        self.add_panel(
            'camera_intrinsics', CameraIntrinsics, self.on_camera_intrinsics_selected)
        self.add_panel(
            'scanner_autocheck', ScannerAutocheck, self.on_scanner_autocheck_selected)
        self.add_panel(
            'laser_triangulation', LaserTriangulation, self.on_laser_triangulation_selected)
        """self.add_panel('platform_extrinsics', PlatformExtrinsics,
                       self.on_platform_extrinsics_selected)"""

        # Add pages
        """self.platform_extrinsics_pages = PlatformExtrinsicsPages(self)"""
        """
        self.hbox.Add(self.platform_extrinsics_pages, 1, wx.ALL | wx.EXPAND, 1)"""

        """
        self.platform_extrinsics_pages.Hide()"""

    def add_pages(self):
        self.add_page('video_view', VideoView(self, self._video_frame, 10, black=True))
        self.add_page('camera_intrinsics_pages', CameraIntrinsicsPages(
            self, start_callback=self.disable_panels, exit_callback=self.update_panels))
        self.add_page('scanner_autocheck_pages', ScannerAutocheckPages(
            self, start_callback=self.disable_panels, exit_callback=self.update_panels))
        self.add_page('laser_triangulation_pages', LaserTriangulationPages(
            self, start_callback=self.disable_panels, exit_callback=self.update_panels))

        self.pages_collection['camera_intrinsics_pages'].Hide()
        self.pages_collection['scanner_autocheck_pages'].Hide()
        self.pages_collection['laser_triangulation_pages'].Hide()

        self.panels_collection.expandable_panels[
            profile.settings['current_panel_calibration']].on_title_clicked(None)

    def _video_frame(self):
        image = image_capture.capture_pattern()
        return image_detection.detect_pattern(image)

    def on_open(self):
        self.panels_collection.expandable_panels[
            profile.settings['current_panel_calibration']].on_title_clicked(None)

    def on_close(self):
        try:
            self.pages_collection['video_view'].stop()
            self.pages_collection['camera_intrinsics_pages'].on_show(False)
            self.pages_collection['scanner_autocheck_pages'].on_show(False)
            self.pages_collection['laser_triangulation_pages'].on_show(False)
        except:
            pass

    def setup_engine(self):
        resolution = profile.settings['resolution'].split('x')
        driver.camera.set_frame_rate(int(profile.settings['framerate']))
        driver.camera.set_resolution(int(resolution[1]), int(resolution[0]))
        image_capture.set_mode_pattern()
        pattern_mode = image_capture.pattern_mode
        pattern_mode.set_brightness(profile.settings['brightness_pattern_calibration'])
        pattern_mode.set_contrast(profile.settings['contrast_pattern_calibration'])
        pattern_mode.set_saturation(profile.settings['saturation_pattern_calibration'])
        pattern_mode.set_exposure(profile.settings['exposure_pattern_calibration'])
        image_capture.set_use_distortion(profile.settings['use_distortion'])
        pattern.rows = profile.settings['pattern_rows']
        pattern.columns = profile.settings['pattern_columns']
        pattern.square_width = profile.settings['pattern_square_width']
        pattern.origin_distance = profile.settings['pattern_origin_distance']
        calibration_data.set_resolution(int(resolution[1]), int(resolution[0]))
        calibration_data.camera_matrix = profile.settings['camera_matrix']
        calibration_data.distortion_vector = profile.settings['distortion_vector']

    def on_pattern_settings_selected(self):
        profile.settings['current_panel_calibration'] = 'pattern_settings'
        self._on_panel_selected(self.pages_collection['video_view'])
        self.pages_collection['video_view'].play()

    def on_camera_intrinsics_selected(self):
        profile.settings['current_panel_calibration'] = 'camera_intrinsics'
        self._on_panel_selected(self.pages_collection['camera_intrinsics_pages'])

    def on_scanner_autocheck_selected(self):
        profile.settings['current_panel_calibration'] = 'scanner_autocheck'
        self._on_panel_selected(self.pages_collection['scanner_autocheck_pages'])

    def on_laser_triangulation_selected(self):
        profile.settings['current_panel_calibration'] = 'laser_triangulation'
        self._on_panel_selected(self.pages_collection['laser_triangulation_pages'])

    def on_platform_extrinsics_selected(self):
        self._on_panel_selected(self.platform_extrinsics_pages)

    def disable_panels(self):
        self.panels_collection.Disable()
        self.GetParent().toolbar.combo.Disable()
        for i in range(4):
            self.GetParent().menu_bar.EnableTop(i, False)

    def update_panels(self):
        self.panels_collection.Enable()
        self.GetParent().toolbar.combo.Enable()
        for i in range(4):
            self.GetParent().menu_bar.EnableTop(i, True)
        self.panels_collection.update_from_profile()

    def _on_panel_selected(self, panel):
        self.pages_collection['video_view'].Hide()
        self.pages_collection['video_view'].stop()
        self.pages_collection['camera_intrinsics_pages'].Hide()
        self.pages_collection['scanner_autocheck_pages'].Hide()
        self.pages_collection['laser_triangulation_pages'].Hide()
        """self.platform_extrinsics_pages.Hide()"""
        panel.Show()
        self.Layout()
