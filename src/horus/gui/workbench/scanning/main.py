# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import struct
import wx._core

from horus.util import resources, profile

from horus.gui.engine import driver, image_capture, laser_segmentation, calibration_data, \
    ciclop_scan, current_video, point_cloud_roi
from horus.gui.workbench.workbench import Workbench
from horus.gui.workbench.scanning.view_page import ViewPage
from horus.gui.workbench.scanning.panels import ScanParameters, RotatingPlatform, \
    PointCloudROI, PointCloudColor


class ScanningWorkbench(Workbench):

    def __init__(self, parent, toolbar_scan):
        Workbench.__init__(self, parent, name=_('Scanning workbench'))

        self.scanning = False
        self.show_video_views = False
        self.toolbar_scan = toolbar_scan

        # Elements
        self.point_cloud_timer = wx.Timer(self)
        self.play_tool = self.toolbar_scan.AddLabelTool(
            wx.NewId(), _("Play"),
            wx.Bitmap(resources.get_path_for_image("play.png")), shortHelp=_("Play"))
        self.stop_tool = self.toolbar_scan.AddLabelTool(
            wx.NewId(), _("Stop"),
            wx.Bitmap(resources.get_path_for_image("stop.png")), shortHelp=_("Stop"))
        self.pause_tool = self.toolbar_scan.AddLabelTool(
            wx.NewId(), _("Pause"),
            wx.Bitmap(resources.get_path_for_image("pause.png")), shortHelp=_("Pause"))
        self.toolbar_scan.Realize()

        self._enable_tool_scan(self.play_tool, False)
        self._enable_tool_scan(self.stop_tool, False)
        self._enable_tool_scan(self.pause_tool, False)

        # Events
        self.toolbar_scan.GetParent().Bind(wx.EVT_TOOL, self.on_play_tool_clicked, self.play_tool)
        self.toolbar_scan.GetParent().Bind(wx.EVT_TOOL, self.on_stop_tool_clicked, self.stop_tool)
        self.toolbar_scan.GetParent().Bind(wx.EVT_TOOL, self.on_pause_tool_clicked, self.pause_tool)
        self.Bind(wx.EVT_TIMER, self.on_point_cloud_timer, self.point_cloud_timer)

    def add_panels(self):
        self.add_panel('scan_parameters', ScanParameters)
        self.add_panel('rotating_platform', RotatingPlatform)
        self.add_panel('point_cloud_roi', PointCloudROI)
        self.add_panel('point_cloud_color', PointCloudColor)

    def add_pages(self):
        self.add_page('view_page', ViewPage(self, self.get_image))
        self.video_view = self.pages_collection['view_page'].video_view
        self.scene_panel = self.pages_collection['view_page'].scene_panel
        self.scene_view = self.pages_collection['view_page'].scene_view
        self.gauge = self.pages_collection['view_page'].gauge
        self.panels_collection.expandable_panels[
            profile.settings['current_panel_scanning']].on_title_clicked(None)

    def on_open(self):
        self.video_view.play()
        self.point_cloud_timer.Stop()

    def on_close(self):
        try:
            self.video_view.stop()
            self.point_cloud_timer.Stop()
            self._enable_tool_scan(self.play_tool, False)
            self._enable_tool_scan(self.stop_tool, False)
            self._enable_tool_scan(self.pause_tool, False)
        except:
            pass

    def setup_engine(self):
        self._enable_tool_scan(self.play_tool, True)
        self._enable_tool_scan(self.stop_tool, False)
        self._enable_tool_scan(self.pause_tool, False)

        resolution = profile.settings['resolution'].split('x')
        driver.camera.set_frame_rate(int(profile.settings['framerate']))
        driver.camera.set_resolution(int(resolution[1]), int(resolution[0]))
        image_capture.set_mode_texture()
        image_capture.texture_mode.set_brightness(profile.settings['brightness_texture_scanning'])
        image_capture.texture_mode.set_contrast(profile.settings['contrast_texture_scanning'])
        image_capture.texture_mode.set_saturation(profile.settings['saturation_texture_scanning'])
        image_capture.texture_mode.set_exposure(profile.settings['exposure_texture_scanning'])
        image_capture.laser_mode.brightness = profile.settings['brightness_laser_scanning']
        image_capture.laser_mode.contrast = profile.settings['contrast_laser_scanning']
        image_capture.laser_mode.saturation = profile.settings['saturation_laser_scanning']
        image_capture.laser_mode.exposure = profile.settings['exposure_laser_scanning']
        image_capture.set_use_distortion(profile.settings['use_distortion'])
        laser_segmentation.red_channel = profile.settings['red_channel_scanning']
        laser_segmentation.open_enable = profile.settings['open_enable_scanning']
        laser_segmentation.open_value = profile.settings['open_value_scanning']
        laser_segmentation.threshold_enable = profile.settings['threshold_enable_scanning']
        laser_segmentation.threshold_value = profile.settings['threshold_value_scanning']
        calibration_data.set_resolution(int(resolution[1]), int(resolution[0]))
        calibration_data.camera_matrix = profile.settings['camera_matrix']
        calibration_data.distortion_vector = profile.settings['distortion_vector']
        calibration_data.laser_planes[0].distance = profile.settings['distance_left']
        calibration_data.laser_planes[0].normal = profile.settings['normal_left']
        calibration_data.laser_planes[1].distance = profile.settings['distance_right']
        calibration_data.laser_planes[1].normal = profile.settings['normal_right']
        calibration_data.platform_rotation = profile.settings['rotation_matrix']
        calibration_data.platform_translation = profile.settings['translation_vector']
        ciclop_scan.capture_texture = profile.settings['capture_texture']
        use_laser = profile.settings['use_laser']
        ciclop_scan.set_use_left_laser(use_laser == 'Left' or use_laser == 'Both')
        ciclop_scan.set_use_right_laser(use_laser == 'Right' or use_laser == 'Both')
        ciclop_scan.motor_step = profile.settings['motor_step_scanning']
        ciclop_scan.motor_speed = profile.settings['motor_speed_scanning']
        ciclop_scan.motor_acceleration = profile.settings['motor_acceleration_scanning']
        ciclop_scan.color = struct.unpack(
            'BBB', profile.settings['point_cloud_color'].decode('hex'))
        point_cloud_roi.set_diameter(profile.settings['roi_diameter'])
        point_cloud_roi.set_height(profile.settings['roi_height'])

    def get_image(self):
        if self.scanning:
            image_capture.stream = False
            return current_video.capture()
        else:
            image_capture.stream = True
            image = image_capture.capture_texture()
            if self.scene_view._view_roi:
                if profile.settings['use_roi']:
                    image = point_cloud_roi.mask_image(image)
                image = point_cloud_roi.draw_roi(image)
            return image

    def on_point_cloud_timer(self, event):
        p, r = ciclop_scan.get_progress()
        self.gauge.SetRange(r)
        self.gauge.SetValue(p)
        point_cloud = ciclop_scan.get_point_cloud_increment()
        if point_cloud is not None:
            if point_cloud[0] is not None and point_cloud[1] is not None:
                if len(point_cloud[0]) > 0:
                    point_cloud = point_cloud_roi.mask_point_cloud(*point_cloud)
                    self.scene_view.append_point_cloud(
                        point_cloud[0], point_cloud[1])

    def on_play_tool_clicked(self, event):
        if ciclop_scan._inactive:
            self._enable_tool_scan(self.play_tool, False)
            self._enable_tool_scan(self.pause_tool, True)
            ciclop_scan.resume()
            self.point_cloud_timer.Start(milliseconds=50)
        else:
            if calibration_data.check_calibration():
                result = True
                if self.scene_view._object is not None:
                    dlg = wx.MessageDialog(self,
                                           _("Your current model will be erased.\n"
                                             "Do you really want to do it?"),
                                           _("Clear Point Cloud"), wx.YES_NO | wx.ICON_QUESTION)
                    result = dlg.ShowModal() == wx.ID_YES
                    dlg.Destroy()
                if result:
                    self.gauge.SetValue(0)
                    self.gauge.Show()
                    self.Layout()
                    ciclop_scan.set_callbacks(self.before_scan,
                                              None, lambda r: wx.CallAfter(self.after_scan, r))
                    ciclop_scan.start()
            else:
                dlg = wx.MessageDialog(self,
                                       _("Calibration hasn't been performed correctly.\n"
                                         "Please repeat calibration process again:\n"
                                         "  1. Scanner autocheck\n"
                                         "  2. Laser triangulation\n"
                                         "  3. Platform extrinsics"),
                                       _("Wrong calibration"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

    def before_scan(self):
        self.scanning = True
        self._enable_tool_scan(self.play_tool, False)
        self._enable_tool_scan(self.stop_tool, True)
        self._enable_tool_scan(self.pause_tool, True)
        self.GetParent().enable_gui(False)
        self.scroll_panel.Hide()
        self.scroll_panel.GetParent().Layout()
        self.scroll_panel.Layout()
        self.GetParent().Layout()
        # self.buttonShowVideoViews.Show()
        self.scene_view.create_default_object()
        self.scene_view.set_show_delete_menu(False)
        self.video_view.set_milliseconds(200)
        self.point_cloud_timer.Start(milliseconds=50)

    def after_scan(self, response):
        ret, result = response
        if ret:
            dlg = wx.MessageDialog(self,
                                   _("Scanning has finished. If you want to save your "
                                     "point cloud go to File > Save Model"),
                                   _("Scanning finished!"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.scanning = False
            self.on_scan_finished()

    def on_stop_tool_clicked(self, event):
        paused = ciclop_scan._inactive
        ciclop_scan.pause()
        dlg = wx.MessageDialog(self,
                               _("Your current scanning will be stopped.\n"
                                 "Do you really want to do it?"),
                               _("Stop Scanning"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()

        if result:
            self.scanning = False
            ciclop_scan.stop()
            self.on_scan_finished()
        else:
            if not paused:
                ciclop_scan.resume()

    def on_scan_finished(self):
        self._enable_tool_scan(self.play_tool, True)
        self._enable_tool_scan(self.stop_tool, False)
        self._enable_tool_scan(self.pause_tool, False)
        self.GetParent().enable_gui(True)
        self.GetParent().on_scanning_panel_clicked(None)
        # self.comboVideoViews.Hide()
        self.scene_view.set_show_delete_menu(True)
        self.video_view.set_milliseconds(10)
        self.point_cloud_timer.Stop()
        self.gauge.SetValue(0)
        self.gauge.Hide()
        self.Layout()

    def on_pause_tool_clicked(self, event):
        self._enable_tool_scan(self.play_tool, True)
        self._enable_tool_scan(self.pause_tool, False)
        ciclop_scan.pause()
        self.point_cloud_timer.Stop()

    def _enable_tool_scan(self, item, enable):
        self.toolbar_scan.EnableTool(item.GetId(), enable)
