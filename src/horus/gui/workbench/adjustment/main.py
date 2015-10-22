# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.util import profile

from horus.gui.engine import driver, image_capture

from horus.gui.workbench.workbench import Workbench
from horus.gui.workbench.adjustment.current_video import CurrentVideo
from horus.gui.workbench.adjustment.panels import ScanCapturePanel, ScanSegmentationPanel, \
    CalibrationCapturePanel, CalibrationSegmentationPanel


class AdjustmentWorkbench(Workbench):

    def __init__(self, parent):
        Workbench.__init__(self, parent, name=_('Adjustment workbench'))

        self.current_video = CurrentVideo()

    def add_panels(self):
        self.add_panel('scan_capture', ScanCapturePanel)
        self.add_panel('scan_segmentation', ScanSegmentationPanel)
        self.add_panel('calibration_capture', CalibrationCapturePanel)
        self.add_panel('calibration_segmentation', CalibrationSegmentationPanel)

    def setup_engine(self):
        resolution = profile.settings['resolution'].split('x')
        driver.camera.set_frame_rate(int(profile.settings['framerate']))
        driver.camera.set_resolution(int(resolution[1]), int(resolution[0]))
        image_capture.texture_mode.set_brightness(profile.settings['brightness_texture_scanning'])
        image_capture.texture_mode.set_contrast(profile.settings['contrast_texture_scanning'])
        image_capture.texture_mode.set_saturation(profile.settings['saturation_texture_scanning'])
        image_capture.texture_mode.set_exposure(profile.settings['exposure_texture_scanning'])
        image_capture.pattern_mode.set_brightness(
            profile.settings['brightness_pattern_calibration'])
        image_capture.pattern_mode.set_contrast(profile.settings['contrast_pattern_calibration'])
        image_capture.pattern_mode.set_saturation(
            profile.settings['saturation_pattern_calibration'])
        image_capture.pattern_mode.set_exposure(profile.settings['exposure_pattern_calibration'])
        image_capture.laser_mode.set_brightness(profile.settings['brightness_laser_scanning'])
        image_capture.laser_mode.set_contrast(profile.settings['contrast_laser_scanning'])
        image_capture.laser_mode.set_saturation(profile.settings['saturation_laser_scanning'])
        image_capture.laser_mode.set_exposure(profile.settings['exposure_laser_scanning'])
        image_capture.set_remove_background(profile.settings['remove_background_scanning'])
        image_capture.set_use_distortion(profile.settings['use_distortion'])

    def video_frame(self):
        return self.current_video.capture()
