# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.\
                 Copyright (C) 2013 David Braam from Cura Project'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import os
import gc
import wx
import math
import numpy
import traceback

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GLU import *
from OpenGL.GL import *

from horus.util import profile, mesh_loader, model, system as sys
from horus.gui.util import opengl_helpers, opengl_gui


class SceneView(opengl_gui.glGuiPanel):

    def __init__(self, parent):
        super(SceneView, self).__init__(parent)

        self._yaw = 30
        self._pitch = 60
        self._zoom = 300
        self._object = None
        self._object_shader = None
        self._object_load_shader = None
        self._obj_color = None
        self._mouse_x = -1
        self._mouse_y = -1
        self._mouse_state = None
        self._mouse_3d_pos = numpy.array([0, 0, 0], numpy.float32)
        self._view_target = numpy.array([0, 0, 0], numpy.float32)
        self._anim_view = None
        self._anim_zoom = None
        self._platform_mesh = {}
        self._platform_texture = None

        self._viewport = None
        self._model_matrix = None
        self._proj_matrix = None
        self.temp_matrix = None

        self.view_mode = 'ply'

        self._move_vertical = False
        self._show_delete_menu = True

        self._z_offset = 0
        self._h_offset = 20

        self._view_roi = False
        self._point_size = 2

        self._object_point_cloud = []
        self._object_texture = []

        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)
        self.Bind(wx.EVT_SHOW, self.on_show)

        self.update_profile_to_controls()

    def on_show(self, event):
        if event.GetShow():
            self.GetParent().Layout()
            self.Layout()

    def __del__(self):
        if self._object_shader is not None:
            self._object_shader.release()
        if self._object_shader_no_light is not None:
            self._object_shader_no_light.release()
        if self._object_load_shader is not None:
            self._object_load_shader.release()
        if self._object is not None:
            if self._object._mesh is not None:
                if self._object._mesh.vbo is not None and self._object._mesh.vbo.dec_ref():
                    self.gl_release_list.append(self._object._mesh.vbo)
                    self._object._mesh.vbo.release()
                del self._object._mesh
            del self._object
        if self._platform_mesh is not None:
            for _object in self._platform_mesh.values():
                if _object._mesh is not None:
                    if _object._mesh.vbo is not None and _object._mesh.vbo.dec_ref():
                        self.gl_release_list.append(_object._mesh.vbo)
                        _object._mesh.vbo.release()
                    del _object._mesh
                del _object
        gc.collect()

    def create_default_object(self):
        self._clear_scene()
        self._object = model.Model(None, is_point_cloud=True)
        self._object._add_mesh()
        self._object._mesh._prepare_vertex_count(4000000)

    def append_point_cloud(self, point, color):
        self._object_point_cloud.append(point)
        self._object_texture.append(color)
        # TODO: optimize
        if self._object is not None:
            if self._object._mesh is not None:
                for i in xrange(point.shape[1]):
                    self._object._mesh._add_vertex(
                        point[0][i], point[1][i], point[2][i],
                        color[0][i], color[1][i], color[2][i])
            # Conpute Z center
            if point.shape[1] > 0:
                zmax = max(point[2])
                if zmax > self._object._size[2]:
                    self._object._size[2] = zmax
                    self.center_height()
                self.queue_refresh()
        # Delete objects
        del point
        del color

    def load_file(self, filename):
        # Only one STL / PLY file can be active
        if filename is not None:
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.ply' or ext == '.stl':
                model_filename = filename
            if model_filename:
                self.load_scene(model_filename)
                self.center_object()

    def center_height(self):
        if self._object is None:
            return
        height = self._object.get_size()[2] / 2
        if abs(height) > abs(self._h_offset):
            height -= self._h_offset
        new_view_pos = numpy.array(
            [self._object.get_position()[0],
             self._object.get_position()[1],
             height - self._z_offset])
        self._anim_view = opengl_gui.animation(self, self._view_target.copy(), new_view_pos, 0.5)

    def load_scene(self, filename):
        try:
            self._clear_scene()
            self._object = mesh_loader.load_mesh(filename)
        except:
            traceback.print_exc()

    def _clear_scene(self):
        if self._object is not None:
            if self._object._mesh is not None:
                if self._object._mesh.vbo is not None and self._object._mesh.vbo.dec_ref():
                    self.gl_release_list.append(self._object._mesh.vbo)
                    self._object._mesh.vbo.release()
                del self._object._mesh
            del self._object
            self._object = None
            self.center_object()
            gc.collect()

    def center_object(self):
        if self._object is None:
            new_view_pos = numpy.array([0, 0, -self._z_offset], numpy.float32)
            new_zoom = 300
        else:
            height = self._object.get_size()[2] / 2
            if abs(height) > abs(self._h_offset):
                height -= self._h_offset
            new_view_pos = numpy.array(
                [self._object.get_position()[0],
                 self._object.get_position()[1],
                 height - self._z_offset])
            new_zoom = self._object.get_boundary_circle() * 4

        if new_zoom > numpy.max(self._machine_size) * 3:
            new_zoom = numpy.max(self._machine_size) * 3

        self._anim_zoom = opengl_gui.animation(self, self._zoom, new_zoom, 0.5)
        self._anim_view = opengl_gui.animation(self, self._view_target.copy(), new_view_pos, 0.5)

    def update_profile_to_controls(self):
        self._machine_size = numpy.array([profile.settings['machine_width'],
                                          profile.settings['machine_depth'],
                                          profile.settings['machine_height']])
        color_string = profile.settings['model_color']
        self._obj_color = [float(int(color_string[0:2], 16)) / 255,
                           float(int(color_string[2:4], 16)) / 255,
                           float(int(color_string[4:6], 16)) / 255, 1.0]

    def shader_update(self, v, f):
        s = opengl_helpers.GLShader(v, f)
        if s.is_valid():
            self._object_load_shader.release()
            self._object_load_shader = s
            self.queue_refresh()

    def on_key_down(self, key_code):
        if key_code == wx.WXK_DELETE or \
                key_code == wx.WXK_NUMPAD_DELETE or \
                (key_code == wx.WXK_BACK and sys.is_darwin()):
            if self._show_delete_menu:
                if self._object is not None:
                    self.on_delete_object(None)
                    self.queue_refresh()
        if key_code == wx.WXK_DOWN:
            if wx.GetKeyState(wx.WXK_SHIFT):
                self._zoom *= 1.2
                if self._zoom > numpy.max(self._machine_size) * 3:
                    self._zoom = numpy.max(self._machine_size) * 3
            elif wx.GetKeyState(wx.WXK_CONTROL):
                self._z_offset += 5
            else:
                self._pitch -= 15
            self.queue_refresh()
        elif key_code == wx.WXK_UP:
            if wx.GetKeyState(wx.WXK_SHIFT):
                self._zoom /= 1.2
                if self._zoom < 1:
                    self._zoom = 1
            elif wx.GetKeyState(wx.WXK_CONTROL):
                self._z_offset -= 5
            else:
                self._pitch += 15
            self.queue_refresh()
        elif key_code == wx.WXK_LEFT:
            self._yaw -= 15
            self.queue_refresh()
        elif key_code == wx.WXK_RIGHT:
            self._yaw += 15
            self.queue_refresh()
        elif key_code == wx.WXK_NUMPAD_ADD or key_code == wx.WXK_ADD or \
                key_code == ord('+') or key_code == ord('='):
            self._zoom /= 1.2
            if self._zoom < 1:
                self._zoom = 1
            self.queue_refresh()
        elif key_code == wx.WXK_NUMPAD_SUBTRACT or key_code == wx.WXK_SUBTRACT or \
                key_code == ord('-'):
            self._zoom *= 1.2
            if self._zoom > numpy.max(self._machine_size) * 3:
                self._zoom = numpy.max(self._machine_size) * 3
            self.queue_refresh()
        elif key_code == wx.WXK_HOME:
            self._yaw = 30
            self._pitch = 60
            self.queue_refresh()
        elif key_code == wx.WXK_PAGEUP:
            self._yaw = 0
            self._pitch = 0
            self.queue_refresh()
        elif key_code == wx.WXK_PAGEDOWN:
            self._yaw = 0
            self._pitch = 90
            self.queue_refresh()
        elif key_code == wx.WXK_END:
            self._yaw = 90
            self._pitch = 90
            self.queue_refresh()

        if key_code == wx.WXK_CONTROL:
            self._move_vertical = True

    def on_key_up(self, key_code):
        if key_code == wx.WXK_CONTROL:
            self._move_vertical = False

    def on_mouse_down(self, e):
        self._mouse_x = e.GetX()
        self._mouse_y = e.GetY()
        self._mouse_click_3d_pos = self._mouse_3d_pos
        self._mouse_click_focus = self._object
        if e.ButtonDClick():
            self._mouse_state = 'doubleClick'
        else:
            self._mouse_state = 'dragOrClick'
        if self._mouse_state == 'doubleClick':
            self._move_vertical = False
            if e.GetButton() == 1:
                self.center_object()
                self.queue_refresh()

    def on_mouse_up(self, e):
        if e.LeftIsDown() or e.MiddleIsDown() or e.RightIsDown():
            return
        if self._mouse_state == 'dragOrClick':
            if e.GetButton() == 3:
                if self._show_delete_menu:
                    menu = wx.Menu()
                    if self._object is not None:
                        self.Bind(
                            wx.EVT_MENU, self.on_delete_object, menu.Append(-1, _("Delete object")))
                    if menu.MenuItemCount > 0:
                        self.PopupMenu(menu)
                    menu.Destroy()
        self._mouse_state = None

    def set_show_delete_menu(self, value=True):
        self._show_delete_menu = value

    def set_point_size(self, value):
        self._point_size = value

    def on_delete_object(self, event):
        if self._object is not None:
            dlg = wx.MessageDialog(
                self, _("Your current model will be deleted.\nAre you sure you want to delete it?"),
                _("Clear point cloud"), wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()
            if result:
                self._clear_scene()

    def on_mouse_motion(self, e):
        if e.Dragging() and self._mouse_state is not None:
            if e.LeftIsDown() and not e.RightIsDown():
                self._mouse_state = 'drag'
                if wx.GetKeyState(wx.WXK_SHIFT):
                    a = math.cos(math.radians(self._yaw)) / 3.0
                    b = math.sin(math.radians(self._yaw)) / 3.0
                    self._view_target[0] += float(e.GetX() - self._mouse_x) * -a
                    self._view_target[1] += float(e.GetX() - self._mouse_x) * b
                    self._view_target[0] += float(e.GetY() - self._mouse_y) * b
                    self._view_target[1] += float(e.GetY() - self._mouse_y) * a
                else:
                    self._yaw += e.GetX() - self._mouse_x
                    self._pitch -= e.GetY() - self._mouse_y
                if self._pitch > 170:
                    self._pitch = 170
                if self._pitch < 10:
                    self._pitch = 10
            elif (e.LeftIsDown() and e.RightIsDown()) or e.MiddleIsDown():
                self._mouse_state = 'drag'
                self._zoom += e.GetY() - self._mouse_y
                if self._zoom < 1:
                    self._zoom = 1
                if self._zoom > numpy.max(self._machine_size) * 3:
                    self._zoom = numpy.max(self._machine_size) * 3

        self._mouse_x = e.GetX()
        self._mouse_y = e.GetY()

    def on_mouse_wheel(self, e):
        delta = float(e.GetWheelRotation()) / float(e.GetWheelDelta())
        delta = max(min(delta, 4), -4)
        if self._move_vertical:
            self._z_offset -= 5 * delta
        else:
            self._zoom *= 1.0 - delta / 10.0
            if self._zoom < 1.0:
                self._zoom = 1.0
            if self._zoom > numpy.max(self._machine_size) * 3:
                self._zoom = numpy.max(self._machine_size) * 3
        self.Refresh()

    def on_mouse_leave(self, e):
        self._mouse_x = -1

    def get_mouseay(self, x, y):
        if self._viewport is None:
            return numpy.array([0, 0, 0], numpy.float32), numpy.array([0, 0, 1], numpy.float32)

        p0 = opengl_helpers.unproject(
            x, self._viewport[1] + self._viewport[3] - y, 0,
            self._model_matrix, self._proj_matrix, self._viewport)
        p1 = opengl_helpers.unproject(
            x, self._viewport[1] + self._viewport[3] - y, 1,
            self._model_matrix, self._proj_matrix, self._viewport)
        if p0 is not None and p1 is not None:
            p0 -= self._view_target
            p1 -= self._view_target
            return p0, p1
        else:
            return numpy.array([0, 0, 0], numpy.float32), numpy.array([0, 0, 1], numpy.float32)

    def _init_3d_view(self):
        # set viewing projection
        size = self.GetSize()
        glViewport(0, 0, size.GetWidth(), size.GetHeight())
        glLoadIdentity()

        glLightfv(GL_LIGHT0, GL_POSITION, [0.2, 0.2, 1.0, 0.0])

        glDisable(GL_RESCALE_NORMAL)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # glClearColor(0.0, 0.0, 0.0, 1.0)
        # glClearStencil(0)
        # glClearDepth(1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = float(size.GetWidth()) / float(size.GetHeight())
        gluPerspective(45.0, aspect, 1.0, numpy.max(self._machine_size) * 4)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glBegin(GL_QUADS)
        glColor3f(0.6, 0.6, 0.6)
        glVertex3f(-1, -1, -1)
        glVertex3f(1, -1, -1)
        glColor3f(0, 0, 0)
        glVertex3f(1, 1, -1)
        glVertex3f(-1, 1, -1)
        glEnd()

        glClear(GL_DEPTH_BUFFER_BIT)
        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    def on_paint(self, e):
        if self._anim_view is not None:
            self._view_target = self._anim_view.get_position()
            if self._anim_view.is_done():
                self._anim_view = None
        if self._anim_zoom is not None:
            self._zoom = self._anim_zoom.get_position()
            if self._anim_zoom.is_done():
                self._anim_zoom = None
        if self._object_shader is None:  # TODO: add loading shaders from file(s)
            if opengl_helpers.has_shader_support():
                self._object_shader = opengl_helpers.GLShader(
                    """
                    varying float light_amount;

                    void main(void)
                    {
                        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                        gl_FrontColor = gl_Color;

                        light_amount = abs(dot(normalize(gl_NormalMatrix * gl_Normal),
                            normalize(gl_LightSource[0].position.xyz)));
                        light_amount += 0.2;
                    }
                    """,
                    """
                    varying float light_amount;

                    void main(void)
                    {
                        gl_FragColor = vec4(gl_Color.xyz * light_amount, gl_Color[3]);
                    }
                    """)
                self._object_shader_no_light = opengl_helpers.GLShader(
                    """
                    varying float light_amount;

                    void main(void)
                    {
                        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                        gl_FrontColor = gl_Color;

                        light_amount = 1.0;
                    }
                    """,
                    """
                    varying float light_amount;

                    void main(void)
                    {
                        gl_FragColor = vec4(gl_Color.xyz * light_amount, gl_Color[3]);
                    }
                    """)
                self._object_load_shader = opengl_helpers.GLShader(
                    """
                    uniform float intensity;
                    uniform float scale;
                    varying float light_amount;

                    void main(void)
                    {
                        vec4 tmp = gl_Vertex;
                        tmp.x += sin(tmp.z/5.0+intensity*30.0) * scale * intensity;
                        tmp.y += sin(tmp.z/3.0+intensity*40.0) * scale * intensity;
                        gl_Position = gl_ModelViewProjectionMatrix * tmp;
                        gl_FrontColor = gl_Color;

                        light_amount = abs(dot(normalize(gl_NormalMatrix * gl_Normal),
                            normalize(gl_LightSource[0].position.xyz)));
                        light_amount += 0.2;
                    }
                    """,
                    """
                    uniform float intensity;
                    varying float light_amount;

                    void main(void)
                    {
                        gl_FragColor = vec4(gl_Color.xyz * light_amount, 1.0-intensity);
                    }
                    """)
            if self._object_shader is None or not self._object_shader.is_valid():
                # Could not make shader.
                self._object_shader = opengl_helpers.GLFakeShader()
                self._object_load_shader = None

        self._init_3d_view()
        glTranslate(0, 0, -self._zoom)
        glRotate(-self._pitch, 1, 0, 0)
        glRotate(self._yaw, 0, 0, 1)
        glTranslate(-self._view_target[0], -self._view_target[1], -
                    self._view_target[2] - self._z_offset)

        self._viewport = glGetIntegerv(GL_VIEWPORT)
        self._model_matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        self._proj_matrix = glGetDoublev(GL_PROJECTION_MATRIX)

        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        if self._mouse_x > -1:  # mouse has not passed over the opengl window.
            glFlush()
            # n = glReadPixels(self._mouse_x, self.GetSize().GetHeight() - 1 -
            #                  self._mouse_y, 1, 1, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8)[0][0] >> 8
            f = glReadPixels(self._mouse_x, self.GetSize().GetHeight() - 1 -
                             self._mouse_y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
            # self.GetTopLevelParent().SetTitle(hex(n) + " " + str(f))
            self._mouse_3d_pos = opengl_helpers.unproject(
                self._mouse_x, self._viewport[1] + self._viewport[3] - self._mouse_y,
                f, self._model_matrix, self._proj_matrix, self._viewport)
            self._mouse_3d_pos -= self._view_target
            self._mouse_3d_pos[2] -= self._z_offset

        self._init_3d_view()
        glTranslate(0, 0, -self._zoom)
        glRotate(-self._pitch, 1, 0, 0)
        glRotate(self._yaw, 0, 0, 1)
        glTranslate(-self._view_target[0], -self._view_target[1], -
                    self._view_target[2] - self._z_offset)

        glStencilFunc(GL_ALWAYS, 1, 1)
        glStencilOp(GL_INCR, GL_INCR, GL_INCR)

        if self._object is not None:

            if self._object.is_point_cloud() and opengl_helpers.has_shader_support():
                self._object_shader_no_light.bind()
            else:
                self._object_shader.bind()

            brightness = 1.0
            glStencilOp(GL_INCR, GL_INCR, GL_INCR)
            glEnable(GL_STENCIL_TEST)
            self._render_object(self._object, brightness)

            glDisable(GL_STENCIL_TEST)
            glDisable(GL_BLEND)
            glEnable(GL_DEPTH_TEST)
            glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

            if self._object.is_point_cloud() and opengl_helpers.has_shader_support():
                self._object_shader_no_light.unbind()
            else:
                self._object_shader.unbind()

        self._draw_machine()

    def _render_object(self, obj, brightness=0):
        glPushMatrix()
        glTranslate(obj.get_position()[0], obj.get_position()[1], obj.get_size()[2] / 2)

        if self.temp_matrix is not None:
            glMultMatrixf(opengl_helpers.convert_3x3_matrix_to_4x4(self.temp_matrix))

        offset = obj.get_draw_offset()
        glTranslate(-offset[0], -offset[1], -offset[2] - obj.get_size()[2] / 2)

        glMultMatrixf(opengl_helpers.convert_3x3_matrix_to_4x4(obj.get_matrix()))

        if obj.is_point_cloud():
            if obj._mesh is not None:
                if obj._mesh.vbo is None or obj._mesh.vertex_count > obj._mesh.vbo._size:
                    if obj._mesh.vbo is not None:
                        obj._mesh.vbo.release()
                    obj._mesh.vbo = opengl_helpers.GLVBO(
                        GL_POINTS,
                        obj._mesh.vertexes[:obj._mesh.vertex_count],
                        color_array=obj._mesh.colors[:obj._mesh.vertex_count],
                        point_size=self._point_size)
                obj._mesh.vbo.render()
        else:
            if obj._mesh is not None:
                if obj._mesh.vbo is None:
                    obj._mesh.vbo = opengl_helpers.GLVBO(
                        GL_TRIANGLES,
                        obj._mesh.vertexes[:obj._mesh.vertex_count],
                        obj._mesh.normal[:obj._mesh.vertex_count])
                if brightness != 0:
                    glColor4fv(map(lambda idx: idx * brightness, self._obj_color))
                obj._mesh.vbo.render()
        glPopMatrix()

    def _draw_machine(self):
        glEnable(GL_BLEND)
        machine_model_path = profile.settings['machine_model_path']
        glEnable(GL_CULL_FACE)

        # Draw Platform
        if machine_model_path in self._platform_mesh:
            try:  # TODO: Fix this. If not in the Scanning workbench, _draw_machine() fails.
                self._platform_mesh[machine_model_path]._mesh.vbo.release()
            except:
                pass

        mesh = mesh_loader.load_mesh(machine_model_path)
        if mesh is not None:
            self._platform_mesh[machine_model_path] = mesh
        else:
            self._platform_mesh[machine_model_path] = None
        self._platform_mesh[machine_model_path]._draw_offset = numpy.array(
            [0, 0, 8.05], numpy.float32)
        glColor4f(0.6, 0.6, 0.6, 0.5)
        self._object_shader.bind()
        self._render_object(self._platform_mesh[machine_model_path])
        self._object_shader.unbind()
        glDisable(GL_CULL_FACE)

        glDepthMask(False)

        machine_shape = profile.settings['machine_shape']

        if machine_shape == 'Circular':
            size = numpy.array([profile.settings['roi_diameter'],
                                profile.settings['roi_diameter'],
                                profile.settings['roi_height']], numpy.float32)
        elif machine_shape == 'Rectangular':
            size = numpy.array([profile.settings['roi_width'],
                                profile.settings['roi_depth'],
                                profile.settings['roi_height']], numpy.float32)

        if self._view_roi:
            polys = profile.get_size_polygons(size, machine_shape)
            height = profile.settings['roi_height']

            # Draw the sides of the build volume.
            glBegin(GL_QUADS)
            for n in xrange(0, len(polys[0])):
                if machine_shape == 'Rectangular':
                    if n % 2 == 0:
                        glColor4ub(5, 171, 231, 96)
                    else:
                        glColor4ub(5, 171, 231, 64)
                elif machine_shape == 'Circular':
                    glColor4ub(5, 171, 231, 96)
                    # glColor4ub(200, 200, 200, 150)

                glVertex3f(polys[0][n][0], polys[0][n][1], height)
                glVertex3f(polys[0][n][0], polys[0][n][1], 0)
                glVertex3f(polys[0][n - 1][0], polys[0][n - 1][1], 0)
                glVertex3f(polys[0][n - 1][0], polys[0][n - 1][1], height)
            glEnd()

            # Draw bottom and top of build volume.
            glColor4ub(5, 171, 231, 150)  # 128)
            # glColor4ub(200, 200, 200, 200)
            glBegin(GL_TRIANGLE_FAN)
            for p in polys[0][::-1]:
                glVertex3f(p[0], p[1], 0)
            glEnd()
            glBegin(GL_TRIANGLE_FAN)
            for p in polys[0][::-1]:
                glVertex3f(p[0], p[1], height)
            glEnd()

            quadric = gluNewQuadric()
            gluQuadricNormals(quadric, GLU_SMOOTH)
            gluQuadricTexture(quadric, GL_TRUE)
            glColor4ub(0, 100, 200, 150)

            gluCylinder(quadric, 6, 6, 1, 32, 16)
            gluDisk(quadric, 0.0, 6, 32, 1)

            glTranslate(0, 0, height - 1)
            gluDisk(quadric, 0.0, 6, 32, 1)
            gluCylinder(quadric, 6, 6, 1, 32, 16)
            glTranslate(0, 0, -height + 1)

        polys = profile.get_machine_size_polygons(profile.settings["machine_shape"])

        # Draw checkerboard
        if self._platform_texture is None:
            self._platform_texture = opengl_helpers.load_gl_texture('checkerboard.png')
            glBindTexture(GL_TEXTURE_2D, self._platform_texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glColor4f(1, 1, 1, 0.5)
        glBindTexture(GL_TEXTURE_2D, self._platform_texture)
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_TRIANGLE_FAN)
        for p in polys[0]:
            glTexCoord2f(p[0] / 20, p[1] / 20)
            glVertex3f(p[0], p[1], 0)
        glEnd()
        glDisable(GL_TEXTURE_2D)

        glDepthMask(True)
        glDisable(GL_BLEND)

# TODO: Remove this or put it in a seperate file


class ShaderEditor(wx.Dialog):

    def __init__(self, parent, callback, v, f):
        super(ShaderEditor, self).__init__(
            parent, title="Shader editor", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self._callback = callback
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)
        self._vertex = wx.TextCtrl(self, -1, v, style=wx.TE_MULTILINE)
        self._fragment = wx.TextCtrl(self, -1, f, style=wx.TE_MULTILINE)
        s.Add(self._vertex, 1, flag=wx.EXPAND)
        s.Add(self._fragment, 1, flag=wx.EXPAND)

        self._vertex.Bind(wx.EVT_TEXT, self.OnText, self._vertex)
        self._fragment.Bind(wx.EVT_TEXT, self.OnText, self._fragment)

        self.SetPosition(self.GetParent().GetPosition())
        self.SetSize((self.GetSize().GetWidth(), self.GetParent().GetSize().GetHeight()))
        self.Show()

    def OnText(self, e):
        self._callback(self._vertex.GetValue(), self._fragment.GetValue())
