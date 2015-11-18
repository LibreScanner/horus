# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import resources, profile

from horus.gui.engine import ciclop_scan, current_video, image_capture, point_cloud_roi
from horus.gui.workbench.workbench import Workbench
from horus.gui.workbench.scanning.view_page import ViewPage
from horus.gui.workbench.scanning.panels import ScanParameters, RotatingPlatform, \
    PointCloudROI, PointCloudColor


class ScanningWorkbench(Workbench):

    def __init__(self, parent):
        Workbench.__init__(self, parent, name=_('Scanning workbench'))

        self.scanning = False
        self.show_video_views = False

        self.pointCloudTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onPointCloudTimer, self.pointCloudTimer)

    def add_toolbar(self):
        # Toolbar Configuration
        self.playTool = self.toolbar.AddLabelTool(
            wx.NewId(), _("Play"),
            wx.Bitmap(resources.get_path_for_image("play.png")), shortHelp=_("Play"))
        self.stopTool = self.toolbar.AddLabelTool(
            wx.NewId(), _("Stop"),
            wx.Bitmap(resources.get_path_for_image("stop.png")), shortHelp=_("Stop"))
        self.pauseTool = self.toolbar.AddLabelTool(
            wx.NewId(), _("Pause"),
            wx.Bitmap(resources.get_path_for_image("pause.png")), shortHelp=_("Pause"))
        self.toolbar.Realize()

        # Disable Toolbar Items
        self.enableLabelTool(self.playTool, False)
        self.enableLabelTool(self.stopTool, False)
        self.enableLabelTool(self.pauseTool, False)

        # Bind Toolbar Items
        self.Bind(wx.EVT_TOOL, self.onPlayToolClicked, self.playTool)
        self.Bind(wx.EVT_TOOL, self.onStopToolClicked, self.stopTool)
        self.Bind(wx.EVT_TOOL, self.onPauseToolClicked, self.pauseTool)

    def add_panels(self):
        self.add_panel('scan_parameters', ScanParameters)
        self.add_panel('rotating_platform', RotatingPlatform)
        self.add_panel('point_cloud_roi', PointCloudROI)
        self.add_panel('point_cloud_color', PointCloudColor)

    def add_pages(self):
        self.add_page('view_page', ViewPage(self, self.get_image))

    def on_open(self):
        pass
        # self.pages_collection['video_view'].play()

    def on_close(self):
        try:
            pass
            # self.pages_collection['video_view'].stop()
        except:
            pass

    def setup_engine(self):
        resolution = profile.settings['resolution'].split('x')
        driver.camera.set_frame_rate(int(profile.settings['framerate']))
        driver.camera.set_resolution(int(resolution[1]), int(resolution[0]))
        image_capture.set_mode_texture()
        image_capture.texture_mode.set_brightness(profile.settings['brightness_control'])
        image_capture.texture_mode.set_contrast(profile.settings['contrast_control'])
        image_capture.texture_mode.set_saturation(profile.settings['saturation_control'])
        image_capture.texture_mode.set_exposure(profile.settings['exposure_control'])
        image_capture.set_use_distortion(profile.settings['use_distortion'])
        driver.board.motor_relative(profile.settings['motor_step_control'])
        driver.board.motor_speed(profile.settings['motor_speed_control'])
        driver.board.motor_acceleration(profile.settings['motor_acceleration_control'])

    def enable_restore(self, value):
        self.controls.enable_restore(value)

    def onShow(self, event):
        if event.GetShow():
            self.updateStatus(self.driver.is_connected)
            self.pointCloudTimer.Stop()
        else:
            try:
                self.pointCloudTimer.Stop()
                self.videoView.stop()
            except:
                pass

    def get_image(self):
        if self.scanning:
            image_capture.stream = False
            return current_video.capture()
        else:
            image_capture.stream = True
            image = image_capture.capture_texture()
            if profile.settings['video_scanning']:
                image = point_cloud_roi.draw_roi(image)
            return image

    def onPointCloudTimer(self, event):
        p, r = ciclop_scan.get_progress()
        self.gauge.SetRange(r)
        self.gauge.SetValue(p)
        pointCloud = ciclop_scan.get_point_cloud_increment()
        if pointCloud is not None:
            if pointCloud[0] is not None and pointCloud[1] is not None:
                if len(pointCloud[0]) > 0:
                    pointCloud = point_cloud_roi.mask_point_cloud(*pointCloud)
                    self.sceneView.appendPointCloud(pointCloud[0], pointCloud[1])

    def onPlayToolClicked(self, event):
        if ciclop_scan._inactive:
            # Resume
            self.enableLabelTool(self.pauseTool, True)
            self.enableLabelTool(self.playTool, False)
            ciclop_scan.resume()
            self.pointCloudTimer.Start(milliseconds=50)
        else:
            result = True
            if self.sceneView._object is not None:
                dlg = wx.MessageDialog(self,
                                       _("Your current model will be erased.\n"
                                         "Do you really want to do it?"),
                                       _("Clear Point Cloud"), wx.YES_NO | wx.ICON_QUESTION)
                result = dlg.ShowModal() == wx.ID_YES
                dlg.Destroy()
            if result:
                self.gauge.SetValue(0)
                self.gauge.Show()
                self.scenePanel.Layout()
                self.Layout()
                ciclop_scan.set_callbacks(self.beforeScan,
                                          None, lambda r: wx.CallAfter(self.afterScan, r))
                ciclop_scan.start()

    def beforeScan(self):
        self.scanning = True
        self.buttonShowVideoViews.Show()
        self.enableLabelTool(self.disconnectTool, False)
        self.enableLabelTool(self.playTool, False)
        self.enableLabelTool(self.stopTool, True)
        self.enableLabelTool(self.pauseTool, True)
        self.sceneView.createDefaultObject()
        self.sceneView.setShowDeleteMenu(False)
        self.videoView.setMilliseconds(200)
        self.combo.Disable()
        self.GetParent().menuFile.Enable(self.GetParent().menuLaunchWizard.GetId(), False)
        self.GetParent().menuFile.Enable(self.GetParent().menuLoadModel.GetId(), False)
        self.GetParent().menuFile.Enable(self.GetParent().menuSaveModel.GetId(), False)
        self.GetParent().menuFile.Enable(self.GetParent().menuClearModel.GetId(), False)
        self.GetParent().menuFile.Enable(self.GetParent().menuOpenCalibrationProfile.GetId(), False)
        self.GetParent().menuFile.Enable(self.GetParent().menuSaveCalibrationProfile.GetId(), False)
        self.GetParent().menuFile.Enable(self.GetParent().menuResetCalibrationProfile.GetId(), False)
        self.GetParent().menuFile.Enable(self.GetParent().menuOpenScanProfile.GetId(), False)
        self.GetParent().menuFile.Enable(self.GetParent().menuSaveScanProfile.GetId(), False)
        self.GetParent().menuFile.Enable(self.GetParent().menuResetScanProfile.GetId(), False)
        self.GetParent().menuFile.Enable(self.GetParent().menuExit.GetId(), False)
        self.GetParent().menuEdit.Enable(self.GetParent().menuPreferences.GetId(), False)
        self.GetParent().menuHelp.Enable(self.GetParent().menuWelcome.GetId(), False)
        panel = self.controls.panels['rotating_platform']
        section = panel.sections['rotating_platform']
        section.disable('motor_speed_scanning')
        section.disable('motor_acceleration_scanning')
        self.enable_restore(False)
        self.pointCloudTimer.Start(milliseconds=50)

    def afterScan(self, response):
        ret, result = response
        if ret:
            dlg = wx.MessageDialog(self,
                                   _("Scanning has finished. If you want to save your "
                                     "point cloud go to File > Save Model"),
                                   _("Scanning finished!"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.scanning = False
            self.onScanFinished()

    def onStopToolClicked(self, event):
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
            self.onScanFinished()
        else:
            if not paused:
                ciclop_scan.resume()

    def onScanFinished(self):
        self.buttonShowVideoViews.Hide()
        self.comboVideoViews.Hide()
        self.enableLabelTool(self.disconnectTool, True)
        self.enableLabelTool(self.playTool, True)
        self.enableLabelTool(self.stopTool, False)
        self.enableLabelTool(self.pauseTool, False)
        self.sceneView.setShowDeleteMenu(True)
        self.combo.Enable()
        self.GetParent().menuFile.Enable(self.GetParent().menuLaunchWizard.GetId(), True)
        self.GetParent().menuFile.Enable(self.GetParent().menuLoadModel.GetId(), True)
        self.GetParent().menuFile.Enable(self.GetParent().menuSaveModel.GetId(), True)
        self.GetParent().menuFile.Enable(self.GetParent().menuClearModel.GetId(), True)
        self.GetParent().menuFile.Enable(self.GetParent().menuOpenCalibrationProfile.GetId(), True)
        self.GetParent().menuFile.Enable(self.GetParent().menuSaveCalibrationProfile.GetId(), True)
        self.GetParent().menuFile.Enable(self.GetParent().menuResetCalibrationProfile.GetId(), True)
        self.GetParent().menuFile.Enable(self.GetParent().menuOpenScanProfile.GetId(), True)
        self.GetParent().menuFile.Enable(self.GetParent().menuSaveScanProfile.GetId(), True)
        self.GetParent().menuFile.Enable(self.GetParent().menuResetScanProfile.GetId(), True)
        self.GetParent().menuFile.Enable(self.GetParent().menuExit.GetId(), True)
        self.GetParent().menuEdit.Enable(self.GetParent().menuPreferences.GetId(), True)
        self.GetParent().menuHelp.Enable(self.GetParent().menuWelcome.GetId(), True)
        panel = self.controls.panels['rotating_platform']
        section = panel.sections['rotating_platform']
        section.enable('motor_speed_scanning')
        section.enable('motor_acceleration_scanning')
        self.enable_restore(True)
        self.pointCloudTimer.Stop()
        self.videoView.setMilliseconds(10)
        self.gauge.SetValue(0)
        self.gauge.Hide()
        self.scenePanel.Layout()
        self.Layout()

    def onPauseToolClicked(self, event):
        self.enableLabelTool(self.pauseTool, False)
        self.enableLabelTool(self.playTool, True)
        ciclop_scan.pause()
        self.pointCloudTimer.Stop()

    def updateToolbarStatus(self, status):
        if status:
            if self.IsShown():
                self.videoView.play()
            self.enableLabelTool(self.playTool, True)
            self.enableLabelTool(self.stopTool, False)
            self.enableLabelTool(self.pauseTool, False)
            self.controls.enableContent()
        else:
            self.videoView.stop()
            self.enableLabelTool(self.playTool, False)
            self.enableLabelTool(self.stopTool, False)
            self.enableLabelTool(self.pauseTool, False)
            self.controls.disableContent()

    def updateProfileToAllControls(self):
        self.controls.updateProfile()
