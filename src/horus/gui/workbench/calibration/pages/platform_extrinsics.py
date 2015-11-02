# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

from horus.gui.workbench.calibration.pages.page import Page
from horus.gui.workbench.calibration.pages.video_page import VideoPage


class PlatformExtrinsicsPages(wx.Panel):

    def __init__(self, parent, accept_callback=None, cancel_callback=None):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)

        self.accept_callback = accept_callback
        self.cancel_callback = cancel_callback

        self.SetBackgroundColour(wx.BLUE)

        self.video_page = VideoPage(self, title=_('Platform extrinsics'),
                                    start_callback=self.on_start, cancel_callback=self.on_cancel)
        self.result_page = ResultPage(self, accet_callback=self.on_accept, reject_callback=self.on_cancel)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.video_page, 1, wx.ALL | wx.EXPAND, 0)
        hbox.Add(self.result_page, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(hbox)

        self._initialize()
        self.Layout()

    def _initialize(self):
        self.video_page.Show()
        # self.result_page.Hide()

    def on_cancel(self):
        self.Hide()
        self._initialize()
        if self.cancel_callback is not None:
            self.cancel_callback()

    def on_start(self):
        self.video_page.Show()
        self.result_page.Hide()
        pass

    def on_accept(self, result):
        self.Hide()
        self._initialize()
        if self.accept_callback is not None:
            self.accept_callback(result)


class ResultPage(Page):

    def __init__(self, parent, accet_callback=None, reject_callback=None):
        Page.__init__(self, parent,
                      title=_('Platform extrinsics result'),
                      left=_('Reject'),
                      right=_('Accept'),
                      button_left_callback=reject_callback,
                      button_right_callback=accet_callback)

        # 3D Plot Panel
        self.plot_panel = PlatformExtrinsics3DPlot(self.panel)

        # Layout
        self.panel_box.Add(self.plot_panel, 2, wx.ALL | wx.EXPAND, 3)

        # Events
        self.Bind(wx.EVT_SHOW, self.on_show)

    def on_show(self, event):
        if event.GetShow():
            self.GetParent().Layout()
            self.Layout()

    def process_calibration(self, response):
        ret, result = response

        if ret:
            # R = result[0]
            # t = result[1]
            # self.GetParent().GetParent().controls.panels[
            #     'platform_extrinsics_panel'].setParameters((R, t))
            self.plot_panel.clear()
            self.plot_panel.add(result)
            self.plot_panel.Show()
            self.Layout()
        else:
            if isinstance(result, PlatformExtrinsicsError):
                dlg = wx.MessageDialog(
                    self, _("Platform Extrinsics Calibration has failed. Please try again."),
                    _(result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()


class PlatformExtrinsics3DPlot(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.initialize()

    def initialize(self):
        fig = Figure(facecolor=(0.7490196, 0.7490196, 0.7490196, 1), tight_layout=True)
        self.canvas = FigureCanvasWxAgg(self, -1, fig)
        self.canvas.SetExtraStyle(wx.EXPAND)
        self.ax = fig.gca(projection='3d', axisbg=(0.7490196, 0.7490196, 0.7490196, 1))

        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Layout()

    def onSize(self, event):
        self.canvas.SetClientSize(self.GetClientSize())
        self.canvas.draw()
        self.Layout()

    def add(self, args):
        R, t, center, point, normal, [x, y, z], circle = args

        # plot the surface, data, and synthetic circle
        self.ax.scatter(x, z, y, c='b', marker='o')
        # self.ax.scatter(center[0], center[2], center[1], c='b', marker='o')
        self.ax.plot(circle[0], circle[2], circle[1], c='r')

        d = pattern.distance

        self.ax.plot([t[0], t[0] + 50 * R[0][0]], [t[2], t[2] + 50 * R[2][0]],
                     [t[1], t[1] + 50 * R[1][0]], linewidth=2.0, color='red')
        self.ax.plot([t[0], t[0] + 50 * R[0][1]], [t[2], t[2] + 50 * R[2][1]],
                     [t[1], t[1] + 50 * R[1][1]], linewidth=2.0, color='green')
        self.ax.plot([t[0], t[0] + d * R[0][2]], [t[2], t[2] + d * R[2][2]],
                     [t[1], t[1] + d * R[1][2]], linewidth=2.0, color='blue')

        self.ax.plot([0, 50], [0, 0], [0, 0], linewidth=2.0, color='red')
        self.ax.plot([0, 0], [0, 0], [0, 50], linewidth=2.0, color='green')
        self.ax.plot([0, 0], [0, 50], [0, 0], linewidth=2.0, color='blue')

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Z')
        self.ax.set_zlabel('Y')

        self.ax.set_xlim(-150, 150)
        self.ax.set_ylim(0, 400)
        self.ax.set_zlim(-150, 150)

        self.ax.invert_xaxis()
        self.ax.invert_yaxis()
        self.ax.invert_zaxis()

        self.canvas.draw()
        self.Layout()

    def clear(self):
        self.ax.cla()
