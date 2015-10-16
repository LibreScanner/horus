# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import numpy as np

from horus import Singleton
from horus.engine.calibration.calibration import CalibrationCancel
from horus.engine.calibration.moving_calibration import MovingCalibration
from horus.engine.calibration import laser_triangulation, platform_extrinsics


class ComboCalibrationError(Exception):

    def __init__(self):
        Exception.__init__(self, "ComboCalibrationError")


@Singleton
class ComboCalibration(MovingCalibration):

    """Combine Laser Triangulation and Platform Extrinsics calibration in one"""

    def __init__(self):
        self.image = None
        self.has_image = False
        MovingCalibration.__init__(self)

    def _initialize(self):
        self.image = None
        self.has_image = True
        self.image_capture.stream = False
        self._point_cloud = [None, None]
        self.x = []
        self.y = []
        self.z = []

    def _capture(self, angle):
        image = self.image_capture.capture_pattern()
        pose = self.image_detection.detect_pose(image)
        if pose is None:
            self.image = image
        else:
            # Platform extrinsics
            t = platform_extrinsics.compute_pattern_position(
                pose, (self.pattern.rows - 1) * self.pattern.square_width)
            if t is not None:
                self.x += [t[0][0]]
                self.y += [t[1][0]]
                self.z += [t[2][0]]

            # Laser triangulation
            plane = self.image_detection.detect_pattern_plane(pose)
            if plane is not None:
                d, n, corners = plane
                for i in xrange(2):
                    image = self.image_capture.capture_laser(i)
                    image = self.image_detection.pattern_mask(image, corners)
                    self.image = image
                    points_2d, _ = self.laser_segmentation.compute_2d_points(image)
                    point_3d = self.point_cloud_generation.compute_camera_point_cloud(
                        points_2d, d, n)
                    if self._point_cloud[i] is None:
                        self._point_cloud[i] = point_3d.T
                    else:
                        self._point_cloud[i] = np.concatenate((self._point_cloud[i], point_3d.T))

    def _calibrate(self):
        self.has_image = False
        self.image_capture.stream = True

        # Platform extrinsics
        t = None
        self.x = np.array(self.x)
        self.y = np.array(self.y)
        self.z = np.array(self.z)
        points = zip(self.x, self.y, self.z)

        if len(points) > 4:
            # Fitting a plane
            point, normal = platform_extrinsics.fit_plane(points)
            if normal[1] > 0:
                normal = -normal
            # Fitting a circle inside the plane
            center, R, circle = platform_extrinsics.fit_circle(point, normal, points)
            # Get real origin
            t = center - self.pattern.distance * np.array(normal)

        # Laser triangulation
        # Save point clouds
        for i in xrange(2):
            laser_triangulation.save_point_cloud('PC' + str(i) + '.ply', self._point_cloud[i])
        # TODO: use arrays
        # Compute planes
        dL, nL, stdL = laser_triangulation.compute_plane(self._point_cloud[0])
        dR, nR, stdR = laser_triangulation.compute_plane(self._point_cloud[1])

        # Return response

        result = True
        if self._is_calibrating:
            if t is not None and np.linalg.norm(t - platform_extrinsics.estimated_t) < 100:
                response_platform_extrinsics = (
                    R, t, center, point, normal, [self.x, self.y, self.z], circle)
            else:
                result = False
                response = ComboCalibrationError

            if nL is not None and nR is not None:
                response_laser_triangulation = ((dL, nL, stdL), (dR, nR, stdR))
            else:
                result = False
                response = ComboCalibrationError

            if result:
                response = (True, (response_platform_extrinsics, response_laser_triangulation))
        else:
            response = (False, CalibrationCancel)

        self._is_calibrating = False

        return response
