# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx

from horus.gui.util.imageView import VideoView

class WizardPage(wx.Panel):
	def __init__(self, parent, title="Title", buttonPrevCallback=None, buttonNextCallback=None):
		wx.Panel.__init__(self, parent)

		self.title = title
		self.panel = wx.Panel(self)

		self.enableNext = True

		self.buttonPrevCallback = buttonPrevCallback
		self.buttonSkipCallback = buttonNextCallback
		self.buttonNextCallback = buttonNextCallback

		self.videoView = VideoView(self, size=(300, 400))
		self.videoView.SetBackgroundColour(wx.BLACK)
		self.prevButton = wx.Button(self, label=_("Prev"))
		self.skipButton = wx.Button(self, label=_("Skip"))
		self.nextButton = wx.Button(self, label=_("Next"))

	def intialize(self, pages):
		self.breadcrumbs = Breadcrumbs(self, pages)

		#-- Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.breadcrumbs, 0, wx.ALL^wx.TOP|wx.EXPAND, 10)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.panel, 1, wx.RIGHT|wx.EXPAND, 10)
		hbox.Add(self.videoView, 0, wx.ALL, 0)
		vbox.Add(hbox, 1, wx.ALL|wx.EXPAND, 20)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.prevButton, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 2)
		hbox.Add((0, 0), 1, wx.EXPAND)
		hbox.Add(self.skipButton, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 2)
		hbox.Add(self.nextButton, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 2)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 10)

		self.SetSizer(vbox)

		#-- Events
		self.prevButton.Bind(wx.EVT_BUTTON, self._onPrevButtonPressed)
		self.skipButton.Bind(wx.EVT_BUTTON, self._onSkipButtonPressed)
		self.nextButton.Bind(wx.EVT_BUTTON, self._onNextButtonPressed)

		self.Layout()

	def addToPanel(self, _object, _size):
		if _object is not None:
			self.panelBox.Add(_object, _size, wx.ALL|wx.EXPAND, 3)

	def _onPrevButtonPressed(self, event):
		if self.buttonPrevCallback is not None:
			self.buttonPrevCallback()

	def _onSkipButtonPressed(self, event):
		if self.buttonSkipCallback is not None:
			self.buttonSkipCallback()

	def _onNextButtonPressed(self, event):
		if self.buttonNextCallback is not None:
			self.buttonNextCallback()


class Breadcrumbs(wx.Panel):
	def __init__(self, parent, pages=[]):
		wx.Panel.__init__(self, parent)

		self.pages = pages

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		for page in self.pages:
			title = wx.StaticText(self, label=page.title)
			title.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
			if self.GetParent().title == page.title:
				title.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
			else:
				title.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_LIGHT)))
			title.Bind(wx.EVT_LEFT_UP, self.onTitlePressed)
			hbox.Add(title, 0, wx.ALL|wx.EXPAND, 0)
			if page is not pages[-1]:
				line = wx.StaticText(self, label="  .....................  ")
				line.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_LIGHT)))
				hbox.Add(line, 0, wx.ALL|wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.ALL|wx.CENTER, 0)

		self.SetSizer(vbox)
		self.Layout()

	def onTitlePressed(self, event):
		label = event.GetEventObject().GetLabel()
		for page in self.pages:
			if page.enableNext:
				if page.title == label:
					page.Show()
				else:
					page.Hide()
			else:
				break

		self.GetParent().GetParent().Layout()