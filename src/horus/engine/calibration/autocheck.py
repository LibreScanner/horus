# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import time
import numpy as np

from horus import Singleton
from horus.engine.calibration.calibration import Calibration


class PatternNotDetected(Exception):

    def __init__(self):
        Exception.__init__(self, _("Pattern Not Detected"))


class WrongMotorDirection(Exception):

    def __init__(self):
        Exception.__init__(self, _("Wrong Motor Direction"))


class LaserNotDetected(Exception):

    def __init__(self):
        Exception.__init__(self, _("Laser Not Detected"))


class WrongLaserPosition(Exception):

    def __init__(self):
        Exception.__init__(self, _("Wrong Laser Position"))


@Singleton
class Autocheck(Calibration):

    """Auto check algorithm:
            - Check pattern detection
            - Check motor direction
            - Check lasers
    """

    def __init__(self):
        self.image = None
        Calibration.__init__(self)

    def _start(self):
        if self.driver.is_connected:

            response = None
            self.image = None
            self._is_calibrating = True
            self.image_capture._flush_pattern = 1

            # Setup scanner
            self.driver.board.lasers_off()
            self.driver.board.motor_enable()

            # Perform autocheck
            try:
                self.check_pattern_and_motor()
                time.sleep(0.1)
                self.check_lasers()
            except Exception as e:
                response = e
            finally:
                self.image = None
                self._is_calibrating = False
                self.image_capture._flush_pattern = 0
                self.driver.board.lasers_off()
                self.driver.board.motor_disable()
                if self._progress_callback is not None:
                    self._progress_callback(100)
                if self._after_callback is not None:
                    self._after_callback(response)

    def check_pattern_and_motor(self):
        scan_step = 30
        patterns_detected = {}
        patterns_sorted = {}

        # Setup scanner
        self.driver.board.motor_speed(300)
        self.driver.board.motor_acceleration(400)

        if self._progress_callback is not None:
            self._progress_callback(0)

        # Capture data
        for i in xrange(0, 360, scan_step):
            image = self.image_capture.capture_pattern()
            pose = self.image_detection.detect_pose(image)
            if pose is not None:
                self.image = self.image_detection.draw_pattern(image, pose[2])
                patterns_detected[i] = pose[0].T[2][0]
            else:
                self.image = self.image_detection.detect_pattern(image)
            if self._progress_callback is not None:
                self._progress_callback(i / 3.6)
            self.driver.board.motor_relative(scan_step)
            self.driver.board.motor_move()

        # Check pattern detection
        if len(patterns_detected) == 0:
            raise PatternNotDetected

        # Check motor direction
        max_x = max(patterns_detected.values())
        max_i = [key for key, value in patterns_detected.items() if value == max_x][0]
        min_v = max_x
        for i in xrange(max_i, max_i + 360, scan_step):
            if i % 360 in patterns_detected:
                v = patterns_detected[i % 360]
                patterns_sorted[i] = v
                if v <= min_v:
                    min_v = v
                else:
                    raise WrongMotorDirection

        # Move to nearest position
        x = np.array(patterns_sorted.keys())
        y = np.array(patterns_sorted.values())
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, y)[0]
        pos = -c / m
        if pos > 180:
            pos = pos - 360
        self.driver.board.motor_relative(pos)
        self.driver.board.motor_move()

    def check_lasers(self):
        for i in xrange(2):
            image = self.image_capture.capture_laser(i)
            self.image = image
            corners = self.image_detection.detect_corners(image)
            image = self.image_detection.pattern_mask(image, corners)
            lines = self.laser_segmentation.compute_hough_lines(image)
            if lines is None:
                raise LaserNotDetected
