# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import struct
import numpy as np
from scipy.sparse import linalg

from horus import Singleton
from horus.engine.calibration.calibration import CalibrationCancel
from horus.engine.calibration.moving_calibration import MovingCalibration

import logging
logger = logging.getLogger(__name__)


class LaserTriangulationError(Exception):

    def __init__(self):
        Exception.__init__(self, "LaserTriangulationError")


@Singleton
class LaserTriangulation(MovingCalibration):

    """Laser triangulation algorithm:

            - Laser coordinates matrix
            - Pattern's origin
            - Pattern's normal
    """

    def __init__(self):
        self.image = None
        self.has_image = False
        MovingCalibration.__init__(self)

    def _initialize(self):
        self.image = None
        self.has_image = True
        self.image_capture.stream = False
        self._point_cloud = [None, None]

    def _capture(self, angle):
        image = self.image_capture.capture_pattern()
        pose = self.image_detection.detect_pose(image)
        ret = self.image_detection.detect_pattern_plane(pose)
        if ret is None:
            self.image = image
        else:
            d, n, corners = ret
            for i in xrange(2):
                image = self.image_capture.capture_laser(i)
                image = self.image_detection.pattern_mask(image, corners)
                self.image = image
                points_2d, image = self.laser_segmentation.compute_2d_points(image)
                point_3d = self.point_cloud_generation.compute_camera_point_cloud(points_2d, d, n)
                if self._point_cloud[i] is None:
                    self._point_cloud[i] = point_3d.T
                else:
                    self._point_cloud[i] = np.concatenate((self._point_cloud[i], point_3d.T))

    def _calibrate(self):
        self.has_image = False
        self.image_capture.stream = True

        # Save point clouds
        for i in xrange(2):
            save_point_cloud('PC' + str(i) + '.ply', self._point_cloud[i])

        # TODO: use arrays
        # Compute planes
        self.dL, self.nL, stdL = compute_plane(0, self._point_cloud[0])
        self.dR, self.nR, stdR = compute_plane(1, self._point_cloud[1])

        if self._is_calibrating and \
           stdL < 5.0 and stdR < 5.0 and \
           self.nL is not None and self.nR is not None:
            response = (True, ((self.dL, self.nL, stdL), (self.dR, self.nR, stdR)))
        else:
            if self._is_calibrating:
                response = (False, LaserTriangulationError())
            else:
                response = (False, CalibrationCancel())

        self._is_calibrating = False
        self.image = None

        return response

    def accept(self):
        self.calibration_data.laser_planes[0].distance = self.dL
        self.calibration_data.laser_planes[0].normal = self.nL
        self.calibration_data.laser_planes[1].distance = self.dR
        self.calibration_data.laser_planes[1].normal = self.nR


def compute_plane(index, X):
    if X is not None:
        X = np.matrix(X).T
        n = X.shape[1]
        std = 0
        size = 0
        if n > 3:
            final_points = []

            for trials in xrange(30):
                X = np.matrix(X)
                n = X.shape[1]
                Xm = X.sum(axis=1) / n
                M = np.array(X - Xm)
                U = linalg.svds(M, k=2)[0]
                s, t = U.T
                normal = np.cross(s, t)
                if normal[2] < 0:
                    normal *= -1
                distance = np.dot(normal, np.array(Xm))[0]
                error_vector = np.dot(M.T, normal)

                std = error_vector.std()

                final_points = np.where(abs(error_vector) < abs(2 * std))[0]

                X = X[:, final_points]

                if std < 0.05 or std > 20.0 or \
                   len(final_points) < 1000 or \
                   size == len(final_points):
                    size = len(final_points)
                    break

                size = len(final_points)

            logger.info("Laser calibration " + str(index))
            logger.info(" Distance: " + str(distance))
            logger.info(" Normal: " + str(normal))
            logger.info(" Standard deviation: " + str(std))
            logger.info(" Iterations: " + str(trials))
            logger.info(" Point cloud size: " + str(size))

            save_point_cloud('PC' + str(index) + '-final.ply', np.array(np.matrix(X).T))

            return distance, normal, std
        else:
            return None, None, None
    else:
        return None, None, None


def save_point_cloud(filename, point_cloud):
    if point_cloud is not None:
        f = open(filename, 'wb')
        save_point_cloud_stream(f, point_cloud)
        f.close()


def save_point_cloud_stream(stream, point_cloud):
    frame = "ply\n"
    frame += "format binary_little_endian 1.0\n"
    frame += "comment Generated by Horus software\n"
    frame += "element vertex {0}\n".format(len(point_cloud))
    frame += "property float x\n"
    frame += "property float y\n"
    frame += "property float z\n"
    frame += "property uchar red\n"
    frame += "property uchar green\n"
    frame += "property uchar blue\n"
    frame += "element face 0\n"
    frame += "property list uchar int vertex_indices\n"
    frame += "end_header\n"
    for point in point_cloud:
        frame += struct.pack("<fffBBB", point[0], point[1], point[2], 255, 0, 0)
    stream.write(frame)
