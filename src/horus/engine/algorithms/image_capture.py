# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2

from horus import Singleton
from horus.engine.driver.driver import Driver
from horus.engine.calibration.calibration_result import CalibrationResult


class CameraSettings(object):

    def __init__(self):
        self.driver = Driver()
        self.selected = False
        self._brightness = 0
        self._contrast = 0
        self._saturation = 0
        self._exposure = 0

    def set_brightness(self, value):
        self._brightness = value
        if selected:
            self.driver.camera.set_brightness(value)

    def set_contrast(self, value):
        self._contrast = value
        if selected:
            self.driver.camera.set_contrast(value)

    def set_saturation(self, value):
        self._saturation = value
        if selected:
            self.driver.camera.set_saturation(value)

    def set_exposure(self, value):
        self._exposure = value
        if selected:
            self.driver.camera.set_exposure(value)

    def send_all_settings(self):
        self.driver.camera.set_brightness(self._brightness)
        self.driver.camera.set_contrast(self._contrast)
        self.driver.camera.set_saturation(self._saturation)
        self.driver.camera.set_exposure(self._exposure)


@Singleton
class ImageCapture(object):

    def __init__(self):
        self.driver = Driver()
        self.calibration_result = CalibrationResult()

        self.pattern_mode = CameraSettings()
        self.laser_mode = CameraSettings()
        self.texture_mode = CameraSettings()

        # TODO: custom flush for each OS
        self._flush_pattern = 0
        self._flush_laser = 1
        self._flush_texture = 0
        self._mode = self.pattern_mode
        self._use_distortion = False
        self._remove_background = True
        self._updating = False

    def set_use_distortion(self, value):
        self._use_distortion = value

    def set_remove_background(self, value):
        self._remove_background = value

    def _set_mode(self, mode):
        if self._mode is not mode:
            self._updating = True
            self._mode.selected = False
            self._mode = mode
            self._mode.selected = True
            self._mode.send_all_settings()
            self._updating = False

    def capture_texture():
        self._set_mode(self.texture_mode)
        self.driver.board.lasers_off()
        image = self._capture_image(flush=self._flush_texture)
        return image

    def capture_laser(index):
        self._set_mode(self.laser_mode)
        self.driver.board.lasers_off()
        self.driver.board.laser_on(index)
        image = self._capture_image(flush=self._flush_laser)
        if self._remove_background:
            self.driver.board.lasers_off()
            image_background = self.capture_image(flush=self._flush_laser)
            if image is not None and image_background is not None:
                image = cv2.subtract(image, image_background)
        return image

    def capture_pattern():
        self._set_mode(self.pattern_mode)
        self.driver.board.lasers_off()
        image = self._capture_image(flush=self._flush_pattern)
        return image

    def _capture_image(self, flush=0):
        image = None
        if not self._updating:
            image = self.driver.camera.capture_image(flush=0)
            if self._use_distortion:
                if self.calibration_result.camera_matrix is not None and \
                   self.calibration_result.distortion_vector is not None and \
                   self.calibration_result.dist_camera_matrix is not None and \
                   self.calibration_result.roi is not None:
                    image = cv2.undistort(image,
                                          self.calibration_result.camera_matrix,
                                          self.calibration_result.distortion_vector,
                                          None,
                                          self.calibration_result.dist_camera_matrix)
                    x, y, w, h = self.calibration_result.roi
                    image = image[y:y + h, x:x + w]
        return image
