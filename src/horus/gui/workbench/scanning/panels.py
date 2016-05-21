# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


import wx._core

from horus.util import profile
from horus.gui.engine import driver, ciclop_scan, point_cloud_roi
from horus.gui.util.custom_panels import ExpandablePanel, Slider, CheckBox, ComboBox, \
    Button, FloatTextBox


class ScanParameters(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(
            self, parent, _("Scan parameters"), has_undo=False, has_restore=False)
        self.main = self.GetParent().GetParent().GetParent()

    def add_controls(self):
        self.add_control('capture_texture', CheckBox)
        self.add_control('use_laser', ComboBox)

    def update_callbacks(self):
        self.update_callback('capture_texture', ciclop_scan.set_capture_texture)
        self.update_callback('use_laser', self.set_use_laser)

    def set_use_laser(self, value):
        ciclop_scan.set_use_left_laser(value == 'Left' or value == 'Both')
        ciclop_scan.set_use_right_laser(value == 'Right' or value == 'Both')

    def on_selected(self):
        self.main.scene_view._view_roi = False
        self.main.scene_view.queue_refresh()
        profile.settings['current_panel_scanning'] = 'scan_parameters'


class RotatingPlatform(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(
            self, parent, _("Rotating platform"), has_undo=False)
        self.main = self.GetParent().GetParent().GetParent()

    def add_controls(self):
        self.add_control(
            'show_center', CheckBox,
            _("Shows the center of the platform using the "
              "current calibration parameters"))
        self.add_control('motor_step_scanning', FloatTextBox)
        self.add_control('motor_speed_scanning', FloatTextBox)
        self.add_control('motor_acceleration_scanning', FloatTextBox)

    def update_callbacks(self):
        self.update_callback('show_center', point_cloud_roi.set_show_center)
        self.update_callback('motor_step_scanning', ciclop_scan.set_motor_step)
        self.update_callback('motor_speed_scanning', ciclop_scan.set_motor_speed)
        self.update_callback('motor_acceleration_scanning', ciclop_scan.set_motor_acceleration)

    def on_selected(self):
        self.main.scene_view._view_roi = False
        self.main.scene_view.queue_refresh()
        profile.settings['current_panel_scanning'] = 'rotating_platform'


class PointCloudROI(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(self, parent, _("Point cloud ROI"))
        self.main = self.GetParent().GetParent().GetParent()

    def add_controls(self):
        self.add_control(
            'use_roi', CheckBox,
            _("Use a Region Of Interest (ROI). "
              "This cylindrical region is the one being scanned. "
              "All information outside won't be taken into account "
              "during the scanning process"))
        self.add_control('roi_diameter', Slider)
        self.add_control('roi_height', Slider)
        # self.add_control('roi_depth', Slider)
        # self.add_control('roi_width', Slider)

    def update_callbacks(self):
        self.update_callback('use_roi', self._set_use_roi)
        self.update_callback('roi_diameter', self._set_roi_diameter)
        self.update_callback('roi_height', self._set_roi_height)

    def _set_use_roi(self, value):
        if driver.is_connected and profile.settings['current_panel_scanning'] == 'point_cloud_roi':
            point_cloud_roi.set_use_roi(value)
            if value:
                point_cloud_roi.set_diameter(profile.settings['roi_diameter'])
                point_cloud_roi.set_height(profile.settings['roi_height'])
            else:
                point_cloud_roi.set_diameter(250)
                point_cloud_roi.set_height(250)
            self.main.scene_view._view_roi = value
            self.main.scene_view.queue_refresh()

    def _set_roi_diameter(self, value):
        profile.settings['roi_diameter'] = value
        point_cloud_roi.set_diameter(profile.settings['roi_diameter'])
        self.main.scene_view.queue_refresh()

    def _set_roi_height(self, value):
        profile.settings['roi_height'] = value
        point_cloud_roi.set_height(profile.settings['roi_height'])
        self.main.scene_view.queue_refresh()

    def on_selected(self):
        if driver.is_connected:
            value = profile.settings['use_roi']
            self.main.scene_view._view_roi = value
            self.main.scene_view.queue_refresh()
        profile.settings['current_panel_scanning'] = 'point_cloud_roi'


class PointCloudColor(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(
            self, parent, _("Point cloud color"), has_undo=False, has_restore=False)
        self.main = self.GetParent().GetParent().GetParent()

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

    def on_selected(self):
        self.main.scene_view._view_roi = False
        self.main.scene_view.queue_refresh()
        profile.settings['current_panel_scanning'] = 'point_cloud_color'
