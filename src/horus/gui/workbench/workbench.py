# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
import wx.lib.scrolledpanel

from horus.util import resources

from horus.gui.engine import driver, image_capture
from horus.engine.driver.board import WrongFirmware, BoardNotConnected
from horus.engine.driver.camera import WrongCamera, CameraNotConnected, InvalidVideo

from horus.gui.util.imageView import VideoView
from horus.gui.util.customPanels import ExpandableControl


class Workbench(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.toolbar = wx.ToolBar(self)
        self.combo = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        self._panel = wx.Panel(self)
        self.scroll_panel = wx.lib.scrolledpanel.ScrolledPanel(self._panel, size=(-1, -1))
        self.scroll_panel.SetupScrolling(scroll_x=False, scrollIntoView=False)
        self.scroll_panel.SetAutoLayout(1)

        self.toolbar.SetDoubleBuffered(True)

        hbox.Add(self.toolbar, 0, wx.ALL | wx.EXPAND, 1)
        hbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 1)
        hbox.Add(self.combo, 0, wx.ALL, 10)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 1)
        vbox.Add(self._panel, 1, wx.ALL | wx.EXPAND, 0)

        self._panel.SetSizer(self.hbox)
        self._panel.Layout()

        self.SetSizer(vbox)
        self.Layout()
        self.Hide()

    def add_to_panel(self, _object, _size):
        if _object is not None:
            self.hbox.Add(_object, _size, wx.ALL | wx.EXPAND, 1)


class WorkbenchConnection(Workbench):

    def __init__(self, parent):
        Workbench.__init__(self, parent)

        # Toolbar Configuration
        self.connect_tool = self.toolbar.AddLabelTool(
            wx.NewId(), _("Connect"),
            wx.Bitmap(resources.get_path_for_image("connect.png")), shortHelp=_("Connect"))
        self.disconnect_tool = self.toolbar.AddLabelTool(
            wx.NewId(), _("Disconnect"),
            wx.Bitmap(resources.get_path_for_image("disconnect.png")), shortHelp=_("Disconnect"))
        self.toolbar.Realize()

        # Disable Toolbar Items
        self._enable_tool(self.connect_tool, True)
        self._enable_tool(self.disconnect_tool, False)

        # Bind Toolbar Items
        self.Bind(wx.EVT_TOOL, self.on_connect_tool_clicked, self.connect_tool)
        self.Bind(wx.EVT_TOOL, self.on_disconnect_tool_clicked, self.disconnect_tool)
        self.Bind(wx.EVT_SHOW, self.on_show)

        # Load controls
        self.controls = ExpandableControl(self.scroll_panel)
        self.load_controls()
        self.controls.init_panels()
        self.controls.update_callbacks()
        self.video_view = VideoView(self._panel, image_capture.capture_image, 10)

        # Layout
        vsbox = wx.BoxSizer(wx.VERTICAL)
        vsbox.Add(self.controls, 0, wx.ALL | wx.EXPAND, 0)
        self.scroll_panel.SetSizer(vsbox)
        vsbox.Fit(self.scroll_panel)
        panel_size = self.scroll_panel.GetSize()[0] + wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
        self.scroll_panel.SetMinSize((panel_size, -1))
        self.add_to_panel(self.scroll_panel, 0)
        self.add_to_panel(self.video_view, 1)

        self.Layout()

    def load_controls(self):
        raise NotImplementedError

    def update_engine(self):
        raise NotImplementedError

    def update_status(self, status):
        self._enable_tool(self.connect_tool, not status)
        self._enable_tool(self.disconnect_tool, status)
        if status:
            self.update_engine()
            self.controls.enableContent()
            callback = self.GetParent().on_board_unplugged
            driver.board.set_unplug_callback(lambda: wx.CallAfter(callback))
            callback = self.GetParent().on_camera_unplugged
            driver.camera.set_unplug_callback(lambda: wx.CallAfter(callback))
        else:
            driver.board.set_unplug_callback(None)
            driver.camera.set_unplug_callback(None)
            self.controls.disableContent()

    def update_controls(self):
        self.controls.updateProfile()
        if driver.is_connected:
            self.update_engine()

    def on_open(self):
        if driver.is_connected:
            self.update_engine()
        self.video_view.play()

    def on_close(self):
        self.video_view.stop()

    def on_show(self, event):
        if event.GetShow():
            self.on_open()
        else:
            self.on_close()

    def on_connect_tool_clicked(self, event):
        driver.set_callbacks(lambda: wx.CallAfter(self.before_connect),
                             lambda r: wx.CallAfter(self.after_connect, r))
        driver.connect()

    def on_disconnect_tool_clicked(self, event):
        driver.disconnect()
        self.update_status(driver.is_connected)

    def before_connect(self):
        self._enable_tool(self.connect_tool, False)
        self.combo.Disable()
        for i in xrange(self.GetParent().menuBar.GetMenuCount()):
            self.GetParent().menuBar.EnableTop(i, False)
        driver.board.set_unplug_callback(None)
        driver.camera.set_unplug_callback(None)
        self.waitCursor = wx.BusyCursor()

    def after_connect(self, response):
        ret, result = response
        if not ret:
            if isinstance(result, WrongFirmware):
                self._show_message(_(result), wx.ICON_INFORMATION,
                                   _("Board has a wrong firmware or an invalid Baud Rate.\n"
                                     "Please select your Board and press Upload Firmware"))
                self.update_status(False)
                self.GetParent().on_preferences(None)
            elif isinstance(result, BoardNotConnected):
                self._show_message(_(result), wx.ICON_INFORMATION,
                                   _("Board is not connected.\n"
                                     "Please connect your board and select a valid Serial Name"))
                self.update_status(False)
                self.GetParent().on_preferences(None)
            elif isinstance(result, WrongCamera):
                self._show_message(_(result), wx.ICON_INFORMATION,
                                   _("You probably have selected a wrong camera.\n"
                                     "Please select other Camera Id"))
                self.update_status(False)
                self.GetParent().on_preferences(None)
            elif isinstance(result, CameraNotConnected):
                self._show_message(_(result), wx.ICON_ERROR,
                                   _("Please plug your camera and try to connect again"))
            elif isinstance(result, InvalidVideo):
                self._show_message(_(result), wx.ICON_ERROR,
                                   _("Unplug and plug your camera USB cable "
                                     "and try to connect again"))

        self.combo.Enable()
        self.update_status(driver.is_connected)
        for i in xrange(self.GetParent().menuBar.GetMenuCount()):
            self.GetParent().menuBar.EnableTop(i, True)
        del self.waitCursor

    def _show_message(self, title, style, desc):
        dlg = wx.MessageDialog(self, desc, result, wx.OK | style)
        dlg.ShowModal()
        dlg.Destroy()

    def _enable_tool(self, item, enable):
        self.toolbar.EnableTool(item.GetId(), enable)
