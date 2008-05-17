#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007-2008 Zuza Software Foundation
#
# This file is part of virtaal.
#
# virtaal is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import gobject
import gtk

from translate.misc.multistring import multistring

import markup
import unit_layout

class UnitEditor(gtk.EventBox, gtk.CellEditable):
    """Text view suitable for cell renderer use."""

    __gtype_name__ = "UnitEditor"

    __gsignals__ = {
        'modified':(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }

    def __init__(self, parent, unit):
        gtk.EventBox.__init__(self)
#        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 50000))

        self.layout, widget_dict = unit_layout.get_blueprints(unit, parent).make_widget()
        self.add(self.layout)

        for target_widget in (s.widget for s in unit_layout.get_targets(unit_layout.get_layout(self.layout))):
            target_widget.child.get_buffer().connect("changed", self._on_modify)

        #blueprints['copy_button'].connect("activate", self._on_copy_original)
        #editor_names['copy_button'].connect("clicked", self._on_copy_original)
        #editor_names['copy_button'].set_relief(gtk.RELIEF_NONE)

        #editor_names['fuzzy_checkbox'].connect("toggled", self._on_modified)

        self.must_advance = False
        self._modified = False
        self._unit = unit
        self._widget_dict = widget_dict

        self.connect('key-press-event', self.on_key_press_event)

    def _on_modify(self, _buf):
        self.emit('modified')

    def on_key_press_event(self, _widget, event, *_args):
        if event.keyval == gtk.keysyms.Return or event.keyval == gtk.keysyms.KP_Enter:
            self.must_advance = True
            self.editing_done()

    def do_start_editing(self, *_args):
        """Start editing."""
        unit_layout.focus_text_view(self._widget_dict['target-0'].child)

    def _on_focus(self, widget, _direction):
        # TODO: Check whether we do need to refocus the last edited text_view when
        #       our program gets focus after having lost it.
        self.recent_textview = widget
        return False

    def _on_modified(self, widget):
        if widget in self.buffers:
            self.fuzzy_checkbox.set_active(False)
        elif self.recent_textview:
            self.recent_textview.grab_focus()
        self.emit("modified")
        self._modified = True
        return False

    def update_for_save(self):
        self.get_unit()
        self.reset_modified()

    def get_modified(self):
        return self._modified

    def reset_modified(self):
        """Resets all the buffers to not modified."""
        for b in self.buffers:
            b.set_modified(False)
        self._modified = False

    def get_text(self):
        targets = [b.props.text for b in self.buffers]
        if len(targets) == 1:
            return targets[0]
        else:
            return multistring(targets)

    def _on_copy_original(self, _widget):
        for buf in self.buffers:
            buf.set_text(markup.escape(self._unit.source))
            self.do_start_editing()
        return True
