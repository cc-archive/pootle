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
import logging
from gtk import gdk

from virtaal.common import GObjectWrapper
from virtaal.views import BaseView

from tmwidgets import *


class TMView(BaseView, GObjectWrapper):
    """The fake drop-down menu in which the TM matches are displayed."""

    __gtype_name__ = 'TMView'
    __gsignals__ = {
        'tm-match-selected': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }

    # INITIALIZERS #
    def __init__(self, controller):
        GObjectWrapper.__init__(self)

        self.controller = controller
        self.isvisible = False
        self.tmwindow = TMWindow(self)
        self.tmwindow.treeview.connect('row-activated', self._on_row_activated)

        self._setup_key_bindings()

    def _setup_key_bindings(self):
        """Setup Gtk+ key bindings (accelerators)."""
        gtk.accel_map_add_entry("<Virtaal>/TM/Select match 1", gtk.keysyms._1, gdk.CONTROL_MASK)
        gtk.accel_map_add_entry("<Virtaal>/TM/Select match 2", gtk.keysyms._2, gdk.CONTROL_MASK)
        gtk.accel_map_add_entry("<Virtaal>/TM/Select match 3", gtk.keysyms._3, gdk.CONTROL_MASK)

        self.accel_group = gtk.AccelGroup()
        self.accel_group.connect_by_path("<Virtaal>/TM/Select match 1", self._on_select_match)
        self.accel_group.connect_by_path("<Virtaal>/TM/Select match 2", self._on_select_match)
        self.accel_group.connect_by_path("<Virtaal>/TM/Select match 3", self._on_select_match)

        mainview = self.controller.main_controller.view # FIXME: Is this acceptable?
        mainview.add_accel_group(self.accel_group)


    # METHODS #
    def clear(self):
        self.tmwindow.liststore.clear()
        self.hide()

    def display_matches(self, matches):
        liststore = self.tmwindow.liststore

        # Get the currently selected target TextView
        selected = self.controller.main_controller.unit_controller.view.targets[0]
        self.tmwindow.update_geometry(selected.parent)

        for match in matches:
            liststore.append([match])

        if len(liststore) > 0:
            self.show()

    def hide(self):
        """Hide the TM window."""
        self.tmwindow.hide()
        self.isvisible = False

    def select_match(self, match_data):
        """Select the match data as accepted by the user."""
        self.controller.select_match(match_data)

    def select_match_index(self, index):
        """Select the TM match with the given index (first match is C{1})."""
        if index < 0:
            return

        logging.debug('Selecting index %d' % (index))
        itr = self.tmwindow.liststore.get_iter_first()

        i=1
        while i < index:
            itr = self.tmwindow.liststore.iter_next(itr)
            i += 1

        path = self.tmwindow.liststore.get_path(itr)
        self.tmwindow.treeview.get_selection().select_iter(itr)
        self.tmwindow.treeview.row_activated(path, self.tmwindow.tvc_match)

    def show(self, force=False):
        """Show the TM window."""
        if self.isvisible and not force:
            return # This window is already visible
        self.tmwindow.show_all()
        # TODO: Scroll to top
        self.isvisible = True


    # EVENT HANDLERS #
    def _on_row_activated(self, treeview, path, column):
        """Called when a TM match is selected in the TM window."""
        liststore = treeview.get_model()
        assert liststore is self.tmwindow.liststore
        itr = liststore.get_iter(path)
        match_data = liststore.get_value(itr, 0)

        self.select_match(match_data)

    def _on_select_match(self, accel_group, acceleratable, keyval, modifier):
        self.select_match_index(int(keyval - gtk.keysyms._0))
