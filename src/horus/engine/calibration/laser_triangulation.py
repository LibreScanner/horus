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


class LaserTriangulationError(Exception):

    def __init__(self):
        Exception.__init__(self, _("LaserTriangulationError"))


class LaserTriangulationCancel(Exception):

    def __init__(self):
        Exception.__init__(self, _("LaserTriangulationCancel"))


@Singleton
class LaserTriangulation(MovingCalibration):

    """Laser triangulation algorithm:

            - Laser coordinates matrix
            - Pattern's origin
            - Pattern's normal
    """

    def __init__(self):
        MovingCalibration.__init__(self)

    def _initialize(self):
        self._point_cloud = [None, None]

    def _capture(self, angle):
        image = self.image_capture.capture_pattern()
        if image is not None:
            d, n, corners = self.image_detect.detect_pattern_plane(image)
            for i in xrange(2):
                image = self.image_capture.capture_laser(i)
                image = self.image_detect.pattern_mask(image, corners)
                points_2d = self.laser_segmentation.compute_2d_points(image)
                point_3d = self.point_cloud_generation.compute_camera_point_cloud(points_2d, d, n)
                if self._point_cloud[i] is None:
                    self._point_cloud[i] = point_3d
                else:
                    self._point_cloud[i] = np.concatenate((self._point_cloud[i], point_3d))

    def _calibrate(self):
        # Save point clouds
        #for i in xrange(2):
        #    self.save_scene('PC'+str(i)+'.ply', self._point_cloud[i])

        # TODO: use arrays
        # Compute planes
        dL, nL, stdL = self.compute_plane(self._point_cloud[0])
        dR, nR, stdR = self.compute_plane(self._point_cloud[1])

        if self._is_calibrating and nL is not None and nR is not None:
            response = (True, ((dL, nL, stdL), (dR, nR, stdR)))
        else:
            if self._is_calibrating:
                response = (False, LaserTriangulationError)
            else:
                response = (False, LaserTriangulationCancel)

        self._is_calibrating = False

        return response

    def compute_plane(self, X):
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
