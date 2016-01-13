# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import platform

from horus import Singleton
from horus.engine.driver.driver import Driver
from horus.engine.calibration.calibration_data import CalibrationData

system = platform.system()


class CameraSettings(object):

    def __init__(self):
        self.driver = Driver()

        self.selected = False
        self.brightness = 0
        self.contrast = 0
        self.saturation = 0
        self.exposure = 0

    def set_brightness(self, value):
        self.brightness = value
        if self.selected:
            self.driver.camera.set_brightness(value)

    def set_contrast(self, value):
        self.contrast = value
        if self.selected:
            self.driver.camera.set_contrast(value)

    def set_saturation(self, value):
        self.saturation = value
        if self.selected:
            self.driver.camera.set_saturation(value)

    def set_exposure(self, value):
        self.exposure = value
        if self.selected:
            self.driver.camera.set_exposure(value)

    def send_all_settings(self):
        self.driver.camera.set_brightness(self.brightness)
        self.driver.camera.set_contrast(self.contrast)
        self.driver.camera.set_saturation(self.saturation)
        self.driver.camera.set_exposure(self.exposure)


@Singleton
class ImageCapture(object):

    def __init__(self):
        self.driver = Driver()
        self.calibration_data = CalibrationData()

        self.texture_mode = CameraSettings()
        self.laser_mode = CameraSettings()
        self.pattern_mode = CameraSettings()

        self.stream = True
        if system == 'Linux':
            self._flush_texture = 2
            self._flush_laser = 2  # exp < 32 ? 2 : 3
            self._flush_pattern = 2
            self._flush_stream_texture = 0
            self._flush_stream_laser = 2
            self._flush_stream_pattern = 0
        elif system == 'Darwin':
            self._flush_texture = 2
            self._flush_laser = 2  # exp < 32 ? 2 : 3
            self._flush_pattern = 2
            self._flush_stream_texture = 0
            self._flush_stream_laser = 2
            self._flush_stream_pattern = 0
        elif system == 'Windows':
            self._flush_texture = 2
            self._flush_laser = 2  # exp < 32 ? 2 : 3
            self._flush_pattern = 2
            self._flush_stream_texture = 0
            self._flush_stream_laser = 2
            self._flush_stream_pattern = 0

        self._mode = self.pattern_mode
        self._mode.selected = True
        self._remove_background = True
        self._updating = False
        self.use_distortion = False

    def initialize(self):
        self.texture_mode.initialize()
        self.laser_mode.initialize()
        self.pattern_mode.initialize()

    def set_use_distortion(self, value):
        self.use_distortion = value

    def set_remove_background(self, value):
        self._remove_background = value

    def set_mode(self, mode):
        if self._mode is not mode:
            self._updating = True
            self._mode.selected = False
            self._mode = mode
            self._mode.selected = True
            self._mode.send_all_settings()
            self._updating = False

    def set_mode_texture(self):
        self.set_mode(self.texture_mode)

    def set_mode_laser(self):
        self.set_mode(self.laser_mode)

    def set_mode_pattern(self):
        self.set_mode(self.pattern_mode)

    def capture_texture(self):
        self.set_mode(self.texture_mode)
        # self.driver.board.lasers_off()
        if self.stream:
            flush = self._flush_stream_texture
        else:
            flush = self._flush_texture
        image = self.capture_image(flush=flush)
        return image

    # TODO: slow with laser

    def _capture_laser(self, index):
        self.set_mode(self.laser_mode)
        self.driver.board.lasers_off()
        self.driver.board.laser_on(index)
        if self.stream:
            flush = self._flush_stream_laser
        else:
            flush = self._flush_laser
        return self.capture_image(flush=flush)

    def capture_laser(self, index):
        image = self._capture_laser(index)
        if self._remove_background:
            self.driver.board.lasers_off()
            if self.stream:
                flush = self._flush_stream_laser
            else:
                flush = self._flush_laser
            image_background = self.capture_image(flush=flush)
            if image is not None and image_background is not None:
                image = cv2.subtract(image, image_background)
        return image

    def capture_lasers(self):
        images = [None, None]
        images[0] = self._capture_laser(0)
        images[1] = self._capture_laser(1)
        if self._remove_background:
            self.driver.board.lasers_off()
            if self.stream:
                flush = self._flush_stream_laser
            else:
                flush = self._flush_laser
            image_background = self.capture_image(flush=flush)
            if image_background is not None:
                if images[0] is not None:
                    images[0] = cv2.subtract(images[0], image_background)
                if images[1] is not None:
                    images[1] = cv2.subtract(images[1], image_background)
        return images

    def capture_all_lasers(self):
        self.set_mode(self.laser_mode)
        self.driver.board.lasers_on()
        if self.stream:
            flush = self._flush_stream_laser
        else:
            flush = self._flush_laser
        image = self.capture_image(flush=flush)
        if self._remove_background:
            self.driver.board.lasers_off()
            image_background = self.capture_image(flush=flush)
            if image is not None and image_background is not None:
                image = cv2.subtract(image, image_background)
        return image

    def capture_pattern(self):
        self.set_mode(self.pattern_mode)
        # self.driver.board.lasers_off()
        if self.stream:
            flush = self._flush_stream_pattern
        else:
            flush = self._flush_pattern
        image = self.capture_image(flush=flush)
        return image

    def capture_image(self, flush=0):
        image = self.driver.camera.capture_image(flush=flush)
        if self.use_distortion:
            if self.calibration_data.camera_matrix is not None and \
               self.calibration_data.distortion_vector is not None and \
               self.calibration_data.dist_camera_matrix is not None and \
               self.calibration_data.roi is not None:
                image = cv2.undistort(image,
                                      self.calibration_data.camera_matrix,
                                      self.calibration_data.distortion_vector,
                                      None,
                                      self.calibration_data.dist_camera_matrix)
                x, y, w, h = self.calibration_data.roi
                image = image[y:y + h + 1, x:x + w + 1]
        return image
