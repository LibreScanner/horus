# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import numpy as np
from scipy import optimize

from horus import Singleton
from horus.engine.calibration.moving_calibration import MovingCalibration


class PlatformExtrinsicsError(Exception):

    def __init__(self):
        Exception.__init__(self, _("PlatformExtrinsicsError"))


class PlatformExtrinsicsCancel(Exception):

    def __init__(self):
        Exception.__init__(self, _("PlatformExtrinsicsCancel"))


@Singleton
class PlatformExtrinsics(MovingCalibration):

    """Platform extrinsics algorithm:

            - Rotation matrix
            - Translation vector
    """

    def __init__(self):
        MovingCalibration.__init__(self)
        self.image = None

    def _initialize(self):
        self.x = []
        self.y = []
        self.z = []

    def _capture(self, angle):
        t = self.compute_pattern_position()
        if t is not None:
            self.x += [t[0][0]]
            self.y += [t[1][0]]
            self.z += [t[2][0]]

    def _calibrate(self):
        t = None

        self.x = np.array(self.x)
        self.y = np.array(self.y)
        self.z = np.array(self.z)

        points = zip(self.x, self.y, self.z)

        if len(points) > 4:

            # Fitting a plane
            point, normal = self.fit_plane(points)

            if normal[1] > 0:
                normal = -normal

            # Fitting a circle inside the plane
            center, R, circle = self.fit_circle(point, normal, points)

            # Get real origin
            t = center - self.pattern.distance * np.array(normal)

        if self._is_calibrating and t is not None and np.linalg.norm(t - [5, 90, 320]) < 100:
            response = (True, (R, t, center, point, normal, [self.x, self.y, self.z], circle))
        else:
            if self._is_calibrating:
                response = (False, PlatformExtrinsicsError)
            else:
                response = (False, PlatformExtrinsicsCancel)

        self._is_calibrating = False

        return response

    def compute_pattern_position(self):
        point = None
        """if system == 'Windows':
            flush = 2
        elif system == 'Darwin':
            flush = 2
        else:
            flush = 1"""
        flush = 1
        image = self.driver.camera.capture_image(flush=flush)
        if image is not None:
            self.image = image
            ret = self.solve_pnp(image)
            if ret is not None:
                # Compute point coordinates
                rotation, origin, corners = ret
                dist = (self.pattern.rows - 1) * self.pattern.square_width
                point = origin + np.matrix(rotation) * np.matrix([[0], [dist], [0]])
                point = np.array(point)
        return point

    def distance2plane(self, p0, n0, p):
        return np.dot(np.array(n0), np.array(p) - np.array(p0))

    def residuals_plane(self, parameters, data_point):
        px, py, pz, theta, phi = parameters
        nx, ny, nz = np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)
        distances = [self.distance2plane(
            [px, py, pz], [nx, ny, nz], [x, y, z]) for x, y, z in data_point]
        return distances

    def fit_plane(self, data):
        estimate = [0, 0, 0, 0, 0]  # px,py,pz and zeta, phi
        # you may automize this by using the center of mass data
        # note that the normal vector is given in polar coordinates
        best_fit_values, ier = optimize.leastsq(self.residuals_plane, estimate, args=(data))
        xF, yF, zF, tF, pF = best_fit_values

        #self.point  = [xF,yF,zF]
        self.point = data[0]
        self.normal = -np.array([np.sin(tF) * np.cos(pF), np.sin(tF) * np.sin(pF), np.cos(tF)])

        return self.point, self.normal

    def residuals_circle(self, parameters, data_point):
        r, s, Ri = parameters
        plane_point = s * self.s + r * self.r + np.array(self.point)
        distance = [np.linalg.norm(plane_point - np.array([x, y, z])) for x, y, z in data_point]
        res = [(Ri - dist) for dist in distance]
        return res

    def fit_circle(self, point, normal, data):
        # creating two inplane vectors
        # assuming that normal not parallel x!
        self.s = np.cross(np.array([1, 0, 0]), np.array(normal))
        self.s = self.s / np.linalg.norm(self.s)
        self.r = np.cross(np.array(normal), self.s)
        self.r = self.r / np.linalg.norm(self.r)  # should be normalized already, but anyhow

        # Define rotation
        R = np.array([self.s, self.r, normal]).T

        estimate_circle = [0, 0, 0]  # px,py,pz and zeta, phi
        best_circle_fit_values, ier = optimize.leastsq(
            self.residuals_circle, estimate_circle, args=(data))

        rF, sF, RiF = best_circle_fit_values

        # Synthetic Data
        center_point = sF * self.s + rF * self.r + np.array(self.point)
        synthetic = [list(center_point + RiF * np.cos(phi) * self.r + RiF * np.sin(phi) * self.s)
                     for phi in np.linspace(0, 2 * np.pi, 50)]
        [cxTupel, cyTupel, czTupel] = [x for x in zip(*synthetic)]

        return center_point, R, [cxTupel, cyTupel, czTupel]
