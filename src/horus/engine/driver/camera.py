# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import math
import time
import glob
import platform

import logging
logger = logging.getLogger(__name__)

system = platform.system()

if system == 'Darwin':
    import uvc


class WrongCamera(Exception):

    def __init__(self):
        Exception.__init__(self, "Wrong Camera")


class CameraNotConnected(Exception):

    def __init__(self):
        Exception.__init__(self, "Camera Not Connected")


class InvalidVideo(Exception):

    def __init__(self):
        Exception.__init__(self, "Invalid Video")


class Camera(object):

    """Camera class. For accessing to the scanner camera"""

    def __init__(self, parent=None, camera_id=0):
        self.parent = parent
        self.camera_id = camera_id
        self.unplug_callback = None

        self._capture = None
        self._is_connected = False
        self._reading = False
        self._updating = False
        self._last_image = None
        self._tries = 0  # Check if command fails

        self.initialize()

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

    def initialize(self):
        self._brightness = 0
        self._contrast = 0
        self._saturation = 0
        self._exposure = 0
        self._frame_rate = 0
        self._width = 0
        self._height = 0

    def connect(self):
        logger.info("Connecting camera {0}".format(self.camera_id))
        self._is_connected = False
        self.initialize()
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
            logger.info(" Done")
        else:
            raise CameraNotConnected()

    def disconnect(self):
        tries = 0
        if self._is_connected:
            logger.info("Disconnecting camera {0}".format(self.camera_id))
            if self._capture is not None:
                if self._capture.isOpened():
                    self._is_connected = False
                    while tries < 10:
                        tries += 1
                        if not self._reading:
                            self._capture.release()
                logger.info(" Done")

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
            if self._updating:
                return self._last_image
            else:
                self._reading = True
                if flush > 0:
                    for i in xrange(0, flush):
                        self._capture.read()
                ret, image = self._capture.read()
                self._reading = False
                if ret:
                    image = cv2.transpose(image)
                    if not mirror:
                        image = cv2.flip(image, 1)
                    self._success()
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    self._last_image = image
                    return image
                else:
                    self._fail()
                    return None
        else:
            return None

    def set_brightness(self, value):
        if self._is_connected:
            if self._brightness != value:
                self._updating = True
                if system == 'Darwin':
                    ctl = self.controls['UVCC_REQ_BRIGHTNESS_ABS']
                    ctl.set_val(self._line(value, 0, self._max_brightness, ctl.min, ctl.max))
                else:
                    value = int(value) / self._max_brightness
                    self._capture.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, value)
                self._brightness = value
                self._updating = False

    def set_contrast(self, value):
        if self._is_connected:
            if self._contrast != value:
                self._updating = True
                if system == 'Darwin':
                    ctl = self.controls['UVCC_REQ_CONTRAST_ABS']
                    ctl.set_val(self._line(value, 0, self._max_contrast, ctl.min, ctl.max))
                else:
                    value = int(value) / self._max_contrast
                    self._capture.set(cv2.cv.CV_CAP_PROP_CONTRAST, value)
                self._contrast = value
                self._updating = False

    def set_saturation(self, value):
        if self._is_connected:
            if self._saturation != value:
                self._updating = True
                if system == 'Darwin':
                    ctl = self.controls['UVCC_REQ_SATURATION_ABS']
                    ctl.set_val(self._line(value, 0, self._max_saturation, ctl.min, ctl.max))
                else:
                    value = int(value) / self._max_saturation
                    self._capture.set(cv2.cv.CV_CAP_PROP_SATURATION, value)
                self._saturation = value
                self._updating = False

    def set_exposure(self, value):
        if self._is_connected:
            if self._exposure != value:
                self._updating = True
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
                self._exposure = value
                self._updating = False

    def set_frame_rate(self, value):
        if self._is_connected:
            if self._frame_rate != value:
                self._updating = True
                self._capture.set(cv2.cv.CV_CAP_PROP_FPS, value)
                self._frame_rate = value
                self._updating = False

    def set_resolution(self, height, width):
        if self._is_connected:
            if self._width != width or self._height != height:
                self._updating = True
                self._set_width(width)
                self._set_height(height)
                self._update_resolution()
                self._updating = False

    def _set_width(self, value):
        self._capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, value)

    def _set_height(self, value):
        self._capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, value)

    def _update_resolution(self):
        self._width = int(self._capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        self._height = int(self._capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

    def get_brightness(self):
        if self._is_connected:
            if system == 'Darwin':
                ctl = self.controls['UVCC_REQ_BRIGHTNESS_ABS']
                value = ctl.get_val()
            else:
                value = self._capture.get(cv2.cv.CV_CAP_PROP_BRIGHTNESS)
                value *= self._max_brightness
            self._brightness = value
            return value

    def get_exposure(self):
        if self._is_connected:
            if system == 'Darwin':
                ctl = self.controls['UVCC_REQ_EXPOSURE_ABS']
                value = ctl.get_val()
                value /= self._rel_exposure
            elif system == 'Windows':
                value = self._capture.get(cv2.cv.CV_CAP_PROP_EXPOSURE)
                value = 2 ** -value
            else:
                value = self._capture.get(cv2.cv.CV_CAP_PROP_EXPOSURE)
                value *= self._max_exposure
            self._exposure = value
            return value

    def get_resolution(self):
        return int(self._height), int(self._width)  # Inverted values because of transpose

    def _success(self):
        self._tries = 0

    def _fail(self):
        logger.debug("Camera fail")
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

    def _count_cameras(self):
        for i in xrange(5):
            cap = cv2.VideoCapture(i)
            res = not cap.isOpened()
            cap.release()
            if res:
                return i
        return 5

    def get_video_list(self):
        baselist = []
        if system == 'Windows':
            count = self._count_cameras()
            for i in xrange(count):
                baselist.append(str(i))
        elif system == 'Darwin':
            for device in uvc.mac.Camera_List():
                baselist.append(str(device.src_id))
        else:
            for device in ['/dev/video*']:
                baselist = baselist + glob.glob(device)
        return baselist
