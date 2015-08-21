# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import numpy as np

from horus import Singleton


class LaserPlane(object):
    def __init__(self):
        self.normal = None
        self.distance = None


@Singleton
class CalibrationData(object):

    def __init__(self):
        self.width = 960
        self.height = 1280

        self._camera_matrix = None
        self._distortion_vector = None
        self._roi = None
        self._dist_camera_matrix = None
        self._weight_matrix = None

        self.laser_planes = [LaserPlane(), LaserPlane()]
        self.platform_rotation = None
        self.platform_translation = None

    def set_resolution(self, width, height):
        self.width = width
        self.height = height

    @property
    def camera_matrix(self):
        return self._camera_matrix

    @camera_matrix.setter
    def camera_matrix(self, value):
        self._camera_matrix = value
        self._compute_dist_camera_matrix()
        self._compute_weight_matrix()

    @property
    def distortion_vector(self):
        return self._distortion_vector

    @distortion_vector.setter
    def distortion_vector(self, value):
        self._distortion_vector = value
        self._compute_dist_camera_matrix()
        self._compute_weight_matrix()

    @property
    def roi(self):
        return self._roi

    @property
    def dist_camera_matrix(self):
        return self._dist_camera_matrix

    @property
    def weight_matrix(self):
        return self._weight_matrix

    def _compute_dist_camera_matrix(self):
        if self._camera_matrix is not None and self._distortion_vector is not None:
            self._dist_camera_matrix, self._roi = cv2.getOptimalNewCameraMatrix(
                self._camera_matrix, self._distortion_vector,
                (int(self.width), int(self.height)), alpha=1)

    def _compute_weight_matrix(self):
        self._weight_matrix = np.array((np.matrix(np.linspace(0, self.width - 1, width)).T * np.matrix(np.ones(self.height))).T)
