# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import math
import time
import platform

system = platform.system()

if system == 'Darwin':
    import uvc


class CameraNotConnected(Exception):

    def __init__(self):
        Exception.__init__(self, _("Camera Not Connected"))


class WrongCamera(Exception):

    def __init__(self):
        Exception.__init__(self, _("Wrong Camera"))


class InvalidVideo(Exception):

    def __init__(self):
        Exception.__init__(self, _("Invalid Video"))


class Camera(object):

    """Camera class. For accessing to the scanner camera"""

    def __init__(self, parent=None, camera_id=0):
        self.parent = parent
        self.camera_id = camera_id
        self.use_distortion = False
        self.unplug_callback = None

        self._capture = None
        self._is_connected = False
        self._reading = False
        self._width = 800
        self._height = 600
        self._camera_matrix = None
        self._distortion_vector = None
        self._dist_camera_matrix = None
        self._tries = 0  # Check if command fails

        if system == 'Windows':
            self._number_frames_fail = 3
            self._max_brightness = 1.
            self._max_contrast = 1.
            self._max_saturation = 1.
        elif system == 'Darwin':
            self._number_frames_fail = 1
            self._max_brightness = 255.
            self._max_contrast = 255.
            self._max_saturation = 255.
            self._rel_exposure = 10.
        else:
            self._number_frames_fail = 3
            self._max_brightness = 255.
            self._max_contrast = 255.
            self._max_saturation = 255.
            self._max_exposure = 1000.

    def connect(self):
        print ">>> Connecting camera {0}".format(self.camera_id)
        self._is_connected = False
        if system == 'Darwin':
            for device in uvc.mac.Camera_List():
                if device.src_id == self.camera_id:
                    self.controls = uvc.mac.Controls(device.uId)
        if self._capture is not None:
            self._capture.release()
        self._capture = cv2.VideoCapture(self.camera_id)
        time.sleep(0.2)
        if not self._capture.isOpened():
            time.sleep(1)
            self._capture.open(self.camera_id)
        if self._capture.isOpened():
            self._is_connected = True
            self._check_video()
            self._check_camera()
            print ">>> Done"
        else:
            raise CameraNotConnected()

    def disconnect(self):
        tries = 0
        if self._is_connected:
            print ">>> Disconnecting camera {0}".format(self.camera_id)
            if self._capture is not None:
                if self._capture.isOpened():
                    self._is_connected = False
                    while tries < 10:
                        tries += 1
                        if not self._reading:
                            self._capture.release()
                print ">>> Done"

    def set_unplug_callback(self, value):
        self.unplug_callback = value

    def _check_video(self):
        """Check correct video"""
        if self.capture_image() is None or (self.capture_image() == 0).all():
            raise InvalidVideo()

    def _check_camera(self):
        """Check correct camera"""
        c_exp = False
        c_bri = False

        # Check exposure
        if system == 'Darwin':
            self.controls['UVCC_REQ_EXPOSURE_AUTOMODE'].set_val(1)
        self.set_exposure(2)
        exposure = self.get_exposure()
        if exposure is not None:
            c_exp = exposure >= 1

        # Check brightness
        self.set_brightness(2)
        brightness = self.get_brightness()
        if brightness is not None:
            c_bri = brightness >= 1

        if not c_exp or not c_bri:
            raise WrongCamera()

    def capture_image(self, flush=0, mirror=False):
        """Capture image from camera"""
        if self._is_connected:
            self._reading = True
            if flush > 0:
                for i in xrange(0, flush):
                    self._capture.read()
            ret, image = self._capture.read()
            self._reading = False
            if ret:
                if self.use_distortion and \
                   self._camera_matrix is not None and \
                   self._distortion_vector is not None and \
                   self._dist_camera_matrix is not None:
                    mapx, mapy = cv2.initUndistortRectifyMap(
                        self._camera_matrix, self._distortion_vector,
                        R=None, new_camera_matrix=self._dist_camera_matrix,
                        size=(self._width, self._height), m1type=5)
                    image = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)
                image = cv2.transpose(image)
                if not mirror:
                    image = cv2.flip(image, 1)
                self._success()
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                self._fail()
                return None
        else:
            self._fail()
            return None

    def set_brightness(self, value):
        if self._is_connected:
            if system == 'Darwin':
                ctl = self.controls['UVCC_REQ_BRIGHTNESS_ABS']
                ctl.set_val(self._line(value, 0, self._max_brightness, ctl.min, ctl.max))
            else:
                value = int(value) / self._max_brightness
                self._capture.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, value)

    def set_contrast(self, value):
        if self._is_connected:
            if system == 'Darwin':
                ctl = self.controls['UVCC_REQ_CONTRAST_ABS']
                ctl.set_val(self._line(value, 0, self._max_contrast, ctl.min, ctl.max))
            else:
                value = int(value) / self._max_contrast
                self._capture.set(cv2.cv.CV_CAP_PROP_CONTRAST, value)

    def set_saturation(self, value):
        if self._is_connected:
            if system == 'Darwin':
                ctl = self.controls['UVCC_REQ_SATURATION_ABS']
                ctl.set_val(self._line(value, 0, self._max_saturation, ctl.min, ctl.max))
            else:
                value = int(value) / self._max_saturation
                self._capture.set(cv2.cv.CV_CAP_PROP_SATURATION, value)

    def set_exposure(self, value):
        if self._is_connected:
            if system == 'Darwin':
                ctl = self.controls['UVCC_REQ_EXPOSURE_ABS']
                value = int(value * self._rel_exposure)
                ctl.set_val(value)
            elif system == 'Windows':
                value = int(round(-math.log(value) / math.log(2)))
                self._capture.set(cv2.cv.CV_CAP_PROP_EXPOSURE, value)
            else:
                value = int(value) / self._max_exposure
                self._capture.set(cv2.cv.CV_CAP_PROP_EXPOSURE, value)

    def set_frame_rate(self, value):
        if self._is_connected:
            self._capture.set(cv2.cv.CV_CAP_PROP_FPS, value)

    def _set_width(self, value):
        if self._is_connected:
            self._capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, value)

    def _set_height(self, value):
        if self._is_connected:
            self._capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, value)

    def _update_resolution(self):
        if self._is_connected:
            self._width = int(self._capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
            self._height = int(self._capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

    def set_resolution(self, width, height):
        if self._is_connected:
            self._set_width(width)
            self._set_height(height)
            self._update_resolution()

    def set_use_distortion(self, value):
        self.use_distortion = value

    @property
    def camera_matrix(self):
        return self._camera_matrix

    @camera_matrix.setter
    def camera_matrix(self, value):
        self._camera_matrix = value
        self._compute_dist_camera_matrix()

    @property
    def distortion_vector(self):
        return self._distortion_vector

    @distortion_vector.setter
    def distortion_vector(self, value):
        self._distortion_vector = value
        self._compute_dist_camera_matrix()

    def _compute_dist_camera_matrix(self):
        if self._camera_matrix is not None and self._distortion_vector is not None:
            self._dist_camera_matrix = cv2.getOptimalNewCameraMatrix(
                self._camera_matrix, self._distortion_vector,
                (int(self._width), int(self._height)), alpha=1)[0]

    def get_brightness(self):
        if self._is_connected:
            if system == 'Darwin':
                ctl = self.controls['UVCC_REQ_BRIGHTNESS_ABS']
                value = ctl.get_val()
            else:
                value = self._capture.get(cv2.cv.CV_CAP_PROP_BRIGHTNESS)
                value *= self._max_brightness
            return value

    def get_exposure(self):
        if self._is_connected:
            if system == 'Darwin':
                ctl = self.controls['UVCC_REQ_EXPOSURE_ABS']
                value = ctl.get_val()
                value /= self._rel_exposure
            elif system == 'Exposure':
                value = self._capture.get(cv2.cv.CV_CAP_PROP_EXPOSURE)
                value = 2 ** -value
            else:
                value = self._capture.get(cv2.cv.CV_CAP_PROP_EXPOSURE)
                value *= self._max_exposure
            return value

    def get_resolution(self):
        return int(self._height), int(self._width)  # Inverted values because of transpose

    def _success(self):
        self._tries = 0

    def _fail(self):
        self._tries += 1
        if self._tries >= self._number_frames_fail:
            self._tries = 0
            if self.unplug_callback is not None and \
               self.parent is not None and \
               not self.parent.unplugged:
                self.parent.unplugged = True
                self.unplug_callback()

    def _line(self, value, imin, imax, omin, omax):
        ret = 0
        if omin is not None and omax is not None:
            if (imax - imin) != 0:
                ret = int((value - imin) * (omax - omin) / (imax - imin) + omin)
        return ret
