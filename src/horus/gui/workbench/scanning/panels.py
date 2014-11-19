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


import wx._core

from horus.gui.util.customPanels import ExpandablePanel, Slider, ComboBox, \
                                        CheckBox, Button, TextBox

from horus.util import profile

from horus.engine.driver import Driver
from horus.engine.scan import SimpleScan, PointCloudGenerator


class ImageAcquisition(ExpandablePanel):
    """"""
    def __init__(self, parent):
        """"""
        ExpandablePanel.__init__(self, parent, _("Image Acquisition"))

        self.driver = Driver.Instance()
        self.simpleScan = SimpleScan.Instance()
        self.pcg = PointCloudGenerator.Instance()
        self.main = self.GetParent().GetParent().GetParent().GetParent()

        self.initialize()
        
    def initialize(self):
        self.clearSections()
        section = self.createSection('camera_scanning', _("Camera"))
        section.addItem(Slider, 'brightness_scanning', self.driver.camera.setBrightness)
        section.addItem(Slider, 'contrast_scanning', self.driver.camera.setContrast)
        section.addItem(Slider, 'saturation_scanning', self.driver.camera.setSaturation)
        section.addItem(Slider, 'exposure_scanning', self.driver.camera.setExposure)
        section.addItem(ComboBox, 'framerate_scanning', lambda v: (self.driver.camera.setFrameRate(int(v)), self.reloadVideo()))
        section.addItem(ComboBox, 'resolution_scanning', lambda v: self.driver.camera.setResolution(int(v.split('x')[0]), int(v.split('x')[1])))
        section.addItem(CheckBox, 'use_distortion_scanning', lambda v: (self.driver.camera.setUseDistortion(v), self.reloadVideo()))
        section.addItem(Button, 'restore_default', self.restoreDefault)
        section = self.createSection('laser_scanning', _("Laser"))
        section.addItem(ComboBox, 'use_laser', lambda v: self.pcg.setUseLaser(v==_("Use Left Laser") or v==_("Use Both Laser"), v==_("Use Right Laser") or v==_("Use Both Laser"))) #TODO: use combo choices
        section = self.createSection('motor_scanning', _("Motor"))
        section.addItem(TextBox, 'step_degrees_scanning', lambda v: (self.driver.board.setRelativePosition(self.getValueFloat(v)), self.pcg.setDegrees(self.getValueFloat(v))))
        section.addItem(TextBox, 'feed_rate_scanning', lambda v: (self.driver.board.setSpeedMotor(self.getValueInteger(v)), self.simpleScan.setSpeedMotor(self.getValueInteger(v))))
        section.addItem(TextBox, 'acceleration_scanning', lambda v: (self.driver.board.setAccelerationMotor(self.getValueInteger(v)), self.simpleScan.setAccelerationMotor(self.getValueInteger(v))))
        section.addItem(Button, 'restore_default', self.restoreDefault)

        #section.addItem(CheckBox, 'use_compact', lambda v: self.pcg.setUseCompact(bool(v)))
        section.addItem(CheckBox, 'fast_scan', lambda v: self.simpleScan.setFastScan(bool(v)))
        

    def restoreDefault(self):
        dlg = wx.MessageDialog(self, _("This will reset scanner settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Scanner Settings reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            self.resetProfile()
            self.main.enableLabelTool(self.main.undoTool, False)
            self.reloadVideo()

    def reloadVideo(self):
        self.main.videoView.pause()
        if self.main.playing:
            self.main.videoView.play()

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


class ImageSegmentation(ExpandablePanel):
    """"""
    def __init__(self, parent):
        """"""
        ExpandablePanel.__init__(self, parent, _("Image Segmentation"))
        
        self.driver = Driver.Instance()
        self.pcg = PointCloudGenerator.Instance()

        self.initialize()
        
    def initialize(self):
        self.clearSections()
        section = self.createSection('image_segmentation')
        section.addItem(CheckBox, 'use_open', lambda v: self.pcg.setUseOpen(bool(v)))
        section.addItem(Slider, 'open_value', lambda v: self.pcg.setOpenValue(int(v)))
        section.addItem(CheckBox, 'use_threshold', lambda v: self.pcg.setUseThreshold(bool(v)))
        section.addItem(Slider, 'threshold_value', lambda v: self.pcg.setThresholdValue(int(v)))


class PointCloudGeneration(ExpandablePanel):
    """"""
    def __init__(self, parent):
        """"""
        ExpandablePanel.__init__(self, parent, _("Point Cloud Generation"))
        
        self.driver = Driver.Instance()
        self.pcg = PointCloudGenerator.Instance()
        self.main = self.GetParent().GetParent().GetParent().GetParent()

        self.initialize()
        
    def initialize(self):
        self.clearSections()
        section = self.createSection('point_cloud_generation')
        section.addItem(CheckBox, 'view_roi', lambda v: (self.pcg.setViewROI(bool(v)), self.main.sceneView.QueueRefresh()))
        section.addItem(Slider, 'roi_diameter', lambda v: (self.pcg.setROIDiameter(int(v)), self.main.sceneView.QueueRefresh()))
        section.addItem(Slider, 'roi_height', lambda v: (self.pcg.setROIHeight(int(v)), self.main.sceneView.QueueRefresh()))