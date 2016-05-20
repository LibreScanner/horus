# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.\
                 Copyright (C) 2013 David Braam from Cura Project'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx
import numpy

from horus.util.resources import get_path_for_image

import OpenGL

OpenGL.ERROR_CHECKING = False
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GL import shaders

import logging
logger = logging.getLogger(__name__)

from sys import platform as _platform
if _platform != 'darwin':
    glutInit()  # Hack; required before glut can be called. Not required for all OS.


class GLReferenceCounter(object):

    def __init__(self):
        self._ref_counter = 1

    def inc_ref(self):
        self._ref_counter += 1

    def dec_ref(self):
        self._ref_counter -= 1
        return self._ref_counter <= 0


def has_shader_support():
    if bool(glCreateShader):
        return True
    return False


class GLShader(GLReferenceCounter):

    def __init__(self, vertex_program, fragment_program):
        super(GLShader, self).__init__()
        self._vertex_program = vertex_program
        self._fragment_program = fragment_program
        try:
            vertex_shader = shaders.compileShader(vertex_program, GL_VERTEX_SHADER)
            fragment_shader = shaders.compileShader(fragment_program, GL_FRAGMENT_SHADER)

            # shader.compileProgram tries to return the shader program as a overloaded int.
            # But the return value of a shader does not always fit in a int (needs to be a long).
            # So we do raw OpenGL calls.
            # This is to ensure that this works on intel GPU's
            # self._program = shaders.compileProgram(self._vertexProgram, self._fragmentProgram)
            self._program = glCreateProgram()
            glAttachShader(self._program, vertex_shader)
            glAttachShader(self._program, fragment_shader)
            glLinkProgram(self._program)
            # Validation has to occur *after* linking
            glValidateProgram(self._program)
            if glGetProgramiv(self._program, GL_VALIDATE_STATUS) == GL_FALSE:
                raise RuntimeError("Validation failure: %s" % (glGetProgramInfoLog(self._program)))
            if glGetProgramiv(self._program, GL_LINK_STATUS) == GL_FALSE:
                raise RuntimeError("Link failure: %s" % (glGetProgramInfoLog(self._program)))
            glDeleteShader(vertex_shader)
            glDeleteShader(fragment_shader)
        except RuntimeError, e:
            logger.error(str(e))
            self._program = None

    def bind(self):
        if self._program is not None:
            shaders.glUseProgram(self._program)

    def unbind(self):
        shaders.glUseProgram(0)

    def release(self):
        if self._program is not None:
            glDeleteProgram(self._program)
            self._program = None

    def set_uniform(self, name, value):
        if self._program is not None:
            if type(value) is float:
                glUniform1f(glGetUniformLocation(self._program, name), value)
            elif type(value) is numpy.matrix:
                glUniformMatrix3fv(
                    glGetUniformLocation(self._program, name), 1, False,
                    value.getA().astype(numpy.float32))
            else:
                logger.warning('Unknown type for setUniform: %s' % (str(type(value))))

    def is_valid(self):
        return self._program is not None

    def get_vertex_shader(self):
        return self._vertex_string

    def get_fragment_shader(self):
        return self._fragment_string

    def __del__(self):
        if self._program is not None and bool(glDeleteProgram):
            logger.warning("Shader was not properly released!")


class GLFakeShader(GLReferenceCounter):
    """
    A Class that acts as an OpenGL shader, but in reality is not one.
    Used if shaders are not supported.
    """

    def __init__(self):
        super(GLFakeShader, self).__init__()

    def bind(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0, 0, 0, 0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0, 0, 0, 0])

    def unbind(self):
        glDisable(GL_LIGHTING)

    def release(self):
        pass

    def set_uniform(self, name, value):
        pass

    def isValid(self):
        return True

    def get_vertex_shader(self):
        return ''

    def get_fragment_shader(self):
        return ''


class GLVBO(GLReferenceCounter):
    """
    Vertex buffer object. Used for faster rendering.
    """

    def __init__(self, render_type, vertex_array,
                 normal_array=None, indices_array=None, color_array=None, point_size=2):
        super(GLVBO, self).__init__()
        self._render_type = render_type
        self._point_size = point_size
        if not bool(glGenBuffers):  # Fallback if buffers are not supported.
            self._vertex_array = vertex_array
            self._normal_array = normal_array
            self._indices_array = indices_array
            self._color_array = color_array
            self._size = len(vertex_array)
            self._buffer = None
            self._has_normals = self._normal_array is not None
            self._has_indices = self._indices_array is not None
            self._has_color = self._color_array is not None
            if self._has_indices:
                self._size = len(indices_array)
        else:
            self._size = len(vertex_array)
            self._has_normals = normal_array is not None
            self._has_indices = indices_array is not None
            self._has_color = color_array is not None
            if self._has_normals:  # TODO: Add size check to see if arrays have same size.
                self._buffer = glGenBuffers(1)
                glBindBuffer(GL_ARRAY_BUFFER, self._buffer)
                glBufferData(GL_ARRAY_BUFFER, numpy.concatenate(
                    (vertex_array, normal_array), 1), GL_STATIC_DRAW)
            else:
                if self._has_color:
                    glPointSize(self._point_size)
                    self._buffer = glGenBuffers(2)
                    glBindBuffer(GL_ARRAY_BUFFER, self._buffer[0])
                    glBufferData(GL_ARRAY_BUFFER, vertex_array, GL_STATIC_DRAW)
                    glBindBuffer(GL_ARRAY_BUFFER, self._buffer[1])
                    glBufferData(
                        GL_ARRAY_BUFFER, numpy.array(color_array, numpy.uint8), GL_STATIC_DRAW)
                else:
                    self._buffer = glGenBuffers(1)
                    glBindBuffer(GL_ARRAY_BUFFER, self._buffer)
                    glBufferData(GL_ARRAY_BUFFER, vertex_array, GL_STATIC_DRAW)

            glBindBuffer(GL_ARRAY_BUFFER, 0)
            if self._has_indices:
                self._size = len(indices_array)
                self._buffer_indices = glGenBuffers(1)
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._buffer_indices)
                glBufferData(GL_ELEMENT_ARRAY_BUFFER, numpy.array(
                    indices_array, numpy.uint32), GL_STATIC_DRAW)

    def render(self):
        glEnableClientState(GL_VERTEX_ARRAY)
        if self._buffer is None:
            glVertexPointer(3, GL_FLOAT, 0, self._vertex_array)
            if self._has_normals:
                glEnableClientState(GL_NORMAL_ARRAY)
                glNormalPointer(GL_FLOAT, 0, self._normal_array)
            if self._has_color:
                glEnableClientState(GL_COLOR_ARRAY)
                glColorPointer(3, GL_UNSIGNED_BYTE, 0, self._color_array)
        else:
            if self._has_normals:
                glBindBuffer(GL_ARRAY_BUFFER, self._buffer)
                glEnableClientState(GL_NORMAL_ARRAY)
                glVertexPointer(3, GL_FLOAT, 2 * 3 * 4, c_void_p(0))
                glNormalPointer(GL_FLOAT, 2 * 3 * 4, c_void_p(3 * 4))
            else:
                if self._has_color:
                    glEnableClientState(GL_COLOR_ARRAY)
                    glBindBuffer(GL_ARRAY_BUFFER, self._buffer[1])
                    glColorPointer(3, GL_UNSIGNED_BYTE, 0, None)
                    glBindBuffer(GL_ARRAY_BUFFER, self._buffer[0])
                    glVertexPointer(3, GL_FLOAT, 0, None)
                else:
                    glBindBuffer(GL_ARRAY_BUFFER, self._buffer)
                    glVertexPointer(3, GL_FLOAT, 3 * 4, c_void_p(0))

            if self._has_indices:
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._buffer_indices)

        if self._has_indices:
            if self._buffer is None:
                glDrawElements(self._render_type, self._size, GL_UNSIGNED_INT, self._indices_array)
            else:
                glDrawElements(self._render_type, self._size, GL_UNSIGNED_INT, c_void_p(0))
        else:
            # Warning, batch_size needs to be dividable by 4 (quads), 3 (triangles) and
            # 2 (lines). Current value is magic.
            batch_size = 996
            extra_start_pos = int(self._size / batch_size) * batch_size  # leftovers.
            extra_count = self._size - extra_start_pos
            for i in xrange(0, int(self._size / batch_size)):
                glDrawArrays(self._render_type, i * batch_size, batch_size)
            glDrawArrays(self._render_type, extra_start_pos, extra_count)

        if self._buffer is not None:
            glBindBuffer(GL_ARRAY_BUFFER, 0)
        if self._has_indices:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        if self._has_normals:
            glDisableClientState(GL_NORMAL_ARRAY)
        if self._has_color:
            glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

    def release(self):
        if self._buffer is not None:
            if self._has_color:
                glBindBuffer(GL_ARRAY_BUFFER, self._buffer[0])
                glBufferData(GL_ARRAY_BUFFER, None, GL_STATIC_DRAW)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glDeleteBuffers(1, [self._buffer[0]])
                glBindBuffer(GL_ARRAY_BUFFER, self._buffer[1])
                glBufferData(GL_ARRAY_BUFFER, None, GL_STATIC_DRAW)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glDeleteBuffers(1, [self._buffer[1]])
                self._buffer = None
            else:
                glBindBuffer(GL_ARRAY_BUFFER, self._buffer)
                glBufferData(GL_ARRAY_BUFFER, None, GL_STATIC_DRAW)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glDeleteBuffers(1, [self._buffer])
                self._buffer = None
            if self._has_indices:
                glBindBuffer(GL_ARRAY_BUFFER, self._buffer_indices)
                glBufferData(GL_ARRAY_BUFFER, None, GL_STATIC_DRAW)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glDeleteBuffers(1, [self._buffer_indices])
        self._vertex_array = None
        self._normal_array = None

    def __del__(self):
        if self._buffer is not None and bool(glDeleteBuffers):
            logger.warning("VBO was not properly released!")


def unproject(winx, winy, winz, model_matrix, proj_matrix, viewport):
    """
    Projects window position to 3D space. (gluUnProject).
    Reimplentation as some drivers crash with the original.
    """
    np_model_matrix = numpy.matrix(numpy.array(model_matrix, numpy.float64).reshape((4, 4)))
    np_proj_matrix = numpy.matrix(numpy.array(proj_matrix, numpy.float64).reshape((4, 4)))
    final_matrix = np_model_matrix * np_proj_matrix
    final_matrix = numpy.linalg.inv(final_matrix)

    viewport = map(float, viewport)
    if viewport[2] > 0 and viewport[3] > 0:
        vector = numpy.array([(winx - viewport[0]) / viewport[2] * 2.0 - 1.0,
                              (winy - viewport[1]) / viewport[3] * 2.0 - 1.0,
                              winz * 2.0 - 1.0, 1]).reshape((1, 4))
        vector = (numpy.matrix(vector) * final_matrix).getA().flatten()
        ret = list(vector)[0:3] / vector[3]
        return ret


def convert_3x3_matrix_to_4x4(matrix):
    return list(matrix.getA()[0]) + [0] + list(matrix.getA()[1]) + \
        [0] + list(matrix.getA()[2]) + [0, 0, 0, 0, 1]


def load_gl_texture(filename):
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    img = wx.ImageFromBitmap(wx.Bitmap(get_path_for_image(filename)))
    rgb_data = img.GetData()
    alpha_data = img.GetAlphaData()
    if alpha_data is not None:
        data = ''
        for i in xrange(0, len(alpha_data)):
            data += rgb_data[i * 3:i * 3 + 3] + alpha_data[i]
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.GetWidth(),
                     img.GetHeight(), 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    else:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.GetWidth(),
                     img.GetHeight(), 0, GL_RGB, GL_UNSIGNED_BYTE, rgb_data)
    return tex
