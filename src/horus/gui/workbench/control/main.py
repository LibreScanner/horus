# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.util import profile

from horus.gui.engine import driver, image_capture
from horus.gui.workbench.workbench import Workbench
from horus.gui.workbench.control.panels import CameraControl, LaserControl, \
    LDRControl, MotorControl, GcodeControl


class ControlWorkbench(Workbench):

    def __init__(self, parent):
        Workbench.__init__(self, parent, name=_('Control workbench'))

    def add_panels(self):
        self.add_panel('camera_control', CameraControl)
        self.add_panel('laser_control', LaserControl)
        self.add_panel('ldr_value', LDRControl)
        self.add_panel('motor_control', MotorControl)
        self.add_panel('gcode_control', GcodeControl)

    def setup_engine(self):
        resolution = profile.settings['resolution'].split('x')
        driver.camera.set_frame_rate(int(profile.settings['framerate']))
        driver.camera.set_resolution(int(resolution[1]), int(resolution[0]))
        image_capture.set_mode_texture()
        image_capture.texture_mode.set_brightness(profile.settings['brightness_control'])
        image_capture.texture_mode.set_contrast(profile.settings['contrast_control'])
        image_capture.texture_mode.set_saturation(profile.settings['saturation_control'])
        image_capture.texture_mode.set_exposure(profile.settings['exposure_control'])
        image_capture.set_use_distortion(profile.settings['use_distortion'])

    def video_frame(self):
        return image_capture.capture_image()
