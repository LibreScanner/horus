# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.util import profile

from horus.gui.engine import driver, pattern, calibration_data, image_capture
from horus.gui.util.video_view import VideoView
from horus.gui.workbench.workbench import Workbench
from horus.gui.workbench.adjustment.current_video import CurrentVideo
from horus.gui.workbench.adjustment.panels import ScanCapturePanel, ScanSegmentationPanel, \
    CalibrationCapturePanel, CalibrationSegmentationPanel


class AdjustmentWorkbench(Workbench):

    def __init__(self, parent):
        Workbench.__init__(self, parent, name=_('Adjustment workbench'))

        self.current_video = CurrentVideo()

    def add_panels(self):
        self.add_panel('scan_capture', ScanCapturePanel)
        self.add_panel('scan_segmentation', ScanSegmentationPanel)
        self.add_panel('calibration_capture', CalibrationCapturePanel)
        self.add_panel('calibration_segmentation', CalibrationSegmentationPanel)

    def add_pages(self):
        self.add_page('video_view', VideoView(self, self._video_frame, wxtimer=False))
        self.panels_collection.expandable_panels[
            profile.settings['current_panel_adjustment']].on_title_clicked(None)

    def _video_frame(self):
        return self.current_video.get_frame()

    def on_open(self):
        current_video_mode = profile.settings['current_video_mode_adjustment']
        self.pages_collection['video_view'].play(
            flush=not (current_video_mode == 'Laser' or current_video_mode == 'Gray'))

    def on_close(self):
        try:
            self.pages_collection['video_view'].stop()
        except:
            pass

    def reset(self):
        self.pages_collection['video_view'].reset()

    def setup_engine(self):
        driver.camera.set_frame_rate(int(profile.settings['frame_rate']))
        driver.camera.set_resolution(
            profile.settings['camera_width'], profile.settings['camera_height'])
        driver.camera.set_rotate(profile.settings['camera_rotate'])
        driver.camera.set_hflip(profile.settings['camera_hflip'])
        driver.camera.set_vflip(profile.settings['camera_vflip'])
        driver.camera.set_luminosity(profile.settings['luminosity'])
        self.current_video.mode = profile.settings['current_video_mode_adjustment']
        pattern.rows = profile.settings['pattern_rows']
        pattern.columns = profile.settings['pattern_columns']
        pattern.square_width = profile.settings['pattern_square_width']
        pattern.distance = profile.settings['pattern_origin_distance']
        image_capture.set_use_distortion(profile.settings['use_distortion'])
        width, height = driver.camera.get_resolution()
        calibration_data.set_resolution(width, height)
        calibration_data.camera_matrix = profile.settings['camera_matrix']
        calibration_data.distortion_vector = profile.settings['distortion_vector']
        self.panels_collection.expandable_panels[
            profile.settings['current_panel_adjustment']].on_title_clicked(None)
