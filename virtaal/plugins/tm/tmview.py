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

import gtk
import gobject

from virtaal.common import GObjectWrapper
from virtaal.views import BaseView


COLUMN_PERCENT, COLUMN_MATCH = range(2, 4)

class TMView(BaseView, GObjectWrapper):
    """The fake drop-down menu in which the TM matches are displayed."""

    __gtype_name__ = 'TMView'
    __gsignals__ = {
        'tm-match-selected': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
    }

    # INITIALIZERS #
    def __init__(self, controller):
        GObjectWrapper.__init__(self)

        self.controller = controller

        self._build_gui()

        self.visible = False

    def _build_gui(self):
        self.window = gtk.Window()
        self.window.connect('key-press-event', self._on_key_press)

        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.treeview = self._create_treeview()

        self.scrolled_window.add(self.treeview)
        self.window.add(self.scrolled_window)

    def _create_treeview(self):
        self.liststore = gtk.ListStore(gobject.TYPE_PYOBJECT)
        treeview = gtk.TreeView(model=self.liststore)

        self.perc_renderer = gtk.CellRendererProgress()
        self.match_renderer = CellRendererTMMatch()

        self.tvc_perc = gtk.TreeViewColumn(
            title='%',
            cell_renderer=self.perc_renderer,
            value=COLUMN_PERCENT
        )
        self.tvc_match = gtk.TreeViewColumn(
            title='Matches',
            cell_renderer=self.match_renderer
        )


    # METHODS #
    def display_matches(self, matches):
        pass

    def hide(self):
        """Hide the TM window."""
        self.window.hide()
        self.visible = False

    def show(self):
        """Show the TM window."""
        self.window.show()
        # TODO: Scroll to top
        self.visible = True


    # EVENT HANDLERS #
    def _on_key_press(self, _widget, event, *_args):
        if event.keyval == gtk.keysyms.Escape:
            self.hide()
