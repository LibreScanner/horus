# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2

from horus import Singleton
from horus.engine.calibration.pattern import Pattern
from horus.engine.calibration.calibration_result import CalibrationResult


@Singleton
class ImageDetection(object):

    def __init__(self):
        self.pattern = Pattern()
        self.calibration_result = CalibrationResult()

        self._criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    def detect_pattern(self, image):
        corners = self._detect_chessboard(image)
        if corners is not None:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.drawChessboardCorners(
                image, (self.pattern.columns, self.pattern.rows), corners, True)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def detect_corners(self, image):
        corners = self._detect_chessboard(image)
        return corners

    def detect_pose(self, image):
        corners = self._detect_chessboard(image)
        if corners is not None:
            ret, rvecs, tvecs = cv2.solvePnP(
                self.pattern.object_points, corners,
                self.calibration_result.camera_matrix, self.calibration_result.distortion_vector)
            if ret:
                return (cv2.Rodrigues(rvecs)[0], tvecs, corners)

    def pattern_mask(self, image):
        corners = self._detect_chessboard(image)
        if corners is not None:
            p1 = corners[0][0]
            p2 = corners[self.pattern.columns - 1][0]
            p3 = corners[self.pattern.columns * (self.pattern.rows - 1) - 1][0]
            p4 = corners[self.pattern.columns * self.pattern.rows - 1][0]
            p11 = min(p1[1], p2[1], p3[1], p4[1])
            p12 = max(p1[1], p2[1], p3[1], p4[1])
            p21 = min(p1[0], p2[0], p3[0], p4[0])
            p22 = max(p1[0], p2[0], p3[0], p4[0])
            d = max(corners[1][0][0] - corners[0][0][0],
                    corners[1][0][1] - corners[0][0][1],
                    corners[self.pattern.columns][0][1] - corners[0][0][1],
                    corners[self.pattern.columns][0][0] - corners[0][0][0])
            mask = np.zeros(image.shape[:2], np.uint8)
            mask[p11 - d:p12 + d, p21 - d:p22 + d] = 255
            image = cv2.bitwise_and(image, image, mask=mask)
        return image

    def _detect_chessboard(self, image):
        if image is not None:
            if self.pattern.rows > 2 or self.pattern.columns > 2:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                ret, corners = cv2.findChessboardCorners(
                    gray, (self.pattern.columns, self.pattern.rows), flags=cv2.CALIB_CB_FAST_CHECK)
                if ret:
                    cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self._criteria)
                return corners
