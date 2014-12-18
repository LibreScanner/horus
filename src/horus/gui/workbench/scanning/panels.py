#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: November 2014                                                   #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>                    #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 2 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
# GNU General Public License for more details.                          #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>.  #
#                                                                       #
#-----------------------------------------------------------------------#

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v2 http://www.gnu.org/licenses/gpl.html"


import os
import wx._core

from horus.gui.util.customPanels import ExpandablePanel, Slider, ComboBox, \
                                        CheckBox, Button, TextBox

from horus.util import profile

from horus.engine.driver import Driver
from horus.engine.scan import SimpleScan, TextureScan, PointCloudGenerator


class ScanParameters(ExpandablePanel):
    """"""
    def __init__(self, parent):
        """"""
        ExpandablePanel.__init__(self, parent, _("Scan Parameters"))
        
        self.driver = Driver.Instance()
        self.simpleScan = SimpleScan.Instance()
        self.textureScan = TextureScan.Instance()
        self.pcg = PointCloudGenerator.Instance()
        self.main = self.GetParent().GetParent().GetParent().GetParent()

        self.initialize()
        
    def initialize(self):
        self.clearSections()
        section = self.createSection('scan_parameters')
        section.addItem(ComboBox, 'scan_type', self.setCurrentScan)
        section.addItem(ComboBox, 'use_laser', self.setUseLaser)
        if os.name != 'nt':
            section.addItem(CheckBox, 'fast_scan', self.setFastScan)

    def setFastScan(self, value):
        self.simpleScan.setFastScan(bool(value))
        self.textureScan.setFastScan(bool(value))

    def setUseLaser(self, value):
        self.pcg.setUseLaser(value==_("Use Left Laser") or value==_("Use Both Laser"),
                             value==_("Use Right Laser") or value==_("Use Both Laser"))

    def setCurrentScan(self, value):
        if not self.main.currentScan.run or self.main.currentScan.inactive:
            if value == _("Without Texture"):
                self.main.currentScan = self.simpleScan
            elif value == _("With Texture"):
                self.main.currentScan = self.textureScan
        else:
            print "Can not change scan type"


class RotativePlatform(ExpandablePanel):
    """"""
    def __init__(self, parent):
        """"""
        ExpandablePanel.__init__(self, parent, _("Rotative Platform"), hasUndo=False)
        
        self.driver = Driver.Instance()
        self.simpleScan = SimpleScan.Instance()
        self.textureScan = TextureScan.Instance()
        self.pcg = PointCloudGenerator.Instance()
        self.main = self.GetParent().GetParent().GetParent().GetParent()

        self.initialize()
        
    def initialize(self):
        self.clearSections()
        section = self.createSection('motor_scanning')
        section.addItem(TextBox, 'step_degrees_scanning', self.setDegrees)
        section.addItem(TextBox, 'feed_rate_scanning', self.setFeedRate)
        section.addItem(TextBox, 'acceleration_scanning', self.setAcceleration)

    def setDegrees(self, value):
        self.driver.board.setRelativePosition(self.getValueFloat(value))
        self.pcg.setDegrees(self.getValueFloat(value))

    def setFeedRate(self, value):
        self.driver.board.setSpeedMotor(self.getValueInteger(value))
        self.simpleScan.setSpeedMotor(self.getValueInteger(value))
        self.textureScan.setSpeedMotor(self.getValueInteger(value))

    def setAcceleration(self, value):
        self.driver.board.setAccelerationMotor(self.getValueInteger(value))
        self.simpleScan.setAccelerationMotor(self.getValueInteger(value))
        self.textureScan.setAccelerationMotor(self.getValueInteger(value))

    #TODO: move
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
    """"""
    def __init__(self, parent):
        """"""
        ExpandablePanel.__init__(self, parent, _("Image Acquisition"))

        self.driver = Driver.Instance()
        self.pcg = PointCloudGenerator.Instance()
        self.simpleScan = SimpleScan.Instance()
        self.textureScan = TextureScan.Instance()
        self.main = self.GetParent().GetParent().GetParent().GetParent()

        self.initialize()
        
    def initialize(self):
        self.clearSections()
        section = self.createSection('camera_scanning') #, _("Camera"))
        section.addItem(Slider, 'brightness_scanning', self.driver.camera.setBrightness)
        section.addItem(Slider, 'contrast_scanning', self.driver.camera.setContrast)
        section.addItem(Slider, 'saturation_scanning', self.driver.camera.setSaturation)
        #section.addItem(Slider, 'exposure_scanning', self.driver.camera.setExposure)
        section.addItem(Slider, 'laser_exposure_scanning', self.setLaserExposure)
        section.addItem(Slider, 'color_exposure_scanning', self.setColorExposure)
        section.addItem(ComboBox, 'framerate_scanning', lambda v: (self.driver.camera.setFrameRate(int(v)), self.reloadVideo()))
        section.addItem(ComboBox, 'resolution_scanning', lambda v: self.driver.camera.setResolution(int(v.split('x')[0]), int(v.split('x')[1])))
        #section.addItem(CheckBox, 'use_distortion_scanning', lambda v: (self.driver.camera.setUseDistortion(v), self.reloadVideo()))

    def setLaserExposure(self, value):
        if self.main.currentScan is self.simpleScan:
            self.driver.camera.setExposure(value)

    def setColorExposure(self, value):
        if self.main.currentScan is self.textureScan:
            self.driver.camera.setExposure(value)

    def reloadVideo(self):
        if self.main.IsShown():
            self.main.videoView.play()


class ImageSegmentation(ExpandablePanel):
    """"""
    def __init__(self, parent):
        """"""
        ExpandablePanel.__init__(self, parent, _("Image Segmentation"))
        
        self.driver = Driver.Instance()
        self.pcg = PointCloudGenerator.Instance()
        self.simpleScan = SimpleScan.Instance()
        self.textureScan = TextureScan.Instance()

        self.initialize()
        
    def initialize(self):
        self.clearSections()
        section = self.createSection('image_segmentation_simple', _("Simple Scan"))
        section.addItem(CheckBox, 'use_cr_threshold', lambda v: self.simpleScan.setUseThreshold(bool(v)))
        section.addItem(Slider, 'cr_threshold_value', lambda v: self.simpleScan.setThresholdValue(int(v)))
        section = self.createSection('image_segmentation_texture', _("Texture Scan"))
        section.addItem(CheckBox, 'use_open', lambda v: self.textureScan.setUseOpen(bool(v)))
        section.addItem(Slider, 'open_value', lambda v: self.textureScan.setOpenValue(int(v)))
        section.addItem(CheckBox, 'use_threshold', lambda v: self.textureScan.setUseThreshold(bool(v)))
        section.addItem(Slider, 'threshold_value', lambda v: self.textureScan.setThresholdValue(int(v)))


class PointCloudGeneration(ExpandablePanel):
    """"""
    def __init__(self, parent):
        """"""
        ExpandablePanel.__init__(self, parent, _("Point Cloud Generation"))
        
        self.driver = Driver.Instance()
        self.simpleScan = SimpleScan.Instance()
        self.pcg = PointCloudGenerator.Instance()
        self.main = self.GetParent().GetParent().GetParent().GetParent()

        self.initialize()
        
    def initialize(self):
        self.clearSections()
        section = self.createSection('point_cloud_generation')
        section.addItem(CheckBox, 'view_roi', lambda v: (self.pcg.setViewROI(bool(v)), self.main.sceneView.QueueRefresh()))
        section.addItem(Slider, 'roi_diameter', lambda v: (self.pcg.setROIDiameter(int(v)), self.main.sceneView.QueueRefresh()))
        section.addItem(Slider, 'roi_height', lambda v: (self.pcg.setROIHeight(int(v)), self.main.sceneView.QueueRefresh()))
        section.addItem(Button, 'point_cloud_color', self.onColourPicker)

    def onColourPicker(self):
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