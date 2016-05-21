# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.\
                 Copyright (C) 2013 David Braam from Cura Project'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx
import traceback
import sys
import os
import time

from wx import glcanvas
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *


class animation(object):

    def __init__(self, gui, start, end, run_time):
        self._start = start
        self._end = end
        self._start_time = time.time()
        self._run_time = run_time
        gui._animation_list.append(self)

    def is_done(self):
        return time.time() > self._start_time + self._run_time

    def get_position(self):
        if self.is_done():
            return self._end
        f = (time.time() - self._start_time) / self._run_time
        ts = f * f
        tc = f * f * f
        # f = 6*tc*ts + -15*ts*ts + 10*tc
        f = tc + -3 * ts + 3 * f
        return self._start + (self._end - self._start) * f


class glGuiControl(object):

    def __init__(self, parent, pos):
        self._parent = parent
        self._base = parent._base
        self._pos = pos
        self._size = (0, 0, 1, 1)
        self._parent.add(self)

    def set_size(self, x, y, w, h):
        self._size = (x, y, w, h)

    def get_size(self):
        return self._size

    def get_min_size(self):
        return 1, 1

    def update_layout(self):
        pass

    def focus_next(self):
        control_list = self._parent._gl_gui_control_list
        for n in xrange(control_list.index(self) + 1, len(control_list)):
            if self._parent._gl_gui_control_list[n].setFocus():
                return
        for n in xrange(0, control_list.index(self)):
            if self._parent._gl_gui_control_list[n].setFocus():
                return

    def focus_previous(self):
        control_list = self._parent._gl_gui_control_list
        for n in xrange(control_list.index(self) - 1, -1, -1):
            if self._parent._gl_gui_control_list[n].setFocus():
                return
        for n in xrange(len(control_list) - 1, control_list.index(self), -1):
            if self._parent._gl_gui_control_list[n].setFocus():
                return

    def set_focus(self):
        return False

    def has_focus(self):
        return self._base._focus == self

    def on_mouse_up(self, x, y):
        pass

    def on_key_down(self, key):
        pass

    def on_key_up(self, key):
        pass


class glGuiContainer(glGuiControl):

    def __init__(self, parent, pos):
        self._gl_gui_control_list = []
        super(glGuiContainer, self).__init__(parent, pos)

    def add(self, ctrl):
        self._gl_gui_control_list.append(ctrl)
        self.update_layout()

    def on_mouse_down(self, x, y, button):
        for ctrl in self._gl_gui_control_list:
            if ctrl.on_mouse_down(x, y, button):
                return True
        return False

    def on_mouse_up(self, x, y):
        for ctrl in self._gl_gui_control_list:
            if ctrl.on_mouse_up(x, y):
                return True
        return False

    def on_mouse_motion(self, x, y):
        handled = False
        for ctrl in self._gl_gui_control_list:
            if ctrl.on_mouse_motion(x, y):
                handled = True
        return handled

    def draw(self):
        for ctrl in self._gl_gui_control_list:
            ctrl.draw()

    def update_layout(self):
        for ctrl in self._gl_gui_control_list:
            ctrl.update_layout()


class glGuiPanel(glcanvas.GLCanvas):

    def __init__(self, parent):
        attrib_list = (glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER,
                       glcanvas.WX_GL_DEPTH_SIZE, 24, glcanvas.WX_GL_STENCIL_SIZE, 8, 0)
        glcanvas.GLCanvas.__init__(self, parent, style=wx.WANTS_CHARS, attribList=attrib_list)
        self._base = self
        self._focus = None
        self._container = None
        self._container = glGuiContainer(self, (0, 0))
        self._shown_error = False

        self._context = glcanvas.GLContext(self)
        self._button_size = 64

        self._animation_list = []
        self.gl_release_list = []
        self._refresh_queued = False
        self._idle_called = False

        wx.EVT_PAINT(self, self._on_gui_paint)
        wx.EVT_SIZE(self, self._on_size)
        wx.EVT_ERASE_BACKGROUND(self, self._on_erase_background)
        wx.EVT_LEFT_DOWN(self, self._on_gui_mouse_down)
        wx.EVT_LEFT_DCLICK(self, self._on_gui_mouse_down)
        wx.EVT_LEFT_UP(self, self._on_gui_mouse_up)
        wx.EVT_RIGHT_DOWN(self, self._on_gui_mouse_down)
        wx.EVT_RIGHT_DCLICK(self, self._on_gui_mouse_down)
        wx.EVT_RIGHT_UP(self, self._on_gui_mouse_up)
        wx.EVT_MIDDLE_DOWN(self, self._on_gui_mouse_down)
        wx.EVT_MIDDLE_DCLICK(self, self._on_gui_mouse_down)
        wx.EVT_MIDDLE_UP(self, self._on_gui_mouse_up)
        wx.EVT_MOTION(self, self._on_gui_mouse_motion)
        wx.EVT_KEY_DOWN(self, self._on_gui_key_down)
        wx.EVT_KEY_UP(self, self._on_gui_key_up)
        wx.EVT_KILL_FOCUS(self, self._on_focus_lost)
        wx.EVT_IDLE(self, self._on_idle)

    def _on_idle(self, e):
        self._idle_called = True
        if len(self._animation_list) > 0 or self._refresh_queued:
            self._refresh_queued = False
            for anim in self._animation_list:
                if anim.is_done():
                    self._animation_list.remove(anim)
            self.Refresh()

    def _on_gui_key_up(self, e):
        if self._focus is not None:
            self._focus.on_key_up(e.GetKeyCode())
            self.Refresh()
        else:
            self.on_key_up(e.GetKeyCode())

    def _on_gui_key_down(self, e):
        if self._focus is not None:
            self._focus.on_key_down(e.GetKeyCode())
            self.Refresh()
        else:
            self.on_key_down(e.GetKeyCode())

    def _on_focus_lost(self, e):
        self._focus = None
        self.Refresh()

    def _on_gui_mouse_down(self, e):
        self.SetFocus()
        if self._container.on_mouse_down(e.GetX(), e.GetY(), e.GetButton()):
            self.Refresh()
            return
        self.on_mouse_down(e)

    def _on_gui_mouse_up(self, e):
        if self._container.on_mouse_up(e.GetX(), e.GetY()):
            self.Refresh()
            return
        self.on_mouse_up(e)

    def _on_gui_mouse_motion(self, e):
        self.Refresh()
        if not self._container.on_mouse_motion(e.GetX(), e.GetY()):
            self.on_mouse_motion(e)

    def _on_gui_paint(self, e):
        wx.PaintDC(self)
        try:
            self.SetCurrent(self._context)
            for obj in self.gl_release_list:
                obj.release()
            del self.gl_release_list[:]
            self.on_paint(e)
            self._draw_gui()
            glFlush()
            self.SwapBuffers()
        except:
            # When an exception happens, catch it and show a message box.
            # If the exception is not caught the draw function bugs out.
            # Only show this exception once so we do not overload the user with popups.
            errStr = _("An error occurred during the 3D view drawing.")
            tb = traceback.extract_tb(sys.exc_info()[2])
            errStr += "\n%s: '%s'" % (str(sys.exc_info()[0].__name__), str(sys.exc_info()[1]))
            for n in xrange(len(tb) - 1, -1, -1):
                locationInfo = tb[n]
                errStr += "\n @ %s:%s:%d" % (
                    os.path.basename(locationInfo[0]), locationInfo[2], locationInfo[1])
            if not self._shown_error:
                traceback.print_exc()
                wx.CallAfter(
                    wx.MessageBox, errStr, _("3D window error"), wx.OK | wx.ICON_EXCLAMATION)
                self._shown_error = True

    def _draw_gui(self):
        # if self._glButtonsTexture is None:
        # self._glButtonsTexture = opengl_helpers.load_gl_texture('glButtons.png')

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)
        glColor4ub(255, 255, 255, 255)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        size = self.GetSize()
        glOrtho(0, size.GetWidth() - 1, size.GetHeight() - 1, 0, -1000.0, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self._container.draw()

    def _on_erase_background(self, event):
        # Workaround for windows background redraw flicker.
        pass

    def _on_size(self, e):
        self._container.set_size(0, 0, self.GetSize().GetWidth(), self.GetSize().GetHeight())
        self._container.update_layout()
        self.Refresh()

    def on_mouse_down(self, e):
        pass

    def on_mouse_up(self, e):
        pass

    def on_mouse_motion(self, e):
        pass

    def on_paint(self, e):
        pass

    def queue_refresh(self):
        wx.CallAfter(self._queue_refresh)

    def _queue_refresh(self):
        if self._idle_called:
            wx.CallAfter(self.Refresh)
        else:
            self._refresh_queued = True

    def add(self, ctrl):
        if self._container is not None:
            self._container.add(ctrl)
