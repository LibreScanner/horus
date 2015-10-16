# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.gui.workbench.calibration.current_video import CurrentVideo
from horus.gui.util.customPanels import ExpandablePanel, Slider, ComboBox, CheckBox

from horus.util import profile

from horus.engine.driver.driver import Driver
from horus.engine.algorithms.image_capture import ImageCapture
from horus.engine.algorithms.image_detection import ImageDetection
from horus.engine.algorithms.laser_segmentation import LaserSegmentation


driver = Driver()
image_capture = ImageCapture()
image_detection = ImageDetection()
laser_segmentation = LaserSegmentation()
current_video = CurrentVideo()


class ScanCapturePanel(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Scan capture"), callback=self.callback)

        self.clearSections()
        section = self.createSection('image_capture')
        section.addItem(ComboBox, 'capture_mode_scanning')

        section = self.createSection('texture_mode')
        section.addItem(Slider, 'brightness_texture_scanning', tooltip=_(
            "Image luminosity. Low values are better for environments with high "
            "ambient light conditions. High values are recommended for poorly lit places"))
        section.addItem(Slider, 'contrast_texture_scanning', tooltip=_(
            "Relative difference in intensity between an image point and its surroundings. "
            "Low values are recommended for black or very dark colored objects. "
            "High values are better for very light colored objects"))
        section.addItem(Slider, 'saturation_texture_scanning', tooltip=_(
            "Purity of color. Low values will cause colors to disappear from the image. "
            "High values will show an image with very intense colors"))
        section.addItem(Slider, 'exposure_texture_scanning', tooltip=_(
            "Amount of light per unit area. It is controlled by the time the camera sensor is "
            "exposed during a frame capture. High values are recommended for poorly lit places"))

        section = self.createSection('laser_mode')
        section.addItem(Slider, 'brightness_laser_scanning', tooltip=_(
            "Image luminosity. Low values are better for environments with high "
            "ambient light conditions. High values are recommended for poorly lit places"))
        section.addItem(Slider, 'contrast_laser_scanning', tooltip=_(
            "Relative difference in intensity between an image point and its surroundings. "
            "Low values are recommended for black or very dark colored objects. "
            "High values are better for very light colored objects"))
        section.addItem(Slider, 'saturation_laser_scanning', tooltip=_(
            "Purity of color. Low values will cause colors to disappear from the image. "
            "High values will show an image with very intense colors"))
        section.addItem(Slider, 'exposure_laser_scanning', tooltip=_(
            "Amount of light per unit area. It is controlled by the time the camera sensor is "
            "exposed during a frame capture. High values are recommended for poorly lit places"))
        section.addItem(CheckBox, 'remove_background_scanning')
        section.Hide()

    def callback(self):
        self.setCameraMode(profile.settings['capture_mode_scanning'])

    def updateCallbacks(self):
        section = self.sections['image_capture']
        section.updateCallback('capture_mode_scanning', lambda v: self.setCameraMode(v))

        mode = image_capture.pattern_mode

        mode = image_capture.texture_mode
        section = self.sections['texture_mode']
        section.updateCallback('brightness_texture_scanning', mode.set_brightness)
        section.updateCallback('contrast_texture_scanning', mode.set_contrast)
        section.updateCallback('saturation_texture_scanning', mode.set_saturation)
        section.updateCallback('exposure_texture_scanning', mode.set_exposure)

        mode = image_capture.laser_mode
        section = self.sections['laser_mode']
        section.updateCallback('brightness_laser_scanning', mode.set_brightness)
        section.updateCallback('contrast_laser_scanning', mode.set_contrast)
        section.updateCallback('saturation_laser_scanning', mode.set_saturation)
        section.updateCallback('exposure_laser_scanning', mode.set_exposure)
        section.updateCallback('remove_background_scanning', image_capture.set_remove_background)

    def setCameraMode(self, mode):
        if mode == 'Laser':
            self.sections['laser_mode'].Show()
            self.sections['texture_mode'].Hide()
        elif mode == 'Texture':
            self.sections['laser_mode'].Hide()
            self.sections['texture_mode'].Show()
        current_video.mode = mode
        self.GetParent().Layout()


class ScanSegmentationPanel(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Scan segmentation"), callback=self.callback)

        self.clearSections()
        section = self.createSection('laser_segmentation', None)
        section.addItem(ComboBox, 'red_channel_scanning')
        section.addItem(Slider, 'open_value_scanning')
        section.addItem(CheckBox, 'open_enable_scanning', tooltip=_(
            "Open is an operation used to remove the noise when scanning. The higher its value, "
            "the lower the noise but also the lower the detail in the image"))
        section.addItem(Slider, 'threshold_value_scanning')
        section.addItem(CheckBox, 'threshold_enable_scanning', tooltip=_(
            "Threshold is a function used to remove the noise when scanning. "
            "It removes a pixel if its intensity is less than the threshold value"))

    def callback(self):
        current_video.mode = 'Gray'

    def updateCallbacks(self):
        section = self.sections['laser_segmentation']
        section.updateCallback('red_channel_scanning', laser_segmentation.set_red_channel)
        section.updateCallback('open_value_scanning', laser_segmentation.set_open_value)
        section.updateCallback('open_enable_scanning', laser_segmentation.set_open_enable)
        section.updateCallback(
            'threshold_value_scanning', laser_segmentation.set_threshold_value)
        section.updateCallback(
            'threshold_enable_scanning', laser_segmentation.set_threshold_enable)


class CalibrationCapturePanel(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Calibration capture"), callback=self.callback)

        self.clearSections()
        section = self.createSection('image_capture')
        section.addItem(ComboBox, 'capture_mode_calibration')

        section = self.createSection('pattern_mode')
        section.addItem(Slider, 'brightness_pattern_calibration', tooltip=_(
            "Image luminosity. Low values are better for environments with high "
            "ambient light conditions. High values are recommended for poorly lit places"))
        section.addItem(Slider, 'contrast_pattern_calibration', tooltip=_(
            "Relative difference in intensity between an image point and its surroundings. "
            "Low values are recommended for black or very dark colored objects. "
            "High values are better for very light colored objects"))
        section.addItem(Slider, 'saturation_pattern_calibration', tooltip=_(
            "Purity of color. Low values will cause colors to disappear from the image. "
            "High values will show an image with very intense colors"))
        section.addItem(Slider, 'exposure_pattern_calibration', tooltip=_(
            "Amount of light per unit area. It is controlled by the time the camera sensor is "
            "exposed during a frame capture. High values are recommended for poorly lit places"))

        section = self.createSection('laser_mode')
        section.addItem(Slider, 'brightness_laser_calibration', tooltip=_(
            "Image luminosity. Low values are better for environments with high "
            "ambient light conditions. High values are recommended for poorly lit places"))
        section.addItem(Slider, 'contrast_laser_calibration', tooltip=_(
            "Relative difference in intensity between an image point and its surroundings. "
            "Low values are recommended for black or very dark colored objects. "
            "High values are better for very light colored objects"))
        section.addItem(Slider, 'saturation_laser_calibration', tooltip=_(
            "Purity of color. Low values will cause colors to disappear from the image. "
            "High values will show an image with very intense colors"))
        section.addItem(Slider, 'exposure_laser_calibration', tooltip=_(
            "Amount of light per unit area. It is controlled by the time the camera sensor is "
            "exposed during a frame capture. High values are recommended for poorly lit places"))
        section.addItem(CheckBox, 'remove_background_calibration')

    def callback(self):
        self.setCameraMode(profile.settings['capture_mode_calibration'])

    def updateCallbacks(self):
        section = self.sections['image_capture']
        section.updateCallback('capture_mode_calibration', lambda v: self.setCameraMode(v))

        mode = image_capture.pattern_mode
        section = self.sections['pattern_mode']
        section.updateCallback('brightness_pattern_calibration', mode.set_brightness)
        section.updateCallback('contrast_pattern_calibration', mode.set_contrast)
        section.updateCallback('saturation_pattern_calibration', mode.set_saturation)
        section.updateCallback('exposure_pattern_calibration', mode.set_exposure)

        mode = image_capture.laser_mode
        section = self.sections['laser_mode']
        section.updateCallback('brightness_laser_calibration', mode.set_brightness)
        section.updateCallback('contrast_laser_calibration', mode.set_contrast)
        section.updateCallback('saturation_laser_calibration', mode.set_saturation)
        section.updateCallback('exposure_laser_calibration', mode.set_exposure)
        section.updateCallback('remove_background_calibration', image_capture.set_remove_background)

    def setCameraMode(self, mode):
        if mode == 'Pattern':
            self.sections['pattern_mode'].Show()
            self.sections['laser_mode'].Hide()
        elif mode == 'Laser':
            self.sections['pattern_mode'].Hide()
            self.sections['laser_mode'].Show()
        current_video.mode = mode
        self.GetParent().Layout()


class CalibrationSegmentationPanel(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Calibration segmentation"),
                                 callback=self.callback)

        self.clearSections()
        section = self.createSection('laser_segmentation', None)
        section.addItem(ComboBox, 'red_channel_calibration')
        section.addItem(Slider, 'open_value_calibration')
        section.addItem(CheckBox, 'open_enable_calibration', tooltip=_(
            "Open is an operation used to remove the noise when scanning. The higher its value, "
            "the lower the noise but also the lower the detail in the image"))
        section.addItem(Slider, 'threshold_value_calibration')
        section.addItem(CheckBox, 'threshold_enable_calibration', tooltip=_(
            "Threshold is a function used to remove the noise when scanning. "
            "It removes a pixel if its intensity is less than the threshold value"))

    def callback(self):
        current_video.mode = 'Gray'

    def updateCallbacks(self):
        section = self.sections['laser_segmentation']
        section.updateCallback('red_channel_calibration', laser_segmentation.set_red_channel)
        section.updateCallback('open_value_calibration', laser_segmentation.set_open_value)
        section.updateCallback('open_enable_calibration', laser_segmentation.set_open_enable)
        section.updateCallback(
            'threshold_value_calibration', laser_segmentation.set_threshold_value)
        section.updateCallback(
            'threshold_enable_calibration', laser_segmentation.set_threshold_enable)
