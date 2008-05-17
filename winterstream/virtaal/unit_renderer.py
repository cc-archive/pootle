#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2007 Osmo Salomaa
# Copyright (C) 2007 Zuza Software Foundation
#
# This file was part of Gaupol.
# This file is part of virtaal.
#
# virtaal is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Translate is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Translate.  If not, see <http://www.gnu.org/licenses/>.
from virtaal.unit_editor import get_layout, get_widget

"""Cell renderer for multiline text data."""

import gobject
import gtk
import pango

import markup
import undo_buffer
from unit_editor import UnitEditor
import unit_layout
from document import get_document

def undo(tree_view):
    undo_buffer.undo(tree_view.get_buffer().__undo_stack)

class UnitRenderer(gtk.GenericCellRenderer):
    """Cell renderer for multiline text data."""

    __gtype_name__ = "UnitRenderer"

    __gproperties__ = {
        "unit":     (gobject.TYPE_PYOBJECT,
                    "The unit",
                    "The unit that this renderer is currently handling",
                    gobject.PARAM_READWRITE),
        "editable": (gobject.TYPE_BOOLEAN,
                    "editable",
                    "A boolean indicating whether this unit is currently editable",
                    False,
                    gobject.PARAM_READWRITE),
    }

    __gsignals__ = {
        "editing-done":  (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                         (gobject.TYPE_STRING, gobject.TYPE_BOOLEAN, gobject.TYPE_BOOLEAN)),
        "modified":      (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }

    def __init__(self, parent):
        gtk.GenericCellRenderer.__init__(self)
        self.set_property('mode', gtk.CELL_RENDERER_MODE_EDITABLE)

        self.parent = parent
        self.__unit = None
        self.editable = False
        self._editor = None
        self.source_layout = None
        self.target_layout = None

    def get_unit(self):
        return self.__unit

    def set_unit(self, value):
        if value.isfuzzy():
            self.props.cell_background = "gray"
            self.props.cell_background_set = True

        else:
            self.props.cell_background_set = False

        self.__unit = value

    unit = property(get_unit, set_unit, None, None)

    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)

    def on_render(self, window, widget, _background_area, cell_area, _expose_area, _flags):
        if self.editable:
            return True
        x_offset, y_offset, width, _height = self.do_get_size(widget, cell_area)
        x = cell_area.x + x_offset
        y = cell_area.y + y_offset
        source_x = x
        target_x = x
        if widget.get_direction() == gtk.TEXT_DIR_LTR:
            target_x += width/2
        else:
            source_x += width/2
        widget.get_style().paint_layout(window, gtk.STATE_NORMAL, False,  
                cell_area, widget, '', source_x, y, self.source_layout)
        widget.get_style().paint_layout(window, gtk.STATE_NORMAL, False, 
                cell_area, widget, '', target_x, y, self.target_layout)

    def get_pango_layout(self, widget, text, width):
        '''Gets the Pango layout used in the cell in a TreeView widget.'''
        layout = pango.Layout(widget.get_pango_context())
        layout.set_wrap(pango.WRAP_WORD_CHAR)
        layout.set_width(width * pango.SCALE)

        #XXX - plurals?
        text = text or ""
        layout.set_markup(markup.markuptext(text))
        return layout

    def compute_cell_height(self, widget, width):
        self.source_layout = self.get_pango_layout(widget, self.unit.source, width / 2)
        self.target_layout = self.get_pango_layout(widget, self.unit.target, width / 2)
        # This makes no sense, but has the desired effect to align things correctly for
        # both LTR and RTL languages:
        if widget.get_direction() == gtk.TEXT_DIR_RTL:
            self.source_layout.set_alignment(pango.ALIGN_RIGHT)
            self.target_layout.set_alignment(pango.ALIGN_RIGHT)
        _layout_width, source_height = self.source_layout.get_pixel_size()
        _layout_width, target_height = self.target_layout.get_pixel_size()
        return max(source_height, target_height)

    def do_get_size(self, widget, _cell_area):
        xpad = 2
        ypad = 2

        #TODO: store last unitid and computed dimensions
        width = widget.get_toplevel().get_allocation().width - 32

        if self.editable:
            height = unit_layout.get_blueprints(self.unit, get_document(widget).nplurals).height(widget, width)
        else:
            height = self.compute_cell_height(widget, width)

        # XXX - comments
        width  = width  + (xpad * 2)
        height = height + (ypad * 2)

        height = min(height, 600)
        return xpad, ypad, width, height

    def _on_editor_done(self, editor):
        self.emit("editing-done", editor.get_data("path"), editor.must_advance, editor.get_modified())
        return True

    def _on_modified(self, widget):
        self.emit("modified")

    def do_start_editing(self, _event, tree_view, path, _bg_area, cell_area, _flags):
        """Initialize and return the editor widget."""
        if not hasattr(self.unit, '__editor'):
            editor = UnitEditor(tree_view, self.unit)
            editor.connect("editing-done", self._on_editor_done)
            editor.connect("modified", self._on_modified)
            editor.set_border_width(min(self.props.xpad, self.props.ypad))
            editor.show_all()
            setattr(self.unit, '__editor', editor)

        def set_heights(layout):
            for child in layout.children:
                set_heights(child)
            get_widget(layout).set_size_request(-1, layout.cached_height)

        editor = getattr(self.unit, '__editor')
        set_heights(get_layout(editor.layout))
        editor.set_size_request(cell_area.width, cell_area.height)
        self._editor = editor
        return editor
