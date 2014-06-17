#!/usr/bin/python

import wx
import sys

from page import *
from workbench import *

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, pos=(150,150), size=(350,200))
	
	"""
	#-- Create Page
        page = Page(self, "Cancel", "Next")
        
	#-- Bing Page's Right Button
	rightButton = page.getRightButton()
	rightButton.Bind(wx.EVT_BUTTON, self.OnClose)

	#-- Set Static Text to Page's Panel
	panel = page.getPanel()
	wx.StaticText(panel, -1, "Text Here", style=wx.ALIGN_CENTRE)
	"""
	
	wb = Workbench(self)

	t = wb.getToolbar()
	t.AddLabelTool(wx.ID_EXIT, '', wx.Bitmap('texit.png'))
        t.Realize()

	panel = wb.getLeftPanel()
	wx.StaticText(panel, -1, "Hola")

    def OnClose(self, event):
        self.Destroy()

app = wx.App()
top = Frame()
top.Show()
app.MainLoop()
