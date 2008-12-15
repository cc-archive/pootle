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
        iter = liststore.get_iter(path)
        match_data = liststore.get_value(iter, 0)

        self.select_match(match_data)
