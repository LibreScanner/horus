# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import numpy as np

from horus import Singleton
from horus.engine.calibration.calibration_data import CalibrationData
from horus.engine.algorithms.point_cloud_roi import PointCloudROI


@Singleton
class LaserSegmentation(object):

    def __init__(self):
        self.calibration_data = CalibrationData()
        self.point_cloud_roi = PointCloudROI()

        self.red_channel = 'R-G (RGB)'
        self.window_enable = False
        self.window_value = 0
        self.blur_enable = False
        self.blur_value = 0
        self.open_enable = False
        self.open_value = 0
        self.threshold_enable = False
        self.threshold_value = 0

    def set_red_channel(self, value):
        self.red_channel = value

    def set_window_enable(self, value):
        self.window_enable = value

    def set_window_value(self, value):
        self.window_value = value

    def set_blur_enable(self, value):
        self.blur_enable = value

    def set_blur_value(self, value):
        self.blur_value = 2 * value + 1

    def set_open_enable(self, value):
        self.open_enable = value

    def set_open_value(self, value):
        self.open_value = 2 * value - 1

    def set_threshold_enable(self, value):
        self.threshold_enable = value

    def set_threshold_value(self, value):
        self.threshold_value = value

    def compute_2d_points(self, image):
        if image is not None:
            image = self.compute_line_segmentation(image)
            # Peak detection: center of mass
            s = image.sum(axis=1)
            v = np.where(s > 0)[0]
            u = (self.calibration_data.weight_matrix * image).sum(axis=1)[v] / s[v]
            return (u, v), image

    def compute_hough_lines(self, image):
        if image is not None:
            image = self.compute_line_segmentation(image)
            lines = cv2.HoughLines(image, 1, np.pi / 180, 120)
            # if lines is not None:
            #   rho, theta = lines[0][0]
            #   ## Calculate coordinates
            #   u1 = rho / np.cos(theta)
            #   u2 = u1 - height * np.tan(theta)
            return lines

    def compute_line_segmentation(self, image, roi_mask=False):
        if image is not None:
            # Apply ROI mask
            if roi_mask:
                image = self.point_cloud_roi.mask_image(image)
            # Obtain red channel
            image = self._obtain_red_channel(image)
            # Open image
            if self.open_enable:
                kernel = cv2.getStructuringElement(
                    cv2.MORPH_RECT, (self.open_value, self.open_value))
                image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
            # Threshold image
            if self.threshold_enable:
                image = cv2.threshold(
                    image, self.threshold_value, 255, cv2.THRESH_TOZERO)[1]
            # Window mask
            if self.window_enable:
                peak = image.argmax(axis=1)
                _min = peak - self.window_value
                _max = peak + self.window_value + 1
                mask = np.zeros_like(image)
                for i in xrange(self.calibration_data.height):
                    mask[i, _min[i]:_max[i]] = 255
            # Blur image
            if self.blur_enable:
                image = cv2.blur(image, (self.blur_value, self.blur_value))
            # Apply mask
            if self.window_enable:
                image = cv2.bitwise_and(image, mask)
            return image

    def _obtain_red_channel(self, image):
        ret = None
        if self.red_channel == 'R-G (RGB)':
            r, g, b = cv2.split(image)
            ret = cv2.subtract(r, g)
            # ret *= 1.0 * np.amax(r) / np.amax(ret)
        elif self.red_channel == 'Cr (YCrCb)':
            ret = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YCR_CB))[1]
        elif self.red_channel == 'U (YUV)':
            ret = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YUV))[1]
        return ret
