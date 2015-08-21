# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import numpy as np

from horus import Singleton


@Singleton
class LaserSegmentation(object):

    def __init__(self):
        self._red_channel = 'R (RGB)'
        self._open_enable = False
        self._open_value = 0
        self._threshold_enable = False
        self._threshold_value = 0

    def set_red_channel(self, value):
        self._red_channel = value

    def set_open_enable(self, value):
        self.open_enable = value

    def set_open_value(self, value):
        self.open_value = value

    def set_threshold_enable(self, value):
        self.threshold_enable = value

    def set_threshold_value(self, value):
        self.threshold_value = value

    def line_segmentation(self, image):
        if image is not None:
            # Apply ROI mask
            #image = self.apply_ROI_mask(image)
            # Obtain red channel
            image = self.obtain_red_channel(image)
            # Open image
            if self.open_enable:
                kernel = cv2.getStructuringElement(
                    cv2.MORPH_RECT, (self.open_value, self.open_value))
                image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
            # Threshold image
            if self.threshold_enable:
                image = cv2.threshold(image, self.threshold_value, 255.0, cv2.THRESH_TOZERO)[1]
            # Peak detection: center of mass
            h, w = image.shape
            W = np.array((np.matrix(np.linspace(0, w - 1, w)).T * np.matrix(np.ones(h))).T)
            s = image.sum(axis=1)
            v = np.where(s > 0)[0]
            u = (W * image).sum(axis=1)[v] / s[v]
            return (u, v)

    def obtain_red_channel(self, image):
        ret = None
        if self._channel == 'R (RGB)':
            ret = cv2.split(image)[0]
        elif self._channel == 'Cr (YCrCb)':
            ret = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YCR_CB))[1]
        elif self._channel == 'U (YUV)':
            ret = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YUV))[1]
        return ret
