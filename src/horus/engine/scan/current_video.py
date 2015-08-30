# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import numpy as np

from horus import Singleton
from horus.engine.algorithms.point_cloud_roi import PointCloudROI


@Singleton
class CurrentVideo(object):

    def __init__(self):
        self.mode = 'Texture'
        self.roi_view = False
        self.point_cloud_roi = PointCloudROI()

        self.images = {}
        self.images['Texture'] = None
        self.images['Laser'] = None
        self.images['Gray'] = None
        self.images['Line'] = None

    def set_roi_view(self, value):
        self.roi_view = value

    def set_texture(self, image):
        image = self._apply_roi(image)
        self.images['Texture'] = image

    def set_laser(self, images):
        image = self._combine_images(images)
        image = self._apply_roi(image)
        self.images['Laser'] = image

    def set_gray(self, images):
        image = self._combine_images(images)
        image = cv2.merge((image, image, image))
        image = self._apply_roi(image)
        self.images['Gray'] = image

    def set_line(self, points, image):
        images = [None, None]
        images[0] = self._compute_line_image(points[0], image)
        images[1] = self._compute_line_image(points[1], image)
        image = self._combine_images(images)
        image = cv2.merge((image, image, image))
        image = self._apply_roi(image)
        self.images['Line'] = image

    def _combine_images(self, images):
        if images[0] is not None and images[1] is not None:
            return np.maximum(images[0], images[1])

        if images[0] is not None:
            return images[0]

        if images[1] is not None:
            return images[1]

    def _compute_line_image(self, points, image):
        u, v = points
        image = np.zeros_like(image)
        image[v.astype(int), u.astype(int)] = 255.0
        return image

    def _apply_roi(self, image):
        image = self.point_cloud_roi.mask_image(image)
        if self.roi_view:
            image = self.point_cloud_roi.draw_roi(image)
        return image

    def capture(self):
        return self.images[self.mode]
