# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.engine.driver.driver import Driver
from horus.engine.calibration.calibration import Calibration

driver = Driver()


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
        if driver.is_connected:

            response = None
            self.image = None

            # Setup scanner
            board.lasers_off()
            board.motor_enable()

            # Perform auto check
            try:
                self.check_pattern_and_motor()
                time.sleep(0.1)
                self.check_lasers()
                self.move_home()
            except Exception as e:
                response = str(e)
            finally:
                board.lasers_off()
                board.motor_disable()

            self.image = None

            self._is_calibrating = False

            if self._after_callback is not None:
                self._after_callback(response)

    def check_pattern_and_motor(self):
        scan_step = 30
        patterns_detected = {}
        patterns_sorted = {}

        # Setup scanner
        board.motor_speed(300)
        board.motor_acceleration(500)

        if self._progress_callback is not None:
            self._progress_callback(0)

        # Capture data
        for i in xrange(0, 360, scan_step):
            image = camera.capture_image(flush=1)
            self.image = image
            ret = solve_pnp(image)
            if ret is not None:
                patterns_detected[i] = ret[0].T[2][0]
            if self._progress_callback is not None:
                self._progress_callback(i / 4.)
            board.motor_relative(scan_step)
            board.motor_move()

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
        board.motor_relative(pos)
        board.motor_move()

    def check_lasers(self):
        img_raw = camera.capture_image(flush=1)
        self.image = img_raw

        if img_raw is not None:
            s = solve_pnp(img_raw)
            if s is not None:
                board.laser_left_on()
                img_las_left = camera.capture_image(flush=1)
                board.laser_left_off()
                board.laser_right_on()
                img_las_right = camera.capture_image(flush=1)
                board.laser_right_off()
                if img_las_left is not None and img_las_right is not None:
                    corners = s[2]

                    # Corners ROI mask
                    img_las_left = corners_mask(img_las_left, corners)
                    img_las_right = corners_mask(img_las_right, corners)

                    # Obtain Lines
                    detect_line(img_raw, img_las_left)
                    detect_line(img_raw, img_las_right)
            else:
                raise PatternNotDetected

    def move_home(self):
        # Setup pattern for the next calibration
        board.motor_relative(-90)
        board.motor_move()

        if self._progress_callback is not None:
            self._progress_callback(100)
