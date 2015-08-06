# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


import wx._core

from horus.gui.util.customPanels import ExpandablePanel, Slider, ComboBox, \
    CheckBox, Button, TextBox

from horus.util import profile, system as sys
from horus.gui.util.resolutionWindow import ResolutionWindow

from horus.engine.driver.driver import Driver
from horus.engine.scan.ciclop_scan import CiclopScan
from horus.engine.algorithms.laser_segmentation import LaserSegmentation
from horus.engine.algorithms.point_cloud_generation import PointCloudGeneration

driver = Driver()
ciclop_scan = CiclopScan()
laser_segmentation = LaserSegmentation()
point_cloud_generation = PointCloudGeneration()


class ScanParameters(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(
            self, parent, _("Scan Parameters"), hasUndo=False, hasRestore=False)

        self.parent = parent

        self.clearSections()
        section = self.createSection('scan_parameters')
        section.addItem(CheckBox, 'capture_texture')
        section.addItem(CheckBox, 'use_left_laser')
        section.addItem(CheckBox, 'use_right_laser')
        section.addItem(CheckBox, 'remove_background')

    def updateCallbacks(self):
        section = self.sections['scan_parameters']
        section.updateCallback('capture_texture', ciclop_scan.set_capture_texture)
        section.updateCallback('use_left_laser', ciclop_scan.set_use_left_laser)
        section.updateCallback('use_right_laser', ciclop_scan.set_use_right_laser)
        section.updateCallback('remove_background', ciclop_scan.set_remove_background)


class RotativePlatform(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Rotative Platform"), hasUndo=False)

        self.clearSections()
        section = self.createSection('motor_scanning')
        section.addItem(TextBox, 'motor_step_scanning')
        section.addItem(TextBox, 'motor_speed_scanning')
        section.addItem(TextBox, 'motor_acceleration_scanning')

    def updateCallbacks(self):
        section = self.sections['motor_scanning']
        section.updateCallback('motor_step_scanning', lambda v: ciclop_scan.set_motor_step(self.getValueFloat(v)))
        section.updateCallback('motor_speed_scanning', lambda v: ciclop_scan.set_motor_speed(self.getValueInteger(v)))
        section.updateCallback('motor_acceleration_scanning', lambda v: ciclop_scan.set_motor_acceleration(self.getValueInteger(v)))

    # TODO: move
    def getValueInteger(self, value):
        try:
            return int(eval(value, {}, {}))
        except:
            return 0

    def getValueFloat(self, value):
        try:
            return float(eval(value.replace(',', '.'), {}, {}))
        except:
            return 0.0


class ImageAcquisition(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Image Acquisition"))

        self.last_resolution = profile.getProfileSetting('resolution_scanning')

        self.clearSections()
        section = self.createSection('camera_scanning')
        section.addItem(Slider, 'brightness_scanning', tooltip=_(
            'Image luminosity. Low values are better for environments with high ambient light conditions. High values are recommended for poorly lit places'))
        section.addItem(Slider, 'contrast_scanning', tooltip=_(
            'Relative difference in intensity between an image point and its surroundings. Low values are recommended for black or very dark colored objects. High values are better for very light colored objects'))
        section.addItem(Slider, 'saturation_scanning', tooltip=_(
            'Purity of color. Low values will cause colors to disappear from the image. High values will show an image with very intense colors'))
        section.addItem(Slider, 'exposure_texture_scanning', tooltip=_(
            'Amount of light per unit area. It is controlled by the time the camera sensor is exposed during a frame capture. High values are recommended for poorly lit places'))
        section.addItem(Slider, 'exposure_laser_scanning', tooltip=_(
            ''))
        section.addItem(ComboBox, 'framerate_scanning', tooltip=_(
            'Number of frames captured by the camera every second. Maximum frame rate is recommended'))
        section.addItem(ComboBox, 'resolution_scanning', tooltip=_(
            'Size of the video. Maximum resolution is recommended'))
        section.addItem(CheckBox, 'use_distortion_scanning', tooltip=_(
            "This option applies lens distortion correction to the video. This process slows the video feed from the camera"))

        if sys.isDarwin():
            section = self.sections['camera_scanning'].disable('framerate_scanning')
            section = self.sections['camera_scanning'].disable('resolution_scanning')

    def updateCallbacks(self):
        section = self.sections['camera_scanning']
        section.updateCallback('brightness_scanning', driver.camera.set_brightness)
        section.updateCallback('contrast_scanning', driver.camera.set_contrast)
        section.updateCallback('saturation_scanning', driver.camera.set_saturation)
        section.updateCallback('exposure_texture_scanning', ciclop_scan.set_exposure_texture)
        section.updateCallback('exposure_laser_scanning', ciclop_scan.set_exposure_laser)
        section.updateCallback(
            'framerate_scanning', lambda v: driver.camera.set_frame_rate(int(v)))
        section.updateCallback('resolution_scanning', lambda v: self.setResolution(v))
        section.updateCallback(
            'use_distortion_scanning', lambda v: driver.camera.set_use_distortion(v))

    def setResolution(self, value):
        if value != self.last_resolution:
            ResolutionWindow(self)
        driver.camera.set_resolution(int(value.split('x')[0]), int(value.split('x')[1]))
        self.last_resolution = profile.getProfileSetting('resolution_scanning')


class ImageSegmentation(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Image Segmentation"))

        self.clearSections()

        section = self.createSection('image_segmentation', None)
        section.addItem(Slider, 'open_value')
        section.addItem(CheckBox, 'open_enable', tooltip=_(
            "Open is an operation used to remove the noise when scanning. The higher its value, the lower the noise but also the lower the detail in the image"))
        section.addItem(Slider, 'threshold_value')
        section.addItem(CheckBox, 'threshold_enable', tooltip=_(
            "Threshold is a function used to remove the noise when scanning. It removes a pixel if its intensity is less than the threshold value"))

    def updateCallbacks(self):
        section = self.sections['image_segmentation']
        section.updateCallback('open_value', laser_segmentation.set_open_value)
        section.updateCallback('open_enable', laser_segmentation.set_open_enable)
        section.updateCallback(
            'threshold_value', laser_segmentation.set_threshold_value)
        section.updateCallback(
            'threshold_enable', laser_segmentation.set_threshold_enable)


class PointCloudGeneration(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Point Cloud Generation"))

        self.main = self.GetParent().GetParent().GetParent().GetParent()

        self.clearSections()
        section = self.createSection('point_cloud_generation')
        section.addItem(CheckBox, 'view_roi', tooltip=_(
            "View the Region Of Interest (ROI). This cylindrical region is the one being scanned. All information outside won't be taken into account during the scanning process"))
        section.addItem(Slider, 'roi_diameter')
        section.addItem(Slider, 'roi_height')
        section.addItem(Button, 'point_cloud_color')

    # TODO: refactor
    def updateCallbacks(self):
        section = self.sections['point_cloud_generation']
        section.updateCallback('view_roi', lambda v: (
            point_cloud_generation.setViewROI(bool(v)), self.main.sceneView.QueueRefresh()))
        section.updateCallback('roi_diameter', lambda v: (
            point_cloud_generation.setROIDiameter(int(v)), self.main.sceneView.QueueRefresh()))
        section.updateCallback('roi_height', lambda v: (
            point_cloud_generation.setROIHeight(int(v)), self.main.sceneView.QueueRefresh()))
        section.updateCallback('point_cloud_color', self.onColorPicker)

    def onColorPicker(self):
        data = wx.ColourData()
        data.SetColour(self.simpleScan.color)
        dialog = wx.ColourDialog(self, data)
        dialog.GetColourData().SetChooseFull(True)
        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetColourData()
            color = data.GetColour().Get()
            self.simpleScan.setColor(color)
            profile.putProfileSetting('point_cloud_color', "".join(map(chr, color)).encode('hex'))
        dialog.Destroy()
