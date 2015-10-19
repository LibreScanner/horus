# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.util import profile

from horus.gui.engine import driver, image_capture
from horus.gui.workbench.workbench import WorkbenchConnection
from horus.gui.workbench.control.panels import CameraControl, LaserControl, \
    LDRControl, MotorControl, GcodeControl


class ControlWorkbench(WorkbenchConnection):

    def __init__(self, parent):
        WorkbenchConnection.__init__(self, parent)

    def load_controls(self):
        self.controls.add_panel(CameraControl, 'camera_control')
        self.controls.add_panel(LaserControl, 'laser_control')
        self.controls.add_panel(LDRControl, 'ldr_value')
        self.controls.add_panel(MotorControl, 'motor_control')
        self.controls.add_panel(GcodeControl, 'gcode_control')

    def update_engine(self):
        resolution = profile.settings['resolution'].split('x')
        driver.camera.set_frame_rate(int(profile.settings['framerate']))
        driver.camera.set_resolution(int(resolution[1]), int(resolution[0]))
        image_capture.texture_mode.brightness = profile.settings['brightness_texture_control']
        image_capture.texture_mode.contrast = profile.settings['contrast_texture_control']
        image_capture.texture_mode.saturation = profile.settings['saturation_texture_control']
        image_capture.texture_mode.exposure = profile.settings['exposure_texture_control']
        image_capture.use_distortion = profile.settings['use_distortion']
