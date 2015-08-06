# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus import Singleton
from horus.engine.calibration.moving_calibration import MovingCalibration


@Singleton
class PlatformExtrinsics(MovingCalibration):

    """Platform extrinsics algorithm:

            - Rotation matrix
            - Translation vector
    """

    def __init__(self):
        MovingCalibration.__init__(self)
        self.image = None

    def _start(self):
        t = None
        angle = 0
        step = 5

        if driver.is_connected:

            x = []
            y = []
            z = []

            # Setup scanner
            board.lasers_off()
            board.motor_enable()
            board.motor_speed(200)
            board.motor_acceleration(200)
            time.sleep(0.1)

            if self._progress_callback is not None:
                self._progress_callback(0)

            while self._is_calibrating and abs(angle) < 180:
                angle += step
                t = self.compute_pattern_position()
                board.motor_relative(step)
                board.motor_move()
                if self._progress_callback is not None:
                    self._progress_callback(1.1 * abs(angle / 2.))
                time.sleep(0.1)
                if t is not None:
                    x += [t[0][0]]
                    y += [t[1][0]]
                    z += [t[2][0]]

            x = np.array(x)
            y = np.array(y)
            z = np.array(z)

            points = zip(x, y, z)

            if len(points) > 4:

                # Fitting a plane
                point, normal = self.fit_plane(points)

                if normal[1] > 0:
                    normal = -normal

                # Fitting a circle inside the plane
                center, R, circle = self.fit_circle(point, normal, points)

                # Get real origin
                t = center - pattern.distance * np.array(normal)

            board.lasers_off()
            board.motor_disable()

        self.image = None

        if self._is_calibrating and t is not None and np.linalg.norm(t - [5, 80, 320]) < 100:
            response = (True, (R, t, center, point, normal, [x, y, z], circle))
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

    def compute_pattern_position(self):
        t = None
        if system == 'Windows':
            flush = 2
        elif system == 'Darwin':
            flush = 2
        else:
            flush = 1
        image = camera.capture_image(flush=flush)
        if image is not None:
            self.image = image
            ret = solve_pnp(image)
            if ret is not None:
                t = ret[1]
        return t

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