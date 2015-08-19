# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2

from horus import Singleton
from horus.engine.driver.driver import Driver
from horus.engine.calibration.pattern import Pattern
from horus.engine.algorithms.laser_segmentation import LaserSegmentation


class CameraSettings(object):

    def __init__(self):
        self.driver = Driver()
        self._enable = False
        self._brightness = 0
        self._contrast = 0
        self._saturation = 0
        self._exposure = 0

    def set_brightness(self, value):
        self._brightness = value
        if self._enable:
            self.driver.camera.set_brightness(value)

    def set_contrast(self, value):
        self._contrast = value
        if self._enable:
            self.driver.camera.set_contrast(value)

    def set_saturation(self, value):
        self._saturation = value
        if self._enable:
            self.driver.camera.set_saturation(value)

    def set_exposure(self, value):
        self._exposure = value
        if self._enable:
            self.driver.camera.set_exposure(value)


@Singleton
class ImageDetection(object):

    def __init__(self):
        self.driver = Driver()
        self.pattern = Pattern()
        self.laser_segmentation = LaserSegmentation()
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        self.segmentation = False
        self.pattern_mode = CameraSettings()
        self.laser_mode = CameraSettings()
        self.texture_mode = CameraSettings()

        self._mode = self.pattern_mode
        self._remove_background = True
        self._updating = False

    def set_pattern_mode(self):
        self._set_mode(self.pattern_mode)

    def set_laser_mode(self, segmentation=False):
        self.segmentation = segmentation
        self._set_mode(self.laser_mode)

    def set_texture_mode(self):
        self._set_mode(self.texture_mode)

    def _set_mode(self, mode):
        self._updating = True
        self._mode._enable = False
        self._mode = mode
        self._mode._enable = True
        self.driver.camera.set_brightness(self._mode._brightness)
        self.driver.camera.set_contrast(self._mode._contrast)
        self.driver.camera.set_saturation(self._mode._saturation)
        self.driver.camera.set_exposure(self._mode._exposure)
        self._updating = False

    def set_remove_background(self, value):
        self._remove_background = value

    def capture(self):
        # TODO: custom flush: detect system
        image = None

        if not self._updating:

            if self._mode is self.pattern_mode:
                self.driver.board.lasers_off()
                image = self.driver.camera.capture_image(flush=0)
                image = self.draw_chessboard(image)

            elif self._mode is self.texture_mode:
                self.driver.board.lasers_off()
                image = self.driver.camera.capture_image(flush=0)

            elif self._mode is self.laser_mode:
                self.driver.board.lasers_on()
                image = self.driver.camera.capture_image(flush=1)
                if self.segmentation:
                    image = self.laser_segmentation.obtain_red_channel(image)

                if self._remove_background:
                    self.driver.board.lasers_off()
                    img_no_laser = self.driver.camera.capture_image(flush=1)
                    if self.segmentation:
                        img_no_laser = self.laser_segmentation.obtain_red_channel(img_no_laser)
                    image = cv2.subtract(image, img_no_laser)

                if self.segmentation:
                    self.laser_segmentation.laser_segmentation(0, image)
                    image = self.laser_segmentation.get_image('gray', 0)

        return image

    def detect_chessboard(self, frame):
        if self.pattern.rows <= 2 or self.pattern.columns <= 2:
            return False, frame, None
        if frame is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(
                gray, (self.pattern.columns, self.pattern.rows), flags=cv2.CALIB_CB_FAST_CHECK)
            if ret:
                cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
            return ret, frame, corners
        else:
            return False, frame, None

    def draw_chessboard(self, frame):
        retval, frame, corners = self.detect_chessboard(frame)
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.drawChessboardCorners(
            frame, (self.pattern.columns, self.pattern.rows), corners, retval)
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
