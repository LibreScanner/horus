# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.engine.driver.driver import Driver
from horus.engine.calibration.calibration import Calibration

driver = Driver()
board = driver.board
camera = driver.camera


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
