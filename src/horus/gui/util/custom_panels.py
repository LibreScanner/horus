# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
from collections import OrderedDict

from horus.util import profile, resources


class ExpandableCollection(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.expandable_panels = OrderedDict()

        # Layout
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vbox)
        self.Layout()

    def add_panel(self, name, panel):
        self.expandable_panels.update({name: panel(self, expand_callback=self._expand_callback)})
        self.vbox.Add(panel, 0, wx.EXPAND, 0)

    def _expand_callback(self, selected_panel):
        for panel in self.expandable_panels.values():
            panel.hide_content()
        selected_panel.show_content()
        self.Layout()
        self.GetParent().Layout()
        self.GetParent().GetParent().Layout()

    def update_callbacks(self):
        for panel in self.panels.values():
            panel.update_callbacks()

    def enable_content(self):
        for panel in self.panels.values():
            panel.enable_content()

    def disable_content(self):
        for panel in self.panels.values():
            panel.disable_content()

    def update_profile(self):
        for panel in self.panels.values():
            panel.update_profile()

    def enable_restore(self, value):
        for panel in self.panels.values():
            panel.enable_restore(value)


class ExpandablePanel(wx.Panel):

    def __init__(self, parent, title="", callback=None, has_undo=True, has_restore=True):
        wx.Panel.__init__(self, parent, size=(-1, -1))

        # Elements
        self.undo_objects = []
        self.callback = callback
        self.title = title
        self.title_text = TitleText(self, title, bold=True)
        self.has_undo = has_undo
        self.has_restore = has_restore
        if self.has_undo:
            self.undo_button = wx.BitmapButton(
                self, wx.NewId(),
                wx.Bitmap(resources.get_path_for_image("undo.png"), wx.BITMAP_TYPE_ANY))
            self.undo_button.Disable()
        if self.has_restore:
            self.restore_button = wx.BitmapButton(
                self, wx.NewId(),
                wx.Bitmap(resources.get_path_for_image("restore.png"), wx.BITMAP_TYPE_ANY))
        self.content = ControlCollection(self)
        self.content.Hide()

        # Layout
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.title_text, 1, wx.ALIGN_CENTER_VERTICAL)
        if self.has_undo:
            self.hbox.Add(
                self.undo_button, 0, wx.RIGHT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        if self.has_restore:
            self.hbox.Add(
                self.restore_button, 0, wx.RIGHT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.vbox.Add(self.hbox, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)
        self.content_box = wx.BoxSizer(wx.VERTICAL)
        self.content.SetSizer(self.content_box)
        self.vbox.Add(self.content, 0, wx.ALL ^ wx.TOP ^ wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(self.vbox)
        self.Layout()

        # Events
        if self.has_undo:
            self.undo_button.Bind(wx.EVT_BUTTON, self.onUndoButtonClicked)
        if self.has_restore:
            self.restore_button.Bind(wx.EVT_BUTTON, self.onRestoreButtonClicked)

    def update_callbacks(self):
        pass

    def enable_content(self):
        self.content.Enable()

    def disable_content(self):
        self.content.Disable()

    def update_profile(self):
        pass

    def reset_profile(self):
        pass

    def updateProfile(self):
        pass

    def onUndoButtonClicked(self, event):
        if self.undo():
            self.undoButton.Enable()
        else:
            self.undoButton.Disable()

    def onRestoreButtonClicked(self, event):
        dlg = wx.MessageDialog(
            self,
            _("This will reset all section settings to defaults.\n"
              "Unless you have saved your current profile, all section settings will be lost!\n"
              "Do you really want to reset?"), self.title, wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            self.resetProfile()
            self.restoreButton.Disable()
            if self.has_undo:
                del self.undoObjects[:]
                self.undoButton.Disable()

    def appendUndo(self, _object):
        if self.has_undo:
            self.undoObjects.append(_object)

    def releaseUndo(self):
        if self.has_undo:
            self.undoButton.Enable()
        if self.has_restore:
            self.restoreButton.Enable()

    def undo(self):
        if len(self.undoObjects) > 0:
            objectToUndo = self.undoObjects.pop()
            objectToUndo.undo()
        return len(self.undoObjects) > 0

    def enableRestore(self, value):
        if hasattr(self, 'restoreButton'):
            if value:
                self.restoreButton.Enable()
            else:
                self.restoreButton.Disable()

    def show(self):
        if self.callback is not None:
            self.callback()
        self.content.Show()


class ControlCollection(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Elements
        self.control_panels = OrderedDict()

        self.append_undo_callback = None
        self.release_undo_callback = None

        # Layout
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vbox)
        self.Layout()

    def add_control(self, _type, _name, tooltip=None):
        control = _type(self, _name, tooltip)
        control.set_undo_callbacks(self.append_undo_callback, self.release_undo_callback)
        self.control_panels.update({_name: item})
        self.vbox.Add(item, 0, wx.BOTTOM | wx.EXPAND, 5)
        self.Layout()

    def update_callback(self, _name, _callback):
        self.control_panels[_name].set_engine_callback(_callback)

    def reset_profile(self):
        for control in self.control_panels.values():
            if control.IsEnabled():
                control.reset_profile()

    def enable(self, _name):
        self.items[_name].Enable()

    def disable(self, _name):
        self.items[_name].Disable()

    def updateProfile(self):
        for control in self.control_panels.values():
            control.update_profile()

    def set_undo_callbacks(self, append_undo_callback=None, release_undo_callback=None):
        self.append_undo_callback = append_undo_callback
        self.release_undo_callback = release_undo_callback

    def show_item(self, _name):
        self.control_panels[_name].Show()
        self.Layout()

    def hide_item(self, _name):
        self.control_panels[_name].Hide()
        self.Layout()


class TitleText(wx.Panel):

    def __init__(self, parent, title, bold=True, hand_cursor=True):
        wx.Panel.__init__(self, parent)

        # Elements
        self.title = wx.StaticText(self, label=title)
        if bold:
            font_weight = wx.FONTWEIGHT_BOLD
        else:
            font_weight = wx.FONTWEIGHT_NORMAL
        self.title.SetFont((wx.Font(wx.SystemSettings.GetFont(
            wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, font_weight)))
        self.line = wx.StaticLine(self)

        if hand_cursor:
            self.title.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
            self.line.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title, 0, wx.ALL ^ wx.BOTTOM | wx.EXPAND, 10)
        vbox.Add(self.line, 1, wx.ALL ^ wx.BOTTOM | wx.EXPAND, 5)
        self.SetSizer(vbox)
        self.Layout()


class ControlPanel(wx.Panel):
    def __init__(self, parent, name, engine_callback=None, tooltip=None):
        wx.Panel.__init__(self, parent)
        self.name = name
        self.engine_callback = engine_callback
        self.setting = profile.settings.get_setting(self.name)

        if tooltip is not None:
            self.SetToolTip(wx.ToolTip(tooltip))

        self.undo_values = []
        self.append_undo_callback = None
        self.release_undo_callback = None

    def set_engine_callback(self, engine_callback=None):
        self.engine_callback = engine_callback

    def set_undo_callbacks(self, append_undo_callback=None, release_undo_callback=None):
        self.append_undo_callback = append_undo_callback
        self.release_undo_callback = release_undo_callback

    def undo(self):
        if len(self.undo_values) > 0:
            value = self.undo_values.pop()
            self.execute(value)
            self.update_to_profile(value)

    def reset_profile(self):
        profile.settings.reset_to_default(self.name)
        value = profile.settings[self.name]
        self.execute(value)
        self.update_to_profile(value)
        del self.undo_values[:]

    def update(self, value):
        self.append_undo(value)
        self.execute(value)
        self.update_to_profile(value)

    def append_undo(self, value):
        self.undo_values.append(value)
        if self.append_undo_callback is not None:
            self.append_undo_callback()
        if self.release_undo_callback is not None:
            self.release_undo_callback()

    def update_to_profile(self, value):
        profile.settings[self.name] = value

    def execute(self, value):
        if self.engine_callback is not None:
            self.engine_callback(value)


class Slider(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        self.flag_first_move = True

        # Elements
        label = wx.StaticText(self, label=self.setting._label, size=(130, -1))
        self.control = wx.Slider(self, value=profile.settings[name],
                                 minValue=profile.settings.get_min_value(name),
                                 maxValue=profile.settings.get_max_value(name),
                                 size=(150, -1),
                                 style=wx.SL_LABELS)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.AddStretchSpacer()
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_COMMAND_SCROLL_LINEUP, self._on_slider)
        self.control.Bind(wx.EVT_COMMAND_SCROLL_LINEDOWN, self._on_slider)
        self.control.Bind(wx.EVT_SCROLL_THUMBRELEASE, self._on_slider_released)
        self.control.Bind(wx.EVT_SCROLL_THUMBTRACK, self._on_slider_tracked)

    def _on_slider(self, event):
        self.update(self.control.GetValue())

    def _on_slider_released(self, event):
        self.flag_first_move = True
        if self.release_undo_callback is not None:
            self.release_undo_callback()

    def _on_slider_tracked(self, event):
        self.update(self.control.GetValue())


class ComboBox(ControlPanel):

    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        choices = self.setting._possible_values
        _choices = [_(i) for i in choices]

        self.key_dict = dict(zip(_choices, choices))

        # Elements
        label = wx.StaticText(self, label=self.setting._label, size=(130, -1))
        self.control = wx.ComboBox(self, wx.ID_ANY,
                                   value=_(profile.settings[self.name]),
                                   choices=_choices,
                                   size=(150, -1),
                                   style=wx.CB_READONLY)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.AddStretchSpacer()
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_COMBOBOX, self._on_combo_box_changed)

    def _on_combo_box_changed(self, event):
        self.update(self.key_dict[self.control.GetValue()])


class CheckBox(ControlPanel):

    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, label=self.setting._label, size=(130, -1))
        self.control = wx.CheckBox(self, size=(150, -1))

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.AddStretchSpacer()
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_CHECKBOX, self._on_check_box_changed)

    def _on_check_box_changed(self, event):
        self.update(self.control.GetValue())


class RadioButton(ControlPanel):

    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, label=self.setting._label)
        self.control = wx.RadioButton(self, style=wx.ALIGN_RIGHT)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.TOP | wx.RIGHT | wx.EXPAND, 15)
        hbox.Add(self.control, 1, wx.TOP | wx.EXPAND, 16)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_RADIOBUTTON, self._on_radio_button_changed)

    def _on_radio_button_changed(self, event):
        self.update(self.control.GetValue())


class TextBox(ControlPanel):

    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, size=(140, -1), label=self.setting._label)
        self.control = wx.TextCtrl(self, size=(120, -1), style=wx.TE_RIGHT)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.AddStretchSpacer()
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_KILL_FOCUS, self._on_text_box_changed)

    def _on_text_box_changed(self, event):
        self.update(self.control.GetValue())


class FloatTextBox(ControlPanel):

    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, size=(140, -1), label=self.setting._label)
        self.control = wx.TextCtrl(self, size=(120, -1), style=wx.TE_RIGHT)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.AddStretchSpacer()
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_KILL_FOCUS, self._on_text_box_lost_focus)

    def _on_text_box_lost_focus(self, event):
        self.update(self.control.GetValue())


class FloatTextBoxArray(ControlPanel):

    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, size=(140, -1), label=self.setting._label)
        self.control = wx.TextCtrl(self, size=(120, -1), style=wx.TE_RIGHT)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.AddStretchSpacer()
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_KILL_FOCUS, self._on_text_box_lost_focus)

    def _on_text_box_lost_focus(self, event):
        self.update(self.control.GetValue())


class Button(ControlPanel):

    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        self.control = wx.Button(self, label=self.setting._label)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.control, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_BUTTON, self._on_button_clicked)

    def _on_button_clicked(self, event):
        if self.engine_callback is not None:
            self.engine_callback()


class CallbackButton(ControlPanel):

    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        self.control = wx.Button(self, label=self.setting._label)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.control, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_BUTTON, self._on_button_clicked)

    def _on_button_clicked(self, event):
        if self.engine_callback is not None:
            self.control.Disable()
            self.waitCursor = wx.BusyCursor()
            self.engine_callback(lambda r: wx.CallAfter(self._on_finish_callback, r))

    def _on_finish_callback(self, ret):
        self.control.Enable()
        if hasattr(self, 'waitCursor'):
            del self.waitCursor


class ToggleButton(ControlPanel):

    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        self.control = wx.ToggleButton(self, label=self.setting._label)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.control, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_TOGGLEBUTTON, self._on_button_toggle)

    def _on_button_toggle(self, event):
        if self.engine_callback is not None:
            if event.IsChecked():
                function = 0
            else:
                function = 1

            if self.engine_callback[function] is not None:
                self.engine_callback[function]()
