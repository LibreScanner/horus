# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.util import profile

from horus.gui.engine import driver, image_capture, image_detection
from horus.gui.workbench.workbench import Workbench
from horus.gui.workbench.calibration.panels import PatternSettings, AutocheckPanel, \
    CameraIntrinsicsPanel, LaserTriangulationPanel, PlatformExtrinsicsPanel

# from horus.gui.workbench.calibration.pages import AutocheckMainPage, CameraIntrinsicsMainPage, \
#    CameraIntrinsicsResultPage, LaserTriangulationMainPage, LaserTriangulationResultPage, \
#    PlatformExtrinsicsMainPage, PlatformExtrinsicsResultPage

from horus.gui.util.patternDistanceWindow import PatternDistanceWindow


class CalibrationWorkbench(Workbench):

    def __init__(self, parent):
        Workbench.__init__(self, parent, name=_('Calibration workbench'))

    def add_panels(self):
        self.add_panel('pattern_settings', PatternSettings)
        # self.controls.addPanel('camera_intrinsics_panel', CameraIntrinsicsPanel(
        #     self.controls, buttonStartCallback=self.onCameraIntrinsicsStartCallback))
        # self.controls.addPanel('autocheck_panel', AutocheckPanel(
        #     self.controls, buttonStartCallback=self.onAutocheckStartCallback,
        #     buttonStopCallback=self.onCancelCallback))
        # self.controls.addPanel('laser_triangulation_panel', LaserTriangulationPanel(
        #     self.controls, buttonStartCallback=self.onLaserTriangulationStartCallback))
        # self.controls.addPanel('platform_extrinsics_panel', PlatformExtrinsicsPanel(
        #     self.controls, buttonStartCallback=self.onPlatformExtrinsicsStartCallback))

    def setup_engine(self):
        pass

    def video_frame(self):
        image = image_capture.capture_pattern()
        return image_detection.detect_pattern(image)
