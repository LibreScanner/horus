# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from horus.gui.engine import pattern
from horus.gui.util.custom_panels import ExpandablePanel, Slider, FloatTextBox, FloatTextBoxArray


class PatternSettings(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(self, parent, _("Pattern settings"),
                                 selected_callback=on_selected_callback, has_undo=False)
        self.on_selected_callback = on_selected_callback

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

    def update_callbacks(self):
        self.update_callback('camera_matrix', lambda v: self._update_camera_matrix(v))
        self.update_callback('distortion_vector', lambda v: self._update_distortion_vector(v))

    def _update_camera_matrix(self, value):
        pass

    def _update_distortion_vector(self, value):
        pass


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

    def update_callbacks(self):
        self.update_callback('distance_left', lambda v: self._update_distance_left(v))
        self.update_callback('normal_left', lambda v: self._update_normal_left(v))
        self.update_callback('distance_right', lambda v: self._update_distance_right(v))
        self.update_callback('normal_right', lambda v: self._update_normal_right(v))

    def _update_distance_left(self, value):
        pass

    def _update_normal_left(self, value):
        pass

    def _update_distance_right(self, value):
        pass

    def _update_normal_right(self, value):
        pass


class PlatformExtrinsics(ExpandablePanel):

    def __init__(self, parent, on_selected_callback):
        ExpandablePanel.__init__(self, parent, _("Platform extrinsics"),
                                 selected_callback=on_selected_callback, has_undo=False)

    def add_controls(self):
        self.add_control('rotation_matrix', FloatTextBoxArray)
        self.add_control('translation_vector', FloatTextBoxArray)

    def update_callbacks(self):
        self.update_callback('rotation_matrix', lambda v: self._update_rotation_matrix(v))
        self.update_callback('translation_vector', lambda v: self._update_translation_vector(v))

    def _update_rotation_matrix(self, value):
        pass

    def _update_translation_vector(self, value):
        pass
