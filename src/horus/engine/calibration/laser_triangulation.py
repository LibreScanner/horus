# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus import Singleton
from horus.engine.calibration.moving_calibration import MovingCalibration


@Singleton
class LaserTriangulation(MovingCalibration):

    """Laser triangulation algorithm:

            - Laser coordinates matrix
            - Pattern's origin
            - Pattern's normal
    """

    def __init__(self):
        MovingCalibration.__init__(self)
        self.image = None
        self.threshold = 0
        self.exposure_laser = 0
        self.exposure_normal = 0

    def _start(self):
        XL = None
        XR = None
        step = 5
        angle = 0

        if system == 'Windows':
            flush = 2
        elif system == 'Darwin':
            flush = 2
        else:
            flush = 1

        if driver.is_connected:
            # Setup scanner
            board.lasers_off()
            board.motor_enable()
            board.motor_speed(200)
            board.motor_acceleration(200)
            time.sleep(0.1)

            if self._progress_callback is not None:
                self._progress_callback(0)

            while self._is_calibrating and abs(angle) < 180:

                if self._progress_callback is not None:
                    self._progress_callback(1.11 * abs(angle / 2.))

                angle += step

                camera.set_exposure(self.exposure_normal)
                img_raw = camera.capture_image(flush=flush)
                self.image = img_raw
                ret = detect_pattern_plane(img_raw)

                if ret is not None:
                    step = 5  # 2

                    d, n, corners = ret

                    # Image laser acquisition
                    camera.set_exposure(self.exposure_laser)

                    img_raw_left = camera.capture_image(flush=flush)
                    board.laser_left_on()
                    img_las_left = camera.capture_image(flush=flush)
                    board.laser_left_off()
                    self.image = img_las_left
                    if img_las_left is None:
                        break

                    img_raw_right = camera.capture_image(flush=flush)
                    board.laser_right_on()
                    img_las_right = camera.capture_image(flush=flush)
                    board.laser_right_off()
                    self.image = img_las_right
                    if img_las_right is None:
                        break

                    # Pattern ROI mask
                    img_las_left = corners_mask(img_las_left, corners)
                    img_raw_left = corners_mask(img_raw_left, corners)
                    img_las_right = corners_mask(img_las_right, corners)
                    img_raw_right = corners_mask(img_raw_right, corners)

                    # Line segmentation
                    uL, vL = compute_laser_line(img_las_left, img_raw_left, self.threshold)
                    uR, vR = compute_laser_line(img_las_right, img_raw_right, self.threshold)

                    # Point Cloud generation
                    xL = compute_point_cloud(uL, vL, d, n)
                    if xL is not None:
                        if XL is None:
                            XL = xL
                        else:
                            XL = np.concatenate((XL, xL))
                    xR = compute_point_cloud(uR, vR, d, n)
                    if xR is not None:
                        if XR is None:
                            XR = xR
                        else:
                            XR = np.concatenate((XR, xR))
                else:
                    step = 5
                    self.image = img_raw

                self.image = img_raw

                board.motor_relative(step)
                board.motor_move()
                time.sleep(0.1)

            # self.save_scene('XL.ply', XL)
            # self.save_scene('XR.ply', XR)

            # Compute planes
            dL, nL, stdL = compute_plane(XL, 'l')
            dR, nR, stdR = compute_plane(XR, 'r')

        board.lasers_off()
        board.motor_disable()

        # Restore camera exposure
        camera.set_exposure(self.exposure_normal)

        self.image = None

        if self._is_calibrating and nL is not None and nR is not None:
            response = (True, ((dL, nL, stdL), (dR, nR, stdR)))
            self.move_home()
        else:
            if self._is_calibrating:
                response = (False, _("Calibration Error"))
            else:
                response = (False, _("Calibration Canceled"))

        self._is_calibrating = False

        if self._after_callback is not None:
            self._after_callback(response)

    def move_home(self):
        # Restart pattern position
        board.motor_relative(-180)
        board.motor_move()

        if self._progress_callback is not None:
            self._progress_callback(100)
