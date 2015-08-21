# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import numpy as np

from horus import Singleton


@Singleton
class CurrentImages(object):
    def __init__(self):
        self.texture = None
        self.laser = [None, None]
        self.gray = [None, None]
        self.line = [None, None]

        self._color = 255.0

    def set_image_texture(self, image):
        self.texture = image

    def set_image_laser(self, image, index):
        self.laser[index] = image

    def set_image_gray(self, image, index):
        self.gray[index] = cv2.merge((image, image, image))

    def set_image_line(self, u, v, index):
        img = np.zeros_like(self.laser[index])
        img[v, u.astype(int)] = self._color
        self.line[index] = cv2.merge((img, img, img))
