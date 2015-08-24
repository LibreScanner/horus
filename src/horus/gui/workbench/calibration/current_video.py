# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import numpy as np

from horus import Singleton
from horus.engine.algorithms.image_capture import ImageCapture
from horus.engine.algorithms.image_detection import ImageDetection
from horus.engine.algorithms.laser_segmentation import LaserSegmentation


@Singleton
class CurrentVideo(object):

    def __init__(self):
        self.image_capture = ImageCapture()
        self.image_detection = ImageDetection()
        self.laser_segmentation = LaserSegmentation()

        self.mode = 'Texture'

    def capture(self):
        if self.mode == 'Texture':
            return self.image_capture.capture_texture()

        if self.mode == 'Pattern':
            image = self.image_capture.capture_pattern()
            return self.image_detection.detect_pattern(image)

        if self.mode == 'Laser':
            return self.image_capture.capture_lasers()

        if self.mode == 'Gray':
            image = self.image_capture.capture_lasers()
            image = self.laser_segmentation.compute_line_segmentation(image)
            return cv2.merge((image, image, image))

        #if self.mode == 'Line':
        #    image = self.image_capture.capture_lasers()
        #    u, v = self.laser_segmentation.compute_2d_points(image)
        #    img = np.zeros_like(image[:, :, 0])
        #    img[v.astype(int), u.astype(int)] = 255.0
        #    return cv2.merge((img, img, img))
