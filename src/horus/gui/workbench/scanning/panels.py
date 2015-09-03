# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


import wx._core

from horus.gui.util.customPanels import ExpandablePanel, Slider, CheckBox, ComboBox, \
    Button, TextBox, FloatTextBox

from horus.util import profile, system as sys

from horus.engine.scan.ciclop_scan import CiclopScan
from horus.engine.scan.current_video import CurrentVideo
from horus.engine.algorithms.point_cloud_roi import PointCloudROI

ciclop_scan = CiclopScan()
current_video = CurrentVideo()
point_cloud_roi = PointCloudROI()


class ScanParameters(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(
            self, parent, _("Scan Parameters"), hasUndo=False, hasRestore=False)

        self.parent = parent

        self.clearSections()
        section = self.createSection('scan_parameters')
        section.addItem(CheckBox, 'capture_texture')
        section.addItem(ComboBox, 'use_laser')

    def updateCallbacks(self):
        section = self.sections['scan_parameters']
        section.updateCallback('capture_texture', ciclop_scan.set_capture_texture)
        section.updateCallback('use_laser', self.set_use_laser)

    def set_use_laser(self, value):
        ciclop_scan.set_use_left_laser(value == 'Left' or value == 'Both')
        ciclop_scan.set_use_right_laser(value == 'Right' or value == 'Both')


class RotatingPlatform(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Rotating platform"), hasUndo=False)

        self.clearSections()
        section = self.createSection('rotating_platform')
        section.addItem(FloatTextBox, 'motor_step_scanning')
        section.addItem(FloatTextBox, 'motor_speed_scanning')
        section.addItem(FloatTextBox, 'motor_acceleration_scanning')

    def updateCallbacks(self):
        section = self.sections['rotating_platform']
        section.updateCallback(
            'motor_step_scanning', lambda v: ciclop_scan.set_motor_step(v))
        section.updateCallback(
            'motor_speed_scanning', lambda v: ciclop_scan.set_motor_speed(v))
        section.updateCallback(
            'motor_acceleration_scanning', lambda v: ciclop_scan.set_motor_acceleration(v))


class PointCloudROI(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(self, parent, _("Point cloud ROI"))

        self.main = self.GetParent().GetParent().GetParent().GetParent()

        self.clearSections()
        section = self.createSection('point_cloud_roi')
        section.addItem(CheckBox, 'roi_view',
                        tooltip=_("View the Region Of Interest (ROI). "
                                  "This cylindrical region is the one being scanned. "
                                  "All information outside won't be taken into account "
                                  "during the scanning process"))
        section.addItem(Slider, 'roi_diameter')
        section.addItem(Slider, 'roi_width')
        section.addItem(Slider, 'roi_height')
        section.addItem(Slider, 'roi_depth')

        section.getItem('roi_diameter').control.Bind(wx.EVT_SCROLL_CHANGED, self.onRoiSliderChange)
        #section.getItem('roi_diameter').control.Bind(wx.EVT_SLIDER, self.onRoiSliderChanging)
        section.getItem('roi_height').control.Bind(wx.EVT_SCROLL_CHANGED, self.onRoiSliderChange)
        #section.getItem('roi_height').control.Bind(wx.EVT_SLIDER, self.onRoiSliderChanging)

    def updateCallbacks(self):
        section = self.sections['point_cloud_roi']
        section.updateCallback('roi_view', lambda v: (
            current_video.set_roi_view(v), self.main.sceneView.QueueRefresh()))
        section.updateCallback('roi_diameter', lambda v: (
            point_cloud_roi.set_diameter(int(v)), self.main.sceneView.QueueRefresh()))
        section.updateCallback('roi_width', lambda v: (
            point_cloud_roi.set_width(int(v)), self.main.sceneView.QueueRefresh()))
        section.updateCallback('roi_height', lambda v: (
            point_cloud_roi.set_height(int(v)), self.main.sceneView.QueueRefresh()))
        section.updateCallback('roi_depth', lambda v: (
            point_cloud_roi.set_depth(int(v)), self.main.sceneView.QueueRefresh()))

    def onRoiSliderChange(self, e):
        # Update the point cloud with the new ROI
        self.main.sceneView.updatePointCloud()

    # Overwrites ExpandablePanel method
    def updateProfile(self):
        section = self.sections['point_cloud_roi']
        section.items['roi_view'][0].updateProfile()
        section.items['roi_diameter'].updateProfile()
        section.items['roi_width'].updateProfile()
        section.items['roi_height'].updateProfile()
        section.items['roi_depth'].updateProfile()
        if profile.settings['machine_shape'] == "Rectangular":
            section.hideItem('roi_diameter')
            section.showItem('roi_width')
            section.showItem('roi_depth')
        elif profile.settings['machine_shape'] == "Circular":
            section.hideItem('roi_width')
            section.hideItem('roi_depth')
            section.showItem('roi_diameter')
        self.GetParent().GetParent().Layout()


class PointCloudColor(ExpandablePanel):

    def __init__(self, parent):
        ExpandablePanel.__init__(
            self, parent, _("Point cloud color"), hasUndo=False, hasRestore=False)
        self.clearSections()

        section = self.createSection('point_cloud_color')
        section.addItem(Button, 'point_cloud_color')

    def updateCallbacks(self):
        section = self.sections['point_cloud_color']
        section.updateCallback('point_cloud_color', self.onColorPicker)

    def onColorPicker(self):
        data = wx.ColourData()
        data.SetColour(ciclop_scan.color)
        dialog = wx.ColourDialog(self, data)
        dialog.GetColourData().SetChooseFull(True)
        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetColourData()
            color = data.GetColour().Get()
            ciclop_scan.color = color
            profile.settings['point_cloud_color'] = unicode("".join(map(chr, color)).encode('hex'))
        dialog.Destroy()
