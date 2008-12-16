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

from virtaal.common import GObjectWrapper
from virtaal.controllers import BaseController

from tmmodel import TMModel
from tmview import TMView


class TMController(BaseController):
    """The logic-filled glue between the TM view and -model."""

    __gtype_name__ = 'TMController'
    QUERY_DELAY = 300

    # INITIALIZERS #
    def __init__(self, main_controller):
        GObjectWrapper.__init__(self)

        self.main_controller = main_controller
        self.view = TMView(self)
        self.model = TMModel(self)

        self._connect_plugin()

    def _connect_plugin(self):
        self._store_loaded_id = self.main_controller.store_controller.connect('store-loaded', self._on_store_loaded)


    # METHODS #
    def accept_response(self, query_str, matches):
        """Accept a query-response from the model.
            (This method is used as Model-Controller communications)"""
        if query_str == self.current_query:
            self.view.display_matches(matches)

    def select_match(self, match_data):
        """Handle a match-selection event.
            (This method is used as View-Controller communications)"""
        unit_controller = self.main_controller.unit_controller
        target_n = unit_controller.view.focused_target_n
        unit_controller.set_unit_target(target_n, match_data['target'])
        self.main_controller.undo_controller.remove_blank_undo()

    def send_tm_query(self, unit=None):
        """Send a new query to the TM engine.
            (This method is used as Controller-Model communications)"""
        if unit is not None:
            self.unit = unit

        self.current_query = unicode(self.unit.source.strings[0])
        self.view.clear()
        self.model.query(self.current_query)


    # EVENT HANDLERS #
    def _on_cursor_changed(self, cursor):
        """Start a TM query after C{self.QUERY_DELAY} milliseconds."""
        self.unit = cursor.model[cursor.index]
        self.view.hide()

        def start_query():
            self.send_tm_query()
            return False

        if getattr(self, '_delay_id', 0):
            gobject.source_remove(self._delay_id)
        self._delay_id = gobject.timeout_add(self.QUERY_DELAY, start_query)

    def _on_store_loaded(self, storecontroller):
        """Disconnect from the previous store's cursor and connect to the new one."""
        if getattr(self, '_cursor_changed_id', None):
            self.storecursor.disconnect(self._cursor_changed_id)
        self.storecursor = storecontroller.cursor
        self._cursor_changed_id = self.storecursor.connect('cursor-changed', self._on_cursor_changed)

        def handle_first_unit():
            self._on_cursor_changed(self.storecursor)
            return False
        gobject.idle_add(handle_first_unit)
