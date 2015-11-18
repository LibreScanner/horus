# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


import wx._core

from horus.util import profile
from horus.gui.engine import ciclop_scan, current_video
from horus.gui.util.custom_panels import ExpandablePanel, Slider, CheckBox, ComboBox, \
    Button, FloatTextBox


class ScanParameters(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(
            self, parent, _("Scan Parameters"), has_undo=False, has_restore=False)

    def add_controls(self):
        self.add_control('capture_texture', CheckBox)
        self.add_control('use_laser', ComboBox)

    def update_callbacks(self):
        self.update_callback('capture_texture', ciclop_scan.set_capture_texture)
        self.update_callback('use_laser', self.set_use_laser)

    def set_use_laser(self, value):
        ciclop_scan.set_use_left_laser(value == 'Left' or value == 'Both')
        ciclop_scan.set_use_right_laser(value == 'Right' or value == 'Both')


class RotatingPlatform(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(
            self, parent, _("Rotating platform"), has_undo=False)

    def add_controls(self):
        self.add_control('motor_step_scanning', FloatTextBox)
        self.add_control('motor_speed_scanning', FloatTextBox)
        self.add_control('motor_acceleration_scanning', FloatTextBox)

    def update_callbacks(self):
        self.update_callback('motor_step_scanning', ciclop_scan.set_motor_step)
        self.update_callback('motor_speed_scanning', ciclop_scan.set_motor_speed)
        self.update_callback('motor_acceleration_scanning', ciclop_scan.set_motor_acceleration)


class PointCloudROI(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(self, parent, _("Point cloud ROI"))

        self.main = self.GetParent().GetParent().GetParent().GetParent()

    def add_controls(self):
        self.add_control(
            'roi_view', CheckBox,
            _("View the Region Of Interest (ROI). "
              "This cylindrical region is the one being scanned. "
              "All information outside won't be taken into account "
              "during the scanning process"))
        self.add_control('roi_diameter', Slider)
        self.add_control('roi_width', Slider)
        self.add_control('roi_height', Slider)
        self.add_control('roi_depth', Slider)

        # section.getItem('roi_diameter').control.Bind(wx.EVT_SCROLL_CHANGED, self.onRoiSliderChange)
        # section.getItem('roi_diameter').control.Bind(wx.EVT_SLIDER, self.onRoiSliderChanging)
        # section.getItem('roi_height').control.Bind(wx.EVT_SCROLL_CHANGED, self.onRoiSliderChange)
        # section.getItem('roi_height').control.Bind(wx.EVT_SLIDER, self.onRoiSliderChanging)

    def update_callbacks(self):
        self.update_callback('roi_view', lambda v: (
            current_video.set_roi_view(v), self.main.scene_view.queue_refresh()))
        self.update_callback('roi_diameter', lambda v: (
            current_video.set_roi_view(v), self.main.scene_view.queue_refresh()))
        self.update_callback('roi_width', lambda v: (
            current_video.set_roi_view(v), self.main.scene_view.queue_refresh()))
        self.update_callback('roi_height', lambda v: (
            current_video.set_roi_view(v), self.main.scene_view.queue_refresh()))
        self.update_callback('roi_depth', lambda v: (
            current_video.set_roi_view(v), self.main.scene_view.queue_refresh()))

    # def onRoiSliderChange(self, e):
        # Update the point cloud with the new ROI
        # self.main.sceneView.updatePointCloud()

    # Overwrites ExpandablePanel method
    """def updateProfile(self):
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
        self.GetParent().GetParent().Layout()"""


class PointCloudColor(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(
            self, parent, _("Point cloud color"), has_undo=False, has_restore=False)

    def add_controls(self):
        self.add_control('point_cloud_color', Button)

    def update_callbacks(self):
        self.update_callback('point_cloud_color', self.on_color_picker)

    def on_color_picker(self):
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
