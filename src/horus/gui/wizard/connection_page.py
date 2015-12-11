# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.util import profile, resources

from horus.gui.engine import driver, scanner_autocheck, image_capture, image_detection
from horus.gui.util.image_view import ImageView
from horus.gui.wizard.wizard_page import WizardPage

from horus.engine.driver.board import WrongFirmware, BoardNotConnected
from horus.engine.driver.camera import WrongCamera, CameraNotConnected, InvalidVideo
from horus.engine.calibration.autocheck import PatternNotDetected, \
    WrongMotorDirection, LaserNotDetected


class ConnectionPage(WizardPage):

    def __init__(self, parent, button_prev_callback=None, button_next_callback=None):
        WizardPage.__init__(self, parent,
                            title=_("Connection"),
                            button_prev_callback=button_prev_callback,
                            button_next_callback=button_next_callback)

        self.parent = parent

        self.connect_button = wx.Button(self.panel, label=_("Connect"))
        self.settings_button = wx.Button(self.panel, label=_("Edit settings"))

        self.pattern_label = wx.StaticText(self.panel, label=_(
            "Put the pattern on the platform as shown in the picture and press \"Auto check\""))
        self.pattern_label.Wrap(400)
        self.image_view = ImageView(self.panel, quality=wx.IMAGE_QUALITY_HIGH)
        self.image_view.set_image(wx.Image(resources.get_path_for_image("pattern-position.png")))
        self.auto_check_button = wx.Button(self.panel, label=_("Auto check"))
        self.gauge = wx.Gauge(self.panel, range=100, size=(-1, 30))
        self.result_label = wx.StaticText(self.panel, size=(-1, 30))

        self.connect_button.Enable()
        self.settings_button.Enable()
        self.pattern_label.Disable()
        self.image_view.Disable()
        self.auto_check_button.Disable()
        self.skip_button.Disable()
        self.next_button.Disable()
        self.result_label.Hide()
        self.enable_next = False

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.connect_button, 1, wx.ALL | wx.EXPAND, 5)
        hbox.Add(self.settings_button, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 2)
        vbox.Add(self.pattern_label, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(self.image_view, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(self.result_label, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(self.gauge, 0, wx.ALL | wx.EXPAND, 5)
        vbox.Add(self.auto_check_button, 0, wx.ALL | wx.EXPAND, 5)
        self.panel.SetSizer(vbox)

        self.Layout()

        self.connect_button.Bind(wx.EVT_BUTTON, self.on_connect_button_clicked)
        self.settings_button.Bind(wx.EVT_BUTTON, self.on_settings_button_clicked)
        self.auto_check_button.Bind(wx.EVT_BUTTON, self.on_auto_check_button_clicked)
        self.Bind(wx.EVT_SHOW, self.on_show)

        self.video_view.set_milliseconds(10)
        self.video_view.set_callback(self.get_image)
        self.update_status(driver.is_connected)

    def on_show(self, event):
        if event.GetShow():
            self.update_status(driver.is_connected)
        else:
            try:
                self.video_view.stop()
            except:
                pass

    def get_image(self):
        if scanner_autocheck.image is not None:
            image = scanner_autocheck.image
        else:
            image = image_capture.capture_pattern()
            image = image_detection.detect_pattern(image)
        return image

    def on_unplugged(self):
        self.video_view.stop()
        scanner_autocheck.cancel()
        self.after_auto_check()

    def on_connect_button_clicked(self, event):
        driver.set_callbacks(
            lambda: wx.CallAfter(self.before_connect),
            lambda r: wx.CallAfter(self.after_connect, r))
        driver.connect()

    def on_settings_button_clicked(self, event):
        SettingsWindow(self)

    def before_connect(self):
        self.settings_button.Disable()
        self.breadcrumbs.Disable()
        self.connect_button.Disable()
        self.prev_button.Disable()
        self.video_view.stop()
        driver.board.set_unplug_callback(None)
        driver.camera.set_unplug_callback(None)
        self.wait_cursor = wx.BusyCursor()

    def after_connect(self, response):
        ret, result = response

        if not ret:
            if isinstance(result, WrongFirmware):
                dlg = wx.MessageDialog(
                    self,
                    _("Board has a wrong firmware or an invalid Baud Rate.\n"
                      "Please select your Board and press Upload Firmware"),
                    _(result), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.update_status(False)
                self.GetParent().parent.on_preferences(None)
            elif isinstance(result, BoardNotConnected):
                dlg = wx.MessageDialog(
                    self,
                    _("Board is not connected.\n"
                      "Please connect your board and select a valid Serial Name"),
                    _(result), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.update_status(False)
                self.GetParent().parent.on_preferences(None)
            elif isinstance(result, WrongCamera):
                dlg = wx.MessageDialog(
                    self,
                    _("You probably have selected a wrong camera.\n"
                      "Please select other Camera Id"),
                    _(result), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.update_status(False)
                self.GetParent().parent.on_preferences(None)
            elif isinstance(result, CameraNotConnected):
                dlg = wx.MessageDialog(
                    self, _("Please plug your camera and try to connect again"),
                    _(result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
            elif isinstance(result, InvalidVideo):
                dlg = wx.MessageDialog(
                    self, _("Unplug and plug your camera USB cable and try to connect again"),
                    _(result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

        self.update_status(driver.is_connected)
        self.settings_button.Enable()
        self.breadcrumbs.Enable()
        self.prev_button.Enable()
        del self.wait_cursor

    def on_auto_check_button_clicked(self, event):
        if profile.settings['adjust_laser']:
            profile.settings['adjust_laser'] = False
            dlg = wx.MessageDialog(
                self,
                _("It is recomended to adjust line lasers vertically.\n"
                  "You need to use the allen wrench.\nDo you want to adjust it now?"),
                _("Manual laser adjustment"), wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()
            if result:
                driver.board.lasers_on()
        else:
            # Perform auto check
            scanner_autocheck.set_callbacks(lambda: wx.CallAfter(self.before_auto_check),
                                            lambda p: wx.CallAfter(self.progress_auto_check, p),
                                            lambda r: wx.CallAfter(self.after_auto_check, r))
            scanner_autocheck.start()

    def before_auto_check(self):
        self.settings_button.Disable()
        self.breadcrumbs.Disable()
        self.auto_check_button.Disable()
        self.prev_button.Disable()
        self.skip_button.Disable()
        self.next_button.Disable()
        self.enable_next = False
        self.gauge.SetValue(0)
        self.result_label.Hide()
        self.gauge.Show()
        self.wait_cursor = wx.BusyCursor()
        self.Layout()

    def progress_auto_check(self, progress):
        self.gauge.SetValue(progress)

    def after_auto_check(self, response):
        ret, result = response

        if ret:
            self.result_label.SetLabel(_("Success. Please press next to continue"))
            dlg = wx.MessageDialog(
                self, _("Scanner configured correctly"),
                _("Success"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.result_label.SetLabel(str(result))
            if isinstance(result, PatternNotDetected):
                dlg = wx.MessageDialog(
                    self, _("Please, put the pattern on the platform"),
                    _(result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
            elif isinstance(result, WrongMotorDirection):
                dlg = wx.MessageDialog(
                    self, _(
                        'Please, select "Invert the motor direction" in Preferences'),
                    _(result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.GetParent().parent.on_preferences(None)
            elif isinstance(result, LaserNotDetected):
                dlg = wx.MessageDialog(
                    self, _("Please, check the lasers connection"),
                    _(result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

        if ret:
            self.skip_button.Disable()
            self.next_button.Enable()
        else:
            self.skip_button.Enable()
            self.next_button.Disable()

        self.settings_button.Enable()
        self.breadcrumbs.Enable()
        self.enable_next = True
        self.result_label.Show()
        self.auto_check_button.Enable()
        self.prev_button.Enable()
        self.gauge.Hide()
        if hasattr(self, 'wait_cursor'):
            del self.wait_cursor
        self.panel.Fit()
        self.panel.Layout()
        self.Layout()

    def update_status(self, status):
        if status:
            driver.board.set_unplug_callback(
                lambda: wx.CallAfter(self.parent.on_board_unplugged))
            driver.camera.set_unplug_callback(
                lambda: wx.CallAfter(self.parent.on_camera_unplugged))
            self.GetParent().parent.workbench['calibration'].setup_engine()
            self.video_view.play()
            self.connect_button.Disable()
            self.auto_check_button.Enable()
            self.settings_button.Enable()
            self.image_view.Enable()
            self.skip_button.Enable()
            self.enable_next = True
            driver.board.lasers_off()
        else:
            self.video_view.stop()
            self.gauge.SetValue(0)
            self.gauge.Show()
            self.result_label.Hide()
            self.result_label.SetLabel("")
            self.connect_button.Enable()
            self.skip_button.Disable()
            self.next_button.Disable()
            self.enable_next = False
            self.auto_check_button.Disable()
        self.Layout()


class SettingsWindow(wx.Dialog):

    def __init__(self, parent):
        super(SettingsWindow, self).__init__(
            parent, title=_('Settings'), size=(420, -1),
            style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        # Elements
        _choices = []
        choices = profile.settings.get_possible_values('luminosity')
        for i in choices:
            _choices.append(_(i))
        self.init_luminosity = profile.settings['luminosity']
        self.luminosity_dict = dict(zip(_choices, choices))
        self.luminosity_text = wx.StaticText(self, label=_('Luminosity'))
        self.luminosity_text.SetToolTip(wx.ToolTip(
            _('Change the luminosity until colored lines appear '
              'over the chess pattern in the video')))
        self.luminosity_combo_box = wx.ComboBox(self, wx.ID_ANY,
                                                value=_(self.init_luminosity),
                                                choices=_choices,
                                                style=wx.CB_READONLY)
        self.ok_button = wx.Button(self, label=_('OK'))
        self.cancel_button = wx.Button(self, label=_('Cancel'))

        # Events
        self.luminosity_combo_box.Bind(wx.EVT_COMBOBOX, self.on_luminosity_combo_box_changed)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_close)
        self.ok_button.Bind(wx.EVT_BUTTON, self.on_ok)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.luminosity_text, 0, wx.ALL, 7)
        hbox.Add(self.luminosity_combo_box, 1, wx.ALL, 3)
        vbox.Add(hbox, 0, wx.ALL ^ wx.BOTTOM | wx.EXPAND, 7)
        vbox.Add(wx.StaticLine(self), 0, wx.ALL ^ wx.BOTTOM | wx.EXPAND, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.cancel_button, 1, wx.ALL, 3)
        hbox.Add(self.ok_button, 1, wx.ALL, 3)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(vbox)
        self.Center()
        self.Fit()

        self.ShowModal()

    def set_luminosity(self, luminosity):
        profile.settings['luminosity'] = luminosity

        if luminosity == 'Low':
            luminosity = 32
        elif luminosity == 'Medium':
            luminosity = 16
        elif luminosity == 'High':
            luminosity = 8
        elif luminosity == 'Very high':
            luminosity = 4

        profile.settings['exposure_control'] = luminosity
        profile.settings['exposure_texture_scanning'] = luminosity
        profile.settings['exposure_pattern_calibration'] = luminosity
        """
        exposure_texture_scanning
        exposure_pattern_calibration
        """
        driver.camera.set_exposure(luminosity)

    def on_luminosity_combo_box_changed(self, event):
        value = self.luminosity_dict[event.GetEventObject().GetValue()]
        self.set_luminosity(value)

    def on_ok(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def on_close(self, event):
        self.set_luminosity(self.init_luminosity)
        self.EndModal(wx.ID_OK)
        self.Destroy()
