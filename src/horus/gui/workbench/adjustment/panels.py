# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.util import profile

from horus.gui.engine import image_capture, laser_segmentation

from horus.gui.workbench.adjustment.current_video import CurrentVideo
from horus.gui.util.custom_panels import ExpandablePanel, Slider, ComboBox, CheckBox

current_video = CurrentVideo()


class ScanCapturePanel(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Scan capture"))

    def add_controls(self):
        self.add_control('capture_mode_scanning', ComboBox)
        self.add_control(
            'brightness_texture_scanning', Slider,
            _("Image luminosity. Low values are better for environments with high ambient "
              "light conditions. High values are recommended for poorly lit places"))
        self.add_control(
            'contrast_texture_scanning', Slider,
            _("Relative difference in intensity between an image point and its "
              "surroundings. Low values are recommended for black or very dark colored "
              "objects. High values are better for very light colored objects"))
        self.add_control(
            'saturation_texture_scanning', Slider,
            _("Purity of color. Low values will cause colors to disappear from the image. "
              "High values will show an image with very intense colors"))
        self.add_control(
            'exposure_texture_scanning', Slider,
            _("Amount of light per unit area. It is controlled by the time the camera "
              "sensor is exposed during a frame capture. "
              "High values are recommended for poorly lit places"))
        self.add_control(
            'brightness_laser_scanning', Slider,
            _("Image luminosity. Low values are better for environments with high ambient "
              "light conditions. High values are recommended for poorly lit places"))
        self.add_control(
            'contrast_laser_scanning', Slider,
            _("Relative difference in intensity between an image point and its "
              "surroundings. Low values are recommended for black or very dark colored "
              "objects. High values are better for very light colored objects"))
        self.add_control(
            'saturation_laser_scanning', Slider,
            _("Purity of color. Low values will cause colors to disappear from the image. "
              "High values will show an image with very intense colors"))
        self.add_control(
            'exposure_laser_scanning', Slider,
            _("Amount of light per unit area. It is controlled by the time the camera "
              "sensor is exposed during a frame capture. "
              "High values are recommended for poorly lit places"))
        self.add_control('remove_background_scanning', CheckBox)

        # Initial layout
        self._set_camera_mode(profile.settings['capture_mode_scanning'])

    def update_callbacks(self):
        self.update_callback('capture_mode_scanning', lambda v: self._set_camera_mode(v))

        mode = image_capture.texture_mode
        self.update_callback('brightness_texture_scanning', mode.set_brightness)
        self.update_callback('contrast_texture_scanning', mode.set_contrast)
        self.update_callback('saturation_texture_scanning', mode.set_saturation)
        self.update_callback('exposure_texture_scanning', mode.set_exposure)

        mode = image_capture.laser_mode
        self.update_callback('brightness_laser_scanning', mode.set_brightness)
        self.update_callback('contrast_laser_scanning', mode.set_contrast)
        self.update_callback('saturation_laser_scanning', mode.set_saturation)
        self.update_callback('exposure_laser_scanning', mode.set_exposure)
        self.update_callback('remove_background_scanning', image_capture.set_remove_background)

    def on_selected(self):
        current_video.mode = profile.settings['capture_mode_scanning']

    def _set_camera_mode(self, mode):
        if mode == 'Laser':
            self.get_control('brightness_texture_scanning').Hide()
            self.get_control('contrast_texture_scanning').Hide()
            self.get_control('saturation_texture_scanning').Hide()
            self.get_control('exposure_texture_scanning').Hide()
            self.get_control('brightness_laser_scanning').Show()
            self.get_control('contrast_laser_scanning').Show()
            self.get_control('saturation_laser_scanning').Show()
            self.get_control('exposure_laser_scanning').Show()
            self.get_control('remove_background_scanning').Show()
        elif mode == 'Texture':
            self.get_control('brightness_texture_scanning').Show()
            self.get_control('contrast_texture_scanning').Show()
            self.get_control('saturation_texture_scanning').Show()
            self.get_control('exposure_texture_scanning').Show()
            self.get_control('brightness_laser_scanning').Hide()
            self.get_control('contrast_laser_scanning').Hide()
            self.get_control('saturation_laser_scanning').Hide()
            self.get_control('exposure_laser_scanning').Hide()
            self.get_control('remove_background_scanning').Hide()
        current_video.mode = mode
        self.GetParent().Layout()


class ScanSegmentationPanel(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Scan segmentation"))

    def add_controls(self):
        self.add_control('red_channel_scanning', ComboBox)
        self.add_control('open_value_scanning', Slider)
        self.add_control(
            'open_enable_scanning',
            CheckBox,
            "Open is an operation used to remove the noise when scanning. The higher its value, "
            "the lower the noise but also the lower the detail in the image")
        self.add_control('threshold_value_scanning', Slider)
        self.add_control(
            'threshold_enable_scanning',
            CheckBox,
            "Threshold is a function used to remove the noise when scanning. "
            "It removes a pixel if its intensity is less than the threshold value")

    def update_callbacks(self):
        self.update_callback('red_channel_scanning', laser_segmentation.set_red_channel)
        self.update_callback('open_value_scanning', laser_segmentation.set_open_value)
        self.update_callback('open_enable_scanning', laser_segmentation.set_open_enable)
        self.update_callback('threshold_value_scanning', laser_segmentation.set_threshold_value)
        self.update_callback('threshold_enable_scanning', laser_segmentation.set_threshold_enable)

    def on_selected(self):
        current_video.mode = 'Gray'


class CalibrationCapturePanel(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Calibration capture"))

    def add_controls(self):
        self.add_control('capture_mode_calibration', ComboBox)
        self.add_control(
            'brightness_pattern_calibration', Slider,
            _("Image luminosity. Low values are better for environments with high ambient "
              "light conditions. High values are recommended for poorly lit places"))
        self.add_control(
            'contrast_pattern_calibration', Slider,
            _("Relative difference in intensity between an image point and its "
              "surroundings. Low values are recommended for black or very dark colored "
              "objects. High values are better for very light colored objects"))
        self.add_control(
            'saturation_pattern_calibration', Slider,
            _("Purity of color. Low values will cause colors to disappear from the image. "
              "High values will show an image with very intense colors"))
        self.add_control(
            'exposure_pattern_calibration', Slider,
            _("Amount of light per unit area. It is controlled by the time the camera "
              "sensor is exposed during a frame capture. "
              "High values are recommended for poorly lit places"))
        self.add_control(
            'brightness_laser_calibration', Slider,
            _("Image luminosity. Low values are better for environments with high ambient "
              "light conditions. High values are recommended for poorly lit places"))
        self.add_control(
            'contrast_laser_calibration', Slider,
            _("Relative difference in intensity between an image point and its "
              "surroundings. Low values are recommended for black or very dark colored "
              "objects. High values are better for very light colored objects"))
        self.add_control(
            'saturation_laser_calibration', Slider,
            _("Purity of color. Low values will cause colors to disappear from the image. "
              "High values will show an image with very intense colors"))
        self.add_control(
            'exposure_laser_calibration', Slider,
            _("Amount of light per unit area. It is controlled by the time the camera "
              "sensor is exposed during a frame capture. "
              "High values are recommended for poorly lit places"))
        self.add_control('remove_background_calibration', CheckBox)

        # Initial layout
        self._set_camera_mode(profile.settings['capture_mode_calibration'])

    def update_callbacks(self):
        self.update_callback('capture_mode_calibration', lambda v: self._set_camera_mode(v))

        mode = image_capture.pattern_mode
        self.update_callback('brightness_pattern_calibration', mode.set_brightness)
        self.update_callback('contrast_pattern_calibration', mode.set_contrast)
        self.update_callback('saturation_pattern_calibration', mode.set_saturation)
        self.update_callback('exposure_pattern_calibration', mode.set_exposure)

        mode = image_capture.laser_mode
        self.update_callback('brightness_laser_calibration', mode.set_brightness)
        self.update_callback('contrast_laser_calibration', mode.set_contrast)
        self.update_callback('saturation_laser_calibration', mode.set_saturation)
        self.update_callback('exposure_laser_calibration', mode.set_exposure)
        self.update_callback('remove_background_calibration', image_capture.set_remove_background)

    def on_selected(self):
        current_video.mode = profile.settings['capture_mode_calibration']

    def _set_camera_mode(self, mode):
        if mode == 'Laser':
            self.get_control('brightness_pattern_calibration').Hide()
            self.get_control('contrast_pattern_calibration').Hide()
            self.get_control('saturation_pattern_calibration').Hide()
            self.get_control('exposure_pattern_calibration').Hide()
            self.get_control('brightness_laser_calibration').Show()
            self.get_control('contrast_laser_calibration').Show()
            self.get_control('saturation_laser_calibration').Show()
            self.get_control('exposure_laser_calibration').Show()
            self.get_control('remove_background_calibration').Show()
        elif mode == 'Pattern':
            self.get_control('brightness_pattern_calibration').Show()
            self.get_control('contrast_pattern_calibration').Show()
            self.get_control('saturation_pattern_calibration').Show()
            self.get_control('exposure_pattern_calibration').Show()
            self.get_control('brightness_laser_calibration').Hide()
            self.get_control('contrast_laser_calibration').Hide()
            self.get_control('saturation_laser_calibration').Hide()
            self.get_control('exposure_laser_calibration').Hide()
            self.get_control('remove_background_calibration').Hide()
        current_video.mode = mode
        self.GetParent().Layout()


class CalibrationSegmentationPanel(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Calibration segmentation"))

    def add_controls(self):
        self.add_control('red_channel_calibration', ComboBox)
        self.add_control('open_value_calibration', Slider)
        self.add_control(
            'open_enable_calibration',
            CheckBox,
            "Open is an operation used to remove the noise when scanning. The higher its value, "
            "the lower the noise but also the lower the detail in the image")
        self.add_control('threshold_value_calibration', Slider)
        self.add_control(
            'threshold_enable_calibration',
            CheckBox,
            "Threshold is a function used to remove the noise when scanning. "
            "It removes a pixel if its intensity is less than the threshold value")

    def update_callbacks(self):
        self.update_callback('red_channel_calibration', laser_segmentation.set_red_channel)
        self.update_callback('open_value_calibration', laser_segmentation.set_open_value)
        self.update_callback('open_enable_calibration', laser_segmentation.set_open_enable)
        self.update_callback('threshold_value_calibration', laser_segmentation.set_threshold_value)
        self.update_callback(
            'threshold_enable_calibration', laser_segmentation.set_threshold_enable)

    def on_selected(self):
        current_video.mode = 'Gray'
