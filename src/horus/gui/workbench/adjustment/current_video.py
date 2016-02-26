# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
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
            return image_capture.capture_all_lasers()

        if self.mode == 'Gray':
            images = [None, None]
            for i in xrange(2):
                images[i] = image_capture.capture_laser(i)
                images[i] = laser_segmentation.compute_line_segmentation(images[i])
            image = images[0] + images[1]
            return cv2.merge((image, image, image))
