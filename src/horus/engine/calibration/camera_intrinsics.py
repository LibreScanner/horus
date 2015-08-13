# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2

from horus import Singleton
from horus.engine.calibration.calibration import Calibration


class CameraIntrinsicsError(Exception):

    def __init__(self):
        Exception.__init__(self, _("CameraIntrinsicsError"))


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
        self.image_points = []
        self.object_points = []

        self._camera_use_distortion = False

    def _start(self):
        ret, error, cmat, dvec, rvecs, tvecs = self.calibrate()

        if ret:
            self.camera_matrix = cmat
            self.distortion_vector = dvec
            response = (True, (error, cmat, dvec, rvecs, tvecs))
        else:
            response = (False, CameraIntrinsicsError)

        self._is_calibrating = False

        if self._after_callback is not None:
            self._after_callback(response)

    def calibrate(self):
        error = 0
        ret, cmat, dvec, rvecs, tvecs = cv2.calibrateCamera(
            self.object_points, self.image_points, self.shape)

        if ret:
            for i in xrange(len(self.object_points)):
                imgpoints2, _ = cv2.projectPoints(
                    self.object_points[i], rvecs[i], tvecs[i], cmat, dvec)
                error += cv2.norm(self.image_points[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            error /= len(self.object_points)

        return ret, error, cmat, dvec.ravel(), rvecs, tvecs

    def reset(self):
        self.image_points = []
        self.object_points = []
        self._camera_use_distortion = self.driver.camera.use_distortion
        self.driver.camera.set_use_distortion(False)

    def capture(self):
        if self.driver.is_connected:
            frame = self.driver.camera.capture_image(flush=1)
            if frame is not None:
                self.shape = frame.shape[:2]
                retval, frame, corners = self.draw_chessboard(frame)
                if retval:
                    if len(self.object_points) < 15:
                        self.image_points.append(corners)
                        self.object_points.append(self.pattern.object_points)
                return retval, frame

    def accept(self):
        self.driver.camera.camera_matrix = self.camera_matrix
        self.driver.camera.distortion_vector = self.distortion_vector
