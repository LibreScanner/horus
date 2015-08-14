# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import numpy as np
from scipy.sparse import linalg

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

        self._pcl = None
        self._pcr = None

    def _capture(self, angle):
        """if system == 'Windows':
            flush = 2
        elif system == 'Darwin':
            flush = 2
        else:
            flush = 1"""
        flush = 1

        self.driver.camera.set_exposure(self.exposure_normal)
        img_raw = self.driver.camera.capture_image(flush=flush)

        ret = self.detect_pattern_plane(img_raw)

        if ret is not None:
            d, n, corners = ret

            # Image laser acquisition
            self.driver.camera.set_exposure(self.exposure_laser)

            img_raw = self.driver.camera.capture_image(flush=flush)

            self.driver.board.laser_left_on()
            img_las_left = self.driver.camera.capture_image(flush=flush)
            self.driver.board.laser_left_off()
            self.image = img_las_left
            if img_las_left is None:
                return

            self.driver.board.laser_right_on()
            img_las_right = self.driver.camera.capture_image(flush=flush)
            self.driver.board.laser_right_off()
            self.image = img_las_right
            if img_las_right is None:
                return

            # Pattern ROI mask
            img_las_raw = self.corners_mask(img_raw, corners)
            img_las_left = self.corners_mask(img_las_left, corners)
            img_las_right = self.corners_mask(img_las_right, corners)

            # Line segmentation
            uL, vL = self.compute_laser_line(img_las_left, img_las_raw)
            uR, vR = self.compute_laser_line(img_las_right, img_las_raw)

            # Point Cloud generation
            _pcl = self.compute_point_cloud(uL, vL, d, n)
            if _pcl is not None:
                if self._pcl is None:
                    self._pcl = _pcl
                else:
                    self._pcl = np.concatenate((self._pcl, _pcl))
            _pcr = self.compute_point_cloud(uR, vR, d, n)
            if _pcr is not None:
                if self._pcr is None:
                    self._pcr = _pcr
                else:
                    self._pcr = np.concatenate((self._pcr, _pcr))

            self.image = img_raw

    def _calibrate(self):
        # Restore camera exposure
        self.driver.camera.set_exposure(self.exposure_normal)

        # Save point clouds
        self.save_scene('PCL.ply', self._pcl)
        self.save_scene('PCR.ply', self._pcr)

        # Compute planes
        dL, nL, stdL = self.compute_plane(self._pcl, 'l')
        dR, nR, stdR = self.compute_plane(self._pcr, 'r')

        if self._is_calibrating and nL is not None and nR is not None:
            response = (True, ((dL, nL, stdL), (dR, nR, stdR)))
        else:
            if self._is_calibrating:
                response = (False, _("Calibration Error"))
            else:
                response = (False, _("Calibration Canceled"))

        self._is_calibrating = False

        return response

    def detect_pattern_plane(self, image):
        if image is not None:
            ret = self.solve_pnp(image)
            if ret is not None:
                R = ret[0]
                t = ret[1].T[0]
                n = R.T[2]
                c = ret[2]
                d = -np.dot(n, t)
                return (d, n, c)

    def compute_laser_line(self, img_las, img_raw):
        # Image segmentation
        sub = cv2.subtract(img_las, img_raw)
        r, g, b = cv2.split(sub)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        r = cv2.morphologyEx(r, cv2.MORPH_OPEN, kernel)
        r = cv2.threshold(r, self.threshold, 255.0, cv2.THRESH_TOZERO)[1]

        # Peak detection: center of mass
        h, w = r.shape
        W = np.array((np.matrix(np.linspace(0, w - 1, w)).T * np.matrix(np.ones(h))).T)
        s = r.sum(axis=1)
        v = np.where(s > 0)[0]
        u = (W * r).sum(axis=1)[v] / s[v]

        return u, v

    def compute_point_cloud(self, u, v, d, n):
        fx = self.driver.camera.camera_matrix[0][0]
        fy = self.driver.camera.camera_matrix[1][1]
        cx = self.driver.camera.camera_matrix[0][2]
        cy = self.driver.camera.camera_matrix[1][2]

        x = np.concatenate(((u - cx) / fx, (v - cy) / fy, np.ones(len(u)))).reshape(3, len(u))

        X = -d / np.dot(n, x) * x

        return X.T

    def compute_plane(self, X, side):
        if X is not None:
            X = np.matrix(X).T
            n = X.shape[1]
            std = 0
            if n > 3:
                final_points = []

                for trials in xrange(30):
                    X = np.matrix(X)
                    n = X.shape[1]

                    Xm = X.sum(axis=1) / n
                    M = np.array(X - Xm)
                    U = linalg.svds(M, k=2)[0]
                    s, t = U.T
                    n = np.cross(s, t)
                    if n[2] < 0:
                        n *= -1
                    d = np.dot(n, np.array(Xm))[0]
                    distance_vector = np.dot(M.T, n)

                    # If last std is equal to current std, break loop
                    if std == distance_vector.std():
                        break

                    std = distance_vector.std()

                    final_points = np.where(abs(distance_vector) < abs(2 * std))[0]

                    X = X[:, final_points]

                    if std < 0.1 or len(final_points) < 1000:
                        break

                return d, n, std
            else:
                return None, None, None
        else:
            return None, None, None
