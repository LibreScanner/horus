# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import time
import struct
import platform
import threading
import numpy as np
from scipy import optimize
from scipy.sparse import linalg

system = platform.system()

from driver import Driver
from horus.util.singleton import Singleton

"""
    Calibrations:

        - Autocheck Algorithm
        - Camera Intrinsics Calibration
        - Laser Triangulation Calibration
        - Platform Extrinsics Calibration
"""

# Common

driver = Driver.Instance()
board = driver.board
camera = driver.camera
pattern = Pattern.Instance()

image_points = []
object_points = []
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)


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


class Calibration(object):

    """Generic class for threading calibration"""

    def __init__(self):
        # TODO: Callbacks to Observer pattern
        self._before_callback = None
        self._progress_callback = None
        self._after_callback = None
        self._is_calibrating = False

    def set_callbacks(self, before, progress, after):
        self._before_callback = before
        self._progress_callback = progress
        self._after_callback = after

    def start(self):
        if not self._is_calibrating:
            if self._before_callback is not None:
                self._before_callback()

            if self._progress_callback is not None:
                self._progress_callback(0)

            self._is_calibrating = True
            threading.Thread(target=self._start).start()

    def _start(self):
        pass

    def cancel(self):
        self._is_calibrating = False


@Singleton
class Pattern(object):

    def __init__(self):
        self._rows = 0
        self._columns = 0
        self._square_width = 0
        self.distance = 0

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, value):
        self._rows = value
        self._generate_object_points()

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        self._columns = value
        self._generate_object_points()

    @property
    def square_width(self):
        return self._square_width

    @square_width.setter
    def square_width(self, value):
        self._square_width = value
        self._generate_object_points()

    def _generate_object_points(self):
        objp = np.zeros((self.columns * self.rows, 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.columns, 0:self.rows].T.reshape(-1, 2)
        objp = np.multiply(objp, self.square_width)
        self.object_points = objp


@Singleton
class AutoCheck(Calibration):

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
                board.left_laser_on()
                img_las_left = camera.capture_image(flush=1)
                board.left_laser_off()
                board.right_laser_on()
                img_las_right = camera.capture_image(flush=1)
                board.right_laser_off()
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


@Singleton
class CameraIntrinsics(Calibration):

    """Camera calibration algorithms, based on [Zhang2000] and [BouguetMCT]:

            - Camera matrix
            - Distortion vector
    """

    def __init__(self):
        Calibration.__init__(self)
        self.shape = None
        self.camera_matrix = None
        self.distortion_vector = None

    def _start(self):
        ret, cmat, dvec, rvecs, tvecs = cv2.calibrateCamera(
            object_points, image_points, self.shape)

        if self._progress_callback is not None:
            self._progress_callback(100)

        if ret:
            self.camera_matrix = cmat
            self.distortion_vector = dvec[0]
            response = (True, (cmat, dvec[0], rvecs, tvecs))
        else:
            response = (False, _("Calibration Error"))

        self._is_calibrating = False

        if self._after_callback is not None:
            self._after_callback(response)

    def capture(self):
        if driver.is_connected:
            frame = camera.capture_image(flush=1, mirror=False)
            if frame is not None:
                self.shape = frame.shape[:2]
                retval, frame = detect_chessboard(frame, capture=True)
                frame = cv2.flip(frame, 1)  # Mirror
                return retval, frame

    def accept(self):
        camera.camera_matrix = self.camera_matrix
        camera.distortion_vector = self.distortion_vector


@Singleton
class LaserTriangulation(Calibration):

    """Laser triangulation algorithm:

            - Laser coordinates matrix
            - Pattern's origin
            - Pattern's normal
    """

    def __init__(self):
        Calibration.__init__(self)
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
                    board.left_laser_on()
                    img_las_left = camera.capture_image(flush=flush)
                    board.left_laser_off()
                    self.image = img_las_left
                    if img_las_left is None:
                        break

                    img_raw_right = camera.capture_image(flush=flush)
                    board.right_laser_on()
                    img_las_right = camera.capture_image(flush=flush)
                    board.right_laser_off()
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


@Singleton
class PlatformExtrinsics(Calibration):

    """Platform extrinsics algorithm:

            - Rotation matrix
            - Translation vector
    """

    def __init__(self):
        Calibration.__init__(self)
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

# Common


def reset_stack():
    image_points = []
    object_points = []


def detect_chessboard(frame, capture=False):
    if pattern.rows < 2 or pattern.columns < 2:
        return False, frame
    if frame is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        retval, corners = cv2.findChessboardCorners(
            gray, (pattern.columns, pattern.rows), flags=cv2.CALIB_CB_FAST_CHECK)

        if retval:
            cv2.cornerSubPix(
                gray, corners, winSize=(11, 11), zeroZone=(-1, -1), criteria=criteria)
            if capture:
                if len(object_points) < 12:
                    image_points.append(corners)
                    object_points.append(pattern.object_points)
            cv2.drawChessboardCorners(
                frame, (pattern.columns, pattern.rows), corners, retval)
        return retval, frame
    else:
        return False, frame


def solve_pnp(image):
    if image is not None:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        retval, corners = cv2.findChessboardCorners(
            gray, (pattern.columns, pattern.rows), flags=cv2.CALIB_CB_FAST_CHECK)

        if retval:
            cv2.cornerSubPix(
                gray, corners, winSize=(11, 11), zeroZone=(-1, -1), criteria=criteria)
            if camera.use_distortion:
                ret, rvecs, tvecs = cv2.solvePnP(
                    pattern.object_points, corners, camera.camera_matrix, camera.distortion_vector)
            else:
                ret, rvecs, tvecs = cv2.solvePnP(
                    pattern.object_points, corners, camera.camera_matrix, None)
            if ret is not None:
                return (cv2.Rodrigues(rvecs)[0], tvecs, corners)
            else:
                return None
        else:
            return None
    else:
        return None


def corners_mask(frame, corners):
    p1 = corners[0][0]
    p2 = corners[pattern.columns - 1][0]
    p3 = corners[pattern.columns * (pattern.rows - 1) - 1][0]
    p4 = corners[pattern.columns * pattern.rows - 1][0]
    p11 = min(p1[1], p2[1], p3[1], p4[1])
    p12 = max(p1[1], p2[1], p3[1], p4[1])
    p21 = min(p1[0], p2[0], p3[0], p4[0])
    p22 = max(p1[0], p2[0], p3[0], p4[0])
    d = max(corners[1][0][0] - corners[0][0][0],
            corners[1][0][1] - corners[0][0][1],
            corners[pattern.columns][0][1] - corners[0][0][1],
            corners[pattern.columns][0][0] - corners[0][0][0])
    mask = np.zeros(frame.shape[:2], np.uint8)
    mask[p11 - d:p12 + d, p21 - d:p22 + d] = 255
    frame = cv2.bitwise_and(frame, frame, mask=mask)
    return frame


def detect_line(img_raw, img_las):
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
        # WrongLaserPosition
    else:
        raise LaserNotDetected


def save_scene(filename, point_cloud):
    if point_cloud is not None:
        f = open(filename, 'wb')
        save_scene_stream(f, point_cloud)
        f.close()


def save_scene_stream(stream, point_cloud):
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


def detect_pattern_plane(image):
    if image is not None:
        ret = solve_pnp(image)
        if ret is not None:
            R = ret[0]
            t = ret[1].T[0]
            n = R.T[2]
            c = ret[2]
            d = -np.dot(n, t)
            return (d, n, c)


def compute_laser_line(img_las, img_raw, threshold):
    # Image segmentation
    sub = cv2.subtract(img_las, img_raw)
    r, g, b = cv2.split(sub)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    r = cv2.morphologyEx(r, cv2.MORPH_OPEN, kernel)
    r = cv2.threshold(r, threshold, 255.0, cv2.THRESH_TOZERO)[1]

    # Peak detection: center of mass
    h, w = r.shape
    W = np.array((np.matrix(np.linspace(0, w - 1, w)).T * np.matrix(np.ones(h))).T)
    s = r.sum(axis=1)
    v = np.where(s > 0)[0]
    u = (W * r).sum(axis=1)[v] / s[v]

    return u, v


def compute_point_cloud(u, v, d, n):
    fx = camera.camera_matrix[0][0]
    fy = camera.camera_matrix[1][1]
    cx = camera.camera_matrix[0][2]
    cy = camera.camera_matrix[1][2]

    x = np.concatenate(((u - cx) / fx, (v - cy) / fy, np.ones(len(u)))).reshape(3, len(u))

    X = -d / np.dot(n, x) * x

    return X.T


def compute_plane(X, side):
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

                # Save each iteration point cloud
                # if side == 'l':
                #   save_scene('new_'+str(trials)+'_XL.ply', np.asarray(X.T))
                # else:
                #   save_scene('new_'+str(trials)+'_XR.ply', np.asarray(X.T))

                if std < 0.1 or len(final_points) < 1000:
                    break

            return d, n, std
        else:
            return None, None, None
    else:
        return None, None, None
