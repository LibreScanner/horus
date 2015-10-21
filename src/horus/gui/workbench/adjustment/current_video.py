# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2

from horus import Singleton
from horus.gui.engine import image_capture, image_detection, laser_segmentation


@Singleton
class CurrentVideo(object):

    def __init__(self):
        self.mode = 'Texture'

    def capture(self):
        if self.mode == 'Texture':
            return image_capture.capture_texture()

        if self.mode == 'Pattern':
            image = image_capture.capture_pattern()
            return image_detection.detect_pattern(image)

        if self.mode == 'Laser':
            return image_capture.capture_lasers()

        if self.mode == 'Gray':
            image = image_capture.capture_lasers()
            image = laser_segmentation.compute_line_segmentation(image)
            return cv2.merge((image, image, image))
