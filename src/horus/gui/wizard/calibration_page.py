# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import profile, resources

from horus.engine.calibration.combo_calibration import ComboCalibrationError
from horus.gui.engine import driver, calibration_data, image_capture, \
    image_detection, combo_calibration
from horus.gui.util.image_view import ImageView
from horus.gui.util.pattern_distance_window import PatternDistanceWindow
from horus.gui.wizard.wizard_page import WizardPage


class CalibrationPage(WizardPage):

    def __init__(self, parent, button_prev_callback=None, button_next_callback=None):
        WizardPage.__init__(self, parent,
                            title=_("Calibration"),
                            button_prev_callback=button_prev_callback,
                            button_next_callback=button_next_callback)

        self.parent = parent

        self.pattern_label = wx.StaticText(self.panel, label=_(
            "Put the pattern on the platform as shown in the picture and press \"Calibrate\""))
        self.pattern_label.Wrap(400)
        self.image_view = ImageView(self.panel, quality=wx.IMAGE_QUALITY_HIGH)
        self.image_view.set_image(wx.Image(resources.get_path_for_image("pattern-position.png")))
        self.calibrate_button = wx.Button(self.panel, label=_("Calibrate"))
        self.cancel_button = wx.Button(self.panel, label=_("Cancel"))
        self.gauge = wx.Gauge(self.panel, range=100, size=(-1, 30))
        self.result_label = wx.StaticText(self.panel, size=(-1, 30))

        self.cancel_button.Disable()
        self.result_label.Hide()
        self.skip_button.Enable()
        self.next_button.Disable()

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.pattern_label, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(self.image_view, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(self.result_label, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(self.gauge, 0, wx.ALL | wx.EXPAND, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.cancel_button, 1, wx.ALL | wx.EXPAND, 5)
        hbox.Add(self.calibrate_button, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 2)
        self.panel.SetSizer(vbox)

        self.Layout()

        self.calibrate_button.Bind(wx.EVT_BUTTON, self.on_calibration_button_clicked)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel_button_clicked)
        self.Bind(wx.EVT_SHOW, self.on_show)

        self.video_view.set_callback(self.get_image)

    def on_show(self, event):
        if event.GetShow():
            driver.board.lasers_off()
            self.update_status(driver.is_connected)
        else:
            try:
                self.video_view.stop()
            except:
                pass

    def get_image(self):
        if combo_calibration.image is not None:
            image = combo_calibration.image
        else:
            image = image_capture.capture_pattern()
            image = image_detection.detect_pattern(image)
        return image

    def on_unplugged(self):
        self.video_view.stop()
        combo_calibration.cancel()
        self.enable_next = True
        driver.disconnect()
        self.parent.on_exit(message=False)

    def on_calibration_button_clicked(self, event):
        combo_calibration.set_callbacks(
            lambda: wx.CallAfter(self.before_calibration),
            lambda p: wx.CallAfter(self.progress_calibration, p),
            lambda r: wx.CallAfter(self.after_calibration, r))
        if profile.settings['pattern_origin_distance'] == 0.0:
            PatternDistanceWindow(self)
        else:
            combo_calibration.start()

    def on_cancel_button_clicked(self, event):
        board_unplug_callback = driver.board.unplug_callback
        camera_unplug_callback = driver.camera.unplug_callback
        driver.board.set_unplug_callback(None)
        driver.camera.set_unplug_callback(None)
        self.result_label.SetLabel(_("Calibration canceled. To try again press \"Calibrate\""))
        combo_calibration.cancel()
        self.skip_button.Enable()
        self.on_finish_calibration()
        driver.board.set_unplug_callback(board_unplug_callback)
        driver.camera.set_unplug_callback(camera_unplug_callback)

    def before_calibration(self):
        self.breadcrumbs.Disable()
        self.calibrate_button.Disable()
        self.cancel_button.Enable()
        self.prev_button.Disable()
        self.skip_button.Disable()
        self.next_button.Disable()
        self.enable_next = False
        self.gauge.SetValue(0)
        self.result_label.Hide()
        self.gauge.Show()
        self.Layout()
        self.wait_cursor = wx.BusyCursor()

    def progress_calibration(self, progress):
        self.gauge.SetValue(progress)

    def after_calibration(self, response):
        ret, result = response

        if ret:
            response_platform_extrinsics = result[0]
            response_laser_triangulation = result[1]

            profile.settings['distance_left'] = response_laser_triangulation[0][0]
            profile.settings['normal_left'] = response_laser_triangulation[0][1]
            profile.settings['distance_right'] = response_laser_triangulation[1][0]
            profile.settings['normal_right'] = response_laser_triangulation[1][1]

            profile.settings['rotation_matrix'] = response_platform_extrinsics[0]
            profile.settings['translation_vector'] = response_platform_extrinsics[1]

            profile.settings['laser_triangulation_hash'] = calibration_data.md5_hash()
            profile.settings['platform_extrinsics_hash'] = calibration_data.md5_hash()

            combo_calibration.accept()
        else:
            if isinstance(result, ComboCalibrationError):
                self.result_label.SetLabel(
                    _("Check the pattern and the lasers and try again"))
                dlg = wx.MessageDialog(
                    self, _("Scanner calibration has failed. "
                            "Please check the pattern and the lasers and try again. "
                            "Also you can set up the calibration's settings "
                            "in the \"Adjustment workbench\" until the pattern "
                            "and the lasers are detected correctly"),
                    _("Calibration failed"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
            self.skip_button.Enable()
            self.on_finish_calibration()

        self.gauge.SetValue(100)

        if ret:
            self.skip_button.Disable()
            self.next_button.Enable()
            self.result_label.SetLabel(_("Success. Please press \"Next\" to continue"))
            dlg = wx.MessageDialog(
                self, _("Scanner calibrated correctly"),
                _("Success"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.skip_button.Enable()
            self.next_button.Disable()

        self.on_finish_calibration()

    def on_finish_calibration(self):
        self.breadcrumbs.Enable()
        self.enable_next = True
        self.gauge.Hide()
        self.result_label.Show()
        self.calibrate_button.Enable()
        self.cancel_button.Disable()
        self.prev_button.Enable()
        self.panel.Fit()
        self.panel.Layout()
        self.Layout()
        if hasattr(self, 'wait_cursor'):
            del self.wait_cursor

    def update_status(self, status):
        if status:
            self.GetParent().parent.workbench['calibration'].setup_engine()
            self.video_view.play()
            self.calibrate_button.Enable()
            self.skip_button.Enable()
            driver.board.lasers_off()
        else:
            self.video_view.stop()
            self.gauge.SetValue(0)
            self.gauge.Show()
            self.prev_button.Enable()
            self.skip_button.Disable()
            self.next_button.Disable()
            self.calibrate_button.Disable()
            self.cancel_button.Disable()
