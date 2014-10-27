#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
# Copyright (C) 2013 David Braam from Cura Project                      #
#                                                                       #
# Date: June 2014                                                       #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>                    #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
# GNU General Public License for more details.                          #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>.  #
#                                                                       #
#-----------------------------------------------------------------------#

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v3 http://www.gnu.org/licenses/gpl.html"

import wx
import traceback
import sys
import os
import time

from wx import glcanvas
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *

from horus.gui.util import openglHelpers

class animation(object):
	def __init__(self, gui, start, end, runTime):
		self._start = start
		self._end = end
		self._startTime = time.time()
		self._runTime = runTime
		gui._animationList.append(self)

	def isDone(self):
		return time.time() > self._startTime + self._runTime

	def getPosition(self):
		if self.isDone():
			return self._end
		f = (time.time() - self._startTime) / self._runTime
		ts = f*f
		tc = f*f*f
		#f = 6*tc*ts + -15*ts*ts + 10*tc
		f = tc + -3*ts + 3*f
		return self._start + (self._end - self._start) * f

class glGuiControl(object):
	def __init__(self, parent, pos):
		self._parent = parent
		self._base = parent._base
		self._pos = pos
		self._size = (0,0, 1, 1)
		self._parent.add(self)

	def setSize(self, x, y, w, h):
		self._size = (x, y, w, h)

	def getSize(self):
		return self._size

	def getMinSize(self):
		return 1, 1

	def updateLayout(self):
		pass

	def focusNext(self):
		for n in xrange(self._parent._glGuiControlList.index(self) + 1, len(self._parent._glGuiControlList)):
			if self._parent._glGuiControlList[n].setFocus():
				return
		for n in xrange(0, self._parent._glGuiControlList.index(self)):
			if self._parent._glGuiControlList[n].setFocus():
				return

	def focusPrevious(self):
		for n in xrange(self._parent._glGuiControlList.index(self) -1, -1, -1):
			if self._parent._glGuiControlList[n].setFocus():
				return
		for n in xrange(len(self._parent._glGuiControlList) - 1, self._parent._glGuiControlList.index(self), -1):
			if self._parent._glGuiControlList[n].setFocus():
				return

	def setFocus(self):
		return False

	def hasFocus(self):
		return self._base._focus == self

	def OnMouseUp(self, x, y):
		pass

	def OnKeyDown(self, key):
		pass

	def OnKeyUp(self, key):
		pass

class glGuiContainer(glGuiControl):
	def __init__(self, parent, pos):
		self._glGuiControlList = []
		glGuiLayoutButtons(self)
		super(glGuiContainer, self).__init__(parent, pos)

	def add(self, ctrl):
		self._glGuiControlList.append(ctrl)
		self.updateLayout()

	def OnMouseDown(self, x, y, button):
		for ctrl in self._glGuiControlList:
			if ctrl.OnMouseDown(x, y, button):
				return True
		return False

	def OnMouseUp(self, x, y):
		for ctrl in self._glGuiControlList:
			if ctrl.OnMouseUp(x, y):
				return True
		return False

	def OnMouseMotion(self, x, y):
		handled = False
		for ctrl in self._glGuiControlList:
			if ctrl.OnMouseMotion(x, y):
				handled = True
		return handled

	def draw(self):
		for ctrl in self._glGuiControlList:
			ctrl.draw()

	def updateLayout(self):
		self._layout.update()
		for ctrl in self._glGuiControlList:
			ctrl.updateLayout()

class glGuiPanel(glcanvas.GLCanvas):
	def __init__(self, parent):
		attribList = (glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 24, glcanvas.WX_GL_STENCIL_SIZE, 8, 0)
		glcanvas.GLCanvas.__init__(self, parent, style=wx.WANTS_CHARS, attribList = attribList)
		self._base = self
		self._focus = None
		self._container = None
		self._container = glGuiContainer(self, (0,0))
		self._shownError = False

		self._context = glcanvas.GLContext(self)
		#self._glButtonsTexture = None
		self._buttonSize = 64

		self._animationList = []
		self.glReleaseList = []
		self._refreshQueued = False
		self._idleCalled = False

		wx.EVT_PAINT(self, self._OnGuiPaint)
		wx.EVT_SIZE(self, self._OnSize)
		wx.EVT_ERASE_BACKGROUND(self, self._OnEraseBackground)
		wx.EVT_LEFT_DOWN(self, self._OnGuiMouseDown)
		wx.EVT_LEFT_DCLICK(self, self._OnGuiMouseDown)
		wx.EVT_LEFT_UP(self, self._OnGuiMouseUp)
		wx.EVT_RIGHT_DOWN(self, self._OnGuiMouseDown)
		wx.EVT_RIGHT_DCLICK(self, self._OnGuiMouseDown)
		wx.EVT_RIGHT_UP(self, self._OnGuiMouseUp)
		wx.EVT_MIDDLE_DOWN(self, self._OnGuiMouseDown)
		wx.EVT_MIDDLE_DCLICK(self, self._OnGuiMouseDown)
		wx.EVT_MIDDLE_UP(self, self._OnGuiMouseUp)
		wx.EVT_MOTION(self, self._OnGuiMouseMotion)
		wx.EVT_KEY_DOWN(self, self._OnGuiKeyDown)
		wx.EVT_KEY_UP(self, self._OnGuiKeyUp)
		wx.EVT_KILL_FOCUS(self, self.OnFocusLost)
		wx.EVT_IDLE(self, self._OnIdle)

	def _OnIdle(self, e):
		self._idleCalled = True
		if len(self._animationList) > 0 or self._refreshQueued:
			self._refreshQueued = False
			for anim in self._animationList:
				if anim.isDone():
					self._animationList.remove(anim)
			self.Refresh()

	def _OnGuiKeyUp(self, e):
		if self._focus is not None:
			self._focus.OnKeyUp(e.GetKeyCode())
			self.Refresh()
		else:
			self.OnKeyUp(e.GetKeyCode())

	def _OnGuiKeyDown(self, e):
		if self._focus is not None:
			self._focus.OnKeyDown(e.GetKeyCode())
			self.Refresh()
		else:
			self.OnKeyDown(e.GetKeyCode())

	def OnFocusLost(self, e):
		self._focus = None
		self.Refresh()

	def _OnGuiMouseDown(self,e):
		self.SetFocus()
		if self._container.OnMouseDown(e.GetX(), e.GetY(), e.GetButton()):
			self.Refresh()
			return
		self.OnMouseDown(e)

	def _OnGuiMouseUp(self, e):
		if self._container.OnMouseUp(e.GetX(), e.GetY()):
			self.Refresh()
			return
		self.OnMouseUp(e)

	def _OnGuiMouseMotion(self,e):
		self.Refresh()
		if not self._container.OnMouseMotion(e.GetX(), e.GetY()):
			self.OnMouseMotion(e)

	def _OnGuiPaint(self, e):
		self._idleCalled = False
		h = self.GetSize().GetHeight()
		w = self.GetSize().GetWidth()
		oldButtonSize = self._buttonSize
		if h / 3 < w / 4:
			w = h * 4 / 3
		if w < 64 * 8:
			self._buttonSize = 32
		elif w < 64 * 10:
			self._buttonSize = 48
		elif w < 64 * 15:
			self._buttonSize = 64
		elif w < 64 * 20:
			self._buttonSize = 80
		else:
			self._buttonSize = 96
		if self._buttonSize != oldButtonSize:
			self._container.updateLayout()

		dc = wx.PaintDC(self)
		try:
			self.SetCurrent(self._context)
			for obj in self.glReleaseList:
				obj.release()
			del self.glReleaseList[:]
			renderStartTime = time.time()
			self.OnPaint(e)
			self._drawGui()
			glFlush()
			self.SwapBuffers()
		except:
			# When an exception happens, catch it and show a message box. If the exception is not caught the draw function bugs out.
			# Only show this exception once so we do not overload the user with popups.
			errStr = _("An error has occurred during the 3D view drawing.")
			tb = traceback.extract_tb(sys.exc_info()[2])
			errStr += "\n%s: '%s'" % (str(sys.exc_info()[0].__name__), str(sys.exc_info()[1]))
			for n in xrange(len(tb)-1, -1, -1):
				locationInfo = tb[n]
				errStr += "\n @ %s:%s:%d" % (os.path.basename(locationInfo[0]), locationInfo[2], locationInfo[1])
			if not self._shownError:
				traceback.print_exc()
				wx.CallAfter(wx.MessageBox, errStr, _("3D window error"), wx.OK | wx.ICON_EXCLAMATION)
				self._shownError = True

	def _drawGui(self):
		#if self._glButtonsTexture is None:
			#self._glButtonsTexture = openglHelpers.loadGLTexture('glButtons.png')

		glDisable(GL_DEPTH_TEST)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glDisable(GL_LIGHTING)
		glColor4ub(255,255,255,255)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		size = self.GetSize()
		glOrtho(0, size.GetWidth()-1, size.GetHeight()-1, 0, -1000.0, 1000.0)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		self._container.draw()

		# glBindTexture(GL_TEXTURE_2D, self._glRobotTexture)
		# glEnable(GL_TEXTURE_2D)
		# glPushMatrix()
		# glColor4f(1,1,1,1)
		# glTranslate(size.GetWidth(),size.GetHeight(),0)
		# s = self._buttonSize * 1
		# glScale(s,s,s)
		# glTranslate(-1.2,-0.2,0)
		# glBegin(GL_QUADS)
		# glTexCoord2f(1, 0)
		# glVertex2f(0,-1)
		# glTexCoord2f(0, 0)
		# glVertex2f(-1,-1)
		# glTexCoord2f(0, 1)
		# glVertex2f(-1, 0)
		# glTexCoord2f(1, 1)
		# glVertex2f(0, 0)
		# glEnd()
		# glDisable(GL_TEXTURE_2D)
		# glPopMatrix()

	def _OnEraseBackground(self,event):
		#Workaround for windows background redraw flicker.
		pass

	def _OnSize(self,e):
		self._container.setSize(0, 0, self.GetSize().GetWidth(), self.GetSize().GetHeight())
		self._container.updateLayout()
		self.Refresh()

	def OnMouseDown(self,e):
		pass
	def OnMouseUp(self,e):
		pass
	def OnMouseMotion(self, e):
		pass
	def OnPaint(self, e):
		pass

	def QueueRefresh(self):
		wx.CallAfter(self._queueRefresh)

	def _queueRefresh(self):
		if self._idleCalled:
			wx.CallAfter(self.Refresh)
		else:
			self._refreshQueued = True

	def add(self, ctrl):
		if self._container is not None:
			self._container.add(ctrl)

class glGuiLayoutButtons(object):
	def __init__(self, parent):
		self._parent = parent
		self._parent._layout = self

	def update(self):
		bs = self._parent._base._buttonSize
		x0, y0, w, h = self._parent.getSize()
		gridSize = bs * 1.0
		for ctrl in self._parent._glGuiControlList:
			pos = ctrl._pos
			if pos[0] < 0:
				x = w + pos[0] * gridSize - bs * 0.2
			else:
				x = pos[0] * gridSize + bs * 0.2
			if pos[1] < 0:
				y = h + pos[1] * gridSize * 1.2 - bs * 0.0
			else:
				y = pos[1] * gridSize * 1.2 + bs * 0.2
			ctrl.setSize(x, y, gridSize, gridSize)

	def getLayoutSize(self):
		_, _, w, h = self._parent.getSize()
		return w, h