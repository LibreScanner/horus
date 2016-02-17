# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.gui.engine import pattern, image_capture
from horus.gui.util.custom_panels import ExpandablePanel, Slider, CheckBox, \
    FloatTextBox, FloatTextBoxArray


class PatternSettings(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(self, parent, _("Pattern settings"),
                                 selected_callback=on_selected_callback)

    def add_controls(self):
        self.add_control('pattern_rows', Slider, 'Number of corner rows in the pattern')
        self.add_control('pattern_columns', Slider, 'Number of corner columns in the pattern')
        self.add_control('pattern_square_width', FloatTextBox)
        self.add_control('pattern_origin_distance', FloatTextBox,
                         "Minimum distance between the origin of the pattern (bottom-left corner) "
                         "and the pattern's base surface")

    def update_callbacks(self):
        self.update_callback('pattern_rows', lambda v: self._update_rows(v))
        self.update_callback('pattern_columns', lambda v: self._update_columns(v))
        self.update_callback('pattern_square_width', lambda v: self._update_square_width(v))
        self.update_callback('pattern_origin_distance', lambda v: self._update_origin_distance(v))

    def _update_rows(self, value):
        pattern.rows = value

    def _update_columns(self, value):
        pattern.columns = value

    def _update_square_width(self, value):
        pattern.square_width = value

    def _update_origin_distance(self, value):
        pattern.origin_distance = value


class CameraIntrinsics(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(self, parent, _("Camera intrinsics"),
                                 selected_callback=on_selected_callback, has_undo=False)

    def add_controls(self):
        self.add_control('camera_matrix', FloatTextBoxArray)
        self.add_control('distortion_vector', FloatTextBoxArray)
        # TODO:
        # self.add_control(
        #     'use_distortion', CheckBox,
        #     _("This option applies lens distortion correction to the video. "
        #       "This process slows the video feed from the camera"))

    def update_callbacks(self):
        pass
        # self.update_callback('use_distortion', lambda v: image_capture.set_use_distortion(v))


class ScannerAutocheck(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(self, parent, _("Scanner autocheck"),
                                 selected_callback=on_selected_callback,
                                 has_undo=False, has_restore=False)


class LaserTriangulation(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(self, parent, _("Laser triangulation"),
                                 selected_callback=on_selected_callback, has_undo=False)

    def add_controls(self):
        self.add_control('distance_left', FloatTextBox)
        self.add_control('normal_left', FloatTextBoxArray)
        self.add_control('distance_right', FloatTextBox)
        self.add_control('normal_right', FloatTextBoxArray)

        self.content.control_panels['distance_left'].control.SetEditable(False)
        self.content.control_panels['distance_right'].control.SetEditable(False)


class PlatformExtrinsics(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(self, parent, _("Platform extrinsics"),
                                 selected_callback=on_selected_callback, has_undo=False)

    def add_controls(self):
        self.add_control('rotation_matrix', FloatTextBoxArray)
        self.add_control('translation_vector', FloatTextBoxArray)
