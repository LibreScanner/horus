# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


from horus import Singleton


@Singleton
class LaserSegmentation(object):

    def __init__(self):
        self.open_enable = True
        self.open_value = 2
        self.threshold_enable = True
        self.threshold_value = 20

        self._images = {'texture': None,
                        'laser': [None, None],
                        'gray': [None, None],
                        'line': [None, None]}

    def set_use_open(self, value):
        self.use_open = value

    def set_open_value(self, value):
        self.open_value = value

    def set_use_threshold(self, value):
        self.threshold_enable = value

    def set_threshold_value(self, value):
        self.threshold_value = value

    def compute_2D_points(self, images):
        uv = []
        self._images['texture'] = images.texture

        # Segmentation
        if images.img_no_laser is None:
            # Simple segmentation
            for i in len(images.img_laser):
                y, cr, cb = cv2.split(cv2.cvtColor(images.img_laser[i], cv2.COLOR_RGB2YCR_CB))
                image = cr
                self._images['laser'][i] = image
                uv += (images.theta, self.laser_segmentation(i, cr))
        else:
            # Diff segmentation
            yn, crn, cbn = cv2.split(cv2.cvtColor(images.img_no_laser, cv2.COLOR_RGB2YCR_CB))
            for i in len(images.img_laser):
                yl, crl, cbl = cv2.split(cv2.cvtColor(images.img_laser[i], cv2.COLOR_RGB2YCR_CB))
                image = cv2.subtract(crl, crn)
                self._images['laser'][i] = image
                uv += (images.theta, self.laser_segmentation(i, image))

        return uv

    def laser_segmentation(self, index, image):

        # Apply ROI mask
        image = self.apply_ROI_mask(image)

        # Open image
        if self.open_enable:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.open_value, self.open_value))
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

        temp_line = np.zeros_like(image)
        temp_line[v, u.astype(int)] = 255.0
        self._images['line'][index] = temp_line
        self._images['gray'][index] = cv2.merge((image, image, image))

        return (u, v)

    def get_image(self, img_type='texture', img_index=None):
        img = None
        if img_index is None:
            img = self._images[img_type]
        else:
            if img_type in ['laser', 'gray', 'line']:
                img = self._images[img_type]

        #if img is not None:
        #    if self.pcg.viewROI:
        #        img = seg.roi2DVisualization(img)

        return img

    """
    # TODO: refactor
    def roi2DVisualization(self, img):
        self.pcg.calculateCenter()
        # params:
        thickness = 6
        thickness_hiden = 1

        center_up_u = self.pcg.no_trimmed_umin + \
            (self.pcg.no_trimmed_umax - self.pcg.no_trimmed_umin) / 2
        center_up_v = self.pcg.upper_vmin + (self.pcg.upper_vmax - self.pcg.upper_vmin) / 2
        center_down_u = self.pcg.no_trimmed_umin + \
            (self.pcg.no_trimmed_umax - self.pcg.no_trimmed_umin) / 2
        center_down_v = self.pcg.lower_vmax + (self.pcg.lower_vmin - self.pcg.lower_vmax) / 2
        axes_up = ((self.pcg.no_trimmed_umax - self.pcg.no_trimmed_umin) / 2,
                   ((self.pcg.upper_vmax - self.pcg.upper_vmin) / 2))
        axes_down = ((self.pcg.no_trimmed_umax - self.pcg.no_trimmed_umin) / 2,
                     ((self.pcg.lower_vmin - self.pcg.lower_vmax) / 2))

        img = img.copy()
        # upper ellipse
        if (center_up_v < self.pcg.cy):
            cv2.ellipse(img, (center_up_u, center_up_v), axes_up,
                        0, 180, 360, (0, 100, 200), thickness)
            cv2.ellipse(img, (center_up_u, center_up_v), axes_up,
                        0, 0, 180, (0, 100, 200), thickness_hiden)
        else:
            cv2.ellipse(img, (center_up_u, center_up_v), axes_up,
                        0, 180, 360, (0, 100, 200), thickness)
            cv2.ellipse(img, (center_up_u, center_up_v), axes_up,
                        0, 0, 180, (0, 100, 200), thickness)

        # lower ellipse
        cv2.ellipse(img, (center_down_u, center_down_v), axes_down,
                    0, 180, 360, (0, 100, 200), thickness_hiden)
        cv2.ellipse(img, (center_down_u, center_down_v),
                    axes_down, 0, 0, 180, (0, 100, 200), thickness)

        # cylinder lines

        cv2.line(img, (self.pcg.no_trimmed_umin, center_up_v),
                 (self.pcg.no_trimmed_umin, center_down_v), (0, 100, 200), thickness)
        cv2.line(img, (self.pcg.no_trimmed_umax, center_up_v),
                 (self.pcg.no_trimmed_umax, center_down_v), (0, 100, 200), thickness)

        # view center
        if axes_up[0] <= 0 or axes_up[1] <= 0:
            axes_up_center = (20, 1)
            axes_down_center = (20, 1)
        else:
            axes_up_center = (20, axes_up[1] * 20 / axes_up[0])
            axes_down_center = (20, axes_down[1] * 20 / axes_down[0])
        # upper center
        cv2.ellipse(img, (self.pcg.center_u, min(center_up_v, self.pcg.center_v)),
                    axes_up_center, 0, 0, 360, (0, 70, 120), -1)
        # lower center
        cv2.ellipse(img, (self.pcg.center_u, self.pcg.center_v),
                    axes_down_center, 0, 0, 360, (0, 70, 120), -1)

        return img

    def apply_ROI_mask(self, image):
        mask = np.zeros(image.shape, np.uint8)
        mask[self.pcg.vmin:self.pcg.vmax,
             self.pcg.umin:self.pcg.umax] = image[self.pcg.vmin:self.pcg.vmax,
                                                  self.pcg.umin:self.pcg.umax]

        return mask"""
