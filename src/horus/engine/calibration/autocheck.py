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
        Calibration.__init__(self)
        self.image = None

    def _start(self):
        if self.driver.is_connected:

            response = None
            self.image = None

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
        self.driver.board.motor_acceleration(500)

        if self._progress_callback is not None:
            self._progress_callback(0)

        # Capture data
        for i in xrange(0, 360, scan_step):
            image = self.driver.camera.capture_image(flush=1, rgb=False)
            self.image = image
            ret = self.solve_pnp(image)
            if ret is not None:
                patterns_detected[i] = ret[0].T[2][0]
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
        img_raw = self.driver.camera.capture_image(flush=1, rgb=False)
        self.image = img_raw

        if img_raw is not None:
            s = self.solve_pnp(img_raw)
            if s is not None:
                self.driver.board.laser_left_on()
                img_las_left = self.driver.camera.capture_image(flush=1)
                self.driver.board.laser_left_off()
                self.driver.board.laser_right_on()
                img_las_right = self.driver.camera.capture_image(flush=1)
                self.driver.board.laser_right_off()
                if img_las_left is not None and img_las_right is not None:
                    corners = s[2]

                    # Corners ROI mask
                    img_las_left = self.corners_mask(img_las_left, corners)
                    img_las_right = self.corners_mask(img_las_right, corners)

                    # Obtain Lines
                    self.detect_line(img_raw, img_las_left)
                    self.detect_line(img_raw, img_las_right)
            else:
                raise PatternNotDetected

    def detect_line(self, img_raw, img_las):
        height, width, depth = img_raw.shape
        img_line = np.zeros((height, width, depth), np.uint8)

        diff = cv2.subtract(img_las, img_raw)
        r, g, b = cv2.split(diff)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        r = cv2.morphologyEx(r, cv2.MORPH_OPEN, kernel)
        edges = cv2.threshold(r, 20.0, 255.0, cv2.THRESH_BINARY)[1]
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

        if lines is not None:
            rho, theta = lines[0][0]
            # Calculate coordinates
            u1 = rho / np.cos(theta)
            u2 = u1 - height * np.tan(theta)
            # TODO: use u1, u2
            #       WrongLaserPosition
        else:
            raise LaserNotDetected
