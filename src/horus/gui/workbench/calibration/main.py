# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.util import profile

from horus.gui.engine import driver, pattern, image_capture, image_detection
from horus.gui.workbench.workbench import Workbench
from horus.gui.workbench.calibration.panels import PatternSettings, CameraIntrinsics, \
    ScannerAutocheck, LaserTriangulation, PlatformExtrinsics


class CalibrationWorkbench(Workbench):

    def __init__(self, parent):
        Workbench.__init__(self, parent, name=_('Calibration workbench'))

    def add_panels(self):
        self.add_panel('pattern_settings', PatternSettings)
        self.add_panel('camera_intrinsics', CameraIntrinsics)
        self.add_panel('scanner_autocheck', ScannerAutocheck)
        self.add_panel('laser_triangulation', LaserTriangulation)
        self.add_panel('platform_extrinsics', PlatformExtrinsics)

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
