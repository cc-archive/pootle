#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Virtaal.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import gobject
import gtk
import pango

from virtaal.views import markup, rendering


class TMWindow(gtk.Window):
    """Constructs the main TM window and all its children."""

    # INITIALIZERS #
    def __init__(self, view):
        super(TMWindow, self).__init__(gtk.WINDOW_POPUP)
        self.view = view

        self._build_gui()

    def _build_gui(self):
        self.connect('key-press-event', self._on_key_press)

        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        self.treeview = self._create_treeview()

        self.scrolled_window.add(self.treeview)
        self.add(self.scrolled_window)

    def _create_treeview(self):
        self.liststore = gtk.ListStore(gobject.TYPE_PYOBJECT)
        treeview = gtk.TreeView(model=self.liststore)
        treeview.set_rules_hint(True)

        self.perc_renderer = gtk.CellRendererProgress()
        self.match_renderer = TMMatchRenderer(self.view)

        # l10n: match quality column label
        self.tvc_perc = gtk.TreeViewColumn(_('%'), self.perc_renderer)
        self.tvc_perc.set_cell_data_func(self.perc_renderer, self._percent_data_func)
        self.tvc_match = gtk.TreeViewColumn(_('Matches'), self.match_renderer, matchdata=0)

        treeview.append_column(self.tvc_perc)
        treeview.append_column(self.tvc_match)

        return treeview

    # METHODS #
    def update_geometry(self, widget):
        """Move this window to right below the given widget so that C{widget}'s
            bottom left corner and this window's top left corner line up."""
        self.set_size_request(400, 300)

        alloc = tuple(widget.get_allocation())
        x = alloc[0]
        y = 0
        while widget:
            alloc = tuple(widget.get_allocation())
            y += alloc[1]
            widget = widget.parent
            if widget is self.view.controller.main_controller.store_controller.view:
                break

        #print '-> %d, %d' % (x, y)
        self.move(x, y)


    # EVENT HANLDERS #
    def _on_key_press(self, _widget, event, *_args):
        if event.keyval == gtk.keysyms.Escape:
            self.view.hide()

    def _percent_data_func(self, column, cell_renderer, tree_model, iter):
        match_data = tree_model.get_value(iter, 0)
        cell_renderer.set_property('value', int(match_data['quality']))
        cell_renderer.set_property('text', _("%(match_quality)s%%") % {"match_quality": match_data['quality']})


class TMMatchRenderer(gtk.GenericCellRenderer):
    """
    Renders translation memory matches.

    This class was adapted from C{virtaal.views.widgets.storeviewwidgets.StoreCellRenderer}.
    """

    __gtype_name__ = 'TMMatchRenderer'
    __gproperties__ = {
        "matchdata": (
            gobject.TYPE_PYOBJECT,
            "The match data.",
            "The match data that this renderer is currently handling",
            gobject.PARAM_READWRITE
        ),
    }

    ROW_PADDING = 10
    """The number of pixels between rows."""

    # INITIALIZERS #
    def __init__(self, view):
        gtk.GenericCellRenderer.__init__(self)

        self.view = view
        self.layout = None
        self.matchdata = None


    # INTERFACE METHODS #
    def do_get_size(self, widget, _cell_area):
        width = widget.get_toplevel().get_allocation().width - 32
        if width < -1:
            width = -1

        height = min(self._compute_cell_height(widget, width), 600)
        y_offset = self.ROW_PADDING / 2
        return 0, y_offset, width, height

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)

    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_start_editing(self, _event, tree_view, path, _bg_area, cell_area, _flags):
        return None # We should never be editing

    def on_render(self, window, widget, _background_area, cell_area, _expose_area, _flags):
        x_offset, y_offset, width, _height = self.do_get_size(widget, cell_area)
        x = cell_area.x + x_offset
        y = cell_area.y + y_offset
        widget.get_style().paint_layout(window, gtk.STATE_NORMAL, False,
                cell_area, widget, '', x, y, self.layout)

    # METHODS #
    def _compute_cell_height(self, widget, width):
        self.layout = self._get_pango_layout(widget, self.matchdata, width,
                rendering.get_source_font_description())
        self.layout.get_context().set_language(rendering.get_source_language())
        # This makes no sense, but has the desired effect to align things correctly for
        # both LTR and RTL languages:
        if widget.get_direction() == gtk.TEXT_DIR_RTL:
            self.layout.set_alignment(pango.ALIGN_RIGHT)
        _layout_width, height = self.layout.get_pixel_size()
        return height + self.ROW_PADDING

    def _get_pango_layout(self, widget, matchdata, width, font_description):
        '''Gets the Pango layout used in the cell in a TreeView widget.'''
        # We can't use widget.get_pango_context() because we'll end up
        # overwriting the language and font settings if we don't have a
        # new one
        layout = pango.Layout(widget.create_pango_context())
        layout.set_font_description(font_description)
        layout.set_wrap(pango.WRAP_WORD_CHAR)
        layout.set_width(width * pango.SCALE)
        #XXX - plurals?
        text = markup.markuptext(matchdata['source']) + '\n\n' + markup.markuptext(matchdata['target'])
        layout.set_markup(text)
        return layout
